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
    """
    Load the Excel file from an uploaded file-like object (Streamlit uploader).
    Expects sheets: People_Data and Bookings_Data.
    """
    xls = pd.ExcelFile(file_obj)
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))
    return data

 
# ============================================================
# FULL METRIC ENGINE — Spend + Activity + Strategic
# ============================================================

def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):
    """
    Computes:
        - Economic Value (Spend)
        - Activity Value (Frequency, Recency, Diversity)
        - Strategic Value (Long-Haul, Package, Channel Fit)
        - SpendScore (0–100 percentile)
        - FrequencyScore (0–100)
        - RecencyScore (holiday-aware)
        - DiversityScore (0, 50, 100)
        - ActivityScore (0–100 weighted)
        - StrategicScore (0–100 weighted)
    Returns:
        Customer-level metrics dataframe.
    """

    # -------------------------------
    # CLEAN + MERGE
    # -------------------------------
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Standardise booking amount
    if 'BookingAmount' not in merged_df.columns and 'Cost' in merged_df.columns:
        merged_df['BookingAmount'] = merged_df['Cost']
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)


    # ============================================================
    # 1. ECONOMIC VALUE — Spend Metrics
    # ============================================================
    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max')
    )


    # ============================================================
    # 2. ACTIVITY VALUE — Behaviour Metrics
    # ============================================================
    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='coerce')
    reference_date = bookings_df['Booking Date'].max()

    # Diversity (Simpson Index)
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

    behavioural_metrics = behavioural_metrics.drop(columns=['LastBookingDate'])

    behavioural_metrics = behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversityIndex': 0,
        'RecencyDays': np.nan
    })


    # ============================================================
    # 3. STRATEGIC VALUE — Alignment Metrics
    # ============================================================
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

    # Channel Fit
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
    # 4. COMBINE RAW METRICS
    # ============================================================
    combined = (
        economic_metrics
        .merge(behavioural_metrics, left_index=True, right_index=True, how='left')
        .merge(strategic_metrics.set_index('Person URN'), left_index=True, right_index=True, how='left')
    )


    # ============================================================
    # 5. SPEND SCORE (Percentile)
    # ============================================================
    combined['SpendPercentile'] = combined['TotalBookingAmount'].rank(pct=True)
    combined['SpendScore'] = (combined['SpendPercentile'] * 100).round(2)


    # ============================================================
    # 6. ACTIVITY TRANSFORMATIONS
    # ============================================================

    # -------------------------------
    # FREQUENCY SCORE (0–100)
    # -------------------------------
    freq = combined['BookingFrequency'].fillna(0)
    combined['FrequencyScore'] = (
        (freq - freq.min()) / (freq.max() - freq.min()) * 100
    ).round(2)

    # -------------------------------
    # RECENCY SCORE (holiday-aware buckets)
    # -------------------------------
    rec = combined['RecencyDays']

    combined['RecencyScore'] = np.select(
        [
            rec <= 365,                # 0–1 year
            rec <= 730,                # 1–2 years
            rec <= 1095,               # 2–3 years
            rec <= 1460,               # 3–4 years
            rec <= 1825,               # 4–5 years
            rec > 1825                 # 5+ years
        ],
        [
            100,
            80,
            60,
            40,
            20,
            0
        ],
        default=0
    )

    # -------------------------------
    # DIVERSITY SCORE (0, 50, 100)
    # -------------------------------
    div = combined['DestinationDiversityIndex'].fillna(0)

    combined['DiversityScore'] = np.select(
        [
            div == 0,
            div <= 0.40,
            div > 0.40
        ],
        [
            0,
            50,
            100
        ]
    ).astype(int)


    # -------------------------------
    # FINAL ACTIVITY SCORE
    # -------------------------------
    combined['ActivityScore'] = (
        0.5 * combined['FrequencyScore'] +
        0.3 * combined['RecencyScore'] +
        0.2 * combined['DiversityScore']
    ).round(2)


    # ============================================================
    # 7. STRATEGIC SCORE (Weighted)
    # ============================================================
    combined['LongHaulScore'] = combined['LongHaulAlignment'].apply(lambda x: 100 if x == 1 else 0)
    combined['PackageScore']  = combined['PackageAlignment'].apply(lambda x: 100 if x == 1 else 0)
    combined['ChannelScore']  = combined['ChannelFit'].apply(lambda x: 100 if x == 1 else 0)

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

