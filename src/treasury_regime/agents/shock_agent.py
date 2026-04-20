from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import pandas as pd

from treasury_regime.constants import SHOCK_CATEGORIES
from treasury_regime.schemas import EvidenceClaim, ShockEvent


@dataclass
class ShockBundle:
    latest: ShockEvent
    history: pd.DataFrame


CATEGORY_CHANNEL = {
    "kinetic_geopolitical": "geopolitical_risk_and_safe_haven",
    "energy_shipping_supply": "energy_and_supply_chain",
    "fiscal_issuance_defense": "issuance_and_term_premium",
    "monetary_credibility": "policy_and_inflation_expectations",
    "funding_liquidity": "funding_and_market_functioning",
    "narrative_policy_signaling": "narrative_and_policy_signaling",
}


class ShockAgent:
    def _category_scores(
        self,
        row: pd.Series,
        recent_claims: list[EvidenceClaim],
    ) -> dict[str, float]:
        titles = " ".join(claim.title.lower() for claim in recent_claims)
        policy_claim_boost = sum(0.2 for claim in recent_claims if claim.regime_axis == "policy")
        fiscal_claim_boost = sum(0.2 for claim in recent_claims if claim.regime_axis == "fiscal")
        inflation_claim_boost = sum(0.2 for claim in recent_claims if claim.regime_axis == "inflation")
        funding_claim_boost = sum(0.2 for claim in recent_claims if claim.regime_axis == "funding")

        scores = {
            "kinetic_geopolitical": 0.45 * max(float(row.get("z_wti", 0.0)), 0.0)
            + 0.35 * max(float(row.get("z_vix", 0.0)), 0.0)
            + (0.8 if any(word in titles for word in ("iran", "israel", "war", "missile", "hormuz")) else 0.0),
            "energy_shipping_supply": 0.55 * max(float(row.get("z_wti", 0.0)), 0.0)
            + 0.30 * max(float(row.get("z_breakeven", 0.0)), 0.0)
            + inflation_claim_boost,
            "fiscal_issuance_defense": 0.55 * max(float(row.get("fiscal_term_premium_score", 0.0)), 0.0)
            + 0.20 * max(float(row.get("z_curve_5s30s", 0.0)), 0.0)
            + fiscal_claim_boost,
            "monetary_credibility": 0.50 * max(float(row.get("policy_constraint_score", 0.0)), 0.0)
            + 0.20 * max(float(row.get("z_2y_move", 0.0)), 0.0)
            + policy_claim_boost,
            "funding_liquidity": 0.65 * max(float(row.get("funding_stress_score", 0.0)), 0.0)
            + 0.15 * max(float(row.get("z_vix", 0.0)), 0.0)
            + funding_claim_boost,
            "narrative_policy_signaling": 0.30 * max(abs(float(row.get("z_2y_move", 0.0))), 0.0)
            + 0.20 * max(abs(float(row.get("z_10y_move", 0.0))), 0.0)
            + 0.25 * len(recent_claims),
        }
        return scores

    def _default_persistence(self, category: str) -> float:
        persistence = {
            "kinetic_geopolitical": 0.60,
            "energy_shipping_supply": 0.72,
            "fiscal_issuance_defense": 0.78,
            "monetary_credibility": 0.74,
            "funding_liquidity": 0.52,
            "narrative_policy_signaling": 0.35,
        }
        return persistence[category]

    def run(self, features: pd.DataFrame, claims: list[EvidenceClaim]) -> ShockBundle:
        features = features.sort_index()
        history_rows: list[dict[str, object]] = []
        latest_date = features.index[-1]
        recent_claims = claims[:12]

        for date, row in features.iterrows():
            scoped_claims = recent_claims if date == latest_date else []
            scores = self._category_scores(row, scoped_claims)
            dominant_category = max(scores, key=scores.get)
            secondary = [
                category
                for category, value in sorted(scores.items(), key=lambda item: item[1], reverse=True)[1:3]
                if value > 0.35
            ]
            severity = min(1.0, max(scores[dominant_category], 0.0) / 2.5)
            confidence = 0.55 + 0.20 * min(1.0, len(scoped_claims) / 4.0) + 0.15 * severity
            source_actor = "market_inference"
            if scoped_claims:
                source_actor = scoped_claims[0].linked_player or "official_sources"
            history_rows.append(
                {
                    "date": date,
                    "dominant_category": dominant_category,
                    "secondary_categories": "|".join(secondary),
                    "transmission_channel": CATEGORY_CHANNEL[dominant_category],
                    "severity_score": severity,
                    "persistence_score": self._default_persistence(dominant_category),
                    "confidence_score": min(0.95, confidence),
                    "source_actor": source_actor,
                }
            )

        history = pd.DataFrame(history_rows).set_index("date")
        latest_row = history.iloc[-1]
        latest = ShockEvent(
            shock_id=f"shock-{uuid4().hex[:12]}",
            date=str(latest_date.date()),
            dominant_category=str(latest_row["dominant_category"]),
            secondary_categories=[value for value in str(latest_row["secondary_categories"]).split("|") if value],
            source_actor=str(latest_row["source_actor"]),
            origin_source="official_and_market_evidence",
            transmission_channel=str(latest_row["transmission_channel"]),
            affected_horizons=["short", "mid", "long"],
            persistence_score=float(latest_row["persistence_score"]),
            severity_score=float(latest_row["severity_score"]),
            confidence_score=float(latest_row["confidence_score"]),
            linked_evidence_ids=[claim.claim_id for claim in recent_claims[:6]],
        )
        return ShockBundle(latest=latest, history=history)
