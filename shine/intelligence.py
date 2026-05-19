"""Context and big-competition adjustment layer for Shine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shine.models import Adjustment, EntityContext, MoneylineEvent
from shine.odds_math import add_logit_delta


BIG_COMPETITION_KEYWORDS = (
    "playoff",
    "final",
    "champions league",
    "world cup",
    "worlds",
    "major",
    "masters",
    "champions",
    "ppv",
    "title fight",
    "grand final",
)

ELITE_COMPETITION_SPORT_KEYS = {
    "soccer_uefa_champs_league",
    "esports_cs2",
    "esports_lol",
    "esports_valorant",
    "mma_mixed_martial_arts",
}


@dataclass(frozen=True)
class EventContext:
    big_competition: bool = False
    venue_altitude_m: float = 0.0
    environment_tags: frozenset[str] = field(default_factory=frozenset)


class IntelligenceLayer:
    """Applies context adjustments without hiding the math behind opaque vibes."""

    def __init__(
        self,
        *,
        entities: dict[str, EntityContext] | None = None,
        events: dict[str, EventContext] | None = None,
        sport_big_competitions: set[str] | None = None,
    ) -> None:
        self.entities = {_normalize_name(name): context for name, context in (entities or {}).items()}
        self.events = events or {}
        self.sport_big_competitions = sport_big_competitions or set()

    @classmethod
    def from_file(cls, path: str | Path) -> "IntelligenceLayer":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntelligenceLayer":
        entities = {
            name: EntityContext(
                pressure_rating=_clamp(float(values.get("pressure_rating", 0.0)), -1.0, 1.0),
                travel_km=max(0.0, float(values.get("travel_km", 0.0))),
                timezone_delta=max(0.0, float(values.get("timezone_delta", 0.0))),
                altitude_m=max(0.0, float(values.get("altitude_m", 0.0))),
                host_region_advantage=bool(values.get("host_region_advantage", False)),
                style_tags=frozenset(str(tag).lower() for tag in values.get("style_tags", [])),
            )
            for name, values in data.get("entities", {}).items()
        }
        events = {
            event_id: EventContext(
                big_competition=bool(values.get("big_competition", False)),
                venue_altitude_m=max(0.0, float(values.get("venue_altitude_m", 0.0))),
                environment_tags=frozenset(str(tag).lower() for tag in values.get("environment_tags", [])),
            )
            for event_id, values in data.get("events", {}).items()
        }
        sport_big_competitions = {
            str(sport_key)
            for sport_key, values in data.get("sports", {}).items()
            if bool(values.get("big_competition", False))
        }
        return cls(entities=entities, events=events, sport_big_competitions=sport_big_competitions)

    def context_for(self, participant: str) -> EntityContext:
        return self.entities.get(_normalize_name(participant), EntityContext())

    def event_context_for(self, event: MoneylineEvent) -> EventContext:
        configured = self.events.get(event.event_id)
        inferred_big_stage = self.is_big_competition(event)
        if configured is None:
            return EventContext(big_competition=inferred_big_stage)
        return EventContext(
            big_competition=configured.big_competition or inferred_big_stage,
            venue_altitude_m=configured.venue_altitude_m,
            environment_tags=configured.environment_tags,
        )

    def is_big_competition(self, event: MoneylineEvent) -> bool:
        if event.sport_key in self.sport_big_competitions or event.sport_key in ELITE_COMPETITION_SPORT_KEYS:
            return True
        haystack = " ".join(
            str(value)
            for value in [
                event.sport_key,
                event.sport_title,
                event.raw.get("sport_title"),
                event.raw.get("event_title"),
                event.raw.get("description"),
            ]
            if value
        ).lower()
        return any(keyword in haystack for keyword in BIG_COMPETITION_KEYWORDS)

    def adjust_probability(
        self,
        event: MoneylineEvent,
        participant: str,
        base_probability: float,
    ) -> tuple[float, tuple[Adjustment, ...], frozenset[str]]:
        entity = self.context_for(participant)
        event_context = self.event_context_for(event)
        adjustments: list[Adjustment] = []

        if participant == event.home_team:
            adjustments.append(Adjustment("home_advantage", 0.055, "Home side gets a small moneyline baseline boost."))

        if event_context.big_competition and entity.pressure_rating:
            delta = entity.pressure_rating * 0.14
            label = "pressure_boost" if delta > 0 else "pressure_penalty"
            adjustments.append(
                Adjustment(label, delta, "Big-stage pressure history from the intelligence profile.")
            )

        if entity.host_region_advantage:
            adjustments.append(Adjustment("host_region", 0.045, "Host-region familiarity improves execution."))

        if entity.travel_km:
            delta = -min(0.12, entity.travel_km / 10000.0 * 0.09)
            adjustments.append(Adjustment("travel_load", delta, "Long travel load reduces expected performance."))

        if entity.timezone_delta:
            delta = -min(0.08, entity.timezone_delta * 0.015)
            adjustments.append(Adjustment("timezone_load", delta, "Time-zone displacement reduces expected performance."))

        if event_context.venue_altitude_m and entity.altitude_m < event_context.venue_altitude_m * 0.6:
            delta = -min(0.06, event_context.venue_altitude_m / 2500.0 * 0.04)
            adjustments.append(Adjustment("altitude_penalty", delta, "Venue altitude is materially above the profile baseline."))

        adjusted = base_probability
        for adjustment in adjustments:
            adjusted = add_logit_delta(adjusted, adjustment.delta)

        style_tags = entity.style_tags | event_context.environment_tags
        return adjusted, tuple(adjustments), style_tags


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _clamp(value: float, floor: float, ceiling: float) -> float:
    return max(floor, min(ceiling, value))
