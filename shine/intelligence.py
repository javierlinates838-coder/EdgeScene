from __future__ import annotations

from typing import Dict

from .models import LegContext

# Stage multipliers are conservative by design to avoid overfitting.
STAGE_PRESSURE_MULTIPLIERS: Dict[str, float] = {
    "regular": 1.0,
    "playoffs": 1.03,
    "semifinal": 1.035,
    "final": 1.05,
    "major": 1.045,
    "championship": 1.05,
    "title_fight": 1.04,
}


def clamp_probability(probability: float) -> float:
    """Keep probabilities inside a stable, non-degenerate range."""
    return max(0.01, min(0.99, probability))


def pressure_multiplier(stage: str) -> float:
    key = stage.strip().lower()
    return STAGE_PRESSURE_MULTIPLIERS.get(key, 1.0)


def travel_multiplier(travel_miles: float, timezone_shift: int) -> float:
    """
    Apply mild penalty for heavier travel burden.

    Each 500 miles trims 0.4% and each timezone shift trims 0.6%.
    """
    miles_penalty = (max(travel_miles, 0.0) / 500.0) * 0.004
    timezone_penalty = abs(timezone_shift) * 0.006
    multiplier = 1.0 - miles_penalty - timezone_penalty
    return max(0.92, multiplier)


def environment_multiplier(
    altitude_meters: float,
    host_region_advantage: float,
    weather_severity: float,
) -> float:
    """
    Blend environment effects:
    - Altitude: up to +2.0% bonus for acclimated side.
    - Host region advantage: direct scalar from caller (0.0-0.03 typical).
    - Weather severity: up to -3.0% if conditions are poor.
    """
    altitude_boost = min(max(altitude_meters, 0.0) / 2500.0, 1.0) * 0.02
    host_boost = max(-0.03, min(0.03, host_region_advantage))
    weather_penalty = max(0.0, min(1.0, weather_severity)) * 0.03
    return 1.0 + altitude_boost + host_boost - weather_penalty


def apply_context_adjustments(base_probability: float, context: LegContext) -> Dict[str, float]:
    p_mult = pressure_multiplier(context.stage)
    t_mult = travel_multiplier(context.travel_miles, context.timezone_shift)
    e_mult = environment_multiplier(
        altitude_meters=context.altitude_meters,
        host_region_advantage=context.host_region_advantage,
        weather_severity=context.weather_severity,
    )
    adjusted = clamp_probability(base_probability * p_mult * t_mult * e_mult)
    return {
        "adjusted_probability": adjusted,
        "pressure_multiplier": p_mult,
        "travel_multiplier": t_mult,
        "environment_multiplier": e_mult,
    }
