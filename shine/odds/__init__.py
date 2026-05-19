"""Odds ingestion."""

from .client import OddsAPIClient, OddsAPIError
from .sports import SPORTS, sport_keys_for

__all__ = ["OddsAPIClient", "OddsAPIError", "SPORTS", "sport_keys_for"]
