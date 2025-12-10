import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



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


# ------------------------------------------------------------
# LOAD DATA + RUN METRICS ENGINE
# ------------------------------------------------------------
data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")

# print unique income values
print(data['People_Data']['Income'].unique())