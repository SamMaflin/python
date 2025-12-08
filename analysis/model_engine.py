import pandas as pd
import numpy as np

from .utils import (
    convert_value_to_millions, 
    LEAGUE_MULTIPLIERS,
)
from .model_config import ROLE_CONFIG



# GLOBAL DEFAULTS


GLOBAL = ROLE_CONFIG["__settings__"]
DEFAULT_PATH = GLOBAL["DEFAULT_PATH"]
DEFAULT_BUDGET = GLOBAL["DEFAULT_BUDGET"]
DEFAULT_MINUTES = GLOBAL["DEFAULT_MINUTES"]



# DATA LOADING


def load_data(path: str, min_minutes: int) -> pd.DataFrame:
    """
    Load raw player-season data and apply a minutes threshold.
    """
    df = pd.read_csv(path)
    df = df[df["Minutes"] >= min_minutes].copy()
    return df



# TEAM CONTEXT METRICS


def add_team_context_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute team-level context metrics (possession proxy, pressing,
    tempo proxy, and xG strength) as minute-weighted averages.

    These are per-team, per-league aggregates and are merged back
    onto the player-level dataframe.

    Created columns:
      - Team_Minutes          : total minutes recorded for the team
      - Team_PossessionProxy  : minute-weighted average of Op_passes
      - Team_PressIntensity   : minute-weighted average of Pressures
      - Team_TempoProxy       : minute-weighted average of Turnovers
      - Team_Att_xg_per90     : minute-weighted average of Np_xg
      - Team_Def_xg_per90     : minute-weighted average of Np_xg_faced (if present)
      - Team_xGD_proxy        : Team_Att_xg_per90 - Team_Def_xg_per90
    """
    required = ["League", "Team", "Minutes"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column for team context: {col}")

    grp = df.groupby(["League", "Team"])

    def wavg(g: pd.DataFrame, col: str) -> float:
        if col not in g.columns or g[col].isna().all():
            return np.nan
        return np.average(g[col], weights=g["Minutes"])

    team_stats = grp.apply(
        lambda g: pd.Series(
            {
                "Team_Minutes": g["Minutes"].sum(),
                # These three are proxies, not strict possession/tempo:
                "Team_PossessionProxy": wavg(g, "Op_passes"),
                "Team_PressIntensity": wavg(g, "Pressures"),
                "Team_TempoProxy": wavg(g, "Turnovers"),
                "Team_Att_xg_per90": wavg(g, "Np_xg"),
                "Team_Def_xg_per90": wavg(g, "Np_xg_faced")
                if "Np_xg_faced" in g.columns
                else np.nan,
            }
        )
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



# HYBRID NORMALISATION


def _hybrid_norm(
    df: pd.DataFrame,
    col: str,
    team_col: str,
    league_mean_col: str,
    suffix: str = "_ctx",
    min_std: float = 1e-6,
) -> pd.DataFrame:
    """
    Context-normalise a metric by scaling it according to how its
    team environment compares to the league average.

    Example:
        metric_ctx = metric * clip( league_mean(team_col) / team_col , 0.5, 1.5 )

    - If the team_col has very little variance across the league (std < min_std),
      the function is a no-op.
    - If any required column is missing, it is a no-op.
    """
    if col not in df.columns or team_col not in df.columns or league_mean_col not in df.columns:
        return df

    # If there's no meaningful spread, don't normalise
    if df[team_col].std(skipna=True) < min_std:
        return df

    denom = df[team_col].replace(0, np.nan)
    factor = (df[league_mean_col] / denom).clip(0.5, 1.5).fillna(1.0)

    df[col + suffix] = df[col] * factor
    return df



# CONTEXT-NORMALISED METRICS


def add_context_normalised_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build context-normalised metrics ( *_ctx ) using team-level proxies
    for possession, press intensity, tempo, and attacking xG.

    All normalisations are per league.
    """
    if "League" not in df.columns:
        raise ValueError("League column is required for context normalisation.")

    lg = df.groupby("League")

    # League means for context drivers
    df["Lg_Team_PossessionProxy"] = lg["Team_PossessionProxy"].transform("mean")
    df["Lg_Team_PressIntensity"] = lg["Team_PressIntensity"].transform("mean")
    df["Lg_Team_TempoProxy"] = lg["Team_TempoProxy"].transform("mean")
    df["Lg_Team_Att_xg"] = lg["Team_Att_xg_per90"].transform("mean")
    df["Lg_Team_xGD"] = lg["Team_xGD_proxy"].transform("mean")


    # POSSESSION-CONTROLLED CREATION / PASSING METRICS

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
        "Touches_in_box",
    ]

    for col in poss_metrics:
        _hybrid_norm(df, col, "Team_PossessionProxy", "Lg_Team_PossessionProxy")


    # PRESSURE ENVIRONMENT

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


    # TEMPO / TRANSITION ENVIRONMENT

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
        _hybrid_norm(df, col, "Team_TempoProxy", "Lg_Team_TempoProxy")


    # XG STRENGTH (ATTACKING)

    xg_metrics = ["Np_xg", "Np_goals", "Np_shots"]

    for col in xg_metrics:
        _hybrid_norm(df, col, "Team_Att_xg_per90", "Lg_Team_Att_xg")

    # Convenience: context-adjusted finishing difference if available
    if "Np_xg_ctx" in df.columns and "Np_goals_ctx" in df.columns:
        df["Actual_vs_xG_ctx"] = df["Np_goals_ctx"] - df["Np_xg_ctx"]

    return df



