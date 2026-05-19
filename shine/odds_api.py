from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen

from .math_utils import american_to_implied_probability, remove_vig
from .models import EventOdds, TeamOdds


DEFAULT_BASE_URL = "https://api.the-odds-api.com/v4"


@dataclass
class OddsApiClient:
    api_key: str
    base_url: str = DEFAULT_BASE_URL

    def fetch_moneyline_odds(
        self,
        sports: Iterable[str],
        regions: str = "us",
        markets: str = "h2h",
        bookmakers: Optional[str] = None,
        odds_format: str = "american",
    ) -> List[EventOdds]:
        events: List[EventOdds] = []
        for sport_key in sports:
            path = f"/sports/{sport_key}/odds"
            params: Dict[str, str] = {
                "apiKey": self.api_key,
                "regions": regions,
                "markets": markets,
                "oddsFormat": odds_format,
            }
            if bookmakers:
                params["bookmakers"] = bookmakers
            raw = self._get_json(path=path, query=params)
            events.extend(self._extract_events(raw, sport_key))
        return events

    def _get_json(self, path: str, query: Dict[str, str]) -> List[dict]:
        url = f"{self.base_url}{path}?{urlencode(query)}"
        with urlopen(url, timeout=30) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        if not isinstance(data, list):
            raise ValueError("Unexpected TheOddsAPI payload.")
        return data

    def _extract_events(self, payload: List[dict], fallback_sport_key: str) -> List[EventOdds]:
        events: List[EventOdds] = []
        for item in payload:
            bookmakers = item.get("bookmakers", [])
            if not bookmakers:
                continue

            market_data = self._extract_market(bookmakers)
            if market_data is None:
                continue

            bookmaker_title, outcomes = market_data
            if len(outcomes) < 2:
                continue

            implied = [american_to_implied_probability(o["price"]) for o in outcomes]
            true_probabilities = remove_vig(implied)
            teams = [
                TeamOdds(
                    team=str(outcome["name"]),
                    american_odds=int(outcome["price"]),
                    implied_probability=implied_prob,
                    true_probability=true_prob,
                )
                for outcome, implied_prob, true_prob in zip(outcomes, implied, true_probabilities)
            ]

            events.append(
                EventOdds(
                    sport_key=str(item.get("sport_key", fallback_sport_key)),
                    sport_title=str(item.get("sport_title", fallback_sport_key)),
                    event_id=str(item["id"]),
                    commence_time=str(item.get("commence_time", "")),
                    home_team=str(item.get("home_team", "")),
                    away_team=str(item.get("away_team", "")),
                    bookmaker=bookmaker_title,
                    teams=teams,
                )
            )
        return events

    @staticmethod
    def _extract_market(bookmakers: List[dict]) -> Optional[tuple[str, List[dict]]]:
        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    outcomes = market.get("outcomes", [])
                    if all(isinstance(out.get("price"), int) for out in outcomes):
                        return str(bookmaker.get("title", "unknown")), outcomes
        return None
