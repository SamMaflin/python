# ========================================
# pizza_components.py 
# FINAL, CLEAN, DARK THEME VERSION
# ========================================

import plotly.graph_objects as go
import streamlit.components.v1 as components


# --------------------------------------------------
# DARK CUSTOM COLOR PALETTE (used for category groups)
# --------------------------------------------------
DARK_PALETTE = [
    "#CA60CA",   # deep purple
    "#FF5656",   # dark magenta
    "#3FB19C",   # deep teal
    "#70B274",   # deep burnt orange
    "#435663",   # navy blue
    "#1D7B71",   # forest green
]



# --------------------------------------------------
# CATEGORY HEADER (e.g. Shot Stopping | Distribution | Sweeper)
# --------------------------------------------------
def render_category_header(groups):

    group_names = list(groups.keys())

    group_colors = {
        g: DARK_PALETTE[i % len(DARK_PALETTE)]
        for i, g in enumerate(group_names)
    }

    html = "<div style='text-align:center; margin-bottom:10px; margin-top:5px;'>"

    for i, g in enumerate(group_names):

        html += f"""
        <span style="
            font-size:26px;
            font-weight:700;
            letter-spacing:-1px;
            color:{group_colors[g]};
            margin:0 18px;
            font-family:'Roboto', sans-serif;
        ">{g}</span>
        """

        if i < len(group_names) - 1:
            html += "<span style='color:white; font-size:28px;'>|</span>"

    html += "</div>"

    components.html(html, height=80, scrolling=False)



# --------------------------------------------------
# METRIC ID KEY (horizontal, dark circles)
# --------------------------------------------------
def render_id_key(groups, id_color="#111111"):

    all_metrics = []
    for g, metrics in groups.items():
        all_metrics.extend(metrics)

    rows_html = """
    <div style="
        width:100%;
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        gap:8px;
        margin-top:10px;
        font-family:'Roboto', sans-serif;
    ">
    """

    for idx, metric in enumerate(all_metrics, start=1):

        rows_html += f"""
        <div style="
            display:flex;
            align-items:center;
            background:rgba(255,255,255,0.12);
            padding:4px 8px;
            border-radius:6px;
        ">

            <span style="
                width:16px;
                height:16px;
                display:inline-flex;
                align-items:center;
                justify-content:center;
                background:{id_color};
                color:white;
                border-radius:50%;
                font-size:11px;
                border:1px solid white;
                margin-right:6px;
                font-family:'Roboto', sans-serif;
            ">{idx}</span>

            <span style="
                font-size:12px;
                color:white;
                font-family:'Roboto', sans-serif;
            ">{metric}</span>

        </div>
        """

    rows_html += "</div>"

    components.html(rows_html, height=200, scrolling=False)




# --------------------------------------------------
# PIZZA RADAR PLOT (modern dark theme)
# --------------------------------------------------
def pizza_plot_combined(row, df, groups, invert):

    # Visual sizing
    BADGE_OFFSET = 1
    BADGE_SIZE = 30

    ID_SIZE = 26        # ⬅⬅⬅ larger black circles
    ID_FONT = 13        # ⬅⬅⬅ larger text inside black circles

    STAT_COLOR = "#FF5500"
    ID_COLOR = "#111111"
    LINE_COLOR = STAT_COLOR
    LINE_WIDTH = 2
    LINE_DASH = "dot"

    PIZZA_SCALE = 1

    # Build metric lists
    all_metrics = []
    metric_colors = []

    for i, (g, metrics) in enumerate(groups.items()):
        color = DARK_PALETTE[i % len(DARK_PALETTE)]
        for m in metrics:
            all_metrics.append(m)
            metric_colors.append(color)

    metric_ids = list(range(1, len(all_metrics) + 1))

    # Percentiles
    values = []
    for m in all_metrics:

        if m not in df.columns:
            values.append(50)
            continue

        pct = df[m].rank(pct=True) * 100
        v = pct.loc[row.name]

        if m in invert:
            v = 100 - v

        values.append(v)

    scaled_values = [v * PIZZA_SCALE for v in values]

    fig = go.Figure()
    n = len(all_metrics)
    angle = 360 / n
    theta_vals = [(i * angle) + angle/2 for i in range(n)]

    # -------------------------------------------
    # 1) Radar wedges
    # -------------------------------------------
    for i, (sv, color) in enumerate(zip(scaled_values, metric_colors)):
        fig.add_trace(go.Barpolar(
            r=[sv],
            theta=[theta_vals[i]],
            width=[angle],
            marker=dict(color=color, line=dict(color="white", width=2)),
            opacity=0.80,
            showlegend=False
        ))

    # -------------------------------------------
    # 2) Circle radii
    # -------------------------------------------
    stat_r = [(v * PIZZA_SCALE) + BADGE_OFFSET for v in values]

    MAX_R = max(stat_r) + 30       # fixed outer ring
    id_r = [MAX_R] * n

    # -------------------------------------------
    # 3) Dotted line between stat circle → ID circle
    # -------------------------------------------
    for i in range(n):
        fig.add_trace(go.Scatterpolar(
            r=[stat_r[i], id_r[i]],
            theta=[theta_vals[i], theta_vals[i]],
            mode="lines",
            line=dict(color="white", width=LINE_WIDTH, dash=LINE_DASH),
            hoverinfo="skip",
            showlegend=False
        ))

    # -------------------------------------------
    # 4) Orange stat circles
    # -------------------------------------------
    fig.add_trace(go.Scatterpolar(
        r=stat_r,
        theta=theta_vals,
        mode="markers+text",
        marker=dict(size=BADGE_SIZE, color=STAT_COLOR, line=dict(color="black", width=2)),
        text=[str(int(v)) for v in values],
        textfont=dict(color="white", size=13, family="Roboto"),
        hoverinfo="skip",
        showlegend=False
    ))

    # -------------------------------------------
    # 5) Larger Black ID circles
    # -------------------------------------------
    fig.add_trace(go.Scatterpolar(
        r=id_r,
        theta=theta_vals,
        mode="markers+text",
        marker=dict(
            size=ID_SIZE,
            color=ID_COLOR,
            symbol="circle",
            line=dict(color="white", width=1),
        ),
        text=[str(i) for i in metric_ids],
        textfont=dict(color="white", size=ID_FONT, family="Roboto"),
        hoverinfo="skip",
        showlegend=False
    ))

    # Layout
    fig.update_layout(
        autosize=True,
        height=780,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False),
            angularaxis=dict(visible=False)
        )
    )

    return fig
