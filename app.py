import pandas as pd
import streamlit as st

from filters import filter_activities
from load_data import load_data
from metrics import (
    aggregate_over_time,
    convert_time_column_to_hours,
    get_activities,
    get_days_without_activity,
    get_summable_metrics,
    select_metric_and_drop_zeros,
)

tab_info = [
    ("Day", "D", "%Y-%m-%d"),
    ("Week", "W", "%Y-%W"),
    ("Month", "ME", "%Y-%m"),
    ("Year", "YE", "%Y"),
]


def get_user_data_section():
    csv_file = st.file_uploader("Upload Garmin CSV file", type="csv")

    if csv_file is None:
        return None

    return load_data(csv_file)


def activity_metrics_over_time_section(df):
    st.header("Activity metrics over time")

    col1, col2 = st.columns(2)

    with col1:
        activities = get_activities(df)
        selected_activities = multiselect(activities, "Activity type")

    if len(selected_activities) == 0:
        st.warning("Please select at least one activity type.")
        return

    df = filter_activities(df, selected_activities)

    with col2:
        valid_metrics = get_summable_metrics(df)
        selected_metric = selectbox(valid_metrics, "Metric")

    df = convert_time_column_to_hours(df)
    df = select_metric_and_drop_zeros(df, selected_metric)

    # Create tabs for different resolutions
    tabs = st.tabs([label for label, _, _ in tab_info])

    for tab, (_, freq, date_format) in zip(tabs, tab_info):
        agg_df = aggregate_over_time(df, freq)
        with tab:
            plot_metric(agg_df, date_format)


def multiselect(choices, description):
    default = choices[0] if len(choices) > 0 else None
    selected = st.multiselect(
        description,
        choices,
        default=default,
        placeholder="Select activity types",
    )
    return selected


def selectbox(choices, description):
    selected = st.selectbox(description, choices)
    return selected


def plot_metric(df, fmt):
    df = df.copy()
    df.index = df.index.strftime(fmt)

    st.bar_chart(df)


def rest_day_stats_section(df):
    st.header("Rest day stats")

    # This has to be done before filtering the df, since the full period is
    # desired regardless of which activities are selected
    start_date = df.index.min()
    end_date = df.index.max()

    activities = get_activities(df)
    active_activities = st.pills(
        "Active day activity types",
        activities,
        selection_mode="multi",
        default=activities,
    )

    df = filter_activities(df, active_activities)

    rest_days = get_days_without_activity(df)

    rest_days_df = pd.DataFrame({"Rest days": 1}, index=rest_days)

    # Create tabs for different resolutions
    tabs = st.tabs([label for label, _, _ in tab_info])
    for tab, (_, freq, date_format) in zip(tabs, tab_info):
        agg_df = aggregate_over_time(rest_days_df, freq, start_date, end_date)
        with tab:
            plot_metric(agg_df, date_format)


def main():
    st.title("Garmin extended data")

    df = get_user_data_section()
    if df is None:
        return

    activity_metrics_over_time_section(df)

    rest_day_stats_section(df)


if __name__ == "__main__":
    main()
