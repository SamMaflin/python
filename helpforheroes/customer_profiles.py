import pandas as pd
import numpy as np
from math import sqrt
from scipy.stats import norm

# ================================================================
#  UTILITY: TWO-PROPORTION Z-TEST + EFFECT SIZE (COHEN'S h)
# ================================================================
def two_proportion_test(success_seg, total_seg, success_pop, total_pop):
    """Run a two-proportion z-test and effect size h."""
    p1 = success_seg / total_seg
    p2 = success_pop / total_pop

    # pooled proportion
    p_pool = (success_seg + success_pop) / (total_seg + total_pop)

    # standard error
    se = sqrt(p_pool * (1 - p_pool) * (1/total_seg + 1/total_pop))
    if se == 0:
        return 0, 1, 0  # no statistical variation

    z = (p1 - p2) / se
    p = 2 * (1 - norm.cdf(abs(z)))   # two-tailed

    # cohen's h
    effect_h = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))

    return z, p, effect_h


# ================================================================
# 1. PEOPLE DATA CLEANING → AGE BRACKETS + INCOME BANDS
# ================================================================
def prepare_people_data(people_df):
    people = people_df.copy()

    # DOB
    people["DOB"] = pd.to_datetime(
        people["DOB"], format="%d/%m/%Y", errors="coerce"
    )

    today = pd.Timestamp("today")
    people["Age"] = people["DOB"].apply(
        lambda d: int((today - d).days / 365.25) if pd.notnull(d) else np.nan
    )

    # age brackets
    bins = [0, 29, 39, 59, 200]
    labels = ["18–29", "30–39", "40–59", "60+"]
    people["AgeBracket"] = pd.cut(people["Age"], bins=bins, labels=labels, include_lowest=True)

    # income mapping
    INCOME_GROUP_MAP = {
        "< £10k": "Low Income",
        "£10 - 20k": "Low–Middle Income",
        "£20 - 30k": "Low–Middle Income",
        "£30 - 40k": "Middle Income",
        "£40 - 50k": "Middle Income",
        "£50 - 70k": "Middle Income",
        "£70 - 80k": "High Income",
        "£80 - 90k": "High Income",
        "£90 - 100k": "High Income",
        "£100k+": "Executive Income",
        "Unclassified": "Unclassified"
    }

    people["Income"] = people["Income"].astype(str).str.strip().str.replace("  ", "")
    people["IncomeBand"] = people["Income"].map(INCOME_GROUP_MAP)

    return people


# ================================================================
# 2. BEHAVIOUR DERIVATION → FREQUENCY + RECENCY
# ================================================================
def derive_booking_behaviour(bookings_df):
    bookings = bookings_df.copy()

    bookings["Booking Date"] = pd.to_datetime(
        bookings["Booking Date"], format="%d/%m/%Y", errors="coerce"
    )

    reference_date = bookings["Booking Date"].max()

    # frequency
    freq = bookings.groupby("Person URN")["Booking URN"].count().rename("Frequency")

    def freq_band(n):
        if n == 1: return "One-Time"
        if n <= 3: return "Occasional"
        if n <= 6: return "Regular"
        return "Frequent"

    freq_band_series = freq.apply(freq_band).rename("FrequencyBand")

    # recency
    last_booking = bookings.groupby("Person URN")["Booking Date"].max().rename("LastBooking")
    recency_days = (reference_date - last_booking).dt.days

    max_real = recency_days.dropna().max()
    recency_days = recency_days.fillna(max_real + 1).rename("RecencyDays")

    def rec_band(d):
        if d <= 365: return "0–1 yr (Very Recent)"
        if d <= 730: return "1–2 yr (Recent)"
        if d <= 1095: return "2–3 yr (Lapsed)"
        if d <= 1460: return "3–4 yr (Dormant)"
        if d <= 1825: return "4–5 yr (Dormant+)"
        return "5+ yr (Very Old)"

    recency_band = recency_days.apply(rec_band).rename("RecencyBand")

    return pd.concat(
        [freq, freq_band_series, last_booking, recency_days, recency_band],
        axis=1
    )


