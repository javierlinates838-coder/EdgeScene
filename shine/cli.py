"""Shine v4 CLI — command-line interface for the parlay engine."""

from __future__ import annotations

import logging
import sys
from typing import List, Optional

import click
from rich.console import Console

from shine.core.config import ALL_SPORTS, SPORT_DISPLAY_NAMES, ShineConfig, Sport
from shine.core.engine import ShineEngine
from shine.utils.display import display_result

console = Console()

SPORT_ALIASES = {
    "nba": [Sport.NBA],
    "nfl": [Sport.NFL],
    "mlb": [Sport.MLB],
    "nhl": [Sport.NHL],
    "soccer": [
        Sport.SOCCER_EPL, Sport.SOCCER_UCL, Sport.SOCCER_LALIGA,
        Sport.SOCCER_BUNDESLIGA, Sport.SOCCER_SERIEA, Sport.SOCCER_LIGUE1,
        Sport.SOCCER_MLS,
    ],
    "epl": [Sport.SOCCER_EPL],
    "ucl": [Sport.SOCCER_UCL],
    "laliga": [Sport.SOCCER_LALIGA],
    "bundesliga": [Sport.SOCCER_BUNDESLIGA],
    "seriea": [Sport.SOCCER_SERIEA],
    "ligue1": [Sport.SOCCER_LIGUE1],
    "mls": [Sport.SOCCER_MLS],
    "cs2": [Sport.CS2],
    "csgo": [Sport.CS2],
    "lol": [Sport.LOL],
    "val": [Sport.VAL],
    "valorant": [Sport.VAL],
    "ufc": [Sport.UFC],
    "mma": [Sport.UFC],
    "esports": [Sport.CS2, Sport.LOL, Sport.VAL],
    "all": ALL_SPORTS,
}


def _resolve_sports(sport_names: tuple) -> List[Sport]:
    """Resolve sport names/aliases to Sport enums."""
    if not sport_names:
        return ALL_SPORTS

    sports: List[Sport] = []
    for name in sport_names:
        key = name.lower().strip()
        if key in SPORT_ALIASES:
            sports.extend(SPORT_ALIASES[key])
        else:
            console.print(f"[red]Unknown sport: {name}[/red]")
            console.print(f"Available: {', '.join(SPORT_ALIASES.keys())}")
            sys.exit(1)

    return list(dict.fromkeys(sports))


@click.group()
@click.version_option(version="4.0.0", prog_name="Shine")
def cli():
    """Shine v4 — AI-Powered Moneyline Parlay Engine"""
    pass


@cli.command()
@click.option("--sports", "-s", multiple=True, help="Sports to analyze (e.g. nba, nfl, cs2)")
@click.option("--legs", "-l", default=3, help="Max legs per parlay (default: 3)")
@click.option("--min-legs", default=2, help="Min legs per parlay (default: 2)")
@click.option("--count", "-n", default=10, help="Max parlays to show (default: 10)")
@click.option("--min-ev", type=float, default=None, help="Minimum EV% threshold")
@click.option("--stake", type=float, default=10.0, help="Stake amount in dollars (default: 10)")
@click.option("--show-adj", is_flag=True, help="Show detailed adjustments per leg")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
def run(sports, legs, min_legs, count, min_ev, stake, show_adj, verbose):
    """Run the Shine engine with live odds."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)

    config = ShineConfig.from_env()
    config.default_stake = stake

    if not config.has_api_key:
        console.print("[red]No ODDS_API_KEY found![/red]")
        console.print("Set your API key in .env or as an environment variable:")
        console.print("  export ODDS_API_KEY=your_key_here")
        console.print("\nOr run [cyan]shine demo[/cyan] to see Shine with mock data.")
        sys.exit(1)

    target_sports = _resolve_sports(sports)

    console.print(f"\n[cyan]Fetching live odds for {len(target_sports)} sports...[/cyan]\n")

    engine = ShineEngine(config)
    result = engine.run(
        sports=target_sports,
        max_parlays=count,
        min_legs=min_legs,
        max_legs=legs,
        min_ev=min_ev,
    )

    display_result(result, show_adjustments=show_adj)


@cli.command()
@click.option("--legs", "-l", default=3, help="Max legs per parlay (default: 3)")
@click.option("--min-legs", default=2, help="Min legs per parlay (default: 2)")
@click.option("--count", "-n", default=10, help="Max parlays to show (default: 10)")
@click.option("--min-ev", type=float, default=None, help="Minimum EV% threshold")
@click.option("--stake", type=float, default=10.0, help="Stake amount in dollars")
@click.option("--show-adj", is_flag=True, help="Show detailed adjustments per leg")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
def demo(legs, min_legs, count, min_ev, stake, show_adj, verbose):
    """Run Shine with mock data (no API key needed)."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)

    from shine.data.mock_odds import get_mock_games

    config = ShineConfig()
    config.default_stake = stake

    console.print("\n[cyan]Running Shine v4 with mock data...[/cyan]\n")

    engine = ShineEngine(config)
    result = engine.run_with_mock_data(
        mock_games=get_mock_games(),
        max_parlays=count,
        min_legs=min_legs,
        max_legs=legs,
        min_ev=min_ev,
    )

    display_result(result, show_adjustments=show_adj)


@cli.command()
def sports():
    """List all supported sports."""
    console.print("\n[bold cyan]Supported Sports[/bold cyan]\n")

    from rich.table import Table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Alias", style="cyan")
    table.add_column("Sport(s)")
    table.add_column("API Key")

    for alias, sport_list in sorted(SPORT_ALIASES.items()):
        if alias == "all":
            continue
        names = ", ".join(SPORT_DISPLAY_NAMES.get(s, s.value) for s in sport_list)
        keys = ", ".join(s.value for s in sport_list)
        table.add_row(alias, names, keys)

    console.print(table)


@cli.command()
@click.argument("odds_a", type=int)
@click.argument("odds_b", type=int)
def vig(odds_a, odds_b):
    """Analyze vig on a moneyline (e.g. shine vig -180 155)."""
    from shine.core.probability import VigAnalysis

    analysis = VigAnalysis.analyze(odds_a, odds_b)

    console.print(f"\n[bold cyan]Vig Analysis[/bold cyan]")
    console.print(f"  Line: {_fmt_odds(odds_a)} / {_fmt_odds(odds_b)}")
    console.print(f"  Implied: {analysis.implied_a*100:.1f}% / {analysis.implied_b*100:.1f}%")
    console.print(f"  Total implied: {analysis.total_implied*100:.1f}% (vig = {analysis.vig_percent:.1f}%)")
    console.print(f"  Fair (vig-free): {analysis.fair_a*100:.1f}% / {analysis.fair_b*100:.1f}%")
    console.print(f"  Method: {analysis.method}\n")


def _fmt_odds(odds: int) -> str:
    return f"+{odds}" if odds > 0 else str(odds)


def main():
    cli()


if __name__ == "__main__":
    main()
