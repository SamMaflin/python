import pandas as pd

def load_helpforheroes_data(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Read all sheets into a dictionary
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    # Ensure People_Data and Bookings_Data are DataFrames even if the sheets are missing
    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data

# Open Streamlit App add title and app description about customer segmentation
import streamlit as st

# include logo
st.image("helpforheroes/hfh_logo.png", width=200)
st.title("Help for Heroes Interview Task")
st.subheader("What makes a customer <b>high-value</b> — and how can we acquire more customers like them?")
 
