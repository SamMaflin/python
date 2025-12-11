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
    """
    Render statistically significant dominance insights AND
    intuitive segment summaries using ✔️ and ✖️ indicators.
    """

    # Run profiling engine
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    st.markdown("<h2>🔍 Customer Segment Profiles — Statistically Significant Differences</h2>",
                unsafe_allow_html=True)

    st.markdown("""
        <p>Below are intuitive summaries describing <b>who each segment is</b>,
        based on <b>only statistically significant (p < 0.05)</b> over/under-representations.</p>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # 1. Parse insights → structured per segment & per field
    # ------------------------------------------------------
    # Example insight format:
    # "[AgeBracket] High Value: HIGHLY dominant for '60+' — 2.5× ..."
    parsed = []
    for txt in insights:
        try:
            field = txt.split("]")[0].replace("[", "")
            remainder = txt.split("] ")[1]
            segment = remainder.split(":")[0]
            dom = ("Under-represented" if "Under-represented" in txt else "Over")
            category = txt.split("'")[1]
            parsed.append((segment, field, category, dom, txt))
        except:
            continue

    # Group insights by segment
    by_segment = {}
    for segment, field, category, dom, full in parsed:
        by_segment.setdefault(segment, []).append((field, category, dom, full))

    # ------------------------------------------------------
    # 2. Write natural-language summaries per segment
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
            if dom == "Over":
                overs.append(f"✔️ More likely to be: <b>{category}</b> <span style='color:green;'>([{field}])</span>")
            else:
                unders.append(f"✖️ Less likely to be: <b>{category}</b> <span style='color:red;'>([{field}])</span>")

        if overs:
            st.markdown("<h4 style='color:green;'>Who they ARE ✔️</h4>", unsafe_allow_html=True)
            for line in overs:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        if unders:
            st.markdown("<h4 style='color:red;'>Who they ARE NOT ✖️</h4>", unsafe_allow_html=True)
            for line in unders:
                st.markdown(f"- {line}", unsafe_allow_html=True)

        # Divider
        st.markdown("<hr>", unsafe_allow_html=True)

    # ------------------------------------------------------
    # 3. Existing detailed insights grouped by field
    # ------------------------------------------------------
    st.markdown("<h2 style='margin-top:60px;'>📊 Detailed Statistically Significant Outputs</h2>",
                unsafe_allow_html=True)

    grouped = {}
    for text in insights:
        try:
            field = text.split("]")[0].replace("[", "")
            grouped.setdefault(field, []).append(text)
        except:
            continue

    for field, entries in grouped.items():

        st.markdown(f"<h3 style='margin-top:40px;'>{field}</h3>", unsafe_allow_html=True)

        over = [i for i in entries if ("dominant" in i)]
        under = [i for i in entries if ("Under-represented" in i)]

        if not over and not under:
            st.info("No statistically significant differences for this attribute.")
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
    # 4. Raw tables (optional)
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
