"""Command-line interface for Shine."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from shine.engine import ShineEngine
from shine.intelligence import IntelligenceLayer
from shine.odds_api import DEFAULT_SPORTS, OddsApiError, TheOddsApiClient, normalize_odds_response


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    intelligence = IntelligenceLayer.from_file(args.intelligence_file) if args.intelligence_file else IntelligenceLayer()

    try:
        if args.list_sports:
            api_key = _resolve_api_key(args.api_key)
            client = TheOddsApiClient(api_key)
            print(json.dumps(client.list_sports(), indent=2, sort_keys=True))
            return 0

        events = sample_events() if args.sample else fetch_events(args)
        engine = ShineEngine(intelligence)
        parlays = engine.rank_parlays(
            events,
            legs_per_parlay=args.legs,
            max_leg_pool=args.max_leg_pool,
            limit=args.limit,
            min_edge=args.min_edge,
        )
    except (ValueError, OddsApiError) as exc:
        print(f"shine: {exc}", file=sys.stderr)
        return 2

    if args.output == "json":
        print(json.dumps([parlay.to_dict() for parlay in parlays], indent=2, sort_keys=True))
    else:
        print_text_report(parlays)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shine",
        description="Build no-vig, context-adjusted moneyline parlays from TheOddsAPI odds.",
    )
    parser.add_argument("--api-key", help="TheOddsAPI key. Defaults to THE_ODDS_API_KEY or ODDS_API_KEY.")
    parser.add_argument("--sports", default=",".join(DEFAULT_SPORTS), help="Comma-separated TheOddsAPI sport keys.")
    parser.add_argument("--regions", default="us", help="TheOddsAPI regions parameter, e.g. us,uk,eu,au.")
    parser.add_argument("--bookmakers", help="Optional comma-separated bookmaker keys.")
    parser.add_argument("--legs", type=int, default=3, help="Legs per parlay.")
    parser.add_argument("--limit", type=int, default=10, help="Number of parlays to print.")
    parser.add_argument("--max-leg-pool", type=int, default=40, help="Maximum candidate legs before combination search.")
    parser.add_argument("--min-edge", type=float, default=-0.05, help="Minimum single-leg edge admitted to the pool.")
    parser.add_argument("--intelligence-file", help="Optional JSON file with team/player context adjustments.")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    parser.add_argument("--sample", action="store_true", help="Run against built-in sample odds instead of live API odds.")
    parser.add_argument("--list-sports", action="store_true", help="Print available TheOddsAPI sports and exit.")
    return parser


def fetch_events(args: argparse.Namespace) -> list[Any]:
    api_key = _resolve_api_key(args.api_key)
    client = TheOddsApiClient(api_key)
    events = []
    for sport_key in _parse_csv(args.sports):
        events.extend(
            client.fetch_moneyline_events(
                sport_key,
                regions=args.regions,
                bookmakers=args.bookmakers,
            )
        )
    if not events:
        raise ValueError("No moneyline events were returned for the requested sports.")
    return events


def print_text_report(parlays: list[Any]) -> None:
    if not parlays:
        print("No parlays found for the requested filters.")
        return

    for index, parlay in enumerate(parlays, start=1):
        print(
            f"{index}. Tier {parlay.tier} | EV {parlay.expected_value * 100:.2f}% | "
            f"true {parlay.true_probability * 100:.2f}% | book {parlay.sportsbook_probability * 100:.2f}% | "
            f"decimal {parlay.offered_decimal_odds:.2f} | corr {parlay.correlation_multiplier:.3f}"
        )
        for leg in parlay.legs:
            adjustments = ", ".join(adjustment.name for adjustment in leg.adjustments) or "no context adjustment"
            print(
                f"   - {leg.sport_title}: {leg.participant} over {leg.opponent or 'field'} "
                f"@ {leg.average_american_odds:+.0f} | no-vig {leg.no_vig_probability * 100:.2f}% | "
                f"adjusted {leg.adjusted_probability * 100:.2f}% | edge {leg.edge * 100:.2f}% | {adjustments}"
            )


def sample_events() -> list[Any]:
    return normalize_odds_response(
        [
            _sample_event(
                "nba-1",
                "basketball_nba",
                "NBA Playoffs",
                "Boston Celtics",
                "Miami Heat",
                [("Boston Celtics", -145), ("Miami Heat", 125)],
                [("Boston Celtics", -150), ("Miami Heat", 130)],
            ),
            _sample_event(
                "nfl-1",
                "americanfootball_nfl",
                "NFL Playoffs",
                "Kansas City Chiefs",
                "Buffalo Bills",
                [("Kansas City Chiefs", -120), ("Buffalo Bills", 105)],
                [("Kansas City Chiefs", -118), ("Buffalo Bills", 102)],
            ),
            _sample_event(
                "ucl-1",
                "soccer_uefa_champs_league",
                "Champions League",
                "Real Madrid",
                "Arsenal",
                [("Real Madrid", 135), ("Arsenal", 205), ("Draw", 230)],
                [("Real Madrid", 130), ("Arsenal", 210), ("Draw", 235)],
            ),
            _sample_event(
                "cs2-1",
                "esports_cs2",
                "CS2 Major",
                "FaZe Clan",
                "Natus Vincere",
                [("FaZe Clan", -110), ("Natus Vincere", -105)],
                [("FaZe Clan", -115), ("Natus Vincere", -102)],
            ),
            _sample_event(
                "ufc-1",
                "mma_mixed_martial_arts",
                "UFC PPV",
                "Elite Striker",
                "Control Grappler",
                [("Elite Striker", 115), ("Control Grappler", -135)],
                [("Elite Striker", 120), ("Control Grappler", -140)],
            ),
        ]
    )


def _sample_event(
    event_id: str,
    sport_key: str,
    sport_title: str,
    home_team: str,
    away_team: str,
    book_a_prices: list[tuple[str, int]],
    book_b_prices: list[tuple[str, int]],
) -> dict[str, Any]:
    return {
        "id": event_id,
        "sport_key": sport_key,
        "sport_title": sport_title,
        "commence_time": "2026-06-01T00:00:00Z",
        "home_team": home_team,
        "away_team": away_team,
        "bookmakers": [
            {
                "key": "book_a",
                "title": "Book A",
                "markets": [{"key": "h2h", "outcomes": [{"name": name, "price": price} for name, price in book_a_prices]}],
            },
            {
                "key": "book_b",
                "title": "Book B",
                "markets": [{"key": "h2h", "outcomes": [{"name": name, "price": price} for name, price in book_b_prices]}],
            },
        ],
    }


def _resolve_api_key(value: str | None) -> str:
    api_key = value or os.getenv("THE_ODDS_API_KEY") or os.getenv("ODDS_API_KEY")
    if not api_key:
        raise ValueError("Set THE_ODDS_API_KEY, ODDS_API_KEY, or pass --api-key. Use --sample to run without an API key.")
    return api_key


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
