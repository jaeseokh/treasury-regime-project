from __future__ import annotations

import time
from typing import Any

import pandas as pd
import requests


TREASURY_API_BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"


def _fetch_all_pages(endpoint: str, *, params: dict[str, Any] | None = None) -> pd.DataFrame:
    session = requests.Session()
    page_number = 1
    frames: list[pd.DataFrame] = []
    while True:
        request_params = {"page[size]": 1000, "page[number]": page_number, "format": "json"}
        if params:
            request_params.update(params)
        response = None
        for attempt in range(4):
            response = session.get(f"{TREASURY_API_BASE}{endpoint}", params=request_params, timeout=30)
            if response.ok:
                break
            if attempt == 3:
                response.raise_for_status()
            time.sleep(1.0 + attempt)
        assert response is not None
        payload = response.json()
        data = payload.get("data", [])
        if not data:
            break
        frames.append(pd.DataFrame(data))
        total_pages = int(payload.get("meta", {}).get("total-pages", 1))
        if page_number >= total_pages:
            break
        page_number += 1

    if not frames:
        return pd.DataFrame()
    frame = pd.concat(frames, ignore_index=True)
    for column in frame.columns:
        if "date" in column.lower():
            frame[column] = pd.to_datetime(frame[column], errors="coerce", format="mixed")
    return frame


def fetch_auction_history(start_date: str = "2024-01-01") -> pd.DataFrame:
    return _fetch_all_pages(
        "/v1/accounting/od/auctions_query",
        params={"filter": f"record_date:gte:{start_date}"},
    )


def fetch_upcoming_auctions() -> pd.DataFrame:
    return _fetch_all_pages("/v1/accounting/od/upcoming_auctions")
