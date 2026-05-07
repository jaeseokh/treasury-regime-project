from __future__ import annotations

import math


def normalize_probabilities(raw: dict[str, float]) -> dict[str, float]:
    total = sum(max(value, 0.0) for value in raw.values())
    if total <= 0:
        uniform = 1.0 / len(raw)
        return {key: uniform for key in raw}
    return {key: max(value, 0.0) / total for key, value in raw.items()}


def normalize_log_scores(log_scores: dict[str, float]) -> dict[str, float]:
    max_score = max(log_scores.values())
    exp_scores = {key: math.exp(value - max_score) for key, value in log_scores.items()}
    return normalize_probabilities(exp_scores)


def blend_probabilities(
    anchor: dict[str, float],
    updated: dict[str, float],
    update_weight: float,
) -> dict[str, float]:
    return normalize_probabilities(
        {
            key: (1.0 - update_weight) * float(anchor.get(key, 0.0))
            + update_weight * float(updated.get(key, 0.0))
            for key in anchor
        }
    )


def apply_probability_floor(probabilities: dict[str, float], floor: float) -> dict[str, float]:
    if floor <= 0:
        return normalize_probabilities(probabilities)
    bounded_floor = min(floor, (1.0 / max(1, len(probabilities))) - 1e-6)
    scale = max(1e-9, 1.0 - len(probabilities) * bounded_floor)
    return normalize_probabilities(
        {
            key: bounded_floor + scale * float(value)
            for key, value in probabilities.items()
        }
    )


def propagate_prior(
    prior: dict[str, float],
    transition_matrix: dict[str, dict[str, float]],
) -> dict[str, float]:
    projected = {
        to_regime: sum(
            float(prior.get(from_regime, 0.0)) * float(transition_row.get(to_regime, 0.0))
            for from_regime, transition_row in transition_matrix.items()
        )
        for to_regime in prior
    }
    return normalize_probabilities(projected)


def combine_prior_and_channels(
    prior: dict[str, float],
    weighted_channel_scores: list[dict[str, float]],
    *,
    temperature: float = 1.0,
    floor: float = 0.0,
    anchor_prior: dict[str, float] | None = None,
    update_weight: float = 1.0,
) -> dict[str, float]:
    log_scores = {key: math.log(max(value, 1e-8)) for key, value in prior.items()}
    for channel in weighted_channel_scores:
        for regime_id, contribution in channel.items():
            log_scores[regime_id] += contribution
    adjusted = {key: value / max(1e-6, temperature) for key, value in log_scores.items()}
    posterior = normalize_log_scores(adjusted)
    if anchor_prior is not None:
        posterior = blend_probabilities(anchor_prior, posterior, update_weight)
    return apply_probability_floor(posterior, floor)


def row_normalize(matrix: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {row: normalize_probabilities(values) for row, values in matrix.items()}
