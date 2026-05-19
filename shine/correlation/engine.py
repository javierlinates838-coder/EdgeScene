"""Correlation engine — models how parlay legs interact with each other.

Positive correlation between legs inflates combined probability (good for
parlays). Negative correlation deflates it (destroys parlay EV).

For each pair of legs in a parlay, we compute a pairwise correlation score
in [-1, 1]. The overall correlation factor is derived from the average
pairwise correlation and applied as a multiplier on the combined probability.

Sport-specific correlation drivers:
  NBA  — pace, defense rating, divisional matchups
  NFL  — script (game flow), weather, divisional
  Soccer — possession vs counter-attack, league matchups
  CS2  — map pool overlap, regional styles
  LoL  — draft meta, regional playstyle
  VAL  — agent comp, map pick tendencies
  UFC  — style matchups (grappler vs striker)
  MLB  — pitching matchups, ballpark factors
  NHL  — goaltending, special teams
"""

from __future__ import annotations
from itertools import combinations
from shine.odds.models import ParlayLeg

# ── Sport groupings for correlation ──────────────────────────────────────────
_SPORT_GROUPS: dict[str, str] = {
    "NBA": "basketball",
    "NFL": "football",
    "MLB": "baseball",
    "NHL": "hockey",
    "soccer": "soccer",
    "soccer_champions_league": "soccer",
    "soccer_mls": "soccer",
    "soccer_la_liga": "soccer",
    "soccer_bundesliga": "soccer",
    "soccer_serie_a": "soccer",
    "soccer_ligue_one": "soccer",
    "CS2": "esports_fps",
    "VAL": "esports_fps",
    "LoL": "esports_moba",
    "UFC": "combat",
}

# Base same-sport correlation (two legs from the same sport naturally share
# some variance — e.g. slate-wide pace in NBA, weather in NFL).
SAME_SPORT_BASE: dict[str, float] = {
    "basketball": 0.08,
    "football": 0.10,
    "baseball": 0.04,
    "hockey": 0.05,
    "soccer": 0.06,
    "esports_fps": 0.07,
    "esports_moba": 0.06,
    "combat": 0.02,
}

# Cross-sport correlation is near zero (independent events).
CROSS_SPORT_CORR = 0.0

# Same-league bump (divisional / conference effects).
SAME_LEAGUE_BUMP = 0.04

# Same-game correlation (if two legs share the same game_id, e.g. different
# markets — but Shine is moneyline only, so this is a safeguard).
SAME_GAME_CORR = 0.30


def _sport_group(sport: str) -> str:
    return _SPORT_GROUPS.get(sport, "other")


def pairwise_correlation(a: ParlayLeg, b: ParlayLeg) -> float:
    """Estimate correlation between two parlay legs in [-1, 1]."""
    if a.game.id == b.game.id:
        return SAME_GAME_CORR

    group_a = _sport_group(a.sport)
    group_b = _sport_group(b.sport)

    if group_a != group_b:
        return CROSS_SPORT_CORR

    base = SAME_SPORT_BASE.get(group_a, 0.03)

    if a.game.league == b.game.league:
        base += SAME_LEAGUE_BUMP

    _shared_teams = {a.game.home.name.lower(), a.game.away.name.lower()} & {
        b.game.home.name.lower(),
        b.game.away.name.lower(),
    }
    if _shared_teams:
        base += 0.15

    return max(-1.0, min(1.0, base))


def correlation_factor(legs: list[ParlayLeg]) -> float:
    """Compute a single multiplicative factor for a parlay's combined probability.

    factor > 1 → positive correlation → parlay is better than independent
    factor < 1 → negative correlation → parlay EV is destroyed
    factor = 1 → legs are independent

    The formula converts average pairwise correlation into a multiplier:
        factor = 1 + (avg_corr * scaling)
    where scaling grows with the number of legs (more legs → correlation
    matters more).
    """
    if len(legs) < 2:
        return 1.0

    pairs = list(combinations(legs, 2))
    avg_corr = sum(pairwise_correlation(a, b) for a, b in pairs) / len(pairs)

    scaling = 0.5 + 0.1 * len(legs)
    factor = 1.0 + avg_corr * scaling

    return max(0.50, min(1.50, factor))
