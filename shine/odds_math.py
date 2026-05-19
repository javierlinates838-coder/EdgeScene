"""Probability and odds helpers for moneyline EV math."""

from __future__ import annotations

import math


def american_to_probability(price: int | float) -> float:
    """Convert American odds into implied probability."""
    if price == 0:
        raise ValueError("American odds cannot be zero")
    if price > 0:
        return 100.0 / (float(price) + 100.0)
    return abs(float(price)) / (abs(float(price)) + 100.0)


def american_to_decimal(price: int | float) -> float:
    """Convert American odds into decimal odds."""
    if price == 0:
        raise ValueError("American odds cannot be zero")
    if price > 0:
        return 1.0 + (float(price) / 100.0)
    return 1.0 + (100.0 / abs(float(price)))


def probability_to_american(probability: float) -> int:
    """Convert a probability to a rounded American fair price."""
    probability = clamp_probability(probability)
    if probability >= 0.5:
        return int(round(-100.0 * probability / (1.0 - probability)))
    return int(round(100.0 * (1.0 - probability) / probability))


def no_vig_probabilities(implied_probabilities: dict[str, float]) -> dict[str, float]:
    """Normalize implied probabilities so the market sums to 100%."""
    total = sum(implied_probabilities.values())
    if total <= 0:
        raise ValueError("Cannot remove vig from probabilities with non-positive total")
    return {name: probability / total for name, probability in implied_probabilities.items()}


def clamp_probability(probability: float, floor: float = 0.001, ceiling: float = 0.999) -> float:
    return max(floor, min(ceiling, probability))


def add_logit_delta(probability: float, delta: float) -> float:
    """Move a probability by a log-odds delta without leaving the 0-1 range."""
    probability = clamp_probability(probability)
    logit = math.log(probability / (1.0 - probability))
    adjusted = 1.0 / (1.0 + math.exp(-(logit + delta)))
    return clamp_probability(adjusted)


def expected_value(true_probability: float, decimal_odds: float) -> float:
    """Return ROI per $1 staked."""
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1")
    return (true_probability * decimal_odds) - 1.0


def product(values: list[float]) -> float:
    result = 1.0
    for value in values:
        result *= value
    return result
