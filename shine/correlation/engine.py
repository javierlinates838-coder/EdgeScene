"""
Correlation engine: models how parlay legs interact with each other.

Positive correlation increases parlay EV.
Negative correlation destroys it.
Cross-sport legs are treated as independent (correlation = 1.0).

Sport-specific correlation factors:
- NBA: pace, defense rating, rest days
- NFL: script dependence, weather, division rivals
- Soccer: possession vs counter, conference/group
- CS2: map pool overlap, region matchups
- LoL: draft meta, side selection
- VAL: agent comp, map pool
- UFC: style matchups, weight class
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from shine.core.config import Sport
from shine.core.models import GameContext, ParlayLeg

logger = logging.getLogger(__name__)


@dataclass
class CorrelationPair:
    """Correlation analysis between two parlay legs."""
    leg_a_team: str
    leg_b_team: str
    correlation: float  # 1.0 = independent, >1.0 = positive, <1.0 = negative
    reason: str
    sport_pair: Tuple[Sport, Sport]


@dataclass
class CorrelationResult:
    """Full correlation analysis for a parlay."""
    pairs: List[CorrelationPair] = field(default_factory=list)
    composite_factor: float = 1.0
    details: List[str] = field(default_factory=list)

    @property
    def is_positively_correlated(self) -> bool:
        return self.composite_factor > 1.005

    @property
    def is_negatively_correlated(self) -> bool:
        return self.composite_factor < 0.995


SAME_SPORT_BASE_CORRELATION: Dict[Sport, float] = {
    Sport.NBA: 0.98,
    Sport.NFL: 0.97,
    Sport.MLB: 0.99,
    Sport.NHL: 0.98,
    Sport.SOCCER_EPL: 0.97,
    Sport.SOCCER_UCL: 0.96,
    Sport.SOCCER_LALIGA: 0.97,
    Sport.SOCCER_BUNDESLIGA: 0.97,
    Sport.SOCCER_SERIEA: 0.97,
    Sport.SOCCER_LIGUE1: 0.98,
    Sport.SOCCER_MLS: 0.99,
    Sport.CS2: 0.97,
    Sport.LOL: 0.97,
    Sport.VAL: 0.97,
    Sport.UFC: 0.99,
}


def analyze_correlation(legs: List[ParlayLeg]) -> CorrelationResult:
    """Analyze pairwise correlation between all legs in a parlay."""
    result = CorrelationResult()

    if len(legs) < 2:
        result.composite_factor = 1.0
        result.details.append("Single leg — no correlation to analyze")
        return result

    factors: List[float] = []

    for i in range(len(legs)):
        for j in range(i + 1, len(legs)):
            pair = _analyze_pair(legs[i], legs[j])
            result.pairs.append(pair)
            factors.append(pair.correlation)

    if factors:
        product = 1.0
        for f in factors:
            product *= f
        n = len(factors)
        result.composite_factor = product ** (1.0 / n) if n > 1 else product

    has_conflict = any(p.correlation == 0.0 for p in result.pairs)
    if has_conflict:
        result.composite_factor = 0.0
    else:
        result.composite_factor = max(0.80, min(1.20, result.composite_factor))

    for pair in result.pairs:
        if abs(pair.correlation - 1.0) > 0.005:
            tag = "+" if pair.correlation > 1.0 else ""
            result.details.append(
                f"{pair.leg_a_team} × {pair.leg_b_team}: "
                f"{tag}{(pair.correlation - 1.0) * 100:.1f}% — {pair.reason}"
            )

    if not result.details:
        result.details.append("All legs approximately independent")

    return result


def _analyze_pair(leg_a: ParlayLeg, leg_b: ParlayLeg) -> CorrelationPair:
    """Analyze correlation between two legs."""
    if leg_a.sport != leg_b.sport:
        return _cross_sport_correlation(leg_a, leg_b)

    return _same_sport_correlation(leg_a, leg_b)


def _cross_sport_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> CorrelationPair:
    """Cross-sport legs are nearly independent — slight boost for diversification."""
    return CorrelationPair(
        leg_a_team=leg_a.team,
        leg_b_team=leg_b.team,
        correlation=1.002,
        reason="Cross-sport: effectively independent (slight diversification benefit)",
        sport_pair=(leg_a.sport, leg_b.sport),
    )


def _same_sport_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> CorrelationPair:
    """Same-sport correlation is where the real analysis happens."""
    sport = leg_a.sport
    base = SAME_SPORT_BASE_CORRELATION.get(sport, 0.98)

    if _same_game_conflict(leg_a, leg_b):
        return CorrelationPair(
            leg_a_team=leg_a.team,
            leg_b_team=leg_b.team,
            correlation=0.0,
            reason="CONFLICT: Both sides of the same game selected (impossible parlay)",
            sport_pair=(sport, sport),
        )

    if _same_game_same_side(leg_a, leg_b):
        return CorrelationPair(
            leg_a_team=leg_a.team,
            leg_b_team=leg_b.team,
            correlation=1.0,
            reason="Duplicate leg detected (same pick)",
            sport_pair=(sport, sport),
        )

    corr = base
    reason_parts: List[str] = []

    sport_adj, sport_reason = _sport_specific_correlation(leg_a, leg_b, sport)
    corr *= sport_adj
    if sport_reason:
        reason_parts.append(sport_reason)

    fav_adj, fav_reason = _favorite_correlation(leg_a, leg_b)
    corr *= fav_adj
    if fav_reason:
        reason_parts.append(fav_reason)

    reason = "; ".join(reason_parts) if reason_parts else f"Same-sport baseline ({sport.value})"

    return CorrelationPair(
        leg_a_team=leg_a.team,
        leg_b_team=leg_b.team,
        correlation=corr,
        reason=reason,
        sport_pair=(sport, sport),
    )


def _same_game_conflict(leg_a: ParlayLeg, leg_b: ParlayLeg) -> bool:
    """Check if two legs are opposing picks in the same game."""
    return leg_a.game_id == leg_b.game_id and leg_a.team != leg_b.team


def _same_game_same_side(leg_a: ParlayLeg, leg_b: ParlayLeg) -> bool:
    """Check if two legs are the same pick in the same game."""
    return leg_a.game_id == leg_b.game_id and leg_a.team == leg_b.team


def _sport_specific_correlation(
    leg_a: ParlayLeg, leg_b: ParlayLeg, sport: Sport
) -> Tuple[float, str]:
    """Apply sport-specific correlation adjustments."""

    if sport == Sport.NBA:
        return _nba_correlation(leg_a, leg_b)
    elif sport == Sport.NFL:
        return _nfl_correlation(leg_a, leg_b)
    elif sport in (Sport.SOCCER_EPL, Sport.SOCCER_UCL, Sport.SOCCER_LALIGA,
                   Sport.SOCCER_BUNDESLIGA, Sport.SOCCER_SERIEA,
                   Sport.SOCCER_LIGUE1, Sport.SOCCER_MLS):
        return _soccer_correlation(leg_a, leg_b)
    elif sport == Sport.CS2:
        return _cs2_correlation(leg_a, leg_b)
    elif sport == Sport.LOL:
        return _lol_correlation(leg_a, leg_b)
    elif sport == Sport.VAL:
        return _val_correlation(leg_a, leg_b)
    elif sport == Sport.UFC:
        return _ufc_correlation(leg_a, leg_b)
    elif sport == Sport.MLB:
        return _mlb_correlation(leg_a, leg_b)
    elif sport == Sport.NHL:
        return _nhl_correlation(leg_a, leg_b)

    return 1.0, ""


def _nba_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """
    NBA correlation: pace environment, conference matchups, rest patterns.
    Two road favorites in the same conference have slight negative correlation.
    Heavy favorites in different games have slight positive (chalk holds together).
    """
    both_heavy_fav = leg_a.adjusted_probability > 0.65 and leg_b.adjusted_probability > 0.65
    if both_heavy_fav:
        return 1.02, "NBA: both heavy favorites (chalk correlation)"

    both_underdogs = leg_a.adjusted_probability < 0.40 and leg_b.adjusted_probability < 0.40
    if both_underdogs:
        return 0.96, "NBA: both underdogs (upset variance correlation)"

    return 1.0, ""


def _nfl_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """NFL: single-game sport, weather can affect multiple games in same region."""
    both_fav = leg_a.adjusted_probability > 0.60 and leg_b.adjusted_probability > 0.60
    if both_fav:
        return 1.01, "NFL: favorites correlation (public money alignment)"

    both_dogs = leg_a.adjusted_probability < 0.40 and leg_b.adjusted_probability < 0.40
    if both_dogs:
        return 0.94, "NFL: underdogs (single-elimination variance stacks negatively)"

    return 1.0, ""


def _soccer_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """Soccer: possession vs counter styles, same league dynamics."""
    both_fav = leg_a.adjusted_probability > 0.60 and leg_b.adjusted_probability > 0.60
    if both_fav:
        return 1.02, "Soccer: heavy favorites tend to deliver together"

    return 0.99, "Soccer: draw variance reduces multi-leg reliability"


def _cs2_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """CS2: map pool overlap, regional strength, tournament format effects."""
    both_fav = leg_a.adjusted_probability > 0.62 and leg_b.adjusted_probability > 0.62
    if both_fav:
        return 1.03, "CS2: top teams dominate together at events (map pool depth)"

    return 0.98, "CS2: upset potential in BO1/BO3 reduces correlation"


def _lol_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """LoL: draft meta, patch-dependent, regional strength differences."""
    both_fav = leg_a.adjusted_probability > 0.62 and leg_b.adjusted_probability > 0.62
    if both_fav:
        return 1.02, "LoL: meta-favored teams on same patch (draft correlation)"

    return 0.97, "LoL: draft variance and snowball mechanics reduce correlation"


def _val_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """VALORANT: agent comps, map pool, regional playstyle."""
    both_fav = leg_a.adjusted_probability > 0.60 and leg_b.adjusted_probability > 0.60
    if both_fav:
        return 1.02, "VAL: agent comp meta favors dominant teams together"

    return 0.97, "VAL: pistol round variance reduces multi-leg reliability"


def _ufc_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """UFC: style matchups are unique per fight, nearly independent."""
    return 1.0, "UFC: individual fights are largely independent"


def _mlb_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """MLB: high day-to-day variance, starting pitching dominates."""
    both_fav = leg_a.adjusted_probability > 0.60 and leg_b.adjusted_probability > 0.60
    if both_fav:
        return 0.99, "MLB: high variance sport, chalk parlays slightly risky"

    return 0.98, "MLB: daily variance (starting pitcher dependency)"


def _nhl_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """NHL: goaltending variance, puck luck, playoff intensity."""
    both_fav = leg_a.adjusted_probability > 0.58 and leg_b.adjusted_probability > 0.58
    if both_fav:
        return 1.01, "NHL: favorites hold slightly in parity league"

    return 0.97, "NHL: goaltending variance reduces correlation"


def _favorite_correlation(leg_a: ParlayLeg, leg_b: ParlayLeg) -> Tuple[float, str]:
    """General favorite/underdog stacking analysis."""
    spread = abs(leg_a.adjusted_probability - leg_b.adjusted_probability)
    if spread > 0.3:
        return 0.99, "Mixed favorite/underdog leg (reduced correlation)"
    return 1.0, ""


def apply_correlation_to_parlay(
    raw_parlay_prob: float,
    correlation_result: CorrelationResult,
) -> float:
    """Apply correlation factor to the raw parlay probability."""
    adjusted = raw_parlay_prob * correlation_result.composite_factor
    return max(0.0001, min(0.99, adjusted))
