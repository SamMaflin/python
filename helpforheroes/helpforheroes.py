import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# COLOUR PALETTE (Scalable + Accessible)
# ============================================================
SPEND_COLOR = "#0095FF"        # deep blue
Engagement_COLOR = "#00FF80"     # green-teal
STRATEGIC_COLOR = "#FF476C"    # crimson red


# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_obj):
    """
    Load Excel file and return a dict with People_Data and Bookings_Data
    as DataFrames (empty if missing).
    """
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
    Calculates Spend, Engagement, Strategic scores and assigns customers to a 
    3×3 segmentation matrix.

    Key design choices:
      - SpendScore: composite of Avg + Max booking amount (70% / 30%), normalised 0–100.
      - EngagementScore: combines Frequency, Recency and a blended Diversity metric:
            Diversity = 80% UniqueDestinations + 20% ExplorationRatio.
      - StrategicScore: binary signals (Long-haul, Package, ChannelFit) mapped to 0/100.
      - Segmentation: tertiles on SpendScore and EngagementScore → 3×3 grid.
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

    # ---------------------- Engagement ----------------------
    bookings_df = bookings_df.copy()
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

    people_df = people_df.copy()
    people_df["ChannelFit"] = people_df["Source"].apply(lambda x: int(x in priority_sources))

    strategic = strategic.merge(
        people_df[["Person URN", "ChannelFit"]],
        on="Person URN",
        how="left"
    )

    # ---------------------- COMBINE ----------------------
    df = (
        economic
        .merge(behavioural, left_index=True, right_index=True, how="left")
        .merge(strategic.set_index("Person URN"), left_index=True, right_index=True, how="left")
    ).fillna(0)

    # ============================================================
    # SPEND SCORE (Avg + Max composite with light winsorisation)
    # ============================================================
    # Normalise average spend using percentile ranking
    df["AvgSpendNorm"] = df["AverageBookingAmount"].rank(pct=True) * 100

    # Winsorise max spend at 95th percentile to reduce outlier distortion
    max_cap = df["MaximumBookingAmount"].quantile(0.95)
    df["MaxSpendClipped"] = df["MaximumBookingAmount"].clip(upper=max_cap)
    df["MaxSpendNorm"] = df["MaxSpendClipped"].rank(pct=True) * 100

    # Composite spend score
    df["SpendScore"] = (
        0.7 * df["AvgSpendNorm"] +
        0.3 * df["MaxSpendNorm"]
    ).round(2)

    # ============================================================
    # Engagement SCORE
    # ============================================================

    # ---- Frequency (percentile, not raw scaling)
    freq = df["BookingFrequency"]
    if freq.max() != freq.min():
        df["FrequencyScore"] = freq.rank(pct=True) * 100
    else:
        df["FrequencyScore"] = 0

    # ---- Recency (bucketed holiday cycles; no-booking customers treated as very old)
    rec = df["RecencyDays"].copy()
    # Customers with no bookings should look "old", not 0 days ago
    rec[(df["BookingFrequency"] == 0) | (rec <= 0) | rec.isna()] = 9999

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

    # ---- BLENDED DIVERSITY SCORE
    # Step 1: Normalise components
    unique_min = df["UniqueDestinations"].min()
    unique_range = df["UniqueDestinations"].max() - unique_min + 1e-9
    df["UniqueNorm"] = ((df["UniqueDestinations"] - unique_min) / unique_range) * 100

    explore_min = df["ExplorationRatio"].min()
    explore_range = df["ExplorationRatio"].max() - explore_min + 1e-9
    df["ExploreNorm"] = ((df["ExplorationRatio"] - explore_min) / explore_range) * 100

    # Step 2: Weighted blend (80% breadth, 20% "how exploratory?")
    df["DiversityScore"] = (
        0.8 * df["UniqueNorm"] +
        0.2 * df["ExploreNorm"]
    ).round(2)

    # ---- Final Engagement Score
    df["EngagementScore"] = (
        0.5 * df["FrequencyScore"] +
        0.3 * df["RecencyScore"] +
        0.2 * df["DiversityScore"]
    ).round(2)

    # ============================================================
    # STRATEGIC SCORE
    # ============================================================
    df[["LongHaulAlignment", "PackageAlignment", "ChannelFit"]] = df[
        ["LongHaulAlignment", "PackageAlignment", "ChannelFit"]
    ].fillna(0)

    df["StrategicScore"] = (
        0.5 * (df["LongHaulAlignment"] * 100) +
        0.3 * (df["PackageAlignment"] * 100) +
        0.2 * (df["ChannelFit"] * 100)
    ).round(2)

    # ============================================================
    # SEGMENTATION
    # ============================================================

    spend33, spend66 = df["SpendScore"].quantile([0.33, 0.66])
    act33, act66 = df["EngagementScore"].quantile([0.33, 0.66])

    df["SpendTier"] = np.select(
        [df["SpendScore"] <= spend33, df["SpendScore"] <= spend66, df["SpendScore"] > spend66],
        ["Low Spend", "Mid Spend", "High Spend"],
        default="Unknown"
    ).astype(object)

    df["EngagementTier"] = np.select(
        [df["EngagementScore"] <= act33, df["EngagementScore"] <= act66, df["EngagementScore"] > act66],
        ["Low Engagement", "Mid Engagement", "High Engagement"],
        default="Unknown"
    ).astype(object)

    # ---- Segment Lookup
    segment_map = {
        ("Low Spend", "Low Engagement"): "Dormant Base",
        ("Low Spend", "Mid Engagement"): "Steady Low-Spend",
        ("Low Spend", "High Engagement"): "Engaged Low-Spend",

        ("Mid Spend", "Low Engagement"): "At-Risk Decliners",
        ("Mid Spend", "Mid Engagement"): "Developing Value",
        ("Mid Spend", "High Engagement"): "Loyal Value",

        ("High Spend", "Low Engagement"): "One-Off Premiums",
        ("High Spend", "Mid Engagement"): "Premium Regulars",
        ("High Spend", "High Engagement"): "Premium Loyalists",
    }

    df["Segment"] = df.apply(
        lambda r: segment_map.get((r["SpendTier"], r["EngagementTier"]), "Unclassified"),
        axis=1
    )

    # ---- Descriptions
    descriptions = {
        "Premium Loyalists": "High spend + high Engagement — highest value.",
        "Loyal Value": "Mid spend + high Engagement — strong loyalty.",
        "Engaged Low-Spend": "Low spend + high Engagement — engaged but low value.",
        "Premium Regulars": "High spend + mid Engagement — stable premium group.",
        "Developing Value": "Mid spend + mid Engagement — growth segment.",
        "Steady Low-Spend": "Low spend + mid Engagement — active but low value.",
        "One-Off Premiums": "High spend + low Engagement — reactivation opportunity.",
        "At-Risk Decliners": "Mid spend + low Engagement — declining engagement.",
        "Dormant Base": "Low spend + low Engagement — lowest priority."
    }

    df["SegmentDescription"] = df["Segment"].map(descriptions).fillna("Unclassified group")

    # Final tidy frame with Person URN as a column
    return df.reset_index().rename(columns={"index": "Person URN"})


