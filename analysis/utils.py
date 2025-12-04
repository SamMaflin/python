import numpy as np
import pandas as pd

# ---------------------------------------------------------
# SAFE DIVISION
# ---------------------------------------------------------
def safe_div(num, den):
    """Avoid divide-by-zero by returning NaN when denominator <= 0."""
    return np.where(den > 0, num / den, np.nan)

# ---------------------------------------------------------
# Z-SCORES
# ---------------------------------------------------------
def add_z(df, cols):
    """Add z-scored versions of each column in 'cols'."""
    for col in cols:
        if col not in df.columns:
            df[f"z_{col}"] = 0.0
            continue
        mu = df[col].mean()
        sd = df[col].std()
        if sd == 0 or pd.isna(sd):
            sd = 1
        df[f"z_{col}"] = (df[col] - mu) / sd
    return df

# ---------------------------------------------------------
# VALUE → £ MILLIONS
# ---------------------------------------------------------
def convert_value_to_millions(value):
    """Convert '£3.2m' / '500k' / '2000000' → consistent millions."""
    if pd.isna(value):
        return np.nan
    s = str(value).lower().replace("€", "").replace("£", "").replace(",", "").strip()
    if "m" in s:
        return float(s.replace("m", ""))
    if "k" in s:
        return float(s.replace("k", "")) / 1000
    try:
        return float(s) / 1_000_000
    except:
        return np.nan

# ---------------------------------------------------------
# AGE MULTIPLIER — RECRUITMENT OPTIMISED
# ---------------------------------------------------------
def age_value_multiplier(age, peak=24.5, width=4.5):
    return np.exp(-((age - peak)**2) / (2 * width**2))


# ---------------------------------------------------------
# LEAGUE MULTIPLIERS (2024/25 ASV)
# ---------------------------------------------------------
LEAGUE_MULTIPLIERS = {
    "Premier League": 1.00,
    "1. Bundesliga": 0.94,
    "Bundesliga": 0.81,
    "Ligue 1": 0.93,
    "Ligue 2": 0.80,
    "Jupiler Pro League": 0.87,
    "Challenger Pro League": 0.80,
    "Championship": 0.86,
    "J1 League": 0.83,
    "Eliteserien": 0.83,
    "Allsvenskan": 0.82,
    "Super League": 0.83,
    "Segunda Liga": 0.81,
    "Premiership": 0.81,
    "DEFAULT": 0.80
}


def add_z_by_league(df, metrics, league_col="League", clip=3.0):
    for m in metrics:
        if m not in df.columns:
            df[f"z_{m}"] = 0
            continue

        g = df.groupby(league_col)[m]
        mean = g.transform("mean")
        std = g.transform("std").replace(0, np.nan)

        df[f"z_{m}"] = (df[m] - mean) / std
        df[f"z_{m}"] = df[f"z_{m}"].fillna(0.0)
        if clip:
            df[f"z_{m}"] = df[f"z_{m}"].clip(-clip, clip)

    return df



def percentile_phrase(p):
    if p >= 95: return "elite, among the very best"
    if p >= 85: return "excellent, well above average"
    if p >= 70: return "strong, clearly above average"
    if p >= 50: return "around average"
    if p >= 30: return "below average"
    return "poor relative to the dataset"