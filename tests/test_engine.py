import unittest

from shine.engine import ShineEngine, ShineEngineConfig
from shine.models import EventOdds, TeamOdds


def _event(
    event_id: str,
    sport_key: str,
    away: str,
    home: str,
    away_odds: int,
    home_odds: int,
    away_true: float,
    home_true: float,
) -> EventOdds:
    return EventOdds(
        sport_key=sport_key,
        sport_title=sport_key,
        event_id=event_id,
        commence_time="2026-05-19T00:00:00Z",
        home_team=home,
        away_team=away,
        bookmaker="testbook",
        teams=[
            TeamOdds(
                team=away,
                american_odds=away_odds,
                implied_probability=0.5,
                true_probability=away_true,
            ),
            TeamOdds(
                team=home,
                american_odds=home_odds,
                implied_probability=0.5,
                true_probability=home_true,
            ),
        ],
    )


class TestShineEngine(unittest.TestCase):
    def test_run_generates_ranked_parlays(self) -> None:
        events = [
            _event("nba-1", "basketball_nba", "AwayA", "HomeA", +110, -120, 0.48, 0.52),
            _event("nfl-1", "americanfootball_nfl", "AwayB", "HomeB", +125, -135, 0.45, 0.55),
            _event("ufc-1", "mma_mixed_martial_arts", "AwayC", "HomeC", +105, -115, 0.49, 0.51),
        ]
        engine = ShineEngine(ShineEngineConfig(max_legs=3, max_parlays=5))
        parlays = engine.run(events)

        self.assertGreater(len(parlays), 0)
        self.assertLessEqual(len(parlays), 5)
        self.assertTrue(all(2 <= len(parlay.legs) <= 3 for parlay in parlays))
        self.assertTrue(all(parlays[i].expected_value >= parlays[i + 1].expected_value for i in range(len(parlays) - 1)))

    def test_unique_event_enforced_per_parlay(self) -> None:
        events = [
            _event("nba-1", "basketball_nba", "AwayA", "HomeA", +110, -120, 0.48, 0.52),
            _event("nba-2", "basketball_nba", "AwayB", "HomeB", +115, -125, 0.47, 0.53),
        ]
        engine = ShineEngine(ShineEngineConfig(max_legs=2, max_parlays=10))
        parlays = engine.run(events)
        for parlay in parlays:
            event_ids = [leg.event_id for leg in parlay.legs]
            self.assertEqual(len(event_ids), len(set(event_ids)))


if __name__ == "__main__":
    unittest.main()
