import pandas as pd
import streamlit as st

from load_data import load_data


def activity_metrics_over_time_section(df):
    st.header("Activity Metrics Over Time")

    col1, col2 = st.columns(2)

    with col1:
        activities = ["Löpning", "Cykling"]
        activity = st.pills("Activity", activities, default=activities[0])

    # Filter for activity
    activity_df = df[df["Aktivitetstyp"] == activity].copy()
    activity_df["Datum"] = pd.to_datetime(activity_df["Datum"])

    # Create tabs for different metrics
    with col2:
        metrics = ["Distans", "Tid", "Total stigning"]
        metric = st.pills("Metric", metrics, default=metrics[0])

    activity_df["Tid"] = activity_df["Tid"].dt.total_seconds() / 60  # minutes

    # Create tabs for different resolutions
    tab_day, tab_week, tab_month, tab_year = st.tabs(["Day", "Week", "Month", "Year"])

    def plot_metric(period_freq, fmt, tab_label):
        temp_df = activity_df.copy()

        # Convert to Period (do NOT convert to start_time yet)
        temp_df["Period"] = temp_df["Datum"].dt.to_period(period_freq)

        # Aggregate with PeriodIndex
        agg_df = temp_df.groupby("Period")[metric].sum().sort_index()

        # Create full period range (including missing periods)
        full_range = pd.period_range(
            start=agg_df.index.min(),
            end=pd.Timestamp.today().to_period(period_freq),
            freq=period_freq,
        )

        # Reindex to include missing periods
        agg_df = agg_df.reindex(full_range, fill_value=0)

        # Convert to timestamps just for plotting / labels
        plot_df = agg_df.to_timestamp(how="start").to_frame(name=metric)
        plot_df["PeriodStr"] = plot_df.index.strftime(fmt)

        with tab_label:
            st.bar_chart(plot_df.set_index("PeriodStr")[metric])

    # Plot each tab
    plot_metric("D", "%Y-%m-%d", tab_day)  # Day
    plot_metric("W", "%Y-%W", tab_week)  # Week
    plot_metric("M", "%Y-%m", tab_month)  # Month
    plot_metric("Y", "%Y", tab_year)  # Year


def main():
    st.title("Garmin extended data")

    csv_file = st.file_uploader("Upload Garmin CSV file", type="csv")

    if csv_file is not None:
        df = load_data(csv_file)
        activity_metrics_over_time_section(df)


if __name__ == "__main__":
    main()
