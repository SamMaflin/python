"""
Help for Heroes — Customer Insights Dashboard
Clean, modular, production-ready rewrite
"""

import streamlit as st

# ---- Internal Modules ----
from data_loader import load_helpforheroes_data
from metrics_engine import calculate_customer_value_metrics
from segment_barchart import segment_barchart_plot
from customer_profiles import customer_profiles  # returns (prof_df, results, insights)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Help for Heroes — Customer Insights",
    layout="centered"
)

# ============================================================
# GLOBAL COLOURS
# ============================================================
SPEND_COLOR      = "#0095FF"
ENGAGEMENT_COLOR = "#00FF80"
STRATEGIC_COLOR  = "#FF476C"


# ============================================================
# CSS
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
        <span style="color:orange; font-weight:bold;">All customers create value</span> — just not equally.<br>
        Some generate high spend, others show strong loyalty, and some align closely with strategic goals.
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
        <p>Based on average booking value and maximum booking value, normalised to 0–100.</p>

        <h4><span style="color:{ENGAGEMENT_COLOR}; font-weight:bold;">● Engagement Score</span> — Behaviour & Loyalty</h4>
        <p>Combines booking frequency, recency, and diversity of destinations into a 0–100 index.</p>

        <h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — Strategic Alignment</h4>
        <p>Captures long-haul, package holiday and channel-fit behaviour where relevant.</p>
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
            <li>Scores are ranked and blended 70% / 30% to reduce outlier skew.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Engagement
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{ENGAGEMENT_COLOR}; font-weight:bold;'>Engagement Score (0–100)</span></h3>
        <ul>
            <li>Includes Frequency, Recency and Destination Diversity.</li>
            <li>Diversity = unique destinations + exploration ratio (unique / total).</li>
            <li>Weights: Frequency 50%, Recency 30%, Diversity 20%.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Strategic
    st.markdown(
        f"""
        <h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score (0–100)</span></h3>
        <ul>
            <li>Long-haul destinations, package holidays and priority channels.</li>
            <li>Mapped to a simple 0/100 style contribution per signal.</li>
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


# ============================================================
# CUSTOMER PROFILES + SIGNIFICANT INSIGHTS
# ============================================================
def render_customer_profiles(df, bookings_df, people_df):

    # Run profiling engine (includes statistical tests)
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ------------------------------------------------------------
    # Intro: how the profiling was built
    # ------------------------------------------------------------
    st.markdown(
        """
<h2>Customer Profiling & Segment Insights</h2>

<h4>1️⃣ Proportional Representation</h4>
<p>
For each characteristic (age, income, gender, occupation, booking channel, frequency, recency,
destination, continent, product), we calculated:<br>
• The % of the <b>overall customer base</b> in each category<br>
• The % of each <b>segment</b> in the same category<br>
This shows whether a segment has <b>more</b> or <b>fewer</b> of a given group than expected.
</p>

<h4>2️⃣ Statistical Testing (Z-Test)</h4>
<p>
We then used a <b>two-proportion Z-test</b> to check whether the difference between the segment
and the total base is statistically reliable (p &lt; 0.05), rather than random noise.
</p>

<h4>3️⃣ Index for Effect Size</h4>
<p>
For every statistically significant result, we calculate a simple Index:<br>
• Index = 1.0 → exactly as expected<br>
• Index = 2.0 → twice as common as expected<br>
• Index = 0.5 → half as common as expected<br>
This helps quantify how strong the difference is, not just whether it exists.
</p>

<p>
Below, each segment has its own panel, listing only the <b>statistically significant</b> and
<strong>meaningful</strong> over- or under-representation patterns.
</p>
""",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ------------------------------------------------------------
    # Group INSIGHTS by segment name
    # ------------------------------------------------------------
    segment_insights = {}

    for text in insights:
        # Example insight:
        # "[IncomeBand] Economy Casuals: HIGHLY dominant for 'Low Income' — 2.26× (Segment 30.0% vs Pop 13.3%) (p=0.0000)"
        try:
            after_bracket = text.split("] ", 1)[1]    # "Economy Casuals: ..."
            segment_name = after_bracket.split(":", 1)[0].strip()
        except Exception:
            continue

        segment_insights.setdefault(segment_name, []).append(text)

    # Use the order of segments as they appear in df (and only those with insights)
    ordered_segments = []
    for seg in df["Segment"].dropna().unique():
        if seg in segment_insights and seg not in ordered_segments:
            ordered_segments.append(seg)

    # ------------------------------------------------------------
    # Render expander per segment with its significant insights
    # ------------------------------------------------------------
    for i, segment in enumerate(ordered_segments, start=1):
        seg_insights = segment_insights[segment]

        with st.expander(f"{i}. {segment}", expanded=False):
            st.markdown(f"<h3>{segment}</h3>", unsafe_allow_html=True)
            st.markdown("<h4>Key Profiling Signals</h4>", unsafe_allow_html=True)

            # Render insights as a clean bullet list
            items_html = "".join([f"<li>{s}</li>" for s in seg_insights])
            st.markdown(f"<ul>{items_html}</ul>", unsafe_allow_html=True)

            st.markdown(
                "<p><i>Only statistically significant and materially over/under-represented patterns are shown.</i></p>",
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
