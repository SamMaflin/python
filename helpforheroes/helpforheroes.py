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


def render_customer_profiles(df, bookings_df, people_df):
    """
    Render an intuitive, story-led set of segment profiles in Streamlit.
    """

    # ------------------------------------------------------------
    # RUN PROFILING ENGINE
    # ------------------------------------------------------------
    prof_df, results, insights = customer_profiles(df, bookings_df, people_df)

    # ------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------
    st.markdown(
        "<h2>Who Are These Customers? — Segment Profiles</h2>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------
    # HIGH-LEVEL EXPLANATION (NON-TECHNICAL)
    # ------------------------------------------------------------
    st.markdown("### How these insights were built (in plain English)")

    st.markdown(
        """
We wanted to understand **who actually sits inside each segment**, and how different they are from your *overall* customer base.

To do this, we:

1. Looked at each customer characteristic:  
   – Age, income, gender, occupation  
   – How they book (channel)  
   – How often and how recently they book  

2. Worked out **what share of the full customer base** is in each category.  
   This is our **baseline**.

3. Then, for each segment, we looked at **what share of that segment** sits in the same category.

- If a segment has **far more** of a group than the baseline → that group is **over-represented**.  
- If it has **far fewer** → that group is **under-represented**.

We also use an **Index** to show how strong the difference is:

- `Index = 1.0` → exactly as expected  
- `Index = 2.0` → **twice as common** as expected  
- `Index = 0.5` → **half as common** as expected  

This lets us turn raw numbers into **human descriptions**:
who dominates each segment, who is missing, and how their behaviour stands out.
        """
    )

    st.markdown("---")

    # ============================================================
    # SEGMENT PROFILES (INTUITIVE DESCRIPTIONS)
    # ============================================================

    # 1️⃣ Economy Casuals
    with st.expander("1️⃣ Economy Casuals", expanded=True):
        st.markdown("**Light, low-commitment travellers, usually phoning in and rarely returning.**")

        st.markdown("**Who they tend to be**")
        st.markdown(
            """
- Slightly more **male** than average  
- Fewer **retired** or **unemployed** customers than expected  
- Income skews a bit lower, but not dramatically  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Almost all are **occasional travellers** (very few repeat trips)  
- Strong preference for **telephone enquiries**  
- Almost **no website usage**  
- Many last booked **3–4 years ago**, so a lot of them are effectively dormant  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Low-effort, low-frequency phone bookers who rarely come back.**")

    # 2️⃣ Economy Explorers
    with st.expander("2️⃣ Economy Explorers"):
        st.markdown("**Value travellers who like variety and travel more actively, but stay budget-conscious.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Strongly **male-dominated**  
- Fewer **students**, **retirees** and very **low-income** customers  
- Higher presence of **professionals**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Prefer **travel agents** over direct or digital  
- More **frequent** and **exploratory** (more destinations per person)  
- Less likely to be long-dormant than other economy segments  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Active male value-seekers who use agents and like to explore.**")

    # 3️⃣ Economy One-Timers
    with st.expander("3️⃣ Economy One-Timers"):
        st.markdown("**Low-income, mostly female customers who took one trip and never came back.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Strong **female** skew  
- Many are **retired** and/or **lower-income**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Less likely to use **travel agents** or **Expedia**  
- Bookings are typically **very old** – long periods with no activity  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Budget-limited one-off female travellers who rarely re-engage.**")

    # 4️⃣ Premium Casuals
    with st.expander("4️⃣ Premium Casuals"):
        st.markdown("**Higher-spend but infrequent travellers who behave like premium customers, but don’t book often.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Income slightly **higher** than economy segments  
- Mix of occupations, with **fewer unemployed**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Very strong **telephone-first** preference  
- Almost **no website bookings**  
- Mostly **occasional** travellers  
- A big chunk last booked **2–3 years ago**  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Premium-leaning but old-fashioned travellers: phone-first, low-frequency, often lapsed.**")

    # 5️⃣ Premium Explorers
    with st.expander("5️⃣ Premium Explorers"):
        st.markdown("**High-value, active, agent-driven male travellers who explore widely.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Heavily **male**  
- Strong **middle-income** presence  
- Many **managers** and **professionals**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Rely heavily on **travel agents** and **Expedia**  
- Visit a **wider range of destinations** than most  
- Less likely to be long-dormant  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **High-value male explorers who book via professional channels and stay active.**")

    # 6️⃣ Premium One-Timers
    with st.expander("6️⃣ Premium One-Timers"):
        st.markdown("**Premium but irregular: higher-spend travellers who behaved like a one-off.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Strong **female** presence  
- Mix of **lower-income** groups  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Low usage of **agents** or **Expedia**  
- Trips are **not recent**, with many falling dormant after a single premium purchase  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Higher-spend females who bought once at a premium level, then disappeared.**")

    # 7️⃣ Saver Casuals
    with st.expander("7️⃣ Saver Casuals"):
        st.markdown("**Very infrequent, price-sensitive customers with little recent activity.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Under-represented in **high income**  
- More likely to be **middle-aged or older**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Almost all are **occasional travellers**  
- Almost **no website usage**  
- A very large share have been **dormant for 4–5 years**  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Price-sensitive, low-engagement customers who haven’t travelled in years.**")

    # 8️⃣ Saver Explorers
    with st.expander("8️⃣ Saver Explorers"):
        st.markdown("**High-frequency budget travellers — very different from Saver Casuals.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Very **male-heavy**  
- Over-represented among **managers** and **retail workers**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Heavily reliant on **travel agents**  
- Over-index on **frequent booking**  
- Explore more destinations than other saver segments  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Budget-savvy male frequent travellers who use agents and still explore.**")

    # 9️⃣ Saver One-Timers
    with st.expander("9️⃣ Saver One-Timers"):
        st.markdown("**Low-income, mostly female one-off travellers who haven’t come back.**")

        st.markdown("**Who they are**")
        st.markdown(
            """
- Strongly **female**  
- High presence of **manual workers** and **retirees**  
- Mostly **low-income**  
            """
        )

        st.markdown("**How they book & behave**")
        st.markdown(
            """
- Very little recent activity — often **dormant for years**  
- Rarely return after their first booking  
            """
        )

        st.markdown("**Overall personality**")
        st.markdown("➡️ **Low-income one-off travellers with minimal likelihood of re-engaging.**")


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
