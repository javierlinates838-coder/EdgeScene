from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence

from .context import ContextInput, travel_environment_multiplier
from .correlation import correlation_multiplier
from .intelligence import pressure_adjustment
from .models import EngineConfig, EventMarket, LegInput, LegScore, ParlayResult
from .probability import ev_tier, expected_value, implied_probability_from_decimal, parlay_probability, remove_vig_from_outcomes


class ShineEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()

    def score_parlay(
        self,
        legs: Sequence[LegInput],
        market_lookup: Mapping[str, EventMarket] | None = None,
        competition_tags: Mapping[str, str] | None = None,
        context_by_event: Mapping[str, ContextInput] | None = None,
    ) -> ParlayResult:
        if not legs:
            raise ValueError("At least one leg is required.")

        market_lookup = market_lookup or {}
        competition_tags = competition_tags or {}
        context_by_event = context_by_event or {}

        leg_scores: List[LegScore] = []
        sportsbook_probs: List[float] = []
        model_probs: List[float] = []

        for leg in legs:
            sportsbook_prob = implied_probability_from_decimal(leg.decimal_odds)
            sportsbook_probs.append(sportsbook_prob)

            no_vig_prob = self._estimate_no_vig_probability(
                leg=leg,
                market=market_lookup.get(leg.event_id),
                fallback=sportsbook_prob,
            )

            factors = {}
            competition_tag = competition_tags.get(leg.event_id)
            pressure_mult = pressure_adjustment(
                base_probability=no_vig_prob,
                team_or_player=leg.team_or_player,
                competition_tag=competition_tag,
                pressure_weight=self.config.pressure_weight,
            )
            factors["pressure"] = pressure_mult

            context = context_by_event.get(leg.event_id, ContextInput())
            context_mult = travel_environment_multiplier(
                context=context,
                travel_weight=self.config.travel_weight,
                home_advantage_weight=self.config.home_advantage_weight,
                host_region_weight=self.config.host_region_weight,
            )
            factors["context"] = context_mult

            combined_mult = pressure_mult * context_mult
            bounded_mult = self._bound_multiplier(combined_mult)
            factors["bounded"] = bounded_mult

            adjusted_prob = self._clamp_probability(no_vig_prob * bounded_mult)
            model_probs.append(adjusted_prob)

            leg_scores.append(
                LegScore(
                    leg=leg,
                    base_probability=sportsbook_prob,
                    no_vig_probability=no_vig_prob,
                    adjusted_probability=adjusted_prob,
                    adjustment_factors=factors,
                )
            )

        sportsbook_parlay_prob = parlay_probability(sportsbook_probs)
        model_parlay_prob = parlay_probability(model_probs)

        corr = correlation_multiplier(legs)
        model_parlay_prob = self._clamp_probability(model_parlay_prob * corr.multiplier)

        payout_multiple = 1.0
        for leg in legs:
            payout_multiple *= leg.decimal_odds

        ev = expected_value(model_parlay_prob, payout_multiple)
        return ParlayResult(
            legs=leg_scores,
            sportsbook_probability=sportsbook_parlay_prob,
            model_probability=model_parlay_prob,
            ev=ev,
            tier=ev_tier(ev),
            expected_payout_multiple=payout_multiple,
            correlation_multiplier=corr.multiplier,
            notes=corr.pairwise_notes,
        )

    @staticmethod
    def _estimate_no_vig_probability(leg: LegInput, market: EventMarket | None, fallback: float) -> float:
        if market is None or not market.prices:
            return fallback

        by_bookmaker: Dict[str, Dict[str, float]] = defaultdict(dict)
        for price in market.prices:
            by_bookmaker[price.bookmaker][price.selection] = price.decimal_odds

        selection_probs: List[float] = []
        for outcomes in by_bookmaker.values():
            if leg.selection not in outcomes:
                continue
            ordered = list(outcomes.items())
            if len(ordered) < 2:
                continue
            odds = [odd for _, odd in ordered]
            try:
                no_vig = remove_vig_from_outcomes(odds)
            except ValueError:
                continue
            names = [name for name, _ in ordered]
            idx = names.index(leg.selection)
            selection_probs.append(no_vig[idx])

        if not selection_probs:
            return fallback
        return sum(selection_probs) / len(selection_probs)

    def _bound_multiplier(self, multiplier: float) -> float:
        max_up = 1.0 + self.config.max_leg_adjustment
        max_down = 1.0 - self.config.max_leg_adjustment
        return max(max_down, min(max_up, multiplier))

    def _clamp_probability(self, probability: float) -> float:
        return max(self.config.min_probability, min(self.config.max_probability, probability))
