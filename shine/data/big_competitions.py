"""
Big-competition intelligence data: pressure performance profiles,
elite event definitions, and historical performance modifiers.

This is the knowledge layer that makes Shine smarter than generic models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from shine.core.config import Sport


@dataclass
class BigCompetition:
    """Definition of a major/elite competition."""
    name: str
    sport: Sport
    keywords: List[str]
    pressure_multiplier: float
    description: str


BIG_COMPETITIONS: List[BigCompetition] = [
    # Basketball
    BigCompetition("NBA Playoffs", Sport.NBA, ["playoff", "postseason"], 1.15, "NBA postseason"),
    BigCompetition("NBA Finals", Sport.NBA, ["finals", "nba finals"], 1.25, "NBA championship series"),
    BigCompetition("NBA Conference Finals", Sport.NBA, ["conference finals", "ecf", "wcf"], 1.20, "Conference championship"),

    # Football
    BigCompetition("NFL Playoffs", Sport.NFL, ["playoff", "wild card", "divisional"], 1.15, "NFL postseason"),
    BigCompetition("NFL Conference Championship", Sport.NFL, ["conference championship", "nfc championship", "afc championship"], 1.20, "Conference title game"),
    BigCompetition("Super Bowl", Sport.NFL, ["super bowl"], 1.30, "NFL championship"),

    # Baseball
    BigCompetition("MLB Postseason", Sport.MLB, ["postseason", "wild card", "alds", "alcs", "nlds", "nlcs"], 1.12, "MLB postseason"),
    BigCompetition("World Series", Sport.MLB, ["world series"], 1.22, "MLB championship"),

    # Hockey
    BigCompetition("NHL Playoffs", Sport.NHL, ["playoff", "stanley cup playoffs"], 1.15, "NHL postseason"),
    BigCompetition("Stanley Cup Finals", Sport.NHL, ["stanley cup final"], 1.25, "NHL championship"),

    # Soccer
    BigCompetition("Champions League Knockout", Sport.SOCCER_UCL, ["knockout", "round of 16", "quarterfinal", "semifinal"], 1.18, "UCL knockout stage"),
    BigCompetition("Champions League Final", Sport.SOCCER_UCL, ["final"], 1.28, "UCL final"),

    # CS2
    BigCompetition("CS2 Major", Sport.CS2, ["major", "iem katowice", "pgl"], 1.20, "CS2 Valve Major"),
    BigCompetition("CS2 Major Playoff", Sport.CS2, ["major playoff", "champions stage"], 1.28, "CS2 Major playoff stage"),

    # LoL
    BigCompetition("LoL Worlds", Sport.LOL, ["worlds", "world championship"], 1.22, "League of Legends World Championship"),
    BigCompetition("LoL MSI", Sport.LOL, ["msi", "mid-season invitational"], 1.15, "LoL Mid-Season Invitational"),
    BigCompetition("LoL Worlds Finals", Sport.LOL, ["worlds final", "grand final"], 1.30, "Worlds Grand Final"),

    # VALORANT
    BigCompetition("VAL Champions", Sport.VAL, ["champions", "val champions"], 1.22, "VALORANT Champions"),
    BigCompetition("VAL Masters", Sport.VAL, ["masters"], 1.15, "VALORANT Masters"),
    BigCompetition("VAL Champions Playoff", Sport.VAL, ["champions playoff", "champions bracket"], 1.28, "Champions playoff bracket"),

    # UFC
    BigCompetition("UFC PPV", Sport.UFC, ["ppv", "pay-per-view", "numbered"], 1.12, "UFC numbered PPV event"),
    BigCompetition("UFC Title Fight", Sport.UFC, ["title fight", "championship", "title bout"], 1.22, "UFC championship fight"),
    BigCompetition("UFC Main Event", Sport.UFC, ["main event"], 1.08, "UFC main event slot"),
]


@dataclass
class PressureProfile:
    """How a team/player performs under pressure compared to regular season."""
    entity_name: str
    sport: Sport
    clutch_rating: float  # >1.0 = performs better under pressure, <1.0 = chokes
    big_game_record: str  # e.g. "15-7 in playoffs"
    notes: str = ""


PRESSURE_PROFILES: Dict[str, PressureProfile] = {
    # NBA — teams known for playoff performance patterns
    "Boston Celtics": PressureProfile("Boston Celtics", Sport.NBA, 1.06, "Strong playoff pedigree", "Deep roster performs well"),
    "Denver Nuggets": PressureProfile("Denver Nuggets", Sport.NBA, 1.08, "Recent champion", "Altitude + Jokic factor"),
    "Milwaukee Bucks": PressureProfile("Milwaukee Bucks", Sport.NBA, 1.04, "2021 champion", "Giannis playoff mode"),
    "Phoenix Suns": PressureProfile("Phoenix Suns", Sport.NBA, 0.95, "Inconsistent in big moments", "Talent doesn't always translate"),
    "Los Angeles Lakers": PressureProfile("Los Angeles Lakers", Sport.NBA, 1.05, "LeBron playoff experience", "Big-game experience"),
    "Golden State Warriors": PressureProfile("Golden State Warriors", Sport.NBA, 1.10, "Dynasty pedigree", "Championship DNA"),
    "Minnesota Timberwolves": PressureProfile("Minnesota Timberwolves", Sport.NBA, 0.94, "Limited playoff experience", "Young roster under pressure"),
    "Oklahoma City Thunder": PressureProfile("Oklahoma City Thunder", Sport.NBA, 0.96, "Young but talented", "SGA developing clutch gene"),

    # NFL
    "Kansas City Chiefs": PressureProfile("Kansas City Chiefs", Sport.NFL, 1.12, "Mahomes playoff dominance", "Best big-game QB"),
    "San Francisco 49ers": PressureProfile("San Francisco 49ers", Sport.NFL, 0.95, "Super Bowl struggles", "Regular season dominant, finals underperform"),
    "Philadelphia Eagles": PressureProfile("Philadelphia Eagles", Sport.NFL, 1.04, "Recent Super Bowl presence", "Strong postseason roster"),
    "Buffalo Bills": PressureProfile("Buffalo Bills", Sport.NFL, 0.93, "Playoff heartbreaks", "Regular season elite, January struggles"),
    "Baltimore Ravens": PressureProfile("Baltimore Ravens", Sport.NFL, 0.96, "Lamar playoff questions", "Dominant regular season"),
    "Detroit Lions": PressureProfile("Detroit Lions", Sport.NFL, 1.02, "New playoff contender", "Trending up"),

    # MLB
    "Los Angeles Dodgers": PressureProfile("Los Angeles Dodgers", Sport.MLB, 1.06, "Perennial contender", "October experience"),
    "Houston Astros": PressureProfile("Houston Astros", Sport.MLB, 1.08, "Consistent postseason team", "Playoff DNA"),
    "Atlanta Braves": PressureProfile("Atlanta Braves", Sport.MLB, 1.04, "2021 champion", "Strong October pedigree"),
    "New York Yankees": PressureProfile("New York Yankees", Sport.MLB, 0.97, "Underperform expectations", "High pressure market"),

    # NHL
    "Edmonton Oilers": PressureProfile("Edmonton Oilers", Sport.NHL, 1.06, "McDavid playoff mode", "Superstar carries"),
    "Florida Panthers": PressureProfile("Florida Panthers", Sport.NHL, 1.05, "Recent Finals team", "Battle-tested"),
    "Vegas Golden Knights": PressureProfile("Vegas Golden Knights", Sport.NHL, 1.04, "2023 champion", "Playoff experience"),

    # Esports — CS2
    "Natus Vincere": PressureProfile("Natus Vincere", Sport.CS2, 1.10, "Major champion", "s1mple/b1t factor"),
    "FaZe Clan": PressureProfile("FaZe Clan", Sport.CS2, 1.08, "Major champion", "Big-stage performers"),
    "G2 Esports": PressureProfile("G2 Esports", Sport.CS2, 0.94, "Historically choke in finals", "Group stage warriors"),
    "Vitality": PressureProfile("Vitality", Sport.CS2, 1.06, "ZywOo major winner", "Consistent at top level"),
    "Team Spirit": PressureProfile("Team Spirit", Sport.CS2, 1.07, "Major champion", "Dark horse to dominant"),

    # Esports — LoL
    "T1": PressureProfile("T1", Sport.LOL, 1.12, "Faker's legacy", "Most Worlds titles"),
    "Gen.G": PressureProfile("Gen.G", Sport.LOL, 0.93, "Worlds underperformers", "Domestic dominance doesn't translate"),
    "JDG": PressureProfile("JDG", Sport.LOL, 1.04, "MSI champion", "LPL powerhouse"),
    "Bilibili Gaming": PressureProfile("Bilibili Gaming", Sport.LOL, 1.02, "Improving internationally", "Rising threat"),

    # Esports — VALORANT
    "Sentinels": PressureProfile("Sentinels", Sport.VAL, 1.06, "Masters champion", "NA pride"),
    "LOUD": PressureProfile("LOUD", Sport.VAL, 1.08, "Champions winner", "Brazilian passion"),
    "Fnatic": PressureProfile("Fnatic", Sport.VAL, 1.05, "Consistent intl results", "Strong team play"),
    "Paper Rex": PressureProfile("Paper Rex", Sport.VAL, 1.04, "Aggressive style works on stage", "Fearless playstyle"),
    "DRX": PressureProfile("DRX", Sport.VAL, 1.07, "Champions 2022", "Underdog mentality"),
}


def detect_big_competition(
    sport: Sport, event_name: str = "", context_hints: List[str] = None
) -> Optional[BigCompetition]:
    """Detect if the current event is a big competition based on name/context."""
    hints = (context_hints or []) + [event_name.lower()]
    search_text = " ".join(hints).lower()

    matches: List[BigCompetition] = []
    for comp in BIG_COMPETITIONS:
        if comp.sport != sport:
            continue
        for keyword in comp.keywords:
            if keyword.lower() in search_text:
                matches.append(comp)
                break

    if not matches:
        return None

    return max(matches, key=lambda c: c.pressure_multiplier)


def get_pressure_profile(team_name: str) -> Optional[PressureProfile]:
    """Look up pressure profile for a team/player."""
    if team_name in PRESSURE_PROFILES:
        return PRESSURE_PROFILES[team_name]

    for name, profile in PRESSURE_PROFILES.items():
        if team_name.lower() in name.lower() or name.lower() in team_name.lower():
            return profile

    return None
