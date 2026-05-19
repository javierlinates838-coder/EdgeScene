# Shine v4 — AI-Powered Moneyline Parlay Engine

Shine is an AI-powered moneyline parlay engine that analyzes live odds, removes sportsbook vig, applies big-competition intelligence, models pressure performance, accounts for travel and environment, and calculates correlation between legs to generate optimized parlays with real expected value.

## What Shine Does

1. **Pulls live moneyline odds** across all major sports via TheOddsAPI (NBA, NFL, MLB, NHL, Soccer, CS2, LoL, VALORANT, UFC)
2. **Removes the vig** using advanced methods (power devigging, Shin model) to calculate true win probabilities
3. **Applies big-competition intelligence** — teams behave differently on big stages (NBA Playoffs, Super Bowl, Champions League, CS2 Majors, LoL Worlds, VAL Champions, UFC PPVs)
4. **Models environment factors** — home advantage, altitude (Denver at 5,280ft), travel distance, timezone crossings
5. **Analyzes correlation between legs** — pace/defense in NBA, map pool in CS2, draft meta in LoL, agent comp in VAL, style matchups in UFC
6. **Calculates true expected value** and assigns tiers (S/A/B/C/D) to every parlay

## Quick Start

### Install

```bash
pip install -e .
```

### Set your API key

```bash
export ODDS_API_KEY=your_key_here
```

Or create a `.env` file:

```
ODDS_API_KEY=your_key_here
```

Get a free API key at [the-odds-api.com](https://the-odds-api.com/).

### Run with live odds

```bash
shine run                          # All sports
shine run -s nba -s nfl            # Specific sports
shine run -s esports --legs 4      # Esports, up to 4-leg parlays
shine run --min-ev 5 --show-adj    # Only 5%+ EV, show adjustments
```

### Run demo (no API key needed)

```bash
shine demo                         # Mock data across all sports
shine demo --show-adj              # See all intelligence adjustments
shine demo --legs 4 --count 15     # More legs, more parlays
```

### Analyze vig on any line

```bash
shine vig -180 155                 # Analyze a specific moneyline
```

### List supported sports

```bash
shine sports
```

## Supported Sports

| Sport | Alias | Key Competitions |
|---|---|---|
| NBA | `nba` | Playoffs, Finals, Conference Finals |
| NFL | `nfl` | Playoffs, Conference Championship, Super Bowl |
| MLB | `mlb` | Postseason, World Series |
| NHL | `nhl` | Stanley Cup Playoffs, Finals |
| Soccer | `soccer`, `epl`, `ucl`, `laliga`, etc. | Champions League, EPL, La Liga, Bundesliga, Serie A |
| CS2 | `cs2` | Majors, Champions Stage |
| LoL | `lol` | Worlds, MSI |
| VALORANT | `val` | Champions, Masters |
| UFC | `ufc` | PPV events, Title Fights |

## Architecture

```
shine/
├── core/
│   ├── config.py          # Sport definitions, tier system, configuration
│   ├── probability.py     # Vig removal, probability math, EV calculation
│   ├── models.py          # Data models (ParlayLeg, Parlay, ShineResult)
│   └── engine.py          # Main engine orchestrator
├── api/
│   └── odds_client.py     # TheOddsAPI v4 client
├── intelligence/
│   └── pressure.py        # Big-competition & pressure performance adjustments
├── environment/
│   └── adjustments.py     # Home advantage, altitude, travel, timezone
├── correlation/
│   └── engine.py          # Sport-specific leg correlation modeling
├── data/
│   ├── big_competitions.py # Competition definitions & pressure profiles
│   └── mock_odds.py       # Realistic mock data for testing
├── utils/
│   └── display.py         # Rich terminal output
└── cli.py                 # Click CLI interface
```

## How EV Tiers Work

| Tier | EV Range | Meaning |
|---|---|---|
| **S** | ≥ +12% | ELITE — Strong positive EV, high confidence |
| **A** | +7% to +12% | GREAT — Solid edge, worth betting |
| **B** | +3% to +7% | GOOD — Modest edge, selective bet |
| **C** | 0% to +3% | NEUTRAL — Breakeven or marginal edge |
| **D** | < 0% | AVOID — Negative EV, sportsbook wins |

## How Correlation Works

Shine doesn't treat parlay legs as independent when they shouldn't be:

- **Cross-sport**: Effectively independent (slight diversification benefit)
- **Same-sport favorites**: Chalk tends to hold together → positive correlation
- **Same-sport underdogs**: Upset variance stacks → negative correlation
- **Same-game conflict**: Detected and blocked (impossible parlay)

Sport-specific factors: NBA pace/defense, NFL weather/script, soccer possession style, CS2 map pool depth, LoL draft meta/patch, VAL agent comps, UFC style matchups.

## Tests

```bash
python3 -m pytest tests/ -v
```

66 tests covering probability math, intelligence layer, correlation engine, environment adjustments, and full engine integration.
