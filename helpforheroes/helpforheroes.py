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
    font-size: 55px !important;
    font-weight: 700 !important;
    margin: 25px 0 25px 0;
}
.stMarkdown h2 {
    font-size: 45px !important;
    font-weight: 400 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown h3 {
    font-size: 35px !important; 
    margin: 20px 0 20px 0;
}
.stMarkdown h4 {
    font-size: 30px !important;
    font-weight: 700 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown p {
    font-size: 22px !important;
    margin: 20px 0 20px 0;
}
</style>
""", unsafe_allow_html=True)

# title
st.markdown("# Help for Heroes Interview Task - Customer Holiday Bookings Insights", unsafe_allow_html=True)


# intro
st.markdown(
    '<h3>'
    'Introduction</h3>',
    unsafe_allow_html=True
)

# intro paragraph
st.markdown(
    '<p>'
    '<span style="color:orange; font-weight:bold;">All customers create value</span>'
    ' — just not in the same way. '
    'Some drive value through big, high-cost bookings, while others do it through consistency, '
    'returning again and again as loyal repeat trippers. Some help grow priority destinations, '
    'others favour products that strengthen our portfolio. By examining who our customers are and how they travel, '
    'we reveal the patterns behind these value types — and identify how we can better support, engage, and grow each of them.'
    '</p>',
    unsafe_allow_html=True
)

# intro
st.markdown(
    "<h3>But how can we measure <span style=\"color:orange; font-weight:bold;\">value</span> among customers?</h2>",
    unsafe_allow_html=True
)


# --- customer value areas --- # 
# economic value
st.markdown(
    '<h4>'
    '<span style="color:orange; font-weight:bold;">● Economic Value — </span>'
    '<span style="font-weight:300;">How customers contribute financially.</span>'
    '</h4>',
    unsafe_allow_html=True
)
# behavioral value
st.markdown(
    '<h4>'
    '<span style="color:orange; font-weight:bold;">● Behavioral Value — </span>'
    '<span style="font-weight:300;">How customers interact and engage.</span>'
    '</h4>',
    unsafe_allow_html=True
)
# strategic value
st.markdown(
    '<h4>'
    '<span style="color:orange; font-weight:bold;">● Strategic Value — </span>'
    '<span style="font-weight:300;">How customers align with business goals.</span>'
    '</h4>',
    unsafe_allow_html=True
)
