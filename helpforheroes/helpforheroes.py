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
            font-size: 50px !important; 
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

    st.markdown("<h2>Metric Construction</h2>", unsafe_allow_html=True)

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
    st.markdown("<h2>Customer Base vs Revenue Contribution by Segment</h2>", unsafe_allow_html=True)
    segment_barchart_plot(df, bookings_df)


# ============================================================
# INSIGHT SECTION
# ============================================================
def render_segment_insights():
    st.markdown("<h3>Early Segment Insights</h3>", unsafe_allow_html=True)

    st.markdown(
        """
        <ul>
            <li><b>Premium Loyalists</b> & <b>Premium Regulars</b> generate the most revenue.</li>
            <li><b>Loyal Value</b> & <b>Developing Value</b> segments represent your best growth potential.</li>
            <li><b>One-Off Premiums</b> are the biggest reactivation upside.</li>
            <li><b>At-Risk Decliners</b> signal churn risk and need intervention.</li>
            <li><b>Engaged Low-Spend</b> can be monetised with tailored offers.</li>
            <li><b>Dormant Base</b> should receive minimal investment.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )


import streamlit as st

def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ============================================================
    # SECTION HEADER
    # ============================================================
    st.markdown("<h2>📊 Customer Segment Profiles</h2>", unsafe_allow_html=True)

    st.markdown(
        """
### 🔍 How These Profiles Were Built — Clear, Non-Technical Overview

To understand **who makes up each customer segment**, we compared the composition of each segment  
against the **overall customer base** using three simple statistical ideas:

#### **1️⃣ Proportional Representation**
For each characteristic (age, income, gender, occupation, channel, frequency, recency), we measured:
- What % of the *whole base* falls into a category  
- What % of the *segment* falls into that category  

This tells us whether a segment has **more or fewer** of a group than expected.

#### **2️⃣ Z-Test for Reliability**
We then ran a **proportions Z-test** to check whether those differences are statistically meaningful  
(rather than random noise).

If the difference is unlikely to occur by chance (p < 0.05), we treat it as a **reliable insight**.

#### **3️⃣ Index for Effect Size**
We translate the difference into an intuitive Index:

- `1.0` → exactly as expected  
- `2.0` → twice as common as expected  
- `0.5` → half as common as expected  

This helps quantify *how strong* the difference is, not just whether it exists.

Together, these steps allow us to produce **clear, human-readable segment profiles** that reflect  
real patterns in behaviour and demographics, not guesswork.
"""
    )

    st.markdown("---")

    # ============================================================
    # SEGMENT PROFILES — PROFESSIONAL DESCRIPTIONS
    # ============================================================

    # 1️⃣ Economy Casuals
    with st.expander("1️⃣ Economy Casuals"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**A low-engagement group that books infrequently, "
            "typically by phone, and shows limited long-term value.**"
        )

        st.markdown("### **Who They Tend to Be**")
        st.markdown(
            """
- Slight male lean  
- Fewer retired and unemployed customers  
- Income slightly below average  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Almost all are **occasional travellers**  
- Strong **telephone-first** behaviour  
- Almost no **website usage**  
- Many last booked **3–4 years ago**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Occasional, low-effort customers who prefer phone interactions and seldom return.**"
        )

    # 2️⃣ Economy Explorers
    with st.expander("2️⃣ Economy Explorers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Active value travellers who engage regularly and explore more destinations while "
            "remaining budget-conscious.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Predominantly **male**  
- Fewer students and retirees  
- Strong representation of **professionals**  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Heavy **travel agent** usage  
- More frequent and more **exploratory**  
- Lower dormancy than other economy segments  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Engaged, value-driven travellers who explore widely and rely on agent channels.**"
        )

    # 3️⃣ Economy One-Timers
    with st.expander("3️⃣ Economy One-Timers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Customers who made a single low-cost booking and did not return.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Strong **female** skew  
- Over-represented among **retirees** and **low-income** groups  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Minimal use of **agents** or **Expedia**  
- Bookings are typically **very old**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Low-income, one-off travellers with limited likelihood of re-engagement.**"
        )

    # 4️⃣ Premium Casuals
    with st.expander("4️⃣ Premium Casuals"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Higher-spending but infrequent travellers who prefer premium-style experiences "
            "despite limited engagement.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Slightly higher incomes  
- Fewer unemployed customers  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Very strong **telephone-first** behaviour  
- Almost zero **digital usage**  
- Mostly **occasional** travellers  
- Many last booked **2–3 years ago**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Premium-leaning but irregular travellers who favour personal channels and lapse easily.**"
        )

    # 5️⃣ Premium Explorers
    with st.expander("5️⃣ Premium Explorers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**High-value, active travellers who explore widely and prefer structured, agent-led booking channels.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Heavily **male**  
- Strong **middle-income** presence  
- Many **managers** and **professionals**  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Heavy reliance on **travel agents** and **Expedia**  
- Broad destination exploration  
- Lower dormancy than other premium segments  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **High-value explorers who consistently engage via trusted, professional channels.**"
        )

    # 6️⃣ Premium One-Timers
    with st.expander("6️⃣ Premium One-Timers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Travellers who made a one-off premium purchase but did not continue travelling with you.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Strong **female** representation  
- Mix of **lower-income** households  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Low use of **agents** or **Expedia**  
- Mostly older bookings leading to fast **dormancy**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **One-time premium purchasers with weak retention behaviour.**"
        )

    # 7️⃣ Saver Casuals
    with st.expander("7️⃣ Saver Casuals"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Very infrequent, price-sensitive customers who show long-term disengagement.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Under-represented among high-income households  
- More common among **middle-aged and older** customers  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Nearly all are **occasional** travellers  
- Almost no digital behaviour  
- High share dormant **4–5 years**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Price-driven customers with minimal engagement and very low repeat potential.**"
        )

    # 8️⃣ Saver Explorers
    with st.expander("8️⃣ Saver Explorers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Highly active budget travellers who rely on agents and maintain strong engagement.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Very **male-dominated**  
- Over-represented among **managers** and **retail workers**  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Heavy **travel agent** reliance  
- More **frequent** and more **exploratory** than other saver groups  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **Engaged budget travellers who explore frequently through traditional channels.**"
        )

    # 9️⃣ Saver One-Timers
    with st.expander("9️⃣ Saver One-Timers"):
        st.markdown("### **Profile Summary**")
        st.markdown(
            "**Low-income, predominantly female customers whose engagement ended after a single booking.**"
        )

        st.markdown("### **Who They Are**")
        st.markdown(
            """
- Strong **female** skew  
- Over-represented among **manual workers** and **retirees**  
            """
        )

        st.markdown("### **How They Book & Behave**")
        st.markdown(
            """
- Very little recent activity  
- Typically dormant for **multiple years**  
            """
        )

        st.markdown("### **Professional Interpretation**")
        st.markdown(
            "➡️ **One-off low-income travellers with minimal re-engagement probability.**"
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
