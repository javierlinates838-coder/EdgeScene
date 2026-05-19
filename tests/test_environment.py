"""Tests for environment adjustments."""

import pytest

from shine.core.config import Sport
from shine.core.models import GameContext
from shine.environment.adjustments import apply_environment


class TestHomeAdvantage:
    def test_home_team_boosted(self):
        context = GameContext(
            sport=Sport.NBA,
            home_team="Boston Celtics",
            away_team="Milwaukee Bucks",
            venue_city="Boston",
        )
        result_a, result_b = apply_environment(
            "Boston Celtics", "Milwaukee Bucks", 0.5, 0.5, context
        )
        assert result_a.adjusted_probability > result_b.adjusted_probability

    def test_neutral_site_no_home_boost(self):
        context = GameContext(
            sport=Sport.NBA,
            is_neutral_site=True,
            home_team="Boston Celtics",
        )
        result_a, result_b = apply_environment(
            "Boston Celtics", "Milwaukee Bucks", 0.5, 0.5, context
        )
        total_adj = abs(result_a.total_adjustment) + abs(result_b.total_adjustment)
        assert total_adj < 0.01

    def test_soccer_higher_home_advantage(self):
        context = GameContext(
            sport=Sport.SOCCER_EPL,
            home_team="Liverpool",
            venue_city="Liverpool",
        )
        result_a, _ = apply_environment(
            "Liverpool", "Manchester City", 0.5, 0.5, context
        )
        assert result_a.total_adjustment > 0.02


class TestAltitude:
    def test_denver_altitude_boost(self):
        context = GameContext(
            sport=Sport.NBA,
            home_team="Denver Nuggets",
            venue_city="Denver",
        )
        result_a, result_b = apply_environment(
            "Denver Nuggets", "Los Angeles Lakers", 0.5, 0.5, context
        )
        has_altitude_adj = any("Altitude" in adj or "altitude" in adj for adj in result_a.adjustments)
        assert has_altitude_adj

    def test_no_altitude_at_sea_level(self):
        context = GameContext(
            sport=Sport.NBA,
            home_team="Miami Heat",
            venue_city="Miami",
        )
        result_a, _ = apply_environment(
            "Miami Heat", "Boston Celtics", 0.5, 0.5, context
        )
        has_altitude = any("altitude" in adj.lower() for adj in result_a.adjustments)
        assert not has_altitude


class TestNormalization:
    def test_probabilities_sum_to_one(self):
        context = GameContext(
            sport=Sport.NFL,
            home_team="Kansas City Chiefs",
            venue_city="Kansas City",
        )
        result_a, result_b = apply_environment(
            "Kansas City Chiefs", "Buffalo Bills", 0.6, 0.4, context
        )
        total = result_a.adjusted_probability + result_b.adjusted_probability
        assert abs(total - 1.0) < 0.01

    def test_extreme_probabilities_bounded(self):
        context = GameContext(
            sport=Sport.NBA,
            home_team="Team A",
            venue_city="Denver",
            altitude_ft=5280,
        )
        result_a, result_b = apply_environment(
            "Team A", "Team B", 0.98, 0.02, context
        )
        assert result_a.adjusted_probability <= 0.98
        assert result_b.adjusted_probability >= 0.02
