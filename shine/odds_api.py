"""TheOddsAPI client and response normalization."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Any

from shine.models import MoneylineEvent, OutcomePrice
from shine.odds_math import american_to_decimal, american_to_probability, no_vig_probabilities


DEFAULT_SPORTS = (
    "basketball_nba",
    "americanfootball_nfl",
    "soccer_uefa_champs_league",
    "baseball_mlb",
    "icehockey_nhl",
    "mma_mixed_martial_arts",
    "esports_cs2",
    "esports_lol",
    "esports_valorant",
)


class OddsApiError(RuntimeError):
    """Raised when TheOddsAPI cannot be reached or returns an error."""


class TheOddsApiClient:
    def __init__(self, api_key: str, base_url: str = "https://api.the-odds-api.com/v4") -> None:
        if not api_key:
            raise ValueError("An API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def list_sports(self) -> list[dict[str, Any]]:
        return self._get_json("/sports", {})

    def fetch_moneyline_events(
        self,
        sport_key: str,
        *,
        regions: str = "us",
        bookmakers: str | None = None,
        odds_format: str = "american",
    ) -> list[MoneylineEvent]:
        params = {
            "regions": regions,
            "markets": "h2h",
            "oddsFormat": odds_format,
            "dateFormat": "iso",
        }
        if bookmakers:
            params["bookmakers"] = bookmakers
        payload = self._get_json(f"/sports/{sport_key}/odds", params)
        return normalize_odds_response(payload, sport_key=sport_key)

    def _get_json(self, path: str, params: dict[str, str]) -> Any:
        query = dict(params)
        query["apiKey"] = self.api_key
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "shine/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise OddsApiError(f"TheOddsAPI returned HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise OddsApiError(f"Could not reach TheOddsAPI: {exc.reason}") from exc
        return json.loads(data)


def normalize_odds_response(payload: list[dict[str, Any]], sport_key: str | None = None) -> list[MoneylineEvent]:
    """Convert TheOddsAPI h2h payload into no-vig moneyline events."""
    events: list[MoneylineEvent] = []
    for item in payload:
        normalized = normalize_event(item, sport_key=sport_key)
        if normalized is not None:
            events.append(normalized)
    return events


def normalize_event(item: dict[str, Any], sport_key: str | None = None) -> MoneylineEvent | None:
    prices_by_participant: dict[str, list[float]] = defaultdict(list)
    decimal_by_participant: dict[str, list[float]] = defaultdict(list)
    implied_by_participant: dict[str, list[float]] = defaultdict(list)
    no_vig_by_participant: dict[str, list[float]] = defaultdict(list)

    for bookmaker in item.get("bookmakers", []):
        market = _first_h2h_market(bookmaker.get("markets", []))
        if not market:
            continue

        implied_market: dict[str, float] = {}
        american_prices: dict[str, float] = {}
        for outcome in market.get("outcomes", []):
            name = outcome.get("name")
            price = outcome.get("price")
            if not name or price in (None, 0):
                continue
            american_prices[str(name)] = float(price)
            implied_market[str(name)] = american_to_probability(float(price))

        if len(implied_market) < 2:
            continue

        no_vig_market = no_vig_probabilities(implied_market)
        for participant, price in american_prices.items():
            prices_by_participant[participant].append(price)
            decimal_by_participant[participant].append(american_to_decimal(price))
            implied_by_participant[participant].append(implied_market[participant])
            no_vig_by_participant[participant].append(no_vig_market[participant])

    outcomes: list[OutcomePrice] = []
    for participant, prices in prices_by_participant.items():
        if not prices:
            continue
        average_american = sum(prices) / len(prices)
        outcomes.append(
            OutcomePrice(
                participant=participant,
                average_american_odds=average_american,
                average_decimal_odds=_average(decimal_by_participant[participant]),
                implied_probability=_average(implied_by_participant[participant]),
                no_vig_probability=_average(no_vig_by_participant[participant]),
                bookmaker_count=len(prices),
            )
        )

    if len(outcomes) < 2:
        return None

    outcomes.sort(key=lambda outcome: outcome.no_vig_probability, reverse=True)
    return MoneylineEvent(
        event_id=str(item.get("id") or ""),
        sport_key=str(sport_key or item.get("sport_key") or ""),
        sport_title=str(item.get("sport_title") or sport_key or ""),
        commence_time=_parse_datetime(item.get("commence_time")),
        home_team=item.get("home_team"),
        away_team=item.get("away_team"),
        outcomes=tuple(outcomes),
        raw=item,
    )


def _first_h2h_market(markets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for market in markets:
        if market.get("key") == "h2h":
            return market
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _average(values: list[float]) -> float:
    return sum(values) / len(values)
