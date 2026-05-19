# Shine

Shine is an AI-assisted moneyline parlay EV engine that pulls live moneyline odds from TheOddsAPI, removes sportsbook vig, converts the market into true win probabilities, applies configurable big-competition intelligence, adjusts for pressure, travel, time zones, altitude, home advantage, and host-region context, scores correlation between legs, and ranks multi-sport parlays by true expected value instead of vibes. It is built for moneyline parlays across sports such as NBA, NFL, soccer, CS2, LoL, VAL, UFC, MLB, and NHL. Shine is not a DFS optimizer and not a prop model; the core is a transparent probability system that compares context-adjusted true probability against sportsbook implied probability and assigns EV tiers from S to D.

## What is included

- TheOddsAPI client for live `h2h` moneyline markets.
- American odds conversion, no-vig normalization, fair price calculation, and EV math.
- Big-competition intelligence layer for pressure performers and chokers.
- Travel, time-zone, altitude, home, and host-region probability adjustments.
- Correlation engine for style/context interactions across sports.
- Parlay ranking with EV tiers:
  - `S`: EV >= 12%
  - `A`: EV >= 6%
  - `B`: EV >= 2%
  - `C`: EV >= 0%
  - `D`: negative EV
- CLI output as clean text or JSON.

## Run locally

```bash
python -m shine.cli --sample
```

With live odds:

```bash
export THE_ODDS_API_KEY="your_api_key_here"
python -m shine.cli --sports basketball_nba,americanfootball_nfl,soccer_uefa_champs_league --legs 3 --limit 10
```

JSON output for a UI or website:

```bash
python -m shine.cli --sample --output json
```

If installed as a package, the `shine` command is available:

```bash
python -m pip install -e .
shine --sample
```

## Intelligence file

You can pass a JSON file that teaches Shine about teams, players, travel load, host-region edge, and style tags:

```json
{
  "entities": {
    "Boston Celtics": {
      "pressure_rating": 0.75,
      "travel_km": 450,
      "timezone_delta": 0,
      "altitude_m": 43,
      "host_region_advantage": true,
      "style_tags": ["pace_up", "home_court"]
    },
    "Miami Heat": {
      "pressure_rating": -0.2,
      "travel_km": 2400,
      "timezone_delta": 1,
      "style_tags": ["defense_grind"]
    }
  },
  "events": {
    "event-id-from-theoddsapi": {
      "big_competition": true,
      "venue_altitude_m": 1600,
      "environment_tags": ["bad_weather"]
    }
  },
  "sports": {
    "basketball_nba": {
      "big_competition": true
    }
  }
}
```

Run with:

```bash
python -m shine.cli --intelligence-file intelligence.json --sports basketball_nba --legs 3
```

## Tests

```bash
python -m unittest
```
