from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from treasury_regime.config import MANUAL_DIR, OUTPUT_DIR, WEBSITE_DATA_DIR
from treasury_regime.modeling.regime_dictionary import BASE_TRANSITION_MATRIX, REGIME_DEFINITIONS
from treasury_regime.utils import read_json, write_json


def export_website_payloads(
    latest_summary_path: Path | None = None,
    posterior_history_path: Path | None = None,
    shock_history_path: Path | None = None,
    player_probabilities_path: Path | None = None,
    regime_review_path: Path | None = None,
    source_scorecard_path: Path | None = None,
    market_features_path: Path | None = None,
    research_upgrade_map_path: Path | None = None,
) -> dict[str, Path]:
    latest_summary_path = latest_summary_path or (OUTPUT_DIR / "daily_summary.json")
    posterior_history_path = posterior_history_path or (OUTPUT_DIR / "posterior_history.csv")
    shock_history_path = shock_history_path or (OUTPUT_DIR / "shock_history.csv")
    player_probabilities_path = player_probabilities_path or (OUTPUT_DIR / "player_probabilities.csv")
    regime_review_path = regime_review_path or (OUTPUT_DIR / "regime_review.csv")
    source_scorecard_path = source_scorecard_path or (OUTPUT_DIR / "source_scorecard.csv")
    market_features_path = market_features_path or (OUTPUT_DIR / "market_features_export.csv")
    research_upgrade_map_path = research_upgrade_map_path or (MANUAL_DIR / "research_upgrade_map.json")

    def _safe_read_csv(path: Path, **kwargs: object) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path, **kwargs)
        except EmptyDataError:
            return pd.DataFrame()

    latest = read_json(latest_summary_path, default={})
    posterior_history = _safe_read_csv(posterior_history_path, parse_dates=["date"])
    shock_history = _safe_read_csv(shock_history_path, parse_dates=["date"])
    player_probabilities = _safe_read_csv(player_probabilities_path)
    regime_review = _safe_read_csv(regime_review_path, parse_dates=["forecast_date"])
    source_scorecard = _safe_read_csv(source_scorecard_path)
    market_features = _safe_read_csv(market_features_path, parse_dates=["date"])
    research_upgrade_map = read_json(research_upgrade_map_path, default={})

    if not posterior_history.empty:
        history = posterior_history.merge(shock_history, on="date", how="left")
        if not market_features.empty:
            columns = [
                "date",
                "yield_2y",
                "yield_10y",
                "curve_2s10s",
                "breakeven_10y",
                "real_10y",
                "expected_short_rate_proxy_10y",
                "term_premium_proxy_10y",
                "ns_curvature",
                "transition_pressure",
            ]
            available = [column for column in columns if column in market_features.columns]
            history = history.merge(market_features.loc[:, available], on="date", how="left")
    else:
        history = pd.DataFrame()

    hierarchy = research_upgrade_map.get("hierarchy", [])
    all_upgrades = [
        upgrade
        for layer in hierarchy
        for upgrade in layer.get("next_upgrades", [])
    ]
    roadmap_summary = {
        "system_version": research_upgrade_map.get("system_version", "v1"),
        "layer_count": len(hierarchy),
        "upgrade_count": len(all_upgrades),
        "high_priority_count": sum(1 for item in all_upgrades if item.get("priority") == "high"),
        "in_progress_count": sum(1 for item in all_upgrades if item.get("status") == "in_progress"),
    }

    latest_payload = {
        "summary": latest,
        "player_probabilities": player_probabilities.to_dict(orient="records"),
        "source_scorecard": source_scorecard.to_dict(orient="records"),
        "roadmap_summary": roadmap_summary,
    }
    history_payload = history.tail(260).to_dict(orient="records") if not history.empty else []
    archive_payload = {
        "notes": history.sort_values("date", ascending=False).head(90).to_dict(orient="records") if not history.empty else [],
        "regime_review": regime_review.to_dict(orient="records"),
        "miss_summary": (
            regime_review.groupby(["target_horizon", "miss_type"], as_index=False)
            .agg(
                observations=("miss_type", "size"),
                avg_directional_accuracy=("directional_accuracy", "mean"),
            )
            .sort_values(["target_horizon", "observations"], ascending=[True, False])
            .to_dict(orient="records")
            if not regime_review.empty and "miss_type" in regime_review.columns
            else []
        ),
    }
    framework_payload = {
        "regimes": REGIME_DEFINITIONS,
        "transition_matrix": BASE_TRANSITION_MATRIX,
    }
    roadmap_payload = research_upgrade_map

    destinations = {
        "latest": write_json(WEBSITE_DATA_DIR / "latest.json", latest_payload),
        "history": write_json(WEBSITE_DATA_DIR / "history.json", history_payload),
        "archive": write_json(WEBSITE_DATA_DIR / "archive.json", archive_payload),
        "framework": write_json(WEBSITE_DATA_DIR / "framework.json", framework_payload),
        "roadmap": write_json(WEBSITE_DATA_DIR / "roadmap.json", roadmap_payload),
    }
    return destinations


def main() -> None:
    destinations = export_website_payloads()
    for name, destination in destinations.items():
        print(f"{name}: {destination}")
