"""Mapping of human sport names to TheOddsAPI sport keys."""

from __future__ import annotations

from typing import Dict, List

# Friendly alias -> list of TheOddsAPI sport keys. A single alias may map
# to several keys (e.g. "soccer" covers many leagues, "esports" covers
# multiple titles).
SPORTS: Dict[str, List[str]] = {
    "nba": ["basketball_nba"],
    "wnba": ["basketball_wnba"],
    "ncaab": ["basketball_ncaab"],
    "nfl": ["americanfootball_nfl"],
    "ncaaf": ["americanfootball_ncaaf"],
    "mlb": ["baseball_mlb"],
    "nhl": ["icehockey_nhl"],
    "ufc": ["mma_mixed_martial_arts"],
    "boxing": ["boxing_boxing"],
    "tennis": ["tennis_atp_french_open", "tennis_wta_french_open"],
    # Soccer — major competitions
    "soccer": [
        "soccer_epl",
        "soccer_uefa_champs_league",
        "soccer_uefa_europa_league",
        "soccer_spain_la_liga",
        "soccer_italy_serie_a",
        "soccer_germany_bundesliga",
        "soccer_france_ligue_one",
        "soccer_fifa_world_cup",
        "soccer_uefa_euro_qualification",
    ],
    # Esports
    "cs2": ["esports_counterstrike"],
    "lol": ["esports_lol"],
    "val": ["esports_valorant"],
    "dota": ["esports_dota2"],
    "esports": [
        "esports_counterstrike",
        "esports_lol",
        "esports_valorant",
        "esports_dota2",
    ],
}


def sport_keys_for(aliases: List[str]) -> List[str]:
    """Expand a list of friendly aliases into concrete TheOddsAPI keys."""
    out: List[str] = []
    for a in aliases:
        a = a.strip().lower()
        if not a:
            continue
        if a in SPORTS:
            out.extend(SPORTS[a])
        else:
            out.append(a)
    # Dedupe while preserving order
    seen = set()
    unique: List[str] = []
    for k in out:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique
