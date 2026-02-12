import pandas as pd
import pytest

from metrics import (
    SUMMABLE_COLUMNS,
    aggregate_over_time,
    convert_time_column_to_hours,
    get_activities,
    get_days_without_activity,
    get_summable_metrics,
    select_metric_and_drop_zeros,
)


@pytest.fixture
def sample_series():
    return pd.Series(
        [5.0, 3.0, 2.0, 10.0],
        index=pd.to_datetime(
            [
                "2024-01-01 13:12:11",
                "2024-01-02 19:01:01",
                "2024-01-02 22:01:01",
                "2024-01-08 01:34:34",
            ]
        ),
    )


@pytest.fixture
def sample_df_2():
    return pd.DataFrame(
        {
            "Distans": [5.0, 3.0, 2.0, 10.0],
            "Tid": [30, 20, 30, 60],
            "Kalorier": [300, 200, 200, 600],
            "Steg": [None, 4000, 3000, 8000],  # contains NaN
            "Totalt nedför": [32, 0, 0, 44],
        },
        index=pd.to_datetime(
            [
                "2024-01-01 13:12:11",
                "2024-01-02 19:01:01",
                "2024-01-02 22:01:01",
                "2024-01-08 01:34:34",
            ]
        ),
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


def test_aggregate_over_time_weekly(sample_series):
    result = aggregate_over_time(
        s=sample_series,
        freq="W",
        start=pd.to_datetime("2024-01-01 12:12:13"),
        end=pd.to_datetime("2024-01-14 12:12:13"),
    )

    expected = pd.Series(
        [0.0, 10.0, 10.0, 0.0],
        index=pd.to_datetime(["2023-12-31", "2024-01-07", "2024-01-14", "2024-01-21"]),
    )

    assert result.equals(expected)


def test_aggregate_over_time_daily(sample_series):
    result = aggregate_over_time(
        s=sample_series,
        freq="D",
        start=pd.to_datetime("2023-12-31 12:12:13"),
        end=pd.to_datetime("2024-01-10 12:12:13"),
    )

    expected = pd.Series(
        [0.0, 5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0],
        index=pd.to_datetime(
            [
                "2023-12-31",
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
                "2024-01-06",
                "2024-01-07",
                "2024-01-08",
                "2024-01-09",
                "2024-01-10",
            ]
        ),
    )

    assert result.equals(expected)


def test_aggregate_over_time_yearly(sample_series):
    result = aggregate_over_time(
        s=sample_series,
        freq="YE",
        start=pd.to_datetime("2023-12-31 12:12:13"),
        end=pd.to_datetime("2025-01-10 12:12:13"),
    )

    expected = pd.Series(
        [0.0, 20.0, 0.0],
        index=pd.to_datetime(
            [
                "2023-12-31",
                "2024-12-31",
                "2025-12-31",
            ]
        ),
    )

    assert result.equals(expected)


def test_get_activites():
    df = pd.DataFrame({"Aktivitetstyp": ["Löpning", "Cycling", "Styrketräning"]})

    activities = get_activities(df)

    assert set(activities) == {"Löpning", "Cycling", "Styrketräning"}


def test_days_without_activity_basic():
    df = pd.DataFrame(
        {
            "Activity": ["A", "B", "C"],
        },
        index=pd.to_datetime(
            [
                "2023-12-30 18:05:42",
                "2024-01-03 01:33:12",
                "2024-01-06 23:23:23",
            ]
        ),
    )

    result = get_days_without_activity(df, df.index.min(), df.index.max())

    expected = pd.Series(
        1,
        index=pd.to_datetime(
            [
                "2023-12-31",
                "2024-01-01",
                "2024-01-02",
                "2024-01-04",
                "2024-01-05",
            ]
        ),
    )

    assert result.equals(expected)


def test_days_without_activity_no_gaps():
    df = pd.DataFrame(
        {
            "Activity": ["A", "B", "C"],
        },
        index=pd.to_datetime(
            [
                "2023-12-31 18:05:42",
                "2024-01-01 01:33:12",
                "2024-01-02 23:23:23",
            ]
        ),
    )

    result = get_days_without_activity(df, df.index.min(), df.index.max())

    expected = pd.Series([], index=pd.DatetimeIndex([], freq="D"), dtype="int64")

    assert result.equals(expected)


def test_get_summable_metrics_excludes_columns_with_nan(sample_df_2):
    summable = get_summable_metrics(sample_df_2)

    required = {"Distans", "Tid", "Kalorier", "Totalt nedför"}
    assert required.issubset(summable)

    # Has NaN → should be excluded
    assert "Steg" not in summable


def test_get_summable_metrics_ignores_missing_columns(sample_df_2):
    summable = get_summable_metrics(sample_df_2)

    # Column does not exist in df
    assert "Total stigning" not in summable


def test_get_summable_metrics_empty_dataframe():
    # Create an empty DataFrame with the same columns as SUMMABLE_COLUMNS
    df = pd.DataFrame(columns=SUMMABLE_COLUMNS)

    summable = get_summable_metrics(df)

    # Since the DataFrame has no rows, no metrics should be considered summable
    assert summable == []


def test_select_metric_and_drop_zeros(sample_df_2):
    res = select_metric_and_drop_zeros(sample_df_2, "Totalt nedför")

    expected = pd.Series(
        [32, 44],
        index=pd.to_datetime(
            [
                "2024-01-01 13:12:11",
                "2024-01-08 01:34:34",
            ]
        ),
    )

    assert res.equals(expected)
