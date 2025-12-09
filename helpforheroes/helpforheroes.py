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

    # print unqiue destination in bookings data
    unique_destinations = data['Bookings_Data']['Destination'].unique()
    print(f"Unique Destinations in Bookings Data: {unique_destinations}")

    return data

# calculate metrics
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):

    # ------- Merge Data -------
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Ensure BookingAmount exists
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)

    # ============================================================
    #                   ECONOMIC VALUE METRICS
    # ============================================================

    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max'),
        MinBookingAmount=('BookingAmount', 'min')
    )

    # Relative Economic Variability
    economic_metrics['RelativeEconomicVariability'] = (
        (economic_metrics['MaximumBookingAmount'] - economic_metrics['MinBookingAmount']) /
        economic_metrics['AverageBookingAmount'].replace(0, np.nan)
    ).fillna(0)

    economic_metrics = economic_metrics.drop(columns=['MinBookingAmount'])

    # ============================================================
    #                   BEHAVIOURAL VALUE METRICS
    # ============================================================

    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='ignore')

    reference_date = bookings_df['Booking Date'].max()

    behavioural_metrics = bookings_df.groupby('Person URN').agg(
        BookingFrequency=('Booking URN', 'count'),
        DestinationDiversity=('Destination', lambda x: x.nunique()),
        LastBookingDate=('Booking Date', 'max')
    )

    behavioural_metrics['RecencyDays'] = (
        reference_date - behavioural_metrics['LastBookingDate']
    ).dt.days

    behavioural_metrics = behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversity': 0,
        'RecencyDays': np.nan
    })

    behavioural_metrics = behavioural_metrics.drop(columns=['LastBookingDate'])

    # ============================================================
    #                   STRATEGIC VALUE METRICS
    # ============================================================

    # Define long-haul destinations
    long_haul_destinations = [
        'United States', 'USA', 'Australia', 'New Zealand',
        'South Africa', 'Namibia', 'Senegal', 'Mali', 'Kuwait'
    ]

    strategic_temp = bookings_df.groupby('Person URN').agg(
        TotalBookings=('Booking URN', 'count'),
        LongHaulBookings=('Destination', lambda x: sum(x.isin(long_haul_destinations))),
        PackageBookings=('Product', lambda x: sum(x == 'Package Holiday'))
    )

    strategic_metrics = pd.DataFrame(index=strategic_temp.index)

    # Long-haul alignment
    strategic_metrics['LongHaulShare'] = (
        strategic_temp['LongHaulBookings'] /
        strategic_temp['TotalBookings'].replace(0, np.nan)
    ).fillna(0)

    # Package holiday alignment
    strategic_metrics['PackageShare'] = (
        strategic_temp['PackageBookings'] /
        strategic_temp['TotalBookings'].replace(0, np.nan)
    ).fillna(0)

    # Channel Fit (based on People Data)
    if priority_sources is None:
        priority_sources = ['Expedia']   # Example — change if you prefer

    people_df['ChannelFit'] = people_df['Source'].apply(
        lambda x: 1 if x in priority_sources else 0
    )

    strategic_metrics = strategic_metrics.merge(
        people_df[['Person URN', 'ChannelFit']],
        on='Person URN',
        how='left'
    )

    # ============================================================
    #                   MERGE ALL VALUE DIMENSIONS
    # ============================================================

    combined = (
        economic_metrics
        .merge(behavioural_metrics, left_index=True, right_index=True, how='left')
        .merge(strategic_metrics.set_index('Person URN'), left_index=True, right_index=True, how='left')
    )

    return combined



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

# research question
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
    '<span style="font-weight:300;">How customers align with business goals (For purposes of our analysis the following destinations are considered long-haul priorities: \'United States\', \'USA\', \'Australia\', \'New Zealand\','
        'South Africa\', \'Namibia\', \'Senegal\', \'Mali\', \'Kuwait\').</span>'
    '</h4>',
    unsafe_allow_html=True
)


# load
data = load_helpforheroes_data('helpforheroes/helpforheroes.xls')