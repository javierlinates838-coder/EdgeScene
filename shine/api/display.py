"""Pretty-printing utilities for Shine results."""

from __future__ import annotations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from shine.odds.models import Parlay

console = Console()

TIER_COLORS = {
    "S": "bold bright_yellow",
    "A": "bold green",
    "B": "bold cyan",
    "C": "bold white",
    "D": "bold red",
}


def _format_american(odds: int) -> str:
    return f"+{odds}" if odds > 0 else str(odds)


def _format_pct(p: float) -> str:
    return f"{p * 100:.1f}%"


def _format_ev(ev: float) -> str:
    sign = "+" if ev >= 0 else ""
    return f"{sign}{ev * 100:.1f}%"


def _parlay_decimal_display(p: Parlay) -> str:
    return f"{p.decimal_odds:.2f}x"


def print_parlays(parlays: list[Parlay], title: str = "SHINE v4 — Top Parlays") -> None:
    """Print a list of parlays to the terminal using Rich tables."""
    if not parlays:
        console.print("[bold red]No parlays found.[/bold red] Check your API key and available games.")
        return

    console.print()
    console.rule(f"[bold bright_yellow]{title}[/bold bright_yellow]")
    console.print()

    for rank, p in enumerate(parlays, 1):
        tier_style = TIER_COLORS.get(p.tier, "white")

        header = Text()
        header.append(f"#{rank}  ", style="bold")
        header.append(f"Tier {p.tier}", style=tier_style)
        header.append(f"  |  EV: {_format_ev(p.ev)}", style="bold green" if p.ev >= 0 else "bold red")
        header.append(f"  |  Odds: {_parlay_decimal_display(p)}")
        header.append(f"  |  True Prob: {_format_pct(p.true_prob)}")
        header.append(f"  |  Implied: {_format_pct(p.implied_prob)}")
        header.append(f"  |  Corr: {p.correlation_factor:.3f}")

        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
        table.add_column("Leg", style="dim")
        table.add_column("Sport")
        table.add_column("Pick", style="bold")
        table.add_column("vs")
        table.add_column("Odds")
        table.add_column("True Prob")
        table.add_column("Book")

        for i, leg in enumerate(p.legs, 1):
            opponent = (
                leg.game.away.name
                if leg.pick == leg.game.home.name
                else leg.game.home.name
            )
            table.add_row(
                str(i),
                leg.sport,
                leg.pick,
                opponent,
                _format_american(leg.american_odds),
                _format_pct(leg.prob),
                leg.bookmaker,
            )

        console.print(Panel(table, title=header, border_style=tier_style, expand=False))
        console.print()


def print_summary(parlays: list[Parlay]) -> None:
    """Print a quick tier distribution summary."""
    if not parlays:
        return
    tiers = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    for p in parlays:
        tiers[p.tier] = tiers.get(p.tier, 0) + 1

    console.print()
    table = Table(title="Tier Distribution", show_header=True, header_style="bold")
    table.add_column("Tier")
    table.add_column("Count", justify="right")
    for t, c in tiers.items():
        style = TIER_COLORS.get(t, "white")
        table.add_row(f"[{style}]{t}[/{style}]", str(c))
    console.print(table)
    console.print()
