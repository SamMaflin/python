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
we measured the % share in the overall population and the % share within each segment.
This reveals whether a segment contains <b>more</b> or <b>fewer</b> customers of a certain type than expected.
</p>

<h4>2️⃣ Statistical Reliability</h4>
<p>
We then apply a <b>proportions Z-test</b> to confirm that differences are statistically meaningful,
and use percentage-point differences to communicate the size of the effect clearly.
</p>

<br><br>
<h2>Final Segment Interpretations</h2>
<br>

<!-- ========================================================= -->
<!-- 1️⃣ Saver Casuals -->
<!-- ========================================================= -->
<h3>1️⃣ Saver Casuals — Interpretation</h3>
<p>
Saver Casuals are low-engagement, price-sensitive travellers who book rarely and often drift into long-term dormancy.
They are overwhelmingly occasional travellers, sitting more than <b>+44 percentage points</b> above the base.
Digital adoption is minimal, with website usage almost <b>10 points lower</b>, and many haven’t travelled for 4–5 years
(<b>+21 ppts</b>).
Their destination choices lean away from Europe and the Americas—especially the United States (<b>−14 ppts</b>)—
while Australia (<b>+14 ppts</b>) and Greece (<b>+6 ppts</b>) feature more prominently.
This group skews slightly older and lower-income, with fewer retired or unemployed customers than expected.
Overall, Saver Casuals represent low-frequency, low-value customers who rarely re-engage once inactive.
</p>
<br>

<!-- ========================================================= -->
<!-- 2️⃣ Premium One-Timers -->
<!-- ========================================================= -->
<h3>2️⃣ Premium One-Timers — Interpretation</h3>
<p>
Premium One-Timers are typically female, with the female share sitting <b>+44 ppts</b> above the base,
and many belong to lower-income households (<b>+12 ppts</b>).
Despite making a premium purchase, they show extremely low retention: more than half fall into the
5+ year very-old booking category (<b>+38 ppts</b>).
They heavily favour digital and phone-led booking routes, especially the website (<b>+32 ppts</b>),
and use travel agents far less (<b>−22 ppts</b>).
Their holidays concentrate in France (<b>+32 ppts</b>) and Germany (<b>+12 ppts</b>), with far less travel to the US or Australasia.
Overall, they are high-spend, predominantly female one-off customers who do not return after their initial premium booking.
</p>
<br>

<!-- ========================================================= -->
<!-- 3️⃣ Economy Explorers -->
<!-- ========================================================= -->
<h3>3️⃣ Economy Explorers — Interpretation</h3>
<p>
Economy Explorers are active, curious travellers who show far more engagement than typical economy segments.
They lean strongly male, with the female share <b>−21 ppts</b> below average,
and are more likely to fall into the middle-income bracket (<b>+18 ppts</b>) and professional occupations.
Their travel frequency stands out: regular travel sits <b>+23 ppts</b> above the base, and frequent travel rises <b>+7 ppts</b>.
Their destination portfolio is internationally oriented—particularly toward the United States (<b>+19 ppts</b>)—
with selective interest in Italy, Kuwait, and Portugal.
They show slightly more recent travel (<b>+3 ppts</b>) and lower dormancy.
Overall, they are value-driven explorers who travel often and lean toward agent-supported international trips.
</p>
<br>

<!-- ========================================================= -->
<!-- 4️⃣ Premium Casuals -->
<!-- ========================================================= -->
<h3>4️⃣ Premium Casuals — Interpretation</h3>
<p>
Premium Casuals are higher-income travellers who display premium preferences despite booking infrequently.
They rely heavily on telephone enquiries (<b>+17 ppts</b>) and almost never use the website (<b>−9 ppts</b>).
Their recency pattern is mixed: fewer very recent trips but also fewer long-dormant customers.
Destination choices favour Germany (<b>+17 ppts</b>) and avoid France (<b>−9 ppts</b>).
They show fewer unemployed or retail workers, aligning with a more financially stable profile.
Overall, Premium Casuals value personalised service and premium products but maintain modest travel frequency.
</p>
<br>

