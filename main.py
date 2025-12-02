# =====================================================================
#  STREAMLIT APP — CELTIC FC PLAYER VALUATION (FULL REWRITE)
#  With global Roboto font + unified pizza chart font
# =====================================================================

import streamlit as st
from analysis import (
    run_gk_model,
    GK_GROUPS,
    GK_INVERT,
    GK_SLIDERS,
    GK_COLS,
    GK_TEXT,
    generate_gk_summary,
)

# =============== IMPORT PIZZA COMPONENTS (included below) ===============
from pizza_chart import (
    pizza_plot_combined,
    render_id_key,
    render_category_header,
)

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
    * {
        font-family: 'Roboto', sans-serif !important;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: #1B593A !important;
    }

    .block-container {
        max-width: 850px !important;
        margin-left: auto;
        margin-right: auto;
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] { display: none; }
    header, footer { visibility: hidden; }

    .title {
        font-size: 60px;
        font-weight: 700;
        color: white;
        letter-spacing: -2px;
        margin-bottom: 0.3em;
        text-align: left;
    }

    .subtitle {
        font-size: 50px;
        font-weight: 700;
        color: white;
        letter-spacing: -2px;
        margin-top: 0.5em;
        margin-bottom: 0.8em;
        text-align: left;
    }

    .intro {
        font-size: 18px;
        color: white;
        opacity: 0.92;
        line-height: 1.6;
        margin-bottom: 2em;
    }

    .section-label {
        font-size: 48px;
        font-weight: 900;
        color: #EB5F1F;
        border: 4px solid #EB5F1F;
        padding: 10px 24px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 1.5em;
        margin-bottom: 1em;
    }

    .simple-text {
        font-size: 18px;
        color: white;
        opacity: 0.95;
        margin-bottom: 1.8em;
        line-height: 1.6;
    }

    .slider-block {
        margin-top: 1.6em;
        margin-bottom: 1.4em;
    }

    .slider-label {
        font-size: 26px;
        font-weight: 700;
        color: white;
        margin-bottom: 0.15em;
    }

    .slider-sublabel {
        font-size: 14px;
        color: white;
        opacity: 0.85;
        margin-bottom: 0.5em;
    }

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
scale = [
    "Very Low", "Low", "Slightly Low", "Balanced",
    "Slightly High", "High", "Very High"
]

MULT = {
    "Very Low": 0.6,
    "Low": 0.75,
    "Slightly Low": 0.9,
    "Balanced": 1.0,
    "Slightly High": 1.1,
    "High": 1.25,
    "Very High": 1.4,
}


# =====================================================================
# POSITION SECTION FUNCTION
# =====================================================================
def position_section(name, text, model_fn, groups, invert, sliders, args, columns):

    st.markdown(f"<div class='section-label'>{name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='simple-text'>{text}</div>", unsafe_allow_html=True)

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
            "",
            options=scale,
            value="Balanced",
            key=f"{name}_{key}"
        )

    if st.button(f"Find {name}"):

        mults = {k: MULT[v] for k, v in slider_vals.items()}

        df = model_fn(**args, **mults)
        top = df.sort_values("BuyScore", ascending=False).iloc[0]

        st.success(f"{name} found: **{top['ID']} – {top['Team']}**")
        st.markdown(generate_gk_summary(top), unsafe_allow_html=True)

        st.markdown("<div class='subtitle'>Profile Breakdown:</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="slider-sublabel"><i>*Metrics shown below are per-90 adjusted percentile rank.</i></div>',
            unsafe_allow_html=True
        )

        render_category_header(groups)
        render_id_key(groups)

        fig = pizza_plot_combined(top, df, groups, invert)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# INTRO SECTION
# =====================================================================
st.image("celticlogo.png", width=260)

st.markdown("<div class='title'>Celtic F.C. Player Evaluation Task</div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="intro">
This application identifies undervalued players for Celtic F.C., using performance data,
contextual factors and tactical fit.  
You can compare and customise models for Goalkeeper, Defender, Midfielder and Striker.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='subtitle'>Let's Get Started…</div>", unsafe_allow_html=True)


# =====================================================================
# GK SECTION
# =====================================================================
position_section(
    "Goalkeeper",
    GK_TEXT,
    run_gk_model,
    GK_GROUPS,
    GK_INVERT,
    GK_SLIDERS,
    args=dict(path="Final_Task_Data.csv", min_minutes=900),
    columns=GK_COLS,
)

# ⬆ END MAIN APP
# =====================================================================


