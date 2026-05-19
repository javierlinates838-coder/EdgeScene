"""Travel-distance and time-zone adjustments.

Long-haul travel and large time-zone shifts measurably hurt visiting teams.
We model that as a small additive probability penalty on the away side.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from ..intelligence._loader import load_json, normalize_name


@dataclass
class TravelInfo:
    distance_km: float
    tz_hours: float
    away_penalty: float   # additive probability penalty on visiting team
    note: str


EARTH_R = 6371.0


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(a))


def _tz_offset_hours(tz: str) -> float:
    """Very small static map of common TZ -> UTC offset (hours).

    A real implementation would use ``zoneinfo`` with the event date, but
    static offsets are good enough for travel deltas where only the
    relative difference matters.
    """
    table = {
        "America/Los_Angeles": -8.0,
        "America/Denver": -7.0,
        "America/Phoenix": -7.0,
        "America/Chicago": -6.0,
        "America/New_York": -5.0,
        "America/Mexico_City": -6.0,
        "Europe/London": 0.0,
        "Europe/Madrid": 1.0,
        "Europe/Paris": 1.0,
        "Europe/Berlin": 1.0,
        "Europe/Copenhagen": 1.0,
        "Asia/Seoul": 9.0,
        "Asia/Shanghai": 8.0,
        "Asia/Tokyo": 9.0,
    }
    return table.get(tz, 0.0)


class TravelModel:
    def __init__(self) -> None:
        self._venues = load_json("venues.json")["venues"]

    def venue_for(self, team: str) -> Optional[dict]:
        return self._venues.get(normalize_name(team))

    def evaluate(self, home_team: str, away_team: str) -> Optional[TravelInfo]:
        home = self.venue_for(home_team)
        away = self.venue_for(away_team)
        if not home or not away:
            return None
        distance = _haversine(home["lat"], home["lon"], away["lat"], away["lon"])
        tz_shift = abs(_tz_offset_hours(home["tz"]) - _tz_offset_hours(away["tz"]))

        # Calibrated, gentle penalty: ~1% per 2000km plus 0.5% per TZ hour,
        # capped so a parlay leg cannot be obliterated by travel alone.
        penalty = min(0.06, distance / 2000.0 * 0.01 + tz_shift * 0.005)
        notes = []
        if distance > 1500:
            notes.append(f"{away_team} travels {distance:.0f}km")
        if tz_shift >= 2:
            notes.append(f"{tz_shift:.0f}h TZ shift")
        return TravelInfo(
            distance_km=distance,
            tz_hours=tz_shift,
            away_penalty=penalty,
            note=", ".join(notes),
        )
