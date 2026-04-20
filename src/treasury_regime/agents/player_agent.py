from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd

from treasury_regime.schemas import PlayerResponse, PlayerScenario


@dataclass
class PlayerBundle:
    responses: list[PlayerResponse]
    frame: pd.DataFrame


def _softmax(scores: dict[str, float]) -> dict[str, float]:
    max_score = max(scores.values())
    exps = {key: math.exp(value - max_score) for key, value in scores.items()}
    total = sum(exps.values())
    return {key: value / total for key, value in exps.items()}


class PlayerAgent:
    def _scenario_templates(
        self,
        player_id: str,
        row: pd.Series,
        dominant_regime: str,
    ) -> dict[str, dict[str, float]]:
        if player_id == "treasury":
            return {
                "short": {
                    "maintain_issuance_mix": 0.2,
                    "communication_support": 0.3 + 0.5 * row.get("fiscal_term_premium_score", 0.0),
                    "bill_heavy_flexibility": 0.25 + 0.4 * row.get("funding_stress_score", 0.0),
                },
                "mid": {
                    "refund_bills_over_coupons": 0.20 + 0.5 * row.get("fiscal_term_premium_score", 0.0),
                    "stabilize_coupon_path": 0.30,
                    "defense_financing_bias": 0.15 + 0.4 * (1.0 if "war" in dominant_regime else 0.0),
                },
                "long": {
                    "preserve_market_confidence": 0.45 + 0.4 * row.get("fiscal_term_premium_score", 0.0),
                    "normalize_issuance_mix": 0.20,
                    "structural_bill_bias": 0.15 + 0.2 * row.get("funding_stress_score", 0.0),
                },
            }
        if player_id == "federal_reserve":
            return {
                "short": {
                    "hawkish_hold": 0.25 + 0.5 * row.get("policy_constraint_score", 0.0),
                    "look_through_supply_shock": 0.20 + 0.3 * row.get("inflation_pressure_score", 0.0),
                    "stability_monitoring": 0.15 + 0.5 * row.get("funding_stress_score", 0.0),
                },
                "mid": {
                    "delay_easing": 0.30 + 0.4 * row.get("inflation_pressure_score", 0.0),
                    "measured_easing": 0.20 + 0.4 * row.get("growth_slowdown_score", 0.0),
                    "liquidity_backstop_if_needed": 0.10 + 0.4 * row.get("funding_stress_score", 0.0),
                },
                "long": {
                    "restore_credibility": 0.35 + 0.3 * row.get("policy_constraint_score", 0.0),
                    "soft_landing_normalization": 0.20,
                    "financial_stability_tools": 0.10 + 0.3 * row.get("funding_stress_score", 0.0),
                },
            }
        if player_id == "sell_side":
            return {
                "short": {
                    "front_end_repricing": 0.25 + 0.5 * abs(row.get("z_2y_move", 0.0)),
                    "balance_sheet_conservatism": 0.20 + 0.5 * row.get("funding_stress_score", 0.0),
                    "flow_amplification": 0.20 + 0.3 * row.get("transition_pressure", 0.0),
                },
                "mid": {
                    "curve_reshaping": 0.25 + 0.4 * abs(row.get("z_curve_5s30s", 0.0)),
                    "client_rehedging": 0.22 + 0.3 * row.get("transition_pressure", 0.0),
                    "inventory_reduction": 0.15 + 0.4 * row.get("funding_stress_score", 0.0),
                },
                "long": {
                    "new_macro_consensus": 0.20 + 0.25 * row.get("transition_pressure", 0.0),
                    "structural_long_end_discount": 0.15 + 0.4 * row.get("fiscal_term_premium_score", 0.0),
                    "normalized_intermediation": 0.18,
                },
            }
        if player_id == "buy_side":
            return {
                "short": {
                    "wait_for_confirmation": 0.24 + 0.3 * row.get("transition_pressure", 0.0),
                    "inflation_hedge_bias": 0.20 + 0.4 * row.get("inflation_pressure_score", 0.0),
                    "quality_duration_bid": 0.18 + 0.4 * row.get("growth_slowdown_score", 0.0),
                },
                "mid": {
                    "underweight_duration": 0.18 + 0.5 * row.get("fiscal_term_premium_score", 0.0),
                    "extend_duration_on_slowdown": 0.20 + 0.5 * row.get("growth_slowdown_score", 0.0),
                    "barbell_real_and_nominal": 0.18 + 0.3 * row.get("inflation_pressure_score", 0.0),
                },
                "long": {
                    "soft_landing_reengagement": 0.18,
                    "structural_inflation_hedge": 0.20 + 0.4 * row.get("inflation_pressure_score", 0.0),
                    "selective_long_duration": 0.18 + 0.3 * row.get("growth_slowdown_score", 0.0),
                },
            }
        return {
            "short": {
                "maintain_reserves": 0.28,
                "shorten_duration": 0.18 + 0.4 * row.get("fiscal_term_premium_score", 0.0),
                "safe_haven_reentry": 0.15 + 0.4 * row.get("growth_slowdown_score", 0.0),
            },
            "mid": {
                "gradual_diversification": 0.15 + 0.3 * row.get("fiscal_term_premium_score", 0.0),
                "maintain_core_treasury_holdings": 0.28,
                "prefer_front_end_liquidity": 0.20 + 0.3 * row.get("funding_stress_score", 0.0),
            },
            "long": {
                "conditional_safe_haven_demand": 0.22,
                "reserve_rebalancing": 0.15 + 0.3 * row.get("fiscal_term_premium_score", 0.0),
                "return_if_reanchoring": 0.15 + 0.3 * (1.0 if dominant_regime == "reanchoring_normalization" else 0.0),
            },
        }

    def run(self, features: pd.DataFrame, regime_summary: dict[str, object]) -> PlayerBundle:
        row = features.iloc[-1].fillna(0.0)
        latest_date = str(features.index[-1].date())
        dominant_mid_regime = regime_summary["dominant_regimes"]["mid"]["regime_id"]

        metadata = {
            "treasury": ("Preserve market access and financing credibility", "Heavy issuance and term-premium sensitivity"),
            "federal_reserve": ("Protect inflation credibility while managing downside risk", "Dual-mandate conflict under uncertainty"),
            "sell_side": ("Intermediate flow and manage balance sheet", "Inventory, funding, and client flow stress"),
            "buy_side": ("Allocate duration and inflation risk efficiently", "Regime uncertainty and drawdown control"),
            "foreign_official": ("Preserve reserves and liquidity", "Dollar exposure and safe-haven confidence"),
        }

        responses: list[PlayerResponse] = []
        frame_rows: list[dict[str, object]] = []
        for player_id, (objective, constraint) in metadata.items():
            templates = self._scenario_templates(player_id, row, dominant_mid_regime)
            horizon_scenarios: dict[str, list[PlayerScenario]] = {}
            for horizon, raw_scores in templates.items():
                normalized = _softmax(raw_scores)
                scenarios = [
                    PlayerScenario(
                        action=action,
                        probability=probability,
                        rationale=f"{player_id} {action.replace('_', ' ')} probability under {dominant_mid_regime}",
                    )
                    for action, probability in sorted(normalized.items(), key=lambda item: item[1], reverse=True)
                ]
                horizon_scenarios[horizon] = scenarios
                for scenario in scenarios:
                    frame_rows.append(
                        {
                            "date": latest_date,
                            "player_id": player_id,
                            "horizon": horizon,
                            "action": scenario.action,
                            "probability": scenario.probability,
                        }
                    )

            responses.append(
                PlayerResponse(
                    player_id=player_id,
                    date=latest_date,
                    main_objective=objective,
                    main_constraint=constraint,
                    horizon_scenarios=horizon_scenarios,
                    linked_market_proxies=[
                        "curve_2s10s",
                        "breakeven_10y",
                        "repo_minus_sofr",
                        "high_yield_spread",
                    ],
                )
            )
        return PlayerBundle(responses=responses, frame=pd.DataFrame(frame_rows))
