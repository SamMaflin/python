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
# FULL METRIC ENGINE + SEGMENTATION (WITH BLENDED DIVERSITY)
# ============================================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):
    """
    Calculates Spend, Activity, Strategic scores and assigns customers to a 
    3×3 segmentation matrix.
    Includes **blended destination diversity metric**:
        80% UniqueDestinations + 20% ExplorationRatio
    """

    # ---------------------- MERGE ----------------------
    merged = pd.merge(people_df, bookings_df, on="Person URN", how="left")

    # Standardise spend column
    if "BookingAmount" not in merged.columns:
        merged["BookingAmount"] = merged["Cost"] if "Cost" in merged.columns else 0
    merged["BookingAmount"] = merged["BookingAmount"].fillna(0)

    # ---------------------- ECONOMIC ----------------------
    economic = merged.groupby("Person URN").agg(
        AverageBookingAmount=("BookingAmount", "mean"),
        MaximumBookingAmount=("BookingAmount", "max"),
        TotalBookings=("BookingAmount", "count")
    )

    # ---------------------- ACTIVITY ----------------------
    bookings_df["Booking Date"] = pd.to_datetime(bookings_df["Booking Date"], errors="coerce")
    reference_date = bookings_df["Booking Date"].max()

    behavioural = bookings_df.groupby("Person URN").agg(
        BookingFrequency=("Booking URN", "count"),
        UniqueDestinations=("Destination", lambda x: x.nunique()),
        LastBookingDate=("Booking Date", "max")
    )

    behavioural["RecencyDays"] = (reference_date - behavioural["LastBookingDate"]).dt.days
    behavioural = behavioural.drop(columns=["LastBookingDate"]).fillna(0)

    # ---- Exploration Ratio (Unique / Frequency), safe divide
    behavioural["ExplorationRatio"] = behavioural.apply(
        lambda r: r["UniqueDestinations"] / r["BookingFrequency"] if r["BookingFrequency"] > 0 else 0,
        axis=1
    )

    # ---------------------- STRATEGIC ----------------------
    long_haul_list = [
        "United States", "USA", "Australia", "New Zealand",
        "South Africa", "Namibia", "Senegal", "Mali", "Kuwait"
    ]

    strategic_temp = bookings_df.groupby("Person URN").agg(
        LongHaulBookings=("Destination", lambda x: np.sum(x.isin(long_haul_list))),
        PackageBookings=("Product", lambda x: np.sum(x == "Package Holiday"))
    )

    strategic = pd.DataFrame(index=strategic_temp.index)
    strategic["LongHaulAlignment"] = (strategic_temp["LongHaulBookings"] > 0).astype(int)
    strategic["PackageAlignment"] = (strategic_temp["PackageBookings"] > 0).astype(int)

    if priority_sources is None:
        priority_sources = ["Expedia"]

    people_df["ChannelFit"] = people_df["Source"].apply(lambda x: int(x in priority_sources))

    strategic = strategic.merge(
        people_df[["Person URN", "ChannelFit"]],
        on="Person URN",
        how="left"
    )

    # ---------------------- COMBINE ----------------------
    df = (
        economic
        .merge(behavioural, left_index=True, right_index=True)
        .merge(strategic.set_index("Person URN"), left_index=True, right_index=True)
    ).fillna(0)

    # ============================================================
    # SPEND SCORE (Avg + Max composite)
    # ============================================================
    df["AvgSpendNorm"] = df["AverageBookingAmount"].rank(pct=True) * 100
    df["MaxSpendNorm"] = df["MaximumBookingAmount"].rank(pct=True) * 100

    df["SpendScore"] = (
        0.7 * df["AvgSpendNorm"] +
        0.3 * df["MaxSpendNorm"]
    ).round(2)

    # ============================================================
    # ACTIVITY SCORE
    # ============================================================

    # ---- Frequency
    freq = df["BookingFrequency"]
    df["FrequencyScore"] = (
        ((freq - freq.min()) / (freq.max() - freq.min())) * 100
        if freq.max() != freq.min() else 0
    )

    # ---- Recency
    rec = df["RecencyDays"]
    df["RecencyScore"] = np.select(
        [
            rec <= 365,
            rec <= 730,
            rec <= 1095,
            rec <= 1460,
            rec <= 1825,
            rec > 1825,
        ],
        [100, 80, 60, 40, 20, 0],
        default=0
    )

    # ---- BLENDED DIVERSITY SCORE (Option B)
    # Step 1: Normalise components
    df["UniqueNorm"] = (
        (df["UniqueDestinations"] - df["UniqueDestinations"].min()) /
        (df["UniqueDestinations"].max() - df["UniqueDestinations"].min() + 1e-9)
    ) * 100

    df["ExploreNorm"] = (
        (df["ExplorationRatio"] - df["ExplorationRatio"].min()) /
        (df["ExplorationRatio"].max() - df["ExplorationRatio"].min() + 1e-9)
    ) * 100

    # Step 2: Weighted blend
    df["DiversityScore"] = (
        0.8 * df["UniqueNorm"] +
        0.2 * df["ExploreNorm"]
    ).round(2)

    # ---- Final Activity Score
    df["ActivityScore"] = (
        0.5 * df["FrequencyScore"] +
        0.3 * df["RecencyScore"] +
        0.2 * df["DiversityScore"]
    ).round(2)

    # ============================================================
    # STRATEGIC SCORE
    # ============================================================
    df["StrategicScore"] = (
        0.5 * (df["LongHaulAlignment"] * 100) +
        0.3 * (df["PackageAlignment"] * 100) +
        0.2 * (df["ChannelFit"] * 100)
    ).round(2)

    # ============================================================
    # SEGMENTATION
    # ============================================================

    spend33, spend66 = df["SpendScore"].quantile([0.33, 0.66])
    act33, act66 = df["ActivityScore"].quantile([0.33, 0.66])

    df["SpendTier"] = np.select(
        [df["SpendScore"] <= spend33, df["SpendScore"] <= spend66, df["SpendScore"] > spend66],
        ["Low Spend", "Mid Spend", "High Spend"],
        default="Unknown"
    ).astype(object)

    df["ActivityTier"] = np.select(
        [df["ActivityScore"] <= act33, df["ActivityScore"] <= act66, df["ActivityScore"] > act66],
        ["Low Activity", "Mid Activity", "High Activity"],
        default="Unknown"
    ).astype(object)

    # ---- Segment Lookup
    segment_map = {
        ("Low Spend", "Low Activity"): "Dormant Base",
        ("Low Spend", "Mid Activity"): "Steady Low-Spend",
        ("Low Spend", "High Activity"): "Engaged Low-Spend",

        ("Mid Spend", "Low Activity"): "At-Risk Decliners",
        ("Mid Spend", "Mid Activity"): "Developing Value",
        ("Mid Spend", "High Activity"): "Loyal Value",

        ("High Spend", "Low Activity"): "One-Off Premiums",
        ("High Spend", "Mid Activity"): "Premium Regulars",
        ("High Spend", "High Activity"): "Premium Loyalists",
    }

    df["Segment"] = df.apply(
        lambda r: segment_map.get((r["SpendTier"], r["ActivityTier"]), "Unclassified"),
        axis=1
    )

    # ---- Descriptions
    descriptions = {
        "Premium Loyalists": "High spend + high activity — highest value.",
        "Loyal Value": "Mid spend + high activity — strong loyalty.",
        "Engaged Low-Spend": "Low spend + high activity — engaged but low value.",
        "Premium Regulars": "High spend + mid activity — stable premium group.",
        "Developing Value": "Mid spend + mid activity — growth segment.",
        "Steady Low-Spend": "Low spend + mid activity — active but low value.",
        "One-Off Premiums": "High spend + low activity — reactivation opportunity.",
        "At-Risk Decliners": "Mid spend + low activity — declining engagement.",
        "Dormant Base": "Low spend + low activity — lowest priority."
    }

    df["SegmentDescription"] = df["Segment"].map(descriptions).fillna("Unclassified group")

    return df.reset_index().rename(columns={"index": "Person URN"})


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
<p>Metrics: Average Booking Value, Maximum Booking Value</p>

