from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TeamOdds:
    team: str
    american_odds: int
    implied_probability: float
    true_probability: float


@dataclass(frozen=True)
class EventOdds:
    sport_key: str
    sport_title: str
    event_id: str
    commence_time: str
    home_team: str
    away_team: str
    bookmaker: str
    teams: List[TeamOdds]


@dataclass(frozen=True)
class LegContext:
    """Context knobs for pressure, travel, and environment modeling."""

    stage: str = "regular"
    travel_miles: float = 0.0
    timezone_shift: int = 0
    altitude_meters: float = 0.0
    host_region_advantage: float = 0.0
    weather_severity: float = 0.0
    notes: Optional[str] = None


@dataclass(frozen=True)
class ParlayLeg:
    sport_key: str
    event_id: str
    matchup: str
    pick: str
    american_odds: int
    base_true_probability: float
    adjusted_probability: float
    pressure_multiplier: float
    travel_multiplier: float
    environment_multiplier: float
    context: LegContext = field(default_factory=LegContext)


@dataclass(frozen=True)
class ParlayEvaluation:
    legs: List[ParlayLeg]
    combined_probability: float
    correlation_score: float
    correlation_multiplier: float
    adjusted_probability: float
    payout_multiplier: float
    sportsbook_implied_probability: float
    expected_value: float
    tier: str
    metadata: Dict[str, float] = field(default_factory=dict)
