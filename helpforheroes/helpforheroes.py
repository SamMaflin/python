import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


# ================================
# DATA LOADING
# ================================
def load_helpforheroes_data(file_obj):
    """
    Load the Excel file from an uploaded file-like object (Streamlit uploader).
    Expects sheets: People_Data and Bookings_Data.
    """
    xls = pd.ExcelFile(file_obj)
    
    # Read all sheets into a dictionary
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    # Ensure People_Data and Bookings_Data are DataFrames even if the sheets are missing
    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data


# ================================
# METRIC ENGINE
# ================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):
    """
    Calculate Economic (Spend), Behavioural (Activity) and Strategic metrics
    at customer (Person URN) level.
    """

    # ============================================================
    #                   MERGE PEOPLE + BOOKINGS DATA
    # ============================================================
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Ensure BookingAmount exists (if your cost column is called 'Cost', rename it before or here)
    if 'BookingAmount' not in merged_df.columns and 'Cost' in merged_df.columns:
        merged_df['BookingAmount'] = merged_df['Cost']
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)

    # ============================================================
    #                   ECONOMIC (MONETARY) VALUE
    # ============================================================
    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max')
    )

    # ============================================================
    #                   BEHAVIOURAL (ACTIVITY) VALUE
    # ============================================================
    # Ensure booking date is datetime
    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='coerce')

    # Reference date for recency (max booking date in dataset)
    reference_date = bookings_df['Booking Date'].max()

    # Simpson Diversity Index function
    def simpson_diversity(destinations):
        counts = destinations.value_counts()
        total = counts.sum()
        if total == 0:
            return 0.0
        p = counts / total
        return 1 - np.sum(p ** 2)

    behavioural_metrics = bookings_df.groupby('Person URN').agg(
        BookingFrequency=('Booking URN', 'count'),
        DestinationDiversityIndex=('Destination', simpson_diversity),
        LastBookingDate=('Booking Date', 'max')
    )

    # Recency (# of days since last booking)
    behavioural_metrics['RecencyDays'] = (
        reference_date - behavioural_metrics['LastBookingDate']
    ).dt.days

    # Drop internal date field
    behavioural_metrics = behavioural_metrics.drop(columns=['LastBookingDate'])

    # Fill missing for customers with no bookings
    behavioural_metrics = behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversityIndex': 0,
        'RecencyDays': np.nan
    })

    # ============================================================
    #                   STRATEGIC FIT VALUE (INDEPENDENT)
    # ============================================================
    # Define long-haul destinations
    long_haul_destinations = [
        'United States', 'USA', 'Australia', 'New Zealand',
        'South Africa', 'Namibia', 'Senegal', 'Mali', 'Kuwait'
    ]

    strategic_temp = bookings_df.groupby('Person URN').agg(
        LongHaulBookings=('Destination', lambda x: np.sum(x.isin(long_haul_destinations))),
        PackageBookings=('Product', lambda x: np.sum(x == 'Package Holiday'))
    )

    strategic_metrics = pd.DataFrame(index=strategic_temp.index)

    # Binary alignment metrics (independent of frequency)
    strategic_metrics['LongHaulAlignment'] = strategic_temp['LongHaulBookings'].apply(
        lambda x: 1 if x > 0 else 0
    )

    strategic_metrics['PackageAlignment'] = strategic_temp['PackageBookings'].apply(
        lambda x: 1 if x > 0 else 0
    )

    # Channel Fit based on People Data
    if priority_sources is None:
        priority_sources = ['Expedia']

    people_df['ChannelFit'] = people_df['Source'].apply(
        lambda x: 1 if x in priority_sources else 0
    )

    strategic_metrics = strategic_metrics.merge(
        people_df[['Person URN', 'ChannelFit']],
        on='Person URN',
        how='left'
    )

    # ============================================================
    #                   MERGE METRIC GROUPS
    # ============================================================
    combined = (
        economic_metrics
        .merge(behavioural_metrics, left_index=True, right_index=True, how='left')
        .merge(strategic_metrics.set_index('Person URN'), left_index=True, right_index=True, how='left')
    )

    return combined


# ================================
# STREAMLIT APP
# ================================

# add logo (optional – make sure the file exists in your repo)
try:
    st.image("helpforheroes/hfh_logo.png", width=200)