<h4><span style="color:{ACTIVITY_COLOR}; font-weight:bold;">● Activity Score</span> — Engagement & behaviour</h4>
<p>Metrics: Booking Frequency, Destination Diversity, Booking Recency</p>

<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — (Optional) Alignment with business goals</h4>
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
        <li>Each Spend metric is right-skewed — a small share of customers generate the majority of revenue.</li>
        <li>This long-tail pattern makes raw spend metrics unsuitable for direct comparison.</li>
    </ul>

    <h4>Fixes:</h4>
    <ul>
        <li>Spend metrics are transformed into a percentile-based SpendScore (0–100).</li>
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
# SEGMENTATION GRID
# ----------------------
st.markdown("<h2>Customer Segmentation Matrix</h2>", unsafe_allow_html=True)

# show matrix
st.image("helpforheroes/matrix_plot.png", use_column_width=True) 


# ------------------------------------------------------------
# LOAD DATA + RUN METRICS ENGINE
# ------------------------------------------------------------
data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")

df = calculate_customer_value_metrics(
    data["People_Data"],
    data["Bookings_Data"]
)

# ------------------------------------------------------------#
# CUSTOMER DISTRIBUTION BY SEGMENT
# ------------------------------------------------------------#
st.markdown("<h2>How Are Customers Distributed by Segment?</h2>", unsafe_allow_html=True)

segment_counts = (
    df["Segment"]
    .value_counts()
    .rename_axis("Segment")
    .reset_index(name="CustomerCount")
)

# count unique Person URNs for total customers
total_customers = df['Person URN'].nunique()
segment_counts["ShareOfBase"] = (segment_counts["CustomerCount"] / total_customers * 100).round(1)
st.dataframe(segment_counts, use_container_width=True)
st.bar_chart(
    segment_counts.set_index("Segment")["CustomerCount"],
    use_container_width=True
)