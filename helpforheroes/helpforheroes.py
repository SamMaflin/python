"""
Help for Heroes — Customer Insights Dashboard
Clean, modular, production-ready rewrite
"""

import streamlit as st

# ---- Internal Modules ----
from data_loader import load_helpforheroes_data
from metrics_engine import calculate_customer_value_metrics
from segment_barchart import segment_barchart_plot


# ============================================================
# GLOBAL SETTINGS & COLOURS
# ============================================================
SPEND_COLOR      = "#0095FF"
ENGAGEMENT_COLOR = "#00FF80"
STRATEGIC_COLOR  = "#FF476C"


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Help for Heroes — Customer Insights",
    layout="wide"
)


# ============================================================
# GLOBAL CSS
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        h1 { font-size: 60px !important; font-weight: 700 !important; }
        h2 { font-size: 50px !important; font-weight: 700 !important; margin-top: 120px !important; }
        h3.small-h3 { font-size: 34px !important; font-weight: 700 !important; margin: 30px 0 15px 0 !important; }
        p, li { font-size: 22px !important; line-height: 1.45 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HEADER + LOGO
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
# INTRODUCTION SECTIONS
# ============================================================
def render_introduction():
    st.markdown("<h2>Introduction</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <p>
        <span style="color:orange; font-weight:bold;">All customers create value</span> — just not in the same way.  
        Some generate high spend, others show strong behavioural loyalty, and some align perfectly with strategic goals.<br><br>
        Understanding <b>how</b> each customer contributes enables smarter targeting, deeper personalisation,  
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
        <p>Based on average booking value and maximum booking value (combined into a 0–100 index).</p>

        <h4><span style="color:{ENGAGEMENT_COLOR}; font-weight:bold;">● Engagement Score</span> — Behaviour & Loyalty</h4>
        <p>Based on booking frequency, destination diversity, and booking recency.</p>

        <h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — Alignment With Business Priorities</h4>
        <p>Based on long-haul behaviour, package adoption, and channel fit.</p>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# METRIC CONSTRUCTION SECTION
# ============================================================
def render_metric_construction():
    st.markdown("<h2>Metric Construction</h2>", unsafe_allow_html=True)

    # Spend
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score (0–100)</span></h3>
        <ul>
            <li>Average Booking Amount reflects typical spend per trip.</li>
            <li>Maximum Booking Amount captures premium trip activity.</li>
            <li>Scores are normalised and combined 70% Avg / 30% Max.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Engagement
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{ENGAGEMENT_COLOR}; font-weight:bold;'>Engagement Score (0–100)</span></h3>
        <ul>
            <li>Combines Frequency, Recency and Diversity.</li>
            <li>Diversity = unique destinations + exploration ratio.</li>
            <li>Weighting reflects realistic travel behaviour patterns.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Strategic
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score (0–100)</span></h3>
        <ul>
            <li>Binary signals mapped to 0/100 for comparability.</li>
            <li>Weights: Long-Haul (50%), Package (30%), Channel Fit (20%).</li>
        </ul>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SEGMENTATION MATRIX
# ============================================================
def render_segmentation_matrix():
    st.markdown("<h2>Customer Segmentation Matrix</h2>", unsafe_allow_html=True)
    st.image("helpforheroes/matrix_plot.png", use_column_width=True)


# ============================================================
# SEGMENTATION CHART
# ============================================================
def render_segment_barchart(df, bookings_df):
    st.markdown("<h2>Customer Base vs Revenue Contribution by Segment</h2>", unsafe_allow_html=True)
    segment_barchart_plot(df, bookings_df)


# ============================================================
# SEGMENT INSIGHTS
# ============================================================
def render_segment_insights():
    st.markdown("<h2>Early Segment Insights</h2>", unsafe_allow_html=True)

    st.markdown(
        """
        <ul>
            <li><b>Premium Loyalists</b> & <b>Premium Regulars</b> generate the majority of revenue — but for different reasons (frequency vs ticket size).</li>
            <li><b>Loyal Value</b> & <b>Developing Value</b> are the strongest growth pools.</li>
            <li><b>One-Off Premiums</b> represent the biggest reactivation opportunity.</li>
            <li><b>At-Risk Decliners</b> are the largest retention concern.</li>
            <li><b>Engaged Low-Spend</b> are a monetisation opportunity.</li>
            <li><b>Dormant Base</b> should not receive heavy marketing investment.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN APP SEQUENCE
# ============================================================
def main():

    inject_css()
    render_logo()
    render_title()

    # INTRO
    render_introduction()
    render_value_dimensions()
    render_metric_construction()

    # SEGMENTATION IMAGE
    render_segmentation_matrix()

    # LOAD DATA + METRICS
    data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")
    df = calculate_customer_value_metrics(data["People_Data"], data["Bookings_Data"])

    # SEGMENT BAR CHART
    render_segment_barchart(df, data["Bookings_Data"])

    # INSIGHTS
    render_segment_insights()


# ============================================================
# RUN APP
# ============================================================
if __name__ == "__main__":
    main()
