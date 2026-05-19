"""Environment adjustments: altitude, home edge, weather hooks, host region."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..intelligence._loader import load_json, normalize_name


@dataclass
class EnvironmentAdjustment:
    home_edge: float          # extra probability awarded to home team
    altitude_penalty: float   # extra probability penalty on away team
    host_region_bonus: float  # bonus for a team from the host region (neutral events)
    note: str


class EnvironmentModel:
    def __init__(self) -> None:
        self._venues = load_json("venues.json")["venues"]
        self._neutral_hosts = load_json("venues.json").get("neutral_hosts", {})
        edges = load_json("home_edge.json")["edges"]
        # Allow soccer to share a single value across all leagues
        self._sport_edges = edges

    def _home_edge_for(self, sport_key: str) -> float:
        if sport_key in self._sport_edges:
            return self._sport_edges[sport_key]
        if sport_key.startswith("soccer"):
            return self._sport_edges.get("soccer", 0.06)
        return 0.02

    def evaluate(
        self,
        sport_key: str,
        home_team: str,
        away_team: str,
        *,
        neutral_host: Optional[str] = None,
        team_region: Optional[str] = None,
    ) -> EnvironmentAdjustment:
        notes = []
        home_edge = 0.0 if neutral_host else self._home_edge_for(sport_key)
        if home_edge:
            notes.append(f"home edge {home_edge*100:.1f}%")

        altitude_penalty = 0.0
        home = self._venues.get(normalize_name(home_team))
        away = self._venues.get(normalize_name(away_team))
        if home and away and not neutral_host:
            alt_diff = home.get("alt_m", 0) - away.get("alt_m", 0)
            if alt_diff > 800:
                altitude_penalty = min(0.04, (alt_diff - 800) / 1000.0 * 0.015)
                notes.append(f"altitude +{alt_diff:.0f}m vs visitor")

        host_bonus = 0.0
        if neutral_host and team_region:
            host = self._neutral_hosts.get(neutral_host)
            if host and host.get("favored_region") == team_region:
                host_bonus = 0.025
                notes.append(f"host crowd ({host['city']}) favors {team_region}")

        return EnvironmentAdjustment(
            home_edge=home_edge,
            altitude_penalty=altitude_penalty,
            host_region_bonus=host_bonus,
            note=", ".join(notes),
        )
