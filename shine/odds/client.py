"""TheOddsAPI client with on-disk JSON caching.

We only use moneyline (``h2h``) markets — Shine is a pure moneyline EV engine.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

from ..config import Settings, get_settings
from ..math.odds import american_to_decimal, decimal_to_prob
from ..models import Event, Outcome

BASE_URL = "https://api.the-odds-api.com/v4"


class OddsAPIError(RuntimeError):
    pass


class OddsAPIClient:
    """Thin client around the v4 REST API."""

    def __init__(self, settings: Optional[Settings] = None, *, session: Optional[requests.Session] = None):
        self.settings = settings or get_settings()
        self.session = session or requests.Session()

    # ------------------------------------------------------------------ cache
    def _cache_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return self.settings.cache_dir / f"{digest}.json"

    def _read_cache(self, key: str) -> Optional[dict]:
        p = self._cache_path(key)
        if not p.exists():
            return None
        try:
            payload = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if time.time() - payload.get("_ts", 0) > self.settings.cache_ttl:
            return None
        return payload.get("data")

    def _write_cache(self, key: str, data) -> None:
        p = self._cache_path(key)
        try:
            p.write_text(json.dumps({"_ts": time.time(), "data": data}))
        except OSError:
            pass

    # ------------------------------------------------------------------ HTTP
    def _get(self, path: str, params: Dict[str, str]) -> object:
        if not self.settings.has_api_key:
            raise OddsAPIError(
                "ODDS_API_KEY is not set. Add it to your environment or .env file."
            )
        params = {"apiKey": self.settings.odds_api_key, **params}
        url = f"{BASE_URL}{path}"
        cache_key = url + "?" + json.dumps(params, sort_keys=True)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached
        try:
            r = self.session.get(url, params=params, timeout=20)
        except requests.RequestException as e:
            raise OddsAPIError(f"Network error talking to TheOddsAPI: {e}") from e
        if r.status_code == 401:
            raise OddsAPIError("TheOddsAPI rejected the key (401). Check ODDS_API_KEY.")
        if r.status_code == 422:
            raise OddsAPIError(f"Invalid request to TheOddsAPI: {r.text}")
        if r.status_code >= 400:
            raise OddsAPIError(f"TheOddsAPI HTTP {r.status_code}: {r.text}")
        data = r.json()
        self._write_cache(cache_key, data)
        return data

    # ------------------------------------------------------------------ API
    def list_sports(self, all_sports: bool = False) -> List[dict]:
        return self._get("/sports", {"all": "true" if all_sports else "false"})  # type: ignore[return-value]

    def get_odds(
        self,
        sport_key: str,
        *,
        regions: Optional[Iterable[str]] = None,
        markets: str = "h2h",
        odds_format: str = "american",
    ) -> List[dict]:
        regions_csv = ",".join(regions or self.settings.regions)
        return self._get(  # type: ignore[return-value]
            f"/sports/{sport_key}/odds",
            {
                "regions": regions_csv,
                "markets": markets,
                "oddsFormat": odds_format,
                "dateFormat": "iso",
            },
        )

    # ---------------------------------------------------------------- helpers
    def fetch_events(self, sport_keys: List[str]) -> List[Event]:
        """Fetch moneyline events across a list of sport keys.

        Bookmakers are aggregated; for each outcome the best (highest decimal)
        price across books is used — this is what a sharp parlay shopper would
        actually do.
        """
        if not self.settings.has_api_key:
            raise OddsAPIError(
                "ODDS_API_KEY is not set. Add it to your environment or .env file."
            )
        events: List[Event] = []
        for key in sport_keys:
            try:
                raw = self.get_odds(key)
            except OddsAPIError as exc:
                # Surface auth/rate-limit errors; skip per-sport availability errors.
                msg = str(exc).lower()
                if "401" in msg or "apikey" in msg or "rejected" in msg or "rate" in msg:
                    raise
                continue
            events.extend(_parse_events(key, raw))
        return events


def _parse_events(sport_key: str, raw: List[dict]) -> List[Event]:
    out: List[Event] = []
    for ev in raw:
        try:
            best: Dict[str, Outcome] = {}
            for book in ev.get("bookmakers", []):
                book_key = book.get("key", "unknown")
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name")
                        price = outcome.get("price")
                        if name is None or price is None:
                            continue
                        decimal = american_to_decimal(int(price))
                        prior = best.get(name)
                        if prior is None or decimal > prior.decimal_odds:
                            best[name] = Outcome(
                                name=name,
                                american_odds=int(price),
                                decimal_odds=decimal,
                                book=book_key,
                                implied_prob=decimal_to_prob(decimal),
                            )
            if len(best) < 2:
                continue
            commence = ev.get("commence_time")
            try:
                ct = datetime.fromisoformat(commence.replace("Z", "+00:00"))
            except Exception:
                ct = datetime.utcnow()
            out.append(
                Event(
                    id=ev.get("id", ""),
                    sport_key=sport_key,
                    sport_title=ev.get("sport_title", sport_key),
                    league=ev.get("sport_title", sport_key),
                    commence_time=ct,
                    home_team=ev.get("home_team", ""),
                    away_team=ev.get("away_team", ""),
                    outcomes=list(best.values()),
                    extra={"raw": ev},
                )
            )
        except Exception:
            continue
    return out
