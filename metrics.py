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


def get_activities(df):
    return df["Aktivitetstyp"].unique()


def get_summable_metrics(df):
    valid_metrics = []
    for col in SUMMABLE_COLUMNS:
        if col in df.columns and not df[col].isna().any():
            valid_metrics.append(col)
    return valid_metrics


def aggregate_metric_over_time(df, metric, period_freq, start, end):
    df = df.copy()
    df["Period"] = df["Datum"].dt.to_period(period_freq)

    agg = df.groupby("Period")[metric].sum().sort_index()

    full_range = pd.period_range(start=start, end=end, freq=period_freq)

    return agg.reindex(full_range, fill_value=0).to_frame(metric)
