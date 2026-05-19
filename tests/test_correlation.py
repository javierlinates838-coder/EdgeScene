from datetime import datetime, timezone

from shine.correlation.engine import CorrelationEngine
from shine.models import Event, Leg, Outcome


def _leg(sport_key: str, event_id: str, pick: str, prob: float = 0.6, dec: float = 1.9) -> Leg:
    ev = Event(
        id=event_id,
        sport_key=sport_key,
        sport_title=sport_key,
        league=sport_key,
        commence_time=datetime.now(timezone.utc),
        home_team="home",
        away_team="away",
        outcomes=[Outcome("home", -110, dec, "b", 1 / dec)],
    )
    return Leg(event=ev, pick=pick, book_decimal=dec, fair_prob=prob, adjusted_prob=prob)


def test_independent_legs_match_naive_product():
    corr = CorrelationEngine()
    legs = [_leg("basketball_nba", "1", "A", 0.6), _leg("soccer_epl", "2", "B", 0.55)]
    naive, c = corr.apply(legs)
    assert abs(naive - 0.6 * 0.55) < 1e-9
    # cross-sport correlation is ~0.02 so c is barely above naive
    assert c >= naive


def test_same_event_same_pick_high_positive():
    corr = CorrelationEngine()
    legs = [_leg("basketball_nba", "1", "A", 0.6), _leg("basketball_nba", "1", "A", 0.6)]
    _, c = corr.apply(legs)
    # Should approach min(p_i) = 0.6
    assert c > 0.5


def test_same_event_opposite_pick_destroys():
    corr = CorrelationEngine()
    legs = [_leg("basketball_nba", "1", "A", 0.6), _leg("basketball_nba", "1", "B", 0.4)]
    _, c = corr.apply(legs)
    # max(0, 0.6+0.4-1) = 0, so correlated prob should be near 0
    assert c < 0.05
