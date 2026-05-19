"""Shine v4 command-line interface."""

from __future__ import annotations
import argparse
import sys
from shine.api.pipeline import run
from shine.api.display import print_parlays, print_summary, console
from shine.config import SPORT_KEYS


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="shine",
        description="Shine v4 — AI-powered moneyline parlay engine",
    )
    p.add_argument(
        "-s", "--sports",
        nargs="+",
        choices=list(SPORT_KEYS.keys()),
        default=None,
        help="Sports to include (default: all). E.g. -s NBA NFL soccer",
    )
    p.add_argument(
        "--min-legs",
        type=int,
        default=2,
        help="Minimum legs per parlay (default: 2)",
    )
    p.add_argument(
        "--max-legs",
        type=int,
        default=6,
        help="Maximum legs per parlay (default: 6)",
    )
    p.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        help="Number of top parlays to show (default: 10)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of Rich tables",
    )
    return p


def _to_json(parlays):
    import json

    out = []
    for p in parlays:
        legs = []
        for leg in p.legs:
            opponent = (
                leg.game.away.name
                if leg.pick == leg.game.home.name
                else leg.game.home.name
            )
            legs.append({
                "sport": leg.sport,
                "pick": leg.pick,
                "opponent": opponent,
                "american_odds": leg.american_odds,
                "true_prob": round(leg.prob, 4),
                "bookmaker": leg.bookmaker,
            })
        out.append({
            "tier": p.tier,
            "ev": round(p.ev, 4),
            "true_prob": round(p.true_prob, 6),
            "implied_prob": round(p.implied_prob, 6),
            "decimal_odds": round(p.decimal_odds, 2),
            "correlation_factor": round(p.correlation_factor, 4),
            "legs": legs,
        })
    return json.dumps(out, indent=2)


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    console.print("[bold bright_yellow]⭐ Shine v4[/bold bright_yellow] — Fetching live odds…")

    try:
        parlays = run(
            sports=args.sports,
            min_legs=args.min_legs,
            max_legs=args.max_legs,
            top_n=args.top,
        )
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    if args.json:
        print(_to_json(parlays))
    else:
        print_parlays(parlays)
        print_summary(parlays)


if __name__ == "__main__":
    main()
