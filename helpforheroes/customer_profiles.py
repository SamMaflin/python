import pandas as pd
import numpy as np


# ============================================================
# 1. CLEAN PEOPLE DATA → Age + AgeBracket
# ============================================================
def prepare_people_data(people_df):
    people = people_df.copy()

    # Convert to datetime
    people["DOB"] = pd.to_datetime(
        people["DOB"], format="%d/%m/%Y", errors="coerce"
    )

    # Compute age relative to TODAY
    today = pd.Timestamp("today")
    people["Age"] = people["DOB"].apply(
        lambda d: int((today - d).days / 365.25) if pd.notnull(d) else np.nan
    )

    # Create age brackets
    bins = [0, 29, 39, 49, 59, 69, 200]
    labels = ["18–29", "30–39", "40–49", "50–59", "60–69", "70+"]
    people["AgeBracket"] = pd.cut(
        people["Age"], bins=bins, labels=labels, include_lowest=True
    )

    return people


# ============================================================
# 2. BEHAVIOURAL FIELDS → FrequencyBand + RecencyBand
# ============================================================
def derive_booking_behaviour(bookings_df):
    bookings = bookings_df.copy()

    bookings["Booking Date"] = pd.to_datetime(
        bookings["Booking Date"], format="%d/%m/%Y", errors="coerce"
    )
    today = pd.Timestamp("today")

    # ---- Frequency ----
    freq = bookings.groupby("Person URN")["Booking URN"].count().rename("Frequency")

    def freq_band(n):
        if n == 1: return "One-Time"
        if n <= 3: return "Occasional"
        if n <= 6: return "Regular"
        return "Frequent"

    freq_band_series = freq.apply(freq_band).rename("FrequencyBand")

    # ---- Recency ----
    last_booking = bookings.groupby("Person URN")["Booking Date"].max().rename("LastBooking")
    recency_days = (today - last_booking).dt.days.rename("RecencyDays")

    def rec_band(d):
        if d <= 90: return "Very Recent"
        if d <= 180: return "Recent"
        if d <= 365: return "Lapsed"
        return "Dormant"

    recency_band = recency_days.apply(rec_band).rename("RecencyBand")

    return pd.concat([freq, freq_band_series, last_booking, recency_days, recency_band], axis=1)


# ============================================================
# 3. POPULATION BASELINE
# ============================================================
def population_baseline(prof_df, field):
    counts = prof_df[field].value_counts(dropna=False)
    pct = counts / counts.sum()
    return pct


# ============================================================
# 4. SEGMENT DISTRIBUTION
# ============================================================
def segment_distribution(prof_df, field, segment_col="Segment"):
    counts = prof_df.groupby([segment_col, field])["Person URN"].count()
    pct = counts / counts.groupby(level=0).sum()
    return pct


# ============================================================
# 5. DOMINANCE TABLE
# ============================================================
def dominance_table(prof_df, field):
    pop_pct = population_baseline(prof_df, field)
    seg_pct = segment_distribution(prof_df, field)

    aligned_pop = pop_pct.reindex(seg_pct.index.get_level_values(field)).values

    df = pd.DataFrame({
        "Segment %": seg_pct,
        "Population %": aligned_pop
    })

    df["Index"] = df["Segment %"] / df["Population %"]
    df["Difference (pp)"] = df["Segment %"] - df["Population %"]

    def label(idx):
        if pd.isna(idx): return "No data"
        if idx >= 2.0: return "HIGHLY dominant"
        if idx >= 1.5: return "Strongly dominant"
        if idx >= 1.2: return "Moderately over-represented"
        if idx > 0.8: return "Normal presence"
        return "Under-represented"

    df["Dominance"] = df["Index"].apply(label)
    return df


# ============================================================
# 6. FULL SEGMENTATION + PROFILING DATASET
# ============================================================
def full_segmentation_breakdown(seg_df, bookings_df, people_df):
    """
    seg_df: segmentation output (Person URN + Segment)
    bookings_df: raw bookings
    people_df: raw demographic data
    """

    # Prepare demographic + behavioural features
    people_clean = prepare_people_data(people_df)
    behaviour = derive_booking_behaviour(bookings_df)

    # Merge all together
    prof_df = (
        seg_df.merge(people_clean, on="Person URN", how="left")
              .merge(behaviour, on="Person URN", how="left")
    )

    # Fields we want to profile
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
# 7. INSIGHT GENERATOR
# ============================================================
def generate_dominance_insights(results_dict):
    insights = []

    for field, table in results_dict.items():
        for (segment, category), row in table.iterrows():
            dom = row["Dominance"]

            # Only meaningful signals
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


# ============================================================
# 8. PUBLIC ENTRYPOINT (no Streamlit)
# ============================================================
def customer_profiles(seg_df, bookings_df, people_df):
    """
    Returns:
        prof_df — merged dataset (segmentation + demographics + behaviour)
        results — dict of dominance tables
        insights — list of meaningful interpreted findings
    """
    prof_df, results = full_segmentation_breakdown(
        seg_df=seg_df,
        bookings_df=bookings_df,
        people_df=people_df
    )

    insights = generate_dominance_insights(results)

    return prof_df, results, insights
