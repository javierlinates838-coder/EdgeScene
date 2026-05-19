# Shine v4

**Shine** is an AI-powered moneyline parlay engine. It pulls live odds from
[TheOddsAPI](https://the-odds-api.com), removes the sportsbook vig, applies a
big‑competition intelligence layer, models pressure performance, accounts for
travel and environment, and runs a correlation engine across legs to produce
optimized parlays with real expected value.

Shine is **not** a DFS model or a player‑props model. It is a pure,
multi‑sport moneyline EV engine.

Supported sports out of the box:

- NBA, WNBA, NCAAB
- NFL, NCAAF
- MLB, NHL
- Soccer (EPL, La Liga, Serie A, Bundesliga, Ligue 1, UCL, UEL, World Cup, etc.)
- UFC / Boxing
- Esports: CS2, LoL, VAL, Dota 2

## Quick start

```bash
git clone <this-repo>
cd <this-repo>
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env       # add your TheOddsAPI key
shine build --sports nba,nfl,soccer --min-legs 2 --max-legs 4 --top 5
```

Or just look at individual edges:

```bash
shine edges --sports nba,cs2,lol --min-edge 1.0 --top 20
```

## How Shine works

```
TheOddsAPI ─▶ Vig removal ─▶ Intelligence ─▶ Context ─▶ Correlation ─▶ EV / Tier
                (Shin)        (pressure +    (travel,    (per-sport      (S/A/B/C/D)
                                stage boost)   altitude,   pairwise ρ)
                                               home edge)
```

1. **Live odds.** The client (`shine/odds/client.py`) pulls H2H moneyline
   markets from TheOddsAPI for every requested sport and selects the **best
   price** for each outcome across all available books (the way a real
   parlay shopper would).
2. **Vig removal.** Shine devigs the two-way market using Shin's (1992)
   insider-trading model by default, with `power` and `multiplicative`
   methods available (`shine/math/devig.py`).
3. **Big-competition intelligence.** Shine detects whether the event is
   regular-season or a big stage (Playoffs, Champions League knockouts, CS2
   Majors, LoL Worlds, VAL Champions, UFC PPV title fights, etc.) and
   amplifies the team's edge accordingly. Teams known to **rise** under
   pressure get a multiplier > 1.0; teams known to **choke** get < 1.0.
   Configurable in `shine/data/pressure_ratings.json`.
4. **Travel + environment.** Distance (haversine), time-zone delta,
   altitude, baseline home edge per sport, and host-region advantage at
   neutral events are all priced in (`shine/context/`).
5. **Correlation engine.** Each pair of legs gets a correlation
   coefficient based on sport-family heuristics — NBA pace/defense, NFL
   script/weather, soccer possession style, CS2 map pool, LoL draft meta,
   VAL agent comps, UFC style matchups. Same-event picks are handled
   explicitly (perfect-positive vs perfect-negative). The joint
   probability is computed via a bounded Fréchet-style blend that
   reduces to the naïve product when ρ = 0.
6. **EV + tier.** The combined book decimal × Shine probability gives the
   true expected value. Tiers:

   | Tier | EV%     |
   |------|---------|
   | S    | ≥ 15.0  |
   | A    | ≥ 8.0   |
   | B    | ≥ 3.0   |
   | C    | ≥ 0.0   |
   | D    | < 0.0   |

## Programmatic use

```python
from shine import ShineEngine
from shine.engine.builder import BuildConfig

engine = ShineEngine()
cfg = BuildConfig(
    sports=["nba", "nfl", "soccer", "cs2"],
    min_legs=2,
    max_legs=4,
    min_ev_pct=2.0,
    top_n=5,
)
for parlay in engine.build_parlays(cfg):
    print(parlay.tier, f"{parlay.ev_pct:+.2f}%", [(l.event.sport_title, l.pick) for l in parlay.legs])
```

## Configuration

Environment variables (see `.env.example`):

| Var                 | Purpose                                |
|---------------------|----------------------------------------|
| `ODDS_API_KEY`      | TheOddsAPI key (required for live data) |
| `SHINE_REGIONS`     | Bookmaker regions, e.g. `us,uk,eu`     |
| `SHINE_ODDS_FORMAT` | `american` (default) or `decimal`      |
| `SHINE_CACHE_TTL`   | Cache lifetime for odds responses (s)  |
| `SHINE_CACHE_DIR`   | On-disk cache directory                |

## Tunable data files

All "soft" knowledge lives in JSON in `shine/data/` so you can iterate
without touching code:

- `competitions.json` — which keywords mean "big stage" per sport, and the
  boost multiplier
- `pressure_ratings.json` — per-team rise/choke ratings
- `venues.json` — lat/lon/altitude/timezone for major teams + neutral
  hosts
- `home_edge.json` — baseline home-field advantage per sport

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT
