import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# COLOUR PALETTE (Scalable + Accessible)
# ============================================================
SPEND_COLOR = "#0095FF"        # deep blue
ACTIVITY_COLOR = "#00FF80"     # green-teal
STRATEGIC_COLOR = "#FF476C"    # crimson red


# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_obj):
    xls = pd.ExcelFile(file_obj)
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))
    return data


# ============================================================
# FULL METRIC ENGINE — Spend + Activity + Strategic
# ============================================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):

    # Merge datasets
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Standardise booking amount
    if 'BookingAmount' not in merged_df.columns and 'Cost' in merged_df.columns:
        merged_df['BookingAmount'] = merged_df['Cost']
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)

    # -------------------------------
    # ECONOMIC VALUE
    # -------------------------------
    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max')
    )

    # -------------------------------
    # ACTIVITY VALUE
    # -------------------------------
    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='coerce')
    reference_date = bookings_df['Booking Date'].max()

    def simpson_diversity(destinations):
        counts = destinations.value_counts()
        if counts.sum() == 0:
            return 0.0
        p = counts / counts.sum()
        return 1 - np.sum(p**2)

    behavioural_metrics = bookings_df.groupby('Person URN').agg(
        BookingFrequency=('Booking URN', 'count'),
        DestinationDiversityIndex=('Destination', simpson_diversity),
        LastBookingDate=('Booking Date', 'max')
    )

    behavioural_metrics['RecencyDays'] = (
        reference_date - behavioural_metrics['LastBookingDate']
    ).dt.days

    behavioural_metrics.drop(columns=['LastBookingDate'], inplace=True)

    behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversityIndex': 0,
        'RecencyDays': np.nan
    }, inplace=True)

    # -------------------------------
    # STRATEGIC VALUE
    # -------------------------------
    long_haul_destinations = [
        'United States', 'USA', 'Australia', 'New Zealand',
        'South Africa', 'Namibia', 'Senegal', 'Mali', 'Kuwait'
    ]

    strategic_temp = bookings_df.groupby('Person URN').agg(
        LongHaulBookings=('Destination', lambda x: np.sum(x.isin(long_haul_destinations))),
        PackageBookings=('Product', lambda x: np.sum(x == 'Package Holiday'))
    )

    strategic_metrics = pd.DataFrame(index=strategic_temp.index)
    strategic_metrics['LongHaulAlignment'] = (strategic_temp['LongHaulBookings'] > 0).astype(int)
    strategic_metrics['PackageAlignment'] = (strategic_temp['PackageBookings'] > 0).astype(int)

    if priority_sources is None:
        priority_sources = ['Expedia']

    people_df['ChannelFit'] = people_df['Source'].apply(lambda x: 1 if x in priority_sources else 0)

    strategic_metrics = strategic_metrics.merge(
        people_df[['Person URN', 'ChannelFit']],
        on='Person URN',
        how='left'
    )

    # -------------------------------
    # COMBINE RAW METRICS
    # -------------------------------
    combined = (
        economic_metrics
        .merge(behavioural_metrics, left_index=True, right_index=True)
        .merge(strategic_metrics.set_index('Person URN'), left_index=True, right_index=True)
    )

    # -------------------------------
    # SPEND SCORE
    # -------------------------------
    combined['SpendPercentile'] = combined['TotalBookingAmount'].rank(pct=True)
    combined['SpendScore'] = (combined['SpendPercentile'] * 100).round(2)

    # -------------------------------
    # ACTIVITY SCORE COMPONENTS
    # -------------------------------
    freq = combined['BookingFrequency'].fillna(0)
    combined['FrequencyScore'] = ((freq - freq.min()) / (freq.max() - freq.min()) * 100).round(2)

    rec = combined['RecencyDays']
    combined['RecencyScore'] = np.select(
        [
            rec <= 365,
            rec <= 730,
            rec <= 1095,
            rec <= 1460,
            rec <= 1825,
            rec > 1825
        ],
        [100, 80, 60, 40, 20, 0],
        default=0
    )

    div = combined['DestinationDiversityIndex'].fillna(0)
    combined['DiversityScore'] = np.select(
        [div == 0, div <= 0.40, div > 0.40],
        [0, 50, 100]
    ).astype(int)

    combined['ActivityScore'] = (
        0.5 * combined['FrequencyScore'] +
        0.3 * combined['RecencyScore'] +
        0.2 * combined['DiversityScore']
    ).round(2)

    # -------------------------------
    # STRATEGIC SCORE
    # -------------------------------
    combined['LongHaulScore'] = combined['LongHaulAlignment'].replace({1: 100, 0: 0})
    combined['PackageScore'] = combined['PackageAlignment'].replace({1: 100, 0: 0})
    combined['ChannelScore'] = combined['ChannelFit'].replace({1: 100, 0: 0})

    combined['StrategicScore'] = (
        0.5 * combined['LongHaulScore'] +
        0.3 * combined['PackageScore'] +
        0.2 * combined['ChannelScore']
    ).round(2)

    return combined



