from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import requests

from .models import EventMarket, OddsBookPrice

THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4"


class OddsApiClient:
    def __init__(self, api_key: str, base_url: str = THE_ODDS_API_BASE, timeout: float = 20.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_moneyline_markets(
        self,
        sport_key: str,
        regions: str = "us,eu,uk",
        bookmakers: Optional[str] = None,
    ) -> List[EventMarket]:
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": "h2h",
            "oddsFormat": "decimal",
            "dateFormat": "iso",
        }
        if bookmakers:
            params["bookmakers"] = bookmakers

        url = f"{self.base_url}/sports/{sport_key}/odds"
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        return [self._parse_event(event, sport_key=sport_key) for event in payload]

    @staticmethod
    def _parse_event(event: dict, sport_key: str) -> EventMarket:
        prices: List[OddsBookPrice] = []
        for bookmaker in event.get("bookmakers", []):
            book_name = bookmaker.get("title", bookmaker.get("key", "unknown"))
            for market in bookmaker.get("markets", []):
                if market.get("key") != "h2h":
                    continue
                for outcome in market.get("outcomes", []):
                    raw_price = outcome.get("price")
                    if raw_price is None:
                        continue
                    prices.append(
                        OddsBookPrice(
                            bookmaker=book_name,
                            selection=outcome.get("name", ""),
                            decimal_odds=float(raw_price),
                        )
                    )
        return EventMarket(
            event_id=event["id"],
            sport_key=sport_key,
            home_team=event.get("home_team", ""),
            away_team=event.get("away_team", ""),
            commence_time=datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00")).astimezone(
                timezone.utc
            ),
            prices=prices,
        )
