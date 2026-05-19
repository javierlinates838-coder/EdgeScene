"""Tests for the correlation engine."""

import pytest

from shine.core.config import Sport
from shine.core.models import ParlayLeg
from shine.correlation.engine import analyze_correlation, apply_correlation_to_parlay


def _make_leg(game_id, sport, team, opponent, prob=0.6, odds=-150, implied=0.55):
    return ParlayLeg(
        game_id=game_id,
        sport=sport,
        team=team,
        opponent=opponent,
        best_american_odds=odds,
        implied_probability=implied,
        true_probability=prob,
        adjusted_probability=prob,
    )


class TestCorrelation:
    def test_single_leg(self):
        legs = [_make_leg("g1", Sport.NBA, "Celtics", "Bucks")]
        result = analyze_correlation(legs)
        assert result.composite_factor == 1.0

    def test_cross_sport_independent(self):
        legs = [
            _make_leg("g1", Sport.NBA, "Celtics", "Bucks"),
            _make_leg("g2", Sport.NFL, "Chiefs", "Bills"),
        ]
        result = analyze_correlation(legs)
        assert abs(result.composite_factor - 1.0) < 0.05

    def test_same_game_conflict_detected(self):
        legs = [
            _make_leg("g1", Sport.NBA, "Celtics", "Bucks"),
            _make_leg("g1", Sport.NBA, "Bucks", "Celtics"),
        ]
        result = analyze_correlation(legs)
        assert result.composite_factor < 0.5

    def test_same_sport_different_games(self):
        legs = [
            _make_leg("g1", Sport.NBA, "Celtics", "Bucks", prob=0.7),
            _make_leg("g2", Sport.NBA, "Lakers", "Warriors", prob=0.7),
        ]
        result = analyze_correlation(legs)
        assert result.composite_factor != 0

    def test_underdog_negative_correlation(self):
        legs = [
            _make_leg("g1", Sport.NFL, "Team A", "Team B", prob=0.35),
            _make_leg("g2", Sport.NFL, "Team C", "Team D", prob=0.35),
        ]
        result = analyze_correlation(legs)
        assert result.composite_factor < 1.0

    def test_correlation_applied_to_probability(self):
        from shine.correlation.engine import CorrelationResult
        result = CorrelationResult(composite_factor=1.05)
        raw_prob = 0.10
        adjusted = apply_correlation_to_parlay(raw_prob, result)
        assert adjusted > raw_prob

    def test_multi_leg_correlation(self):
        legs = [
            _make_leg("g1", Sport.NBA, "Celtics", "Bucks", prob=0.65),
            _make_leg("g2", Sport.NFL, "Chiefs", "Bills", prob=0.6),
            _make_leg("g3", Sport.CS2, "NaVi", "FaZe", prob=0.55),
        ]
        result = analyze_correlation(legs)
        assert 0.8 < result.composite_factor < 1.2
