from datetime import datetime, timezone

from shine.engine import ShineEngine
from shine.models import EventMarket, LegInput, OddsBookPrice


def test_engine_scores_parlay() -> None:
    engine = ShineEngine()
    market = EventMarket(
        event_id="event_1",
        sport_key="basketball_nba",
        home_team="Boston Celtics",
        away_team="Miami Heat",
        commence_time=datetime.now(timezone.utc),
        prices=[
            OddsBookPrice(bookmaker="BookA", selection="Boston Celtics", decimal_odds=1.90),
            OddsBookPrice(bookmaker="BookA", selection="Miami Heat", decimal_odds=2.00),
            OddsBookPrice(bookmaker="BookB", selection="Boston Celtics", decimal_odds=1.88),
            OddsBookPrice(bookmaker="BookB", selection="Miami Heat", decimal_odds=2.02),
        ],
    )
    legs = [
        LegInput(
            sport_key="basketball_nba",
            event_id="event_1",
            selection="Boston Celtics",
            decimal_odds=1.95,
            team_or_player="Boston Celtics",
            tags=("pace_up", "weak_defense"),
        ),
        LegInput(
            sport_key="basketball_nba",
            event_id="event_2",
            selection="Denver Nuggets",
            decimal_odds=2.10,
            team_or_player="Denver Nuggets",
            tags=("pace_up", "weak_defense"),
        ),
    ]

    result = engine.score_parlay(
        legs=legs,
        market_lookup={"event_1": market},
        competition_tags={"event_1": "nba_playoffs"},
    )

    assert 0.0 < result.model_probability < 1.0
    assert result.expected_payout_multiple > 1.0
    assert result.tier in {"S", "A", "B", "C", "D"}
