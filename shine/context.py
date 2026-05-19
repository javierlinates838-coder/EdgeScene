from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ContextInput:
    travel_km: float = 0.0
    timezone_shift_hours: float = 0.0
    altitude_meters: float = 0.0
    home_team: bool = False
    host_region_advantage: bool = False


def travel_environment_multiplier(
    context: ContextInput,
    travel_weight: float,
    home_advantage_weight: float,
    host_region_weight: float,
) -> float:
    """Compute a bounded multiplier from travel + environment context."""
    travel_drag = -(context.travel_km / 1000.0) * (travel_weight * 0.20)
    timezone_drag = -abs(context.timezone_shift_hours) * (travel_weight * 0.03)
    altitude_effect = -(context.altitude_meters / 1000.0) * (travel_weight * 0.02)
    home_bump = home_advantage_weight if context.home_team else 0.0
    host_bump = host_region_weight if context.host_region_advantage else 0.0

    total = travel_drag + timezone_drag + altitude_effect + home_bump + host_bump
    return 1.0 + total
