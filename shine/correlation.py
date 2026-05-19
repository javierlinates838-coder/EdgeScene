from __future__ import annotations

from itertools import combinations
from typing import List

from .models import ParlayLeg

# The score is translated into a multiplier: 1 + score.
# Positive means legs support each other; negative means interference.
SAME_SPORT_BASE_CORRELATION = {
    "basketball_nba": 0.03,
    "americanfootball_nfl": 0.025,
    "soccer": 0.02,
    "esports_cs2": 0.03,
    "esports_lol": 0.03,
    "esports_valorant": 0.03,
    "mma_mixed_martial_arts": 0.01,
    "baseball_mlb": 0.015,
    "icehockey_nhl": 0.015,
}


def _sport_family(sport_key: str) -> str:
    if sport_key.startswith("soccer"):
        return "soccer"
    return sport_key


def _pair_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> float:
    family_a = _sport_family(leg_a.sport_key)
    family_b = _sport_family(leg_b.sport_key)

    if leg_a.event_id == leg_b.event_id:
        # Same event moneyline picks against each other are strongly conflicting.
        if leg_a.pick != leg_b.pick:
            return -0.30
        return 0.12

    if family_a == family_b:
        return SAME_SPORT_BASE_CORRELATION.get(family_a, 0.012)

    # Small neutral cross-sport effect.
    return 0.003


def correlation_score(legs: List[ParlayLeg]) -> float:
    if len(legs) < 2:
        return 0.0
    total = 0.0
    pair_count = 0
    for leg_a, leg_b in combinations(legs, 2):
        total += _pair_correlation(leg_a, leg_b)
        pair_count += 1
    return total / pair_count if pair_count else 0.0


def correlation_multiplier(legs: List[ParlayLeg]) -> float:
    score = correlation_score(legs)
    # Keep the multiplier in a stable range.
    return max(0.65, min(1.30, 1.0 + score))
