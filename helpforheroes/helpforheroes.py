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
For each characteristic (age, income, gender, occupation, channel, frequency, recency , destination, continent, product),
we measured:<br></br>
<br>• The % of the <b>overall population</b> in each category  
<br>• The % of the <b>segment</b> in each category  
</p>
<p>This shows whether a segment has <b>more</b> or <b>fewer</b> of a group than expected.<br></br>
</p>

<h4>2️⃣ Z-Test for Statistical Reliability + Index for Effect Size</h4>
<p>
We apply a <b>proportions Z-test</b> to confirm whether those differences are
statistically meaningful and not random noise. Then compute an intuitive index to assess the effect size.<br></br>
</p> 
<br></br>

# ============================
# SEGMENT INTERPRETATIONS
# ============================

<h2>Final Segment Interpretations</h2>
<br>

<!-- ========================================================= -->
<!-- 1️⃣ Saver Casuals -->
<!-- ========================================================= -->
<h3>1️⃣ Saver Casuals — Final Interpretation</h3>
<ul>
    <li>Very low-engagement, price-sensitive travellers who book infrequently and show long-term dormancy.</li>
    <li>Overwhelmingly occasional travellers (+44.0 ppts vs base).</li>
    <li>Very low digital use, especially website (−9.4 ppts).</li>
    <li>Strongly over-represented in 4–5 year dormant recency (+21.1 ppts).</li>
    <li>Travel less to Europe and the Americas (e.g., United States −14 ppts), but more to Australia (+14.3 ppts) and Greece (+5.9 ppts).</li>
    <li>Slightly older and lower-income with fewer retired or unemployed customers.</li>
</ul>
<p><b>Overall:</b> Low-return, low-frequency customers who rarely re-engage.</p>
<br>

<!-- ========================================================= -->
<!-- 2️⃣ Premium One-Timers -->
<!-- ========================================================= -->
<h3>2️⃣ Premium One-Timers — Final Interpretation</h3>
<ul>
    <li>Predominantly female (+43.7 ppts) with notable lean toward lower-income brackets (+12 ppts).</li>
    <li>Extremely low retention, with a large share in the 5+ year very old category (+38.3 ppts).</li>
    <li>Prefer website (+32.1 ppts) and phone (+11.8 ppts) while avoiding travel agents (−22 ppts).</li>
    <li>Destinations skew toward France (+32.2 ppts) and Germany (+12 ppts), with low interest in US and Australasia.</li>
</ul>
<p><b>Overall:</b> High-spend, predominantly female one-off customers who do not return.</p>
<br>

<!-- ========================================================= -->
<!-- 3️⃣ Economy Explorers -->
<!-- ========================================================= -->
<h3>3️⃣ Economy Explorers — Final Interpretation</h3>
<ul>
    <li>Engaged, exploratory travellers more active than other economy groups.</li>
    <li>Strong male skew (female share −21.4 ppts).</li>
    <li>More middle-income (+18 ppts) and more professionally employed.</li>
    <li>Book more regularly (+23.4 ppts) and frequently (+6.8 ppts).</li>
    <li>Prefer United States travel (+19.1 ppts) and show interest in Italy, Kuwait, Portugal.</li>
    <li>Less dormant, with more recent travel (+2.7 ppts).</li>
</ul>
<p><b>Overall:</b> Value-driven explorers who travel often and favour agent-supported international trips.</p>
<br>

<!-- ========================================================= -->
<!-- 4️⃣ Premium Casuals -->
<!-- ========================================================= -->
<h3>4️⃣ Premium Casuals — Final Interpretation</h3>
<ul>
    <li>Higher-income but infrequent travellers who behave in a premium style.</li>
    <li>Strong preference for telephone enquiries (+17.2 ppts) and almost no website use (−8.6 ppts).</li>
    <li>Fewer recent bookings and fewer long-dormant travellers (balanced recency profile).</li>
    <li>Prefer Germany (+17.3 ppts) and strongly avoid France (−8.6 ppts).</li>
    <li>Fewer unemployed or retail workers — financially stable profile.</li>
</ul>
<p><b>Overall:</b> Premium-leaning but low-frequency customers who value personal service.</p>
<br>

