import pandas as pd
import numpy as np
from utils import (
    safe_div,
    add_z,
    convert_value_to_millions,
    age_value_multiplier,
    LEAGUE_MULTIPLIERS,
)

# --- POSITION CONFIGS -------------------------------------------------------

POSITION_CONFIGS = {
    "gk": {
        "label": "Goalkeeper",
        "position_filters": ["Goalkeeper"],  # Position_1 / Position_2 values

        # Baseline (radar-layer) metrics: name -> function(df) -> series
        "baseline_metrics": {
            # --- Shot Stopping ---
            "Save Efficiency Above Expected (%)": lambda df: (
                df["Save_percentage"] - df["Xsave_percentage"]
            ),
            "Goals Saved Above Expected per Shot": lambda df: safe_div(
                df["Goals_saved_above_avg"], df["Shots_on_target_faced"]
            ),

            # --- Distribution ---
            "Pressured Pass Efficiency": lambda df: (
                df["Passing_percentage_under_pressure"]
                * (df["Percentage_passes_under_pressure"] / 100)
            ),
            "Long Pass Efficiency": lambda df: (
                df["Long_ball_percentage"] * df["Successful_pass_length"]
            ),
            "Pass Progression Efficiency": lambda df: (
                df["Forward_pass_proportion"] * df["Successful_pass_length"]
            ),
            "Pass Completion": lambda df: df["Passing_percentage"],

            # --- Sweeper ---
            "Sweeper Action Distance": lambda df: df["Gk_defesive_action_distance"],
            "Sweeper Actions": lambda df: df["Defensive_actions"],

            # --- Risk ---
            "Error Rate": lambda df: safe_div(
                df.get("Errors", 0) + df.get("Turnovers", 0),
                df["Minutes"] / 90,
            ),
        },

        # Component indices: index_name -> { metrics: {col_name: weight} }
        "indices": {
            "ShotStop_Index": {
                "metrics": {
                    "Save Efficiency Above Expected (%)": 0.25,
                    "Goals Saved Above Expected per Shot": 0.30,
                    "Goals_saved_above_avg": 0.45,  # raw column from data
                }
            },
            "Distribution_Index": {
                "metrics": {
                    "Pressured Pass Efficiency": 0.20,
                    "Long Pass Efficiency": 0.25,
                    "Pass Progression Efficiency": 0.25,
                    "Pass Completion": 0.30,
                }
            },
            "Sweeper_Index": {
                "metrics": {
                    "Sweeper Actions": 0.60,
                    "Sweeper Action Distance": 0.30,
                    "Error Rate": -0.10,  # negative weight = inverted
                }
            },
        },

        # Radar groups for UI
        "radar_groups": {
            "Shot Stopping": [
                "Goals Saved Above Expected per Shot",
                "Save Efficiency Above Expected (%)",
            ],
            "Distribution": [
                "Pressured Pass Efficiency",
                "Long Pass Efficiency",
                "Pass Progression Efficiency",
                "Pass Completion",
            ],
            "Sweeping": [
                "Sweeper Actions",
                "Sweeper Action Distance",
                "Error Rate",
            ],
        },
        "radar_invert": ["Error Rate"],

        # Mapping from radar group -> index name
        "group_to_index": {
            "Shot Stopping": "ShotStop_Index",
            "Distribution": "Distribution_Index",
            "Sweeping": "Sweeper_Index",
        },

        # Base tactical weights (before sliders)
        "overall_weights": {
            "Shot Stopping": 0.60,
            "Distribution": 0.35,
            "Sweeping": 0.05,
        },

        # Column names for overall score
        "overall_cols": {
            "raw": "GK_Overall_pre_raw",
            "adj": "GK_Overall_adj",
            "pct": "GK_Overall_pct",
        },
    },

    # --- TEMPLATE: WINGER (fill later) --------------------------------------
    # "winger": {
    #     "label": "Winger",
    #     "position_filters": ["Right Winger", "Left Winger"],
    #     "baseline_metrics": {
    #         # e.g. "Expected Assists": lambda df: df["xA"],
    #     },
    #     "indices": {
    #         # e.g. "Attacking_Index": { "metrics": {"xG": 0.5, "xA": 0.5} }
    #     },
    #     "radar_groups": {},
    #     "radar_invert": [],
    #     "group_to_index": {},
    #     "overall_weights": {},
    #     "overall_cols": {
    #         "raw": "Attacker_Overall_pre_raw",
    #         "adj": "Attacker_Overall_adj",
    #         "pct": "Attacker_Overall_pct",
    #     },
    # },
}


