"""Core data models used by Shine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class OutcomePrice:
    participant: str
    average_american_odds: float
    average_decimal_odds: float
    implied_probability: float
    no_vig_probability: float
    bookmaker_count: int


@dataclass(frozen=True)
class MoneylineEvent:
    event_id: str
    sport_key: str
    sport_title: str
    commence_time: datetime | None
    home_team: str | None
    away_team: str | None
    outcomes: tuple[OutcomePrice, ...]
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def participants(self) -> tuple[str, ...]:
        return tuple(outcome.participant for outcome in self.outcomes)


@dataclass(frozen=True)
class EntityContext:
    pressure_rating: float = 0.0
    travel_km: float = 0.0
    timezone_delta: float = 0.0
    altitude_m: float = 0.0
    host_region_advantage: bool = False
    style_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Adjustment:
    name: str
    delta: float
    reason: str


@dataclass(frozen=True)
class ParlayLeg:
    event_id: str
    sport_key: str
    sport_title: str
    participant: str
    opponent: str | None
    average_american_odds: float
    average_decimal_odds: float
    market_implied_probability: float
    no_vig_probability: float
    adjusted_probability: float
    edge: float
    fair_american_odds: int
    adjustments: tuple[Adjustment, ...] = field(default_factory=tuple)
    style_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ParlayCandidate:
    legs: tuple[ParlayLeg, ...]
    offered_decimal_odds: float
    sportsbook_probability: float
    independent_probability: float
    correlation_score: float
    correlation_multiplier: float
    true_probability: float
    expected_value: float
    tier: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "expected_value": round(self.expected_value, 4),
            "expected_value_percent": round(self.expected_value * 100.0, 2),
            "offered_decimal_odds": round(self.offered_decimal_odds, 4),
            "sportsbook_probability": round(self.sportsbook_probability, 4),
            "independent_probability": round(self.independent_probability, 4),
            "correlation_score": round(self.correlation_score, 4),
            "correlation_multiplier": round(self.correlation_multiplier, 4),
            "true_probability": round(self.true_probability, 4),
            "legs": [
                {
                    "sport": leg.sport_title,
                    "event_id": leg.event_id,
                    "pick": leg.participant,
                    "opponent": leg.opponent,
                    "average_american_odds": round(leg.average_american_odds),
                    "market_implied_probability": round(leg.market_implied_probability, 4),
                    "no_vig_probability": round(leg.no_vig_probability, 4),
                    "adjusted_probability": round(leg.adjusted_probability, 4),
                    "edge": round(leg.edge, 4),
                    "fair_american_odds": leg.fair_american_odds,
                    "adjustments": [
                        {"name": adjustment.name, "delta": round(adjustment.delta, 4), "reason": adjustment.reason}
                        for adjustment in leg.adjustments
                    ],
                    "style_tags": sorted(leg.style_tags),
                }
                for leg in self.legs
            ],
        }
