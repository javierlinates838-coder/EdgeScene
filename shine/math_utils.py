from __future__ import annotations

from itertools import combinations
from math import prod
from typing import Iterable, List, Sequence, Tuple


def american_to_implied_probability(american_odds: int) -> float:
    """Convert American odds into implied probability with vig."""
    if american_odds == 0:
        raise ValueError("American odds cannot be zero.")

    if american_odds > 0:
        return 100 / (american_odds + 100)
    return (-american_odds) / ((-american_odds) + 100)


def american_to_decimal_multiplier(american_odds: int) -> float:
    """Convert American odds into decimal odds multiplier."""
    if american_odds == 0:
        raise ValueError("American odds cannot be zero.")
    if american_odds > 0:
        return 1 + (american_odds / 100)
    return 1 + (100 / (-american_odds))


def remove_vig(implied_probabilities: Sequence[float]) -> List[float]:
    """Normalize implied probabilities so they sum to 1.0."""
    total = sum(implied_probabilities)
    if total <= 0:
        raise ValueError("Implied probabilities must sum to a positive value.")
    return [p / total for p in implied_probabilities]


def parlay_payout_multiplier(american_odds: Iterable[int]) -> float:
    """Product of decimal multipliers across all legs."""
    return prod(american_to_decimal_multiplier(odds) for odds in american_odds)


def generate_combinations(indices: Sequence[int], max_legs: int) -> List[Tuple[int, ...]]:
    """Generate all leg index combinations from 2 legs up to max_legs."""
    max_size = max(2, max_legs)
    output: List[Tuple[int, ...]] = []
    for size in range(2, min(max_size, len(indices)) + 1):
        output.extend(combinations(indices, size))
    return output
