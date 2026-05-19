# Shine v4 Engine

Shine is an AI-powered moneyline parlay engine that pulls live odds, removes sportsbook vig, applies big-competition intelligence, models pressure and travel context, measures leg correlation, and ranks parlays by true expected value (EV).

## What this repository includes

- Live moneyline ingest from TheOddsAPI
- No-vig implied probability conversion
- Competition pressure adjustment layer
- Travel and environment context adjustments
- Correlation-aware parlay probability scoring
- Tiered EV output (`S`, `A`, `B`, `C`, `D`)
- Command-line interface for local use in Cursor

## Quick start

1. Create a virtual environment and install:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -e .[dev]`
2. Set your API key:
   - `export THE_ODDS_API_KEY="your_key_here"`
3. Run:
   - `shine --sport basketball_nba --legs "Boston Celtics,Boston Celtics,2.10" "Denver Nuggets,Denver Nuggets,2.05"`

## CLI leg format

Each `--legs` item uses:

`"selection_name,team_or_player_name,decimal_odds"`

Example:

`"Arsenal,Arsenal,2.00"`

## Notes

- This engine is intentionally moneyline-first (not DFS, not props).
- The intelligence and correlation rules are extensible and designed to be expanded sport by sport.
- Use this as the v4 core, then layer a web or UI front-end later.
