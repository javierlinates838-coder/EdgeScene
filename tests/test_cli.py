import unittest

from shine.cli import _sanitize_api_key


class TestCliHelpers(unittest.TestCase):
    def test_sanitize_api_key_uses_token_with_toa_prefix(self) -> None:
        raw = "this the api for the toa_live_30c71bf4 the theoddsapi"
        self.assertEqual(_sanitize_api_key(raw), "toa_live_30c71bf4")

    def test_sanitize_api_key_returns_clean_value(self) -> None:
        self.assertEqual(_sanitize_api_key("  toa_live_abc123  "), "toa_live_abc123")
        self.assertEqual(_sanitize_api_key(""), "")


if __name__ == "__main__":
    unittest.main()
