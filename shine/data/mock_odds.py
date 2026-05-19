"""
Mock odds data for testing Shine without hitting the API.
Realistic odds across multiple sports.
"""

from shine.core.config import Sport


def get_mock_games():
    """Return realistic mock game data across all supported sports."""
    return [
        # NBA Games
        {
            "_sport": Sport.NBA,
            "id": "nba_001",
            "sport_key": "basketball_nba",
            "sport_title": "NBA",
            "home_team": "Boston Celtics",
            "away_team": "Milwaukee Bucks",
            "commence_time": "2026-05-20T00:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Boston Celtics", -180, "Milwaukee Bucks", 155),
                _bookmaker("FanDuel", "Boston Celtics", -175, "Milwaukee Bucks", 150),
                _bookmaker("BetMGM", "Boston Celtics", -185, "Milwaukee Bucks", 160),
                _bookmaker("Caesars", "Boston Celtics", -170, "Milwaukee Bucks", 148),
            ],
        },
        {
            "_sport": Sport.NBA,
            "id": "nba_002",
            "sport_key": "basketball_nba",
            "sport_title": "NBA Playoffs",
            "home_team": "Denver Nuggets",
            "away_team": "Oklahoma City Thunder",
            "commence_time": "2026-05-20T02:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Denver Nuggets", -145, "Oklahoma City Thunder", 125),
                _bookmaker("FanDuel", "Denver Nuggets", -140, "Oklahoma City Thunder", 120),
                _bookmaker("BetMGM", "Denver Nuggets", -150, "Oklahoma City Thunder", 130),
            ],
        },
        {
            "_sport": Sport.NBA,
            "id": "nba_003",
            "sport_key": "basketball_nba",
            "sport_title": "NBA",
            "home_team": "Golden State Warriors",
            "away_team": "Los Angeles Lakers",
            "commence_time": "2026-05-20T03:30:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Golden State Warriors", -130, "Los Angeles Lakers", 110),
                _bookmaker("FanDuel", "Golden State Warriors", -125, "Los Angeles Lakers", 108),
                _bookmaker("BetMGM", "Golden State Warriors", -135, "Los Angeles Lakers", 115),
            ],
        },

        # NFL Games
        {
            "_sport": Sport.NFL,
            "id": "nfl_001",
            "sport_key": "americanfootball_nfl",
            "sport_title": "NFL",
            "home_team": "Kansas City Chiefs",
            "away_team": "Buffalo Bills",
            "commence_time": "2026-09-07T20:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Kansas City Chiefs", -155, "Buffalo Bills", 135),
                _bookmaker("FanDuel", "Kansas City Chiefs", -150, "Buffalo Bills", 130),
                _bookmaker("BetMGM", "Kansas City Chiefs", -160, "Buffalo Bills", 140),
            ],
        },
        {
            "_sport": Sport.NFL,
            "id": "nfl_002",
            "sport_key": "americanfootball_nfl",
            "sport_title": "NFL",
            "home_team": "Philadelphia Eagles",
            "away_team": "San Francisco 49ers",
            "commence_time": "2026-09-07T16:30:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Philadelphia Eagles", -120, "San Francisco 49ers", 102),
                _bookmaker("FanDuel", "Philadelphia Eagles", -118, "San Francisco 49ers", 100),
                _bookmaker("BetMGM", "Philadelphia Eagles", -125, "San Francisco 49ers", 105),
            ],
        },

        # Soccer (EPL)
        {
            "_sport": Sport.SOCCER_EPL,
            "id": "epl_001",
            "sport_key": "soccer_epl",
            "sport_title": "EPL",
            "home_team": "Manchester City",
            "away_team": "Liverpool",
            "commence_time": "2026-10-15T14:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Manchester City", -110, "Liverpool", 105, draw=280),
                _bookmaker("Bet365", "Manchester City", -108, "Liverpool", 100, draw=275),
                _bookmaker("William Hill", "Manchester City", -115, "Liverpool", 110, draw=285),
            ],
        },

        # CS2
        {
            "_sport": Sport.CS2,
            "id": "cs2_001",
            "sport_key": "esports_csgo",
            "sport_title": "CS2 Major",
            "home_team": "Natus Vincere",
            "away_team": "FaZe Clan",
            "commence_time": "2026-06-15T16:00:00Z",
            "bookmakers": [
                _bookmaker("Betway", "Natus Vincere", -125, "FaZe Clan", 105),
                _bookmaker("Pinnacle", "Natus Vincere", -118, "FaZe Clan", 102),
            ],
        },
        {
            "_sport": Sport.CS2,
            "id": "cs2_002",
            "sport_key": "esports_csgo",
            "sport_title": "CS2 Major",
            "home_team": "Vitality",
            "away_team": "G2 Esports",
            "commence_time": "2026-06-15T18:00:00Z",
            "bookmakers": [
                _bookmaker("Betway", "Vitality", -140, "G2 Esports", 120),
                _bookmaker("Pinnacle", "Vitality", -135, "G2 Esports", 115),
            ],
        },

        # LoL
        {
            "_sport": Sport.LOL,
            "id": "lol_001",
            "sport_key": "esports_lol",
            "sport_title": "LoL Worlds",
            "home_team": "T1",
            "away_team": "Gen.G",
            "commence_time": "2026-10-20T10:00:00Z",
            "bookmakers": [
                _bookmaker("Betway", "T1", -115, "Gen.G", -102),
                _bookmaker("Pinnacle", "T1", -110, "Gen.G", -105),
            ],
        },

        # VALORANT
        {
            "_sport": Sport.VAL,
            "id": "val_001",
            "sport_key": "esports_valorant",
            "sport_title": "VAL Champions",
            "home_team": "Sentinels",
            "away_team": "Fnatic",
            "commence_time": "2026-08-10T18:00:00Z",
            "bookmakers": [
                _bookmaker("Betway", "Sentinels", 110, "Fnatic", -130),
                _bookmaker("Pinnacle", "Sentinels", 105, "Fnatic", -125),
            ],
        },

        # UFC
        {
            "_sport": Sport.UFC,
            "id": "ufc_001",
            "sport_key": "mma_mixed_martial_arts",
            "sport_title": "UFC PPV",
            "home_team": "Fighter Alpha",
            "away_team": "Fighter Beta",
            "commence_time": "2026-07-05T22:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Fighter Alpha", -200, "Fighter Beta", 170),
                _bookmaker("FanDuel", "Fighter Alpha", -195, "Fighter Beta", 165),
                _bookmaker("BetMGM", "Fighter Alpha", -210, "Fighter Beta", 175),
            ],
        },

        # MLB
        {
            "_sport": Sport.MLB,
            "id": "mlb_001",
            "sport_key": "baseball_mlb",
            "sport_title": "MLB",
            "home_team": "Los Angeles Dodgers",
            "away_team": "Houston Astros",
            "commence_time": "2026-06-20T19:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Los Angeles Dodgers", -135, "Houston Astros", 115),
                _bookmaker("FanDuel", "Los Angeles Dodgers", -130, "Houston Astros", 112),
                _bookmaker("BetMGM", "Los Angeles Dodgers", -140, "Houston Astros", 120),
            ],
        },

        # NHL
        {
            "_sport": Sport.NHL,
            "id": "nhl_001",
            "sport_key": "icehockey_nhl",
            "sport_title": "NHL Stanley Cup Playoffs",
            "home_team": "Edmonton Oilers",
            "away_team": "Florida Panthers",
            "commence_time": "2026-05-25T20:00:00Z",
            "bookmakers": [
                _bookmaker("DraftKings", "Edmonton Oilers", -120, "Florida Panthers", 102),
                _bookmaker("FanDuel", "Edmonton Oilers", -118, "Florida Panthers", 100),
                _bookmaker("BetMGM", "Edmonton Oilers", -125, "Florida Panthers", 105),
            ],
        },
    ]


def _bookmaker(name, team_a, odds_a, team_b, odds_b, draw=None):
    """Helper to build bookmaker data in API format."""
    outcomes = [
        {"name": team_a, "price": odds_a},
        {"name": team_b, "price": odds_b},
    ]
    if draw is not None:
        outcomes.append({"name": "Draw", "price": draw})

    return {
        "key": name.lower().replace(" ", "_"),
        "title": name,
        "last_update": "2026-05-19T18:00:00Z",
        "markets": [
            {
                "key": "h2h",
                "outcomes": outcomes,
            }
        ],
    }
