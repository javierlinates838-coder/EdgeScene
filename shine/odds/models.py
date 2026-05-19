"""Data models for odds and games."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TeamOdds:
    """Moneyline odds for one side of a matchup."""

    name: str
    american_odds: int
    implied_prob: float = 0.0
    true_prob: float = 0.0

    def __post_init__(self) -> None:
        self.implied_prob = self._american_to_prob(self.american_odds)

    @staticmethod
    def _american_to_prob(odds: int) -> float:
        if odds < 0:
            return abs(odds) / (abs(odds) + 100)
        return 100 / (odds + 100)


@dataclass
class Game:
    """A single matchup with moneyline odds for both sides."""

    id: str
    sport: str
    league: str
    commence_time: datetime
    home: TeamOdds
    away: TeamOdds
    bookmaker: str
    vig: float = 0.0

    def __post_init__(self) -> None:
        total = self.home.implied_prob + self.away.implied_prob
        self.vig = total - 1.0
        if total > 0:
            self.home.true_prob = self.home.implied_prob / total
            self.away.true_prob = self.away.implied_prob / total


@dataclass
class ParlayLeg:
    """One leg of a parlay — a pick on a specific game."""

    game: Game
    pick: str  # team name
    prob: float  # adjusted probability after all layers
    american_odds: int
    bookmaker: str
    sport: str

    @property
    def decimal_odds(self) -> float:
        if self.american_odds < 0:
            return 1 + 100 / abs(self.american_odds)
        return 1 + self.american_odds / 100


@dataclass
class Parlay:
    """A complete parlay with calculated EV and tier."""

    legs: list[ParlayLeg] = field(default_factory=list)
    true_prob: float = 0.0
    implied_prob: float = 0.0
    decimal_odds: float = 0.0
    ev: float = 0.0
    tier: str = "D"
    correlation_factor: float = 1.0
