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
    simple recommendations for how to maximise value from each segment.
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

    # -----------------------------------------
    # PERSONA SUMMARIES — EFFECT-SCALED LANGUAGE
    # -----------------------------------------

    personas = {
        "Economy One-Timers": {
            "summary": """
                ✔️ Much more likely to come from lower-income backgrounds, make simple one-off bookings, 
                and favour familiar European destinations like France and Germany.<br>
                ✔️ More likely to be older and long inactive.<br><br>
                ✖️ Much less likely to travel long-haul or return regularly.<br>
                ✖️ Less likely to use digital channels or travel agents.
            """,
            "strategy": """
                • Keep offers simple and cost-conscious.<br>
                • Promote easy European getaways.<br>
                • Use phone-friendly or low-friction booking prompts.
            """
        },

        "Economy Casuals": {
            "summary": """
                ✔️ More likely to be light, occasional travellers who prefer phoning to enquire and stick to familiar European destinations.<br>
                ✔️ More likely to be dormant for long stretches.<br><br>
                ✖️ Far less likely to book online or behave like frequent travellers.
            """,
            "strategy": """
                • Use reactivation campaigns with clear, simple pricing.<br>
                • Keep communication personal and phone-led.<br>
                • Encourage small steps toward repeat-booking habits.
            """
        },

        "Economy Explorers": {
            "summary": """
                ✔️ Much more likely to be higher-income, active travellers exploring destinations across Europe, the Americas and Asia.<br>
                ✔️ More likely to book frequently and very recently.<br><br>
                ✖️ Much less likely to be low-income or Europe-only travellers.
            """,
            "strategy": """
                • Promote diverse itineraries and multi-destination offers.<br>
                • Use loyalty-style incentives to maintain high engagement.<br>
                • Showcase long-haul and premium upgrade opportunities.
            """
        },

        "Premium Explorers": {
            "summary": """
                ✔️ Far more likely to be affluent, globally oriented travellers choosing long-haul destinations like Africa, the Americas and Asia.<br>
                ✔️ Book frequently and prefer specialist accommodation offerings.<br><br>
                ✖️ Much less likely to be Europe-focused or digital-channel users.
            """,
            "strategy": """
                • Offer personalised, concierge-style travel support.<br>
                • Highlight long-haul inspirational content.<br>
                • Use outbound phone/email rather than digital-led acquisition.
            """
        },

        "Premium One-Timers": {
            "summary": """
                ✔️ More likely to be lower-income, older customers booking one-off European trips.<br>
                ✔️ Prefer simple channels like telephone or website.<br><br>
                ✖️ Less likely to be professionals or long-haul travellers.
            """,
            "strategy": """
                • Promote straightforward European packages.<br>
                • Use simple value framing and reassurance messages.<br>
                • Encourage trial of a second “follow-up” trip.
            """
        },

        "Saver Casuals": {
            "summary": """
                ✔️ More likely to be occasional travellers drawn to long-haul destinations like Australia and Greece.<br>
                ✔️ More likely to be long-term dormant.<br><br>
                ✖️ Far less likely to use online channels or travel recently.
            """,
            "strategy": """
                • Use offline, phone-friendly engagement methods.<br>
                • Offer inspirational long-haul content with easy payment options.<br>
                • Use dormant-winback campaigns.
            """
        },

        "Saver Explorers": {
            "summary": """
                ✔️ Much more likely to be higher-income repeat travellers with strong interest in Africa and Portugal.<br>
                ✔️ Prefer long-haul or niche destinations over mainstream Europe.<br><br>
                ✖️ Much less likely to be low-income or infrequent travellers.
            """,
            "strategy": """
                • Promote niche and specialist itineraries.<br>
                • Encourage loyalty with multi-trip or exploration-themed bundles.<br>
                • Provide tailored content about unusual global destinations.
            """
        }
    }

    # -----------------------------------------
    # RENDER PERSONAS (clean, no code-box artefacts)
    # -----------------------------------------
    for segment, info in personas.items():

        st.markdown(f"<h3 style='margin-top:35px;'>{segment}</h3>", unsafe_allow_html=True)

        # Persona Summary (no div, no grey box, no indentation → no code block)
        st.markdown(
            f"""
            <p style='font-size:20px; line-height:1.6;'>
            {info['summary']}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<b>Recommended Strategy:</b>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <ul style='font-size:20px; line-height:1.6; margin-top:8px;'>
                {''.join([f"<li>{line.strip()}</li>" for line in info['strategy'].split("<br>") if line.strip()])}
            </ul>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr style='margin-top:30px; margin-bottom:30px;'>", unsafe_allow_html=True)


 



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
