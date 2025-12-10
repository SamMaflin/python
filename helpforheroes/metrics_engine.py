import pandas as pd
import numpy as np

# ============================================================
# FULL METRIC ENGINE + NEW 3×3 SEGMENTATION MODEL
# ============================================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):
    """
    Calculates SpendScore, EngagementScore, StrategicScore
    and assigns customers to the NEW 3×3 segmentation:

        Spend Tiers:      Saver → Economy → Premium
        Engagement Tiers: One-Timers → Casuals → Explorers

    Produces 9 new segments, e.g.:
        Premium Explorers, Saver Casuals, Economy One-Timers, etc.
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

    # ---------------------- ENGAGEMENT ----------------------
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

    behavioural["ExplorationRatio"] = behavioural.apply(
        lambda r: r["UniqueDestinations"] / r["BookingFrequency"]
        if r["BookingFrequency"] > 0 else 0,
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

    # ChannelFit
    if priority_sources is None:
        priority_sources = ["Expedia"]

    people_df = people_df.copy()
    people_df["ChannelFit"] = people_df["Source"].apply(lambda x: int(x in priority_sources))

    strategic = strategic.merge(people_df[["Person URN", "ChannelFit"]], on="Person URN", how="left")

    # ---------------------- COMBINE ----------------------
    df = (
        economic
        .merge(behavioural, left_index=True, right_index=True, how="left")
        .merge(strategic.set_index("Person URN"), left_index=True, right_index=True, how="left")
    ).fillna(0)

    # ============================================================
    # SPEND SCORE
    # ============================================================
    df["AvgSpendNorm"] = df["AverageBookingAmount"].rank(pct=True) * 100

    max_cap = df["MaximumBookingAmount"].quantile(0.95)
    df["MaxSpendClipped"] = df["MaximumBookingAmount"].clip(upper=max_cap)
    df["MaxSpendNorm"] = df["MaxSpendClipped"].rank(pct=True) * 100

    df["SpendScore"] = (0.7 * df["AvgSpendNorm"] + 0.3 * df["MaxSpendNorm"]).round(2)

    # ============================================================
    # ENGAGEMENT SCORE
    # ============================================================
    freq = df["BookingFrequency"]
    df["FrequencyScore"] = freq.rank(pct=True) * 100 if freq.max() != freq.min() else 0

    # Recency (keep your thresholds)
    rec = df["RecencyDays"].copy()
    max_real = rec[rec > 0].max()
    rec[(df["BookingFrequency"] == 0) | rec.isna() | (rec <= 0)] = max_real + 1

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

    # Diversity score
    unique_range = df["UniqueDestinations"].max() - df["UniqueDestinations"].min() + 1e-9
    explore_range = df["ExplorationRatio"].max() - df["ExplorationRatio"].min() + 1e-9

    df["UniqueNorm"] = (df["UniqueDestinations"] - df["UniqueDestinations"].min()) / unique_range * 100
    df["ExploreNorm"] = (df["ExplorationRatio"] - df["ExplorationRatio"].min()) / explore_range * 100

    df["DiversityScore"] = (0.8 * df["UniqueNorm"] + 0.2 * df["ExploreNorm"]).round(2)

    df["EngagementScore"] = (
        0.5 * df["FrequencyScore"] +
        0.3 * df["RecencyScore"] +
        0.2 * df["DiversityScore"]
    ).round(2)

    # ============================================================
    # STRATEGIC SCORE
    # ============================================================
    df["StrategicScore"] = (
        0.5 * df["LongHaulAlignment"] * 100 +
        0.3 * df["PackageAlignment"] * 100 +
        0.2 * df["ChannelFit"] * 100
    ).round(2)

    # ============================================================
    # NEW SEGMENTATION — Spend × Engagement
    # ============================================================

    spend33, spend66 = df["SpendScore"].quantile([0.33, 0.66])
    eng33, eng66 = df["EngagementScore"].quantile([0.33, 0.66])

    # Spend tiers → Saver / Economy / Premium
    df["SpendTier"] = np.select(
        [
            df["SpendScore"] <= spend33,
            df["SpendScore"] <= spend66,
            df["SpendScore"] > spend66
        ],
        ["Saver", "Economy", "Premium"],
        default="Unknown"
    )

    # Engagement tiers → One-Timers / Casuals / Explorers
    df["EngagementTier"] = np.select(
        [
            df["EngagementScore"] <= eng33,
            df["EngagementScore"] <= eng66,
            df["EngagementScore"] > eng66
        ],
        ["One-Timers", "Casuals", "Explorers"],
        default="Unknown"
    )

    # ---------------------- NEW SEGMENT GRID ----------------------
    segment_map = {
        ("Saver", "One-Timers"): "Saver One-Timers",
        ("Saver", "Casuals"): "Saver Casuals",
        ("Saver", "Explorers"): "Saver Explorers",

        ("Economy", "One-Timers"): "Economy One-Timers",
        ("Economy", "Casuals"): "Economy Casuals",
        ("Economy", "Explorers"): "Economy Explorers",

        ("Premium", "One-Timers"): "Premium One-Timers",
        ("Premium", "Casuals"): "Premium Casuals",
        ("Premium", "Explorers"): "Premium Explorers",
    }

    df["Segment"] = df.apply(
        lambda r: segment_map.get((r["SpendTier"], r["EngagementTier"]), "Unclassified"),
        axis=1
    )

    # ---------------------- NEW SEGMENT DESCRIPTIONS ----------------------
    descriptions = {
        "Premium Explorers": "High-value, highly engaged frequent travellers.",
        "Premium Casuals": "High spenders with moderate, steady engagement.",
        "Premium One-Timers": "High spend but low repeat activity — strong reactivation potential.",

        "Economy Explorers": "Engaged mid-spend travellers; core repeating customers.",
        "Economy Casuals": "Predictable, mid-spend customers with steady behaviours.",
        "Economy One-Timers": "Occasional mid-spend travellers with low repeat behaviour.",

        "Saver Explorers": "Low spend but highly engaged — budget-active travellers.",
        "Saver Casuals": "Low spend but moderately engaged travellers.",
        "Saver One-Timers": "Low spend + low engagement — lowest commercial priority.",
    }

    df["SegmentDescription"] = df["Segment"].map(descriptions).fillna("Unclassified group")

    return df.reset_index().rename(columns={"index": "Person URN"})
