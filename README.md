# Shine v4 Moneyline Engine

Shine is an AI-powered moneyline parlay engine that ingests live odds from TheOddsAPI across major sports, removes sportsbook vig, converts prices into true win probabilities, applies big-competition pressure intelligence, adjusts for travel, altitude, time zones, and host-region effects, estimates inter-leg correlation by sport-specific game dynamics, and returns optimized multi-sport parlays ranked by real expected value so you can prioritize mathematically strong tickets instead of trend-driven picks.

## What this repository includes

- A local-first Python implementation of the Shine v4 core engine.
- TheOddsAPI client for pulling live `h2h` (moneyline) odds.
- Probability math utilities (American odds conversion, no-vig normalization).
- Pressure + environment intelligence adjustments.
- Correlation model to penalize or reward leg interactions.
- EV computation and tier grading (`S`, `A`, `B`, `C`, `D`).
- CLI workflow for generating ranked parlay candidates.
- Unit tests for core math and engine behavior.

## Quick start

1. Ensure Python 3.11+ is installed.
2. Export your API key:

```bash
export ODDS_API_KEY="your_theoddsapi_key"
```

3. Run the CLI:

```bash
python -m shine.cli \
  --sports basketball_nba,americanfootball_nfl,soccer_epl,baseball_mlb,icehockey_nhl,esports_cs2,esports_lol,mma_mixed_martial_arts \
  --regions us,eu,uk \
  --max-legs 3 \
  --max-parlays 20
```

## CLI options

- `--sports`: Comma-delimited TheOddsAPI sport keys.
- `--regions`: Odds regions (default: `us`).
- `--bookmakers`: Optional comma list to constrain books.
- `--max-legs`: Maximum legs per parlay (default: `3`).
- `--max-parlays`: Number of ranked parlays to return (default: `10`).
- `--min-tier`: Lowest tier to include (`S`, `A`, `B`, `C`, `D`).
- `--api-key`: Override `ODDS_API_KEY`.

## Example output

```text
1) Tier S | EV +22.41% | Corr +0.12 | True Win 0.2143 | Payout 6.80x
   - NBA: Nuggets ML vs Lakers @ -110 (adj p=0.551)
   - NFL: Ravens ML vs Bengals @ +105 (adj p=0.511)
   - UFC: Fighter A ML vs Fighter B @ -125 (adj p=0.566)
```

## Notes

- This engine is a research tool, not financial advice.
- The model is intentionally modular so you can swap in deeper sport-specific logic or historical training data later.
