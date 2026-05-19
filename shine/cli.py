"""Shine command-line interface."""

from __future__ import annotations

from typing import List

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .engine.builder import BuildConfig, ShineEngine
from .models import Parlay, Tier
from .odds.client import OddsAPIError

console = Console()


_TIER_STYLES = {
    Tier.S: "bold magenta",
    Tier.A: "bold green",
    Tier.B: "green",
    Tier.C: "yellow",
    Tier.D: "red",
}


@click.group()
@click.version_option(package_name="shine", prog_name="shine")
def cli() -> None:
    """Shine — AI-powered moneyline parlay engine."""


@cli.command()
@click.option("--sports", "-s", default="nba,nfl,soccer", help="Comma-separated sports (nba,nfl,mlb,nhl,soccer,cs2,lol,val,ufc,...)")
@click.option("--min-legs", default=2, show_default=True, type=int)
@click.option("--max-legs", default=4, show_default=True, type=int)
@click.option("--min-ev", default=0.0, show_default=True, type=float, help="Minimum parlay EV% to surface")
@click.option("--min-leg-edge", default=0.5, show_default=True, type=float, help="Minimum single-leg edge% to consider")
@click.option("--top", default=5, show_default=True, type=int)
@click.option("--devig", default="shin", type=click.Choice(["shin", "power", "multiplicative"]), show_default=True)
def build(sports: str, min_legs: int, max_legs: int, min_ev: float, min_leg_edge: float, top: int, devig: str) -> None:
    """Pull live odds and build top-EV parlays."""
    sport_list = [s.strip() for s in sports.split(",") if s.strip()]
    cfg = BuildConfig(
        sports=sport_list,
        min_legs=min_legs,
        max_legs=max_legs,
        min_ev_pct=min_ev,
        min_leg_edge_pct=min_leg_edge,
        top_n=top,
        devig_method=devig,
    )

    engine = ShineEngine()
    console.print(Panel.fit(
        f"[bold]Shine v4[/]\nFetching live moneyline odds for [cyan]{', '.join(sport_list)}[/]…",
        border_style="cyan",
    ))
    try:
        parlays = engine.build_parlays(cfg)
    except OddsAPIError as exc:
        console.print(f"[red]TheOddsAPI error:[/] {exc}")
        raise SystemExit(1)
    if not parlays:
        console.print("[yellow]No +EV parlays found. Try a different sport mix or relax --min-ev.[/]")
        return
    for i, parlay in enumerate(parlays, start=1):
        _render_parlay(i, parlay)


@cli.command()
@click.option("--sports", "-s", default="nba,nfl,soccer")
@click.option("--min-edge", default=0.5, show_default=True, type=float)
@click.option("--top", default=20, show_default=True, type=int)
def edges(sports: str, min_edge: float, top: int) -> None:
    """Show individual moneyline legs ranked by Shine edge %."""
    sport_list = [s.strip() for s in sports.split(",") if s.strip()]
    engine = ShineEngine()
    try:
        events = engine.fetch_events(sport_list)
    except OddsAPIError as exc:
        console.print(f"[red]TheOddsAPI error:[/] {exc}")
        raise SystemExit(1)
    legs = engine.candidate_legs(events, min_edge_pct=min_edge)[:top]
    if not legs:
        console.print("[yellow]No edges found.[/]")
        return
    table = Table(title="Shine Edges (single moneyline legs)", show_lines=False)
    table.add_column("#", justify="right")
    table.add_column("Sport")
    table.add_column("Matchup")
    table.add_column("Pick")
    table.add_column("Odds", justify="right")
    table.add_column("Fair", justify="right")
    table.add_column("Shine", justify="right")
    table.add_column("Edge %", justify="right")
    for i, leg in enumerate(legs, start=1):
        matchup = f"{leg.event.away_team} @ {leg.event.home_team}"
        table.add_row(
            str(i),
            leg.event.sport_title,
            matchup,
            leg.pick,
            f"{leg.book_decimal:.2f}",
            f"{leg.fair_prob*100:.1f}%",
            f"{leg.adjusted_prob*100:.1f}%",
            f"[green]{leg.edge_pct:+.1f}%[/]" if leg.edge_pct > 0 else f"[red]{leg.edge_pct:+.1f}%[/]",
        )
    console.print(table)


def _render_parlay(index: int, parlay: Parlay) -> None:
    tier_style = _TIER_STYLES.get(parlay.tier, "white")
    header = (
        f"#{index}  [bold]Tier {parlay.tier.value}[/]  "
        f"EV [{tier_style}]{parlay.ev_pct:+.2f}%[/]  "
        f"Odds [cyan]{parlay.combined_decimal:.2f}[/]  "
        f"Shine win prob [cyan]{parlay.correlated_prob*100:.1f}%[/]  "
        f"Book implied [dim]{parlay.book_implied*100:.1f}%[/]  "
        f"avg ρ [cyan]{parlay.correlation_score:+.2f}[/]"
    )
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("#", justify="right", width=3)
    table.add_column("Sport", width=14)
    table.add_column("Matchup")
    table.add_column("Pick")
    table.add_column("Book", justify="right", width=8)
    table.add_column("Fair", justify="right", width=7)
    table.add_column("Shine", justify="right", width=7)
    table.add_column("Edge", justify="right", width=8)
    for i, leg in enumerate(parlay.legs, start=1):
        matchup = f"{leg.event.away_team} @ {leg.event.home_team}"
        table.add_row(
            str(i),
            leg.event.sport_title,
            matchup,
            leg.pick,
            f"{leg.book_decimal:.2f}",
            f"{leg.fair_prob*100:.1f}%",
            f"{leg.adjusted_prob*100:.1f}%",
            f"{leg.edge_pct:+.1f}%",
        )
    console.print(Panel(table, title=header, border_style=tier_style))
    if parlay.notes:
        console.print("  [dim]Correlation:[/] " + "; ".join(parlay.notes))
    leg_notes: List[str] = []
    for i, leg in enumerate(parlay.legs, start=1):
        if leg.notes:
            leg_notes.append(f"L{i}: " + " | ".join(leg.notes))
    if leg_notes:
        for ln in leg_notes:
            console.print(f"  [dim]{ln}[/]")
    console.print()


def main() -> None:
    cli(prog_name="shine")


if __name__ == "__main__":
    main()
