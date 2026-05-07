from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from typing import Any


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


@dataclass
class RegimeDefinition:
    regime_id: str
    regime_name: str
    regime_family: str
    economic_definition: str
    inflation_state: str
    growth_state: str
    labor_state: str
    policy_state: str
    financial_state: str
    fiscal_geopolitical_state: str
    treasury_signature: list[str]
    entry_conditions: list[str]
    exit_conditions: list[str]
    allowed_next_regimes: list[str]


@dataclass
class EvidenceClaim:
    claim_id: str
    source_name: str
    source_family: str
    source_type: str
    published_at: str
    title: str
    summary: str
    url: str
    linked_player: str | None
    regime_axis: str
    expected_direction: str
    expected_channel: str
    horizon: str
    confidence: float


@dataclass
class ShockEvent:
    shock_id: str
    date: str
    dominant_category: str
    secondary_categories: list[str]
    source_actor: str
    origin_source: str
    transmission_channel: str
    affected_horizons: list[str]
    persistence_score: float
    severity_score: float
    confidence_score: float
    linked_evidence_ids: list[str] = field(default_factory=list)


@dataclass
class ChannelUpdate:
    channel_name: str
    horizon: str
    regime_likelihoods: dict[str, float]
    transition_likelihoods: dict[str, dict[str, float]]
    confidence: float
    notes: str


@dataclass
class PlayerScenario:
    action: str
    probability: float
    rationale: str


@dataclass
class PlayerResponse:
    player_id: str
    date: str
    main_objective: str
    main_constraint: str
    horizon_scenarios: dict[str, list[PlayerScenario]]
    linked_market_proxies: list[str]


@dataclass
class ForecastScore:
    forecast_date: str
    target_horizon: str
    object_type: str
    object_id: str
    predicted_state: str
    realized_state: str
    directional_accuracy: float
    probability_score: float
    channel_accuracy: float
    persistence_accuracy: float
