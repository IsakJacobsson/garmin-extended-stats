import pandas as pd
import pytest

from metrics import SUMMABLE_COLUMNS, aggregate_metric_over_time, get_valid_metrics


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


def test_get_valid_metrics_excludes_columns_with_nan(sample_df):
    valid = get_valid_metrics(sample_df)

    assert "Distans" in valid
    assert "Tid" in valid
    assert "Kalorier" in valid

    # Has NaN → should be excluded
    assert "Steg" not in valid


def test_get_valid_metrics_ignores_missing_columns(sample_df):
    valid = get_valid_metrics(sample_df)

    # Column does not exist in df
    assert "Total stigning" not in valid


def test_get_valid_metrics_empty_dataframe():
    df = pd.DataFrame()

    valid = get_valid_metrics(df)

    assert valid == []


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
