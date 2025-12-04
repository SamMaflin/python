# =====================================================================
# MODEL ENGINE – LEVEL 3/4 HYBRID
# League-aware, team-style-normalised, config-driven
# =====================================================================

import pandas as pd
import numpy as np

from .utils import (
    convert_value_to_millions,
    age_value_multiplier,
    LEAGUE_MULTIPLIERS,
)

from .model_config import ROLE_CONFIG


# =====================================================================
# GLOBAL DEFAULTS
# =====================================================================

GLOBAL = ROLE_CONFIG["__settings__"]
DEFAULT_PATH = GLOBAL["DEFAULT_PATH"]
DEFAULT_BUDGET = GLOBAL["DEFAULT_BUDGET"]
DEFAULT_MINUTES = GLOBAL["DEFAULT_MINUTES"]


# =====================================================================
# DATA LOADING
# =====================================================================

def load_data(path: str, min_minutes: int) -> pd.DataFrame:
    """
    Load raw data and apply a minutes threshold.
    """
    df = pd.read_csv(path)
    df = df[df["Minutes"] >= min_minutes].copy()
    return df


# =====================================================================
# TEAM CONTEXT METRICS
# =====================================================================

def add_team_context_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute team-level context metrics (possession, pressing, tempo, xG strength)
    using minute-weighted averages. These are per-team, per-league aggregates.

    Output columns merged back onto df:
      - Team_Minutes
      - Team_Possession
      - Team_PressIntensity
      - Team_Tempo
      - Team_Att_xg_per90
      - Team_Def_xg_per90
      - Team_xGD_proxy
    """
    required = ["League", "Team", "Minutes"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column for team context: {col}")

    grp = df.groupby(["League", "Team"])

    def wavg(g: pd.DataFrame, col: str):
        if col not in g.columns or g[col].isna().all():
            return np.nan
        return np.average(g[col], weights=g["Minutes"])

    team_stats = grp.apply(
        lambda g: pd.Series({
            "Team_Minutes": g["Minutes"].sum(),
            "Team_Possession": wavg(g, "Op_passes"),
            "Team_PressIntensity": wavg(g, "Pressures"),
            "Team_Tempo": wavg(g, "Turnovers"),
            "Team_Att_xg_per90": wavg(g, "Np_xg"),
            "Team_Def_xg_per90": wavg(g, "Np_xg_faced") if "Np_xg_faced" in g.columns else np.nan,
        })
    )

    team_stats["Team_xGD_proxy"] = (
        team_stats["Team_Att_xg_per90"] - team_stats["Team_Def_xg_per90"]
    )

    df = df.merge(
        team_stats,
        left_on=["League", "Team"],
        right_index=True,
        how="left",
        validate="many_to_one",
    )

    return df


# =====================================================================
# CONTEXT-NORMALISED METRICS (HYBRID NORMALISATION – OPTION C)
# =====================================================================

def _hybrid_norm(df: pd.DataFrame, col: str, team_col: str, league_mean_col: str, suffix="_ctx"):
    """
    Hybrid normalisation:

        X_ctx = X * (LeagueMeanTeamContext / TeamContext)

    with clipping of the factor to [0.5, 1.5] to avoid extreme values.
    """
    if col not in df.columns or team_col not in df.columns or league_mean_col not in df.columns:
        return df

    denom = df[team_col].replace(0, np.nan)
    factor = (df[league_mean_col] / denom)
    factor = factor.clip(0.5, 1.5).fillna(1.0)

    df[col + suffix] = df[col] * factor
    return df


def add_context_normalised_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create *_ctx metrics that adjust for team style:
      - Team_Possession
      - Team_PressIntensity
      - Team_Tempo
      - Team_Att_xg_per90 / Team_xGD_proxy

    This runs on the full dataset (all positions) BEFORE position filtering.
    """

    # League-level means of team style metrics
    lg = df.groupby("League")
    df["Lg_Team_Possession"] = lg["Team_Possession"].transform("mean")
    df["Lg_Team_PressIntensity"] = lg["Team_PressIntensity"].transform("mean")
    df["Lg_Team_Tempo"] = lg["Team_Tempo"].transform("mean")
    df["Lg_Team_Att_xg"] = lg["Team_Att_xg_per90"].transform("mean")
    df["Lg_Team_xGD"] = lg["Team_xGD_proxy"].transform("mean")

    # ---------------------------------------------------------
    # POSSESSION-DRIVEN METRICS
    # ---------------------------------------------------------
    poss_metrics = [
        "Op_passes",
        "Op_key_passes",
        "Op_passes_into_box",
        "Passes_inside_box",
        "Through_balls",
        "Op_xa",
        "Key_passes",
        "Assists",
        "Op_last_3rd_passes",
        "Xgchain",
        "Op_xgchain",
        "Xgbuildup",
        "Op_xgbuildup",
        "Xgchain_per_possession",
        "Op_xgchain_per_possession",
        "Xgbuildup_per_possession",
        "Op_xgbuildup_per_possession",
        "Pass_and_carry_last_3rd",
        "Crosses_completed",
        "Sp_pass_into_box",
        # IMPORTANT: used directly in ROLE_CONFIG
        "Touches_in_box",
    ]

    for col in poss_metrics:
        _hybrid_norm(df, col, "Team_Possession", "Lg_Team_Possession")

    # ---------------------------------------------------------
    # PRESSING-DRIVEN METRICS
    # ---------------------------------------------------------
    press_metrics = [
        "Pressures",
        "Padj_pressures",
        "Counterpressures",
        "Opp_half_pressures",
        "Opp_half_counterpressures",
        "Successful_pressures",
        "Successful_counterpressures",
        "Defensive_actions",
        "Tackles",
        "Interceptions",
        "Padj_tackles",
        "Padj_interceptions",
        "Ball_recoveries",
    ]

    for col in press_metrics:
        _hybrid_norm(df, col, "Team_PressIntensity", "Lg_Team_PressIntensity")

    # ---------------------------------------------------------
    # TEMPO-DRIVEN METRICS (TRANSITIONS / CARRY / TURNOVERS)
    # ---------------------------------------------------------
    tempo_metrics = [
        "Carries",
        "Dribbles_attempts",
        "Dribbles_successful",
        "Turnovers",
        "Carry_length",
        "Failed_dribbles",
        "Dispossessed",
    ]

    for col in tempo_metrics:
        _hybrid_norm(df, col, "Team_Tempo", "Lg_Team_Tempo")

    # ---------------------------------------------------------
    # ATTACKING STRENGTH / XG-DRIVEN METRICS
    # ---------------------------------------------------------
    xg_metrics = [
        "Np_xg",
        "Np_goals",
        "Np_shots",
    ]

    for col in xg_metrics:
        _hybrid_norm(df, col, "Team_Att_xg_per90", "Lg_Team_Att_xg")

    # Derived contextual finishing helper (if needed later)
    if "Np_xg_ctx" in df.columns and "Np_goals_ctx" in df.columns:
        df["Actual_vs_xG_ctx"] = df["Np_goals_ctx"] - df["Np_xg_ctx"]

    return df