# Styling
st.markdown("""
<style>
.stMarkdown h1 { font-size: 60px !important; font-weight: 700 !important; margin: 20px 0 20px 0; }
.stMarkdown h2 { font-size: 50px !important; font-weight: 400 !important; margin: 20px 0 20px 0; }
.stMarkdown h3 { font-size: 40px !important; margin: 150px 0 20px 0; }
.stMarkdown h4 { font-size: 28px !important; font-weight: 700 !important; margin: 20px 0 20px 0; }
.stMarkdown p  { font-size: 22px !important; margin: 20px 0 60px 0; }
</style>
""", unsafe_allow_html=True)


# ----------------------
# TITLE
# ----------------------
st.markdown("# Help for Heroes Interview Task — Customer Holiday Bookings Insights")


# ----------------------
# INTRO SECTION
# ----------------------
st.markdown("<h3>Introduction</h3>", unsafe_allow_html=True)

st.markdown(
    """
<p>
<span style="color:orange; font-weight:bold;">All customers create value</span> — just not in the same way.  
Some generate value through high-cost bookings, others through consistent repeat travel.  
Some help grow priority destinations, others strengthen the product portfolio.  
Understanding <b>how</b> each customer contributes allows us to design better engagement, targeting, and strategy.
</p>
""",
    unsafe_allow_html=True
)


# ----------------------
# VALUE DIMENSIONS
# ----------------------
st.markdown(
    "<hr style='border: 1.5px solid orange; margin-top: 30px; margin-bottom: 10px;'>"
    "<h3>But how can we measure <span style='color:orange; font-weight:bold;'>value</span> among customers?</h3>",
    unsafe_allow_html=True
)

# Spend
st.markdown(
    f"""
<h4><span style="color:{SPEND_COLOR}; font-weight:bold;">● Spend — </span>
<span style="font-weight:300;">How customers contribute financially.</span></h4>
<p>Metrics: Total Spend, Average Booking Value, Maximum Booking Value</p>
""",
    unsafe_allow_html=True,
)

# Activity
st.markdown(
    f"""
<h4><span style="color:{ACTIVITY_COLOR}; font-weight:bold;">● Activity — </span>
<span style="font-weight:300;">How customers interact and engage.</span></h4>
<p>Metrics: Booking Frequency, Destination Diversity Index (Simpson’s), Recency</p>
""",
    unsafe_allow_html=True,
)

# Strategic
st.markdown(
    f"""
<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic — </span>
<span style="font-weight:300;">How customers align with business priorities.</span></h4>
<p>Metrics: Long-Haul Alignment, Package Alignment, Channel Fit</p>
""",
    unsafe_allow_html=True,
)


# ----------------------
# EARLY INSIGHTS
# ----------------------
st.markdown(
    "<hr style='border: 1.5px solid orange; margin-top: 30px; margin-bottom: 10px;'>"
    "<h3>Early Insights...</h3>",
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <h4><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend</span></h4>
    <ul>
        <li>Spend was heavily right-skewed, with a small number of customers contributing the majority of total revenue.</li>
        <li>Raw spend couldn’t be compared directly because a few very high-value customers distorted the scale.</li> 
    </ul>
    <h4><span style="color:orange; font-weight:bold;">Fix</span></h4>
    <ul>
    <li>A percentile-based SpendScore (0–100) was applied.</li>
    <li>Percentiles handle long-tail spend patterns naturally and place each customer relative to the overall population, enabling fair comparison across value segments.</li>
    </ul>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <h4><span style='color:{ACTIVITY_COLOR}; font-weight:bold;'>Activity</span></h4> 
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <h4><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic</span></h4> 
    """,
    unsafe_allow_html=True
)


