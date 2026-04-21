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

    def _miss_type(
        self,
        horizon: str,
        target_hits: dict[str, float],
        start_values: dict[str, float],
        first_day_values: dict[str, float],
        final_values: dict[str, float],
        dominant_regime: str,
    ) -> tuple[str, str]:
        if all(hit >= 1.0 for hit in target_hits.values()):
            return "correct", "All tracked Treasury targets moved in the expected direction."

        first_day_hits = {
            target: float(
                self._expected_direction(dominant_regime, target, horizon)
                == self._realized_direction(start_values[target], first_day_values[target])
            )
            for target in target_hits
        }

        yield_hits = [target_hits["yield_2y"], target_hits["yield_10y"]]
        if first_day_hits["yield_2y"] + first_day_hits["yield_10y"] >= 1.0 and sum(yield_hits) == 0:
            return "wrong_persistence", "The initial move aligned with the call, but the horizon follow-through did not persist."

        if sum(yield_hits) == 0:
            return "wrong_regime_direction", "Front-end and long-end direction both contradicted the dominant regime call."

        if first_day_hits["curve_2s10s"] == 1.0 and target_hits["curve_2s10s"] == 0.0:
            return "wrong_persistence", "The curve initially behaved as expected, but that transmission faded over the review horizon."

        if target_hits["curve_2s10s"] == 0.0 and sum(yield_hits) >= 1.0:
            return "wrong_transmission", "Rate direction was partly right, but the curve transmission was wrong."

        if horizon != "short" and sum(first_day_hits.values()) > sum(target_hits.values()):
            return "wrong_persistence", "The short-horizon direction looked right, but the move did not hold through the target horizon."

        return "mixed_miss", "The regime call captured part of the move, but the realized path was mixed across targets."

    def run(self, market_data: pd.DataFrame, posterior_history: pd.DataFrame, evidence_frame: pd.DataFrame) -> ReviewBundle:
        market_data = market_data.sort_index()
        posterior_history = posterior_history.sort_index()
        horizon_days = {"short": 1, "mid": 5, "long": 22}
        targets = ["yield_2y", "yield_10y", "curve_2s10s"]
        score_rows: list[dict[str, object]] = []

        for horizon, days in horizon_days.items():
            for date in posterior_history.index[:-days]:
                future_date = posterior_history.index[posterior_history.index.get_loc(date) + days]
                first_day_date = posterior_history.index[posterior_history.index.get_loc(date) + 1]
                dominant_regime = posterior_history.loc[date, f"{horizon}_dominant_regime"]
                directional_hits = []
                hit_map: dict[str, float] = {}
                start_values: dict[str, float] = {}
                first_day_values: dict[str, float] = {}
                final_values: dict[str, float] = {}
                for target in targets:
                    start_value = float(market_data.loc[date, target])
                    final_value = float(market_data.loc[future_date, target])
                    expected = self._expected_direction(str(dominant_regime), target, horizon)
                    realized = self._realized_direction(
                        start_value,
                        final_value,
                    )
                    hit = float(expected == realized)
                    directional_hits.append(hit)
                    hit_map[target] = hit
                    start_values[target] = start_value
                    first_day_values[target] = float(market_data.loc[first_day_date, target])
                    final_values[target] = final_value

                miss_type, miss_note = self._miss_type(
                    horizon,
                    hit_map,
                    start_values,
                    first_day_values,
                    final_values,
                    str(dominant_regime),
                )
                score_rows.append(
                    {
                        "forecast_date": date,
                        "target_horizon": horizon,
                        "dominant_regime": dominant_regime,
                        "directional_accuracy": float(np.mean(directional_hits)),
                        "yield_2y_hit": hit_map["yield_2y"],
                        "yield_10y_hit": hit_map["yield_10y"],
                        "curve_2s10s_hit": hit_map["curve_2s10s"],
                        "miss_type": miss_type,
                        "miss_note": miss_note,
                    }
                )

        regime_scores = pd.DataFrame(score_rows)
        if regime_scores.empty:
            regime_scores = pd.DataFrame(
                columns=[
                    "forecast_date",
                    "target_horizon",
                    "dominant_regime",
                    "directional_accuracy",
                    "yield_2y_hit",
                    "yield_10y_hit",
                    "curve_2s10s_hit",
                    "miss_type",
                    "miss_note",
                ]
            )

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
