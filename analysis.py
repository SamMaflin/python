import pandas as pd
import numpy as np


# ============================================================
# CONFIG
# ============================================================

LEAGUE_MULTIPLIERS = {
    "Premier League": 1.00,
    "1. Bundesliga": 0.97,
    "Ligue 1": 0.95,
    "Championship": 0.93,
    "Jupiler Pro League": 0.92,
    "2. Bundesliga": 0.92,
    "J1 League": 0.88,
    "Super League": 0.88,
    "Ligue 2": 0.90,
    "Premiership": 0.87,
    "Bundesliga": 0.86,
    "Allsvenskan": 0.85,
    "Eliteserien": 0.84,
    "Challenger Pro League": 0.83,
    "Segunda Liga": 0.84,
    "DEFAULT": 0.85,
}

GK_POSITIONS = ["Goalkeeper"]


# ============================================================
# DATA LOADING
# ============================================================

def load_data(path="Final_Task_Data.csv", min_minutes=900):
    df = pd.read_csv(path)
    df = df[df["Minutes"] >= min_minutes].copy()
    return df


# ============================================================
# UTILS
# ============================================================

def safe_div(num, den):
    """Vectorised safe division."""
    return np.where(den > 0, num / den, np.nan)


def add_z(df, cols):
    """Add z-scores for a list of columns."""
    for col in cols:
        mu = df[col].mean()
        sigma = df[col].std() or 1
        df[f"z_{col}"] = (df[col] - mu) / sigma
    return df


def build_index(df, z_cols, weights, volume_col, volume_target, out_name):
    """
    Generic index-builder:
    - Weighted sum of standardized components
    - Volume-based weighting
    """
    raw = sum(w * df[z] for z, w in zip(z_cols, weights))
    df[f"{out_name}_raw"] = raw

    df[f"{out_name}_weight"] = np.minimum(1, df[volume_col] / volume_target)
    df[f"{out_name}_Index"] = df[f"{out_name}_raw"] * df[f"{out_name}_weight"]

    return df


# ============================================================
# SHOT-STOPPING ENGINE
# ============================================================

def shotstopper_metrics(df):
    df["Save_over_expected"] = df["Save_percentage"] - df["Xsave_percentage"]
    df["GSAx_per_shot"] = safe_div(df["Goals_saved_above_avg"], df["Shots_on_target_faced"])
    df["Avg_xg_per_shot"] = safe_div(df["Np_xg_faced"], df["Shots_on_target_faced"])

    base_metrics = ["Save_over_expected", "GSAx_per_shot", "Avg_xg_per_shot"]
    df = add_z(df, base_metrics)

    # Skill + context
    df["ShotStop_skill"] = 0.6 * df["z_Save_over_expected"] + 0.3 * df["z_GSAx_per_shot"]
    df["ShotStop_context_adj"] = -0.1 * df["z_Avg_xg_per_shot"]
    df["ShotStop_raw"] = df["ShotStop_skill"] + df["ShotStop_context_adj"]

    df["SOT_total"] = df["Shots_on_target_faced"] * (df["Minutes"] / 90)
    df["ShotStop_weight"] = np.minimum(1, df["SOT_total"] / 40)
    df["ShotStop_Index"] = df["ShotStop_raw"] * df["ShotStop_weight"]
    return df


# ============================================================
# DISTRIBUTION ENGINE
# ============================================================

def distribution_metrics(df):
    df["Press_Evasion"] = df["Passing_percentage_under_pressure"] * (df["Percentage_passes_under_pressure"] / 100)
    df["LongPass_Value"] = df["Long_ball_percentage"] * df["Successful_pass_length"]
    df["Progression_Index"] = df["Forward_pass_proportion"] * df["Successful_pass_length"]

    derived = ["Press_Evasion", "LongPass_Value", "Progression_Index"]
    df = add_z(df, derived)

    df = build_index(
        df,
        z_cols=["z_Press_Evasion", "z_LongPass_Value", "z_Progression_Index"],
        weights=[0.4, 0.3, 0.3],
        volume_col="Pass_total",
        volume_target=500,
        out_name="Distribution"
    )

    return df


# ============================================================
# SWEEPER ENGINE
# ============================================================

def sweeper_metrics(df):
    df["Sweeper_Actions"] = df["Defensive_actions"]
    df["Sweeper_Range"] = df["Gk_defesive_action_distance"]
    df["Sweeper_Safety"] = -df["Errors"]  # Fewer errors = better

    metrics = ["Sweeper_Actions", "Sweeper_Range", "Sweeper_Safety"]
    df = add_z(df, metrics)

    df["Sweeper_total"] = df["Sweeper_Actions"] * (df["Minutes"] / 90)

    df = build_index(
        df,
        z_cols=["z_Sweeper_Actions", "z_Sweeper_Range", "z_Sweeper_Safety"],
        weights=[0.45, 0.35, 0.20],
        volume_col="Sweeper_total",
        volume_target=70,
        out_name="Sweeper"
    )

    return df


# ============================================================
# FINAL OVERALL RATING
# ============================================================

def gk_overall(df, ss_input=0.55, d_input=0.3, sw_input=0.15):

    # Add z-scores for final components
    df = add_z(df, ["ShotStop_Index", "Distribution_Index", "Sweeper_Index"])

    # Weighted combination
    df["GK_Overall_raw"] = (
        ss_input * df["z_ShotStop_Index"] +
        d_input * df["z_Distribution_Index"] +
        sw_input * df["z_Sweeper_Index"]
    )

    # League strength adjustment
    df["LeagueMult"] = (
        df["League"]
        .map(LEAGUE_MULTIPLIERS)
        .fillna(LEAGUE_MULTIPLIERS["DEFAULT"])
    )

    df["GK_Overall_adj"] = df["GK_Overall_raw"] * df["LeagueMult"]

    # Percentile ranking
    df["GK_Overall_pct"] = df["GK_Overall_adj"].rank(pct=True) * 100

    return df



# ============================================================
# PIPELINE
# ============================================================

def run_gk_model(path="Final_Task_Data.csv", min_minutes=900):
    df = load_data(path, min_minutes)
    gk = df[(df["Position_1"].isin(GK_POSITIONS)) | (df["Position_2"].isin(GK_POSITIONS))].copy()

    gk = shotstopper_metrics(gk)
    gk = distribution_metrics(gk)
    gk = sweeper_metrics(gk)
    gk = gk_overall(gk)

    return gk


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    gk = run_gk_model()

    print(
        gk.sort_values("GK_Overall_pct", ascending=False)[
            ["ID", "Team", "ShotStop_Index", "Distribution_Index", "Sweeper_Index", "GK_Overall_pct"]
        ].head(20)
    )
