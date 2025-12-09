# ============================================================
# test.py — Customer Insight Metric Engine + Distribution Explorer
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# DATA LOADING
# ============================================================
def load_helpforheroes_data(file_path):
    """
    Load Excel file with People_Data and Bookings_Data sheets.
    """
    xls = pd.ExcelFile(file_path)
    data = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}

    data['People_Data'] = pd.DataFrame(data.get('People_Data', pd.DataFrame()))
    data['Bookings_Data'] = pd.DataFrame(data.get('Bookings_Data', pd.DataFrame()))

    return data


# ============================================================
# METRIC ENGINE
# ============================================================
def calculate_customer_value_metrics(people_df, bookings_df, priority_sources=None):

    # Merge datasets
    merged_df = pd.merge(people_df, bookings_df, on='Person URN', how='left')

    # Ensure booking amount exists
    if 'BookingAmount' not in merged_df.columns and 'Cost' in merged_df.columns:
        merged_df['BookingAmount'] = merged_df['Cost']
    merged_df['BookingAmount'] = merged_df['BookingAmount'].fillna(0)

    # -------------------------------
    # ECONOMIC (SPEND) VALUE
    # -------------------------------
    economic_metrics = merged_df.groupby('Person URN').agg(
        TotalBookingAmount=('BookingAmount', 'sum'),
        AverageBookingAmount=('BookingAmount', 'mean'),
        MaximumBookingAmount=('BookingAmount', 'max')
    )

    # -------------------------------
    # BEHAVIOURAL (ACTIVITY) VALUE
    # -------------------------------
    bookings_df['Booking Date'] = pd.to_datetime(bookings_df['Booking Date'], errors='coerce')
    reference_date = bookings_df['Booking Date'].max()

    def simpson_diversity(destinations):
        counts = destinations.value_counts()
        if counts.sum() == 0:
            return 0.0
        p = counts / counts.sum()
        return 1 - np.sum(p**2)

    behavioural_metrics = bookings_df.groupby('Person URN').agg(
        BookingFrequency=('Booking URN', 'count'),
        DestinationDiversityIndex=('Destination', simpson_diversity),
        LastBookingDate=('Booking Date', 'max')
    )

    behavioural_metrics['RecencyDays'] = (reference_date - behavioural_metrics['LastBookingDate']).dt.days
    behavioural_metrics = behavioural_metrics.drop(columns=['LastBookingDate'])

    behavioural_metrics = behavioural_metrics.fillna({
        'BookingFrequency': 0,
        'DestinationDiversityIndex': 0,
        'RecencyDays': np.nan
    })

    # -------------------------------
    # STRATEGIC (ALIGNMENT) VALUE
    # -------------------------------
    long_haul_destinations = [
        'United States', 'USA', 'Australia', 'New Zealand',
        'South Africa', 'Namibia', 'Senegal', 'Mali', 'Kuwait'
    ]

    strategic_temp = bookings_df.groupby('Person URN').agg(
        LongHaulBookings=('Destination', lambda x: np.sum(x.isin(long_haul_destinations))),
        PackageBookings=('Product', lambda x: np.sum(x == 'Package Holiday'))
    )

    strategic_metrics = pd.DataFrame(index=strategic_temp.index)
    strategic_metrics['LongHaulAlignment'] = (strategic_temp['LongHaulBookings'] > 0).astype(int)
    strategic_metrics['PackageAlignment'] = (strategic_temp['PackageBookings'] > 0).astype(int)

    # Channel Fit
    if priority_sources is None:
        priority_sources = ['Expedia']

    # Add channel fit from People table
    people_df['ChannelFit'] = people_df['Source'].apply(
        lambda x: 1 if x in priority_sources else 0
    )

    strategic_metrics = strategic_metrics.merge(
        people_df[['Person URN', 'ChannelFit']],
        on='Person URN',
        how='left'
    )

    # -------------------------------
    # COMBINE ALL METRICS
    # -------------------------------
    combined = (
        economic_metrics
        .merge(behavioural_metrics, left_index=True, right_index=True, how='left')
        .merge(strategic_metrics.set_index('Person URN'), left_index=True, right_index=True, how='left')
    )

    return combined


# ============================================================
# DISTRIBUTION PLOTTING FUNCTION
# ============================================================
sns.set(style="whitegrid")

def plot_metric_distributions(df, metrics=None, bins=30, log_scale=False):
    """
    Plot histograms for selected metrics.
    Runs outside Streamlit.
    """
    if metrics is None:
        metrics = df.select_dtypes(include=[np.number]).columns.tolist()

    n = len(metrics)
    rows = (n + 1) // 2

    plt.figure(figsize=(16, rows * 5))

    for i, col in enumerate(metrics, 1):
        plt.subplot(rows, 2, i)

        data = df[col].dropna()

        if log_scale:
            data = np.log1p(data)

        sns.histplot(data, bins=bins, kde=False, color="#4682B4")

        title = f"Distribution of {col}"
        if log_scale:
            title += " (log)"
        plt.title(title, fontsize=14, weight="bold")

        plt.xlabel(col)
        plt.ylabel("Count")

        stats = df[col].describe()
        stat_text = (
            f"min: {stats['min']:.1f}\n"
            f"25%: {stats['25%']:.1f}\n"
            f"50%: {stats['50%']:.1f}\n"
            f"75%: {stats['75%']:.1f}\n"
            f"max: {stats['max']:.1f}"
        )

        plt.gca().text(
            0.95, 0.95, stat_text,
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(facecolor="white", alpha=0.7)
        )

    plt.tight_layout()
    plt.show()


# ============================================================
# MAIN EXECUTION (python test.py)
# ============================================================
if __name__ == "__main__":
    print("\n=== Help for Heroes Customer Metrics — Running Offline Analysis ===\n")

    # ----------------------------------------------------------
    # UPDATED FILE PATH
    # ----------------------------------------------------------
    file_path = "helpforheroes/helpforheroes.xls"

    print(f"Loading data from: {file_path} ...")
    data = load_helpforheroes_data(file_path)

    people_df = data['People_Data']
    bookings_df = data['Bookings_Data']

    print("Calculating customer metrics...")
    combined = calculate_customer_value_metrics(people_df, bookings_df)

    print("\nPreview of Combined Metrics:")
    print(combined.head())

    # Metrics to plot
    metrics_to_plot = [
        'TotalBookingAmount',
        'AverageBookingAmount',
        'MaximumBookingAmount',
        'BookingFrequency',
        'DestinationDiversityIndex',
        'RecencyDays',
        'LongHaulAlignment',
        'PackageAlignment',
        'ChannelFit'
    ]

    print("\nPlotting raw distributions...")
    plot_metric_distributions(combined, metrics=metrics_to_plot, log_scale=False)

    print("\nPlotting log-transformed distributions...")
    plot_metric_distributions(combined, metrics=metrics_to_plot, log_scale=True)

    print("\n=== Analysis Complete ===\n")
