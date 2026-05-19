"""Build candidate legs from raw events using all of Shine's intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..context.environment import EnvironmentModel
from ..context.travel import TravelModel
from ..intelligence.pressure import PressureModel
from ..intelligence.stage import StageDetector
from ..math.devig import devig
from ..models import Event, Leg


@dataclass
class LegFactoryConfig:
    devig_method: str = "shin"
    min_book_decimal: float = 1.20  # skip ultra-heavy chalk by default
    max_book_decimal: float = 8.00  # skip massive longshots by default


class LegFactory:
    def __init__(self, cfg: Optional[LegFactoryConfig] = None) -> None:
        self.cfg = cfg or LegFactoryConfig()
        self.stage = StageDetector()
        self.pressure = PressureModel()
        self.travel = TravelModel()
        self.environment = EnvironmentModel()

    def build(self, event: Event) -> List[Leg]:
        if len(event.outcomes) < 2:
            return []

        implied = [o.implied_prob for o in event.outcomes]
        try:
            fair_probs = devig(implied, method=self.cfg.devig_method)
        except Exception:
            fair_probs = devig(implied, method="multiplicative")

        stage = self.stage.detect(event)
        on_big_stage = bool(stage and stage.boost > 1.0)

        legs: List[Leg] = []
        for outcome, fair in zip(event.outcomes, fair_probs):
            if outcome.decimal_odds < self.cfg.min_book_decimal:
                continue
            if outcome.decimal_odds > self.cfg.max_book_decimal:
                continue

            notes: List[str] = []
            adjusted = fair

            press = self.pressure.adjust(outcome.name, on_big_stage=on_big_stage)
            if press.multiplier != 1.0:
                adjusted *= press.multiplier
                if press.note:
                    notes.append(press.note)

            if stage:
                # On a big stage we tilt confidence toward the team Shine
                # already favors: amplify the deviation from 50/50.
                adjusted = 0.5 + (adjusted - 0.5) * stage.boost
                notes.append(f"stage: {stage.name} (boost {stage.boost:.2f}x)")

            is_home = outcome.name.lower() == (event.home_team or "").lower()
            env = self.environment.evaluate(event.sport_key, event.home_team, event.away_team)
            if is_home and env.home_edge:
                adjusted += env.home_edge
            if (not is_home) and env.altitude_penalty:
                adjusted -= env.altitude_penalty
            if env.note:
                notes.append(env.note)

            travel = self.travel.evaluate(event.home_team, event.away_team)
            if travel and travel.away_penalty:
                if not is_home:
                    adjusted -= travel.away_penalty
                if travel.note:
                    notes.append(travel.note)

            # Renormalize lightly back into (0,1)
            adjusted = max(0.01, min(0.99, adjusted))

            legs.append(
                Leg(
                    event=event,
                    pick=outcome.name,
                    book_decimal=outcome.decimal_odds,
                    fair_prob=fair,
                    adjusted_prob=adjusted,
                    notes=notes,
                )
            )
        return legs
