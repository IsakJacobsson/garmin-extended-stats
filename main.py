import pandas as pd
import streamlit as st

from load_data import load_data

SUMMABLE_COLUMNS = [
    "Distans",
    "Tid",
    "Total stigning",
    "Steg",
    "Kalorier",
    "Aerobisk Training Effect",
    "Total stigning",
    "Totalt nedför",
    "Totalt antal årtag",
    "Totalt antal repetitioner",
    "Totalt antal set",
]


def activity_metrics_over_time_section(df):
    st.header("Activity metrics over time")

    col1, col2 = st.columns(2)

    with col1:
        selected_activities = activity_multiselector(df)

    activity_df = filter_activities(df, selected_activities)

    # Create tabs for different metrics
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
    plot_metric_tab(activity_df, selected_metric, "D", "%Y-%m-%d", tab_day)  # Day
    plot_metric_tab(activity_df, selected_metric, "W", "%Y-%W", tab_week)  # Week
    plot_metric_tab(activity_df, selected_metric, "M", "%Y-%m", tab_month)  # Month
    plot_metric_tab(activity_df, selected_metric, "Y", "%Y", tab_year)  # Year


def activity_multiselector(df):
    activities = df["Aktivitetstyp"].unique()
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


def get_valid_metrics(df):
    valid_metrics = []
    for col in SUMMABLE_COLUMNS:
        if not df[col].isna().any():
            valid_metrics.append(col)
    return valid_metrics


def convert_time_column_to_hours(df):
    df = df.copy()
    if "Tid" in df.columns:
        df["Tid"] = df["Tid"].dt.total_seconds() / 3600
    return df


def plot_metric_tab(df, metric, freq, fmt, tab):
    agg_df = aggregate_metric_over_time(df, metric, freq)

    plot_df = agg_df.copy()
    plot_df.index = plot_df.index.to_timestamp(how="start")
    plot_df["PeriodStr"] = plot_df.index.strftime(fmt)

    with tab:
        st.bar_chart(plot_df.set_index("PeriodStr")[metric])


def aggregate_metric_over_time(df, metric, period_freq, end_period=None):
    df = df.copy()
    df["Period"] = df["Datum"].dt.to_period(period_freq)

    agg = df.groupby("Period")[metric].sum().sort_index()

    if end_period is None:
        end_period = pd.Timestamp.today().to_period(period_freq)

    full_range = pd.period_range(
        start=agg.index.min(),
        end=end_period,
        freq=period_freq,
    )

    return agg.reindex(full_range, fill_value=0).to_frame(metric)


def main():
    st.title("Garmin extended data")

    csv_file = st.file_uploader("Upload Garmin CSV file", type="csv")

    if csv_file is not None:
        df = load_data(csv_file)
        activity_metrics_over_time_section(df)


if __name__ == "__main__":
    main()
