"""Core data models for Shine v4."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from shine.core.config import Sport, Tier, tier_from_ev


@dataclass
class Team:
    name: str
    sport: Sport
    home: bool = False
    location: Optional[str] = None
    conference: Optional[str] = None
    seed: Optional[int] = None


@dataclass
class Odds:
    """Odds from a single bookmaker for one outcome."""
    bookmaker: str
    american: int
    implied_probability: float
    last_update: Optional[datetime] = None


@dataclass
class MarketOdds:
    """All bookmaker odds for a single h2h market."""
    team_a: str
    team_b: str
    odds_a: List[Odds] = field(default_factory=list)
    odds_b: List[Odds] = field(default_factory=list)
    draw_odds: Optional[List[Odds]] = None

    @property
    def best_odds_a(self) -> Optional[Odds]:
        if not self.odds_a:
            return None
        return max(self.odds_a, key=lambda o: o.american)

    @property
    def best_odds_b(self) -> Optional[Odds]:
        if not self.odds_b:
            return None
        return max(self.odds_b, key=lambda o: o.american)


@dataclass
class GameContext:
    """Rich context about a game for intelligence adjustments."""
    sport: Sport
    is_playoff: bool = False
    is_major: bool = False
    playoff_round: Optional[str] = None
    season_phase: str = "regular"
    venue: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    altitude_ft: float = 0.0
    temperature_f: Optional[float] = None
    is_neutral_site: bool = False
    is_international: bool = False


@dataclass
class AdjustedProbability:
    """A probability after all Shine adjustments."""
    team: str
    raw_implied: float
    vig_free: float
    intelligence_adj: float
    environment_adj: float
    final_probability: float
    adjustments_log: List[str] = field(default_factory=list)

    @property
    def total_adjustment(self) -> float:
        return self.final_probability - self.vig_free


@dataclass
class ParlayLeg:
    """A single leg of a parlay."""
    game_id: str
    sport: Sport
    team: str
    opponent: str
    best_american_odds: int
    implied_probability: float
    true_probability: float
    adjusted_probability: float
    context: Optional[GameContext] = None
    adjustments: List[str] = field(default_factory=list)

    @property
    def edge(self) -> float:
        return self.adjusted_probability - self.implied_probability

    @property
    def display_odds(self) -> str:
        prefix = "+" if self.best_american_odds > 0 else ""
        return f"{prefix}{self.best_american_odds}"


@dataclass
class Parlay:
    """A complete parlay with EV analysis."""
    legs: List[ParlayLeg]
    raw_parlay_prob: float
    correlated_parlay_prob: float
    sportsbook_implied_prob: float
    true_ev_percent: float
    tier: Tier
    correlation_factor: float = 1.0
    fair_american_odds: int = 0
    sportsbook_american_odds: int = 0
    stake: float = 10.0
    expected_profit: float = 0.0
    correlation_details: List[str] = field(default_factory=list)

    @property
    def num_legs(self) -> int:
        return len(self.legs)

    @property
    def sports_involved(self) -> List[Sport]:
        return list(set(leg.sport for leg in self.legs))

    @property
    def is_cross_sport(self) -> bool:
        return len(self.sports_involved) > 1


@dataclass
class ShineResult:
    """Complete output of a Shine analysis run."""
    timestamp: datetime
    parlays: List[Parlay]
    games_analyzed: int
    sports_covered: List[Sport]
    api_calls_used: int = 0
    api_calls_remaining: Optional[int] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def best_parlay(self) -> Optional[Parlay]:
        if not self.parlays:
            return None
        return max(self.parlays, key=lambda p: p.true_ev_percent)

    def parlays_by_tier(self, tier: Tier) -> List[Parlay]:
        return [p for p in self.parlays if p.tier == tier]
