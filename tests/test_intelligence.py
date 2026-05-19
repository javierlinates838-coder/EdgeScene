"""Tests for the intelligence layer."""

import pytest

from shine.core.config import Sport
from shine.core.models import GameContext
from shine.data.big_competitions import (
    detect_big_competition,
    get_pressure_profile,
)
from shine.intelligence.pressure import apply_intelligence


class TestBigCompetitionDetection:
    def test_nba_playoffs(self):
        comp = detect_big_competition(Sport.NBA, "NBA Playoffs Round 1")
        assert comp is not None
        assert "Playoff" in comp.name

    def test_super_bowl(self):
        comp = detect_big_competition(Sport.NFL, "Super Bowl LVIII")
        assert comp is not None
        assert comp.pressure_multiplier > 1.2

    def test_cs2_major(self):
        comp = detect_big_competition(Sport.CS2, "PGL Major Copenhagen")
        assert comp is not None

    def test_worlds(self):
        comp = detect_big_competition(Sport.LOL, "LoL World Championship")
        assert comp is not None

    def test_no_match(self):
        comp = detect_big_competition(Sport.NBA, "regular season Tuesday game")
        assert comp is None


class TestPressureProfiles:
    def test_known_team(self):
        profile = get_pressure_profile("Kansas City Chiefs")
        assert profile is not None
        assert profile.clutch_rating > 1.0

    def test_partial_match(self):
        profile = get_pressure_profile("Chiefs")
        assert profile is not None

    def test_unknown_team(self):
        profile = get_pressure_profile("Nonexistent Unicorns")
        assert profile is None

    def test_esports_team(self):
        profile = get_pressure_profile("T1")
        assert profile is not None
        assert profile.clutch_rating > 1.0


class TestIntelligenceAdjustments:
    def test_probabilities_sum_to_one(self):
        context = GameContext(sport=Sport.NBA)
        result_a, result_b = apply_intelligence(
            "Boston Celtics", "Milwaukee Bucks", 0.6, 0.4, context
        )
        total = result_a.adjusted_probability + result_b.adjusted_probability
        assert abs(total - 1.0) < 0.01

    def test_playoff_adjustment(self):
        context = GameContext(
            sport=Sport.NBA,
            is_playoff=True,
            playoff_round="Conference Finals",
            season_phase="playoff",
            home_team="Boston Celtics",
        )
        result_a, result_b = apply_intelligence(
            "Boston Celtics", "Milwaukee Bucks", 0.55, 0.45, context
        )
        assert len(result_a.adjustments) > 0 or len(result_b.adjustments) > 0

    def test_known_vs_unknown(self):
        context = GameContext(sport=Sport.NBA)
        result_a, result_b = apply_intelligence(
            "Golden State Warriors", "Unknown Team", 0.5, 0.5, context
        )
        assert result_a.adjusted_probability != result_b.adjusted_probability or \
               len(result_a.adjustments) != len(result_b.adjustments)

    def test_bounds_respected(self):
        context = GameContext(sport=Sport.NBA, is_playoff=True, season_phase="playoff")
        result_a, result_b = apply_intelligence(
            "Boston Celtics", "Milwaukee Bucks", 0.95, 0.05, context
        )
        assert 0.01 < result_a.adjusted_probability < 0.99
        assert 0.01 < result_b.adjusted_probability < 0.99
