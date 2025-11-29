import streamlit as st
import pandas as pd
import numpy as np

# ==========================================================
# THEME CONSTANTS
# ==========================================================

FONT_FAMILY = "'Belleza', sans-serif"
COLOR_BG_MAIN = "#1A5638"
COLOR_BG_SIDEBAR = "#15472F"
COLOR_TEXT = "white"
LOGO_PATH = "/celtic_logo.png"
LOGO_SIZE = "350px"

TITLE_SIZE_H1 = "80px"
TITLE_SIZE_H3 = "60px"
BODY_FONT_SIZE = "22px"


# ==========================================================
# STYLESHEET (CSS)
# ==========================================================

CELTIC_CSS = f"""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Belleza&display=swap');

    /* Global font + text color */
    * {{
        font-family: {FONT_FAMILY} !important;
        color: {COLOR_TEXT} !important;
    }}

    /* Headings */
    h1 {{
        font-size: {TITLE_SIZE_H1} !important;
        font-weight: 600 !important;
        letter-spacing: -1px !important;
        line-height: 1 !important;
        padding-bottom: 10% !important;
    }}

    h3 {{
        font-size: {TITLE_SIZE_H3} !important;
        font-weight: 600 !important;
        letter-spacing: -1px !important;
        line-height: 1 !important;
    }}

    p {{
        font-size: {BODY_FONT_SIZE} !important;
    }}

    /* Application background */
    .stApp {{
        background-color: {COLOR_BG_MAIN} !important;
        background-image: url("{LOGO_PATH}") !important;
        background-repeat: no-repeat;
        background-attachment: fixed !important;
        background-position: center center !important;
        background-size: {LOGO_SIZE} !important;
    }}

    /* Header bar */
    header[data-testid="stHeader"] {{
        background-color: {COLOR_BG_MAIN} !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BG_SIDEBAR} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {COLOR_TEXT} !important;
    }}

    /* Selectbox label fix */
    .stSelectbox label {{
        color: {COLOR_TEXT} !important;
    }}
</style>
"""


# ==========================================================
# INJECT CSS
# ==========================================================

st.markdown(CELTIC_CSS, unsafe_allow_html=True)


# ==========================================================
# DATA LOADING + CLEANING
# ==========================================================

DEFAULT_DATA_PATH = "Final_Task_Data.csv"
DEFAULT_MIN_MINUTES = 900

def load_clean_data(path: str = DEFAULT_DATA_PATH, min_minutes: int = DEFAULT_MIN_MINUTES) -> pd.DataFrame:
    """
    Load the player dataset and filter out players below the minimum playing time threshold.

    Parameters
    ----------
    path : str
        File path to the CSV dataset.
    min_minutes : int
        Minimum number of minutes required to include a player.

    Returns
    -------
    pd.DataFrame
        Cleaned player data.
    """
    df = pd.read_csv(path)
    return df[df["Minutes"] >= min_minutes]


df = load_clean_data()


# ==========================================================
# PAGE HEADER + INTRO
# ==========================================================

st.title("Celtic F.C. Player Evaluation Task")

INTRO_TEXT = """
Welcome. This application assists in identifying potential player recruitment targets by analysing key 
performance indicators that highlight the profile and attributes of each player in the dataset.
<br><br>
For the purposes of this assignment, <b>four</b> players have been automatically identified as suitable 
candidates for Celtic F.C. You can also use the optional sliders to refine the criteria and explore 
alternative player fits.
"""

st.markdown(INTRO_TEXT, unsafe_allow_html=True)

st.subheader("Let's get started...")




















# def calculate_shot_stopping_rating(df):
#     """
#     Computes a goalkeeper shot-stopping value from 1–99.
#     Automatically derives advanced metrics:
#     - SavePlus
#     - GSA_Rate
#     - SDI
#     Based on modern GK analytics.
#     """
# 
#     df = df['Position'].copy()
#     eps = 1e-6
# 
#     # ==========================================================
#     # 1. DERIVED ADVANCED SHOT-STOPPING METRICS
#     # ==========================================================
# 
#     # Save% minus expected save%
#     df["SavePlus"] = df["Save_percentage"] - df["Xsave_percentage"]
# 
#     # Goals Saved Above Average per shot
#     df["GSA_Rate"] = df["Goals_saved_above_avg"] / (df["Shots_on_target_faced"] + eps)
#     df["GSA_Rate"].replace([np.inf, -np.inf], np.nan, inplace=True)
#     df["GSA_Rate"].fillna(0, inplace=True)
# 
#     # Shot Difficulty Index: PSxG per shot on target
#     df["SDI"] = df["Np_psxg_faced"] / (df["Shots_on_target_faced"] + eps)
#     df["SDI"].replace([np.inf, -np.inf], np.nan, inplace=True)
#     df["SDI"].fillna(0, inplace=True)
# 
#     # ==========================================================
#     # 2. METRIC WEIGHTS (COMPREHENSIVE MODERN MODEL)
#     # ==========================================================
# 
#     metric_weights = {
#         "Save_percentage": 0.25,
#         "Xsave_percentage": 0.25,
#         "Goals_saved_above_avg": 0.20,
#         "SavePlus": 0.10,
#         "GSA_Rate": 0.10,
#         "SDI": 0.10,
#     }
# 
#     # ==========================================================
#     # 3. PERCENTILE NORMALISATION (for each metric)
#     # ==========================================================
# 
#     pct_df = pd.DataFrame(index=df.index)
# 
#     for metric, weight in metric_weights.items():
# 
#         if metric not in df.columns:
#             continue
# 
#         # Percentile rank → 0 to 100
#         pct_df[metric] = df[metric].rank(pct=True) * 100
#         pct_df[metric].fillna(50, inplace=True)
# 
#     # ==========================================================
#     # 4. WEIGHTED FINAL SCORE
#     # ==========================================================
# 
#     final_score = sum(
#         pct_df[m] * w for m, w in metric_weights.items() if m in pct_df
#     )
# 
#     # convert to 1–99
#     shot_rating = (
#         (final_score / 100)
#         .clip(lower=1, upper=99)
#         .round()
#         .astype(int)
#     )
# 
#     # ==========================================================
#     # 5. RETURN SIMPLE RATING TABLE
#     # ==========================================================
# 
#     result = pd.DataFrame({
#         "ID": df["ID"],
#         "ShotStopping_1_99": shot_rating
#     })
# 
#     return result
# 
# 
# df = load_clean_data()
# shot_ratings = calculate_shot_stopping_rating(df)
# 
# print(shot_ratings.sort_values("ShotStopping_1_99", ascending=False).head(10))
# 