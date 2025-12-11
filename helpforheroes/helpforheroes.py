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
For each characteristic (age, income, gender, occupation, channel, frequency, recency, destination, continent, product),
we compared each segment’s share to the overall customer base. This highlights where segments
<b>over-index</b> on key traits.
</p>

<h4>2️⃣ Statistical Reliability + Effect Sizing</h4>
<p>
We apply a <b>proportions Z-test</b> to confirm differences are statistically meaningful,
and use percentage-point differences to quantify the size of each effect clearly.
</p>

<br><br>
<h2>Final Segment Interpretations</h2>
<br>

<!-- ========================================================= -->
<!-- 1️⃣ Saver Casuals -->
<!-- ========================================================= -->
<h3>1️⃣ Saver Casuals — Interpretation</h3>
<p>
Saver Casuals are value-focused travellers with clear, predictable patterns.  
<br><br>
✅ Very strong representation among occasional travellers (<b>+44 ppts</b>)<br>
✅ A notable group with 4–5 year recency (<b>+21 ppts</b>)<br>
✅ Higher preference for Australia (<b>+14</b>) and Greece (<b>+6</b>)<br>
✅ Slightly older, modest-income profile<br>
<br>
Overall, a segment defined by <b>infrequent but consistent value-driven travel habits</b>.
</p>
<br>

<!-- ========================================================= -->
<!-- 2️⃣ Premium One-Timers -->
<!-- ========================================================= -->
<h3>2️⃣ Premium One-Timers — Interpretation</h3>
<p>
Premium One-Timers make high-value purchases and show distinctive digital and demographic patterns.  
<br><br>
✅ Strong female representation (<b>+44 ppts</b>)<br>
✅ Higher presence of lower-income households (<b>+12 ppts</b>)<br>
✅ High usage of digital & phone channels (<b>+32 ppts website</b>)<br>
✅ Strong interest in France (<b>+32</b>) and Germany (<b>+12</b>)<br>
<br>
Overall, a <b>premium but one-off segment</b> with clear digital-first behaviours.
</p>
<br>

<!-- ========================================================= -->
<!-- 3️⃣ Economy Explorers -->
<!-- ========================================================= -->
<h3>3️⃣ Economy Explorers — Interpretation</h3>
<p>
Economy Explorers are active, internationally minded travellers with strong engagement levels.  
<br><br>
✅ Strong male skew (female <b>−21 ppts</b>)<br>
✅ Higher middle-income share (<b>+18 ppts</b>)<br>
✅ Very strong travel frequency — regular (<b>+23</b>), frequent (<b>+7</b>)<br>
✅ Over-index on US travel (<b>+19</b>) and selective global destinations<br>
<br>
Overall, <b>curious, frequent travellers</b> who prefer agent-supported international trips.
</p>
<br>

<!-- ========================================================= -->
<!-- 4️⃣ Premium Casuals -->
<!-- ========================================================= -->
<h3>4️⃣ Premium Casuals — Interpretation</h3>
<p>
Premium Casuals show premium preferences with modest, steady engagement.  
<br><br>
✅ High use of telephone enquiries (<b>+17 ppts</b>)<br>
✅ Distinct preference for Germany (<b>+17</b>)<br>
✅ More financially stable occupational profile<br>
<br>
Overall, a <b>service-first premium segment</b> that values personalised support.
</p>
<br>

<!-- ========================================================= -->
<!-- 5️⃣ Economy One-Timers -->
<!-- ========================================================= -->
<h3>5️⃣ Economy One-Timers — Interpretation</h3>
<p>
Economy One-Timers are digital-first travellers who engage once with clear destination preferences.  
<br><br>
✅ Strong female skew (<b>+45 ppts</b>)<br>
✅ Higher representation of lower-income households (<b>+13</b>)<br>
✅ Very high website usage (<b>+34 ppts</b>)<br>
✅ Strong focus on France (<b>+34</b>) and Germany (<b>+12</b>)<br>
<br>
Overall, a <b>digital, destination-focused segment</b> with simple one-off travel behaviour.
</p>
<br>

<!-- ========================================================= -->
<!-- 6️⃣ Saver One-Timers -->
<!-- ========================================================= -->
<h3>6️⃣ Saver One-Timers — Interpretation</h3>
<p>
Saver One-Timers represent a clear, consistent profile of low-spend digital users.  
<br><br>
✅ Very strong female representation (<b>+58 ppts</b>)<br>
✅ Higher share of low-income households (<b>+17</b>)<br>
✅ Very high website usage (<b>+38 ppts</b>)<br>
✅ Clear focus on France (<b>+39</b>) and Germany (<b>+20</b>)<br>
<br>
Overall, a <b>digital-heavy, low-frequency segment</b> with well-defined patterns.
</p>
<br>

<!-- ========================================================= -->
<!-- 7️⃣ Economy Casuals -->
<!-- ========================================================= -->
<h3>7️⃣ Economy Casuals — Interpretation</h3>
<p>
Economy Casuals prefer simple, phone-led booking experiences and travel occasionally.  
<br><br>
✅ Strong phone usage (<b>+16 ppts</b>)<br>
✅ High concentration of occasional travellers (<b>+43 ppts</b>)<br>
✅ Recency peak at 3–4 years (<b>+12</b>)<br>
✅ Preference for Germany (<b>+16</b>)<br>
<br>
Overall, a <b>low-effort, phone-first</b> segment with predictable behaviours.
</p>
<br>

<!-- ========================================================= -->
<!-- 8️⃣ Premium Explorers -->
<!-- ========================================================= -->
<h3>8️⃣ Premium Explorers — Interpretation</h3>
<p>
Premium Explorers are the highest-value and most engaged customers across the base.  
<br><br>
✅ Strong male skew (female <b>−24</b>)<br>
✅ Slightly higher income (<b>+3 ppts</b>)<br>
✅ Exceptional travel frequency — regular (<b>+20</b>), frequent (<b>+19</b>)<br>
✅ Very strong international focus — US (<b>+24</b>), Italy, Kuwait, Africa<br>
<br>
Overall, a <b>top-tier, internationally active</b> segment ideal for loyalty and premium strategy.
</p>
<br>

<!-- ========================================================= -->
<!-- 9️⃣ Saver Explorers -->
<!-- ========================================================= -->
<h3>9️⃣ Saver Explorers — Interpretation</h3>
<p>
Saver Explorers are budget-conscious but highly active and adventurous travellers.  
<br><br>
✅ Very strong regular travel behaviour (<b>+29 ppts</b>)<br>
✅ Lower likelihood of occasional travel (<b>−18</b>)<br>
✅ Male-skewed (female <b>−23</b>)<br>
✅ Higher middle-income representation (<b>+19</b>)<br>
✅ Interest in Portugal, Namibia, and Africa<br>
<br>
Overall, a <b>budget-savvy, high-engagement explorer segment</b> with broad destination variety.
</p>
<br>
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
