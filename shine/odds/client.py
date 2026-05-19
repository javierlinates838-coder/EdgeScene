"""TheOddsAPI client — pulls live moneyline odds for all configured sports."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

import requests

from shine.config import ODDS_API_KEY, ODDS_API_BASE, SPORT_KEYS, PREFERRED_BOOKS
from shine.odds.models import TeamOdds, Game


def _pick_bookmaker(bookmakers: list[dict]) -> Optional[dict]:
    """Return the first bookmaker matching our preference list, else first available."""
    by_key = {b["key"]: b for b in bookmakers}
    for pref in PREFERRED_BOOKS:
        if pref in by_key:
            return by_key[pref]
    return bookmakers[0] if bookmakers else None


def _extract_h2h(markets: list[dict]) -> Optional[dict]:
    for m in markets:
        if m["key"] == "h2h":
            return m
    return None


def fetch_games(sport_key: str, league_label: str) -> list[Game]:
    """Fetch upcoming moneyline odds for a single sport key."""
    if not ODDS_API_KEY:
        raise RuntimeError("ODDS_API_KEY is not set. Add it to .env")

    url = f"{ODDS_API_BASE}/sports/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us,eu",
        "markets": "h2h",
        "oddsFormat": "american",
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    games: list[Game] = []
    for event in data:
        book = _pick_bookmaker(event.get("bookmakers", []))
        if book is None:
            continue
        market = _extract_h2h(book.get("markets", []))
        if market is None:
            continue

        outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
        home_team = event.get("home_team", "")
        away_team = event.get("away_team", "")
        if home_team not in outcomes or away_team not in outcomes:
            continue

        commence = datetime.fromisoformat(
            event["commence_time"].replace("Z", "+00:00")
        )

        games.append(
            Game(
                id=event["id"],
                sport=league_label,
                league=league_label,
                commence_time=commence,
                home=TeamOdds(name=home_team, american_odds=outcomes[home_team]),
                away=TeamOdds(name=away_team, american_odds=outcomes[away_team]),
                bookmaker=book["key"],
            )
        )
    return games


def fetch_all_games() -> list[Game]:
    """Pull live odds for every configured sport."""
    all_games: list[Game] = []
    for label, sport_key in SPORT_KEYS.items():
        try:
            games = fetch_games(sport_key, label)
            all_games.extend(games)
        except Exception:
            pass  # sport may have no upcoming events
    return all_games
