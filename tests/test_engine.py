"""End-to-end tests for the Shine v4 engine using synthetic game data.

No API key needed — these tests inject fake Game objects directly into the
pipeline and verify that vig removal, intelligence, environment, correlation,
EV calculation, and tier assignment all work correctly.
"""

from __future__ import annotations
import math
from datetime import datetime, timezone

from shine.odds.models import TeamOdds, Game, ParlayLeg, Parlay
from shine.intelligence.big_stage import apply_big_stage, _is_big_stage
from shine.environment.factors import apply_environment, compute_env_shift, _haversine
from shine.correlation.engine import pairwise_correlation, correlation_factor
from shine.ev.calculator import calculate_ev
from shine.optimizer.builder import build_parlays
from shine.api.pipeline import run_from_games


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_game(
    sport: str = "NBA",
    home_name: str = "Boston Celtics",
    away_name: str = "Miami Heat",
    home_odds: int = -150,
    away_odds: int = 130,
    game_id: str = "test-001",
) -> Game:
    return Game(
        id=game_id,
        sport=sport,
        league=sport,
        commence_time=datetime.now(timezone.utc),
        home=TeamOdds(name=home_name, american_odds=home_odds),
        away=TeamOdds(name=away_name, american_odds=away_odds),
        bookmaker="fanduel",
    )


# ── Vig removal ─────────────────────────────────────────────────────────────

class TestVigRemoval:
    def test_vig_is_positive(self):
        g = _make_game(home_odds=-150, away_odds=130)
        assert g.vig > 0, "Sportsbook vig should be positive"

    def test_true_probs_sum_to_one(self):
        g = _make_game(home_odds=-200, away_odds=170)
        assert abs(g.home.true_prob + g.away.true_prob - 1.0) < 1e-9

    def test_favourite_has_higher_prob(self):
        g = _make_game(home_odds=-300, away_odds=250)
        assert g.home.true_prob > g.away.true_prob

    def test_even_odds(self):
        g = _make_game(home_odds=100, away_odds=100)
        assert abs(g.home.true_prob - 0.5) < 1e-9
        assert abs(g.vig) < 1e-9


# ── Big-stage intelligence ───────────────────────────────────────────────────

class TestBigStage:
    def test_playoff_detected(self):
        g = _make_game(sport="NBA")
        g.league = "NBA playoff"
        assert _is_big_stage(g)

    def test_regular_season_not_big_stage(self):
        g = _make_game(sport="NBA")
        g.league = "NBA"
        g.id = "regular-season-001"
        assert not _is_big_stage(g)

    def test_apply_modifies_probs(self):
        g = _make_game(sport="NBA", home_name="Golden State Warriors", away_name="Dallas Cowboys")
        g.league = "NBA playoff"
        orig_home = g.home.true_prob
        apply_big_stage(g)
        assert g.home.true_prob != orig_home

    def test_probs_still_sum_to_one(self):
        g = _make_game(sport="NBA", home_name="Golden State Warriors")
        g.league = "NBA playoff"
        apply_big_stage(g)
        assert abs(g.home.true_prob + g.away.true_prob - 1.0) < 1e-9


# ── Environment ──────────────────────────────────────────────────────────────

class TestEnvironment:
    def test_home_advantage_positive(self):
        g = _make_game()
        shift = compute_env_shift(g)
        assert shift > 0

    def test_denver_altitude_boost(self):
        g = _make_game(
            home_name="Denver Nuggets",
            away_name="Miami Heat",
        )
        shift = compute_env_shift(g)
        assert shift > 0.03, "Denver altitude should give noticeable boost"

    def test_apply_keeps_sum_to_one(self):
        g = _make_game()
        apply_environment(g)
        assert abs(g.home.true_prob + g.away.true_prob - 1.0) < 1e-9

    def test_haversine_known_distance(self):
        nyc = (40.71, -74.01)
        la = (34.05, -118.24)
        dist = _haversine(*nyc, *la)
        assert 3900 < dist < 4000, f"NYC→LA should be ~3944 km, got {dist}"


# ── Correlation ──────────────────────────────────────────────────────────────