<!-- ========================================================= -->
<!-- 5️⃣ Economy One-Timers -->
<!-- ========================================================= -->
<h3>5️⃣ Economy One-Timers — Final Interpretation</h3>
<ul>
    <li>Strongly female (+45.1 ppts) and heavily lower-income (+13.1 ppts).</li>
    <li>Overwhelmingly one-booking-only customers (+35.4 ppts).</li>
    <li>Very high website usage (+33.7 ppts) and very low agent usage (−26.1 ppts).</li>
    <li>Long-term disengagement with many 5+ year very old bookings (+36.4 ppts).</li>
    <li>Prefer France (+33.8 ppts) and Germany (+11.8 ppts); reduced US travel (−27.3 ppts).</li>
</ul>
<p><b>Overall:</b> Budget-limited, one-off customers with minimal long-term value.</p>
<br>

<!-- ========================================================= -->
<!-- 6️⃣ Saver One-Timers -->
<!-- ========================================================= -->
<h3>6️⃣ Saver One-Timers — Final Interpretation</h3>
<ul>
    <li>Almost entirely female (+57.8 ppts) and strongly low-income (+17.3 ppts).</li>
    <li>Extremely strong one-time behaviour (+40.9 ppts) and long-term dormancy (+31.4 ppts for 4–5 yrs).</li>
    <li>Prefer website (+38.4 ppts) and phone, with minimal agent usage (−30.9 ppts).</li>
    <li>Heavily concentrated in France (+38.5 ppts) and Germany (+19.5 ppts); very low US and Australasia travel.</li>
    <li>Over-representation in manual work and under-representation in professional roles.</li>
</ul>
<p><b>Overall:</b> Low-income, one-off travellers with very low re-engagement potential.</p>
<br>

<!-- ========================================================= -->
<!-- 7️⃣ Economy Casuals -->
<!-- ========================================================= -->
<h3>7️⃣ Economy Casuals — Final Interpretation</h3>
<ul>
    <li>Light, low-commitment travellers who favour simple booking channels.</li>
    <li>Strongly prefer telephone enquiries (+15.9 ppts) and rarely use the website (−9 ppts).</li>
    <li>Almost entirely occasional travellers (+42.9 ppts).</li>
    <li>Many haven’t travelled for 3–4 years (+11.7 ppts) and fewer in 4–5 years (−11.3 ppts).</li>
    <li>Prefer Germany (+16.1 ppts) and avoid France (−9 ppts) and the US (−15.4 ppts).</li>
    <li>Fewer unemployed or retired customers; lower middle-income share.</li>
</ul>
<p><b>Overall:</b> Low-effort, phone-first customers with low repeat behaviour.</p>
<br>

<!-- ========================================================= -->
<!-- 8️⃣ Premium Explorers -->
<!-- ========================================================= -->
<h3>8️⃣ Premium Explorers — Final Interpretation</h3>
<ul>
    <li>High-value, highly active travellers with strong engagement.</li>
    <li>Strongly male, with fewer females (−23.7 ppts).</li>
    <li>Higher-income (+2.7 ppts High Income; +0.5 ppts Executive Income).</li>
    <li>Book regularly (+19.7 ppts) and frequently (+18.5 ppts); fewer occasional travellers (−28.3 ppts).</li>
    <li>More recent travel (+1.8 ppts) and much lower dormancy (−15.9 ppts for 4–5 yrs).</li>
    <li>Significant US preference (+24.1 ppts), plus Kuwait, Italy, Africa.</li>
    <li>Strong avoidance of France (−9.3 ppts) and Europe overall (−23.5 ppts).</li>
</ul>
<p><b>Overall:</b> Engaged, high-value explorers with international, agent-led travel styles.</p>
<br>

<!-- ========================================================= -->
<!-- 9️⃣ Saver Explorers -->
<!-- ========================================================= -->
<h3>9️⃣ Saver Explorers — Final Interpretation</h3>
<ul>
    <li>Budget-conscious but very active travellers with strong repeat patterns.</li>
    <li>Favour regular travel (+28.5 ppts) and have reduced occasional travel (−18.3 ppts).</li>
    <li>More middle-income (+18.9 ppts) and significantly more male (−23.3 ppts females).</li>
    <li>Over-index on managers and retail workers; under-index on retired/manual workers.</li>
    <li>Prefer off-beat destinations like Portugal (+1.1 ppts), Namibia, and Africa (+0.7 ppts).</li>
    <li>Travel to Europe far less often (−19.1 ppts).</li>
    <li>Stronger agent usage and reduced phone enquiries (−13.6 ppts).</li>
</ul>
<p><b>Overall:</b> Active, curious budget travellers who explore widely and rely on agents.</p>
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
