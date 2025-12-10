import pandas as pd
import numpy as np

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



data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")

df = calculate_customer_value_metrics(
    data["People_Data"],
    data["Bookings_Data"]
)

print(df)