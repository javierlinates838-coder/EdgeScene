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


if __name__ == "__main__":
    unittest.main()
