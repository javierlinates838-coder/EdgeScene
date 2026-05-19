from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


def implied_probability_from_decimal(decimal_odds: float) -> float:
    if decimal_odds <= 1.0:
        raise ValueError(f"Decimal odds must be greater than 1.0, got {decimal_odds}")
    return 1.0 / decimal_odds


def remove_vig_from_outcomes(decimal_odds: Sequence[float]) -> List[float]:
    if not decimal_odds:
        raise ValueError("At least one outcome is required.")
    implied = [implied_probability_from_decimal(odd) for odd in decimal_odds]
    total = sum(implied)
    if total <= 0:
        raise ValueError("Total implied probability must be positive.")
    return [p / total for p in implied]


def parlay_probability(probabilities: Iterable[float]) -> float:
    result = 1.0
    for p in probabilities:
        if p < 0 or p > 1:
            raise ValueError(f"Probability must be between 0 and 1, got {p}")
        result *= p
    return result


def expected_value(model_probability: float, decimal_payout_multiple: float) -> float:
    if decimal_payout_multiple <= 1.0:
        raise ValueError("Parlay decimal payout multiple must be greater than 1.0.")
    # EV on a 1-unit stake.
    return (model_probability * (decimal_payout_multiple - 1.0)) - (1.0 - model_probability)


def ev_tier(ev: float) -> str:
    if ev >= 0.20:
        return "S"
    if ev >= 0.12:
        return "A"
    if ev >= 0.06:
        return "B"
    if ev >= 0.0:
        return "C"
    return "D"


def average_no_vig_probability(selection_odds: Sequence[float], opposing_odds: Sequence[float]) -> Tuple[float, float]:
    """Return average no-vig probs for selection and opposition."""
    if not selection_odds or not opposing_odds:
        raise ValueError("Need both selection and opposing prices.")
    paired = min(len(selection_odds), len(opposing_odds))
    selection_probs: List[float] = []
    opposition_probs: List[float] = []
    for i in range(paired):
        no_vig = remove_vig_from_outcomes([selection_odds[i], opposing_odds[i]])
        selection_probs.append(no_vig[0])
        opposition_probs.append(no_vig[1])
    return sum(selection_probs) / paired, sum(opposition_probs) / paired
