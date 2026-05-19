from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Sequence

from .context import ContextInput
from .engine import ShineEngine
from .models import EventMarket, LegInput
from .odds_api import OddsApiClient


def _parse_leg(raw: str, sport_key: str, inferred_event_id: str = "") -> LegInput:
    parts = [item.strip() for item in raw.split(",")]
    if len(parts) < 3:
        raise ValueError(f"Invalid leg format: {raw}")

    selection, team_or_player, odds_str = parts[0], parts[1], parts[2]
    event_id = parts[3] if len(parts) >= 4 and parts[3] else inferred_event_id
    tags = tuple(tag for tag in (parts[4].split(";") if len(parts) >= 5 else []) if tag)

    return LegInput(
        sport_key=sport_key,
        event_id=event_id,
        selection=selection,
        decimal_odds=float(odds_str),
        team_or_player=team_or_player,
        tags=tags,
    )


def _index_markets(markets: Sequence[EventMarket]) -> Dict[str, EventMarket]:
    return {market.event_id: market for market in markets}


def _infer_event_by_team(markets: Sequence[EventMarket], team_or_player: str) -> str:
    needle = team_or_player.lower()
    for market in markets:
        if needle in {market.home_team.lower(), market.away_team.lower()}:
            return market.event_id
    return ""


def _parse_key_values(entries: Sequence[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Expected key=value, got {entry}")
        key, value = entry.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def _parse_context(entries: Sequence[str]) -> Dict[str, ContextInput]:
    # event_id=travel_km:timezone_shift:altitude:home:host_region
    out: Dict[str, ContextInput] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Expected event_id=context fields, got {entry}")
        event_id, value = entry.split("=", 1)
        fields = value.split(":")
        if len(fields) != 5:
            raise ValueError(f"Expected 5 context fields in {entry}")
        out[event_id.strip()] = ContextInput(
            travel_km=float(fields[0]),
            timezone_shift_hours=float(fields[1]),
            altitude_meters=float(fields[2]),
            home_team=fields[3].strip().lower() == "true",
            host_region_advantage=fields[4].strip().lower() == "true",
        )
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shine v4 moneyline parlay EV engine")
    parser.add_argument("--sport", required=True, help="TheOddsAPI sport key, e.g. basketball_nba")
    parser.add_argument(
        "--legs",
        nargs="+",
        required=True,
        help='Legs as "selection,team_or_player,decimal_odds[,event_id][,tag1;tag2]"',
    )
    parser.add_argument("--regions", default="us,eu,uk", help="Odds regions for TheOddsAPI")
    parser.add_argument("--bookmakers", default=None, help="Optional bookmaker filter list")
    parser.add_argument("--competition", nargs="*", default=[], help="event_id=competition_tag")
    parser.add_argument(
        "--context",
        nargs="*",
        default=[],
        help="event_id=travel_km:timezone_shift:altitude:home_team:host_region_advantage",
    )
    parser.add_argument("--no-fetch", action="store_true", help="Skip live market lookup and use provided leg odds only")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    markets: List[EventMarket] = []
    if not args.no_fetch:
        api_key = os.getenv("THE_ODDS_API_KEY")
        if not api_key:
            parser.error("THE_ODDS_API_KEY is required unless --no-fetch is used.")
        client = OddsApiClient(api_key=api_key)
        markets = client.get_moneyline_markets(
            sport_key=args.sport,
            regions=args.regions,
            bookmakers=args.bookmakers,
        )

    legs: List[LegInput] = []
    for raw_leg in args.legs:
        inferred = _infer_event_by_team(markets, raw_leg.split(",")[1].strip()) if markets else ""
        legs.append(_parse_leg(raw_leg, sport_key=args.sport, inferred_event_id=inferred))

    competition_tags = _parse_key_values(args.competition)
    context_by_event = _parse_context(args.context)
    market_lookup = _index_markets(markets)

    engine = ShineEngine()
    result = engine.score_parlay(
        legs=legs,
        market_lookup=market_lookup,
        competition_tags=competition_tags,
        context_by_event=context_by_event,
    )

    output = {
        "tier": result.tier,
        "ev": round(result.ev, 4),
        "sportsbook_probability": round(result.sportsbook_probability, 6),
        "model_probability": round(result.model_probability, 6),
        "expected_payout_multiple": round(result.expected_payout_multiple, 4),
        "correlation_multiplier": round(result.correlation_multiplier, 4),
        "notes": result.notes,
        "legs": [
            {
                "event_id": leg.leg.event_id,
                "selection": leg.leg.selection,
                "base_probability": round(leg.base_probability, 6),
                "no_vig_probability": round(leg.no_vig_probability, 6),
                "adjusted_probability": round(leg.adjusted_probability, 6),
                "factors": {key: round(value, 4) for key, value in leg.adjustment_factors.items()},
            }
            for leg in result.legs
        ],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