# --- LOAD DATA --------------------------------------------------------------

def load_data(path="Final_Task_Data.csv", min_minutes=900):
    df = pd.read_csv(path)
    return df[df["Minutes"] >= min_minutes].copy()


# --- GK UI CONSTANTS (CONVENIENCE) -----------------------------------------

GK_CONFIG = POSITION_CONFIGS["gk"]

GK_SLIDERS = [
    ("Shot Stopping", "Shot Stopping"),
    ("Distribution", "Distribution"),
    ("Sweeping", "Sweeping"),
]

GK_COLS = [
    "ID", "Team", "League",
    "ShotStop_Index", "Distribution_Index", "Sweeper_Index",
    "ShotStop_pct", "Distribution_pct", "Sweeper_pct",
    "GK_Overall_pct", "BuyScore",
    "Age", "Value",
]

GK_TEXT = """
Where else to begin but with the <i>Gatekeepers</i> — the last line of defence.
Choose your preferred <b>priority levels</b> across goalkeeping skill sets to
create a bespoke, data-driven target.
"""

GK_POSITIONS = GK_CONFIG["position_filters"]

# Radar helpers for GK (backwards compatible with your UI)
GK_GROUPS = GK_CONFIG["radar_groups"]
GK_INVERT = set(GK_CONFIG["radar_invert"])


# --- BASELINE METRICS (GENERIC) --------------------------------------------

def make_baseline_metrics(df, config):
    """
    Apply all baseline metric functions for a given position config.
    """
    for name, func in config["baseline_metrics"].items():
        df[name] = func(df)
    return df


# --- INDEX ENGINES (GENERIC) -----------------------------------------------

def compute_indices(df, config):
    """
    Compute all component indices defined in config["indices"].
    Each index is a weighted combination of z-scored metrics.
    """
    for index_name, details in config["indices"].items():
        metrics = details["metrics"]  # dict: col_name -> weight

        # z-score metrics (handles missing cols internally via add_z)
        df = add_z(df, list(metrics.keys()))

        # weighted sum of z-metrics
        df[index_name] = sum(
            weight * df[f"z_{metric_name}"]
            for metric_name, weight in metrics.items()
        )

    return df


# --- COMPONENT PERCENTILES (GENERIC) ---------------------------------------

def add_component_percentiles(df, config):
    """
    For each component index, add a percentile column.
    Uses convention: ShotStop_Index -> ShotStop_pct, etc.
    """
    for index_name in config["indices"].keys():
        pct_name = index_name.replace("_Index", "_pct")
        df[pct_name] = df[index_name].rank(pct=True) * 100
    return df


# --- OVERALL & BUY SCORE (GENERIC) -----------------------------------------

def overall_rating(df, config, slider_multipliers=None):
    """
    Combine component indices into overall rating for a position.

    slider_multipliers: dict mapping radar group -> slider value
    (e.g. {"Shot Stopping": 1.0, "Distribution": 0.9, "Sweeping": 1.1})
    """
    if slider_multipliers is None:
        slider_multipliers = {}

    indices = config["indices"]
    group_to_index = config["group_to_index"]
    base_weights = config["overall_weights"]
    overall_cols = config["overall_cols"]

    index_names = list(indices.keys())
    df = add_z(df, index_names)

    # Apply sliders on top of base tactical weights
    adjusted = {
        group: base_weights[group] * slider_multipliers.get(group, 1.0)
        for group in base_weights
    }

    total = sum(adjusted.values()) or 1.0
    final_w = {g: w / total for g, w in adjusted.items()}

    # Store final weights (optional but nice for debugging/UI)
    for group, idx_name in group_to_index.items():
        w_col = f"w_{idx_name}"
        df[w_col] = final_w[group]

    # Compute raw overall score
    raw_col = overall_cols["raw"]
    df[raw_col] = 0.0
    for group, idx_name in group_to_index.items():
        df[raw_col] += final_w[group] * df[f"z_{idx_name}"]

    # League adjustment (shared logic)
    adj_col = overall_cols["adj"]
    pct_col = overall_cols["pct"]

    df["LeagueMult"] = df["League"].map(LEAGUE_MULTIPLIERS).fillna(
        LEAGUE_MULTIPLIERS["DEFAULT"]
    )
    df[adj_col] = df[raw_col] * df["LeagueMult"]
    df[pct_col] = df[adj_col].rank(pct=True) * 100

    return df


