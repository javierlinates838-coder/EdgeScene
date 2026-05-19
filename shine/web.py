from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .engine import ShineEngine, ShineEngineConfig
from .models import LegContext, ParlayEvaluation
from .odds_api import OddsApiClient, OddsApiError

SPORT_OPTIONS: List[Dict[str, str]] = [
    {"key": "basketball_nba", "label": "NBA"},
    {"key": "americanfootball_nfl", "label": "NFL"},
    {"key": "baseball_mlb", "label": "MLB"},
    {"key": "icehockey_nhl", "label": "NHL"},
    {"key": "soccer_epl", "label": "Soccer (EPL)"},
    {"key": "soccer_uefa_champs_league", "label": "Champions League"},
    {"key": "esports_cs2", "label": "CS2"},
    {"key": "esports_lol", "label": "LoL"},
    {"key": "esports_valorant", "label": "VAL"},
    {"key": "mma_mixed_martial_arts", "label": "UFC / MMA"},
]

DEFAULT_SPORTS = [
    "basketball_nba",
    "americanfootball_nfl",
    "baseball_mlb",
    "icehockey_nhl",
    "soccer_epl",
    "esports_cs2",
    "esports_lol",
    "esports_valorant",
    "mma_mixed_martial_arts",
]


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/meta")
    def api_meta() -> Any:
        return jsonify(
            {
                "sport_options": SPORT_OPTIONS,
                "defaults": {
                    "sports": DEFAULT_SPORTS,
                    "regions": "us,eu,uk",
                    "max_legs": 3,
                    "max_parlays": 20,
                    "min_tier": "D",
                },
            }
        )

    @app.post("/api/parlays")
    def api_parlays() -> Any:
        payload = request.get_json(silent=True) or {}

        api_key = _sanitize_api_key(str(payload.get("api_key", "") or os.getenv("ODDS_API_KEY", "")))
        if not api_key:
            return jsonify({"error": "Missing API key. Provide api_key or set ODDS_API_KEY."}), 400

        sports = _normalize_sports(payload.get("sports"))
        if not sports:
            return jsonify({"error": "Provide at least one sport key."}), 400

        regions = str(payload.get("regions", "us")).strip() or "us"
        bookmakers_raw = str(payload.get("bookmakers", "")).strip()
        bookmakers = bookmakers_raw if bookmakers_raw else None

        max_legs = _safe_int(payload.get("max_legs"), default=3, lower=2, upper=8)
        max_parlays = _safe_int(payload.get("max_parlays"), default=20, lower=1, upper=250)
        min_tier = _normalize_min_tier(payload.get("min_tier"))
        context_overrides = _normalize_context_overrides(payload.get("context_overrides"))

        client = OddsApiClient(api_key=api_key)
        try:
            events = client.fetch_moneyline_odds(
                sports=sports,
                regions=regions,
                bookmakers=bookmakers,
            )
        except OddsApiError as error:
            status_code = error.status_code if error.status_code else 502
            return jsonify({"error": f"TheOddsAPI failed: {error}", "status_code": error.status_code}), status_code

        if not events:
            return jsonify({"error": "No eligible moneyline events returned from TheOddsAPI."}), 404

        engine = ShineEngine(
            ShineEngineConfig(
                max_legs=max_legs,
                max_parlays=max_parlays,
                min_tier=min_tier,
            )
        )
        parlays = engine.run(events=events, context_overrides=context_overrides)
        response = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "event_count": len(events),
            "parlay_count": len(parlays),
            "parlays": [_serialize_parlay(parlay) for parlay in parlays],
            "request": {
                "sports": sports,
                "regions": regions,
                "bookmakers": bookmakers,
                "max_legs": max_legs,
                "max_parlays": max_parlays,
                "min_tier": min_tier,
            },
        }
        return jsonify(response)

    return app


def _normalize_sports(raw_sports: Any) -> List[str]:
    if isinstance(raw_sports, list):
        values = [str(item).strip() for item in raw_sports]
    elif isinstance(raw_sports, str):
        values = [part.strip() for part in raw_sports.split(",")]
    else:
        values = DEFAULT_SPORTS
    return [value for value in values if value]


def _safe_int(value: Any, default: int, lower: int, upper: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(lower, min(upper, parsed))


def _normalize_min_tier(value: Any) -> str:
    if not value:
        return "D"
    normalized = str(value).strip().upper()
    return normalized if normalized in {"S", "A", "B", "C", "D"} else "D"


def _normalize_context_overrides(raw_overrides: Any) -> Dict[str, LegContext]:
    if not isinstance(raw_overrides, dict):
        return {}

    output: Dict[str, LegContext] = {}
    for event_id, raw in raw_overrides.items():
        if not isinstance(event_id, str) or not isinstance(raw, dict):
            continue
        output[event_id] = LegContext(
            stage=str(raw.get("stage", "regular")),
            travel_miles=float(raw.get("travel_miles", 0.0) or 0.0),
            timezone_shift=int(raw.get("timezone_shift", 0) or 0),
            altitude_meters=float(raw.get("altitude_meters", 0.0) or 0.0),
            host_region_advantage=float(raw.get("host_region_advantage", 0.0) or 0.0),
            weather_severity=float(raw.get("weather_severity", 0.0) or 0.0),
            notes=str(raw.get("notes", "")) or None,
        )
    return output


def _sanitize_api_key(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        return ""
    if " " not in value and "\t" not in value and "\n" not in value:
        return value

    tokens = [token.strip() for token in value.replace("\n", " ").split(" ") if token.strip()]
    for token in tokens:
        if token.startswith("toa_"):
            return token
    return tokens[0] if tokens else ""


def _serialize_parlay(parlay: ParlayEvaluation) -> Dict[str, Any]:
    return {
        "tier": parlay.tier,
        "expected_value": parlay.expected_value,
        "combined_probability": parlay.combined_probability,
        "correlation_score": parlay.correlation_score,
        "correlation_multiplier": parlay.correlation_multiplier,
        "adjusted_probability": parlay.adjusted_probability,
        "payout_multiplier": parlay.payout_multiplier,
        "sportsbook_implied_probability": parlay.sportsbook_implied_probability,
        "edge_over_book": parlay.metadata.get("edge_over_book", 0.0),
        "legs": [
            {
                "sport_key": leg.sport_key,
                "event_id": leg.event_id,
                "matchup": leg.matchup,
                "pick": leg.pick,
                "american_odds": leg.american_odds,
                "base_true_probability": leg.base_true_probability,
                "adjusted_probability": leg.adjusted_probability,
                "pressure_multiplier": leg.pressure_multiplier,
                "travel_multiplier": leg.travel_multiplier,
                "environment_multiplier": leg.environment_multiplier,
                "context": {
                    "stage": leg.context.stage,
                    "travel_miles": leg.context.travel_miles,
                    "timezone_shift": leg.context.timezone_shift,
                    "altitude_meters": leg.context.altitude_meters,
                    "host_region_advantage": leg.context.host_region_advantage,
                    "weather_severity": leg.context.weather_severity,
                    "notes": leg.context.notes,
                },
            }
            for leg in parlay.legs
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Shine web app")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
