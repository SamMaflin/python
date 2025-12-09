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

    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

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

    behavioural_metrics['RecencyDays'] = (reference_date - behavioural_metrics['LastBookingDate']).dt.days
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

try:
    st.image("helpforheroes/hfh_logo.png", width=200)
except:
    pass

# -------------------------------
# CSS FIX (Header Spacing)
# -------------------------------
st.markdown("""
<style>
h3.page-header {
    font-size: 60px !important;
    margin-top: 50px !important;
    margin-bottom: 50px !important;
}

h3.section-header {
    font-size: 34px !important;
    margin-top: 20px !important;
    margin-bottom: 10px !important;
}

h4 {
    margin-top: 10px !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# TITLE
# -------------------------------
st.markdown("<h3 class='page-header'>Help for Heroes Interview Task — Customer Holiday Bookings Insights</h3>", unsafe_allow_html=True)


# -------------------------------
# INTRO
# -------------------------------
st.markdown("<h3 class='page-header'>Introduction</h3>", unsafe_allow_html=True)

st.markdown(
    """
<p>
<span style="color:orange; font-weight:bold;">All customers create value</span> — but not in the same way.  
Some generate high spend, others book frequently, and some perfectly match strategic business goals.  
Understanding <b>how</b> each customer contributes enables stronger targeting, segmentation, and strategy.
</p>
""",
    unsafe_allow_html=True
)


# -------------------------------
# VALUE DIMENSIONS
# -------------------------------
st.markdown("<h3 class='page-header'>How do we measure customer value?</h3>", unsafe_allow_html=True)

st.markdown(
    f"""
<h4><span style="color:{SPEND_COLOR}; font-weight:bold;">Spend</span> — Financial contribution</h4>
<p>Metrics: Total Spend, Average Booking Value, Maximum Booking Value</p>

<h4><span style="color:{ACTIVITY_COLOR}; font-weight:bold;">Activity</span> — Engagement & behaviour</h4>
<p>Metrics: Booking Frequency, Destination Diversity, Recency</p>

<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">Strategic</span> — Alignment with business goals</h4>
<p>Metrics: Long-Haul, Package Adoption, Channel Fit</p>
""",
    unsafe_allow_html=True
)


# -------------------------------
# EARLY INSIGHTS
# -------------------------------
st.markdown("<h3 class='page-header'>Early Insights</h3>", unsafe_allow_html=True)

# ============================================================
# SPEND SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='section-header'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend</span></h3>
    <ul>
        <li>Spend is heavily right-skewed — a small group of customers accounts for most revenue.</li>
        <li>This long-tail structure makes raw spend values poor for comparison.</li>
    </ul>

    <h4><span style="color:orange; font-weight:bold;">Fix</span></h4>
    <ul>
        <li>Spend was transformed into a percentile-based SpendScore (0–100).</li>
        <li>This ranks customers relative to the population and handles skew naturally.</li>
    </ul>
    """,
    unsafe_allow_html=True
)

# ============================================================
# ACTIVITY SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='section-header'><span style='color:{ACTIVITY_COLOR}; font-weight:bold;'>Activity</span></h3>

    <ul>
        <li>Booking frequency is low (1–2 bookings for most customers).</li>
        <li>Recency is heavily skewed — very few recent travellers, most last booked 3–5 years ago.</li>
        <li>Destination diversity is polarised: many visit only one destination, few explore widely.</li>
    </ul>

    <h4><span style="color:orange; font-weight:bold;">Fix</span></h4>
    <ul>
        <li>Frequency scaled to 0–100 to align with other metrics.</li>
        <li>Recency bucketed into realistic holiday cycles (1 year, 2 years, etc.).</li>
        <li>Diversity grouped into behavioural buckets (0, 50, 100) to distinguish repeaters vs explorers.</li>
    </ul>
    """,
    unsafe_allow_html=True
)

# ============================================================
# STRATEGIC SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='section-header'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic</span></h3>

    <ul>
        <li>Strategic signals (long-haul, package, channel) are binary and unevenly distributed.</li>
        <li>Raw 0/1 values cannot be compared to other 0–100 value scores.</li>
    </ul>

    <h4><span style="color:orange; font-weight:bold;">Fix</span></h4>
    <ul>
        <li>Converted all strategic indicators to 0 or 100 to match the scoring framework.</li>
        <li>Weighted StrategicScore built: Long-Haul (50%), Package (30%), Channel Fit (20%).</li>
    </ul>
    """,
    unsafe_allow_html=True
)
