from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .math_utils import american_to_implied_probability, remove_vig
from .models import EventOdds, TeamOdds


DEFAULT_BASE_URL = "https://api.the-odds-api.com/v4"


class OddsApiError(RuntimeError):
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


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
        try:
            with urlopen(url, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="ignore")
            message = self._extract_error_message(body) or error.reason or "request failed"
            raise OddsApiError(str(message), status_code=error.code) from error
        except URLError as error:
            raise OddsApiError(f"network error: {error.reason}") from error

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as error:
            raise OddsApiError("invalid JSON returned by TheOddsAPI") from error
        if not isinstance(data, list):
            raise OddsApiError("unexpected payload format returned by TheOddsAPI")
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

    @staticmethod
    def _extract_error_message(raw_body: str) -> Optional[str]:
        if not raw_body:
            return None
        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError:
            return raw_body.strip() or None
        if isinstance(parsed, dict):
            for key in ("message", "error", "detail"):
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return raw_body.strip() or None