# PER-LEAGUE Z-SCORING (IDEMPOTENT)


def zscore_once(df: pd.DataFrame, metrics, prefix: str = "z_") -> pd.DataFrame:
    """
    Compute z-scores within each league for the given metrics.

    - Idempotent: if z_<metric> already exists, it is NOT recomputed.
    - Missing metrics get a z-score of 0.0.
    - Values are clipped to [-3, 3] to avoid extreme outliers.
    """
    if "League" not in df.columns:
        raise ValueError("League column is required for z-scoring.")

    for m in metrics:
        zcol = f"{prefix}{m}"
        if zcol in df.columns:
            # Already computed – don't re-normalise
            continue

        if m not in df.columns:
            df[zcol] = 0.0
            continue

        g = df.groupby("League")[m]
        mean = g.transform("mean")
        std = g.transform("std").replace(0, np.nan)

        z = (df[m] - mean) / std
        df[zcol] = z.fillna(0.0).clip(-3.0, 3.0)

    return df



# BASELINE METRICS


def compute_baseline(df: pd.DataFrame, baseline: dict) -> pd.DataFrame:
    """
    Compute all custom baseline metrics defined in ROLE_CONFIG[role]["baseline"].
    Many of these now use *_ctx metrics as inputs.
    """
    for name, fn in baseline.items():
        df[name] = fn(df)
    return df



# ROLE INDICES


def compute_indices(df: pd.DataFrame, indices: dict) -> pd.DataFrame:
    """
    Compute each role index (e.g. BallCarrier_Index, Finisher_Index)
    as a weighted sum of per-league z-scores of its component metrics.
    """
    for idx_name, metric_weights in indices.items():
        metrics = list(metric_weights.keys())
        df = zscore_once(df, metrics)

        df[idx_name] = sum(df[f"z_{m}"] * w for m, w in metric_weights.items())

    return df



# INDEX PERCENTILES


def add_index_percentiles(df: pd.DataFrame, indices: dict) -> pd.DataFrame:
    """
    Add percentile columns for each index.
    E.g. BallCarrier_Index → BallCarrier_pct.
    """
    for idx_name in indices.keys():
        pct_col = idx_name.replace("_Index", "_pct")
        if idx_name in df.columns:
            df[pct_col] = df[idx_name].rank(pct=True) * 100
        else:
            df[pct_col] = 0.0
    return df



# OVERALL ROLE RATING


def compute_overall(
    df: pd.DataFrame,
    groups: dict,
    weights: dict,
    sliders: dict,
) -> pd.DataFrame:
    """
    Compute overall rating as a weighted combination of group-level z-scores.

    groups : { "GroupName": [metric1, metric2, ...], ... }
    weights: { "GroupName": weight, ... }
    sliders: UI-controlled multipliers per group (default 1.0 if missing).

    League strength is applied at the final Overall stage so that
    league z-scoring (relative performance) is preserved, and then
    adjusted by a global league multiplier.
    """
    # 1) Z-score all raw metrics that feed into groups (idempotent)
    all_metrics = {m for metric_list in groups.values() for m in metric_list}
    df = zscore_once(df, list(all_metrics))

    df["Overall_raw"] = 0.0

    # Slider-adjusted group weights
    adj_weights = {g: weights[g] * sliders.get(g, 1.0) for g in weights}
    total_weight = sum(adj_weights.values()) or 1.0

    # 2) Group-level z-aggregates and raw overall
    for g, metric_list in groups.items():
        z_cols = [f"z_{m}" for m in metric_list if f"z_{m}" in df.columns]
        if not z_cols:
            continue

        df[f"{g}_GroupZ"] = df[z_cols].mean(axis=1)
        df["Overall_raw"] += (adj_weights[g] / total_weight) * df[f"{g}_GroupZ"]

    # 3) Apply league strength at the final stage
    df["LeagueMult"] = df["League"].map(LEAGUE_MULTIPLIERS).fillna(
        LEAGUE_MULTIPLIERS.get("DEFAULT", 1.0)
    )
    df["Overall_adj"] = df["Overall_raw"] * df["LeagueMult"]

    # 4) Percentile within the role-filtered dataset
    df["Overall_pct"] = df["Overall_adj"].rank(pct=True) * 100

    return df



# BUY SCORE (Celtic-optimised)


