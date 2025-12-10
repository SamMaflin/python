
import streamlit as st

from data_loader import load_helpforheroes_data
from metrics_engine import calculate_customer_value_metrics
from segment_barchart import segment_barchart_plot


# ============================================================
# COLOUR PALETTE (Consistent Across Dashboard)
# ============================================================
SPEND_COLOR       = "#0095FF"   # deep blue
ENGAGEMENT_COLOR  = "#00FF80"   # green-teal
STRATEGIC_COLOR   = "#FF476C"   # crimson red


# ============================================================
# STREAMLIT APP UI
# ============================================================

# -------------------------------
# LOGO
# -------------------------------
try:
    st.image("helpforheroes/hfh_logo.png", width=200)
except:
    pass


# -------------------------------
# GLOBAL CSS STYLING
# -------------------------------
st.markdown("""
<style>

h1 { font-size: 60px !important; font-weight: 700 !important; }
h2 { font-size: 50px !important; font-weight: 700 !important; margin-top: 120px !important; }

h3.small-h3 {
    font-size: 34px !important;
    font-weight: 700 !important;
    margin: 30px 0 15px 0 !important;
}

p, li { 
    font-size: 22px !important; 
    line-height: 1.45 !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# TITLE
# -------------------------------
st.markdown("<h1>Help for Heroes — Customer Holiday Bookings Insights</h1>", unsafe_allow_html=True)



# ============================================================
# INTRODUCTION
# ============================================================
st.markdown("<h2>Introduction</h2>", unsafe_allow_html=True)

st.markdown("""
<p>
All customers create value — but not in the same way.  
Some generate high spend, some demonstrate very strong behavioural loyalty,  
and others align closely with strategic business priorities.

Understanding <b>how</b> each customer contributes enables:
• better targeting,  
• more personalised marketing,  
• and improved value growth.
</p>
""", unsafe_allow_html=True)



# ============================================================
# VALUE DIMENSIONS OVERVIEW
# ============================================================
st.markdown("<h2>How Do We Measure Customer Value?</h2>", unsafe_allow_html=True)

st.markdown(
f"""
<h4><span style="color:{SPEND_COLOR}; font-weight:bold;">● Spend Score</span> — Financial Contribution</h4>
<p>Based on Average Booking Value and Maximum Booking Value.</p>

<h4><span style="color:{ENGAGEMENT_COLOR}; font-weight:bold;">● Engagement Score</span> — Behaviour & Loyalty</h4>
<p>Based on Frequency, Destination Diversity, and Booking Recency.</p>

<h4><span style="color:{STRATEGIC_COLOR}; font-weight:bold;">● Strategic Score</span> — Alignment With Business Goals</h4>
<p>Based on Long-Haul behaviour, Package adoption, and Channel fit.</p>
""",
unsafe_allow_html=True)



# ============================================================
# METRIC CONSTRUCTION SECTION
# ============================================================
st.markdown("<h2>Metric Construction</h2>", unsafe_allow_html=True)



# -------------------------------
# SPEND SCORE
# -------------------------------
st.markdown(
f"""
<h3 class='small-h3'><span style='color:{SPEND_COLOR}; font-weight:bold;'>Spend Score (0–100)</span></h3>
<ul>
    <li><b>Average Booking Amount</b> reflects typical spend per trip.</li>
    <li><b>Maximum Booking Amount</b> picks up premium or high-value trips.</li>
    <li>The combined SpendScore (70% Avg / 30% Max), normalised 0–100, balances stability with sensitivity to premium purchases.</li>
</ul>
""",
unsafe_allow_html=True
)



# -------------------------------
# ENGAGEMENT SCORE
# -------------------------------
st.markdown(
f"""
<h3 class='small-h3'><span style='color:{ENGAGEMENT_COLOR}; font-weight:bold;'>Engagement Score (0–100)</span></h3>
<ul>
    <li>Combines <b>Frequency</b>, <b>Recency</b>, and <b>Diversity</b> into a single index.</li>
    <li><b>Diversity</b> blends unique destinations and exploration ratio (unique ÷ trips).</li>
    <li>Weighting: 50% Frequency, 30% Recency, 20% Diversity — reflecting actual holiday behaviours and churn risk.</li>
</ul>
""",
unsafe_allow_html=True
)



# -------------------------------
# STRATEGIC SCORE
# -------------------------------
st.markdown(
f"""
<h3 class='small-h3'><span style='color:{STRATEGIC_COLOR}; font-weight:bold;'>Strategic Score (0–100)</span></h3>
<ul>
    <li>Binary indicators (Long-haul, Package, Channel Fit) mapped to 0/100 for consistency.</li>
    <li>Weighted StrategicScore: Long-Haul (50%), Package (30%), Channel Fit (20%).</li>
</ul>
""",
unsafe_allow_html=True
)



# ============================================================
# SEGMENTATION GRID (IMAGE)
# ============================================================
st.markdown("<h2>Customer Segmentation Matrix</h2>", unsafe_allow_html=True)
st.image("helpforheroes/matrix_plot.png", use_column_width=True)



# ============================================================
# LOAD DATA + CALCULATE METRICS
# ============================================================
data = load_helpforheroes_data("helpforheroes/helpforheroes.xls")
df = calculate_customer_value_metrics(data["People_Data"], data["Bookings_Data"])



# ============================================================
# CUSTOMER BASE vs REVENUE CONTRIBUTION
# ============================================================
st.markdown("<h2>Customer Base vs Revenue Contribution by Segment</h2>", unsafe_allow_html=True)

# Render external chart module
segment_barchart_plot(df, data["Bookings_Data"])



# ============================================================
# SEGMENT INSIGHTS
# ============================================================
st.markdown("<h2>Early Segment Insights</h2>", unsafe_allow_html=True)

st.markdown("""
<ul>
    <li><b>Premium Loyalists</b> and <b>Premium Regulars</b> generate the largest share of revenue — but for different reasons (frequency vs ticket size).</li>
    <li><b>Loyal Value</b> and <b>Developing Value</b> represent strong growth opportunities.</li>
    <li><b>One-Off Premiums</b> hold the biggest reactivation opportunity.</li>
    <li><b>At-Risk Decliners</b> are a priority group for retention intervention.</li>
    <li><b>Engaged Low-Spend</b> show high loyalty but low spend — a monetisation opportunity.</li>
    <li><b>Dormant Base</b> is low-value and should not receive heavy marketing investment.</li>
</ul>
""",
unsafe_allow_html=True)
