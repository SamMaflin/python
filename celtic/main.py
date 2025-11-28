import streamlit as st
import pandas as pd

# --- Your existing function ---
def load_clean_data(path=r"C:\Users\SMafl\python\celtic\Final_Task_Data.csv", min_mins=900):
    df = pd.read_csv(path)
    df = df[df["Minutes"] >= min_mins]
    return df

import streamlit as st

PASSWORD = "celtic"

st.title("Celtic F.C Recruitment Task")

password = st.text_input("Enter password:", type="password")

if password != PASSWORD:
    st.stop()

st.success("Access granted!")

# rest of your app...













# 
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