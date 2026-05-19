from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Sequence


@dataclass(slots=True)
class OddsBookPrice:
    bookmaker: str
    selection: str
    decimal_odds: float


@dataclass(slots=True)
class EventMarket:
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: datetime
    prices: List[OddsBookPrice]


@dataclass(slots=True)
class LegInput:
    sport_key: str
    event_id: str
    selection: str
    decimal_odds: float
    team_or_player: str
    tags: Sequence[str] = field(default_factory=tuple)


@dataclass(slots=True)
class LegScore:
    leg: LegInput
    base_probability: float
    no_vig_probability: float
    adjusted_probability: float
    adjustment_factors: Dict[str, float]


@dataclass(slots=True)
class CorrelationResult:
    multiplier: float
    pairwise_notes: List[str]


@dataclass(slots=True)
class ParlayResult:
    legs: List[LegScore]
    sportsbook_probability: float
    model_probability: float
    ev: float
    tier: str
    expected_payout_multiple: float
    correlation_multiplier: float
    notes: List[str]


@dataclass(slots=True)
class EngineConfig:
    pressure_weight: float = 0.08
    travel_weight: float = 0.05
    home_advantage_weight: float = 0.04
    host_region_weight: float = 0.03
    max_leg_adjustment: float = 0.25
    min_probability: float = 0.01
    max_probability: float = 0.99
