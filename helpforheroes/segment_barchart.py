# segment_barchart.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# ============================================================
# SEGMENT BAR CHART FUNCTION (Updated for new segmentation)
# ============================================================
def segment_barchart_plot(df, bookings_df):
    """
    Creates a Streamlit horizontal grouped bar chart comparing:
        • Customer Share (%) per new segment
        • Revenue Share (%) per new segment

    Works with the updated segmentation model:
        Spend  → Saver, Economy, Premium
        Engage → One-Timers, Casuals, Explorers
    """

    # ------------------------------------------------------------
    # CUSTOMER DISTRIBUTION
    # ------------------------------------------------------------
    segment_counts = (
        df["Segment"]
        .value_counts()
        .rename_axis("Segment")
        .reset_index(name="CustomerCount")
    )

    total_customers = df["Person URN"].nunique()
    segment_counts["ShareOfBase"] = (
        segment_counts["CustomerCount"] / total_customers * 100
    ).round(1)


    # ------------------------------------------------------------
    # REVENUE DISTRIBUTION
    # ------------------------------------------------------------
    customer_revenue = (
        bookings_df
        .groupby("Person URN")["Cost"]
        .sum()
        .rename("TotalRevenue")
    )

    df_rev = df.merge(customer_revenue, on="Person URN", how="left")

    rev_segment = (
        df_rev.groupby("Segment")["TotalRevenue"]
        .sum()
        .rename("Revenue")
        .reset_index()
    )

    total_revenue = rev_segment["Revenue"].sum()
    rev_segment["ShareOfRevenue"] = (
        rev_segment["Revenue"] / total_revenue * 100
    ).round(1)


    # ------------------------------------------------------------
    # MERGE + ORDER SEGMENTS (ascending by revenue share)
    # ------------------------------------------------------------
    merged = segment_counts.merge(
        rev_segment[["Segment", "ShareOfRevenue"]],
        on="Segment",
        how="left"
    ).sort_values("ShareOfRevenue", ascending=True)

    segments      = merged["Segment"].tolist()
    customer_vals = merged["ShareOfBase"].tolist()
    revenue_vals  = merged["ShareOfRevenue"].tolist()


    # ------------------------------------------------------------
    # BUILD THE HORIZONTAL GROUPED BAR CHART
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10))

    bar_height = 0.50
    y_positions = np.arange(len(segments)) * 1.4  # spacing between segment rows


    # Colors (kept consistent with dashboard)
    COLOR_CUST = "#0095FF"   # Blue
    COLOR_REV  = "#FF476C"   # Red


    bars_cust = ax.barh(
        y_positions - bar_height/2,
        customer_vals,
        height=bar_height,
        color=COLOR_CUST,
        label="Customer Share (%)"
    )

    bars_rev = ax.barh(
        y_positions + bar_height/2,
        revenue_vals,
        height=bar_height,
        color=COLOR_REV,
        label="Revenue Share (%)"
    )


    # ------------------------------------------------------------
    # INSIDE LABELS (white text inside bars)
    # ------------------------------------------------------------
    def add_inside_labels(bars):
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width * 0.97,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="right",
                va="center",
                fontsize=12,
                fontweight="bold",
                color="white"
            )

    add_inside_labels(bars_cust)
    add_inside_labels(bars_rev)


    # ------------------------------------------------------------
    # Y-AXIS LABELS
    # ------------------------------------------------------------
    ax.set_yticks(y_positions)
    ax.set_yticklabels(segments, fontsize=14)


    # ------------------------------------------------------------
    # TITLE & LEGEND
    # ------------------------------------------------------------
    ax.set_title(
        "Customer vs Revenue Contribution by Segment",
        fontsize=22,
        fontweight="bold",
        pad=25
    )

    ax.legend(fontsize=13, loc="lower right")


    # ------------------------------------------------------------
    # CLEAN VISUAL — no x-axis, no spines
    # ------------------------------------------------------------
    ax.xaxis.set_visible(False)

    for spine in ax.spines.values():
        spine.set_visible(False)


    # ------------------------------------------------------------
    # RENDER IN STREAMLIT
    # ------------------------------------------------------------
    plt.tight_layout()
    st.pyplot(fig)
