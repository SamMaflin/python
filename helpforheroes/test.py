# ============================================================
# test.py — Customer Insight Metric Engine + Distribution Explorer
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_path):
    """
    Load Excel file with People_Data and Bookings_Data sheets.
    """
    xls = pd.ExcelFile(file_path)
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    # count number of unique customers
    num_customers = data['People_Data']['Person URN'].nunique()
    print(f"Loaded data with {num_customers} unique customers.")

    return data

load_helpforheroes_data('helpforheroes/helpforheroes.xls')