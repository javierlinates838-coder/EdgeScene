"""Big-competition pressure performance model.

Given a team and the stage of the competition, produce a multiplier that
adjusts the team's fair win probability. Pressure ratings come from
``shine/data/pressure_ratings.json`` and only fire in big-stage matchups
(i.e. when ``StageDetector`` returned a non-regular stage).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ._loader import load_json, normalize_name


@dataclass
class PressureAdjustment:
    multiplier: float
    note: str


class PressureModel:
    def __init__(self) -> None:
        self._ratings = load_json("pressure_ratings.json")["ratings"]

    def rating(self, team: str) -> float:
        return float(self._ratings.get(normalize_name(team), 1.0))

    def adjust(self, team: str, *, on_big_stage: bool) -> PressureAdjustment:
        r = self.rating(team)
        if not on_big_stage:
            # Compress pressure effects when it's a regular game; the team's
            # mental edge matters far less when nothing is at stake.
            r = 1.0 + (r - 1.0) * 0.25
        if r > 1.0:
            note = f"{team} historically rises ({(r - 1) * 100:+.1f}% pressure)"
        elif r < 1.0:
            note = f"{team} historically chokes ({(r - 1) * 100:+.1f}% pressure)"
        else:
            note = ""
        return PressureAdjustment(multiplier=r, note=note)
