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
    Convert raw (field, category) pairs into intuitive,
    natural-language traits for persona-style summaries.
    """

    # AGE
    if field == "AgeBracket":
        mapping = {
            "18–29": "a younger traveller base",
            "30–39": "customers in their thirties",
            "40–59": "mature travellers",
            "60+": "older customers"
        }
        return f"Tend to skew toward {mapping.get(category, category)}" if positive else \
               f"Less likely to include {mapping.get(category, category)}"

    # INCOME
    if field == "IncomeBand":
        mapping = {
            "Low Income": "lower-income households",
            "Low–Middle Income": "budget-conscious earners",
            "Middle Income": "middle-income families",
            "High Income": "higher-income customers",
            "Executive Income": "affluent, premium customers"
        }
        return f"More likely to be {mapping.get(category, category)}" if positive else \
               f"Rarely {mapping.get(category, category)}"

    # FREQUENCY
    if field == "FrequencyBand":
        mapping = {
            "One-Time": "one-off bookers",
            "Occasional": "occasional travellers",
            "Regular": "steady, repeat travellers",
            "Frequent": "highly engaged, frequent travellers"
        }
        return f"Often {mapping.get(category, category)}" if positive else \
               f"Seldom {mapping.get(category, category)}"

    # RECENCY
    if field == "RecencyBand":
        mapping = {
            "0–1 yr (Very Recent)": "recently active",
            "1–2 yr (Recent)": "fairly active",
            "2–3 yr (Lapsed)": "lapsing",
            "3–4 yr (Dormant)": "dormant",
            "4–5 yr (Dormant+)": "long-dormant",
            "5+ yr (Very Old)": "inactive for many years"
        }
        return f"More likely to be {mapping.get(category, category)}" if positive else \
               f"Less likely to be {mapping.get(category, category)}"

    # DESTINATION
    if field == "Destination":
        return f"Show a preference for travelling to <b>{category}</b>" if positive else \
               f"Less commonly choose <b>{category}</b>"

    # CONTINENT
    if field == "Continent":
        return f"Drawn toward <b>{category}</b> trips" if positive else \
               f"Less drawn to <b>{category}</b>"

    # PRODUCT
    if field == "Product":
        return f"More inclined toward <b>{category}</b> products" if positive else \
               f"Less likely to choose <b>{category}</b> products"

    # GENDER / OCCUPATION / SOURCE (default fallback)
    if positive:
        return f"Tend to include more <b>{category}</b>"
    else:
        return f"Less likely to include <b>{category}</b>"




    # ------------------------------------------------------
    # 2. Intuitive persona-style summaries per segment
    # ------------------------------------------------------
    st.markdown("<h2>🧭 Segment Summary Profiles</h2>", unsafe_allow_html=True)

    if not by_segment:
        st.info("No statistically significant differences available.")
        return

    for segment, items in by_segment.items():
        st.markdown(f"<h3 style='margin-top:35px;'>{segment}</h3>", unsafe_allow_html=True)

        overs = []
        unders = []

        for field, category, dom, full in items:
            # Build intuitive phrases
            if dom == "Over":
                phrase = intuitive_phrase(field, category, positive=True)
                overs.append(f"✔️ {phrase}")
            else:
                phrase = intuitive_phrase(field, category, positive=False)
                unders.append(f"✖️ {phrase}")

        if overs:
            st.markdown("<h4 style='color:green;'>What defines this group ✔️</h4>", unsafe_allow_html=True)
            for line in overs:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        if unders:
            st.markdown("<h4 style='color:red;'>Less typical traits ✖️</h4>", unsafe_allow_html=True)
            for line in unders:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)




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
