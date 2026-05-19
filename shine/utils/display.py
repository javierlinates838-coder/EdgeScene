"""Rich terminal display for Shine results."""

from __future__ import annotations

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from shine.core.config import SPORT_DISPLAY_NAMES, TIER_LABELS, Tier
from shine.core.models import Parlay, ParlayLeg, ShineResult

console = Console()

TIER_COLORS = {
    Tier.S: "bold yellow",
    Tier.A: "bold green",
    Tier.B: "cyan",
    Tier.C: "white",
    Tier.D: "red",
}

TIER_EMOJI = {
    Tier.S: "S",
    Tier.A: "A",
    Tier.B: "B",
    Tier.C: "C",
    Tier.D: "D",
}


def display_result(result: ShineResult, show_adjustments: bool = False) -> None:
    """Display full Shine analysis results."""
    _display_header(result)

    if not result.parlays:
        console.print("\n[yellow]No parlays found matching criteria.[/yellow]")
        if result.warnings:
            for w in result.warnings:
                console.print(f"  [dim]Warning: {w}[/dim]")
        return

    for i, parlay in enumerate(result.parlays, 1):
        _display_parlay(parlay, i, show_adjustments)

    _display_summary(result)


def _display_header(result: ShineResult) -> None:
    """Display the Shine header."""
    sports_str = ", ".join(
        SPORT_DISPLAY_NAMES.get(s, s.value) for s in result.sports_covered
    )

    header = Table.grid(padding=1)
    header.add_column(style="bold cyan", justify="center")
    header.add_row("[bold bright_white]SHINE v4[/bold bright_white]")
    header.add_row("[dim]AI-Powered Moneyline Parlay Engine[/dim]")
    header.add_row(f"[dim]{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    header.add_row(f"Games analyzed: [bright_white]{result.games_analyzed}[/bright_white]")
    header.add_row(f"Sports: [bright_white]{sports_str or 'None'}[/bright_white]")
    if result.api_calls_remaining is not None:
        header.add_row(f"API calls remaining: [bright_white]{result.api_calls_remaining}[/bright_white]")

    console.print(Panel(header, border_style="bright_cyan", padding=(1, 2)))


def _display_parlay(parlay: Parlay, index: int, show_adjustments: bool = False) -> None:
    """Display a single parlay."""
    tier = parlay.tier
    color = TIER_COLORS.get(tier, "white")
    tier_label = TIER_LABELS.get(tier, "")

    ev_color = "green" if parlay.true_ev_percent > 0 else "red"
    ev_str = f"{parlay.true_ev_percent:+.1f}%"
    profit_str = f"${parlay.expected_profit:+.2f}"

    title = (
        f"[{color}]PARLAY #{index} — Tier {TIER_EMOJI[tier]}[/{color}]  "
        f"[{ev_color}]EV: {ev_str}[/{ev_color}]  "
        f"[dim]({parlay.num_legs} legs)[/dim]"
    )

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Sport", width=8)
    table.add_column("Pick", min_width=22)
    table.add_column("vs", min_width=18)
    table.add_column("Odds", justify="right", width=8)
    table.add_column("Implied", justify="right", width=8)
    table.add_column("True", justify="right", width=8)
    table.add_column("Edge", justify="right", width=8)

    for j, leg in enumerate(parlay.legs, 1):
        sport_name = SPORT_DISPLAY_NAMES.get(leg.sport, leg.sport.value)
        edge = leg.edge * 100
        edge_color = "green" if edge > 0 else "red"
        edge_str = f"[{edge_color}]{edge:+.1f}%[/{edge_color}]"

        table.add_row(
            str(j),
            sport_name,
            f"[bold]{leg.team}[/bold]",
            f"[dim]{leg.opponent}[/dim]",
            leg.display_odds,
            f"{leg.implied_probability * 100:.1f}%",
            f"{leg.adjusted_probability * 100:.1f}%",
            edge_str,
        )

        if show_adjustments and leg.adjustments:
            for adj in leg.adjustments:
                table.add_row("", "", f"  [dim italic]{adj}[/dim italic]", "", "", "", "", "")

    corr_str = f"{parlay.correlation_factor:.3f}"
    corr_color = "green" if parlay.correlation_factor > 1.0 else ("red" if parlay.correlation_factor < 1.0 else "white")

    footer_parts = [
        f"Correlation: [{corr_color}]{corr_str}[/{corr_color}]",
        f"Fair Odds: {_format_american(parlay.fair_american_odds)}",
        f"Book Odds: {_format_american(parlay.sportsbook_american_odds)}",
        f"Expected Profit: [{ev_color}]{profit_str}[/{ev_color}] on ${parlay.stake:.0f}",
    ]
    footer = "  |  ".join(footer_parts)

    content = Table.grid()
    content.add_row(table)
    content.add_row("")
    content.add_row(f"[dim]{footer}[/dim]")

    if parlay.correlation_details:
        for detail in parlay.correlation_details:
            content.add_row(f"  [dim italic]{detail}[/dim italic]")

    border_color = color.replace("bold ", "")
    console.print(Panel(content, title=title, border_style=border_color, padding=(0, 1)))


def _display_summary(result: ShineResult) -> None:
    """Display summary stats."""
    tier_counts = {}
    for parlay in result.parlays:
        tier_counts[parlay.tier] = tier_counts.get(parlay.tier, 0) + 1

    summary = Table.grid(padding=1)
    summary.add_column(style="bold", justify="right")
    summary.add_column()

    summary.add_row("Total parlays:", str(len(result.parlays)))
    for tier in Tier:
        count = tier_counts.get(tier, 0)
        if count > 0:
            color = TIER_COLORS.get(tier, "white")
            summary.add_row(f"  Tier [{color}]{tier.value}[/{color}]:", str(count))

    best = result.best_parlay
    if best:
        ev_color = "green" if best.true_ev_percent > 0 else "red"
        summary.add_row(
            "Best EV:",
            f"[{ev_color}]{best.true_ev_percent:+.1f}%[/{ev_color}] ({best.num_legs}-leg)"
        )

    console.print(Panel(summary, title="[bold]Summary[/bold]", border_style="dim"))


def _format_american(odds: int) -> str:
    """Format American odds with + prefix for positive."""
    if odds > 0:
        return f"+{odds}"
    return str(odds)
