import unittest
from unittest.mock import patch

from shine.models import EventOdds, TeamOdds
from shine.web import create_app


def _fake_event() -> EventOdds:
    return EventOdds(
        sport_key="basketball_nba",
        sport_title="NBA",
        event_id="evt-1",
        commence_time="2026-01-01T00:00:00Z",
        home_team="Lakers",
        away_team="Nuggets",
        bookmaker="testbook",
        teams=[
            TeamOdds(team="Lakers", american_odds=-110, implied_probability=0.5, true_probability=0.51),
            TeamOdds(team="Nuggets", american_odds=105, implied_probability=0.5, true_probability=0.49),
        ],
    )


class TestWebApp(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        self.client = app.test_client()

    def test_meta_endpoint(self) -> None:
        response = self.client.get("/api/meta")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("sport_options", payload)
        self.assertIn("defaults", payload)

    def test_parlays_requires_api_key(self) -> None:
        response = self.client.post("/api/parlays", json={"sports": ["basketball_nba"]})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertIn("Missing API key", payload["error"])

    @patch("shine.web.OddsApiClient.fetch_moneyline_odds")
    def test_parlays_returns_results(self, mock_fetch) -> None:
        mock_fetch.return_value = [_fake_event()]
        response = self.client.post(
            "/api/parlays",
            json={
                "api_key": "toa_live_example",
                "sports": ["basketball_nba"],
                "max_legs": 2,
                "max_parlays": 5,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertGreaterEqual(payload["event_count"], 1)
        self.assertIn("parlays", payload)


if __name__ == "__main__":
    unittest.main()
