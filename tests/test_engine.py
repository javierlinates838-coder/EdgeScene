from __future__ import annotations

import unittest

from shine.engine import ShineEngine, tier_for_ev
from shine.intelligence import IntelligenceLayer
from shine.odds_api import normalize_odds_response
from shine.odds_math import american_to_probability, no_vig_probabilities


class OddsMathTests(unittest.TestCase):
    def test_no_vig_probabilities_sum_to_one(self) -> None:
        implied = {
            "Favorite": american_to_probability(-150),
            "Dog": american_to_probability(130),
        }

        no_vig = no_vig_probabilities(implied)

        self.assertAlmostEqual(sum(no_vig.values()), 1.0)
        self.assertGreater(no_vig["Favorite"], no_vig["Dog"])


class EngineTests(unittest.TestCase):
    def test_context_adjustment_boosts_big_stage_team(self) -> None:
        events = _events()
        intelligence = IntelligenceLayer.from_dict(
            {
                "entities": {
                    "Team Alpha": {
                        "pressure_rating": 0.8,
                        "style_tags": ["pace_up"],
                    }
                },
                "events": {"event-1": {"big_competition": True}},
            }
        )

        legs = ShineEngine(intelligence).build_legs(events)
        alpha = next(leg for leg in legs if leg.participant == "Team Alpha")

        self.assertGreater(alpha.adjusted_probability, alpha.no_vig_probability)
        self.assertIn("pressure_boost", {adjustment.name for adjustment in alpha.adjustments})
        self.assertIn("pace_up", alpha.style_tags)

    def test_rank_parlays_uses_distinct_events_and_tiers_ev(self) -> None:
        events = _events()
        intelligence = IntelligenceLayer.from_dict(
            {
                "entities": {
                    "Team Alpha": {"pressure_rating": 1.0, "style_tags": ["pace_up"]},
                    "Team Gamma": {"pressure_rating": 1.0, "style_tags": ["pace_up"]},
                    "Team Epsilon": {"pressure_rating": 1.0, "style_tags": ["pace_up"]},
                },
                "events": {
                    "event-1": {"big_competition": True},
                    "event-2": {"big_competition": True},
                    "event-3": {"big_competition": True},
                },
            }
        )

        parlays = ShineEngine(intelligence).rank_parlays(events, legs_per_parlay=3, limit=5)

        self.assertTrue(parlays)
        for parlay in parlays:
            self.assertEqual(len({leg.event_id for leg in parlay.legs}), 3)
            self.assertIn(parlay.tier, {"S", "A", "B", "C", "D"})

    def test_tier_thresholds(self) -> None:
        self.assertEqual(tier_for_ev(0.12), "S")
        self.assertEqual(tier_for_ev(0.06), "A")
        self.assertEqual(tier_for_ev(0.02), "B")
        self.assertEqual(tier_for_ev(0.0), "C")
        self.assertEqual(tier_for_ev(-0.01), "D")


def _events():
    payload = [
        _event("event-1", "basketball_nba", "NBA Playoffs", "Team Alpha", "Team Beta", -110, -105),
        _event("event-2", "basketball_nba", "NBA Playoffs", "Team Gamma", "Team Delta", 120, -140),
        _event("event-3", "basketball_nba", "NBA Playoffs", "Team Epsilon", "Team Zeta", 140, -160),
    ]
    return normalize_odds_response(payload)


def _event(
    event_id: str,
    sport_key: str,
    sport_title: str,
    home_team: str,
    away_team: str,
    home_price: int,
    away_price: int,
):
    return {
        "id": event_id,
        "sport_key": sport_key,
        "sport_title": sport_title,
        "commence_time": "2026-05-20T00:00:00Z",
        "home_team": home_team,
        "away_team": away_team,
        "bookmakers": [
            {
                "key": "book_a",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": home_team, "price": home_price},
                            {"name": away_team, "price": away_price},
                        ],
                    }
                ],
            },
            {
                "key": "book_b",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": home_team, "price": home_price + 5},
                            {"name": away_team, "price": away_price - 5},
                        ],
                    }
                ],
            },
        ],
    }


if __name__ == "__main__":
    unittest.main()
