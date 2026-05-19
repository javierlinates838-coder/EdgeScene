"""Core data models used throughout Shine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Tier(str, Enum):
    """EV tier for a parlay. S is best, D is worst."""

    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

    @classmethod
    def from_ev(cls, ev_pct: float) -> "Tier":
        """Map an EV percent (e.g. 12.5 for +12.5%) to a tier."""
        if ev_pct >= 15.0:
            return cls.S
        if ev_pct >= 8.0:
            return cls.A
        if ev_pct >= 3.0:
            return cls.B
        if ev_pct >= 0.0:
            return cls.C
        return cls.D


@dataclass
class Outcome:
    """A single moneyline outcome (team) with the best book price found."""

    name: str
    american_odds: int
    decimal_odds: float
    book: str
    implied_prob: float


@dataclass
class Event:
    """A single sporting event with its two-way moneyline outcomes."""

    id: str
    sport_key: str
    sport_title: str
    league: str
    commence_time: datetime
    home_team: str
    away_team: str
    outcomes: List[Outcome]
    venue: Optional[str] = None
    extra: Dict[str, object] = field(default_factory=dict)

    def outcome_for(self, team: str) -> Optional[Outcome]:
        for o in self.outcomes:
            if o.name.lower() == team.lower():
                return o
        return None


@dataclass
class Leg:
    """A single parlay leg: pick one outcome from one event."""

    event: Event
    pick: str
    book_decimal: float
    fair_prob: float            # after vig removal
    adjusted_prob: float        # after intelligence / context adjustments
    notes: List[str] = field(default_factory=list)

    @property
    def edge_pct(self) -> float:
        """Single-leg edge vs. book, before correlation."""
        book_prob = 1.0 / self.book_decimal if self.book_decimal else 0.0
        if book_prob <= 0:
            return 0.0
        return (self.adjusted_prob - book_prob) / book_prob * 100.0


@dataclass
class Parlay:
    legs: List[Leg]
    combined_decimal: float
    naive_prob: float           # product of adjusted probs
    correlated_prob: float      # after correlation adjustment
    book_implied: float         # 1 / combined decimal
    ev_pct: float
    tier: Tier
    correlation_score: float    # average pairwise correlation
    notes: List[str] = field(default_factory=list)