# =====================================================================
# LEAGUE STRENGTH MULTIPLIER
# =====================================================================

def apply_league_strength(df: pd.DataFrame, metrics):
    """
    Multiply metrics by league-strength multiplier before z-scoring.
    Works on the derived metrics (baseline, indices, groups).
    """
    df["LeagueMult"] = df["League"].map(LEAGUE_MULTIPLIERS).fillna(
        LEAGUE_MULTIPLIERS["DEFAULT"]
    )

    for m in metrics:
        if m in df.columns:
            df[m] = df[m] * df["LeagueMult"]

    return df


# =====================================================================
# PER-LEAGUE Z-SCORING
# =====================================================================

def add_z_by_league(df: pd.DataFrame, metrics, league_col: str = "League", clip: float = 3.0):
    """
    Compute z-scores within each league to avoid cross-league inflation.
    """
    for m in metrics:
        if m not in df.columns:
            df[f"z_{m}"] = 0.0
            continue

        g = df.groupby(league_col)[m]
        mean = g.transform("mean")
        std = g.transform("std").replace(0, np.nan)

        df[f"z_{m}"] = (df[m] - mean) / std
        df[f"z_{m}"] = df[f"z_{m}"].fillna(0.0)

        if clip is not None:
            df[f"z_{m}"] = df[f"z_{m}"].clip(-clip, clip)

    return df


# =====================================================================
# BASELINE METRICS
# =====================================================================

