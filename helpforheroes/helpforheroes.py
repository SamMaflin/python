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

<br><br>
<h2>Final Segment Interpretations</h2>
<br>

<!-- ========================================================= -->
<!-- 1️⃣ Saver Casuals -->
<!-- ========================================================= -->
<h3>1️⃣ Saver Casuals — Interpretation</h3>
<p>
Saver Casuals are low-engagement, price-sensitive travellers who book rarely and tend to drift into long-term dormancy.
They are overwhelmingly occasional travellers, sitting more than +44 percentage points above the base.
Digital adoption is minimal, with website usage almost 10 points lower than average, and many haven’t travelled for 4–5 years (+21 ppts).
Their destination choices lean away from Europe and the Americas—especially the United States (−14 ppts)—while they are more drawn to Australia (+14 ppts) and Greece (+6 ppts).
This group skews slightly older and lower-income, with fewer retired or unemployed customers than expected.
Overall, Saver Casuals represent low-frequency, low-value customers who rarely re-engage once inactive.
</p>
<br>

<!-- ========================================================= -->
<!-- 2️⃣ Premium One-Timers -->
<!-- ========================================================= -->
<h3>2️⃣ Premium One-Timers — Interpretation</h3>
<p>
Premium One-Timers are typically female, with the female share sitting +44 points above the base, and many come from lower-income households (+12 ppts).
Despite making one premium purchase, they show extremely low retention: over half fall into the 5+ year very-old booking category (+38 ppts).
They favour digital and phone-led booking routes, especially the website (+32 ppts), and are far less likely to use travel agents (−22 ppts).
Their travel concentrates heavily in France (+32 ppts) and Germany (+12 ppts), while destinations like the US and Australasia are less common.
In essence, these customers make a high-value single purchase but almost never return, forming a premium—but one-off—segment.
</p>
<br>

<!-- ========================================================= -->
<!-- 3️⃣ Economy Explorers -->
<!-- ========================================================= -->
<h3>3️⃣ Economy Explorers — Interpretation</h3>
<p>
Economy Explorers are active, curious travellers who are far more engaged than typical economy customers.
They lean strongly male, with the female share sitting 21 points lower than average.
They are more middle-income (+18 ppts), more professionally employed, and their travel patterns reflect this: regular travel is +23 ppts above the base, and frequent travel also rises (+7 ppts).
Their destination portfolio is internationally oriented—particularly toward the United States (+19 ppts), along with selective interest in Italy, Kuwait, and Portugal.
They are also less dormant, showing slightly more recent travel activity (+3 ppts).
Overall, they are value-driven explorers who engage consistently and gravitate toward international destinations with agent support.
</p>
<br>

<!-- ========================================================= -->
<!-- 4️⃣ Premium Casuals -->
<!-- ========================================================= -->
<h3>4️⃣ Premium Casuals — Interpretation</h3>
<p>
Premium Casuals are higher-income travellers who show premium-style preferences despite booking infrequently.
They rely heavily on telephone enquiries (+17 ppts) and almost never use the website (−9 ppts).
Their recency profile is mixed, with fewer very recent bookings but also fewer extremely dormant customers.
Germany stands out strongly (+17 ppts), while France is notably under-represented (−9 ppts).
Demographically they show fewer unemployed and retail workers, aligning with a more financially stable segment.
Overall, Premium Casuals value personalised service and premium products but travel infrequently.
</p>
<br>

<!-- ========================================================= -->
<!-- 5️⃣ Economy One-Timers -->
<!-- ========================================================= -->
<h3>5️⃣ Economy One-Timers — Interpretation</h3>
<p>
Economy One-Timers are dominated by female customers (+45 ppts) and lean heavily toward lower-income households (+13 ppts).
As expected, this segment is overwhelmingly one-booking-only, sitting +35 ppts above the base.
They favour digital channels, especially the website (+34 ppts), and rarely use travel agents (−26 ppts).
Their recency profile shows deep inactivity, with many having booked more than five years ago (+36 ppts).
Their travel is concentrated in France (+34 ppts) and Germany (+12 ppts), while interest in the United States is much lower (−27 ppts).
Ultimately, Economy One-Timers represent budget-conscious, digitally driven, one-off customers who do not return.
</p>
<br>

<!-- ========================================================= -->
<!-- 6️⃣ Saver One-Timers -->
<!-- ========================================================= -->
<h3>6️⃣ Saver One-Timers — Interpretation</h3>
<p>
Saver One-Timers are almost entirely female (+58 ppts) and strongly low-income (+17 ppts).
They show very strong one-time behaviour, exceeding the base by +41 ppts, and recency indicates long-term disengagement, with a large spike in 4–5 year dormancy (+31 ppts).
Website usage is extremely high (+38 ppts), and agent usage is strikingly low (−31 ppts).
Travel patterns are concentrated in France (+39 ppts) and Germany (+20 ppts), with minimal travel to the US or Australasia.
This is a low-return, low-income group with very limited reactivation potential.
</p>
<br>

<!-- ========================================================= -->
<!-- 7️⃣ Economy Casuals -->
<!-- ========================================================= -->
<h3>7️⃣ Economy Casuals — Interpretation</h3>
<p>
Economy Casuals are light, low-commitment travellers who prefer simple booking paths.
They strongly favour telephone enquiries (+16 ppts) and rarely use the website (−9 ppts).
Almost all of them are occasional travellers, sitting +43 ppts above the base.
Many last travelled 3–4 years ago (+12 ppts), although fewer fall into the longest-dormant bucket (−11 ppts).
They show a preference for Germany (+16 ppts) but travel less often to France (−9 ppts) and the United States (−15 ppts).
Demographically they have fewer unemployed or retired customers and a lower share of middle-income earners.
Overall, these are low-effort customers who engage via phone and rarely return.
</p>
<br>

<!-- ========================================================= -->
<!-- 8️⃣ Premium Explorers -->
<!-- ========================================================= -->
<h3>8️⃣ Premium Explorers — Interpretation</h3>
<p>
Premium Explorers are highly engaged, high-value travellers with consistent activity.
They lean strongly male, with the female share 24 ppts below average, and tend to have higher incomes (+3 ppts High Income).
Their travel frequency is exceptional: regular travel is +20 ppts above the base, and frequent travel is +19 ppts, while occasional travel is significantly lower (−28 ppts).
They show more recent activity (+2 ppts) and far less long-term dormancy (−16 ppts in 4–5 years).
The United States is their standout destination (+24 ppts), supported by interest in Italy, Kuwait, and African destinations.
They avoid France (−9 ppts) and Europe more broadly (−23 ppts).
Overall, Premium Explorers are high-value, internationally oriented travellers with strong engagement and agent-led booking behaviour.
</p>
<br>

<!-- ========================================================= -->
<!-- 9️⃣ Saver Explorers -->
<!-- ========================================================= -->
<h3>9️⃣ Saver Explorers — Interpretation</h3>
<p>
Saver Explorers are budget-conscious yet highly active travellers with strong repeat patterns.
They favour regular travel (+29 ppts) and are much less likely to travel only occasionally (−18 ppts).
They skew male (female share −23 ppts) and are more likely to fall into the middle-income bracket (+19 ppts).
They over-index in managerial and retail roles and under-index among retired or manual workers.
Their travel choices lean toward off-beat destinations such as Portugal (+1 ppt), Namibia, and Africa (+1 ppt), while Europe is notably less common (−19 ppts).
They also rely more on agents and less on phone enquiries (−14 ppts).
Overall, Saver Explorers are active, curious travellers who explore widely while staying budget-conscious.
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
