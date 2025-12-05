# =====================================================================
#  STREAMLIT APP — CELTIC FC PLAYER VALUATION (CONFIG-DRIVEN)
# =====================================================================

import streamlit as st
import plotly.graph_objects as go


from analysis.model_engine import run_model
from analysis.model_config import ROLE_CONFIG

from analysis.summaries import (
    generate_gk_summary,
    generate_winger_summary,
    generate_midfielder_summary,
    generate_striker_summary,
)

from analysis.pizza_chart import (
    pizza_plot_combined,
    render_id_key,
    render_category_header,
)

# =====================================================================
# ROLE ORDER + SUMMARY MAPPING
# =====================================================================

# Fixed order: Goalkeeper → Winger → Central Midfielder → Striker
ROLE_ORDER = [
    ("goalkeeper", "Goalkeeper"),
    ("winger", "Winger"),
    ("midfielder", "Central Midfielder"),
    ("striker", "Striker"),
]

SUMMARY_FUNCS = {
    "goalkeeper": generate_gk_summary,
    "winger": generate_winger_summary,
    "midfielder": generate_midfielder_summary,
    "striker": generate_striker_summary,
}

# Global settings from config
GLOBAL_SETTINGS = ROLE_CONFIG["__settings__"]
DEFAULT_PATH = GLOBAL_SETTINGS["DEFAULT_PATH"]
DEFAULT_BUDGET = GLOBAL_SETTINGS["DEFAULT_BUDGET"]
DEFAULT_MINUTES = GLOBAL_SETTINGS["DEFAULT_MINUTES"]

# Optional: role-specific overrides (e.g. strikers with lower minutes)
ROLE_MIN_MINUTES = {
    "goalkeeper": DEFAULT_MINUTES,
    "winger": DEFAULT_MINUTES,
    "midfielder": DEFAULT_MINUTES,
    "striker": DEFAULT_MINUTES,  # as in your original app
}

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Celtic F.C Player Valuation Task",
    layout="centered",
)

# =====================================================================
# GLOBAL CSS + ROBOTO FONT
# =====================================================================
st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">

