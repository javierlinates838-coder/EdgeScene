"""EV / tier calculation for a parlay."""

from __future__ import annotations

from typing import List

from ..correlation.engine import CorrelationEngine
from ..models import Leg, Parlay, Tier


def build_parlay(legs: List[Leg], correlator: CorrelationEngine) -> Parlay:
    if not legs:
        raise ValueError("Cannot build a parlay with zero legs")

    combined_decimal = 1.0
    for leg in legs:
        combined_decimal *= leg.book_decimal

    naive, corr = correlator.apply(legs)
    book_implied = 1.0 / combined_decimal if combined_decimal else 0.0

    ev_pct = (corr * combined_decimal - 1.0) * 100.0
    tier = Tier.from_ev(ev_pct)

    notes = correlator.explain(legs)
    return Parlay(
        legs=legs,
        combined_decimal=combined_decimal,
        naive_prob=naive,
        correlated_prob=corr,
        book_implied=book_implied,
        ev_pct=ev_pct,
        tier=tier,
        correlation_score=correlator.average_rho(legs),
        notes=notes,
    )
