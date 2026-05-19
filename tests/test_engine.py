"""End-to-end engine tests using synthetic events (no API key needed)."""

from datetime import datetime, timezone

from shine.correlation.engine import CorrelationEngine
from shine.engine.builder import BuildConfig, ShineEngine
from shine.engine.ev import build_parlay
from shine.engine.leg_factory import LegFactory
from shine.math.odds import american_to_decimal, decimal_to_prob
from shine.models import Event, Outcome, Tier


def _event(
    sport_key: str,
    sport_title: str,
    home: str,
    away: str,
    home_odds: int,
    away_odds: int,
    event_id: str = "e1",
) -> Event:
    dec_h, dec_a = american_to_decimal(home_odds), american_to_decimal(away_odds)
    return Event(
        id=event_id,
        sport_key=sport_key,
        sport_title=sport_title,
        league=sport_title,
        commence_time=datetime.now(timezone.utc),
        home_team=home,
        away_team=away,
        outcomes=[
            Outcome(name=home, american_odds=home_odds, decimal_odds=dec_h, book="b1", implied_prob=decimal_to_prob(dec_h)),
            Outcome(name=away, american_odds=away_odds, decimal_odds=dec_a, book="b1", implied_prob=decimal_to_prob(dec_a)),
        ],
    )


def test_leg_factory_produces_two_legs():
    ev = _event("basketball_nba", "NBA", "Boston Celtics", "Miami Heat", -160, +135)
    factory = LegFactory()
    legs = factory.build(ev)
    assert len(legs) == 2
    assert 0.0 < legs[0].fair_prob < 1.0
    assert 0.0 < legs[0].adjusted_prob < 1.0


def test_build_parlay_ev_and_tier():
    factory = LegFactory()
    corr = CorrelationEngine()
    e1 = _event("basketball_nba", "NBA", "Boston Celtics", "Miami Heat", -160, +135, event_id="e1")
    e2 = _event("americanfootball_nfl", "NFL", "Kansas City Chiefs", "Buffalo Bills", -130, +110, event_id="e2")
    legs = [factory.build(e1)[0], factory.build(e2)[0]]
    parlay = build_parlay(legs, corr)
    assert parlay.combined_decimal > 1.0
    assert parlay.tier in {Tier.S, Tier.A, Tier.B, Tier.C, Tier.D}
    # EV is finite
    assert parlay.ev_pct == parlay.ev_pct  # not NaN


def test_engine_build_parlays_from_synthetic_events():
    events = [
        _event("basketball_nba", "NBA", "Boston Celtics", "Miami Heat", -150, +130, event_id="e1"),
        _event("basketball_nba", "NBA", "Denver Nuggets", "Los Angeles Lakers", -140, +120, event_id="e2"),
        _event("americanfootball_nfl", "NFL", "Kansas City Chiefs", "Buffalo Bills", -130, +110, event_id="e3"),
        _event("soccer_uefa_champs_league", "Champions League", "Real Madrid", "Bayern Munich", -120, +260, event_id="e4"),
    ]
    engine = ShineEngine()
    cfg = BuildConfig(sports=["nba", "nfl", "soccer"], min_legs=2, max_legs=3, min_ev_pct=-100, top_n=5, min_leg_edge_pct=-100)
    parlays = engine.build_parlays(cfg, events=events)
    assert parlays, "Engine should produce at least one parlay"
    for p in parlays:
        assert 2 <= len(p.legs) <= 3