<style>
    * { font-family: 'Roboto', sans-serif !important; }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: #1B593A !important;
    }

    .block-container {
        max-width: 850px !important;
        margin-left: auto; margin-right: auto;
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] { display: none; }
    header, footer { visibility: hidden; }

    .title {
        font-size: 90px; font-weight: 600; color: white; letter-spacing: -1px;
        margin-bottom: 1em; text-align: left; line-height: 1.2;
    }

    .subtitle {
        font-size: 50px; font-weight: 700; color: white;
        margin-top: 0.5em; margin-bottom: 0.8em; text-align: left;
    }

    .intro {
        font-size: 18px; color: white; opacity: 0.92;
        line-height: 1.6; margin-bottom: 2em;
    }

    .section-label {
        font-size: 48px; font-weight: 900; color: #EB5F1F;
        border: 4px solid #EB5F1F; padding: 10px 24px;
        border-radius: 10px; display: inline-block;
        margin-top: 1.5em; margin-bottom: 1em;
    }

    .simple-text {
        font-size: 18px; color: white; opacity: 0.95;
        margin-bottom: 1.8em; line-height: 1.6;
    }

    .slider-block { margin-top: 1.6em; margin-bottom: 1.4em; }

    .slider-label { font-size: 26px; font-weight: 700; color: white; }
    .slider-sublabel { font-size: 14px; color: white; opacity: 0.85; }

    div.stButton > button {
        padding: 18px 32px !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# PRIORITY SCALE + MULTIPLIERS
# =====================================================================
PRIORITY_SCALE = [
    "Minimum",
    "Very Low",
    "Low",
    "Slightly Low",
    "Balanced",
    "Slightly High",
    "High",
    "Very High",
    "Maximum"
]

PRIORITY_MULT = {
    "Minimum": 0.01,
    "Very Low": 0.25,
    "Low": 0.5,
    "Slightly Low": 0.75,
    "Balanced": 1.0,
    "Slightly High": 1.25,
    "High": 1.5,
    "Very High": 1.75,
    "Maximum": 2
}

# =====================================================================
# UNIVERSAL ROLE SECTION
# =====================================================================
def role_section(role_key: str, display_name: str):
    """
    Render one role block (Goalkeeper, Winger, Central Midfielder, Striker)
    using ROLE_CONFIG and run_model.
    """
    cfg = ROLE_CONFIG[role_key]
    text = cfg["text"]
    sliders = cfg["sliders"]
    groups = cfg["groups"]
    invert = cfg["invert"]
    summary_fn = SUMMARY_FUNCS[role_key]

    # Header + descriptive text
    st.markdown(
        f"<div class='section-label'>{display_name}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='simple-text'>{text}</div>",
        unsafe_allow_html=True,
    )

    # Collect slider priorities from user
    slider_vals = {}
    for label, key in sliders:
        st.markdown(
            f"""
            <div class="slider-block">
                <div class="slider-label">{label}</div>
                <div class="slider-sublabel">(Priority Level)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        slider_vals[key] = st.select_slider(
            label=f"{label} Priority",
            options=PRIORITY_SCALE,
            value="Balanced",
            key=f"{role_key}_{key}",  # ensure uniqueness across roles
            label_visibility="collapsed",
        )

    # Run the model when the user clicks the button
    if st.button(f"Find {display_name}", key=f"find_{role_key}"):

        # Convert slider words → numeric multipliers
        multiplier_dict = {k: PRIORITY_MULT[v] for k, v in slider_vals.items()}

        min_minutes = ROLE_MIN_MINUTES.get(role_key, DEFAULT_MINUTES)

        df = run_model(
            role_key,
            path=DEFAULT_PATH,
            min_minutes=min_minutes,
            budget_million=DEFAULT_BUDGET,
            **multiplier_dict,
        )

        if df.empty:
            st.warning("No players matched the filters for this position.")
            return

        # Rank by BuyScore
        df_sorted = df.sort_values("BuyScore", ascending=False)
        top = df_sorted.iloc[0]
        others = df_sorted.iloc[1:4].copy()

        # Hit summary
        st.success(f"{display_name} found: **{top['ID']} – {top['Team']}**")
        st.markdown(summary_fn(top, others), unsafe_allow_html=True)

        # Profile breakdown
        st.markdown(
            "<div class='subtitle'>Profile Breakdown:</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='slider-sublabel'><i>*Percentiles are per-90 and competition-adjusted.</i></div>",
            unsafe_allow_html=True,
        )

        render_category_header(groups)
        render_id_key(groups)

        fig = pizza_plot_combined(top, df_sorted, groups, invert)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# INTRO SECTION
# =====================================================================
st.image("analysis/celticlogo.png", width=260)

st.markdown(
    "<div class='title'>Celtic F.C. Player Recruitment Task</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="intro">
Welcome! The following application was designed to identify potentially undervalued players using performance, contextual and market data.
The task was to identify <span style="color:#FFA500;"><b>four</b></span> value-efficient targets across key roles:
<span style="color:#FFA500;"><b>Goalkeeper</b></span>,
<span style="color:#FFA500;"><b>Winger</b></span>,
<span style="color:#FFA500;"><b>Striker</b></span>,
and <span style="color:#FFA500;"><b>Central Midfielder</b></span>, after adjusting for factors including
<i>team style</i>, <i>league strength</i>, <i>age</i> and <i>transfer value</i>.<br></br>

The model is fully configurable, allowing you to prioritise different attributes via sliders.
Once selected, the model will generate a ranked shortlist of candidates according to a
<span style="color:#FFA500;"><b>BuyScore</b></span> index.<br></br>
</div>
""",
    unsafe_allow_html=True,
)


st.markdown("<div class='subtitle'>Let's Get Started…</div>", unsafe_allow_html=True)

# =====================================================================
# RENDER ROLES IN FIXED ORDER
# =====================================================================
for role_key, display_name in ROLE_ORDER:
    role_section(role_key, display_name)


# Header + descriptive text
st.markdown(
    f"<div class='section-label'>Review</div>",
    unsafe_allow_html=True,
)

# Question + Answer
st.markdown(
    f"""
    <div class='simple-text'>
    <b>Q: If you had access to more data, what would change in your approach?</b><br><br>

    If I had access to more detailed and contextual data, my approach would become sharper, more predictive, and much more tightly aligned to Celtic’s game model. I already apply league-strength and age multipliers, but they are necessarily broad. With richer datasets, I could build <b>position- and league-specific translation factors</b> that better reflect real tactical environments. For example, goalkeepers in England are typically exposed to more aerial traffic and physical contact, while those in more possession-oriented leagues develop stronger distribution skills. These nuances matter, and better data would allow me to quantify them instead of relying on generic corrections (This is a very vague generalisation but you get the point!).<br><br>

    The biggest limitation of pure event data is the lack of <b>physical, tracking, and off-ball information</b>. Celtic’s style demands high-intensity repetition, aggressive counterpressing, sharp accelerations over short distances, and the ability to receive and play under pressure. None of that is fully captured in standard event logs. With access to physical outputs – such as high-intensity runs, repeat-sprint capacity, pressing velocity, and deceleration profiles – I could build more accurate archetypes for press-resistant midfielders, energy eights, proactive centre-backs, and forwards who trigger the counterpress. These factors would also feed into a more realistic <b>BuyScore</b>, where physical resilience and durability sit alongside technical and tactical quality.<br><br>

    <b>Injury data</b> is another key gap. A clearer view of injury frequency, severity, re-injury risk, minutes lost, and recovery patterns would help ensure the BuyScore reflects not just performance, but <i>availability</i> – a critical edge in Celtic’s congested domestic and European schedule.<br><br>

    Finally, with more time and access to Celtic’s internal GPS benchmarks, tactical templates, and squad physical profiles, I would build <b>Celtic-specific benchmarking</b>. That would allow me to compare targets directly against current Celtic players in the same role, so we are not just identifying good players, but the ones who represent a reliable and meaningful upgrade for Celtic.
    </div>
    """,
    unsafe_allow_html=True,
)



# =====================================================================
# END OF APP
# =====================================================================
