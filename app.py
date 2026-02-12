import pandas as pd
import streamlit as st

from filters import filter_activities
from load_data import load_data
from metrics import (
    get_activities,
    get_days_without_activity,
    get_summable_metrics,
    select_metric_and_drop_zeros,
)
from plot import aggregation_bar_plot

tab_info = [
    ("Day", "D", "%Y-%m-%d"),
    ("Week", "W", "%Y-%W"),
    ("Month", "ME", "%Y-%m"),
    ("Year", "YE", "%Y"),
]


def get_user_data_section() -> pd.DataFrame:
    st.subheader("Upload Garmin CSV file")
    with st.expander("Don't have a CSV file yet?"):
        st.markdown(
            "If you don’t have a CSV file yet, follow the steps below to export your own activity data from Garmin Connect:\n"
            "1. Navigate to [Garmin Connect activity page](https://connect.garmin.com/app/activities).\n"
            "2. Set Garmin Connect's language to **Swedish** (the app currently only reads Swedish CSV files).\n"
            "3. Scroll to the bottom of your activity list to load **all activities**.\n"
            "4. Click **Exportera CSV** to download your file.\n"
        )
    csv_file = st.file_uploader("Garmin CSV file", type="csv")

    if csv_file is None:
        return None

    return load_data(csv_file)


def activity_metrics_over_time_section(df: pd.DataFrame) -> None:
    st.header("Activity metrics over time")

    col1, col2 = st.columns(2)

    with col1:
        activities = get_activities(df)
        selected_activities = multiselect(activities, "Activity type")

    has_selection = len(selected_activities) > 0

    with col2:
        filtered_df = filter_activities(df, selected_activities)
        valid_metrics = get_summable_metrics(filtered_df)

        selected_metric = selectbox(
            valid_metrics,
            "Metric",
        )

    if not has_selection:
        st.warning("Select at least one activity type to generate a plot.")
        return

    df = filter_activities(df, selected_activities)

    metric_data = select_metric_and_drop_zeros(df, selected_metric)

    aggregation_bar_plot(metric_data)


def multiselect(choices: list[str], description: str) -> list[str]:
    default = choices[0] if len(choices) > 0 else None
    selected = st.multiselect(
        description,
        choices,
        default=default,
        placeholder="Select activity types",
    )
    return selected


def selectbox(choices: list[str], description: str) -> str:
    return st.selectbox(description, choices)


def rest_days_section(df: pd.DataFrame):
    st.header("Rest days")

    # This has to be done before filtering the df, since the full period is
    # desired regardless of which activities are selected
    start_date = df.index.min()
    end_date = df.index.max()

    activities = get_activities(df)
    rest_activities = st.multiselect(
        "Activities to ignore when counting rest days",
        activities,
        placeholder="All activities break rest by default",
    )

    st.caption(
        "Days containing only these activities will still be counted as rest days."
    )

    rest_set = set(rest_activities)
    active_activities = [
        activity for activity in activities if activity not in rest_set
    ]

    df = filter_activities(df, active_activities)

    rest_days = get_days_without_activity(df, start_date, end_date)

    aggregation_bar_plot(rest_days, start_date, end_date)


def main():
    st.title("Garmin activity analyzer")

    df = get_user_data_section()
    if df is None:
        return

    activity_metrics_over_time_section(df)

    rest_days_section(df)


if __name__ == "__main__":
    main()
