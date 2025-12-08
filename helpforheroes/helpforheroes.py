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
    font-size: 60px !important;
    font-weight: 700 !important;
    margin: 25px 0 25px 0;
}
.stMarkdown h2 {
    font-size: 50px !important;
    font-weight: 400 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown h3 {
    font-size: 40px !important;
    font-weight: 700 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown p {
    font-size: 25px !important;
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
    "<h3>But how can we measure <span style=\"color:orange; font-weight:bold;\">value</span> among customers?</h3>",
    unsafe_allow_html=True
)


# customer value areas 
# economics
st.markdown(
    "<h3><span style=\"color:orange; font-weight:bold;\">● Economics Value</span></h3><span>How customers contribute financially.</span>",
    unsafe_allow_html=True
)
# behavioural
#st.markdown("<h3>Behavioural Value</h3>",unsafe_allow_html=True)
#st.markdown("<p>How customers engage over time.</p>",unsafe_allow_html=True)
# strategic
#st.markdown("<h3>Strategic Value</h3>",unsafe_allow_html=True)
#st.markdown("<p>How customers support business priorities.</p>",unsafe_allow_html=True)
