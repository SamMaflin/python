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
    font-size: 50px !important;
    font-weight: 600 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown h3 {
    font-size: 40px !important;
    font-weight: 500 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown p {
    font-size: 20px !important;
    margin: 20px 0 20px 0;
}
</style>
""", unsafe_allow_html=True)

# title
st.markdown("# Help for Heroes Interview Task")

# customer holiday insights
st.markdown(
    '<h2>'
    'Customer Holiday Bookings Insights'
    '</h2>',
    unsafe_allow_html=True
)

# research question
st.markdown(
    '<h3>'
    'Introduction</h3>',
    unsafe_allow_html=True
)


# research question
st.markdown(
    '<p>'
    'All customers create value  — just not in the same way. ' \
    'Some drive value through big, high-cost bookings, while others do it through consistency, ' \
    'returning again and again as loyal repeat trippers. Some help grow priority destinations, ' \
    'others favour products that strengthen our portfolio. This following insight attempts to uncover' \
    ' the different ways value shows up across our customer base. By examining who our customers are and how they travel,' \
    ' we reveal the patterns behind these value types — and identify how we can better support, engage, and grow each of them.'
    '</p>',
    unsafe_allow_html=True
)

