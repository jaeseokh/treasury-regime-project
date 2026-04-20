from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ReviewBundle:
    regime_scores: pd.DataFrame
    source_scorecard: pd.DataFrame


class ReviewAgent:
    def _expected_direction(self, regime_id: str, target: str, horizon: str) -> str:
        mapping = {
            "policy_trapped_stagflation_risk": {"yield_2y": "up", "yield_10y": "up", "curve_2s10s": "flat"},
            "war_augmented_inflation_pressure": {"yield_2y": "up", "yield_10y": "up", "curve_2s10s": "flat"},
            "growth_slowdown_constrained_easing": {"yield_2y": "down", "yield_10y": "down", "curve_2s10s": "up"},
            "fiscal_term_premium_repricing": {"yield_2y": "flat", "yield_10y": "up", "curve_2s10s": "up"},
            "funding_liquidity_stress": {"yield_2y": "down", "yield_10y": "down", "curve_2s10s": "flat"},
            "reanchoring_normalization": {"yield_2y": "down", "yield_10y": "down", "curve_2s10s": "up"},
        }
        return mapping.get(regime_id, {}).get(target, "flat")

    def _realized_direction(self, start: float, end: float) -> str:
        delta = end - start
        if delta > 0.015:
            return "up"
        if delta < -0.015:
            return "down"
        return "flat"

    def run(self, market_data: pd.DataFrame, posterior_history: pd.DataFrame, evidence_frame: pd.DataFrame) -> ReviewBundle:
        market_data = market_data.sort_index()
        posterior_history = posterior_history.sort_index()
        horizon_days = {"short": 1, "mid": 5, "long": 22}
        targets = ["yield_2y", "yield_10y", "curve_2s10s"]
        score_rows: list[dict[str, object]] = []

        for horizon, days in horizon_days.items():
            for date in posterior_history.index[:-days]:
                future_date = posterior_history.index[posterior_history.index.get_loc(date) + days]
                dominant_regime = posterior_history.loc[date, f"{horizon}_dominant_regime"]
                directional_hits = []
                for target in targets:
                    expected = self._expected_direction(str(dominant_regime), target, horizon)
                    realized = self._realized_direction(
                        float(market_data.loc[date, target]),
                        float(market_data.loc[future_date, target]),
                    )
                    directional_hits.append(float(expected == realized))
                score_rows.append(
                    {
                        "forecast_date": date,
                        "target_horizon": horizon,
                        "dominant_regime": dominant_regime,
                        "directional_accuracy": float(np.mean(directional_hits)),
                    }
                )

        regime_scores = pd.DataFrame(score_rows)
        if regime_scores.empty:
            regime_scores = pd.DataFrame(columns=["forecast_date", "target_horizon", "dominant_regime", "directional_accuracy"])

        source_rows: list[dict[str, object]] = []
        if not evidence_frame.empty:
            recent = evidence_frame.copy()
            recent["published_at"] = pd.to_datetime(recent["published_at"], errors="coerce")
            recent = recent.dropna(subset=["published_at"])
            for _, row in recent.iterrows():
                source_rows.append(
                    {
                        "source_name": row["source_name"],
                        "source_family": row["source_family"],
                        "claims_tracked": 1,
                        "d1_score": 0.5,
                        "w1_score": 0.5,
                        "m1_score": 0.5,
                    }
                )
        source_scorecard = pd.DataFrame(source_rows)
        if not source_scorecard.empty:
            source_scorecard = (
                source_scorecard.groupby(["source_name", "source_family"], as_index=False)
                .agg(
                    claims_tracked=("claims_tracked", "sum"),
                    d1_score=("d1_score", "mean"),
                    w1_score=("w1_score", "mean"),
                    m1_score=("m1_score", "mean"),
                )
                .sort_values(["claims_tracked", "source_name"], ascending=[False, True])
            )
        else:
            source_scorecard = pd.DataFrame(
                columns=["source_name", "source_family", "claims_tracked", "d1_score", "w1_score", "m1_score"]
            )
        return ReviewBundle(regime_scores=regime_scores, source_scorecard=source_scorecard)