def compute_buy_score(df: pd.DataFrame, budget_million: float) -> pd.DataFrame:
    """
    Level 4 BuyScore for Celtic:

    Combines:
      - Value Efficiency
      - Age Profile
      - Reliability (availability)
      - Sustainability (regression risk on G/xG + A/xA)
      - Performance (Overall_adj)

    Then filters to players within the transfer budget.
    """

    # 1. VALUE EFFICIENCY  
    df["Value_million"] = df["Value"].apply(convert_value_to_millions).fillna(99)

    # ability-per-cost (log dampens inflation)
    df["ValueEff"] = df["Overall_adj"] / np.log(df["Value_million"] + 1.75)

    # 2. AGE PREMIUM (Celtic-specific optimal window: ~20–24) 
    df["AgePremium"] = 1 / (1 + np.exp((df["Age"] - 23) / 3))

    # 3. RELIABILITY (Minutes availability – league normalised)  
    league_mean_minutes = df.groupby("League")["Minutes"].transform("mean")
    df["Reliability"] = (df["Minutes"] / league_mean_minutes).replace(
        [np.inf, -np.inf], np.nan
    )
    df["Reliability"] = df["Reliability"].fillna(0.0).clip(0, 1.5)

    # 4. SUSTAINABILITY (penalise volatile overperformance)  
    if "Np_goals_ctx" in df.columns and "Np_xg_ctx" in df.columns:
        df["FinishingDiff"] = df["Np_goals_ctx"] - df["Np_xg_ctx"]
    else:
        df["FinishingDiff"] = 0.0

    if "Assists_ctx" in df.columns and "Op_xa_ctx" in df.columns:
        df["AssistDiff"] = df["Assists_ctx"] - df["Op_xa_ctx"]
    else:
        df["AssistDiff"] = 0.0

    total_diff = df["FinishingDiff"] + df["AssistDiff"]
    over = total_diff.clip(lower=0)          # overperformance
    under = (-total_diff).clip(lower=0)      # underperformance

    # Overperformance regresses more heavily than underperformance
    df["Sustainability"] = np.exp(-(2 * over + 1 * under) / 2)

    # 5. PERFORMANCE FIT 
    df["Perf"] = df["Overall_adj"]

    # NORMALISE BUY COMPONENTS (per league) 
    df = zscore_once(df, ["ValueEff", "AgePremium", "Reliability", "Sustainability", "Perf"])

    # CELTIC-OPTIMISED WEIGHTING 
    df["BuyScore"] = (
        0.10 * df["z_ValueEff"]
        + 0.20 * df["z_AgePremium"]
        + 0.10 * df["z_Reliability"]
        + 0.05 * df["z_Sustainability"]
        + 0.60 * df["z_Perf"]  # sliders heavily steer Perf via Overall_adj
    )

    # APPLY BUDGET FILTER 
    df = df[df["Value_million"] <= budget_million].copy()
    return df



# MAIN PIPELINE (ASSUMES CONTEXT IS ALREADY ADDED)


def run_pipeline(
    df: pd.DataFrame,
    cfg: dict,
    sliders: dict,
    budget_million: float,
) -> pd.DataFrame:
    """
    Full modelling pipeline for a given role.
    """
    baseline = cfg["baseline"]
    indices = cfg["indices"]
    groups = cfg["groups"]
    weights = cfg["weights"]

    # 1) Compute baseline metrics (many use *_ctx)
    df = compute_baseline(df, baseline)

    # 2) Compute role indices + index percentiles
    df = compute_indices(df, indices)
    df = add_index_percentiles(df, indices)

    # 3) Compute OVERALL (performance ability score, with league strength)
    df = compute_overall(df, groups, weights, sliders)

    # 4) GLOBAL OVERALL PERCENTILE (before budget filter)
    df["Overall_pct_global"] = df["Overall_adj"].rank(pct=True) * 100

    # 5) BUY SCORE (handles age, value, and budget, and filters by budget)
    df = compute_buy_score(df, budget_million)

    return df



# UNIVERSAL ENTRY POINT


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
        run_model("winger", Ball Carrier=1.2, Goal Threat=0.8)
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
        df["Position_1"].isin(cfg["positions"])
        | df["Position_2"].isin(cfg["positions"])
    )
    df = df[mask].copy()

    if df.empty:
        return df

    # 4) Run role-specific pipeline
    return run_pipeline(df, cfg, sliders, budget_million)

 
# ROLE WRAPPERS 

def run_gk_model(**kwargs) -> pd.DataFrame:
    return run_model("goalkeeper", **kwargs)


def run_winger_model(**kwargs) -> pd.DataFrame:
    return run_model("winger", **kwargs)


def run_midfielder_model(**kwargs) -> pd.DataFrame:
    return run_model("midfielder", **kwargs)


def run_striker_model(**kwargs) -> pd.DataFrame:
    return run_model("striker", **kwargs)