except Exception:
    pass

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
st.markdown('<h3>Introduction</h3>', unsafe_allow_html=True)

st.markdown(
    '''
    <p>
    <span style="color:orange; font-weight:bold;">All customers create value</span>
    — just not in the same way.
    Some drive value through big, high-cost bookings, while others do it through consistency,
    returning again and again as loyal repeat trippers. Some help grow priority destinations,
    others favour products that strengthen our portfolio. By examining who our customers are and how they travel,
    we reveal the patterns behind these value types.
    </p>
    ''',
    unsafe_allow_html=True
)

# research question
st.markdown(
    "<h3>But how can we measure <span style=\"color:orange; font-weight:bold;\">value</span> among customers?</h3>",
    unsafe_allow_html=True
)

# --- customer value areas --- # 

# Economic / Spend Value
st.markdown(
    '''
    <h4>
        <span style="color:orange; font-weight:bold;">● Spend — </span>
        <span style="font-weight:300;">How customers contribute financially.</span>
    </h4>
    <p>Metrics: Total Spend, Average Booking Value, Maximum Booking Value</p>
    ''',
    unsafe_allow_html=True
)

# Behavioural / Activity Value
st.markdown(
    '''
    <h4>
        <span style="color:orange; font-weight:bold;">● Activity — </span>
        <span style="font-weight:300;">How customers interact and engage.</span>
    </h4>
    <p>Metrics: Booking Frequency, Destination Diversity Index (Simpson’s), Recency (Days Since Last Booking)</p>
    ''',
    unsafe_allow_html=True
)

# Strategic Fit Value
st.markdown(
    '''
    <h4>
        <span style="color:orange; font-weight:bold;">● Strategic Asset — </span>
        <span style="font-weight:300;">How customers align with business goals.</span>
    </h4>
    <p>Metrics: Long-Haul Alignment, Package Alignment, Channel Fit</p>
    ''',
    unsafe_allow_html=True
)

# ================================
# FILE UPLOAD + METRIC CALCULATION
# ================================

st.markdown("### Upload Data File")

uploaded_file = st.file_uploader(
    "Upload the Excel file containing People_Data and Bookings_Data",
    type=["xls", "xlsx"]
)

if uploaded_file is None:
    st.warning("Please upload an Excel file to continue.")
    st.stop()

data = load_helpforheroes_data(uploaded_file)
people_df = data['People_Data']
bookings_df = data['Bookings_Data']

# calculate all metrics
combined_metrics = calculate_customer_value_metrics(people_df, bookings_df)

# ================================
# METRIC DISTRIBUTIONS
# ================================

st.markdown("<h3>Customer Value Metric Distributions</h3>", unsafe_allow_html=True)

# --- ECONOMIC METRIC DISTRIBUTIONS ---
st.markdown("<h4 style='color:orange;'>Spend Value Distributions</h4>", unsafe_allow_html=True)

economic_cols = ['TotalBookingAmount', 'AverageBookingAmount', 'MaximumBookingAmount']

for col in economic_cols:
    st.markdown(f"<p><b>{col}</b></p>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    ax.hist(combined_metrics[col], bins=20, edgecolor='black')
    ax.set_title(f"Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)

# --- BEHAVIOURAL METRIC DISTRIBUTIONS ---
st.markdown("<h4 style='color:orange;'>Activity Value Distributions</h4>", unsafe_allow_html=True)

behavioural_cols = ['BookingFrequency', 'DestinationDiversityIndex', 'RecencyDays']

for col in behavioural_cols:
    st.markdown(f"<p><b>{col}</b></p>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    ax.hist(combined_metrics[col].dropna(), bins=20, edgecolor='black')
    ax.set_title(f"Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)

# --- STRATEGIC METRIC DISTRIBUTIONS ---
st.markdown("<h4 style='color:orange;'>Strategic Asset Distributions</h4>", unsafe_allow_html=True)

strategic_cols = ['LongHaulAlignment', 'PackageAlignment', 'ChannelFit']

for col in strategic_cols:
    st.markdown(f"<p><b>{col}</b></p>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    value_counts = combined_metrics[col].value_counts().sort_index()
    ax.bar(value_counts.index.astype(str), value_counts.values)
    ax.set_title(f"{col} Distribution")
    ax.set_xlabel("Value (0 = No, 1 = Yes)")
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)
