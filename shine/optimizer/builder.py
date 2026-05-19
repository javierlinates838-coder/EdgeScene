"""Parlay builder — selects the best leg combinations from available games.

Strategy:
  1. Filter out games where neither side meets MIN_LEG_PROB.
  2. For every eligible side, create a candidate ParlayLeg.
  3. Generate all k-leg combinations for k in [MIN_LEGS .. MAX_LEGS].
  4. Score each combo via the EV calculator.
  5. Return the top-N parlays sorted by EV (descending).

To keep runtime tractable when there are many eligible legs, we cap the
candidate pool and use a greedy heuristic for larger k.
"""

from __future__ import annotations
from itertools import combinations
from typing import Optional

from shine.config import MIN_LEGS, MAX_LEGS, MIN_LEG_PROB
from shine.odds.models import Game, ParlayLeg, Parlay
from shine.ev.calculator import calculate_ev


MAX_CANDIDATES = 40  # cap to keep combos feasible
MAX_COMBOS_PER_K = 10_000
TOP_N = 20


def _make_leg(game: Game, pick_home: bool) -> ParlayLeg:
    side = game.home if pick_home else game.away
    return ParlayLeg(
        game=game,
        pick=side.name,
        prob=side.true_prob,
        american_odds=side.american_odds,
        bookmaker=game.bookmaker,
        sport=game.sport,
    )


def _eligible_legs(games: list[Game]) -> list[ParlayLeg]:
    """Build candidate legs from all games, keeping only those above MIN_LEG_PROB."""
    legs: list[ParlayLeg] = []
    for g in games:
        if g.home.true_prob >= MIN_LEG_PROB:
            legs.append(_make_leg(g, pick_home=True))
        if g.away.true_prob >= MIN_LEG_PROB:
            legs.append(_make_leg(g, pick_home=False))
    legs.sort(key=lambda l: l.prob, reverse=True)
    return legs[:MAX_CANDIDATES]


def _no_same_game(combo: tuple[ParlayLeg, ...]) -> bool:
    """Ensure we don't pick both sides of the same game."""
    ids = [leg.game.id for leg in combo]
    return len(ids) == len(set(ids))


def build_parlays(
    games: list[Game],
    min_legs: int = MIN_LEGS,
    max_legs: int = MAX_LEGS,
    top_n: int = TOP_N,
) -> list[Parlay]:
    """Generate and rank the best parlays from a pool of games."""
    candidates = _eligible_legs(games)
    if len(candidates) < min_legs:
        return []

    all_parlays: list[Parlay] = []

    for k in range(min_legs, min(max_legs, len(candidates)) + 1):
        count = 0
        for combo in combinations(candidates, k):
            if count >= MAX_COMBOS_PER_K:
                break
            if not _no_same_game(combo):
                count += 1
                continue
            p = Parlay(legs=list(combo))
            calculate_ev(p)
            all_parlays.append(p)
            count += 1

    all_parlays.sort(key=lambda p: p.ev, reverse=True)
    return all_parlays[:top_n]