class TestCorrelation:
    def test_same_game_high_corr(self):
        g = _make_game(game_id="same")
        leg_a = ParlayLeg(game=g, pick=g.home.name, prob=0.6, american_odds=-150, bookmaker="fd", sport="NBA")
        leg_b = ParlayLeg(game=g, pick=g.away.name, prob=0.4, american_odds=130, bookmaker="fd", sport="NBA")
        assert pairwise_correlation(leg_a, leg_b) >= 0.25

    def test_cross_sport_near_zero(self):
        g1 = _make_game(sport="NBA", game_id="nba-1")
        g2 = _make_game(sport="NFL", game_id="nfl-1")
        leg_a = ParlayLeg(game=g1, pick=g1.home.name, prob=0.6, american_odds=-150, bookmaker="fd", sport="NBA")
        leg_b = ParlayLeg(game=g2, pick=g2.home.name, prob=0.6, american_odds=-150, bookmaker="fd", sport="NFL")
        assert abs(pairwise_correlation(leg_a, leg_b)) < 0.01

    def test_factor_independent_is_near_one(self):
        legs = []
        for i, sport in enumerate(["NBA", "NFL", "MLB"]):
            g = _make_game(sport=sport, game_id=f"game-{i}")
            legs.append(ParlayLeg(game=g, pick=g.home.name, prob=0.6, american_odds=-150, bookmaker="fd", sport=sport))
        factor = correlation_factor(legs)
        assert 0.95 <= factor <= 1.05

    def test_same_sport_slightly_positive(self):
        legs = []
        for i in range(3):
            g = _make_game(sport="NBA", game_id=f"nba-{i}", home_name=f"Team H{i}", away_name=f"Team A{i}")
            legs.append(ParlayLeg(game=g, pick=g.home.name, prob=0.6, american_odds=-150, bookmaker="fd", sport="NBA"))
        factor = correlation_factor(legs)
        assert factor > 1.0


# ── EV Calculator ────────────────────────────────────────────────────────────

class TestEVCalculator:
    def test_positive_ev(self):
        g = _make_game(home_odds=-110, away_odds=110)
        leg = ParlayLeg(game=g, pick=g.home.name, prob=0.60, american_odds=-110, bookmaker="fd", sport="NBA")
        p = Parlay(legs=[leg])
        calculate_ev(p)
        assert p.ev > 0, f"Should have +EV, got {p.ev}"

    def test_tier_assignment_s(self):
        g = _make_game()
        leg = ParlayLeg(game=g, pick=g.home.name, prob=0.70, american_odds=-110, bookmaker="fd", sport="NBA")
        p = Parlay(legs=[leg])
        calculate_ev(p)
        assert p.tier == "S"

    def test_tier_assignment_d(self):
        g = _make_game()
        leg = ParlayLeg(game=g, pick=g.home.name, prob=0.20, american_odds=-300, bookmaker="fd", sport="NBA")
        p = Parlay(legs=[leg])
        calculate_ev(p)
        assert p.tier == "D"

    def test_multi_leg_ev(self):
        legs = []
        for i in range(3):
            g = _make_game(game_id=f"ml-{i}", sport="NBA" if i < 2 else "NFL")
            leg = ParlayLeg(game=g, pick=g.home.name, prob=0.58, american_odds=-140, bookmaker="fd", sport=g.sport)
            legs.append(leg)
        p = Parlay(legs=legs)
        calculate_ev(p)
        assert p.true_prob > 0
        assert p.decimal_odds > 1.0


# ── Optimizer / Builder ──────────────────────────────────────────────────────

class TestOptimizer:
    def test_builds_parlays(self):
        games = [
            _make_game(game_id=f"opt-{i}", sport="NBA", home_name=f"Home {i}", away_name=f"Away {i}")
            for i in range(5)
        ]
        parlays = build_parlays(games, min_legs=2, max_legs=3, top_n=5)
        assert len(parlays) > 0
        assert all(p.ev is not None for p in parlays)

    def test_sorted_by_ev(self):
        games = [
            _make_game(game_id=f"sort-{i}", sport="NBA", home_name=f"Home {i}", away_name=f"Away {i}")
            for i in range(6)
        ]
        parlays = build_parlays(games, min_legs=2, max_legs=3, top_n=10)
        evs = [p.ev for p in parlays]
        assert evs == sorted(evs, reverse=True)

    def test_no_same_game_conflict(self):
        games = [
            _make_game(game_id=f"conflict-{i}", sport="NBA", home_name=f"Home {i}", away_name=f"Away {i}")
            for i in range(4)
        ]
        parlays = build_parlays(games, min_legs=2, max_legs=4, top_n=20)
        for p in parlays:
            ids = [leg.game.id for leg in p.legs]
            assert len(ids) == len(set(ids)), "Found same-game conflict in parlay"


# ── Full pipeline ────────────────────────────────────────────────────────────

class TestPipeline:
    def test_end_to_end(self):
        games = [
            _make_game(game_id="e2e-0", sport="NBA", home_name="Boston Celtics", away_name="Miami Heat",
                       home_odds=-160, away_odds=140),
            _make_game(game_id="e2e-1", sport="NFL", home_name="Kansas City Chiefs", away_name="Dallas Cowboys",
                       home_odds=-200, away_odds=170),
            _make_game(game_id="e2e-2", sport="NBA", home_name="Denver Nuggets", away_name="Phoenix Suns",
                       home_odds=-130, away_odds=110),
            _make_game(game_id="e2e-3", sport="soccer", home_name="Real Madrid", away_name="PSG",
                       home_odds=-120, away_odds=100),
        ]
        parlays = run_from_games(games, min_legs=2, max_legs=3, top_n=5)
        assert len(parlays) > 0
        best = parlays[0]
        assert best.tier in ("S", "A", "B", "C", "D")
        assert best.true_prob > 0
        assert best.decimal_odds > 1.0
