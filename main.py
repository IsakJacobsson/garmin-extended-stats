import streamlit as st

from filters import filter_activities
from load_data import load_data
from metrics import (
    aggregate_metric_over_time,
    convert_time_column_to_hours,
    get_activities,
    get_summable_metrics,
)


def get_user_data_section():
    csv_file = st.file_uploader("Upload Garmin CSV file", type="csv")

    if csv_file is None:
        return None

    return load_data(csv_file)


def activity_metrics_over_time_section(df):
    df = df.copy()
    st.header("Activity metrics over time")

    start_date = df["Datum"].min()
    end_date = df["Datum"].max()

    col1, col2 = st.columns(2)

    with col1:
        activities = get_activities(df)
        selected_activities = multiselect(activities, "Activity type")

    df = filter_activities(df, selected_activities)

    with col2:
        valid_metrics = get_summable_metrics(df)
        selected_metric = selectbox(valid_metrics, "Metric")

    df = convert_time_column_to_hours(df)

    if len(selected_activities) == 0:
        st.warning("Please select at least one activity type.")
        return

    # Create tabs for different resolutions
    tab_day, tab_week, tab_month, tab_year = st.tabs(["Day", "Week", "Month", "Year"])

    # Plot each tab
    plot_metric_tab(df, selected_metric, "D", "%Y-%m-%d", tab_day, start_date, end_date)
    plot_metric_tab(df, selected_metric, "W", "%Y-%W", tab_week, start_date, end_date)
    plot_metric_tab(df, selected_metric, "M", "%Y-%m", tab_month, start_date, end_date)
    plot_metric_tab(df, selected_metric, "Y", "%Y", tab_year, start_date, end_date)


def multiselect(choices, description):
    default = choices[0] if len(choices) > 0 else None
    selected_activities = st.multiselect(
        description,
        choices,
        default=default,
        placeholder="Select activity types",
    )
    return selected_activities


def selectbox(choices, description):
    selected_metric = st.selectbox(description, choices)
    return selected_metric


def plot_metric_tab(df, metric, freq, fmt, tab, start_date, end_date):
    agg_df = aggregate_metric_over_time(df, metric, freq, start_date, end_date)

    plot_df = agg_df.copy()
    plot_df.index = plot_df.index.to_timestamp(how="start")
    plot_df["PeriodStr"] = plot_df.index.strftime(fmt)

    with tab:
        st.bar_chart(plot_df.set_index("PeriodStr")[metric])


def main():
    st.title("Garmin extended data")

    df = get_user_data_section()
    if df is None:
        return

    activity_metrics_over_time_section(df)


if __name__ == "__main__":
    main()
