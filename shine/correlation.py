from __future__ import annotations

from itertools import combinations
from typing import List, Sequence, Tuple

from .models import CorrelationResult, LegInput


def correlation_multiplier(legs: Sequence[LegInput]) -> CorrelationResult:
    multiplier = 1.0
    notes: List[str] = []

    for left, right in combinations(legs, 2):
        pair_mult, note = _pairwise_correlation(left, right)
        multiplier *= pair_mult
        if note:
            notes.append(note)

    # Keep multiplier in practical bounds.
    multiplier = max(0.70, min(1.30, multiplier))
    return CorrelationResult(multiplier=multiplier, pairwise_notes=notes)


def _pairwise_correlation(left: LegInput, right: LegInput) -> Tuple[float, str]:
    if left.event_id == right.event_id and left.selection == right.selection:
        return 1.05, "duplicate-same-side event exposure increased positive correlation"

    if left.sport_key != right.sport_key:
        return 1.0, ""

    tags = {tag.lower() for tag in left.tags}.union({tag.lower() for tag in right.tags})
    sport = left.sport_key.lower()

    if "basketball" in sport or "nba" in sport:
        if {"pace_up", "weak_defense"} <= tags:
            return 1.04, "nba pace + weak-defense tag alignment"
        if {"slow_pace", "elite_defense"} <= tags:
            return 0.97, "nba slow pace and elite defense reduced parlay hit rate"

    if "americanfootball" in sport or "nfl" in sport:
        if {"run_heavy", "bad_weather"} <= tags:
            return 0.96, "nfl run-heavy plus weather suppresses scoring variance"
        if {"script_positive", "favorable_weather"} <= tags:
            return 1.03, "nfl game-script and weather support favorites"

    if "soccer" in sport:
        if {"counterattack_edge", "possession_gap"} <= tags:
            return 1.03, "soccer possession and counter mismatch signal"
        if {"derby_volatility"} <= tags:
            return 0.95, "soccer derby volatility penalty"

    if "cs2" in sport:
        if {"map_pool_edge", "ct_side_strength"} <= tags:
            return 1.04, "cs2 map pool plus side-strength synergy"

    if "lol" in sport:
        if {"draft_edge", "early_objective_control"} <= tags:
            return 1.04, "lol draft and objective-control synergy"

    if "valorant" in sport or "val" in sport:
        if {"agent_comp_edge", "map_pool_edge"} <= tags:
            return 1.04, "val agent comp and map pool correlation"

    if "ufc" in sport or "mma" in sport:
        if {"style_mismatch"} <= tags:
            return 1.03, "ufc style mismatch confidence boost"

    return 1.0, ""
