"""
Shine v4 Engine — the core parlay builder.

Orchestrates:
1. Pull live odds via TheOddsAPI
2. Remove vig → true probabilities
3. Apply intelligence layer (big-competition, pressure)
4. Apply environment adjustments (home, travel, altitude)
5. Analyze correlation between legs
6. Calculate true EV and assign tiers
7. Rank and output optimized parlays
"""

from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from shine.api.odds_client import OddsAPIClient
from shine.core.config import (
    ALL_SPORTS,
    ShineConfig,
    Sport,
    Tier,
    tier_from_ev,
)
from shine.core.models import (
    AdjustedProbability,
    GameContext,
    MarketOdds,
    Parlay,
    ParlayLeg,
    ShineResult,
)
from shine.core.probability import (
    VigAnalysis,
    american_to_implied,
    calculate_ev_percent,
    implied_to_american,
    median_probability,
    parlay_probability,
    remove_vig_best,
)
from shine.correlation.engine import (
    CorrelationResult,
    analyze_correlation,
    apply_correlation_to_parlay,
)
from shine.environment.adjustments import apply_environment
from shine.intelligence.pressure import apply_intelligence

logger = logging.getLogger(__name__)


@dataclass
class ProcessedGame:
    """A game fully processed through the Shine pipeline."""
    game_id: str
    sport: Sport
    team_a: str
    team_b: str
    implied_a: float
    implied_b: float
    true_prob_a: float
    true_prob_b: float
    adjusted_prob_a: float
    adjusted_prob_b: float
    best_odds_a: int
    best_odds_b: int
    context: GameContext
    adjustments_a: List[str] = field(default_factory=list)
    adjustments_b: List[str] = field(default_factory=list)


