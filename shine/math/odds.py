"""Odds format conversions."""

from __future__ import annotations


def american_to_decimal(odds: int) -> float:
    """Convert American odds to decimal odds (gross multiplier including stake)."""
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    if odds > 0:
        return 1.0 + odds / 100.0
    return 1.0 + 100.0 / abs(odds)


def decimal_to_american(decimal: float) -> int:
    """Convert decimal odds to American odds, rounded to nearest integer."""
    if decimal <= 1.0:
        raise ValueError("Decimal odds must be > 1.0")
    if decimal >= 2.0:
        return int(round((decimal - 1.0) * 100.0))
    return int(round(-100.0 / (decimal - 1.0)))


def decimal_to_prob(decimal: float) -> float:
    """Convert decimal odds to implied probability (with vig)."""
    if decimal <= 0:
        return 0.0
    return 1.0 / decimal


def prob_to_decimal(prob: float) -> float:
    """Convert a true probability into decimal odds (fair line)."""
    if prob <= 0 or prob >= 1:
        raise ValueError("Probability must be in (0, 1)")
    return 1.0 / prob
