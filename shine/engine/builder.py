"""High-level Shine engine: pull odds, build legs, search parlays."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence

from ..correlation.engine import CorrelationEngine
from ..models import Event, Leg, Parlay
from ..odds.client import OddsAPIClient
from ..odds.sports import sport_keys_for
from .ev import build_parlay
from .leg_factory import LegFactory, LegFactoryConfig


@dataclass
class BuildConfig:
    sports: List[str] = field(default_factory=lambda: ["nba", "nfl", "soccer"])
    min_legs: int = 2
    max_legs: int = 5
    min_ev_pct: float = 0.0
    min_leg_edge_pct: float = 0.5
    top_n: int = 10
    devig_method: str = "shin"


class ShineEngine:
    """Orchestrates the whole pipeline."""

    def __init__(
        self,
        client: Optional[OddsAPIClient] = None,
        *,
        leg_factory: Optional[LegFactory] = None,
        correlator: Optional[CorrelationEngine] = None,
    ) -> None:
        self.client = client or OddsAPIClient()
        self.leg_factory = leg_factory or LegFactory()
        self.correlator = correlator or CorrelationEngine()

    # ------------------------------------------------------------------ data
    def fetch_events(self, sports: Sequence[str]) -> List[Event]:
        keys = sport_keys_for(list(sports))
        return self.client.fetch_events(keys)

    def candidate_legs(self, events: Iterable[Event], *, min_edge_pct: float = 0.0) -> List[Leg]:
        legs: List[Leg] = []
        for ev in events:
            for leg in self.leg_factory.build(ev):
                if leg.edge_pct >= min_edge_pct:
                    legs.append(leg)
        legs.sort(key=lambda l: l.edge_pct, reverse=True)
        return legs

    # ------------------------------------------------------------------ search
    def build_parlays(self, cfg: BuildConfig, events: Optional[List[Event]] = None) -> List[Parlay]:
        if events is None:
            events = self.fetch_events(cfg.sports)

        legs = self.candidate_legs(events, min_edge_pct=cfg.min_leg_edge_pct)
        if len(legs) < cfg.min_legs:
            return []

        # Greedy search with diversity: start from the top-edge leg, then
        # repeatedly add the leg that maximizes parlay EV until we either
        # hit max_legs or further legs no longer help.
        # We also generate parlays of every size in [min_legs, max_legs].
        parlays: List[Parlay] = []
        seen_combos: set = set()

        # Limit the candidate pool to keep search tractable.
        pool = legs[: max(20, cfg.max_legs * 6)]

        # Avoid stacking two legs from the same event (same picks especially).
        def can_add(existing: List[Leg], candidate: Leg) -> bool:
            for l in existing:
                if l.event.id == candidate.event.id and candidate.event.id:
                    return False
            return True

        # For each starting leg, try a greedy expansion up to max_legs.
        for start in pool[: min(len(pool), 30)]:
            current = [start]
            for _ in range(cfg.max_legs - 1):
                best_next = None
                best_ev = float("-inf")
                for cand in pool:
                    if cand is start or cand in current:
                        continue
                    if not can_add(current, cand):
                        continue
                    trial = current + [cand]
                    p = build_parlay(trial, self.correlator)
                    if p.ev_pct > best_ev:
                        best_ev = p.ev_pct
                        best_next = cand
                if best_next is None:
                    break
                current.append(best_next)
                if len(current) >= cfg.min_legs:
                    combo_key = tuple(sorted((l.event.id or l.pick, l.pick) for l in current))
                    if combo_key not in seen_combos:
                        seen_combos.add(combo_key)
                        parlays.append(build_parlay(list(current), self.correlator))

        parlays = [p for p in parlays if p.ev_pct >= cfg.min_ev_pct]
        parlays.sort(key=lambda p: p.ev_pct, reverse=True)
        return parlays[: cfg.top_n]
