import pandas as pd
import numpy as np


def prepare_people_data(people_df, bookings_df=None, reference_date=None):
    people = people_df.copy()

    # Parse DOB
    people["DOB"] = pd.to_datetime(
        people["DOB"], format="%d/%m/%Y", errors="coerce"
    )

    # Choose a sensible reference date
    if reference_date is None:
        if bookings_df is not None and "Booking Date" in bookings_df.columns:
            ref = pd.to_datetime(bookings_df["Booking Date"], errors="coerce").max()
        else:
            ref = pd.Timestamp.today().normalize()
    else:
        ref = pd.to_datetime(reference_date)

    # Calculate age at reference date
    people["Age"] = people["DOB"].apply(
        lambda d: int((ref - d).days / 365.25) if pd.notnull(d) else np.nan
    )

    # Age brackets (with a proper <18 bucket)
    bins   = [0, 18, 30, 40, 50, 60, 70, 200]
    labels = ["<18", "18–29", "30–39", "40–49", "50–59", "60–69", "70+"]

    people["AgeBracket"] = pd.cut(
        people["Age"], bins=bins, labels=labels, right=False, include_lowest=True
    )

    return people


# ============================================================
# 2. POPULATION BASELINE
# ============================================================
def population_baseline(prof_df, field):
    counts = prof_df[field].value_counts(dropna=False)
    pct = counts / counts.sum()
    return pct


# ============================================================
# 3. SEGMENT DISTRIBUTION
# ============================================================
def segment_distribution(prof_df, field, segment_col="Segment"):
    counts = prof_df.groupby([segment_col, field])["Person URN"].count()
    pct = counts / counts.groupby(level=0).sum()
    return pct


# ============================================================
# 4. DOMINANCE TABLE
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
# 5. FULL SEGMENTATION BREAKDOWN
# ============================================================
def full_segmentation_breakdown(seg_df, people_df):
    """
    seg_df    = metrics engine output (must contain Person URN + Segment)
    people_df = raw demographic dataset
    """

    people_clean = prepare_people_data(people_df)

    # Merge segmentation + demographics
    prof_df = seg_df.merge(people_clean, on="Person URN", how="left")

    fields = ["AgeBracket", "Income", "Gender", "Occupation", "Source"]

    results = {}
    for field in fields:
        if field in prof_df.columns:
            results[field] = dominance_table(prof_df, field)

    return prof_df, results


# ============================================================
# 6. INSIGHT GENERATOR
# ============================================================
def generate_dominance_insights(results_dict):
    insights = []

    for field, table in results_dict.items():
        for (segment, category), row in table.iterrows():

            seg_pct, pop_pct, idx, dom = (
                row["Segment %"], row["Population %"],
                row["Index"], row["Dominance"]
            )

            if dom in ["HIGHLY dominant", "Strongly dominant", "Under-represented"]:
                insights.append(
                    f"[{field}] {segment}: {dom} for '{category}' "
                    f"(Segment {seg_pct:.1%} vs Pop {pop_pct:.1%}, Index={idx:.2f})"
                )

    return insights


# ============================================================
# 7. PUBLIC ENTRYPOINT (no Streamlit)
# ============================================================
def customer_profiles(seg_df, bookings_df, people_df):
    """
    Returns pure dataframes and insight text.
    """
    prof_df, results = full_segmentation_breakdown(seg_df, people_df)
    insights = generate_dominance_insights(results)

    return prof_df, results, insights
