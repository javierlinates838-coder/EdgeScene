"""Detect competition stage (regular vs playoffs/majors/finals) from event metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ._loader import load_json
from ..models import Event


@dataclass
class StageInfo:
    name: str
    boost: float       # multiplicative confidence amplifier (>1 in big stages)


class StageDetector:
    def __init__(self) -> None:
        self._data = load_json("competitions.json")["stages"]

    def detect(self, event: Event) -> Optional[StageInfo]:
        cfg = self._data.get(event.sport_key)
        if not cfg:
            return None
        title = f"{event.sport_title} {event.league}".lower()
        # Search raw blob too for "stage"/"phase" hints if present
        raw = event.extra.get("raw") if isinstance(event.extra, dict) else None
        if isinstance(raw, dict):
            for k in ("stage", "phase", "tournament", "round"):
                v = raw.get(k)
                if isinstance(v, str):
                    title += " " + v.lower()
        best: Optional[StageInfo] = None
        for stage_name, stage_cfg in cfg.items():
            keywords = stage_cfg.get("keywords", [])
            for kw in keywords:
                if kw in title:
                    candidate = StageInfo(name=stage_name, boost=float(stage_cfg.get("stage_boost", 1.0)))
                    if best is None or candidate.boost > best.boost:
                        best = candidate
                    break
        return best
