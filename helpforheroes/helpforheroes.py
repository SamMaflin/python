import pandas as pd
import streamlit as st, numpy as np


def load_helpforheroes_data(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Read all sheets into a dictionary
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    # Ensure People_Data and Bookings_Data are DataFrames even if the sheets are missing
    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data

# calculate economic, behavioural and strategic value metrics 
def calculate_customer_value_metrics(people_df, bookings_df):

    # --- Merge People and Bookings ---
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Ensure BookingAmount column exists and fill missing with 0 (no bookings)
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)

    # --- Economic Value Metrics ---
    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max'),
        MinBookingAmount=('BookingAmount', 'min')  # needed for REV
    )

    # --- Relative Economic Variability (REV) ---
    # REV = (max - min) / average   --> avoid division by zero
    economic_metrics['RelativeEconomicVariability'] = (
        (economic_metrics['MaximumBookingAmount'] - economic_metrics['MinBookingAmount']) /
        economic_metrics['AverageBookingAmount'].replace(0, np.nan)
    ).fillna(0)

    # Drop min column from final output
    economic_metrics = economic_metrics.drop(columns=['MinBookingAmount'])

    return economic_metrics
 

def calculate_behavioral_metrics(bookings_df, reference_date=None):
    """
    Calculates behavioural metrics:
    - Booking Frequency
    - Destination Diversity
    - Recency (days since last booking)
    """

    # ensure Booking Date is datetime
    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='coerce')

    # Use a reference date for recency calculations (e.g. today or max booking date)
    if reference_date is None:
        reference_date = bookings_df['Booking Date'].max()

    # Group by Person URN to compute behavioural metrics
    behavioural_metrics = bookings_df.groupby('Person URN').agg(
        BookingFrequency=('Booking URN', 'count'),
        DestinationDiversity=('Destination', lambda x: x.nunique()),
        LastBookingDate=('Booking Date', 'max')
    )

    # Calculate Recency (days since last booking)
    behavioural_metrics['RecencyDays'] = (reference_date - behavioural_metrics['LastBookingDate']).dt.days

    # Replace NaNs (customers with no bookings)
    behavioural_metrics = behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversity': 0,
        'RecencyDays': np.nan  # No recency for customers without bookings
    })

    # Drop LastBookingDate (internal column)
    behavioural_metrics = behavioural_metrics.drop(columns=['LastBookingDate'])

    return behavioural_metrics



# Open Streamlit App

# add logo
st.image("helpforheroes/hfh_logo.png", width=200)

# styling
st.markdown("""
<style>
.stMarkdown h1 {
    font-size: 55px !important;
    font-weight: 700 !important;
    margin: 25px 0 60px 0;
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
    font-size: 26px !important;
    font-weight: 700 !important;
    margin: 20px 0 20px 0;
}
.stMarkdown p {
    font-size: 22px !important;
    margin: 20px 0 60px 0;
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
    'we reveal the patterns behind these value types.'
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
    '<span style="color:orange; font-weight:bold;">● Monetary — </span>'
    '<span style="font-weight:300;">How customers contribute financially.</span>'
    '</h4>',
    unsafe_allow_html=True
)
# behavioral value
st.markdown(
    '<h4>'
    '<span style="color:orange; font-weight:bold;">● Activity — </span>'
    '<span style="font-weight:300;">How customers interact and engage.</span>'
    '</h4>',
    unsafe_allow_html=True
)
# strategic value
st.markdown(
    '<h4>'
    '<span style="color:orange; font-weight:bold;">● Strategic Fit — </span>'
    '<span style="font-weight:300;">How customers align with business goals.</span>'
    '</h4>',
    unsafe_allow_html=True
)
