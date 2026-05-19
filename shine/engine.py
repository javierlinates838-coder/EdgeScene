"""Shine v4 moneyline parlay engine."""

from __future__ import annotations

from itertools import combinations

from shine.correlation import score_correlation
from shine.intelligence import IntelligenceLayer
from shine.models import MoneylineEvent, ParlayCandidate, ParlayLeg
from shine.odds_math import expected_value, probability_to_american, product


class ShineEngine:
    """Build and rank moneyline parlays from normalized odds events."""

    def __init__(self, intelligence: IntelligenceLayer | None = None) -> None:
        self.intelligence = intelligence or IntelligenceLayer()

    def build_legs(self, events: list[MoneylineEvent]) -> list[ParlayLeg]:
        legs: list[ParlayLeg] = []
        for event in events:
            for outcome in event.outcomes:
                adjusted_probability, adjustments, style_tags = self.intelligence.adjust_probability(
                    event,
                    outcome.participant,
                    outcome.no_vig_probability,
                )
                legs.append(
                    ParlayLeg(
                        event_id=event.event_id,
                        sport_key=event.sport_key,
                        sport_title=event.sport_title,
                        participant=outcome.participant,
                        opponent=_opponent_for(event, outcome.participant),
                        average_american_odds=outcome.average_american_odds,
                        average_decimal_odds=outcome.average_decimal_odds,
                        market_implied_probability=outcome.implied_probability,
                        no_vig_probability=outcome.no_vig_probability,
                        adjusted_probability=adjusted_probability,
                        edge=adjusted_probability - outcome.implied_probability,
                        fair_american_odds=probability_to_american(adjusted_probability),
                        adjustments=adjustments,
                        style_tags=style_tags,
                    )
                )
        return sorted(legs, key=lambda leg: leg.edge, reverse=True)

    def rank_parlays(
        self,
        events: list[MoneylineEvent],
        *,
        legs_per_parlay: int = 3,
        max_leg_pool: int = 40,
        limit: int = 10,
        min_edge: float = -0.05,
    ) -> list[ParlayCandidate]:
        if legs_per_parlay < 2:
            raise ValueError("Parlays require at least two legs")

        leg_pool = [leg for leg in self.build_legs(events) if leg.edge >= min_edge][:max_leg_pool]
        candidates: list[ParlayCandidate] = []
        for combo in combinations(leg_pool, legs_per_parlay):
            if len({leg.event_id for leg in combo}) != legs_per_parlay:
                continue
            offered_decimal_odds = product([leg.average_decimal_odds for leg in combo])
            sportsbook_probability = 1.0 / offered_decimal_odds
            independent_probability = product([leg.adjusted_probability for leg in combo])
            correlation_score, correlation_multiplier = score_correlation(tuple(combo))
            true_probability = min(0.999, independent_probability * correlation_multiplier)
            ev = expected_value(true_probability, offered_decimal_odds)
            candidates.append(
                ParlayCandidate(
                    legs=tuple(combo),
                    offered_decimal_odds=offered_decimal_odds,
                    sportsbook_probability=sportsbook_probability,
                    independent_probability=independent_probability,
                    correlation_score=correlation_score,
                    correlation_multiplier=correlation_multiplier,
                    true_probability=true_probability,
                    expected_value=ev,
                    tier=tier_for_ev(ev),
                )
            )

        candidates.sort(key=lambda candidate: (candidate.expected_value, candidate.true_probability), reverse=True)
        return candidates[:limit]


def tier_for_ev(ev: float) -> str:
    if ev >= 0.12:
        return "S"
    if ev >= 0.06:
        return "A"
    if ev >= 0.02:
        return "B"
    if ev >= 0.0:
        return "C"
    return "D"


def _opponent_for(event: MoneylineEvent, participant: str) -> str | None:
    for outcome in event.outcomes:
        if outcome.participant != participant:
            return outcome.participant
    return None
