import streamlit as st
import pandas as pd

# python -m streamlit run main.py


# ================================================================
#                   CONFIGURATION + STYLING
# ================================================================

FONT_FAMILY_URL = "https://fonts.googleapis.com/css2?family=Belleza&display=swap"
FONT_NAME = "'Belleza', sans-serif"

SIZE_H1 = "100px"
SIZE_H3 = "60px"
SIZE_H4 = "50px"
SIZE_H5 = "24px"
SIZE_P = "20px"

DEFAULT_WEIGHT = 500
LINE_HEIGHT = "1.6"

COLOR_TEXT = "white"
COLOR_BG_MAIN = "#1B593A"
COLOR_BG_SIDEBAR = "#113825"
ORANGE = "#EC7C2C"

LOGO_PATH = "/celticlogo.png"
LOGO_SIZE = "350px"

MARGIN_BOTTOM = "0.5em"
MARGIN_BOTTOM_LARGE = "3em"
MARGIN_BOTTOM_TOP = "3em"

# ================================================================
#                           GLOBAL CSS
# ================================================================

GLOBAL_CSS = f"""
<style>
    @import url('{FONT_FAMILY_URL}');

    html, body, * {{
        font-family: {FONT_NAME};
        color: {COLOR_TEXT};
    }}

    .text-h1 {{
        font-size: {SIZE_H1};
        line-height: 1;
        margin-bottom: {MARGIN_BOTTOM};
        font-weight: 600;
    }}

    .text-h3 {{
        font-size: {SIZE_H3};
        line-height: {LINE_HEIGHT};
        margin-bottom: {MARGIN_BOTTOM};
        font-weight: 600;
    }}

    .text-h4 {{
        font-size: {SIZE_H4};
        line-height: {LINE_HEIGHT};
        margin-bottom: {MARGIN_BOTTOM};
        font-weight: 600;
    }}

    .text-h5 {{
        font-size: {SIZE_H5};
        margin-bottom: {MARGIN_BOTTOM};
        font-weight: 600;
    }}

    .text-p {{
        font-size: {SIZE_P};
        line-height: {LINE_HEIGHT};
        margin-bottom: {MARGIN_BOTTOM_LARGE};
        margin-top: {MARGIN_BOTTOM_TOP};
    }}

    .stApp {{
        background-color: {COLOR_BG_MAIN};
        background-image: url("{LOGO_PATH}");
        background-position: center;
        background-size: {LOGO_SIZE};
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BG_SIDEBAR};
    }}

    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    div[data-baseweb="slider"] span {{
        display: none !important;
    }}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ================================================================
#                     STATIC TEXT STYLER
# ================================================================

STYLE_MAP = {
    "h1": ("text-h1", SIZE_H1),
    "h3": ("text-h3", SIZE_H3),
    "h4": ("text-h4", SIZE_H4),
    "h5": ("text-h5", SIZE_H5),
    "p":  ("text-p", SIZE_P),
}

def styled(text, type="p", color=None, weight=None, border=False):
    css_class, _ = STYLE_MAP[type]
    extra_color = f"color:{color};" if color else ""
    weight_css = f"font-weight:{weight if weight else DEFAULT_WEIGHT};"

    border_css = ""
    if border:
        border_css = (
            f"border: 3px solid {ORANGE};"
            "padding: 15px 25px;"
            "border-radius: 10px;"
            "display: inline-block;"
        )

    st.markdown(
        f'''
        <div class="{css_class}"
             style="{extra_color}{weight_css}{border_css}">
            {text}
        </div>
        ''',
        unsafe_allow_html=True
    )

# ================================================================
#                   GK WEIGHTING SYSTEM
# ================================================================

SS_BASE = 0.55
D_BASE  = 0.30
SW_BASE = 0.15

MULTIPLIER_MAP = {
    "Very Low": 0.70,
    "Low": 0.85,
    "Slightly Low": 0.95,
    "Balanced": 1.00,
    "Slightly High": 1.10,
    "High": 1.20,
    "Very High": 1.30
}

def calculate_gk_weights(shot_label, dist_label, sweep_label):

    ss = SS_BASE * MULTIPLIER_MAP[shot_label]
    d  = D_BASE  * MULTIPLIER_MAP[dist_label]
    sw = SW_BASE * MULTIPLIER_MAP[sweep_label]

    total = ss + d + sw

    ss /= total
    d  /= total
    sw /= total

    # Print to terminal (what you asked for)
    print("=== GK Weight Output ===")
    print("Shot-Stopping:", ss)
    print("Distribution:", d)
    print("Sweeper:", sw)
    print("========================")

    return ss, d, sw

# ================================================================
#                             CONTENT
# ================================================================

def intro_section():

    # --- Center Celtic Logo Above Title ---
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-top:20px; margin-bottom:10px;">
            <img src="{LOGO_PATH}" style="width:200px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Title
    styled("Celtic F.C. Player Evaluation Task", "h1")

    # Description
    styled(
        """
        Welcome. This application is designed to support player value identification by 
        assessing on-field performance metrics alongside key contextual factors 
        to profile players by position.
        """,
        "p"
    )

    styled("Let's Get Started…", "h3")



def render_gks():

    # Section title
    styled("GOALKEEPERS", "h3", color=ORANGE, border=True)

    # Description
    styled(
        """
        We begin with the goalkeepers. Using your selected priorities for shot-stopping, 
        distribution, and sweeping actions, the model highlights the one goalkeeper who 
        most closely matches your desired profile.
        """,
        "p"
    )

    # Playstyle Preferences
    styled("Select Playstyle Preferences...", "h4")

    scale = [
        "Very Low", "Low", "Slightly Low", "Balanced",
        "Slightly High", "High", "Very High"
    ]

    styled("The Shot Stopper", "h5")
    st.select_slider("Shot Priority", options=scale, value="Balanced", key="shot")

    styled("The Distributor", "h5")
    st.select_slider("Distribution Priority", options=scale, value="Balanced", key="dist")

    styled("The Sweeper", "h5")
    st.select_slider("Sweeper Priority", options=scale, value="Balanced", key="sweep")

    # ====================================================
    # PROPER BUTTON: Visual HTML button + Hidden trigger
    # ====================================================

    # Beautiful centered HTML button (visual only)
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin-top:45px;">
            <button id="find-player-btn" style="
                background-color:#113825;
                color:white;
                border:2px solid white;
                padding:22px 60px;
                font-size:24px;
                font-family:'Belleza', sans-serif;
                border-radius:12px;
                cursor:pointer;
            ">
                Find Player
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Hidden Streamlit button (real Python trigger)
    clicked = st.button(" ", key="find_gk_hidden")

    # ====================================================
    # When clicked → Calculate weights (Print to terminal ONLY)
    # ====================================================

    if clicked:
        shot_label  = st.session_state["shot"]
        dist_label  = st.session_state["dist"]
        sweep_label = st.session_state["sweep"]

        # Calculate & print to terminal only
        ss_w, d_w, sw_w = calculate_gk_weights(shot_label, dist_label, sweep_label)

        # Do NOT show anything in the app
        # Only printed in terminal via calculate_gk_weights()
        pass


# ================================================================
#                             RUN PAGE
# ================================================================

intro_section()
render_gks()
