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
    st.markdown("<h2>Customer Segmentation Matrix...</h2>", unsafe_allow_html=True)
    st.image("helpforheroes/matrix_plot.png", use_column_width=True)


# ============================================================
# SEGMENT BAR CHART
# ============================================================
def render_segment_barchart(df, bookings_df):
    st.markdown("<h2>📊 Customer Base vs Revenue Contribution by Segment...</h2>", unsafe_allow_html=True)
    segment_barchart_plot(df, bookings_df)

 


import streamlit as st

def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ============================================================
    # SECTION HEADER
    # ============================================================
    st.markdown("<h2>📊 Customer Segment Profiles...</h2>", unsafe_allow_html=True)

    import streamlit as st

def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ============================================================
    # INTRODUCTION
    # ============================================================
    st.markdown(
        """
<h2>Customer Profiling</h2>

<h4>1️⃣ Proportional Representation</h4>
<p>
For each characteristic (age, income, gender, occupation, channel, frequency, recency),
we measured:<br></br>
<br>• The % of the <b>overall population</b> in each category  
<br>• The % of the <b>segment</b> in each category  
</p>
<p>This shows whether a segment has <b>more</b> or <b>fewer</b> of a group than expected.<br></br>
</p>

<h4>2️⃣ Z-Test for Statistical Reliability</h4>
<p>
We apply a <b>proportions Z-test</b> to confirm whether those differences are
statistically meaningful and not random noise.<br></br>
</p>

<h4>3️⃣ Index for Effect Size</h4>
<p>
We also compute an intuitive Index:
<br><b>1.0</b> = exactly as expected  
<br><b>2.0</b> = twice as common as expected  
<br><b>0.5</b> = half as common as expected  
</p> 
<br></br>

<hr>
        """,
        unsafe_allow_html=True
    )

    # ============================================================
    # SEGMENT PROFILES (H2 → H3 → H4 hierarchy)
    # ============================================================

    # -------------------------
    # 1️⃣ Economy Casuals
    # -------------------------
    with st.expander("1️⃣ Economy Casuals"):
        st.markdown(
            """
<h2>Economy Casuals</h2>

<h3>Profile Summary</h3>
<p>
A low-engagement group that books infrequently—usually by phone—and shows limited long-term value.
</p>

<h4>Who They Tend to Be</h4>
<p>
• Slight male lean<br>
• Fewer retired and unemployed customers<br>
• Slightly below-average income levels  
</p>

<h4>How They Book & Behave</h4>
<p>
• Almost all are <b>occasional</b> travellers<br>
• Very strong <b>telephone-first</b> habits<br>
• Almost no website usage<br>
• Many last booked <b>3–4 years ago</b>  
</p>

<h4>Professional Interpretation</h4>
<p><b>Low-effort, low-frequency customers who prefer phone interactions and rarely return.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 2️⃣ Economy Explorers
    # -------------------------
    with st.expander("2️⃣ Economy Explorers"):
        st.markdown(
            """
<h2>Economy Explorers</h2>

<h3>Profile Summary</h3>
<p>
Active value travellers who explore more destinations and maintain higher engagement
while staying budget-conscious.
</p>

<h4>Who They Are</h4>
<p>
• Predominantly male<br>
• Fewer students and retirees<br>
• Strong representation of professionals  
</p>

<h4>How They Book & Behave</h4>
<p>
• Heavy reliance on <b>travel agents</b><br>
• More <b>frequent</b> and <b>exploratory</b> behaviour<br>
• Lower levels of long-term dormancy  
</p>

<h4>Professional Interpretation</h4>
<p><b>Engaged value-seekers who rely on agents and exhibit broad destination interest.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 3️⃣ Economy One-Timers
    # -------------------------
    with st.expander("3️⃣ Economy One-Timers"):
        st.markdown(
            """
<h2>Economy One-Timers</h2>

<h3>Profile Summary</h3>
<p>
Customers who made one low-value booking and did not return.
</p>

<h4>Who They Are</h4>
<p>
• Strong female skew<br>
• High presence of retirees and low-income households  
</p>

<h4>How They Book & Behave</h4>
<p>
• Minimal use of agents or Expedia<br>
• Bookings tend to be <b>very old</b>  
</p>

<h4>Professional Interpretation</h4>
<p><b>Low-income, one-off travellers with very limited re-engagement potential.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 4️⃣ Premium Casuals
    # -------------------------
    with st.expander("4️⃣ Premium Casuals"):
        st.markdown(
            """
<h2>Premium Casuals</h2>

<h3>Profile Summary</h3>
<p>
Higher-spending but infrequent travellers who prefer personalised booking channels.
</p>

<h4>Who They Are</h4>
<p>
• Slightly higher incomes<br>
• Lower unemployment representation  
</p>

<h4>How They Book & Behave</h4>
<p>
• Very strong <b>telephone-first</b> behaviour<br>
• Almost no digital usage<br>
• Mostly occasional travellers<br>
• Many last booked <b>2–3 years ago</b>  
</p>

<h4>Professional Interpretation</h4>
<p><b>Premium-leaning, low-frequency travellers who favour personal service but lapse easily.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 5️⃣ Premium Explorers
    # -------------------------
    with st.expander("5️⃣ Premium Explorers"):
        st.markdown(
            """
<h2>Premium Explorers</h2>

<h3>Profile Summary</h3>
<p>
High-value, highly active travellers who use structured channels and explore extensively.
</p>

<h4>Who They Are</h4>
<p>
• Heavily male<br>
• Strong middle-income representation<br>
• Many managers and professionals  
</p>

<h4>How They Book & Behave</h4>
<p>
• Heavy use of <b>travel agents</b> and <b>Expedia</b><br>
• Broad destination exploration<br>
• Low dormancy  
</p>

<h4>Professional Interpretation</h4>
<p><b>Reliable, high-value explorers who stay active and prefer professional booking channels.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 6️⃣ Premium One-Timers
    # -------------------------
    with st.expander("6️⃣ Premium One-Timers"):
        st.markdown(
            """
<h2>Premium One-Timers</h2>

<h3>Profile Summary</h3>
<p>
Customers who made one premium purchase but did not continue travelling with you.
</p>

<h4>Who They Are</h4>
<p>
• Strong female representation<br>
• Mix of lower-income households  
</p>

<h4>How They Book & Behave</h4>
<p>
• Low use of agents or Expedia<br>
• Often lapsed shortly after their first premium purchase  
</p>

<h4>Professional Interpretation</h4>
<p><b>One-time premium buyers with weak follow-up engagement.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 7️⃣ Saver Casuals
    # -------------------------
    with st.expander("7️⃣ Saver Casuals"):
        st.markdown(
            """
<h2>Saver Casuals</h2>

<h3>Profile Summary</h3>
<p>
Very infrequent, price-sensitive customers who show long-term inactivity.
</p>

<h4>Who They Are</h4>
<p>
• Under-represented among high-income groups<br>
• More commonly middle-aged or older  
</p>

<h4>How They Book & Behave</h4>
<p>
• Almost exclusively occasional travellers<br>
• Almost no digital behaviour<br>
• High share dormant <b>4–5 years</b>  
</p>

<h4>Professional Interpretation</h4>
<p><b>Low-engagement, price-sensitive travellers with minimal repeat likelihood.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 8️⃣ Saver Explorers
    # -------------------------
    with st.expander("8️⃣ Saver Explorers"):
        st.markdown(
            """
<h2>Saver Explorers</h2>

<h3>Profile Summary</h3>
<p>
Highly active budget travellers who rely on travel agents and remain engaged.
</p>

<h4>Who They Are</h4>
<p>
• Strong male dominance<br>
• Over-represented among managers and retail workers  
</p>

<h4>How They Book & Behave</h4>
<p>
• Heavy travel agent usage<br>
• More frequent and exploratory than other saver segments  
</p>

<h4>Professional Interpretation</h4>
<p><b>Engaged budget travellers who show strong repeat and exploratory behaviour.</b></p>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 9️⃣ Saver One-Timers
    # -------------------------
    with st.expander("9️⃣ Saver One-Timers"):
        st.markdown(
            """
<h2>Saver One-Timers</h2>

<h3>Profile Summary</h3>
<p>
Low-income, predominantly female customers whose engagement ended after a single booking.
</p>

<h4>Who They Are</h4>
<p>
• Strong female skew<br>
• Over-represented among manual workers and retirees  
</p>

<h4>How They Book & Behave</h4>
<p>
• Very little recent activity<br>
• Often dormant for multiple years  
</p>

<h4>Professional Interpretation</h4>
<p><b>One-off, low-income travellers with minimal likelihood of returning.</b></p>
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
