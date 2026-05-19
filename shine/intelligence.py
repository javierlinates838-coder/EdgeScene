from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence


@dataclass(frozen=True)
class CompetitionProfile:
    pressure_boost: float
    clutch_index: float
    choke_risk: float


# Example priors. Extend with richer historical modeling over time.
BIG_STAGE_PRIORS: Dict[str, CompetitionProfile] = {
    "nba_playoffs": CompetitionProfile(pressure_boost=0.05, clutch_index=0.04, choke_risk=-0.03),
    "nfl_playoffs": CompetitionProfile(pressure_boost=0.06, clutch_index=0.03, choke_risk=-0.03),
    "champions_league": CompetitionProfile(pressure_boost=0.05, clutch_index=0.05, choke_risk=-0.04),
    "cs2_major": CompetitionProfile(pressure_boost=0.07, clutch_index=0.04, choke_risk=-0.05),
    "lol_worlds": CompetitionProfile(pressure_boost=0.06, clutch_index=0.04, choke_risk=-0.04),
    "val_champions": CompetitionProfile(pressure_boost=0.06, clutch_index=0.04, choke_risk=-0.04),
    "ufc_ppv": CompetitionProfile(pressure_boost=0.04, clutch_index=0.05, choke_risk=-0.03),
}


def pressure_adjustment(
    base_probability: float,
    team_or_player: str,
    competition_tag: str | None,
    pressure_weight: float,
) -> float:
    """Apply pressure-performance uplift or penalty in multiplier space."""
    if not competition_tag:
        return 1.0

    profile = BIG_STAGE_PRIORS.get(competition_tag)
    if profile is None:
        return 1.0

    # Placeholder deterministic personality prior:
    # teams/players with certain naming patterns get a slight clutch lean.
    # Replace with a learned metric once historical event data is integrated.
    identity_signal = _identity_pressure_signal(team_or_player)
    profile_signal = profile.pressure_boost + profile.clutch_index + profile.choke_risk
    weighted = (identity_signal + profile_signal) * pressure_weight
    return 1.0 + weighted


def _identity_pressure_signal(team_or_player: str) -> float:
    text = team_or_player.lower()
    positive_cues: Sequence[str] = ("champ", "dynasty", "legacy", "major", "prime")
    negative_cues: Sequence[str] = ("rookie", "new", "academy", "mix")

    score = 0.0
    for cue in positive_cues:
        if cue in text:
            score += 0.02
    for cue in negative_cues:
        if cue in text:
            score -= 0.02
    return score
