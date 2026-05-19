"""TheOddsAPI client — pulls live moneyline odds across all sports."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

from shine.core.config import ALL_SPORTS, ShineConfig, Sport
from shine.core.models import MarketOdds, Odds
from shine.core.probability import american_to_implied

logger = logging.getLogger(__name__)

API_TIMEOUT = 15


@dataclass
class APIUsage:
    requests_used: int = 0
    requests_remaining: Optional[int] = None


class OddsAPIClient:
    """Client for TheOddsAPI v4."""

    def __init__(self, config: ShineConfig):
        self.config = config
        self.base_url = config.odds_api_base
        self.api_key = config.odds_api_key
        self.usage = APIUsage()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make an authenticated GET request."""
        if not self.api_key:
            raise ValueError(
                "No ODDS_API_KEY configured. Set it in .env or environment."
            )

        url = f"{self.base_url}{endpoint}"
        request_params = {"apiKey": self.api_key}
        if params:
            request_params.update(params)

        response = requests.get(url, params=request_params, timeout=API_TIMEOUT)

        remaining = response.headers.get("x-requests-remaining")
        used = response.headers.get("x-requests-used")
        if remaining is not None:
            self.usage.requests_remaining = int(remaining)
        if used is not None:
            self.usage.requests_used = int(used)

        response.raise_for_status()
        return response.json()

    def get_sports(self) -> List[Dict]:
        """Get all available sports from the API."""
        return self._get("/sports")

    def get_live_odds(
        self,
        sport: Sport,
        regions: Optional[str] = None,
        markets: str = "h2h",
    ) -> List[Dict]:
        """Pull live odds for a sport."""
        params = {
            "regions": regions or self.config.default_regions,
            "markets": markets,
            "oddsFormat": "american",
        }
        return self._get(f"/sports/{sport.value}/odds", params)

    def get_all_live_odds(
        self,
        sports: Optional[List[Sport]] = None,
        regions: Optional[str] = None,
    ) -> Dict[Sport, List[Dict]]:
        """Pull live odds for all specified sports."""
        target_sports = sports or ALL_SPORTS
        all_odds: Dict[Sport, List[Dict]] = {}

        for sport in target_sports:
            try:
                odds_data = self.get_live_odds(sport, regions)
                if odds_data:
                    all_odds[sport] = odds_data
                    logger.info(
                        f"Fetched {len(odds_data)} games for {sport.value}"
                    )
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 422:
                    logger.debug(f"Sport {sport.value} not available: {e}")
                else:
                    logger.warning(f"Error fetching {sport.value}: {e}")
            except Exception as e:
                logger.warning(f"Error fetching {sport.value}: {e}")

        return all_odds

    def parse_market_odds(self, game_data: Dict) -> Optional[MarketOdds]:
        """Parse raw API response into MarketOdds model."""
        bookmakers = game_data.get("bookmakers", [])
        if not bookmakers:
            return None

        home_team = game_data.get("home_team", "")
        away_team = game_data.get("away_team", "")

        market = MarketOdds(team_a=home_team, team_b=away_team)

        for bookmaker in bookmakers:
            book_name = bookmaker.get("title", bookmaker.get("key", "unknown"))
            last_update_str = bookmaker.get("last_update")
            last_update = None
            if last_update_str:
                try:
                    last_update = datetime.fromisoformat(
                        last_update_str.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            for mkt in bookmaker.get("markets", []):
                if mkt.get("key") != "h2h":
                    continue

                outcomes = {o["name"]: o["price"] for o in mkt.get("outcomes", [])}

                if home_team in outcomes:
                    price = outcomes[home_team]
                    market.odds_a.append(Odds(
                        bookmaker=book_name,
                        american=price,
                        implied_probability=american_to_implied(price),
                        last_update=last_update,
                    ))

                if away_team in outcomes:
                    price = outcomes[away_team]
                    market.odds_b.append(Odds(
                        bookmaker=book_name,
                        american=price,
                        implied_probability=american_to_implied(price),
                        last_update=last_update,
                    ))

                if "Draw" in outcomes:
                    price = outcomes["Draw"]
                    if market.draw_odds is None:
                        market.draw_odds = []
                    market.draw_odds.append(Odds(
                        bookmaker=book_name,
                        american=price,
                        implied_probability=american_to_implied(price),
                        last_update=last_update,
                    ))

        if not market.odds_a or not market.odds_b:
            return None

        return market
