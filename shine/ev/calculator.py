"""Expected-value calculator and tier assignment.

Combines adjusted probabilities across all legs, applies the correlation
factor, computes parlay decimal odds, and determines EV and tier.

EV formula:
    true_prob  = product(leg.prob for each leg) × correlation_factor
    decimal    = product(leg.decimal_odds for each leg)
    implied    = 1 / decimal
    ev         = (true_prob × decimal) − 1

Tier thresholds are defined in config.EV_TIERS.
"""

from __future__ import annotations
import math
from shine.config import EV_TIERS
from shine.odds.models import Parlay, ParlayLeg
from shine.correlation.engine import correlation_factor


def calculate_ev(parlay: Parlay) -> Parlay:
    """Fill in true_prob, implied_prob, decimal_odds, ev, tier, and
    correlation_factor on the given Parlay object."""
    if not parlay.legs:
        return parlay

    raw_prob = math.prod(leg.prob for leg in parlay.legs)
    corr = correlation_factor(parlay.legs)
    parlay.correlation_factor = corr

    parlay.true_prob = max(1e-12, min(1.0, raw_prob * corr))

    parlay.decimal_odds = math.prod(leg.decimal_odds for leg in parlay.legs)
    parlay.implied_prob = 1.0 / parlay.decimal_odds if parlay.decimal_odds > 0 else 0

    parlay.ev = (parlay.true_prob * parlay.decimal_odds) - 1.0

    parlay.tier = _assign_tier(parlay.ev)
    return parlay


def _assign_tier(ev: float) -> str:
    for tier, threshold in EV_TIERS.items():
        if ev >= threshold:
            return tier
    return "D"
