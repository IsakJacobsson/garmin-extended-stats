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


def aggregate_metric_over_time(df, metric, period_freq, start, end):
    df = df.copy()
    df["Period"] = df["Datum"].dt.to_period(period_freq)

    agg = df.groupby("Period")[metric].sum().sort_index()

    full_range = pd.period_range(start=start, end=end, freq=period_freq)

    return agg.reindex(full_range, fill_value=0).to_frame(metric)


def get_activities(df):
    return df["Aktivitetstyp"].unique()


def get_summable_metrics(df):
    valid_metrics = []
    for col in SUMMABLE_COLUMNS:
        if col in df.columns and not df[col].isna().any():
            valid_metrics.append(col)
    return valid_metrics


def insert_rest_days(df, start_date, end_date):
    df = df.copy()

    # Ensure 'Datum' is datetime
    df["Datum"] = pd.to_datetime(df["Datum"])

    # Normalize to just dates for comparison
    df["Day"] = df["Datum"].dt.normalize()

    # Extract just the date part for comparison
    df["DateOnly"] = df["Datum"].dt.date

    # Full date range
    all_days = pd.date_range(start=start_date, end=end_date, freq="D").date

    # Days that already have any activity
    active_days = set(df["DateOnly"].unique())

    # Days with no activity
    rest_days = [d for d in all_days if d not in active_days]

    # Create "Rest day" rows with midnight timestamps
    rest_df = pd.DataFrame(
        {
            "Aktivitetstyp": "Rest day",
            "Datum": pd.to_datetime(
                rest_days
            ),  # convert back to Timestamps at midnight
            "Namn": "Rest day",
            "Rest count": 1,
        }
    )

    # Combine and sort
    df_with_rest = pd.concat([df, rest_df], ignore_index=True)
    df_with_rest = df_with_rest.sort_values("Datum").reset_index(drop=True)

    # Drop helper column
    df_with_rest = df_with_rest.drop(columns=["DateOnly"])

    return df_with_rest
