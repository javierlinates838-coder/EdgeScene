"""Correlation scoring for parlay legs."""

from __future__ import annotations

from itertools import combinations

from shine.models import ParlayLeg


CONFLICTING_TAGS = {
    "pace_up": {"defense_grind", "slow_tempo"},
    "defense_grind": {"pace_up", "shootout"},
    "shootout": {"defense_grind", "bad_weather"},
    "bad_weather": {"shootout", "pass_heavy"},
    "possession": {"counterattack"},
    "counterattack": {"possession"},
    "map_pool_edge": {"map_pool_weakness"},
    "draft_meta_edge": {"draft_meta_weakness"},
    "agent_comp_edge": {"agent_comp_weakness"},
    "striker": {"grappler_control"},
    "grappler_control": {"striker"},
}

SPORT_CONTEXT_TAGS = {
    "basketball": {"pace_up", "defense_grind", "home_court"},
    "americanfootball": {"shootout", "bad_weather", "pass_heavy", "defense_grind"},
    "soccer": {"possession", "counterattack", "low_block"},
    "esports_cs": {"map_pool_edge", "map_pool_weakness"},
    "esports_lol": {"draft_meta_edge", "draft_meta_weakness"},
    "esports_valorant": {"agent_comp_edge", "agent_comp_weakness"},
    "mma": {"striker", "grappler_control", "cardio_edge"},
}


def score_correlation(legs: tuple[ParlayLeg, ...]) -> tuple[float, float]:
    """Return a pairwise correlation score and a bounded multiplier."""
    if len(legs) < 2:
        return 0.0, 1.0

    score = 0.0
    for left, right in combinations(legs, 2):
        score += _pair_score(left, right)

    multiplier = max(0.85, min(1.15, 1.0 + score))
    return score, multiplier


def _pair_score(left: ParlayLeg, right: ParlayLeg) -> float:
    if left.event_id == right.event_id:
        return -0.30

    score = 0.0
    shared_tags = left.style_tags & right.style_tags
    score += min(0.05, len(shared_tags) * 0.018)

    if _same_sport_family(left.sport_key, right.sport_key):
        score += 0.006

    for tag in left.style_tags:
        if CONFLICTING_TAGS.get(tag, set()) & right.style_tags:
            score -= 0.025

    for family, tags in SPORT_CONTEXT_TAGS.items():
        if family in left.sport_key and family in right.sport_key:
            left_family_tags = left.style_tags & tags
            right_family_tags = right.style_tags & tags
            if left_family_tags and right_family_tags:
                score += 0.008

    return score


def _same_sport_family(left_key: str, right_key: str) -> bool:
    return left_key.split("_", 1)[0] == right_key.split("_", 1)[0]
