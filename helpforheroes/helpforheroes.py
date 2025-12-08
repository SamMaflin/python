import pandas as pd
import streamlit as st


def load_helpforheroes_data(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Read all sheets into a dictionary
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    # Ensure People_Data and Bookings_Data are DataFrames even if the sheets are missing
    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data

# Open Streamlit App

# add logo
st.image("helpforheroes/hfh_logo.png", width=200)

# styling
st.markdown("""
<style>
.stMarkdown h1 {
    font-size: 75px !important;
    font-weight: 700 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown h2 {
    font-size: 45px !important;
    font-weight: 500 !important;
    margin: 15px 0 15px 0;
}
.stMarkdown h3 {
    font-size: 25px !important;
    font-weight: 400 !important;
    margin: 15px 0 15px 0;
}
</style>
""", unsafe_allow_html=True)

# title
st.markdown("# Help for Heroes Interview Task")

# customer holiday insights
st.markdown(
    '<h2 style="font-size: 50px; font-weight: 400;">'
    'Customer Holiday Bookings Deep Dive'
    '</h2>',
    unsafe_allow_html=True
)

# research question
st.markdown(
    '<h3 style="font-size: 50px; font-weight: 400;">'
    '<b>Question:</b> What makes a customer <span style="color: orange;"><b>high-value</b></span> — '
    'and how can we acquire more customers like them?'
    '</h3>',
    unsafe_allow_html=True
)

