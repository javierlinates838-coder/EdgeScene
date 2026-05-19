"""Central configuration for the Shine engine."""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API ──────────────────────────────────────────────────────────────────────
ODDS_API_KEY: str = os.getenv("ODDS_API_KEY", "")
ODDS_API_BASE: str = "https://api.the-odds-api.com/v4"

# ── Sport keys recognized by TheOddsAPI ──────────────────────────────────────
SPORT_KEYS: dict[str, str] = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "soccer": "soccer_epl",
    "soccer_champions_league": "soccer_uefa_champions_league",
    "soccer_mls": "soccer_usa_mls",
    "soccer_la_liga": "soccer_spain_la_liga",
    "soccer_bundesliga": "soccer_germany_bundesliga",
    "soccer_serie_a": "soccer_italy_serie_a",
    "soccer_ligue_one": "soccer_france_ligue_one",
    "CS2": "csgo",  # TheOddsAPI still uses the csgo key
    "LoL": "lol",
    "VAL": "valorant",
    "UFC": "mma_mixed_martial_arts",
}

# ── Bookmaker preference (first match wins) ─────────────────────────────────
PREFERRED_BOOKS: list[str] = [
    "fanduel",
    "draftkings",
    "betmgm",
    "caesars",
    "pointsbet",
    "bovada",
    "betonlineag",
    "pinnacle",
]

# ── EV tier thresholds ───────────────────────────────────────────────────────
EV_TIERS: dict[str, float] = {
    "S": 0.15,   # ≥15 % edge
    "A": 0.08,   # ≥ 8 %
    "B": 0.03,   # ≥ 3 %
    "C": 0.00,   # ≥ 0 % (break-even or better)
    "D": -999.0, # anything worse
}

# ── Parlay constraints ───────────────────────────────────────────────────────
MIN_LEGS: int = 2
MAX_LEGS: int = 8
MIN_LEG_PROB: float = 0.30  # ignore heavy underdogs below 30 %

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
