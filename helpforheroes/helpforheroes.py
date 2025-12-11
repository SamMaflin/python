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






def summarise_traits(overs, unders):
    """
    Turn long lists of intuitive traits into a short persona-style
    summary with ✔️ and ✖️ emojis.
    """

    def cluster(traits, keywords):
        return [t for t in traits if any(k in t.lower() for k in keywords)]

    # --- Cluster themes for overs (positive traits)
    income_pos = cluster(overs, ["income"])
    age_pos = cluster(overs, ["young", "older", "mature"])
    behaviour_pos = cluster(overs, ["traveller", "booker", "engaged", "frequent", "recent"])
    destination_pos = cluster(overs, ["travel", "drawn", "preference", "holidays"])
    channel_pos = cluster(overs, ["website", "telephone", "agent"])
    occupation_pos = cluster(overs, ["working as"])

    # --- Cluster themes for unders (negative traits)
    income_neg = cluster(unders, ["income"])
    behaviour_neg = cluster(unders, ["seldom", "less likely", "inactive", "dormant"])
    destination_neg = cluster(unders, ["travel", "drawn", "holidays"])
    occupation_neg = cluster(unders, ["working as"])
    
    summary = []

    # ✔️ POSITIVE SUMMARY
    if income_pos or age_pos or behaviour_pos or destination_pos:
        pos_sentence = "✔️ "
        if income_pos:
            pos_sentence += "Often defined by their income profile; "
        if age_pos:
            pos_sentence += "skewing towards a specific age group; "
        if behaviour_pos:
            pos_sentence += "with recognisable booking behaviour; "
        if destination_pos:
            pos_sentence += "and clear destination preferences."
        summary.append(pos_sentence)

    # ✖️ NEGATIVE SUMMARY
    if income_neg or behaviour_neg or destination_neg:
        neg_sentence = "✖️ "
        if income_neg:
            neg_sentence += "Less represented in certain income groups; "
        if behaviour_neg:
            neg_sentence += "not typically showing other behavioural patterns; "
        if destination_neg:
            neg_sentence += "and not strongly associated with some destinations."
        summary.append(neg_sentence)

    # Fallback when list too small
    if not summary:
        summary.append("✔️ Distinct behavioural and demographic traits compared to the wider base.")

    return " ".join(summary)



def render_customer_profiles(df, bookings_df, people_df):
    """
    Render SHORT, intuitive segment persona summaries.
    No long lists, no statistical breakdowns.
    """

    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    st.markdown("<h2>🧭 Segment Persona Summaries</h2>", unsafe_allow_html=True)
    st.markdown("""
        <p>These personas summarise the most meaningful, statistically significant traits 
        of each customer segment, expressed intuitively.</p>
    """, unsafe_allow_html=True)

    # --- Parse structure from insights ---
    parsed = []
    for txt in insights:
        try:
            field = txt.split("]")[0].replace("[", "")
            segment = txt.split("] ")[1].split(":")[0]
            category = txt.split("'")[1]
            dom = "Under" if "Under-represented" in txt else "Over"
            readable = intuitive_phrase(field, category, positive=(dom=="Over"))
            parsed.append((segment, dom, readable))
        except:
            continue

    # --- Group traits by segment ---
    by_segment = {}
    for segment, dom, phrase in parsed:
        by_segment.setdefault(segment, {"over": [], "under": []})
        if dom == "Over":
            by_segment[segment]["over"].append(phrase)
        else:
            by_segment[segment]["under"].append(phrase)

    # --- Generate summarised personas ---
    for segment, groups in by_segment.items():

        st.markdown(f"<h3 style='margin-top:30px;'>{segment}</h3>", unsafe_allow_html=True)

        summary_text = summarise_traits(groups["over"], groups["under"])

        st.markdown(f"""
            <p style='font-size:22px; line-height:1.5;'>{summary_text}</p>
        """, unsafe_allow_html=True)

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
