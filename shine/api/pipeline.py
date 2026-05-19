"""Shine v4 pipeline — the full engine in one call.

Steps:
  1. Fetch live odds from TheOddsAPI for every configured sport.
  2. Remove vig and compute true probabilities (done in Game.__post_init__).
  3. Apply big-stage intelligence adjustments.
  4. Apply environmental adjustments.
  5. Build and rank parlays using the optimizer.
  6. Return the top parlays with EV and tiers.
"""

from __future__ import annotations
from typing import Optional

from shine.odds.client import fetch_all_games, fetch_games
from shine.odds.models import Game, Parlay
from shine.intelligence.big_stage import apply_big_stage
from shine.environment.factors import apply_environment
from shine.optimizer.builder import build_parlays
from shine.config import SPORT_KEYS


def _adjust_games(games: list[Game]) -> list[Game]:
    """Run each game through the intelligence + environment layers."""
    for g in games:
        apply_big_stage(g)
        apply_environment(g)
    return games


def run(
    sports: Optional[list[str]] = None,
    min_legs: int = 2,
    max_legs: int = 6,
    top_n: int = 10,
) -> list[Parlay]:
    """Execute the full Shine v4 pipeline.

    Args:
        sports:   List of sport labels to include (e.g. ["NBA", "NFL"]).
                  If None, all configured sports are used.
        min_legs: Minimum legs per parlay.
        max_legs: Maximum legs per parlay.
        top_n:    Number of top parlays to return.

    Returns:
        Sorted list of Parlay objects (best EV first).
    """
    if sports:
        games: list[Game] = []
        for label in sports:
            key = SPORT_KEYS.get(label)
            if key:
                try:
                    games.extend(fetch_games(key, label))
                except Exception:
                    pass
    else:
        games = fetch_all_games()

    if not games:
        return []

    games = _adjust_games(games)
    return build_parlays(games, min_legs=min_legs, max_legs=max_legs, top_n=top_n)


def run_from_games(
    games: list[Game],
    min_legs: int = 2,
    max_legs: int = 6,
    top_n: int = 10,
) -> list[Parlay]:
    """Run the pipeline on an already-fetched list of games (useful for testing)."""
    games = _adjust_games(games)
    return build_parlays(games, min_legs=min_legs, max_legs=max_legs, top_n=top_n)
