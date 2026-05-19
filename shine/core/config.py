"""Global configuration and sport definitions for Shine v4."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


class Sport(str, Enum):
    NBA = "basketball_nba"
    NFL = "americanfootball_nfl"
    MLB = "baseball_mlb"
    NHL = "icehockey_nhl"
    SOCCER_EPL = "soccer_epl"
    SOCCER_UCL = "soccer_uefa_champs_league"
    SOCCER_LALIGA = "soccer_spain_la_liga"
    SOCCER_BUNDESLIGA = "soccer_germany_bundesliga"
    SOCCER_SERIEA = "soccer_italy_serie_a"
    SOCCER_LIGUE1 = "soccer_france_ligue_one"
    SOCCER_MLS = "soccer_usa_mls"
    CS2 = "esports_csgo"
    LOL = "esports_lol"
    VAL = "esports_valorant"
    UFC = "mma_mixed_martial_arts"


SPORT_DISPLAY_NAMES = {
    Sport.NBA: "NBA",
    Sport.NFL: "NFL",
    Sport.MLB: "MLB",
    Sport.NHL: "NHL",
    Sport.SOCCER_EPL: "EPL",
    Sport.SOCCER_UCL: "Champions League",
    Sport.SOCCER_LALIGA: "La Liga",
    Sport.SOCCER_BUNDESLIGA: "Bundesliga",
    Sport.SOCCER_SERIEA: "Serie A",
    Sport.SOCCER_LIGUE1: "Ligue 1",
    Sport.SOCCER_MLS: "MLS",
    Sport.CS2: "CS2",
    Sport.LOL: "LoL",
    Sport.VAL: "VALORANT",
    Sport.UFC: "UFC",
}

SPORT_CATEGORIES = {
    "basketball": [Sport.NBA],
    "football": [Sport.NFL],
    "baseball": [Sport.MLB],
    "hockey": [Sport.NHL],
    "soccer": [
        Sport.SOCCER_EPL, Sport.SOCCER_UCL, Sport.SOCCER_LALIGA,
        Sport.SOCCER_BUNDESLIGA, Sport.SOCCER_SERIEA, Sport.SOCCER_LIGUE1,
        Sport.SOCCER_MLS,
    ],
    "esports": [Sport.CS2, Sport.LOL, Sport.VAL],
    "mma": [Sport.UFC],
}

ALL_SPORTS = list(Sport)


class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


def tier_from_ev(ev_percent: float) -> Tier:
    """Assign tier based on expected value percentage edge."""
    if ev_percent >= 12.0:
        return Tier.S
    elif ev_percent >= 7.0:
        return Tier.A
    elif ev_percent >= 3.0:
        return Tier.B
    elif ev_percent >= 0.0:
        return Tier.C
    else:
        return Tier.D


TIER_LABELS = {
    Tier.S: "ELITE — Strong positive EV, high confidence",
    Tier.A: "GREAT — Solid edge, worth betting",
    Tier.B: "GOOD — Modest edge, selective bet",
    Tier.C: "NEUTRAL — Breakeven or marginal edge",
    Tier.D: "AVOID — Negative EV, sportsbook wins",
}


@dataclass
class ShineConfig:
    odds_api_key: str = field(default_factory=lambda: os.getenv("ODDS_API_KEY", ""))
    odds_api_base: str = "https://api.the-odds-api.com/v4"
    default_regions: str = "us,us2,eu"
    default_markets: str = "h2h"
    min_legs: int = 2
    max_legs: int = 10
    min_ev_threshold: float = -5.0
    default_stake: float = 10.0
    correlation_weight: float = 1.0
    intelligence_weight: float = 1.0
    environment_weight: float = 1.0

    @property
    def has_api_key(self) -> bool:
        return bool(self.odds_api_key)

    @classmethod
    def from_env(cls) -> "ShineConfig":
        return cls(
            odds_api_key=os.getenv("ODDS_API_KEY", ""),
            default_regions=os.getenv("ODDS_REGIONS", "us,us2,eu"),
        )