class ShineEngine:
    """The Shine v4 parlay engine."""

    def __init__(self, config: Optional[ShineConfig] = None):
        self.config = config or ShineConfig.from_env()
        self.client = OddsAPIClient(self.config)
        self.processed_games: List[ProcessedGame] = []

    def run(
        self,
        sports: Optional[List[Sport]] = None,
        max_parlays: int = 20,
        min_legs: int = 2,
        max_legs: int = 5,
        min_ev: Optional[float] = None,
    ) -> ShineResult:
        """
        Run the full Shine pipeline:
        1. Fetch odds
        2. Process each game
        3. Generate parlay combinations
        4. Rank by EV
        """
        target_sports = sports or ALL_SPORTS
        min_ev_threshold = min_ev if min_ev is not None else self.config.min_ev_threshold

        logger.info(f"Shine v4 engine starting — {len(target_sports)} sports")

        all_odds = self.client.get_all_live_odds(target_sports)

        self.processed_games = []
        for sport, games in all_odds.items():
            for game_data in games:
                processed = self._process_game(game_data, sport)
                if processed:
                    self.processed_games.append(processed)

        logger.info(f"Processed {len(self.processed_games)} games")

        if len(self.processed_games) < min_legs:
            return ShineResult(
                timestamp=datetime.now(),
                parlays=[],
                games_analyzed=len(self.processed_games),
                sports_covered=list(set(g.sport for g in self.processed_games)),
                api_calls_used=self.client.usage.requests_used,
                api_calls_remaining=self.client.usage.requests_remaining,
                warnings=["Not enough games available to build parlays"],
            )

        legs = self._generate_all_legs()
        parlays = self._build_parlays(legs, min_legs, max_legs, max_parlays, min_ev_threshold)

        return ShineResult(
            timestamp=datetime.now(),
            parlays=parlays,
            games_analyzed=len(self.processed_games),
            sports_covered=list(set(g.sport for g in self.processed_games)),
            api_calls_used=self.client.usage.requests_used,
            api_calls_remaining=self.client.usage.requests_remaining,
        )

    def run_with_mock_data(
        self,
        mock_games: List[Dict],
        max_parlays: int = 20,
        min_legs: int = 2,
        max_legs: int = 4,
        min_ev: Optional[float] = None,
    ) -> ShineResult:
        """Run the engine with pre-loaded mock data (for testing without API)."""
        min_ev_threshold = min_ev if min_ev is not None else self.config.min_ev_threshold

        self.processed_games = []
        for game_data in mock_games:
            sport = game_data.get("_sport", Sport.NBA)
            processed = self._process_game(game_data, sport)
            if processed:
                self.processed_games.append(processed)

        if len(self.processed_games) < min_legs:
            return ShineResult(
                timestamp=datetime.now(),
                parlays=[],
                games_analyzed=len(self.processed_games),
                sports_covered=[],
                warnings=["Not enough games to build parlays"],
            )

        legs = self._generate_all_legs()
        parlays = self._build_parlays(legs, min_legs, max_legs, max_parlays, min_ev_threshold)

        return ShineResult(
            timestamp=datetime.now(),
            parlays=parlays,
            games_analyzed=len(self.processed_games),
            sports_covered=list(set(g.sport for g in self.processed_games)),
        )

    def _process_game(self, game_data: Dict, sport: Sport) -> Optional[ProcessedGame]:
        """Process a single game through the full pipeline."""
        market = self.client.parse_market_odds(game_data)
        if not market:
            return None

        median_a = median_probability([o.implied_probability for o in market.odds_a])
        median_b = median_probability([o.implied_probability for o in market.odds_b])

        true_a, true_b = remove_vig_best(median_a, median_b)

        context = self._build_context(game_data, sport, market.team_a, market.team_b)

        intel_a, intel_b = apply_intelligence(
            market.team_a, market.team_b, true_a, true_b, context
        )

        env_a, env_b = apply_environment(
            market.team_a, market.team_b,
            intel_a.adjusted_probability, intel_b.adjusted_probability,
            context
        )

        all_adj_a = intel_a.adjustments + env_a.adjustments
        all_adj_b = intel_b.adjustments + env_b.adjustments

        best_a = market.best_odds_a
        best_b = market.best_odds_b

        return ProcessedGame(
            game_id=game_data.get("id", ""),
            sport=sport,
            team_a=market.team_a,
            team_b=market.team_b,
            implied_a=median_a,
            implied_b=median_b,
            true_prob_a=true_a,
            true_prob_b=true_b,
            adjusted_prob_a=env_a.adjusted_probability,
            adjusted_prob_b=env_b.adjusted_probability,
            best_odds_a=best_a.american if best_a else 0,
            best_odds_b=best_b.american if best_b else 0,
            context=context,
            adjustments_a=all_adj_a,
            adjustments_b=all_adj_b,
        )

    def _build_context(
        self, game_data: Dict, sport: Sport,
        team_a: str, team_b: str
    ) -> GameContext:
        """Build GameContext from raw API data."""
        home_team = game_data.get("home_team", "")
        away_team = game_data.get("away_team", "")

        is_playoff = False
        season_phase = "regular"
        tournament = game_data.get("sport_title", "")
        if any(kw in tournament.lower() for kw in ["playoff", "postseason", "final", "major", "worlds", "champions"]):
            is_playoff = True
            season_phase = "playoff"

        return GameContext(
            sport=sport,
            is_playoff=is_playoff,
            is_major=is_playoff,
            season_phase=season_phase,
            home_team=home_team,
            away_team=away_team,
            venue_city=_extract_city(home_team),
        )

    def _generate_all_legs(self) -> List[ParlayLeg]:
        """Generate all possible legs from processed games."""
        legs: List[ParlayLeg] = []

        for game in self.processed_games:
            legs.append(ParlayLeg(
                game_id=game.game_id,
                sport=game.sport,
                team=game.team_a,
                opponent=game.team_b,
                best_american_odds=game.best_odds_a,
                implied_probability=game.implied_a,
                true_probability=game.true_prob_a,
                adjusted_probability=game.adjusted_prob_a,
                context=game.context,
                adjustments=game.adjustments_a,
            ))

            legs.append(ParlayLeg(
                game_id=game.game_id,
                sport=game.sport,
                team=game.team_b,
                opponent=game.team_a,
                best_american_odds=game.best_odds_b,
                implied_probability=game.implied_b,
                true_probability=game.true_prob_b,
                adjusted_probability=game.adjusted_prob_b,
                context=game.context,
                adjustments=game.adjustments_b,
            ))

        return legs

    def _build_parlays(
        self,
        all_legs: List[ParlayLeg],
        min_legs: int,
        max_legs: int,
        max_parlays: int,
        min_ev: float,
    ) -> List[Parlay]:
        """Build and rank parlays from available legs."""
        best_legs = self._select_best_legs(all_legs)

        parlays: List[Parlay] = []

        for size in range(min_legs, min(max_legs + 1, len(best_legs) + 1)):
            for combo in itertools.combinations(best_legs, size):
                combo_list = list(combo)

                if self._has_same_game_conflict(combo_list):
                    continue

                parlay = self._evaluate_parlay(combo_list)
                if parlay and parlay.true_ev_percent >= min_ev:
                    parlays.append(parlay)

        parlays.sort(key=lambda p: p.true_ev_percent, reverse=True)

        return parlays[:max_parlays]

    def _select_best_legs(self, all_legs: List[ParlayLeg], max_per_game: int = 1) -> List[ParlayLeg]:
        """Select the best leg per game (highest edge)."""
        game_best: Dict[str, ParlayLeg] = {}
        for leg in all_legs:
            if leg.game_id not in game_best or leg.edge > game_best[leg.game_id].edge:
                game_best[leg.game_id] = leg

        selected = sorted(game_best.values(), key=lambda l: l.edge, reverse=True)

        return selected[:25]

    def _has_same_game_conflict(self, legs: List[ParlayLeg]) -> bool:
        """Check for same-game conflicts in a leg combination."""
        game_ids = [leg.game_id for leg in legs]
        return len(game_ids) != len(set(game_ids))

    def _evaluate_parlay(self, legs: List[ParlayLeg]) -> Optional[Parlay]:
        """Evaluate a parlay: calculate EV, apply correlation, assign tier."""
        adjusted_probs = [leg.adjusted_probability for leg in legs]
        implied_probs = [leg.implied_probability for leg in legs]

        raw_prob = parlay_probability(adjusted_probs)
        sportsbook_prob = parlay_probability(implied_probs)

        correlation = analyze_correlation(legs)
        correlated_prob = apply_correlation_to_parlay(raw_prob, correlation)

        ev_percent = calculate_ev_percent(correlated_prob, sportsbook_prob)
        tier = tier_from_ev(ev_percent)

        try:
            fair_odds = implied_to_american(correlated_prob)
            book_odds = implied_to_american(sportsbook_prob)
        except (ValueError, ZeroDivisionError):
            fair_odds = 0
            book_odds = 0

        stake = self.config.default_stake
        if sportsbook_prob > 0:
            decimal_odds = 1.0 / sportsbook_prob
            expected_profit = (correlated_prob * decimal_odds - 1.0) * stake
        else:
            expected_profit = 0.0

        return Parlay(
            legs=legs,
            raw_parlay_prob=raw_prob,
            correlated_parlay_prob=correlated_prob,
            sportsbook_implied_prob=sportsbook_prob,
            true_ev_percent=ev_percent,
            tier=tier,
            correlation_factor=correlation.composite_factor,
            fair_american_odds=fair_odds,
            sportsbook_american_odds=book_odds,
            stake=stake,
            expected_profit=expected_profit,
            correlation_details=correlation.details,
        )


def _extract_city(team_name: str) -> str:
    """Extract probable city from a team name."""
    from shine.environment.adjustments import CITY_COORDINATES

    for city in CITY_COORDINATES:
        if city.lower() in team_name.lower():
            return city

    parts = team_name.rsplit(" ", 1)
    if parts[0] in CITY_COORDINATES:
        return parts[0]

    return ""
