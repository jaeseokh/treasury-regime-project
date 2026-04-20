from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from treasury_regime.config import PROCESSED_DIR, RAW_DIR
from treasury_regime.modeling.market_features import build_market_features, summarize_auctions
from treasury_regime.sources.fred_client import download_market_dataset
from treasury_regime.sources.treasury_client import fetch_auction_history, fetch_upcoming_auctions
from treasury_regime.utils import write_frame


@dataclass
class DataBundle:
    market_data: pd.DataFrame
    auction_history: pd.DataFrame
    upcoming_auctions: pd.DataFrame
    auction_summary: pd.DataFrame
    market_features: pd.DataFrame
    paths: dict[str, Path]


class DataAgent:
    def __init__(self, start_date: str = "2007-01-01") -> None:
        self.start_date = start_date

    def run(self) -> DataBundle:
        market_data = download_market_dataset(start_date=self.start_date)
        auction_history = fetch_auction_history(start_date=self.start_date)
        upcoming_auctions = fetch_upcoming_auctions()
        auction_summary = summarize_auctions(auction_history, upcoming_auctions)
        market_features = build_market_features(market_data, auction_summary)

        paths = {
            "market_data": write_frame(RAW_DIR / "market_data.csv", market_data),
            "auction_history": write_frame(RAW_DIR / "auction_history.csv", auction_history, index=False),
            "upcoming_auctions": write_frame(RAW_DIR / "upcoming_auctions.csv", upcoming_auctions, index=False),
            "auction_summary": write_frame(PROCESSED_DIR / "auction_summary.csv", auction_summary),
            "market_features": write_frame(PROCESSED_DIR / "market_features.csv", market_features),
        }
        return DataBundle(
            market_data=market_data,
            auction_history=auction_history,
            upcoming_auctions=upcoming_auctions,
            auction_summary=auction_summary,
            market_features=market_features,
            paths=paths,
        )
