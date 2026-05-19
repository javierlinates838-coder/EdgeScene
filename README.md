# Shine v4 — AI-Powered Moneyline Parlay Engine

Shine analyzes live odds, removes sportsbook vig, applies big-competition intelligence, models pressure performance, accounts for travel and environment, calculates correlation between legs, and generates optimized parlays with real expected value.

## Architecture

```
┌──────────────┐     ┌────────────────┐     ┌───────────────┐
│  TheOddsAPI  │────▶│  Vig Removal   │────▶│  True Probs   │
└──────────────┘     └────────────────┘     └───────┬───────┘
                                                    │
                     ┌────────────────┐             │
                     │  Big-Stage     │◀────────────┤
                     │  Intelligence  │             │
                     └───────┬────────┘             │
                             │                      │
                     ┌───────▼────────┐             │
                     │  Environment   │◀────────────┘
                     │  (travel, tz,  │
                     │   altitude)    │
                     └───────┬────────┘
                             │
                     ┌───────▼────────┐
                     │  Correlation   │
                     │  Engine        │
                     └───────┬────────┘
                             │
                     ┌───────▼────────┐
                     │  EV Calculator │
                     │  & Tier System │
                     └───────┬────────┘
                             │
                     ┌───────▼────────┐
                     │  Parlay        │
                     │  Optimizer     │
                     └───────┬────────┘
                             │
                     ┌───────▼────────┐
                     │  Output (CLI / │
                     │  JSON / UI)    │
                     └────────────────┘
```

## Supported Sports

| Sport | Key | Big-Stage Events |
|-------|-----|-----------------|
| NBA | `basketball_nba` | Playoffs, Finals, Play-In |
| NFL | `americanfootball_nfl` | Playoffs, Super Bowl |
| MLB | `baseball_mlb` | Playoffs, World Series |
| NHL | `icehockey_nhl` | Playoffs, Stanley Cup |
| Soccer | Multiple leagues | Champions League, World Cup, Copa America |
| CS2 | `csgo` | Majors, IEM Katowice, IEM Cologne |
| LoL | `lol` | Worlds, MSI |
| VAL | `valorant` | Champions, Masters |
| UFC | `mma_mixed_martial_arts` | PPV, Title Fights |

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/javierlinates838-coder/EdgeScene.git
cd EdgeScene

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env
# Edit .env and paste your TheOddsAPI key

# 4. Run Shine
python run_shine.py
```

## Usage

```bash
# All sports, top 10 parlays
python run_shine.py

# Specific sports
python run_shine.py -s NBA NFL soccer

# Custom leg range
python run_shine.py --min-legs 3 --max-legs 5

# More results
python run_shine.py -n 20

# JSON output (for piping to other tools)
python run_shine.py --json

# Combine options
python run_shine.py -s NBA NFL -n 15 --min-legs 2 --max-legs 4
```

## How It Works

### 1. Vig Removal
Pulls American moneyline odds from TheOddsAPI and converts them to implied probabilities. Since the book's implied probabilities sum to more than 100% (the vig), Shine normalizes them to get true win probabilities.

### 2. Big-Stage Intelligence
Teams perform differently on the biggest stages. Shine maintains a pressure-performance database that boosts clutch performers (e.g. Golden State Warriors in NBA Playoffs, T1 at LoL Worlds, Real Madrid in Champions League) and penalizes teams that historically underperform (e.g. Toronto Maple Leafs in NHL Playoffs, Dallas Cowboys in NFL Playoffs).

### 3. Environmental Factors
- **Home advantage**: Sport-specific baseline (NBA ~3%, soccer ~4%, esports ~1%)
- **Travel distance**: Penalty for away teams flying cross-country
- **Timezone crossings**: Jet lag penalty per hour of timezone difference
- **Altitude**: Teams at high altitude (Denver at 1,609m, Mexico City at 2,240m) get a boost against sea-level visitors

### 4. Correlation Engine
Parlay legs are not independent. Shine models how legs interact:
- **Same sport**: Shared variance from pace, weather, schedule effects
- **Same league**: Divisional/conference effects add correlation
- **Cross sport**: Near-zero correlation (independent events)
- **Same game**: High correlation (safeguard against conflicting picks)

Positive correlation → parlay EV increases. Negative correlation → parlay EV collapses.

### 5. EV Calculation
```
true_prob  = Π(leg_i.adjusted_prob) × correlation_factor
decimal    = Π(leg_i.decimal_odds)
implied    = 1 / decimal
EV         = (true_prob × decimal) - 1
```

### 6. Tier System
| Tier | EV Threshold | Meaning |
|------|-------------|---------|
| S | ≥ +15% | Elite edge — slam it |
| A | ≥ +8% | Strong value |
| B | ≥ +3% | Decent edge |
| C | ≥ 0% | Break-even or marginal |
| D | < 0% | Negative EV — avoid |

## Project Structure

```
shine/
├── __init__.py           # Package metadata
├── config.py             # API keys, sport keys, thresholds
├── cli.py                # Command-line interface
├── odds/
│   ├── models.py         # TeamOdds, Game, ParlayLeg, Parlay
│   └── client.py         # TheOddsAPI client
├── intelligence/
│   └── big_stage.py      # Pressure-performance adjustments
├── environment/
│   └── factors.py        # Travel, timezone, altitude, home edge
├── correlation/
│   └── engine.py         # Pairwise correlation + factor computation
├── ev/
│   └── calculator.py     # EV math and tier assignment
├── optimizer/
│   └── builder.py        # Parlay combination generator + ranker
└── api/
    ├── pipeline.py       # Full engine pipeline
    └── display.py        # Rich terminal output
tests/
└── test_engine.py        # Full test suite (no API key needed)
run_shine.py              # Entry point
```

## Running Tests

```bash
pytest tests/ -v
```

Tests use synthetic game data — no API key required.

## API Key

Get your free key at [the-odds-api.com](https://the-odds-api.com). The free tier gives 500 requests/month. Add it to `.env`:

```
ODDS_API_KEY=your_key_here
```

## What Makes Shine Different

Most "AI parlay builders" are just trend followers or random pickers. Shine is fundamentally different:

- **Real math**: Vig removal, true probability computation, EV calculation
- **Context-aware**: Big-stage intelligence that knows Golden State is different in the playoffs
- **Environmental modeling**: Travel, timezone, altitude — factors other tools ignore
- **Correlation-aware**: Understands that parlay legs interact, and accounts for it
- **Multi-sport**: NBA, NFL, MLB, NHL, soccer, CS2, LoL, VAL, UFC — all in one engine
- **Transparent**: Every number is shown — true prob, implied prob, EV, correlation factor, tier