# ============================================================
# STREAMLIT APP UI
# ============================================================

# -------------------------------
# LOGO (Optional)
# -------------------------------
try:
    st.image("helpforheroes/hfh_logo.png", width=200)
except:
    pass

# -------------------------------
# UPDATED CSS WITH TWO H3 CLASSES
# -------------------------------
st.markdown("""
<style>

.stMarkdown h1 { 
    font-size: 60px !important; 
    font-weight: 700 !important; 
    margin: 20px 0 20px 0; 
}

.stMarkdown h2 { 
    font-size: 50px !important; 
    font-weight: 700 !important; 
    margin: 150px 0 20px 0; 
}

/* Large H3 (for main sections) */
h3.big-h3 {
    font-size: 40px !important;
    font-weight: 700 !important;
    margin: 80px 0 20px 0 !important;
}

/* Small H3 (for Spend / Activity / Strategic) */
h3.small-h3 {
    font-size: 34px !important;
    font-weight: 700 !important;
    margin: 25px 0 10px 0 !important;
}

.stMarkdown h4 {
    font-size: 28px !important;
    font-weight: 700 !important;
    margin: 20px 0 10px 0 !important;
}

.stMarkdown p  { 
    font-size: 22px !important; 
    margin: 20px 0 40px 0; 
}

</style>
""", unsafe_allow_html=True)


# ----------------------
# TITLE
# ----------------------
st.markdown("<h1>Help for Heroes Interview Task — Customer Holiday Bookings Insights</h1>", unsafe_allow_html=True)


# ----------------------
# INTRO SECTION
# ----------------------
st.markdown("<h2>Introduction</h2>", unsafe_allow_html=True)

st.markdown(
    """
<p>
<span style="color:orange; font-weight:bold;">All customers create value</span> — just not in the same way.  
Some generate high spend, others show strong behavioural loyalty, and some perfectly align with strategic priorities.  
Understanding <b>how</b> each customer contributes allows us to target better, personalise better, and grow value more effectively.
</p>
""",
    unsafe_allow_html=True
)


# ----------------------
# VALUE DIMENSIONS
# ----------------------
st.markdown("<h2>How Do We Measure Customer Value?</h2>", unsafe_allow_html=True)

st.markdown(
    f"""
<h4><span style="color:{SPEND_COLOR}; font-weight:bold;">● Spend Score</span> — Financial contribution</h4>
<p>Metrics: Total Spend, Average Booking Value, Maximum Booking Value</p>

<h4><span style="color:{ACTIVITY_COLOR}; font-weight:bold;">● Activity Score</span> — Engagement & behaviour</h4>
<p>Metrics: Booking Frequency, Destination Diversity, Recency</p>

<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — Alignment with business goals</h4>
<p>Metrics: Long-Haul, Package Adoption, Channel Fit</p>
""",
    unsafe_allow_html=True
)


# ----------------------
# EARLY INSIGHTS
# ----------------------
st.markdown("<h2>Early Insights</h2>", unsafe_allow_html=True)


# ============================================================
# SPEND SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score</span></h3>
    <ul>
        <li>Spend is heavily right-skewed — a small share of customers generate the majority of revenue.</li>
        <li>This long-tail pattern makes raw spend unsuitable for direct comparison.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>Spend was transformed into a percentile-based SpendScore (0–100).</li>
        <li>This method handles skew naturally and ranks customers fairly across the population.</li>
    </ul>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ACTIVITY SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{ACTIVITY_COLOR}; font-weight:bold;'>Activity Score</span></h3>

    <ul>
        <li>Most customers book only once or twice.</li>
        <li>Recency is highly skewed — very few recent travellers.</li>
        <li>Destination diversity shows polarised behaviour: 
            some customers revisit the same place, while a minority explore widely.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>Frequency scaled to a 0–100 FrequencyScore.</li>
        <li>Recency bucketed into realistic holiday cycles (1 year, 2 years, etc.).</li>
        <li>Diversity grouped into behavioural buckets (0, 50, 100) to distinguish repeaters from explorers.</li>
    </ul>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STRATEGIC SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score</span></h3>

    <ul>
        <li>Long-haul, package adoption, and channel fit are binary strategic signals.</li>
        <li>Raw 0/1 values were incompatible with the 0–100 scaling used elsewhere.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>All strategic indicators were mapped to 0/100 to match the unified scoring framework.</li>
        <li>Weighted StrategicScore created: Long-Haul (50%), Package (30%), Channel Fit (20%).</li>
    </ul>
    """,
    unsafe_allow_html=True
)
