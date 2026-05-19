from __future__ import annotations

import argparse
import os
from typing import List

from .engine import ShineEngine, ShineEngineConfig
from .odds_api import OddsApiClient, OddsApiError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shine v4 moneyline EV parlay engine")
    parser.add_argument(
        "--sports",
        required=True,
        help="Comma-separated TheOddsAPI sport keys (e.g. basketball_nba,americanfootball_nfl).",
    )
    parser.add_argument("--regions", default="us", help="Odds region list supported by TheOddsAPI.")
    parser.add_argument(
        "--bookmakers",
        default=None,
        help="Optional comma-separated bookmaker keys to constrain odds sources.",
    )
    parser.add_argument("--max-legs", type=int, default=3, help="Maximum legs per parlay.")
    parser.add_argument("--max-parlays", type=int, default=10, help="Maximum parlays to output.")
    parser.add_argument(
        "--min-tier",
        default="D",
        choices=["S", "A", "B", "C", "D"],
        help="Lowest EV tier to include in output.",
    )
    parser.add_argument("--api-key", default=None, help="TheOddsAPI key (defaults to ODDS_API_KEY).")
    return parser


def _comma_split(value: str) -> List[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


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


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    api_key = _sanitize_api_key(args.api_key or os.getenv("ODDS_API_KEY", ""))
    if not api_key:
        raise SystemExit("Missing API key: set ODDS_API_KEY or pass --api-key.")

    sports = _comma_split(args.sports)
    if not sports:
        raise SystemExit("At least one sport key is required.")

    client = OddsApiClient(api_key=api_key)
    try:
        events = client.fetch_moneyline_odds(
            sports=sports,
            regions=args.regions,
            bookmakers=args.bookmakers,
        )
    except OddsApiError as error:
        status = f"{error.status_code}" if error.status_code is not None else "n/a"
        raise SystemExit(f"TheOddsAPI request failed (status {status}): {error}") from error
    if not events:
        raise SystemExit("No eligible moneyline events returned from TheOddsAPI.")

    engine = ShineEngine(
        ShineEngineConfig(
            max_legs=max(2, args.max_legs),
            max_parlays=max(1, args.max_parlays),
            min_tier=args.min_tier,
        )
    )
    parlays = engine.run(events)
    if not parlays:
        raise SystemExit("No parlays met current constraints.")

    for idx, parlay in enumerate(parlays, start=1):
        print(
            f"{idx}) Tier {parlay.tier} | EV {parlay.expected_value:+.2%} | "
            f"Corr {parlay.correlation_score:+.3f} | "
            f"True Win {parlay.adjusted_probability:.4f} | "
            f"Payout {parlay.payout_multiplier:.2f}x"
        )
        for leg in parlay.legs:
            print(
                f"   - {leg.sport_key}: {leg.pick} ML in {leg.matchup} "
                f"@ {leg.american_odds:+d} (adj p={leg.adjusted_probability:.3f})"
            )
        print()


if __name__ == "__main__":
    main()
