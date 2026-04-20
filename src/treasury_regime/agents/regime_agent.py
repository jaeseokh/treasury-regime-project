from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from treasury_regime.config import HORIZONS
from treasury_regime.modeling.bayes import combine_prior_and_channels, row_normalize
from treasury_regime.modeling.regime_dictionary import BASE_TRANSITION_MATRIX, INITIAL_REGIME_PRIOR, regime_ids
from treasury_regime.schemas import ChannelUpdate, ShockEvent


@dataclass
class RegimeBundle:
    posterior_history: pd.DataFrame
    latest_summary: dict[str, object]
    latest_channel_updates: list[ChannelUpdate]


class RegimeAgent:
    def _treasury_market_scores(self, row: pd.Series) -> dict[str, float]:
        return {
            "policy_trapped_stagflation_risk": 0.60 * row["policy_constraint_score"] + 0.40 * row["inflation_pressure_score"] + 0.20 * row["policy_uncertainty_score"] - 0.20 * row["growth_slowdown_score"],
            "war_augmented_inflation_pressure": 0.80 * row["inflation_pressure_score"] + 0.25 * row["z_vix"] + 0.20 * row["stagflation_signal"] + 0.15 * row["transition_pressure"],
            "growth_slowdown_constrained_easing": 0.90 * row["growth_slowdown_score"] - 0.20 * row["inflation_pressure_score"],
            "fiscal_term_premium_repricing": 0.70 * row["fiscal_term_premium_score"] + 0.20 * row["z_term_premium_10y"] + 0.15 * row["term_premium_slope_score"] + 0.10 * row.get("z_auction_tail", 0.0),
            "funding_liquidity_stress": 1.00 * row["funding_stress_score"] + 0.20 * row["z_vix"],
            "reanchoring_normalization": -0.45 * row["transition_pressure"] - 0.35 * row["funding_stress_score"] - 0.25 * row["inflation_pressure_score"] - 0.10 * row["policy_uncertainty_score"],
        }

    def _inflation_scores(self, row: pd.Series) -> dict[str, float]:
        core_inflation = row.get("core_pce", row.get("core_cpi", 0.0))
        inflation_level = 0.0 if pd.isna(core_inflation) else (float(core_inflation) - 2.0)
        return {
            "policy_trapped_stagflation_risk": 0.45 * row["inflation_pressure_score"] + 0.15 * inflation_level,
            "war_augmented_inflation_pressure": 0.55 * row["inflation_pressure_score"] + 0.20 * max(float(row["z_wti"]), 0.0),
            "growth_slowdown_constrained_easing": -0.10 * row["inflation_pressure_score"],
            "fiscal_term_premium_repricing": 0.15 * row["inflation_pressure_score"],
            "funding_liquidity_stress": 0.05 * row["inflation_pressure_score"],
            "reanchoring_normalization": -0.30 * row["inflation_pressure_score"] - 0.10 * inflation_level,
        }

    def _policy_scores(self, row: pd.Series) -> dict[str, float]:
        return {
            "policy_trapped_stagflation_risk": 0.70 * row["policy_constraint_score"],
            "war_augmented_inflation_pressure": 0.25 * row["policy_constraint_score"],
            "growth_slowdown_constrained_easing": -0.25 * row["policy_constraint_score"] + 0.20 * row["growth_slowdown_score"],
            "fiscal_term_premium_repricing": 0.05 * row["policy_constraint_score"],
            "funding_liquidity_stress": 0.10 * row["funding_stress_score"],
            "reanchoring_normalization": -0.25 * row["policy_constraint_score"],
        }

    def _activity_scores(self, row: pd.Series) -> dict[str, float]:
        unemployment_gap = 0.0 if pd.isna(row.get("unemployment_rate", np.nan)) else float(row["unemployment_rate"]) - 4.2
        growth_signal = 0.20 * unemployment_gap + 0.15 * row.get("growth_slowdown_score", 0.0)
        return {
            "policy_trapped_stagflation_risk": 0.10 * growth_signal,
            "war_augmented_inflation_pressure": -0.05 * growth_signal,
            "growth_slowdown_constrained_easing": 0.50 * growth_signal,
            "fiscal_term_premium_repricing": 0.05 * row["fiscal_term_premium_score"],
            "funding_liquidity_stress": 0.20 * row["funding_stress_score"],
            "reanchoring_normalization": -0.25 * growth_signal,
        }

    def _shock_scores(self, row: pd.Series, shock_event: ShockEvent) -> dict[str, float]:
        dominant = shock_event.dominant_category
        scores = {regime_id: 0.0 for regime_id in regime_ids()}
        if dominant == "kinetic_geopolitical":
            scores["war_augmented_inflation_pressure"] += 0.70
            scores["policy_trapped_stagflation_risk"] += 0.20
        elif dominant == "energy_shipping_supply":
            scores["war_augmented_inflation_pressure"] += 0.65
            scores["policy_trapped_stagflation_risk"] += 0.15
        elif dominant == "fiscal_issuance_defense":
            scores["fiscal_term_premium_repricing"] += 0.70
            scores["war_augmented_inflation_pressure"] += 0.10
        elif dominant == "monetary_credibility":
            scores["policy_trapped_stagflation_risk"] += 0.55
            scores["growth_slowdown_constrained_easing"] += 0.10
        elif dominant == "funding_liquidity":
            scores["funding_liquidity_stress"] += 0.75
            scores["growth_slowdown_constrained_easing"] += 0.10
        else:
            scores["policy_trapped_stagflation_risk"] += 0.20
        scores["reanchoring_normalization"] -= 0.10 * row["transition_pressure"]
        return scores

    def _weighted_channel_contributions(
        self,
        row: pd.Series,
        horizon: str,
        shock_event: ShockEvent,
    ) -> tuple[list[dict[str, float]], list[ChannelUpdate]]:
        cfg = HORIZONS[horizon]
        channel_map = {
            "treasury_market": (self._treasury_market_scores(row), cfg.treasury_weight),
            "shock_player": (self._shock_scores(row, shock_event), cfg.shock_weight),
            "policy_framework": (self._policy_scores(row), cfg.policy_weight),
            "inflation_regime": (self._inflation_scores(row), cfg.inflation_weight),
            "activity_anchor": (self._activity_scores(row), cfg.activity_weight),
        }

        weighted_scores: list[dict[str, float]] = []
        updates: list[ChannelUpdate] = []
        for channel_name, (scores, weight) in channel_map.items():
            weighted = {regime_id: weight * float(value) for regime_id, value in scores.items()}
            weighted_scores.append(weighted)
            updates.append(
                ChannelUpdate(
                    channel_name=channel_name,
                    horizon=horizon,
                    regime_likelihoods={key: float(value) for key, value in scores.items()},
                    transition_likelihoods=self._transition_updates(scores),
                    confidence=min(0.95, 0.55 + 0.40 * weight),
                    notes=f"{channel_name} contribution for {horizon} horizon",
                )
            )
        return weighted_scores, updates

    def _transition_updates(self, scores: dict[str, float]) -> dict[str, dict[str, float]]:
        updates: dict[str, dict[str, float]] = {}
        for from_regime, row in BASE_TRANSITION_MATRIX.items():
            adjusted = {}
            for to_regime, probability in row.items():
                adjusted[to_regime] = probability + 0.02 * max(scores.get(to_regime, 0.0), -0.5)
            updates[from_regime] = adjusted
        return row_normalize(updates)

    def run(self, features: pd.DataFrame, shock_event: ShockEvent) -> RegimeBundle:
        features = features.sort_index()
        priors = {horizon: INITIAL_REGIME_PRIOR.copy() for horizon in HORIZONS}
        history_rows: list[dict[str, object]] = []
        latest_updates: list[ChannelUpdate] = []

        for date, row in features.iterrows():
            row = row.fillna(0.0)
            row_result: dict[str, object] = {"date": date}
            for horizon in HORIZONS:
                weighted_scores, updates = self._weighted_channel_contributions(row, horizon, shock_event)
                posterior = combine_prior_and_channels(priors[horizon], weighted_scores)
                priors[horizon] = posterior
                for regime_id, probability in posterior.items():
                    row_result[f"{horizon}_{regime_id}"] = probability
                row_result[f"{horizon}_dominant_regime"] = max(posterior, key=posterior.get)
                row_result[f"{horizon}_dominant_probability"] = posterior[row_result[f"{horizon}_dominant_regime"]]
                if date == features.index[-1]:
                    latest_updates.extend(updates)
            history_rows.append(row_result)

        posterior_history = pd.DataFrame(history_rows).set_index("date")
        latest = posterior_history.iloc[-1]
        latest_summary = {
            "date": str(posterior_history.index[-1].date()),
            "dominant_regimes": {
                horizon: {
                    "regime_id": str(latest[f"{horizon}_dominant_regime"]),
                    "probability": float(latest[f"{horizon}_dominant_probability"]),
                }
                for horizon in HORIZONS
            },
            "transition_matrix": row_normalize(BASE_TRANSITION_MATRIX),
        }
        return RegimeBundle(
            posterior_history=posterior_history,
            latest_summary=latest_summary,
            latest_channel_updates=latest_updates,
        )