# ================================================================
# 3. POPULATION BASELINE
# ================================================================
def population_baseline(prof_df, field):
    counts = prof_df[field].value_counts(dropna=False)
    return counts / counts.sum(), counts.sum(), counts


# ================================================================
# 4. DOMINANCE TABLE (WITH Z TESTS)
# ================================================================
def dominance_table(prof_df, field):

    pop_pct, pop_total, pop_counts = population_baseline(prof_df, field)

    seg_counts = prof_df.groupby(["Segment", field])["Person URN"].count()
    seg_totals = prof_df.groupby("Segment")["Person URN"].count()

    rows = []

    for (segment, category), seg_count in seg_counts.items():

        seg_total = seg_totals[segment]
        pop_count = pop_counts.get(category, 0)

        seg_pct = seg_count / seg_total
        pop_prop = pop_pct.get(category, 0)

        # statistical test
        z, p, h = two_proportion_test(
            seg_count, seg_total, pop_count, pop_total
        )

        idx = seg_pct / pop_prop if pop_prop > 0 else np.nan

        # interpretation
        if pd.isna(idx):
            dom = "No data"
        elif idx >= 2.0:
            dom = "HIGHLY dominant"
        elif idx >= 1.5:
            dom = "Strongly dominant"
        elif idx >= 1.2:
            dom = "Moderately over-represented"
        elif idx > 0.8:
            dom = "Normal presence"
        else:
            dom = "Under-represented"

        rows.append([
            segment, category,
            seg_pct, pop_prop,
            idx, seg_pct - pop_prop,
            dom, p, h
        ])

    df = pd.DataFrame(rows, columns=[
        "Segment", "Category",
        "Segment %", "Population %",
        "Index", "Diff(pp)",
        "Dominance", "p_value", "EffectSize_h"
    ])

    return df.set_index(["Segment", "Category"])


# ================================================================
# 5. FULL PROFILING ENGINE (NOW WITH DESTINATION DATA)
# ================================================================
def full_segmentation_breakdown(seg_df, bookings_df, people_df):

    # standardise destination spelling
    bookings_df = bookings_df.copy()
    bookings_df["Destination"] = bookings_df["Destination"].replace({
        "USA": "United States"
    })

    people_clean = prepare_people_data(people_df)
    behaviour = derive_booking_behaviour(bookings_df)

    # merge everything
    prof_df = (
        seg_df
        .merge(people_clean, on="Person URN", how="left")
        .merge(behaviour, on="Person URN", how="left")
        .merge(bookings_df[["Person URN", "Destination", "Continent", "Product"]],
               on="Person URN", how="left")
    )

    # profiling dimensions
    fields = [
        "AgeBracket", "IncomeBand", "Gender", "Occupation",
        "Source", "FrequencyBand", "RecencyBand",
        "Destination", "Continent", "Product"   # ← NEW
    ]

    results = {field: dominance_table(prof_df, field) for field in fields}

    return prof_df, results


# ================================================================
# 6. INSIGHT GENERATOR
# ================================================================
def generate_dominance_insights(results_dict):

    insights = []

    for field, table in results_dict.items():
        for (segment, category), row in table.iterrows():

            if row["p_value"] >= 0.05:
                continue  # not statistically reliable

            dom = row["Dominance"]
            if dom not in ["HIGHLY dominant", "Strongly dominant", "Under-represented"]:
                continue

            seg_pct = row["Segment %"]
            pop_pct = row["Population %"]
            idx = row["Index"]

            multiplier = (
                f"{idx:.2f}×" if idx >= 1 else f"{(1/idx):.2f}× less likely"
            )

            insights.append(
                f"[{field}] {segment}: {dom} for '{category}' — "
                f"{multiplier} (Segment {seg_pct:.1%} vs Pop {pop_pct:.1%}) "
                f"(p={row['p_value']:.4f})"
            )

    return insights


# ================================================================
# 7. PUBLIC ENTRYPOINT
# ================================================================
def customer_profiles(seg_df, bookings_df, people_df):
    prof_df, results = full_segmentation_breakdown(seg_df, bookings_df, people_df)
    insights = generate_dominance_insights(results)
    return prof_df, results, insights
