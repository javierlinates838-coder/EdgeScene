"""
Intelligence layer: pressure performance, big-competition adjustments.

This is what makes Shine smarter than every other parlay builder —
it knows that teams perform differently on big stages.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from shine.core.config import Sport
from shine.core.models import GameContext
from shine.data.big_competitions import (
    BigCompetition,
    PressureProfile,
    detect_big_competition,
    get_pressure_profile,
)

logger = logging.getLogger(__name__)

MAX_SINGLE_ADJUSTMENT = 0.08
MIN_PROBABILITY = 0.02
MAX_PROBABILITY = 0.98


@dataclass
class IntelligenceResult:
    """Result of the intelligence adjustment for one team."""
    team: str
    base_probability: float
    adjusted_probability: float
    adjustments: List[str] = field(default_factory=list)
    total_adjustment: float = 0.0


def apply_intelligence(
    team_a: str,
    team_b: str,
    prob_a: float,
    prob_b: float,
    context: GameContext,
) -> Tuple[IntelligenceResult, IntelligenceResult]:
    """
    Apply the full intelligence layer to a matchup.
    Adjusts probabilities based on:
    - Big competition detection
    - Pressure performance profiles
    - Clutch ratings
    """
    result_a = IntelligenceResult(team=team_a, base_probability=prob_a, adjusted_probability=prob_a)
    result_b = IntelligenceResult(team=team_b, base_probability=prob_b, adjusted_probability=prob_b)

    competition = detect_big_competition(
        context.sport,
        context.playoff_round or "",
        [context.season_phase, context.venue or ""],
    )

    if competition:
        _apply_competition_boost(result_a, result_b, competition, context)

    _apply_pressure_profiles(result_a, result_b, context)
    _apply_sport_specific_intel(result_a, result_b, context)

    _normalize_pair(result_a, result_b)

    return result_a, result_b


def _apply_competition_boost(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    competition: BigCompetition,
    context: GameContext,
) -> None:
    """Apply big-competition pressure adjustments."""
    profile_a = get_pressure_profile(result_a.team)
    profile_b = get_pressure_profile(result_b.team)

    base_boost = (competition.pressure_multiplier - 1.0) * 0.5

    if profile_a:
        adj_a = base_boost * (profile_a.clutch_rating - 1.0) * 4.0
        adj_a = max(-MAX_SINGLE_ADJUSTMENT, min(MAX_SINGLE_ADJUSTMENT, adj_a))
        result_a.adjusted_probability += adj_a
        result_a.total_adjustment += adj_a
        tag = "boost" if adj_a > 0 else "penalty"
        result_a.adjustments.append(
            f"Big-stage {tag}: {adj_a:+.3f} ({competition.name}, clutch={profile_a.clutch_rating:.2f})"
        )

    if profile_b:
        adj_b = base_boost * (profile_b.clutch_rating - 1.0) * 4.0
        adj_b = max(-MAX_SINGLE_ADJUSTMENT, min(MAX_SINGLE_ADJUSTMENT, adj_b))
        result_b.adjusted_probability += adj_b
        result_b.total_adjustment += adj_b
        tag = "boost" if adj_b > 0 else "penalty"
        result_b.adjustments.append(
            f"Big-stage {tag}: {adj_b:+.3f} ({competition.name}, clutch={profile_b.clutch_rating:.2f})"
        )

    if not profile_a and not profile_b:
        result_a.adjustments.append(f"Big competition detected: {competition.name} (no profile data)")
        result_b.adjustments.append(f"Big competition detected: {competition.name} (no profile data)")


def _apply_pressure_profiles(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """Apply baseline pressure profile adjustments even outside big competitions."""
    profile_a = get_pressure_profile(result_a.team)
    profile_b = get_pressure_profile(result_b.team)

    if context.is_playoff or context.is_major:
        return

    if profile_a and profile_a.clutch_rating != 1.0:
        baseline_adj = (profile_a.clutch_rating - 1.0) * 0.02
        baseline_adj = max(-0.02, min(0.02, baseline_adj))
        result_a.adjusted_probability += baseline_adj
        result_a.total_adjustment += baseline_adj
        if abs(baseline_adj) > 0.001:
            result_a.adjustments.append(
                f"Pressure baseline: {baseline_adj:+.3f} (clutch={profile_a.clutch_rating:.2f})"
            )

    if profile_b and profile_b.clutch_rating != 1.0:
        baseline_adj = (profile_b.clutch_rating - 1.0) * 0.02
        baseline_adj = max(-0.02, min(0.02, baseline_adj))
        result_b.adjusted_probability += baseline_adj
        result_b.total_adjustment += baseline_adj
        if abs(baseline_adj) > 0.001:
            result_b.adjustments.append(
                f"Pressure baseline: {baseline_adj:+.3f} (clutch={profile_b.clutch_rating:.2f})"
            )


def _apply_sport_specific_intel(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """Sport-specific intelligence that doesn't come from pressure profiles."""
    sport = context.sport

    if sport == Sport.NBA:
        if context.is_playoff:
            _nba_playoff_intel(result_a, result_b, context)
    elif sport == Sport.NFL:
        if context.is_playoff:
            _nfl_playoff_intel(result_a, result_b, context)
    elif sport in (Sport.CS2, Sport.LOL, Sport.VAL):
        _esports_intel(result_a, result_b, context)
    elif sport == Sport.UFC:
        _ufc_intel(result_a, result_b, context)


