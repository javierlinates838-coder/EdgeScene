"""
Environment & travel adjustment module.

Models: home advantage, travel distance, time zones, altitude,
temperature, host-region advantage for international events.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from shine.core.config import Sport
from shine.core.models import GameContext

logger = logging.getLogger(__name__)


SPORT_HOME_ADVANTAGE: Dict[Sport, float] = {
    Sport.NBA: 0.030,
    Sport.NFL: 0.028,
    Sport.MLB: 0.022,
    Sport.NHL: 0.025,
    Sport.SOCCER_EPL: 0.040,
    Sport.SOCCER_UCL: 0.035,
    Sport.SOCCER_LALIGA: 0.042,
    Sport.SOCCER_BUNDESLIGA: 0.038,
    Sport.SOCCER_SERIEA: 0.040,
    Sport.SOCCER_LIGUE1: 0.038,
    Sport.SOCCER_MLS: 0.032,
    Sport.CS2: 0.005,
    Sport.LOL: 0.008,
    Sport.VAL: 0.005,
    Sport.UFC: 0.010,
}

CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    # NBA
    "Boston": (42.36, -71.06), "New York": (40.71, -74.01),
    "Brooklyn": (40.68, -73.97), "Philadelphia": (39.95, -75.17),
    "Toronto": (43.65, -79.38), "Milwaukee": (43.04, -87.91),
    "Cleveland": (41.50, -81.69), "Miami": (25.76, -80.19),
    "Atlanta": (33.75, -84.39), "Chicago": (41.88, -87.63),
    "Indiana": (39.77, -86.16), "Indianapolis": (39.77, -86.16),
    "Orlando": (28.54, -81.38), "Charlotte": (35.23, -80.84),
    "Washington": (38.91, -77.04), "Detroit": (42.33, -83.05),
    "Denver": (39.74, -104.99), "Los Angeles": (34.05, -118.24),
    "Phoenix": (33.45, -112.07), "Sacramento": (38.58, -121.49),
    "Golden State": (37.77, -122.42), "San Francisco": (37.77, -122.42),
    "Dallas": (32.78, -96.80), "Houston": (29.76, -95.37),
    "San Antonio": (29.42, -98.49), "Memphis": (35.15, -90.05),
    "New Orleans": (29.95, -90.07), "Minnesota": (44.98, -93.27),
    "Oklahoma City": (35.47, -97.52), "Portland": (45.52, -122.68),
    "Utah": (40.76, -111.89), "Salt Lake City": (40.76, -111.89),
    "Seattle": (47.61, -122.33),
    # NFL
    "Kansas City": (39.10, -94.58), "Baltimore": (39.29, -76.61),
    "Buffalo": (42.89, -78.88), "Cincinnati": (39.10, -84.51),
    "Pittsburgh": (40.44, -79.99), "Jacksonville": (30.33, -81.66),
    "Tampa Bay": (27.95, -82.46), "Tampa": (27.95, -82.46),
    "Las Vegas": (36.17, -115.14), "Green Bay": (44.51, -88.02),
    # Soccer
    "London": (51.51, -0.13), "Manchester": (53.48, -2.24),
    "Liverpool": (53.41, -2.98), "Madrid": (40.42, -3.70),
    "Barcelona": (41.39, 2.17), "Munich": (48.14, 11.58),
    "Paris": (48.86, 2.35), "Milan": (45.46, 9.19),
    "Turin": (45.07, 7.69), "Rome": (41.90, 12.50),
    "Amsterdam": (52.37, 4.90), "Dortmund": (51.51, 7.47),
    # International
    "Seoul": (37.57, 126.98), "Shanghai": (31.23, 121.47),
    "Tokyo": (35.68, 139.69), "São Paulo": (-23.55, -46.63),
    "Rio de Janeiro": (-22.91, -43.17), "Istanbul": (41.01, 28.98),
    "Singapore": (1.35, 103.82), "Reykjavik": (64.15, -21.94),
    "Copenhagen": (55.68, 12.57), "Riyadh": (24.71, 46.68),
    "Abu Dhabi": (24.45, 54.65),
}

CITY_ALTITUDES_FT: Dict[str, float] = {
    "Denver": 5280, "Salt Lake City": 4226, "Utah": 4226,
    "Mexico City": 7350, "Bogota": 8660, "Quito": 9350,
    "La Paz": 11975, "Colorado Springs": 6035,
    "Johannesburg": 5751, "Nairobi": 5889, "Addis Ababa": 7726,
}

CITY_TIMEZONE_OFFSETS: Dict[str, int] = {
    "New York": -5, "Boston": -5, "Brooklyn": -5, "Philadelphia": -5,
    "Miami": -5, "Atlanta": -5, "Cleveland": -5, "Orlando": -5,
    "Charlotte": -5, "Washington": -5, "Detroit": -5, "Toronto": -5,
    "Chicago": -6, "Milwaukee": -6, "Indiana": -5, "Indianapolis": -5,
    "Memphis": -6, "New Orleans": -6, "Minnesota": -6, "Dallas": -6,
    "Houston": -6, "San Antonio": -6, "Oklahoma City": -6,
    "Kansas City": -6, "Green Bay": -6,
    "Denver": -7, "Salt Lake City": -7, "Utah": -7, "Phoenix": -7,
    "Los Angeles": -8, "Golden State": -8, "San Francisco": -8,
    "Sacramento": -8, "Portland": -8, "Seattle": -8, "Las Vegas": -8,
    "London": 0, "Paris": 1, "Madrid": 1, "Barcelona": 1,
    "Munich": 1, "Milan": 1, "Turin": 1, "Rome": 1,
    "Amsterdam": 1, "Dortmund": 1, "Istanbul": 3,
    "Seoul": 9, "Tokyo": 9, "Shanghai": 8, "Singapore": 8,
    "São Paulo": -3, "Rio de Janeiro": -3,
    "Riyadh": 3, "Abu Dhabi": 4, "Reykjavik": 0, "Copenhagen": 1,
}


@dataclass
class EnvironmentResult:
    team: str
    base_probability: float
    adjusted_probability: float
    adjustments: List[str] = field(default_factory=list)
    total_adjustment: float = 0.0


def apply_environment(
    team_a: str,
    team_b: str,
    prob_a: float,
    prob_b: float,
    context: GameContext,
) -> Tuple[EnvironmentResult, EnvironmentResult]:
    """Apply all environment-based adjustments."""
    result_a = EnvironmentResult(team=team_a, base_probability=prob_a, adjusted_probability=prob_a)
    result_b = EnvironmentResult(team=team_b, base_probability=prob_b, adjusted_probability=prob_b)

    if not context.is_neutral_site:
        _apply_home_advantage(result_a, result_b, context)

    _apply_altitude(result_a, result_b, context)
    _apply_travel_fatigue(result_a, result_b, context)

    _normalize_env(result_a, result_b)

    return result_a, result_b


def _apply_home_advantage(
    result_a: EnvironmentResult,
    result_b: EnvironmentResult,
    context: GameContext,
) -> None:
    """Apply sport-specific home-court/field/ice advantage."""
    base_advantage = SPORT_HOME_ADVANTAGE.get(context.sport, 0.02)

    if context.is_playoff or context.is_major:
        base_advantage *= 1.15

    if context.home_team:
        if context.home_team == result_a.team:
            result_a.adjusted_probability += base_advantage
            result_a.total_adjustment += base_advantage
            result_a.adjustments.append(f"Home advantage: +{base_advantage:.3f}")
            result_b.adjusted_probability -= base_advantage * 0.5
            result_b.total_adjustment -= base_advantage * 0.5
            result_b.adjustments.append(f"Away penalty: -{base_advantage * 0.5:.3f}")
        elif context.home_team == result_b.team:
            result_b.adjusted_probability += base_advantage
            result_b.total_adjustment += base_advantage
            result_b.adjustments.append(f"Home advantage: +{base_advantage:.3f}")
            result_a.adjusted_probability -= base_advantage * 0.5
            result_a.total_adjustment -= base_advantage * 0.5
            result_a.adjustments.append(f"Away penalty: -{base_advantage * 0.5:.3f}")


def _apply_altitude(
    result_a: EnvironmentResult,
    result_b: EnvironmentResult,
    context: GameContext,
) -> None:
    """Altitude advantage for home team in high-altitude venues."""
    venue_city = context.venue_city or ""
    altitude = context.altitude_ft

    if altitude == 0 and venue_city in CITY_ALTITUDES_FT:
        altitude = CITY_ALTITUDES_FT[venue_city]

    if altitude < 3000:
        return

    alt_factor = min((altitude - 3000) / 5000.0, 1.0)
    alt_boost = 0.015 * alt_factor

    if context.sport in (Sport.NBA, Sport.NFL, Sport.MLB, Sport.NHL):
        if context.home_team == result_a.team:
            result_a.adjusted_probability += alt_boost
            result_a.total_adjustment += alt_boost
            result_a.adjustments.append(f"Altitude advantage ({altitude:.0f}ft): +{alt_boost:.3f}")
        elif context.home_team == result_b.team:
            result_b.adjusted_probability += alt_boost
            result_b.total_adjustment += alt_boost
            result_b.adjustments.append(f"Altitude advantage ({altitude:.0f}ft): +{alt_boost:.3f}")


def _apply_travel_fatigue(
    result_a: EnvironmentResult,
    result_b: EnvironmentResult,
    context: GameContext,
) -> None:
    """Model travel fatigue based on distance and timezone crossing."""
    home_city = context.venue_city or ""
    away_city = _infer_city(result_b.team if context.home_team == result_a.team else result_a.team)

    if not home_city or not away_city:
        return

    home_coords = CITY_COORDINATES.get(home_city)
    away_coords = CITY_COORDINATES.get(away_city)

    if not home_coords or not away_coords:
        return

    distance_km = _haversine(home_coords, away_coords)

    if distance_km < 500:
        return

    tz_home = CITY_TIMEZONE_OFFSETS.get(home_city, 0)
    tz_away = CITY_TIMEZONE_OFFSETS.get(away_city, 0)
    tz_diff = abs(tz_home - tz_away)

    distance_factor = min(distance_km / 5000.0, 1.0)
    tz_factor = min(tz_diff / 6.0, 1.0)
    travel_penalty = 0.008 * distance_factor + 0.006 * tz_factor

    if context.home_team == result_a.team:
        result_b.adjusted_probability -= travel_penalty
        result_b.total_adjustment -= travel_penalty
        if travel_penalty > 0.002:
            result_b.adjustments.append(
                f"Travel fatigue ({distance_km:.0f}km, {tz_diff}h TZ): -{travel_penalty:.3f}"
            )
    elif context.home_team == result_b.team:
        result_a.adjusted_probability -= travel_penalty
        result_a.total_adjustment -= travel_penalty
        if travel_penalty > 0.002:
            result_a.adjustments.append(
                f"Travel fatigue ({distance_km:.0f}km, {tz_diff}h TZ): -{travel_penalty:.3f}"
            )


def _haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate distance between two lat/lon points in km."""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return 6371 * c


def _infer_city(team_name: str) -> str:
    """Try to extract city from team name."""
    for city in CITY_COORDINATES:
        if city.lower() in team_name.lower():
            return city
    parts = team_name.rsplit(" ", 1)
    if len(parts) >= 1:
        candidate = parts[0]
        if candidate in CITY_COORDINATES:
            return candidate
    return ""


def _normalize_env(
    result_a: EnvironmentResult,
    result_b: EnvironmentResult,
) -> None:
    """Normalize adjusted probabilities to sum to 1.0."""
    result_a.adjusted_probability = max(0.02, min(0.98, result_a.adjusted_probability))
    result_b.adjusted_probability = max(0.02, min(0.98, result_b.adjusted_probability))

    total = result_a.adjusted_probability + result_b.adjusted_probability
    if abs(total - 1.0) > 0.001:
        result_a.adjusted_probability /= total
        result_b.adjusted_probability /= total