# ============================================================
# STREAMLIT APP UI
# ============================================================

# -------------------------------
# LOGO (Optional)
# -------------------------------
try:
    st.image("helpforheroes/hfh_logo.png", width=200)
except Exception:
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

/* Small H3 (for Spend / Engagement / Strategic) */
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
<p>Metrics: Average Booking Value, Maximum Booking Value (composited into a 0–100 SpendScore).</p>

<h4><span style="color:{Engagement_COLOR}; font-weight:bold;">● Engagement Score</span> — Engagement & behaviour</h4>
<p>Metrics: Booking Frequency, Destination Diversity, Booking Recency.</p>

<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — Alignment with business goals</h4>
<p>Metrics: Long-Haul participation, Package Adoption, Channel Fit.</p>
""",
    unsafe_allow_html=True
)


# ----------------------
# METRIC CONSTRUCTION
# ----------------------
st.markdown("<h2>Metric Construction</h2>", unsafe_allow_html=True)


# ============================================================
# SPEND SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score (0–100)</span></h3>
    <ul>
        <li><b>Average Booking Amount</b> is the primary financial signal — it avoids inflating scores for frequent travellers and reflects typical spend per holiday.</li>
        <li><b>Maximum Booking Amount</b> picks up occasional high-value or premium purchases that average spend would flatten.</li>
        <li>A composite SpendScore (70% Avg, 30% Max), normalised 0–100, balances stable spend behaviour with sensitivity to premium trips and corrects skewed spend distributions.</li>
    </ul> 
    """,
    unsafe_allow_html=True
)


# ============================================================
# Engagement SECTION
# ============================================================
st.markdown(
    f"""
    <h3 class='small-h3'><span style='color:{Engagement_COLOR}; font-weight:bold;'>Engagement Score (0–100)</span></h3>

    <ul>
        <li>Blends <b>Frequency</b> (percentile of total trips), <b>Recency</b> (bucketed into realistic holiday cycles: 1–5+ years) and a <b>Diversity</b> metric.</li>
        <li>Diversity is a blend of <b>Unique Destinations</b> (breadth of travel) and an <b>Exploration Ratio</b> (unique destinations ÷ trips), rewarding both wide and authentic exploration.</li>
        <li>Weighting of 50% Frequency, 30% Recency, 20% Diversity prioritises ongoing engagement while still surfacing explorers and churn risk.</li>
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
        <li>Long-haul, package adoption, and channel fit are treated as binary strategic signals and mapped to 0/100 for consistency.</li>
        <li>Weighted StrategicScore: Long-Haul (50%), Package (30%), Channel Fit (20%) — reflecting their relative commercial importance.</li>
    </ul>
    """,
    unsafe_allow_html=True
)