def compute_baseline(df: pd.DataFrame, baseline: dict) -> pd.DataFrame:
    """
    Compute all custom baseline metrics defined in ROLE_CONFIG["role"]["baseline"].
    Many of these use *_ctx metrics now.
    """
    for name, fn in baseline.items():
        df[name] = fn(df)
    return df


# =====================================================================
# ROLE INDICES
# =====================================================================

def compute_indices(df: pd.DataFrame, indices: dict) -> pd.DataFrame:
    """
    Compute each role index (e.g. Carrier_Index, Finisher_Index)
    as a weighted sum of per-league z-scores of its component metrics.
    """
    for idx_name, metric_weights in indices.items():
        metrics = list(metric_weights.keys())
        df = add_z_by_league(df, metrics)

        df[idx_name] = sum(
            df[f"z_{m}"] * w for m, w in metric_weights.items()
        )

    return df


# =====================================================================
# INDEX PERCENTILES
# =====================================================================

def add_index_percentiles(df: pd.DataFrame, indices: dict) -> pd.DataFrame:
    """
    Add percentile columns for each index.
    E.g. Carrier_Index → Carrier_pct.
    """
    for idx_name in indices.keys():
        pct_col = idx_name.replace("_Index", "_pct")
        df[pct_col] = df[idx_name].rank(pct=True) * 100
    return df


# =====================================================================
# OVERALL ROLE RATING
# =====================================================================

def compute_overall(df: pd.DataFrame, groups: dict, weights: dict, sliders: dict) -> pd.DataFrame:
    """
    Compute overall rating as a weighted combination of group-level z-scores.

    groups: { "GroupName": [metric1, metric2, ...], ... }
    weights: { "GroupName": weight, ... }
    sliders: UI-controlled multipliers per group.
    """

    all_metrics = {m for metric_list in groups.values() for m in metric_list}
    df = add_z_by_league(df, list(all_metrics))

    df["Overall_raw"] = 0.0

    # Slider-adjusted group weights
    adj_weights = {g: weights[g] * sliders.get(g, 1.0) for g in weights}
    total_weight = sum(adj_weights.values()) or 1.0

    for g, metric_list in groups.items():
        z_cols = [f"z_{m}" for m in metric_list if f"z_{m}" in df.columns]
        if not z_cols:
            continue

        df[f"{g}_GroupZ"] = df[z_cols].mean(axis=1)
        df["Overall_raw"] += (adj_weights[g] / total_weight) * df[f"{g}_GroupZ"]

    df["Overall_adj"] = df["Overall_raw"]
    df["Overall_pct"] = df["Overall_adj"].rank(pct=True) * 100

    return df


# =====================================================================
# BUY SCORE
# =====================================================================

def compute_buy_score(df: pd.DataFrame, budget_million: float) -> pd.DataFrame:
    """
    Celtic-optimised Level 4 BuyScore:
    Value Efficiency + Age Premium + Reliability + Sustainability + Performance Fit.
    """

    # --------------------------------------------
    # 1. VALUE EFFICIENCY (Most important for Celtic)
    # --------------------------------------------
    df["Value_million"] = df["Value"].apply(convert_value_to_millions).fillna(99)

    # ability-per-cost (log dampens inflation)
    df["ValueEff"] = df["Overall_adj"] / np.log(df["Value_million"] + 1.75)

    # --------------------------------------------
    # 2. AGE PREMIUM (Celtic-specific optimal window: 20–24)
    # --------------------------------------------
    df["AgePremium"] = 1 / (1 + np.exp((df["Age"] - 23) / 3))

    # --------------------------------------------
    # 3. RELIABILITY (Minutes availability)
    # --------------------------------------------
    df["Reliability"] = df["Minutes"] / df["Minutes"].max()

    # --------------------------------------------
    # 4. SUSTAINABILITY (penalise volatile overperformance)
    # --------------------------------------------
    if "Np_goals_ctx" in df.columns and "Np_xg_ctx" in df.columns:
        df["FinishingDiff"] = df["Np_goals_ctx"] - df["Np_xg_ctx"]
    else:
        df["FinishingDiff"] = 0

    if "Assists_ctx" in df.columns and "Op_xa_ctx" in df.columns:
        df["AssistDiff"] = df["Assists_ctx"] - df["Op_xa_ctx"]
    else:
        df["AssistDiff"] = 0

    df["Sustainability"] = np.exp(-(df["FinishingDiff"].abs() + df["AssistDiff"].abs()) / 2)

    # --------------------------------------------
    # 5. PERFORMANCE FIT
    # --------------------------------------------
    df["Perf"] = df["Overall_adj"]  # <-- NEEDED so z_Perf exists

    # --------------------------------------------
    # NORMALISE COMPONENTS (league aware)
    # --------------------------------------------
    df = add_z_by_league(df, ["ValueEff", "AgePremium", "Reliability", "Sustainability", "Perf"])

    # --------------------------------------------
    # CELTIC-OPTIMISED WEIGHTING
    # --------------------------------------------
    df["BuyScore"] = (
        0.1 * df["z_ValueEff"] +
        0.15 * df["z_AgePremium"] +
        0.10 * df["z_Reliability"] +
        0.10 * df["z_Sustainability"] +
        0.55 * df["z_Perf"]          # massive steering via sliders
    )



    # --------------------------------------------
    # APPLY BUDGET FILTER
    # --------------------------------------------
    df = df[df["Value_million"] <= budget_million].copy()
    return df



