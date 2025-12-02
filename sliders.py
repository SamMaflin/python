# ========================
# sliders.py
# ========================

import streamlit as st

SCALE = [
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


def render_sliders(slider_definition, section_name):
    """
    slider_definition = list of tuples:
        [("Shot Stopping", "shot_stop"), ("Distribution", "dist"), ...]
    """

    slider_values = {}

    for label, key in slider_definition:
        st.markdown(
            f"""
            <div class="slider-block">
                <div class="slider-label">{label}</div>
                <div class="slider-sublabel">(Priority Level)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        slider_values[key] = st.select_slider(
            "",
            options=SCALE,
            value="Balanced",
            key=f"{section_name}_{key}"
        )

    # Convert UI values → Multipliers
    multipliers = {k: MULT[v] for k, v in slider_values.items()}
    return multipliers
