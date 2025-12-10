import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_obj):
    """
    Load Excel file and return a dict with People_Data and Bookings_Data
    as DataFrames (empty if missing).
    """
    xls = pd.ExcelFile(file_obj)
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    data["People_Data"] = pd.DataFrame(data.get("People_Data", pd.DataFrame()))
    data["Bookings_Data"] = pd.DataFrame(data.get("Bookings_Data", pd.DataFrame()))

    return data


# Print unique booking data destination, continent and product
def summarize_booking_data(bookings_df):
    if bookings_df.empty:
        print("No booking data available.")
        return

    destinations = bookings_df['Destination'].dropna().unique()
    continents = bookings_df['Continent'].dropna().unique()
    products = bookings_df['Product'].dropna().unique()

    print("Unique Destinations:", destinations)
    print("Unique Continents:", continents)
    print("Unique Products:", products)


# ============================================================
# FIX: Load file and call the function properly
# ============================================================

# Example: replace 'your_file.xlsx' with your actual file object or path
file_obj = "helpforheroes/helpforheroes.xls"

data = load_helpforheroes_data(file_obj)
bookings_df = data["Bookings_Data"]

summarize_booking_data(bookings_df)
