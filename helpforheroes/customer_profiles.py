import pandas as pd
import numpy as np


# ============================================================
# 1. DEMOGRAPHICS → Clean DOB → Age → AgeBracket
# ============================================================
def prepare_people_data(people_df):
    people = people_df.copy()

    # Convert DOB → datetime
    people["DOB"] = pd.to_datetime(
        people["DOB"], format="%d/%m/%Y", errors="coerce"
    )

    # Compute Age (years) relative to today
    today = pd.Timestamp("today")
    people["Age"] = people["DOB"].apply(
        lambda d: int((today - d).days / 365.25) if pd.notnull(d) else np.nan
    )

    # Age Brackets
    bins = [0, 29, 39, 49, 59, 69, 200]
    labels = ["18–29", "30–39", "40–49", "50–59", "60–69", "70+"]

    people["AgeBracket"] = pd.cut(
        people["Age"], bins=bins, labels=labels, include_lowest=True
    )

    return people


# ============================================================
# 2. BEHAVIOURAL VARIABLES → FrequencyBand + RecencyBand
# ============================================================
def derive_booking_behaviour(bookings_df):
    bookings = bookings_df.copy()

    # Convert booking date
    bookings["Booking Date"] = pd.to_datetime(
        bookings["Booking Date"], format="%d/%m/%Y", errors="coerce"
    )

    today = pd.Timestamp("today")

    # ---- Booking frequency per person ----
    bookings_per_person = (
        bookings.groupby("Person URN")["Booking URN"].count()
        .rename("Frequency")
    )

    def frequency_band(n):
        if n == 1:  return "One-Time"
        if n <= 3: return "Occasional"
        if n <= 6: return "Regular"
        return "Frequent"

    freq_band = bookings_per_person.apply(frequency_band).rename("FrequencyBand")

    # ---- Recency: days since last booking ----
    last_booking_date = (
        bookings.groupby("Person URN")["Booking Date"].max()
        .rename("LastBooking")
    )

    recency_days = (today - last_booking_date).dt.days.rename("RecencyDays")

    def recency_band(d):
        if d <= 90:  return "Very Recent"
        if d <= 180: return "Recent"
        if d <= 365: return "Lapsed"
        return "Dormant"

    rec_band = recency_days.apply(recency_band).rename("RecencyBand")

    # Combine into a single behaviour table
    behaviour = pd.concat(
        [bookings_per_person, freq_band, last_booking_date, recency_days, rec_band],
        axis=1
    )

    return behaviour


# ============================================================
# 3. POPULATION BASELINE (global distribution)
# ============================================================
def population_baseline(prof_df, field):
    counts = prof_df[field].value_counts(dropna=False)
    return counts / counts.sum()


# ============================================================
# 4. SEGMENT DISTRIBUTION (within-segment distribution)
# ============================================================
def segment_distribution(prof_df, field):
    counts = prof_df.groupby(["Segment", field])["Person URN"].count()
    return counts / counts.groupby(level=0).sum()


# ============================================================
# 5. DOMINANCE TABLE → Over/Under representation per segment
# ============================================================
def dominance_table(prof_df, field):
    pop_pct = population_baseline(prof_df, field)
    seg_pct = segment_distribution(prof_df, field)

    # Align population % to match multiindex shape
    aligned_pop = pop_pct.reindex(seg_pct.index.get_level_values(field)).values

    df = pd.DataFrame({
        "Segment %": seg_pct,
        "Population %": aligned_pop
    })

    # Representation Index = Segment% / Population%
    df["Index"] = df["Segment %"] / df["Population %"]

    # Difference in percentage points
    df["Difference (pp)"] = df["Segment %"] - df["Population %"]

    # Categorise dominance meaningfully
    def classify(idx):
        if pd.isna(idx): return "No data"
        if idx >= 2.0:  return "HIGHLY dominant"
        if idx >= 1.5:  return "Strongly dominant"
        if idx >= 1.2:  return "Moderately over-represented"
        if idx > 0.8:   return "Normal presence"
        return "Under-represented"

    df["Dominance"] = df["Index"].apply(classify)

    return df


# ============================================================
# 6. FULL SEGMENTATION BREAKDOWN
#    Merge → Demographics + Behaviour → Dominance Analysis
# ============================================================
def full_segmentation_breakdown(df, bookings_df, people_df):
    """
    df           = segmentation output (Person URN, Segment)
    bookings_df  = raw booking data
    people_df    = raw demographics dataset
    """

    # Prepare demographics
    people_clean = prepare_people_data(people_df)

    # Prepare behavioural features
    behaviour = derive_booking_behaviour(bookings_df)

    # Merge all into profiling dataset
    prof_df = (
        df.merge(people_clean, on="Person URN", how="left")
          .merge(behaviour, on="Person URN", how="left")
    )

    # Fields to run dominance analysis on
    profiling_fields = [
        "AgeBracket",
        "Income",
        "Gender",
        "Occupation",
        "Source",
        "FrequencyBand",
        "RecencyBand"
    ]

    results = {}
    for field in profiling_fields:
        if field in prof_df.columns:
            results[field] = dominance_table(prof_df, field)

    return prof_df, results


# ============================================================
# 7. INSIGHT GENERATOR → Extract meaningful signals only
# ============================================================
def generate_dominance_insights(results_dict):
    insights = []

    for field, table in results_dict.items():
        for (segment, category), row in table.iterrows():

            dom = row["Dominance"]

            # Keep only meaningful insights
            if dom not in ["HIGHLY dominant", "Strongly dominant", "Under-represented"]:
                continue

            seg_pct = row["Segment %"]
            pop_pct = row["Population %"]
            idx = row["Index"]

            insights.append(
                f"[{field}] {segment}: {dom} for '{category}' "
                f"(Segment {seg_pct:.1%} vs Pop {pop_pct:.1%}, Index={idx:.2f})"
            )

    return insights