<!-- ========================================================= -->
<!-- 5️⃣ Economy One-Timers -->
<!-- ========================================================= -->
<h3>5️⃣ Economy One-Timers — Interpretation</h3>
<p>
Economy One-Timers are heavily female (<b>+45 ppts</b>) and lean toward lower-income households (<b>+13 ppts</b>).
As expected, one-time behaviour is highly dominant (<b>+35 ppts</b> above the base).
They strongly favour digital channels, especially the website (<b>+34 ppts</b>), and rarely use agents (<b>−26 ppts</b>).
Their recency indicates deep disengagement, with many having booked more than five years ago (<b>+36 ppts</b>).
Their holidays concentrate in France (<b>+34 ppts</b>) and Germany (<b>+12 ppts</b>), and they show reduced interest in the United States (<b>−27 ppts</b>).
Overall, they are budget-conscious, digitally driven one-off customers with minimal long-term value.
</p>
<br>

<!-- ========================================================= -->
<!-- 6️⃣ Saver One-Timers -->
<!-- ========================================================= -->
<h3>6️⃣ Saver One-Timers — Interpretation</h3>
<p>
Saver One-Timers are almost entirely female (<b>+58 ppts</b>) and strongly represented in low-income households (<b>+17 ppts</b>).
They show extremely strong one-time behaviour (<b>+41 ppts</b>) and long-term disengagement, with a large spike in 4–5 year dormancy (<b>+31 ppts</b>).
Website usage is exceptionally high (<b>+38 ppts</b>), and travel agent usage is very low (<b>−31 ppts</b>).
Their destination patterns cluster around France (<b>+39 ppts</b>) and Germany (<b>+20 ppts</b>), with very little travel to the US or Australasia.
Overall, Saver One-Timers are low-income, low-return travellers with minimal reactivation potential.
</p>
<br>

<!-- ========================================================= -->
<!-- 7️⃣ Economy Casuals -->
<!-- ========================================================= -->
<h3>7️⃣ Economy Casuals — Interpretation</h3>
<p>
Economy Casuals are light, low-commitment travellers who prefer simple booking channels.
They strongly favour telephone enquiries (<b>+16 ppts</b>) and rarely use the website (<b>−9 ppts</b>).
Almost all are occasional travellers (<b>+43 ppts</b> above the base).
Many last travelled 3–4 years ago (<b>+12 ppts</b>), with fewer in the longest-dormant bucket (<b>−11 ppts</b>).
They show a preference for Germany (<b>+16 ppts</b>) and reduced travel to France (<b>−9 ppts</b>) and the United States (<b>−15 ppts</b>).
Demographically, they include fewer unemployed or retired customers and a smaller middle-income share.
Overall, they represent low-effort, phone-first customers with limited repeat behaviour.
</p>
<br>

<!-- ========================================================= -->
<!-- 8️⃣ Premium Explorers -->
<!-- ========================================================= -->
<h3>8️⃣ Premium Explorers — Interpretation</h3>
<p>
Premium Explorers are highly engaged, high-value travellers with strong, consistent activity.
They lean strongly male (female share <b>−24 ppts</b>) and sit slightly higher in income brackets (<b>+3 ppts</b> High Income).
Their travel frequency is exceptional: regular travel is <b>+20 ppts</b> above the base and frequent travel is <b>+19 ppts</b>,
with far fewer occasional travellers (<b>−28 ppts</b>).
They show more recent activity (<b>+2 ppts</b>) and far less long-term dormancy (<b>−16 ppts</b>).
Their destination preferences are strongly international, led by the United States (<b>+24 ppts</b>),
alongside Italy, Kuwait, and Africa.
They avoid France (<b>−9 ppts</b>) and Europe more broadly (<b>−23 ppts</b>).
Overall, Premium Explorers are high-value, internationally oriented travellers who rely on agent-led booking styles.
</p>
<br>

<!-- ========================================================= -->
<!-- 9️⃣ Saver Explorers -->
<!-- ========================================================= -->
<h3>9️⃣ Saver Explorers — Interpretation</h3>
<p>
Saver Explorers are budget-conscious but highly active travellers with strong repeat habits.
They favour regular travel (<b>+29 ppts</b>) and are far less likely to travel only occasionally (<b>−18 ppts</b>).
They skew more male (female share <b>−23 ppts</b>) and more often fall into the middle-income bracket (<b>+19 ppts</b>).
Occupationally, they over-index among managers and retail workers and under-index among retired or manual workers.
Their travel choices include off-beat destinations such as Portugal (<b>+1 ppt</b>), Namibia, and Africa (<b>+1 ppt</b>),
while Europe is significantly less common (<b>−19 ppts</b>).
They rely more on travel agents and less on phone enquiries (<b>−14 ppts</b>).
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
