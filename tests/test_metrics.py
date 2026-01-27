import numpy as np
import pandas as pd
import pytest

from metrics import (
    aggregate_metric_over_time,
    convert_time_column_to_hours,
    get_activities,
    get_days_without_activity,
    get_summable_metrics,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Datum": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-08"]),
            "Distans": [5.0, 3.0, 10.0],
            "Tid": [30, 20, 60],
            "Kalorier": [300, 200, 600],
            "Steg": [None, 4000, 8000],  # contains NaN
        }
    )


def test_convert_time_column_to_hours_converts_correctly():
    df = pd.DataFrame(
        {
            "Tid": pd.to_timedelta([3600, 5400], unit="s"),
        }
    )

    result = convert_time_column_to_hours(df)

    assert result["Tid"].tolist() == [1.0, 1.5]


def test_convert_time_column_to_hours_no_tid_column():
    df = pd.DataFrame(
        {
            "Distans": [5, 10],
        }
    )

    result = convert_time_column_to_hours(df)

    assert result.equals(df)


def test_convert_time_column_to_hours_outputs_float():
    df = pd.DataFrame(
        {
            "Tid": pd.to_timedelta([3600], unit="s"),
        }
    )

    result = convert_time_column_to_hours(df)

    assert result["Tid"].dtype == "float64"


def test_aggregate_metric_over_time_weekly(sample_df):
    result = aggregate_metric_over_time(
        df=sample_df,
        metric="Distans",
        period_freq="W",
        start=pd.Timestamp("2024-01-01"),
        end=pd.Timestamp("2024-01-18"),
    )

    print(result)

    # Expect 3 weeks in range
    assert len(result) == 3

    # Week 1: Jan 1 + Jan 2
    assert result.iloc[0]["Distans"] == 8.0

    # Week 2: Jan 8
    assert result.iloc[1]["Distans"] == 10.0

    # Week 3: no data → filled with 0
    assert result.iloc[2]["Distans"] == 0


def test_aggregate_metric_over_time_daily(sample_df):
    result = aggregate_metric_over_time(
        df=sample_df,
        metric="Tid",
        period_freq="D",
        start=pd.Timestamp("2024-01-01"),
        end=pd.Timestamp("2024-01-03"),
    )

    assert result.loc[pd.Period("2024-01-01", freq="D"), "Tid"] == 30
    assert result.loc[pd.Period("2024-01-02", freq="D"), "Tid"] == 20

    # Missing date → zero-filled
    assert result.loc[pd.Period("2024-01-03", freq="D"), "Tid"] == 0


def test_aggregate_metric_over_time_does_not_modify_original_df(sample_df):
    _ = aggregate_metric_over_time(
        df=sample_df,
        metric="Distans",
        period_freq="W",
        start=pd.Timestamp("2024-01-01"),
        end=pd.Timestamp("2024-01-14"),
    )

    assert "Period" not in sample_df.columns


def test_get_activites():
    df = pd.DataFrame({"Aktivitetstyp": ["Löpning", "Cycling", "Styrketräning"]})

    activities = get_activities(df)

    assert set(activities) == {"Löpning", "Cycling", "Styrketräning"}


def test_days_without_activity_basic():
    df = pd.DataFrame(
        {
            "Activity": ["A", "B", "C"],
            "Datum": [
                "2023-12-30 18:05:42",
                "2024-01-03 01:33:12",
                "2024-01-06 23:23:23",
            ],
        }
    )

    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    start_date = df["Datum"].min()
    end_date = df["Datum"].max()

    result = get_days_without_activity(df, start_date, end_date)

    expected = pd.DatetimeIndex(
        [
            pd.Timestamp("2023-12-31"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-04"),
            pd.Timestamp("2024-01-05"),
        ]
    )

    assert result.equals(expected)


def test_days_without_activity_no_gaps():
    df = pd.DataFrame(
        {
            "Activity": ["A", "B", "C"],
            "Datum": [
                "2023-12-31 18:05:42",
                "2024-01-01 01:33:12",
                "2024-01-02 23:23:23",
            ],
        }
    )

    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    start_date = df["Datum"].min()
    end_date = df["Datum"].max()

    result = get_days_without_activity(df, start_date, end_date)

    expected = pd.DatetimeIndex([])

    assert result.equals(expected)


def test_get_summable_metrics_excludes_columns_with_nan(sample_df):
    summable = get_summable_metrics(sample_df)

    assert "Distans" in summable
    assert "Tid" in summable
    assert "Kalorier" in summable

    # Has NaN → should be excluded
    assert "Steg" not in summable


def test_get_summable_metrics_ignores_missing_columns(sample_df):
    summable = get_summable_metrics(sample_df)

    # Column does not exist in df
    assert "Total stigning" not in summable


def test_get_summable_metrics_empty_dataframe():
    df = pd.DataFrame()

    summable = get_summable_metrics(df)

    assert summable == []
