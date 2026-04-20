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


def combine_prior_and_channels(
    prior: dict[str, float],
    weighted_channel_scores: list[dict[str, float]],
) -> dict[str, float]:
    log_scores = {key: math.log(max(value, 1e-8)) for key, value in prior.items()}
    for channel in weighted_channel_scores:
        for regime_id, contribution in channel.items():
            log_scores[regime_id] += contribution
    return normalize_log_scores(log_scores)


def row_normalize(matrix: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {row: normalize_probabilities(values) for row, values in matrix.items()}
