from typing import Optional

import pandas as pd
import streamlit as st

from metrics import aggregate_over_time

tab_info = [
    ("Day", "D", "%Y-%m-%d"),
    ("Week", "W", "%Y-%W"),
    ("Month", "ME", "%Y-%m"),
    ("Year", "YE", "%Y"),
]


def aggregation_bar_plot(
    s: pd.Series,
    start: Optional[pd.Timestamp] = None,
    end: Optional[pd.Timestamp] = None,
) -> None:
    # Create tabs for different resolutions
    tabs = st.tabs([label for label, _, _ in tab_info])
    for tab, (_, freq, date_format) in zip(tabs, tab_info):
        aggregated_s = aggregate_over_time(s, freq, start, end)
        with tab:
            plot_metric(aggregated_s, date_format)


def plot_metric(data: pd.Series, fmt: str) -> None:
    data = data.copy()
    data.index = data.index.strftime(fmt)

    st.bar_chart(data)
