"""Environmental adjustment layer.

Accounts for travel distance, timezone delta, altitude, home-court advantage,
and host-region advantage. Each factor produces a small additive shift to the
home team's true probability (negative = away team benefits).

The combined shift is clamped and probabilities are re-normalized.
"""

from __future__ import annotations
import math
from shine.odds.models import Game

# ── Venue database (city → lat, lon, altitude_m, timezone_utc_offset) ────────
# Populated with major North American + EU cities. Extend as needed.
VENUES: dict[str, tuple[float, float, int, int]] = {
    # NBA / NFL / MLB / NHL cities — (lat, lon, altitude_m, tz_offset)
    "boston": (42.36, -71.06, 43, -5),
    "new york": (40.71, -74.01, 10, -5),
    "brooklyn": (40.68, -73.94, 10, -5),
    "philadelphia": (39.95, -75.17, 12, -5),
    "miami": (25.76, -80.19, 2, -5),
    "atlanta": (33.75, -84.39, 320, -5),
    "chicago": (41.88, -87.63, 181, -6),
    "milwaukee": (43.04, -87.91, 188, -6),
    "cleveland": (41.50, -81.69, 199, -5),
    "detroit": (42.33, -83.05, 183, -5),
    "indianapolis": (39.77, -86.16, 218, -5),
    "toronto": (43.65, -79.38, 76, -5),
    "dallas": (32.78, -96.80, 131, -6),
    "houston": (29.76, -95.37, 15, -6),
    "san antonio": (29.42, -98.49, 198, -6),
    "memphis": (35.15, -90.05, 102, -6),
    "new orleans": (29.95, -90.07, 2, -6),
    "oklahoma city": (35.47, -97.52, 395, -6),
    "minneapolis": (44.98, -93.27, 264, -6),
    "denver": (39.74, -104.99, 1609, -7),
    "salt lake city": (40.76, -111.89, 1288, -7),
    "portland": (45.52, -122.68, 15, -8),
    "seattle": (47.61, -122.33, 52, -8),
    "sacramento": (38.58, -121.49, 9, -8),
    "san francisco": (37.77, -122.42, 16, -8),
    "oakland": (37.80, -122.27, 13, -8),
    "los angeles": (34.05, -118.24, 71, -8),
    "phoenix": (33.45, -112.07, 331, -7),
    "las vegas": (36.17, -115.14, 620, -8),
    "tampa": (27.95, -82.46, 14, -5),
    "jacksonville": (30.33, -81.66, 8, -5),
    "nashville": (36.16, -86.78, 182, -6),
    "charlotte": (35.23, -80.84, 229, -5),
    "washington": (38.91, -77.04, 22, -5),
    "pittsburgh": (40.44, -80.00, 230, -5),
    "baltimore": (39.29, -76.61, 10, -5),
    "green bay": (44.51, -88.02, 180, -6),
    "kansas city": (39.10, -94.58, 277, -6),
    # Soccer / Esports EU
    "london": (51.51, -0.13, 11, 0),
    "manchester": (53.48, -2.24, 38, 0),
    "liverpool": (53.41, -2.98, 30, 0),
    "madrid": (40.42, -3.70, 667, 1),
    "barcelona": (41.39, 2.17, 12, 1),
    "paris": (48.86, 2.35, 35, 1),
    "munich": (48.14, 11.58, 520, 1),
    "milan": (45.46, 9.19, 120, 1),
    "rome": (41.90, 12.50, 21, 1),
    "berlin": (52.52, 13.41, 34, 1),
    "istanbul": (41.01, 28.98, 39, 3),
    "mexico city": (19.43, -99.13, 2240, -6),
    "bogota": (4.71, -74.07, 2640, -5),
    "sao paulo": (-23.55, -46.63, 760, -3),
    "buenos aires": (-34.60, -58.38, 25, -3),
    # Esports hubs
    "seoul": (37.57, 126.98, 38, 9),
    "shanghai": (31.23, 121.47, 4, 8),
    "copenhagen": (55.68, 12.57, 14, 1),
    "katowice": (50.26, 19.02, 284, 1),
    "cologne": (50.94, 6.96, 53, 1),
    "reykjavik": (64.15, -21.94, 0, 0),
    "los angeles esports": (34.05, -118.24, 71, -8),
}

# ── Tuning knobs ─────────────────────────────────────────────────────────────
HOME_ADVANTAGE: dict[str, float] = {
    "NBA": 0.030,
    "NFL": 0.025,
    "MLB": 0.020,
    "NHL": 0.022,
    "soccer": 0.040,
    "soccer_champions_league": 0.035,
    "soccer_mls": 0.038,
    "soccer_la_liga": 0.040,
    "soccer_bundesliga": 0.038,
    "soccer_serie_a": 0.040,
    "soccer_ligue_one": 0.035,
    "CS2": 0.010,  # LAN events reduce home edge
    "LoL": 0.008,
    "VAL": 0.008,
    "UFC": 0.005,
}

TRAVEL_PENALTY_PER_1000KM = 0.006
TIMEZONE_PENALTY_PER_HOUR = 0.004
ALTITUDE_BONUS_PER_500M = 0.008  # home team acclimated, away is not
MAX_ENV_SHIFT = 0.07


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two lat/lon pairs."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _guess_city(team_name: str) -> str | None:
    """Naively extract city from team name by matching known venue cities."""
    lower = team_name.lower()
    for city in VENUES:
        if city in lower:
            return city
    return None


def compute_env_shift(game: Game) -> float:
    """Return a probability shift favouring home (positive) or away (negative).

    Components:
      - base home advantage (sport-specific)
      - away-team travel penalty
      - timezone crossing penalty for away team
      - altitude advantage for home team
    """
    shift = HOME_ADVANTAGE.get(game.sport, 0.02)

    home_city = _guess_city(game.home.name)
    away_city = _guess_city(game.away.name)
    if home_city and away_city and home_city in VENUES and away_city in VENUES:
        h = VENUES[home_city]
        a = VENUES[away_city]

        dist_km = _haversine(h[0], h[1], a[0], a[1])
        shift += (dist_km / 1000) * TRAVEL_PENALTY_PER_1000KM

        tz_delta = abs(h[3] - a[3])
        shift += tz_delta * TIMEZONE_PENALTY_PER_HOUR

        alt_diff = h[2] - a[2]
        if alt_diff > 0:
            shift += (alt_diff / 500) * ALTITUDE_BONUS_PER_500M

    return max(-MAX_ENV_SHIFT, min(MAX_ENV_SHIFT, shift))


def apply_environment(game: Game) -> Game:
    """Adjust game probabilities based on environmental factors."""
    shift = compute_env_shift(game)

    new_home = game.home.true_prob + shift
    new_away = game.away.true_prob - shift

    new_home = max(0.01, min(0.99, new_home))
    new_away = max(0.01, min(0.99, new_away))
    total = new_home + new_away
    game.home.true_prob = new_home / total
    game.away.true_prob = new_away / total
    return game
