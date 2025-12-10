import pandas as pd, numpy as np


def customer_profiles(df, bookings_df, people_df):
    """
    Renders customer profiles section in Streamlit app.

    Inputs:
        df (DataFrame)           — Output of metrics_engine (contains Segment + Person URN)
        bookings_df (DataFrame)  — Original bookings file (contains Cost + Person URN)
        people_df (DataFrame)    — Original people file (contains Person URN + demographic info)

    Output:
        A Streamlit-rendered customer profiles section
    """

