import unittest

from shine.odds_api import OddsApiClient


class TestOddsApiHelpers(unittest.TestCase):
    def test_extract_error_message_from_json(self) -> None:
        body = '{"message":"Invalid API key"}'
        self.assertEqual(OddsApiClient._extract_error_message(body), "Invalid API key")

    def test_extract_error_message_from_text(self) -> None:
        body = "Unauthorized"
        self.assertEqual(OddsApiClient._extract_error_message(body), "Unauthorized")

    def test_extract_error_message_empty(self) -> None:
        self.assertIsNone(OddsApiClient._extract_error_message(""))

    def test_normalize_american_price_handles_string_number(self) -> None:
        self.assertEqual(OddsApiClient._normalize_american_price("+115"), 115)
        self.assertEqual(OddsApiClient._normalize_american_price("-110.0"), -110)

    def test_extract_market_accepts_numeric_string_prices(self) -> None:
        bookmakers = [
            {
                "title": "book-a",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team A", "price": "-110"},
                            {"name": "Team B", "price": "+105"},
                        ],
                    }
                ],
            }
        ]
        market = OddsApiClient._extract_market(bookmakers)
        self.assertIsNotNone(market)
        bookmaker, outcomes = market  # type: ignore[misc]
        self.assertEqual(bookmaker, "book-a")
        self.assertEqual(outcomes[0]["price"], -110)
        self.assertEqual(outcomes[1]["price"], 105)


if __name__ == "__main__":
    unittest.main()
