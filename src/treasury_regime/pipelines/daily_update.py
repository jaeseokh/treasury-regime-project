from __future__ import annotations

import logging
from pathlib import Path

from treasury_regime.agents.data_agent import DataAgent
from treasury_regime.agents.evidence_agent import EvidenceAgent
from treasury_regime.agents.player_agent import PlayerAgent
from treasury_regime.agents.regime_agent import RegimeAgent
from treasury_regime.agents.report_agent import ReportAgent
from treasury_regime.agents.review_agent import ReviewAgent
from treasury_regime.agents.shock_agent import ShockAgent
from treasury_regime.config import MANUAL_DIR, OUTPUT_DIR
from treasury_regime.pipelines.website_export import export_website_payloads
from treasury_regime.utils import read_json, write_frame, write_json


def run_daily_update() -> dict[str, object]:
    data_bundle = DataAgent().run()
    evidence_bundle = EvidenceAgent().run()
    shock_bundle = ShockAgent().run(data_bundle.market_features, evidence_bundle.claims)
    regime_bundle = RegimeAgent().run(data_bundle.market_features, shock_bundle.history)
    player_bundle = PlayerAgent().run(data_bundle.market_features, regime_bundle.latest_summary)
    review_bundle = ReviewAgent().run(
        data_bundle.market_data,
        regime_bundle.posterior_history,
        evidence_bundle.frame,
    )
    report_bundle = ReportAgent().run(
        data_bundle.market_data,
        data_bundle.market_features,
        shock_bundle.latest,
        regime_bundle.latest_summary,
        regime_bundle.latest_channel_updates,
        player_bundle.responses,
        review_bundle.source_scorecard,
    )

    write_frame(OUTPUT_DIR / "posterior_history.csv", regime_bundle.posterior_history)
    write_frame(OUTPUT_DIR / "shock_history.csv", shock_bundle.history)
    write_frame(OUTPUT_DIR / "player_probabilities.csv", player_bundle.frame, index=False)
    write_frame(OUTPUT_DIR / "regime_review.csv", review_bundle.regime_scores, index=False)
    write_frame(OUTPUT_DIR / "source_scorecard.csv", review_bundle.source_scorecard, index=False)
    write_frame(OUTPUT_DIR / "market_features_export.csv", data_bundle.market_features.reset_index(), index=False)
    write_json(OUTPUT_DIR / "shock_latest.json", shock_bundle.latest)
    write_json(OUTPUT_DIR / "regime_latest.json", regime_bundle.latest_summary)
    write_json(OUTPUT_DIR / "research_upgrade_map.json", read_json(MANUAL_DIR / "research_upgrade_map.json", default={}))
    export_website_payloads()

    return {
        "data_bundle": data_bundle,
        "evidence_bundle": evidence_bundle,
        "shock_bundle": shock_bundle,
        "regime_bundle": regime_bundle,
        "player_bundle": player_bundle,
        "review_bundle": review_bundle,
        "report_bundle": report_bundle,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    results = run_daily_update()
    summary = results["report_bundle"].summary
    print(f"Date: {summary['date']}")
    print(f"Short regime: {summary['current_regime']['short']['regime_id']}")
    print(f"Mid regime: {summary['current_regime']['mid']['regime_id']}")
    print(f"Long regime: {summary['current_regime']['long']['regime_id']}")
    print(f"Dominant shock: {summary['shock_event'].dominant_category}")
