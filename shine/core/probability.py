"""Probability math: vig removal, implied-to-true conversion, parlay math."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


def american_to_implied(american: int) -> float:
    """Convert American odds to implied probability (0-1)."""
    if american > 0:
        return 100.0 / (american + 100.0)
    else:
        return abs(american) / (abs(american) + 100.0)


def implied_to_american(prob: float) -> int:
    """Convert implied probability (0-1) back to American odds."""
    if prob <= 0 or prob >= 1:
        raise ValueError(f"Probability must be between 0 and 1, got {prob}")
    if prob >= 0.5:
        return int(round(-prob * 100.0 / (1.0 - prob)))
    else:
        return int(round((1.0 - prob) * 100.0 / prob))


def decimal_to_implied(decimal_odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / decimal_odds


def remove_vig_power(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """
    Remove vig using the power method (multiplicative normalization).
    More accurate than additive for skewed lines.
    """
    total = prob_a + prob_b
    if total <= 1.0:
        return prob_a, prob_b

    k = math.log(2) / math.log(2 * total / (prob_a + prob_b))
    fair_a = prob_a ** k / (prob_a ** k + prob_b ** k)
    fair_b = 1.0 - fair_a
    return fair_a, fair_b


def remove_vig_additive(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """Remove vig via simple additive normalization."""
    total = prob_a + prob_b
    if total <= 1.0:
        return prob_a, prob_b
    return prob_a / total, prob_b / total


def remove_vig_shin(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """
    Shin method for vig removal — better for markets with insider information.
    Uses the Shin (1993) model to estimate fair probabilities.
    """
    total = prob_a + prob_b
    if total <= 1.0:
        return prob_a, prob_b

    z = _solve_shin_z(prob_a, prob_b)
    fair_a = (math.sqrt(z ** 2 + 4 * (1 - z) * prob_a ** 2 / total) - z) / (2 * (1 - z))
    fair_b = 1.0 - fair_a
    return max(0.001, fair_a), max(0.001, fair_b)


def _solve_shin_z(prob_a: float, prob_b: float, iterations: int = 50) -> float:
    """Iteratively solve for Shin's z parameter."""
    total = prob_a + prob_b
    z = (total - 1.0) / (total)
    for _ in range(iterations):
        new_z = 0.0
        for p in [prob_a, prob_b]:
            sq = math.sqrt(z ** 2 + 4 * (1 - z) * p ** 2 / total)
            new_z += (sq - z) / (2 * (1 - z))
        z_candidate = 1.0 - 1.0 / (new_z if new_z > 0 else 1.0)
        z = max(0.0, min(z_candidate, 0.5))
    return z


def remove_vig_best(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """
    Apply the best vig removal method based on market characteristics.
    Uses power method for most cases, Shin for heavily skewed lines.
    """
    skew = abs(prob_a - prob_b)
    if skew > 0.5:
        return remove_vig_shin(prob_a, prob_b)
    return remove_vig_power(prob_a, prob_b)


def median_probability(probabilities: List[float]) -> float:
    """Get the median of a list of probabilities from multiple books."""
    if not probabilities:
        return 0.5
    sorted_probs = sorted(probabilities)
    n = len(sorted_probs)
    if n % 2 == 1:
        return sorted_probs[n // 2]
    return (sorted_probs[n // 2 - 1] + sorted_probs[n // 2]) / 2.0


def parlay_probability(leg_probs: List[float]) -> float:
    """Calculate raw parlay probability (product of independent leg probs)."""
    result = 1.0
    for p in leg_probs:
        result *= p
    return result


def parlay_decimal_odds(leg_probs: List[float]) -> float:
    """Calculate fair decimal odds for a parlay."""
    prob = parlay_probability(leg_probs)
    if prob <= 0:
        return float("inf")
    return 1.0 / prob


def parlay_american_odds(leg_probs: List[float]) -> int:
    """Calculate fair American odds for a parlay."""
    prob = parlay_probability(leg_probs)
    return implied_to_american(prob)


def calculate_ev(true_prob: float, decimal_odds: float, stake: float = 1.0) -> float:
    """
    Calculate expected value.
    EV = (prob * payout) - stake
    """
    payout = stake * decimal_odds
    return (true_prob * payout) - stake


def calculate_ev_percent(true_prob: float, implied_prob: float) -> float:
    """
    Calculate EV as a percentage edge.
    Positive = you have an edge over the book.
    """
    if implied_prob <= 0:
        return 0.0
    return ((true_prob - implied_prob) / implied_prob) * 100.0


@dataclass
class VigAnalysis:
    """Analysis of the vig/juice on a market."""
    implied_a: float
    implied_b: float
    fair_a: float
    fair_b: float
    total_implied: float
    vig_percent: float
    method: str

    @classmethod
    def analyze(cls, odds_a: int, odds_b: int) -> "VigAnalysis":
        implied_a = american_to_implied(odds_a)
        implied_b = american_to_implied(odds_b)
        total = implied_a + implied_b
        vig = (total - 1.0) * 100.0
        fair_a, fair_b = remove_vig_best(implied_a, implied_b)
        method = "shin" if abs(implied_a - implied_b) > 0.5 else "power"
        return cls(
            implied_a=implied_a,
            implied_b=implied_b,
            fair_a=fair_a,
            fair_b=fair_b,
            total_implied=total,
            vig_percent=vig,
            method=method,
        )
