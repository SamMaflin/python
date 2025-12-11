"""
Help for Heroes — Customer Insights Dashboard
Clean, modular, production-ready rewrite
"""

import streamlit as st

# ---- Internal Modules ----
from data_loader import load_helpforheroes_data
from metrics_engine import calculate_customer_value_metrics
from segment_barchart import segment_barchart_plot
from customer_profiles import customer_profiles

# ============================================================
# PAGE CONFIG — NOW MATCHES YOUR ORIGINAL STYLE
# ============================================================
st.set_page_config(
    page_title="Help for Heroes — Customer Insights",
    layout="centered"   # ⬅️ RESTORED ORIGINAL LOOK
)


# ============================================================
# GLOBAL COLOURS
# ============================================================
SPEND_COLOR      = "#0095FF"
ENGAGEMENT_COLOR = "#00FF80"
STRATEGIC_COLOR  = "#FF476C"


# ============================================================
# CSS — EXACT SAME STYLING YOU USED BEFORE
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>

        .stMarkdown h1 { 
            font-size: 60px !important; 
            font-weight: 700 !important; 
            margin: 20px 0 20px 0; 
        }

        .stMarkdown h2 { 
            font-size: 45px !important; 
            font-weight: 700 !important; 
            margin: 150px 0 20px 0; 
        }

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

        p, li { 
            font-size: 22px !important; 
            line-height: 1.45 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HEADER AREA
# ============================================================
def render_logo():
    try:
        st.image("helpforheroes/hfh_logo.png", width=200)
    except:
        pass


def render_title():
    st.markdown(
        "<h1>Help for Heroes Interview Task — Customer Holiday Bookings Insights</h1>",
        unsafe_allow_html=True
    )


# ============================================================
# INTRO SECTIONS
# ============================================================
def render_introduction():
    st.markdown("<h2>Introduction</h2>", unsafe_allow_html=True)

    st.markdown(
        """
        <p>
        <span style="color:orange; font-weight:bold;">All customers create value</span> — just not equally.  
        Some generate high spend, others show great loyalty, and some align closely with strategic goals.
        Understanding <b>how</b> customers differ enables better targeting, personalisation,  
        and more efficient value growth.
        </p>
        """,
        unsafe_allow_html=True
    )


def render_value_dimensions():
    st.markdown("<h2>How Do We Measure Customer Value?</h2>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <h4><span style="color:{SPEND_COLOR}; font-weight:bold;">● Spend Score</span> — Financial Contribution</h4>
        <p>Based on average booking value and maximum booking value.</p>

        <h4><span style="color:{ENGAGEMENT_COLOR}; font-weight:bold;">● Engagement Score</span> — Behaviour & Loyalty</h4>
        <p>Based on booking frequency, destination diversity, and recency.</p>

        <h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — (Optional) Strategic Alignment</h4>
        <p>Based on long-haul trips, package behaviour, and channel fit.</p>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# METRIC CONSTRUCTION
# ============================================================
def render_metric_construction():

    st.markdown("<h2>Metric Construction...</h2>", unsafe_allow_html=True)

    # Spend
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score (0–100)</span></h3>
        <ul>
            <li>Average Booking Amount reflects typical trip value.</li>
            <li>Maximum Booking Amount captures premium behaviour.</li>
            <li>Scores normalised and blended at 70% / 30%.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Engagement
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{ENGAGEMENT_COLOR}; font-weight:bold;'>Engagement Score (0–100)</span></h3>
        <ul>
            <li>Includes Frequency, Recency and Diversity.</li>
            <li>Diversity = unique destinations + exploration ratio.</li>
            <li>Weights (50/30/20) reflect realistic travel patterns.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Strategic
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score (0–100)</span></h3>
        <ul>
            <li>Binary signals: long-haul, package, channel fit.</li>
            <li>Weighted (50/30/20) based on commercial value.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SEGMENT MATRIX
# ============================================================
def render_segmentation_matrix():
    st.markdown("<h2>Customer Segmentation Matrix</h2>", unsafe_allow_html=True)
    st.image("helpforheroes/matrix_plot.png", use_column_width=True)


# ============================================================
# SEGMENT BAR CHART
# ============================================================
def render_segment_barchart(df, bookings_df):
    st.markdown("<h2>📊 Customer Base vs Revenue Contribution by Segment</h2>", unsafe_allow_html=True)
    segment_barchart_plot(df, bookings_df)

  

def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ============================================================
    # SECTION HEADER
    # ============================================================
    st.markdown("<h2>📊 Customer Segment Profiles...</h2>", unsafe_allow_html=True)






def intuitive_phrase(field, category, positive=True):
    """
    Convert raw statistical dominance attributes into natural,
    intuitive, persona-style descriptions.
    """

    # -------------------------
    # AGE
    # -------------------------
    if field == "AgeBracket":
        mapping = {
            "18–29": "younger adults",
            "30–39": "people in their thirties",
            "40–59": "mature travellers in mid-life",
            "60+": "older, more seasoned travellers"
        }
        phrase = mapping.get(category, category)
        return (
            f"Tend to skew toward {phrase}"
            if positive else
            f"Less likely to include {phrase}"
        )

    # -------------------------
    # INCOME
    # -------------------------
    if field == "IncomeBand":
        mapping = {
            "Low Income": "lower-income households",
            "Low–Middle Income": "budget-conscious earners",
            "Middle Income": "middle-income families",
            "High Income": "higher-income customers",
            "Executive Income": "affluent, premium customers"
        }
        phrase = mapping.get(category, category)
        return (
            f"Often come from {phrase}"
            if positive else
            f"Rarely come from {phrase}"
        )

    # -------------------------
    # GENDER
    # -------------------------
    if field == "Gender":
        return (
            f"More commonly {category.lower()}"
            if positive else
            f"Less commonly {category.lower()}"
        )

    # -------------------------
    # OCCUPATION
    # -------------------------
    if field == "Occupation":
        return (
            f"More typically working as {category.lower()}"
            if positive else
            f"Less typically working as {category.lower()}"
        )

    # -------------------------
    # BOOKING FREQUENCY
    # -------------------------
    if field == "FrequencyBand":
        mapping = {
            "One-Time": "one-off holiday makers",
            "Occasional": "light or occasional travellers",
            "Regular": "consistent repeat travellers",
            "Frequent": "highly engaged, frequent travellers"
        }
        phrase = mapping.get(category, category)
        return (
            f"Often behave like {phrase}"
            if positive else
            f"Seldom behave like {phrase}"
        )

    # -------------------------
    # RECENCY
    # -------------------------
    if field == "RecencyBand":
        mapping = {
            "0–1 yr (Very Recent)": "very recent bookers",
            "1–2 yr (Recent)": "fairly recent bookers",
            "2–3 yr (Lapsed)": "customers beginning to lapse",
            "3–4 yr (Dormant)": "dormant customers",
            "4–5 yr (Dormant+)": "long-term dormant customers",
            "5+ yr (Very Old)": "very old or inactive customers"
        }
        phrase = mapping.get(category, category)
        return (
            f"More likely to be {phrase}"
            if positive else
            f"Less likely to be {phrase}"
        )

    # -------------------------
    # DESTINATION
    # -------------------------
    if field == "Destination":
        return (
            f"Show a stronger preference for travelling to <b>{category}</b>"
            if positive else
            f"Less commonly travel to <b>{category}</b>"
        )

    # -------------------------
    # CONTINENT
    # -------------------------
    if field == "Continent":
        return (
            f"More drawn to <b>{category}</b> holidays"
            if positive else
            f"Less drawn to <b>{category}</b> holidays"
        )

    # -------------------------
    # PRODUCT TYPE
    # -------------------------
    if field == "Product":
        return (
            f"Often choose <b>{category}</b>-type trips"
            if positive else
            f"Less likely to book <b>{category}</b>-type trips"
        )

    # -------------------------
    # FALLBACK
    # -------------------------
    return (
        f"Tend to include more <b>{category}</b>"
        if positive else
        f"Less likely to include <b>{category}</b>"
    )



def render_customer_profiles(df, bookings_df, people_df):
    """
    Render intuitive persona-style segment summaries AND
    detailed statistically significant dominance insights.
    """

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # -----------------------------------------
    # HEADER
    # -----------------------------------------
    st.markdown("<h2>🔍 Customer Segment Profiles</h2>", unsafe_allow_html=True)
    st.markdown("""
        <p>This section summarises who each customer segment really is —
        based on <b>statistically significant</b> differences from the overall population.</p>
        <p>✔️ = traits they are more likely to have<br>
        ✖️ = traits they are less likely to have</p>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # 1. Parse insights → structured per segment & per field
    # ------------------------------------------------------
    parsed = []
    for txt in insights:
        # Example format:
        # "[AgeBracket] High Value: HIGHLY dominant for '60+' — ..."
        try:
            field = txt.split("]")[0].replace("[", "")
            remainder = txt.split("] ")[1]
            segment = remainder.split(":")[0]
            category = txt.split("'")[1]
            dom = "Under" if "Under-represented" in txt else "Over"
            parsed.append((segment, field, category, dom, txt))
        except:
            continue

    # Group insights by segment
    by_segment = {}
    for segment, field, category, dom, full in parsed:
        by_segment.setdefault(segment, []).append((field, category, dom, full))

    # ------------------------------------------------------
    # 2. Persona-style summaries per segment
    # ------------------------------------------------------
    st.markdown("<h2>🧭 Segment Persona Summaries</h2>", unsafe_allow_html=True)

    if not by_segment:
        st.info("No statistically significant differences found.")
        return

    for segment, items in by_segment.items():

        st.markdown(f"<h3 style='margin-top:35px;'>{segment}</h3>", unsafe_allow_html=True)

        overs = []
        unders = []

        for field, category, dom, full in items:
            positive = (dom == "Over")
            phrase = intuitive_phrase(field, category, positive=positive)

            if positive:
                overs.append(f"✔️ {phrase}")
            else:
                unders.append(f"✖️ {phrase}")

        # Present segment profile
        if overs:
            st.markdown("<h4 style='color:green;'>What typically defines them ✔️</h4>", unsafe_allow_html=True)
            for line in overs:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        if unders:
            st.markdown("<h4 style='color:red;'>Traits they are less associated with ✖️</h4>", unsafe_allow_html=True)
            for line in unders:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

    # ------------------------------------------------------
    # 3. Detailed breakdown by attribute
    # ------------------------------------------------------
    st.markdown("<h2 style='margin-top:60px;'>📊 Detailed Statistically Significant Insights</h2>",
                unsafe_allow_html=True)

    # Group insights by profiling dimension
    grouped = {}
    for text in insights:
        try:
            field = text.split("]")[0].replace("[", "")
            grouped.setdefault(field, []).append(text)
        except:
            continue

    # Display each dimension
    for field, entries in grouped.items():

        st.markdown(f"<h3 style='margin-top:40px;'>{field}</h3>", unsafe_allow_html=True)

        over = [i for i in entries if ("dominant" in i)]
        under = [i for i in entries if ("Under-represented" in i)]

        if not over and not under:
            st.info("No significant differences for this attribute.")
            continue

        if over:
            st.markdown("<h4 style='color:green;'>Over-represented</h4>", unsafe_allow_html=True)
            for line in over:
                st.markdown(f"• {line}")

        if under:
            st.markdown("<h4 style='color:red;'>Under-represented</h4>", unsafe_allow_html=True)
            for line in under:
                st.markdown(f"• {line}")

    # ------------------------------------------------------
    # 4. Raw dominance tables (optional)
    # ------------------------------------------------------
    with st.expander("View full dominance tables (all attributes)"):
        for field, table in results.items():
            st.markdown(f"### {field}")
            st.dataframe(table)





# ============================================================
# MAIN APP
# ============================================================
def main():

    inject_css()
    render_logo()
    render_title()

    render_introduction()
    render_value_dimensions()
    render_metric_construction()
    render_segmentation_matrix()

    # ---- Load Data + Build Metrics ----
    data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")
    df   = calculate_customer_value_metrics(data["People_Data"], data["Bookings_Data"])

    render_segment_barchart(df, data["Bookings_Data"])
    render_customer_profiles(df, data["Bookings_Data"], data["People_Data"])


# ============================================================
# RUN APP
# ============================================================
if __name__ == "__main__":
    main()
