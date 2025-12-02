import numpy as np
import pandas as pd 


# safe division
def safe_div(num, den):
    return np.where(den > 0, num / den, np.nan)

# add z-score columns
def add_z(df, cols):
    """Add z-score columns for each feature."""
    for col in cols:
        if col not in df.columns:
            df[f"z_{col}"] = 0.0
            continue
        mu = df[col].mean()
        sd = df[col].std() or 1
        df[f"z_{col}"] = (df[col] - mu) / sd
    return df

# convert monetary value to millions
def convert_value_to_millions(v):
    if pd.isna(v):
        return np.nan
    s = str(v).lower().replace("€", "").replace("£", "").replace(",", "").strip()
    if "m" in s:
        return float(s.replace("m", ""))
    if "k" in s:
        return float(s.replace("k", "")) / 1000
    try:
        return float(s) / 1_000_000
    except Exception:
        return np.nan


# crude age value multiplier
def age_value_multiplier(age):
    """
    Robust, smoothed goalkeeper age curve.
    Peak years = 28 to 32.
    Designed to avoid cliffs and keep age influence moderate.
    """

    # Very young — volatile
    if age <= 20:
        return 0.85

    # Young but improving quickly (21–23)
    if 21 <= age <= 23:
        return 0.90 + 0.02 * (age - 21)    # 0.90 → 0.94

    # Approaching peak (24–27)
    if 24 <= age <= 27:
        return 0.96 + 0.02 * (age - 24)    # 0.96 → 1.02

    # Prime goalkeeper years (28–32)
    if 28 <= age <= 32:
        return 1.08                        # stable peak

    # Mild early decline (33–35)
    if 33 <= age <= 35:
        return 0.95

    # Noticeable decline (36–37)
    if 36 <= age <= 37:
        return 0.85

    # Late-career decline (38–39)
    if 38 <= age <= 39:
        return 0.75

    # Very late (40+)
    return 0.7



# league multipliers based on Average Squad Value (ASV) data from Transfermarkt (2024/25)
LEAGUE_MULTIPLIERS = {
    "Premier League":        1.00,
    "LaLiga":                0.95,
    "Bundesliga":            0.94,
    "Serie A":               0.92,
    "Ligue 1":               0.89,
    "Eredivisie":            0.80,
    "Primeira Liga":         0.78,
    "MLS":                   0.76,
    "Championship":          0.74,
    "2. Bundesliga":         0.70,
    "Swiss Super League":    0.69,
    "Jupiler Pro League":    0.66,
    "Segunda Liga":          0.65,
    "Allsvenskan":           0.60,
    "Eliteserien":           0.58,
    "Challenger Pro League": 0.56,
    "J1 League":             0.67,
    "DEFAULT":               0.60,
}
