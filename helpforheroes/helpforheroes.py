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



def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ============================================================
    # INTRODUCTION
    # ============================================================
    st.markdown(
        """
<h2>Customer Profiling Approach</h2>

<h4>1️⃣ Proportional Representation</h4>
<p>
We compare each segment’s share of key characteristics (age, income, gender, occupation, channel, frequency, recency, destination, product)
against the full customer base to highlight where groups <b>over-index</b>.
</p>

<h4>2️⃣ Statistical Reliability + Effect Sizing</h4>
<p>
A <b>proportions Z-test</b> confirms differences are statistically meaningful,
and percentage-point deltas clearly show the magnitude of each effect.
</p>

<br><br>
<h2>Final Segment Interpretations</h2>
""",
        unsafe_allow_html=True
    )

    # ============================================================
    # CLICKABLE DROPDOWN SECTIONS
    # ============================================================

    with st.expander("1️⃣ Saver Casuals — Interpretation"):
        st.markdown(
            """
Saver Casuals are value-focused travellers with clear, predictable patterns.

<br><br>
✅ Very strong representation among occasional travellers (<b>+44 ppts</b>)  
✅ Significant 4–5 year recency group (<b>+21 ppts</b>)  
✅ Higher preference for Australia (<b>+14</b>) and Greece (<b>+6</b>)  
✅ Slightly older, modest-income profile  

<br>
<b>Overall:</b> A segment defined by <b>infrequent but consistent value-driven travel habits</b>.
""",
            unsafe_allow_html=True
        )

    with st.expander("2️⃣ Premium One-Timers — Interpretation"):
        st.markdown(
            """
Premium One-Timers make high-value purchases with clear digital and destination preferences.

<br><br>
✅ Strong female representation (<b>+44 ppts</b>)  
✅ Higher proportion of lower-income households (<b>+12 ppts</b>)  
✅ High website and phone usage (<b>+32 ppts website</b>)  
✅ Preference for France (<b>+32</b>) and Germany (<b>+12</b>)  

<br>
<b>Overall:</b> A <b>premium but one-off</b> segment with strong digital-first behaviours.
""",
            unsafe_allow_html=True
        )

    with st.expander("3️⃣ Economy Explorers — Interpretation"):
        st.markdown(
            """
Economy Explorers are active, internationally minded travellers with strong engagement.

<br><br>
✅ Male-skewed segment (female <b>−21</b>)  
✅ Higher middle-income representation (<b>+18 ppts</b>)  
✅ Strong travel frequency — regular (<b>+23</b>), frequent (<b>+7</b>)  
✅ Over-index on US trips (<b>+19</b>) and global destinations  

<br>
<b>Overall:</b> <b>Curious, frequent travellers</b> who favour agent-supported international trips.
""",
            unsafe_allow_html=True
        )

    with st.expander("4️⃣ Premium Casuals — Interpretation"):
        st.markdown(
            """
Premium Casuals prefer personalised, service-led booking experiences.

<br><br>
✅ Strong use of telephone enquiries (<b>+17 ppts</b>)  
✅ Clear preference for Germany (<b>+17</b>)  
✅ More financially stable occupational profile  

<br>
<b>Overall:</b> A <b>premium-leaning, service-first</b> segment with modest booking frequency.
""",
            unsafe_allow_html=True
        )

    with st.expander("5️⃣ Economy One-Timers — Interpretation"):
        st.markdown(
            """
Economy One-Timers are digital-first travellers with simple one-off behaviour.

<br><br>
✅ Strong female skew (<b>+45 ppts</b>)  
✅ Higher lower-income representation (<b>+13</b>)  
✅ Very high website use (<b>+34</b>)  
✅ Focus on France (<b>+34</b>) and Germany (<b>+12</b>)  

<br>
<b>Overall:</b> A <b>digital, destination-focused</b> segment with clear one-time engagement.
""",
            unsafe_allow_html=True
        )

    with st.expander("6️⃣ Saver One-Timers — Interpretation"):
        st.markdown(
            """
Saver One-Timers are a clearly defined digital-heavy segment.

<br><br>
✅ Very strong female presence (<b>+58 ppts</b>)  
✅ Higher low-income share (<b>+17</b>)  
✅ Very high website usage (<b>+38</b>)  
✅ Destination focus on France (<b>+39</b>) and Germany (<b>+20</b>)  

<br>
<b>Overall:</b> A <b>low-frequency, digital-first</b> group with consistent behavioural patterns.
""",
            unsafe_allow_html=True
        )

    with st.expander("7️⃣ Economy Casuals — Interpretation"):
        st.markdown(
            """
Economy Casuals prefer simple phone-led journeys and travel occasionally.

<br><br>
✅ Strong phone usage (<b>+16</b>)  
✅ High share of occasional travellers (<b>+43</b>)  
✅ Recency peak at 3–4 years (<b>+12</b>)  
✅ Preference for Germany (<b>+16</b>)  

<br>
<b>Overall:</b> A <b>low-effort, phone-first</b> segment with predictable rhythms.
""",
            unsafe_allow_html=True
        )

    with st.expander("8️⃣ Premium Explorers — Interpretation"):
        st.markdown(
            """
Premium Explorers are the highest-value, most engaged customers.

<br><br>
✅ Strong male skew (female <b>−24</b>)  
✅ Slightly higher income (<b>+3</b>)  
✅ Exceptional frequency — regular (<b>+20</b>), frequent (<b>+19</b>)  
✅ International destination focus: US (<b>+24</b>), Italy, Kuwait, Africa  

<br>
<b>Overall:</b> A <b>top-tier, internationally active</b> loyalty priority.
""",
            unsafe_allow_html=True
        )

    with st.expander("9️⃣ Saver Explorers — Interpretation"):
        st.markdown(
            """
Saver Explorers are budget-savvy but highly active and adventurous.

<br><br>
✅ Very strong regular travel behaviour (<b>+29</b>)  
✅ Male-skewed (female <b>−23</b>)  
✅ Higher middle-income share (<b>+19</b>)  
✅ Interest in Portugal, Namibia, and Africa  

<br>
<b>Overall:</b> A <b>budget-conscious, high-engagement explorer</b> group.
""",
            unsafe_allow_html=True
        )




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
