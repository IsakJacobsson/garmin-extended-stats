import pandas as pd

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


def convert_time_column_to_hours(df):
    df = df.copy()
    if "Tid" in df.columns:
        df["Tid"] = df["Tid"].dt.total_seconds() / 3600
    return df


def aggregate_metric_over_time(df, metric, freq, start, end):
    start = start.normalize()
    end = end.normalize()

    # Need to fix end date for years for some reason...
    if freq == "YE":
        end = end + pd.offsets.YearEnd(0)

    out = (
        df[metric]
        .resample(freq)
        .sum()
        .reindex(pd.date_range(start, end, freq=freq))
        .fillna(0)
        .to_frame(metric)
    )

    return out


def get_activities(df):
    return df["Aktivitetstyp"].unique()


def get_days_without_activity(df, start_date, end_date):
    activity_days = df.index.normalize()
    start_date = start_date.normalize()
    end_date = end_date.normalize()

    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    days_without_activity = all_days.difference(activity_days)

    return days_without_activity


def get_summable_metrics(df):
    valid_metrics = []
    for col in SUMMABLE_COLUMNS:
        if col in df.columns and not df[col].isna().any():
            valid_metrics.append(col)
    return valid_metrics
