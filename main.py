import pandas as pd
import streamlit as st

from load_data import load_data
from metrics import aggregate_metric_over_time, get_activities, get_valid_metrics


def activity_metrics_over_time_section(df):
    st.header("Activity metrics over time")

    start_date = df["Datum"].min()
    end_date = df["Datum"].max()

    col1, col2 = st.columns(2)

    with col1:
        activities = get_activities(df)
        selected_activities = activity_multiselector(df, activities)

    activity_df = filter_activities(df, selected_activities)

    with col2:
        valid_metrics = get_valid_metrics(activity_df)
        selected_metric = metric_selector(valid_metrics)

    activity_df = convert_time_column_to_hours(activity_df)

    if len(selected_activities) == 0:
        st.warning("Please select at least one activity type.")
        return

    # Create tabs for different resolutions
    tab_day, tab_week, tab_month, tab_year = st.tabs(["Day", "Week", "Month", "Year"])

    # Plot each tab
    plot_metric_tab(
        activity_df, selected_metric, "D", "%Y-%m-%d", tab_day, start_date, end_date
    )  # Day
    plot_metric_tab(
        activity_df, selected_metric, "W", "%Y-%W", tab_week, start_date, end_date
    )  # Week
    plot_metric_tab(
        activity_df, selected_metric, "M", "%Y-%m", tab_month, start_date, end_date
    )  # Month
    plot_metric_tab(
        activity_df, selected_metric, "Y", "%Y", tab_year, start_date, end_date
    )  # Year


def activity_multiselector(df, activities):
    selected_activities = st.multiselect(
        "Activity type",
        activities,
        default=activities[0] if len(activities) > 0 else None,
        placeholder="Select activity types",
    )
    return selected_activities


def metric_selector(metrics):
    selected_metric = st.selectbox("Metric", metrics)
    return selected_metric


def filter_activities(df, activities):
    df = df[df["Aktivitetstyp"].isin(activities)].copy()
    return df


def convert_time_column_to_hours(df):
    df = df.copy()
    if "Tid" in df.columns:
        df["Tid"] = df["Tid"].dt.total_seconds() / 3600
    return df


def plot_metric_tab(df, metric, freq, fmt, tab, start_date, end_date):
    agg_df = aggregate_metric_over_time(df, metric, freq, start_date, end_date)

    plot_df = agg_df.copy()
    plot_df.index = plot_df.index.to_timestamp(how="start")
    plot_df["PeriodStr"] = plot_df.index.strftime(fmt)

    with tab:
        st.bar_chart(plot_df.set_index("PeriodStr")[metric])


def main():
    st.title("Garmin extended data")

    csv_file = st.file_uploader("Upload Garmin CSV file", type="csv")

    if csv_file is not None:
        df = load_data(csv_file)
        activity_metrics_over_time_section(df)


if __name__ == "__main__":
    main()
