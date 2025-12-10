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
# FULL METRIC ENGINE + SEGMENTATION
# ============================================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):

    # ---------------------- MERGE ----------------------
    merged = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    if "BookingAmount" not in merged.columns and "Cost" in merged.columns:
        merged["BookingAmount"] = merged["Cost"]

    merged["BookingAmount"] = merged["BookingAmount"].fillna(0)

    # ---------------------- ECONOMIC ----------------------
    economic = merged.groupby("Person URN").agg(
        TotalBookingAmount=("BookingAmount", "sum"),
        AverageBookingAmount=("BookingAmount", "mean"),
        MaximumBookingAmount=("BookingAmount", "max"),
    )

    # ---------------------- ACTIVITY ----------------------
    bookings_df["Booking Date"] = pd.to_datetime(bookings_df["Booking Date"], errors="coerce")
    ref_date = bookings_df["Booking Date"].max()

    def simpson(div):
        counts = div.value_counts()
        if counts.sum() == 0:
            return 0
        p = counts / counts.sum()
        return 1 - np.sum(p**2)

    behavioural = bookings_df.groupby("Person URN").agg(
        BookingFrequency=("Booking URN", "count"),
        DestinationDiversityIndex=("Destination", simpson),
        LastBookingDate=("Booking Date", "max")
    )

    behavioural["RecencyDays"] = (ref_date - behavioural["LastBookingDate"]).dt.days
    behavioural.drop(columns=["LastBookingDate"], inplace=True)

    behavioural.fillna({
        "BookingFrequency": 0,
        "DestinationDiversityIndex": 0,
        "RecencyDays": np.nan
    }, inplace=True)

    # ---------------------- STRATEGIC ----------------------
    long_haul = [
        'United States', 'USA', 'Australia', 'New Zealand',
        'South Africa', 'Namibia', 'Senegal', 'Mali', 'Kuwait'
    ]

    strategic_temp = bookings_df.groupby("Person URN").agg(
        LongHaulBookings=("Destination", lambda x: np.sum(x.isin(long_haul))),
        PackageBookings=("Product", lambda x: np.sum(x == "Package Holiday"))
    )

    strategic = pd.DataFrame(index=strategic_temp.index)
    strategic["LongHaulAlignment"] = (strategic_temp["LongHaulBookings"] > 0).astype(int)
    strategic["PackageAlignment"] = (strategic_temp["PackageBookings"] > 0).astype(int)

    if priority_sources is None:
        priority_sources = ["Expedia"]

    people_df["ChannelFit"] = people_df["Source"].apply(lambda x: 1 if x in priority_sources else 0)

    strategic = strategic.merge(
        people_df[["Person URN", "ChannelFit"]],
        on="Person URN",
        how="left"
    )

    # ---------------------- COMBINE RAW METRICS ----------------------
    df = (
        economic
        .merge(behavioural, left_index=True, right_index=True)
        .merge(strategic.set_index("Person URN"), left_index=True, right_index=True)
    )

    # ---------------------- SPEND SCORE ----------------------
    df["SpendScore"] = (df["TotalBookingAmount"].rank(pct=True) * 100).round(2)

    # ---------------------- ACTIVITY SCORE ----------------------
    freq = df["BookingFrequency"]

    if freq.max() != freq.min():
        df["FrequencyScore"] = ((freq - freq.min()) / (freq.max() - freq.min()) * 100).round(2)
    else:
        df["FrequencyScore"] = 0

    rec = df["RecencyDays"]

    df["RecencyScore"] = np.select(
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

    div = df["DestinationDiversityIndex"]

    df["DiversityScore"] = np.select(
        [div == 0, div <= 0.40, div > 0.40],
        [0, 50, 100]
    )

    df["ActivityScore"] = (
        0.5 * df["FrequencyScore"] +
        0.3 * df["RecencyScore"] +
        0.2 * df["DiversityScore"]
    ).round(2)

    # ---------------------- STRATEGIC SCORE ----------------------
    df["LongHaulScore"] = df["LongHaulAlignment"] * 100
    df["PackageScore"] = df["PackageAlignment"] * 100
    df["ChannelScore"] = df["ChannelFit"] * 100

    df["StrategicScore"] = (
        0.5 * df["LongHaulScore"] +
        0.3 * df["PackageScore"] +
        0.2 * df["ChannelScore"]
    ).round(2)

    # ============================================================
    # SEGMENTATION (3×3 framework)
    # ============================================================
    spend33, spend66 = df["SpendScore"].quantile([0.33, 0.66])
    act33, act66 = df["ActivityScore"].quantile([0.33, 0.66])

    df["SpendTier"] = np.select(
        [df["SpendScore"] <= spend33, df["SpendScore"] <= spend66, df["SpendScore"] > spend66],
        ["Low Spend", "Mid Spend", "High Spend"]
    )

    df["ActivityTier"] = np.select(
        [df["ActivityScore"] <= act33, df["ActivityScore"] <= act66, df["ActivityScore"] > act66],
        ["Low Activity", "Mid Activity", "High Activity"]
    )

    # ---- 9 customer segments ----
    def assign_segment(row):
        if row["ActivityTier"] == "High Activity":
            if row["SpendTier"] == "High Spend": return "Premium Loyalists"
            if row["SpendTier"] == "Mid Spend": return "Loyal Value"
            if row["SpendTier"] == "Low Spend": return "Engaged Low-Spend"

        if row["ActivityTier"] == "Mid Activity":
            if row["SpendTier"] == "High Spend": return "Premium Regulars"
            if row["SpendTier"] == "Mid Spend": return "Developing Value"
            if row["SpendTier"] == "Low Spend": return "Steady Low-Spend"

        if row["ActivityTier"] == "Low Activity":
            if row["SpendTier"] == "High Spend": return "One-Off Premiums"
            if row["SpendTier"] == "Mid Spend": return "At-Risk Decliners"
            if row["SpendTier"] == "Low Spend": return "Dormant Base"

        return "Unclassified"

    df["Segment"] = df.apply(assign_segment, axis=1)

    # ---- Descriptions ----
    desc = {
        "Premium Loyalists": "High spend & high activity — top value core.",
        "Loyal Value": "Frequent mid-spenders showing loyalty & upsell potential.",
        "Engaged Low-Spend": "Low spend but high activity — strong engagement.",
        "Premium Regulars": "High spend but moderate frequency — stable value.",
        "Developing Value": "Mid-spend & mid-activity — customers with growth potential.",
        "Steady Low-Spend": "Consistent low-value users.",
        "One-Off Premiums": "High spend but very inactive — big reactivation upside.",
        "At-Risk Decliners": "Mid-spend users showing reduced activity — churn risk.",
        "Dormant Base": "Low spend & low activity — lowest commercial priority."
    }

    df["SegmentDescription"] = df["Segment"].map(desc)

    return df



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
st.markdown("<h2>Metric Construction</h2>", unsafe_allow_html=True)


# ============================================================
# SPEND SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score (0–100)</span></h3>
    <ul>
        <li>Each Spend metric is heavily right-skewed — a small share of customers generate the majority of revenue.</li>
        <li>This long-tail pattern makes raw spend metrics unsuitable for direct comparison.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>Spend metrics are transformed into a percentile-based SpendScore (0–100).</li>
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
    <h3 class='small-h3'><span style='color:{ACTIVITY_COLOR}; font-weight:bold;'>Activity Score (0–100)</span></h3>

    <ul>
        <li>Most customers book only once or twice.</li>
        <li>Recency metric is highly skewed — very few recent travellers.</li>
        <li>Destination diversity metric shows polarised behaviour: 
            some customers revisit the same place, while a minority explore widely.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>Frequency metric scaled to a 0–100 FrequencyScore.</li>
        <li>Recency metric bucketed into realistic holiday cycles (1 year, 2 years, ... 5+ years ).</li>
        <li>Diversity metric grouped into behavioural buckets (0, 50, 100) to distinguish repeaters from explorers.</li>
    </ul>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STRATEGIC SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score (0–100)</span></h3>

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


# ----------------------
# SEGMENTATION ANALYSIS
# ----------------------
st.markdown("<h2>Segmentation Insights</h2>", unsafe_allow_html=True)

st.markdown("Customer Value Matrix (Spend × Activity)")

segment_grid = [
    ["Premium Loyalists", "Loyal Value", "Engaged Low-Spend"],
    ["Premium Regulars", "Developing Value", "Steady Low-Spend"],
    ["One-Off Premiums", "At-Risk Decliners", "Dormant Base"]
]

colors = {
    "Premium Loyalists": "#1f77b4",
    "Loyal Value": "#2ca02c",
    "Engaged Low-Spend": "#17becf",
    "Premium Regulars": "#9467bd",
    "Developing Value": "#8c564b",
    "Steady Low-Spend": "#bcbd22",
    "One-Off Premiums": "#ff7f0e",
    "At-Risk Decliners": "#d62728",
    "Dormant Base": "#7f7f7f"
}

for row in segment_grid:
    cols = st.columns(3)
    for idx, segment in enumerate(row):
        with cols[idx]:
            st.markdown(
                f"""
                <div style='padding:15px; border-radius:10px; 
                background-color:{colors[segment]}; color:white; text-align:center;'>
                    <b>{segment}</b>
                </div>
                """, unsafe_allow_html=True
            )
