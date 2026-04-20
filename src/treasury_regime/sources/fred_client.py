from __future__ import annotations

from io import StringIO
import time

import pandas as pd
import requests

from treasury_regime.constants import FRED_SERIES


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def download_series(series_id: str, column_name: str, start_date: str) -> pd.DataFrame:
    session = requests.Session()
    response = None
    for attempt in range(4):
        response = session.get(FRED_CSV_URL, params={"id": series_id}, timeout=30)
        if response.ok:
            break
        if attempt == 3:
            response.raise_for_status()
        time.sleep(1.0 + attempt)
    assert response is not None
    frame = pd.read_csv(StringIO(response.text))
    frame = frame.rename(columns={frame.columns[0]: "date", frame.columns[1]: column_name})
    frame["date"] = pd.to_datetime(frame["date"])
    frame[column_name] = pd.to_numeric(frame[column_name], errors="coerce")
    frame = frame.set_index("date").sort_index()
    frame = frame.loc[pd.Timestamp(start_date) :]
    return frame[[column_name]]


def download_market_dataset(start_date: str = "2024-01-01") -> pd.DataFrame:
    frames = [download_series(series_id, column_name, start_date) for series_id, column_name in FRED_SERIES.items()]
    dataset = pd.concat(frames, axis=1, join="outer").sort_index()
    dataset = dataset.ffill()
    dataset.index = pd.DatetimeIndex(dataset.index, name="date")
    dataset["curve_2s10s"] = dataset["yield_10y"] - dataset["yield_2y"]
    dataset["curve_5s30s"] = dataset["yield_30y"] - dataset["yield_5y"]
    dataset["fly_2s5s10s"] = dataset["yield_2y"] - 2.0 * dataset["yield_5y"] + dataset["yield_10y"]
    dataset["sofr_minus_ff"] = dataset["sofr"] - dataset["fed_funds_effective"]
    dataset["repo_minus_sofr"] = dataset["overnight_bank_funding_rate"] - dataset["sofr"]
    dataset["breakeven_gap_5s10s"] = dataset["breakeven_10y"] - dataset["breakeven_5y"]
    return dataset.dropna(how="all")