def _nba_playoff_intel(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """NBA playoff-specific intelligence: experience matters more, variance drops."""
    exp_adj = 0.01
    if context.home_team == result_a.team:
        result_a.adjusted_probability += exp_adj
        result_a.total_adjustment += exp_adj
        result_a.adjustments.append(f"NBA playoff home boost: +{exp_adj:.3f}")
    elif context.home_team == result_b.team:
        result_b.adjusted_probability += exp_adj
        result_b.total_adjustment += exp_adj
        result_b.adjustments.append(f"NBA playoff home boost: +{exp_adj:.3f}")


def _nfl_playoff_intel(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """NFL single-elimination increases pressure impact."""
    pressure_amp = 0.015
    if context.home_team == result_a.team:
        result_a.adjusted_probability += pressure_amp
        result_a.total_adjustment += pressure_amp
        result_a.adjustments.append(f"NFL playoff home-field: +{pressure_amp:.3f}")
    elif context.home_team == result_b.team:
        result_b.adjusted_probability += pressure_amp
        result_b.total_adjustment += pressure_amp
        result_b.adjustments.append(f"NFL playoff home-field: +{pressure_amp:.3f}")


def _esports_intel(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """Esports: international events have higher variance, host-region advantage."""
    if context.is_international:
        host_boost = 0.012
        if context.venue_country:
            for team, adj in [(result_a, host_boost), (result_b, host_boost)]:
                team.adjustments.append(f"International event context: no region-specific boost applied")


def _ufc_intel(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
    context: GameContext,
) -> None:
    """UFC: PPV main events have different dynamics — more cautious fighting early."""
    if context.is_major:
        cautiousness = 0.005
        for team in [result_a, result_b]:
            if team.adjusted_probability > 0.5:
                team.adjusted_probability += cautiousness
                team.total_adjustment += cautiousness
                team.adjustments.append(f"UFC PPV favorite bump: +{cautiousness:.3f}")


def _normalize_pair(
    result_a: IntelligenceResult,
    result_b: IntelligenceResult,
) -> None:
    """Ensure adjusted probabilities sum to 1.0 and are within bounds."""
    result_a.adjusted_probability = max(MIN_PROBABILITY, min(MAX_PROBABILITY, result_a.adjusted_probability))
    result_b.adjusted_probability = max(MIN_PROBABILITY, min(MAX_PROBABILITY, result_b.adjusted_probability))

    total = result_a.adjusted_probability + result_b.adjusted_probability
    if abs(total - 1.0) > 0.001:
        result_a.adjusted_probability /= total
        result_b.adjusted_probability /= total