# ----------------------
# SEGMENTATION GRID
# ----------------------
st.markdown("<h2>Customer Segmentation Matrix</h2>", unsafe_allow_html=True)

# Show pre-generated matrix plot image
st.image("helpforheroes/matrix_plot.png", use_column_width=True)


# ------------------------------------------------------------
# LOAD DATA + RUN METRICS ENGINE
# ------------------------------------------------------------
data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")

df = calculate_customer_value_metrics(
    data["People_Data"],
    data["Bookings_Data"]
)

# ------------------------------------------------------------
# CUSTOMER BASE vs REVENUE CONTRIBUTION (Improved Butterfly Chart)
# ------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

st.markdown("<h2>Customer Base vs Revenue Contribution</h2>", unsafe_allow_html=True)


# ============================
# 1. DATA PREPARATION
# ============================
cust_counts = (
    df.groupby("Segment")["Person URN"]
    .nunique()
    .rename("CustomerCount")
    .reset_index()
)

total_customers = cust_counts["CustomerCount"].sum()
cust_counts["CustomerShare"] = cust_counts["CustomerCount"] / total_customers * 100


customer_revenue = (
    data["Bookings_Data"]
    .groupby("Person URN")["Cost"]
    .sum()
    .rename("TotalRevenue")
)

df_rev = df.merge(customer_revenue, on="Person URN", how="left").fillna({"TotalRevenue": 0})

rev_segment = (
    df_rev.groupby("Segment")["TotalRevenue"]
    .sum()
    .rename("Revenue")
    .reset_index()
)

total_revenue = rev_segment["Revenue"].sum()
rev_segment["RevenueShare"] = rev_segment["Revenue"] / total_revenue * 100

# Merge
combined = (
    cust_counts.merge(rev_segment, on="Segment", how="left")
    .sort_values("CustomerShare", ascending=True)  # order visually
    .reset_index(drop=True)
)

y = np.arange(len(combined))


# ============================
# 2. COLOUR SCALES (Red → Yellow → Green)
# ============================
cmap = mcolors.LinearSegmentedColormap.from_list("RYG", ["#D32F2F", "#FFEB3B", "#1B5E20"])

# Normalise values 0–100 into 0–1 for colouring
cust_norm = combined["CustomerShare"] / combined["CustomerShare"].max()
rev_norm  = combined["RevenueShare"] / combined["RevenueShare"].max()

cust_colors = [cmap(v) for v in cust_norm]
rev_colors  = [cmap(v) for v in rev_norm]


# ============================
# 3. BUTTERFLY CHART (Dual Positive Axes)
# ============================
fig, ax = plt.subplots(figsize=(14, 10))

bar_height = 0.35

# Left bars — Customer Share
ax.barh(
    y - bar_height/2,
    combined["CustomerShare"],
    color=cust_colors,
    height=bar_height,
    label="Customer Share (%)",
)

# Right bars — Revenue Share using second axis
ax2 = ax.twiny()
ax2.barh(
    y + bar_height/2,
    combined["RevenueShare"],
    color=rev_colors,
    height=bar_height,
    label="Revenue Share (%)",
)


# ============================
# 4. DOTTED GUIDE LINES
# ============================
for yi in y:
    ax.axhline(yi - bar_height/2, color="grey", linestyle="dotted", linewidth=0.7, alpha=0.6)
    ax2.axhline(yi + bar_height/2, color="grey", linestyle="dotted", linewidth=0.7, alpha=0.6)


# ============================
# 5. LABELS & TITLES
# ============================
ax.set_yticks(y)
ax.set_yticklabels(combined["Segment"], fontsize=12)

# Axis titles with larger spacing
ax.set_xlabel("Customer Share (%)", fontsize=13, labelpad=20)
ax2.set_xlabel("Revenue Share (%)", fontsize=13, labelpad=20)

# Main chart title
plt.title(
    "Customer Base vs Revenue Contribution by Segment",
    fontsize=18,
    fontweight="bold",
    pad=30
)

# Matching x-axis limits
max_val = max(combined["CustomerShare"].max(), combined["RevenueShare"].max())
ax.set_xlim(0, max_val * 1.15)
ax2.set_xlim(0, max_val * 1.15)


# ============================
# 6. VALUE LABELS
# ============================
for i, row in combined.iterrows():

    # Customer share labels (left)
    ax.text(
        row["CustomerShare"] + 0.5, i - bar_height/2,
        f"{row['CustomerShare']:.1f}%",
        va="center", fontsize=10
    )

    # Revenue share labels (right)
    ax2.text(
        row["RevenueShare"] + 0.5, i + bar_height/2,
        f"{row['RevenueShare']:.1f}%",
        va="center", fontsize=10
    )

plt.tight_layout()
st.pyplot(fig)

