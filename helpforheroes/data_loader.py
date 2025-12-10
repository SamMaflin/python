import pandas as pd, numpy as np

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

    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data