# =====================================================================
# MAIN PIPELINE (ASSUMES CONTEXT IS ALREADY ADDED)
# =====================================================================

def run_pipeline(df: pd.DataFrame, cfg: dict, sliders: dict, budget_million: float) -> pd.DataFrame:
    """
    Full modelling pipeline for a given role — now includes a GLOBAL
    ability percentile (Overall_pct_global) computed BEFORE the budget filter.
    """

    baseline = cfg["baseline"]
    indices = cfg["indices"]
    groups = cfg["groups"]
    weights = cfg["weights"]
 
    # 1) Compute baseline metrics (many use *_ctx) 
    df = compute_baseline(df, baseline)
 
    # 2) Apply league strength multiplier 
    all_metrics = set(baseline.keys())
    for idx in indices.values():
        all_metrics |= set(idx.keys())
    for grp in groups.values():
        all_metrics |= set(grp)

    df = apply_league_strength(df, all_metrics)
 
    # 3) Compute role indices + index percentiles 
    df = compute_indices(df, indices)
    df = add_index_percentiles(df, indices)
 
    # 4) Compute OVERALL (performance ability score) 
    df = compute_overall(df, groups, weights, sliders) 
    # 5) GLOBAL OVERALL PERCENTILE (NEW — BEFORE BUDGET FILTER) 
    df["Overall_pct_global"] = df["Overall_adj"].rank(pct=True) * 100
 
    # 6) BUY SCORE (handles age, value, and budget) 
    df = compute_buy_score(df, budget_million)

    # df is already budget-filtered inside compute_buy_score()
    return df



# =====================================================================
# UNIVERSAL ENTRY POINT
# =====================================================================

def run_model(
    role: str,
    *,
    path: str = DEFAULT_PATH,
    min_minutes: int | None = None,
    budget_million: float | None = None,
    **sliders,
) -> pd.DataFrame:
    """
    Generic runner for any configured role.

    Example:
        run_model("winger", Carrier=1.2, Presser=0.8)
    """

    if role not in ROLE_CONFIG:
        raise ValueError(f"Unknown role: {role}")

    cfg = ROLE_CONFIG[role]
    min_minutes = min_minutes or cfg.get("min_minutes", DEFAULT_MINUTES)
    budget_million = budget_million or DEFAULT_BUDGET

    # 1) Load FULL dataset (all positions)
    df = load_data(path, min_minutes)

    # 2) Add team context & *_ctx metrics on the FULL dataset
    df = add_team_context_metrics(df)
    df = add_context_normalised_metrics(df)

    # 3) Now filter to role positions (AFTER context is built)
    mask = (
        df["Position_1"].isin(cfg["positions"]) |
        df["Position_2"].isin(cfg["positions"])
    )
    df = df[mask].copy()

    if df.empty:
        return df

    # 4) Run role-specific pipeline
    return run_pipeline(df, cfg, sliders, budget_million)


# =====================================================================
# ROLE WRAPPERS
# =====================================================================

def run_gk_model(**kwargs) -> pd.DataFrame:
    return run_model("goalkeeper", **kwargs)


def run_winger_model(**kwargs) -> pd.DataFrame:
    return run_model("winger", **kwargs)


def run_midfielder_model(**kwargs) -> pd.DataFrame:
    return run_model("midfielder", **kwargs)


def run_striker_model(**kwargs) -> pd.DataFrame:
    return run_model("striker", **kwargs)
