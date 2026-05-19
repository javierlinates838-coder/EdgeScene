from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence

from .correlation import correlation_multiplier, correlation_score
from .intelligence import apply_context_adjustments
from .math_utils import parlay_payout_multiplier
from .models import EventOdds, LegContext, ParlayEvaluation, ParlayLeg


TIER_ORDER = ["S", "A", "B", "C", "D"]


@dataclass
class ShineEngineConfig:
    max_legs: int = 3
    max_candidate_legs: int = 40
    max_parlays: int = 10
    min_tier: str = "D"
    default_stage_by_sport: Dict[str, str] = field(
        default_factory=lambda: {
            "basketball_nba": "playoffs",
            "americanfootball_nfl": "playoffs",
            "mma_mixed_martial_arts": "title_fight",
            "esports_cs2": "major",
            "esports_lol": "championship",
            "esports_valorant": "championship",
        }
    )


class ShineEngine:
    def __init__(self, config: Optional[ShineEngineConfig] = None) -> None:
        self.config = config or ShineEngineConfig()

    def build_legs(
        self,
        events: Iterable[EventOdds],
        context_overrides: Optional[Dict[str, LegContext]] = None,
    ) -> List[ParlayLeg]:
        overrides = context_overrides or {}
        legs: List[ParlayLeg] = []
        for event in events:
            matchup = f"{event.away_team} vs {event.home_team}".strip()
            base_stage = self.config.default_stage_by_sport.get(event.sport_key, "regular")
            base_context = LegContext(stage=base_stage)
            event_override = overrides.get(event.event_id)

            for team_odds in event.teams:
                context = event_override or base_context
                adjusted = apply_context_adjustments(team_odds.true_probability, context)
                legs.append(
                    ParlayLeg(
                        sport_key=event.sport_key,
                        event_id=event.event_id,
                        matchup=matchup,
                        pick=team_odds.team,
                        american_odds=team_odds.american_odds,
                        base_true_probability=team_odds.true_probability,
                        adjusted_probability=adjusted["adjusted_probability"],
                        pressure_multiplier=adjusted["pressure_multiplier"],
                        travel_multiplier=adjusted["travel_multiplier"],
                        environment_multiplier=adjusted["environment_multiplier"],
                        context=context,
                    )
                )
        return legs

    def rank_legs(self, legs: Sequence[ParlayLeg]) -> List[ParlayLeg]:
        """
        Rank legs by edge signal:
        - Improvement over base probability
        - Absolute adjusted probability
        """
        def score(leg: ParlayLeg) -> float:
            edge = leg.adjusted_probability - leg.base_true_probability
            return (edge * 0.65) + (leg.adjusted_probability * 0.35)

        ranked = sorted(legs, key=score, reverse=True)
        return ranked[: self.config.max_candidate_legs]

    def evaluate_parlays(self, candidate_legs: Sequence[ParlayLeg]) -> List[ParlayEvaluation]:
        parlays: List[ParlayEvaluation] = []
        max_legs = max(2, self.config.max_legs)
        unique_event_legs = self._dedupe_event_leg_collisions(candidate_legs)

        for size in range(2, min(max_legs, len(unique_event_legs)) + 1):
            for combo in combinations(unique_event_legs, size):
                if not self._has_unique_events(combo):
                    continue
                parlays.append(self._evaluate_single_parlay(list(combo)))

        ranked = sorted(parlays, key=lambda p: p.expected_value, reverse=True)
        min_tier_idx = TIER_ORDER.index(self.config.min_tier)
        filtered = [p for p in ranked if TIER_ORDER.index(p.tier) <= min_tier_idx]
        return filtered[: self.config.max_parlays]

    def run(
        self,
        events: Iterable[EventOdds],
        context_overrides: Optional[Dict[str, LegContext]] = None,
    ) -> List[ParlayEvaluation]:
        legs = self.build_legs(events=events, context_overrides=context_overrides)
        ranked_legs = self.rank_legs(legs)
        return self.evaluate_parlays(ranked_legs)

    @staticmethod
    def _has_unique_events(legs: Sequence[ParlayLeg]) -> bool:
        event_ids = {leg.event_id for leg in legs}
        return len(event_ids) == len(legs)

    @staticmethod
    def _dedupe_event_leg_collisions(legs: Sequence[ParlayLeg]) -> List[ParlayLeg]:
        """
        Keep strongest leg per (event, pick) tuple. This trims duplicate books.
        """
        deduped: Dict[tuple[str, str], ParlayLeg] = {}
        for leg in legs:
            key = (leg.event_id, leg.pick)
            existing = deduped.get(key)
            if existing is None or leg.adjusted_probability > existing.adjusted_probability:
                deduped[key] = leg
        return list(deduped.values())

    def _evaluate_single_parlay(self, legs: List[ParlayLeg]) -> ParlayEvaluation:
        base_probability = 1.0
        for leg in legs:
            base_probability *= leg.adjusted_probability

        c_score = correlation_score(legs)
        c_multiplier = correlation_multiplier(legs)
        adjusted_probability = max(0.0001, min(0.99, base_probability * c_multiplier))

        payout = parlay_payout_multiplier(leg.american_odds for leg in legs)
        sportsbook_implied = 1 / payout
        expected_value = (adjusted_probability * payout) - 1

        return ParlayEvaluation(
            legs=legs,
            combined_probability=base_probability,
            correlation_score=c_score,
            correlation_multiplier=c_multiplier,
            adjusted_probability=adjusted_probability,
            payout_multiplier=payout,
            sportsbook_implied_probability=sportsbook_implied,
            expected_value=expected_value,
            tier=self._tier_for_ev(expected_value),
            metadata={"edge_over_book": adjusted_probability - sportsbook_implied},
        )

    @staticmethod
    def _tier_for_ev(expected_value: float) -> str:
        if expected_value >= 0.20:
            return "S"
        if expected_value >= 0.12:
            return "A"
        if expected_value >= 0.06:
            return "B"
        if expected_value >= 0.01:
            return "C"
        return "D"
