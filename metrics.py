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


def get_valid_metrics(df):
    valid_metrics = []
    for col in SUMMABLE_COLUMNS:
        if col in df.columns and not df[col].isna().any():
            valid_metrics.append(col)
    return valid_metrics


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