def buy_score(df, config):
    """
    Combine performance, age and value into a BuyScore index.
    Uses the config's overall adjusted column.
    """
    overall_adj_col = config["overall_cols"]["adj"]

    df["Value_million"] = df["Value"].apply(convert_value_to_millions)
    df["Age_Mult"] = df["Age"].apply(age_value_multiplier)

    # Age-adjusted performance
    df["Age_Adjusted_Perf"] = df[overall_adj_col] * df["Age_Mult"]

    # Clamp low values to avoid cheap-player inflation
    df["Value_million_clamped"] = df["Value_million"].clip(lower=0.5)

    # Value efficiency
    df["Value_eff"] = df["Age_Adjusted_Perf"] / np.log1p(df["Value_million_clamped"])

    # Normalize components
    df = add_z(df, ["Age_Adjusted_Perf", "Value_eff", overall_adj_col])

    df["BuyScore"] = (
        0.80 * df["z_Age_Adjusted_Perf"] +
        0.05 * df["z_Value_eff"] +
        0.15 * df[f"z_{overall_adj_col}"]
    )

    return df


# --- SUMMARY TEXT (GK-SPECIFIC, BUT CAN BE CLONED PER POSITION) ------------

def describe_percentile(p):
    if p >= 95:
        return "elite, among the very best"
    if p >= 85:
        return "excellent, well above the majority"
    if p >= 70:
        return "strong, clearly above average"
    if p >= 50:
        return "around the overall average level"
    if p >= 30:
        return "below the average level"
    return "well below the typical standard"


def generate_gk_summary(row):

    ss_desc = describe_percentile(row["ShotStop_pct"])
    d_desc  = describe_percentile(row["Distribution_pct"])
    sw_desc = describe_percentile(row["Sweeper_pct"])

    def orange(val):
        return f"<b><span style='color:#EB881F;'>{val:.0f}</span></b>"

    return f"""
    <div style='color:white; font-size:18px; line-height:1.55; margin-top:1em;'>

    Player <b>{row['ID']}</b> played for <b>{row['Team']}</b> in the <b>{row['League']}</b>.
    Age: <b>{int(row['Age'])}</b>. Market Value: <b>£{row['Value']}</b>.<br><br>

    • <b>Shot Stopping:</b> {orange(row['ShotStop_pct'])} — {ss_desc}.<br>
    • <b>Distribution:</b> {orange(row['Distribution_pct'])} — {d_desc}.<br>
    • <b>Sweeping:</b> {orange(row['Sweeper_pct'])} — {sw_desc}.<br><br>

    <b>Overall Percentile Rank:</b> {orange(row['GK_Overall_pct'])}.<br><br>

    This contributes to his final BuyScore rating.
    </div>
    """


# --- MAIN ENTRYPOINTS -------------------------------------------------------

def run_position_model(
    position_key: str,
    path: str = "Final_Task_Data.csv",
    min_minutes: int = 900,
    slider_multipliers: dict | None = None,
):
    """
    Generic multi-position model runner.
    position_key must exist in POSITION_CONFIGS (e.g. "gk", "winger", etc.)
    """
    config = POSITION_CONFIGS[position_key]

    df = load_data(path, min_minutes)

    # Filter by position(s)
    filters = config["position_filters"]
    mask = df["Position_1"].isin(filters) | df["Position_2"].isin(filters)
    players = df[mask].copy()

    # Pipeline
    players = make_baseline_metrics(players, config)
    players = compute_indices(players, config)
    players = overall_rating(players, config, slider_multipliers)
    players = buy_score(players, config)
    players = add_component_percentiles(players, config)

    return players


def run_gk_model(
    path="Final_Task_Data.csv",
    min_minutes=900,
    Shot_Stopping=1.0,
    Distribution=1.0,
    Sweeping=1.0,
    **kwargs
):
    slider_multipliers = {
        "Shot Stopping": Shot_Stopping,
        "Distribution": Distribution,
        "Sweeping": Sweeping,
    }

    return run_position_model(
        "gk",
        path=path,
        min_minutes=min_minutes,
        slider_multipliers=slider_multipliers,
    )



# --- DEBUG ------------------------------------------------------------------

if __name__ == "__main__":
    gk = run_gk_model() 
