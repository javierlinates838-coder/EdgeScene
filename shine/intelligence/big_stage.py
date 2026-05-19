"""Big-competition intelligence layer.

Adjusts true probabilities based on how teams/players historically perform
on the biggest stages: playoffs, majors, finals, PPVs, etc.

The approach:
  1.  Detect whether the current event is a "big stage" competition.
  2.  Look up each team/player in the pressure-performance database.
  3.  Apply a multiplier (boost for clutch, penalty for chokers).

Multipliers are bounded to avoid runaway values and re-normalized so the
two-side probabilities still sum to 1.
"""

from __future__ import annotations
from shine.odds.models import Game

# ── Big-stage competition identifiers ────────────────────────────────────────
BIG_STAGE_TAGS: dict[str, list[str]] = {
    "NBA": ["playoff", "finals", "play-in", "in-season tournament"],
    "NFL": ["playoff", "super bowl", "wild card", "divisional", "conference"],
    "MLB": ["playoff", "world series", "wild card", "division series", "championship series"],
    "NHL": ["playoff", "stanley cup", "conference finals"],
    "soccer": ["champions league", "world cup", "europa league", "copa america", "euro"],
    "soccer_champions_league": ["knockout", "final", "semi-final", "quarter-final"],
    "CS2": ["major", "blast premier", "iem katowice", "iem cologne", "rio"],
    "LoL": ["worlds", "msi", "finals", "playoffs"],
    "VAL": ["champions", "masters", "lock-in", "playoffs"],
    "UFC": ["ppv", "title fight", "championship", "main event"],
}

# ── Pressure performance database ───────────────────────────────────────────
# Maps normalized team/player names → big-stage multiplier.
# > 1.0 = clutch performer, < 1.0 = historically chokes.
# This would eventually be trained from historical data; seeded here with
# well-known examples across sports.
PRESSURE_DB: dict[str, float] = {
    # NBA
    "boston celtics": 1.06,
    "los angeles lakers": 1.05,
    "golden state warriors": 1.08,
    "miami heat": 1.07,
    "denver nuggets": 1.04,
    "milwaukee bucks": 0.96,
    "philadelphia 76ers": 0.94,
    "phoenix suns": 0.95,
    # NFL
    "kansas city chiefs": 1.10,
    "san francisco 49ers": 0.96,
    "philadelphia eagles": 1.03,
    "buffalo bills": 0.93,
    "dallas cowboys": 0.90,
    # MLB
    "los angeles dodgers": 1.05,
    "houston astros": 1.06,
    "new york yankees": 1.03,
    "atlanta braves": 0.97,
    # NHL
    "vegas golden knights": 1.05,
    "florida panthers": 1.04,
    "edmonton oilers": 1.03,
    "toronto maple leafs": 0.91,
    # Soccer
    "real madrid": 1.10,
    "manchester city": 1.04,
    "bayern munich": 1.03,
    "psg": 0.92,
    "atletico madrid": 1.05,
    "liverpool": 1.05,
    "inter milan": 1.02,
    # CS2
    "natus vincere": 1.08,
    "faze clan": 1.05,
    "g2 esports": 1.03,
    "team vitality": 1.04,
    "team liquid": 0.95,
    # LoL
    "t1": 1.12,
    "gen.g": 1.04,
    "jdg intel esports club": 1.03,
    "cloud9": 0.93,
    # VAL
    "sentinels": 1.06,
    "fnatic": 1.05,
    "drx": 1.04,
    "paper rex": 1.03,
    "loud": 1.05,
    # UFC (fighters)
    "islam makhachev": 1.08,
    "alex pereira": 1.07,
    "jon jones": 1.10,
    "israel adesanya": 0.96,
    "conor mcgregor": 1.04,
}

# ── Bounds ───────────────────────────────────────────────────────────────────
MAX_BOOST = 1.12
MIN_BOOST = 0.88


def _is_big_stage(game: Game) -> bool:
    """Heuristic: check the league label / game metadata for big-stage tags."""
    sport_tags = BIG_STAGE_TAGS.get(game.sport, [])
    searchable = f"{game.league} {game.id}".lower()
    return any(tag in searchable for tag in sport_tags)


def _lookup(team: str) -> float:
    return PRESSURE_DB.get(team.lower().strip(), 1.0)


def apply_big_stage(game: Game) -> Game:
    """Mutate game's true_prob for home/away based on pressure performance.

    Only applies when the game qualifies as a big-stage event.
    Always re-normalizes to keep probabilities summing to 1.
    """
    if not _is_big_stage(game):
        return game

    h_mult = max(MIN_BOOST, min(MAX_BOOST, _lookup(game.home.name)))
    a_mult = max(MIN_BOOST, min(MAX_BOOST, _lookup(game.away.name)))

    raw_h = game.home.true_prob * h_mult
    raw_a = game.away.true_prob * a_mult
    total = raw_h + raw_a
    if total > 0:
        game.home.true_prob = raw_h / total
        game.away.true_prob = raw_a / total
    return game
