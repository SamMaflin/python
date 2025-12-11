import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_obj):
    """
    Load Excel file and return a dictionary containing:
    - People_Data
    - Bookings_Data
    
    If sheets are missing, empty DataFrames are returned.
    """
    xls = pd.ExcelFile(file_obj)
    sheets = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    return {
        "People_Data": sheets.get("People_Data", pd.DataFrame()),
        "Bookings_Data": sheets.get("Bookings_Data", pd.DataFrame())
    }


# ============================================================
# MISSING DATA SUMMARY
# ============================================================
def missing_summary(df):
    """
    Returns a DataFrame summarizing missing values for each column:
    - Missing Values: count of NaN entries
    - Percent Missing: % of NaN relative to total rows
    """
    if df.empty:
        return pd.DataFrame(columns=["Missing Values", "Percent Missing"])

    missing_count = df.isna().sum()
    missing_percent = (missing_count / len(df)) * 100

    summary = pd.DataFrame({
        "Missing Values": missing_count,
        "Percent Missing (%)": missing_percent.round(2)
    })

    return summary


# ============================================================
# LOAD DATA + RUN MISSING SUMMARY
# ============================================================
file_obj = "helpforheroes/helpforheroes.xls"
data = load_helpforheroes_data(file_obj)

people_missing = missing_summary(data["People_Data"])
bookings_missing = missing_summary(data["Bookings_Data"])

print("=== Missing Summary: People_Data ===")
print(people_missing)

print("\n=== Missing Summary: Bookings_Data ===")
print(bookings_missing)
