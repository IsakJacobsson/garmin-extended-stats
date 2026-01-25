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
    st.header("Activity metrics over time")

    # This has to be done before filtering the df, since the full period is
    # desired regardless of which activities are selected
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
    tab_info = [
        ("Day", "D", "%Y-%m-%d"),
        ("Week", "W", "%Y-%W"),
        ("Month", "M", "%Y-%m"),
        ("Year", "Y", "%Y"),
    ]

    tabs = st.tabs([label for label, _, _ in tab_info])

    for tab, (_, freq, date_format) in zip(tabs, tab_info):
        agg_df = aggregate_metric_over_time(
            df, selected_metric, freq, start_date, end_date
        )
        with tab:
            plot_metric(agg_df, selected_metric, date_format)


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


def plot_metric(df, metric, fmt):
    df = df.copy()
    df.index = df.index.to_timestamp(how="start")
    df["PeriodStr"] = df.index.strftime(fmt)

    st.bar_chart(df.set_index("PeriodStr")[metric])


def main():
    st.title("Garmin extended data")

    df = get_user_data_section()
    if df is None:
        return

    activity_metrics_over_time_section(df)


if __name__ == "__main__":
    main()
