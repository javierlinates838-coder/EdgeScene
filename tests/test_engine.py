"""Tests for the Shine engine end-to-end."""

import pytest

from shine.core.config import ShineConfig, Sport, Tier
from shine.core.engine import ShineEngine
from shine.data.mock_odds import get_mock_games


class TestEngineWithMockData:
    def setup_method(self):
        self.config = ShineConfig()
        self.engine = ShineEngine(self.config)
        self.mock_games = get_mock_games()

    def test_produces_parlays(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=5)
        assert len(result.parlays) > 0

    def test_games_analyzed(self):
        result = self.engine.run_with_mock_data(self.mock_games)
        assert result.games_analyzed > 0

    def test_multi_sport_coverage(self):
        result = self.engine.run_with_mock_data(self.mock_games)
        assert len(result.sports_covered) > 1

    def test_parlay_structure(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=3)
        for parlay in result.parlays:
            assert len(parlay.legs) >= 2
            assert parlay.tier in Tier
            assert parlay.raw_parlay_prob > 0
            assert parlay.correlated_parlay_prob > 0
            assert parlay.correlation_factor > 0

    def test_legs_have_data(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=1)
        if result.parlays:
            for leg in result.parlays[0].legs:
                assert leg.team
                assert leg.opponent
                assert leg.best_american_odds != 0
                assert 0 < leg.adjusted_probability < 1

    def test_ev_calculated(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=5)
        for parlay in result.parlays:
            assert isinstance(parlay.true_ev_percent, float)

    def test_sorted_by_ev(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=10)
        evs = [p.true_ev_percent for p in result.parlays]
        assert evs == sorted(evs, reverse=True)

    def test_no_same_game_conflicts(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=20)
        for parlay in result.parlays:
            game_ids = [leg.game_id for leg in parlay.legs]
            assert len(game_ids) == len(set(game_ids))

    def test_best_parlay(self):
        result = self.engine.run_with_mock_data(self.mock_games)
        best = result.best_parlay
        if result.parlays:
            assert best is not None
            assert best.true_ev_percent >= max(p.true_ev_percent for p in result.parlays) - 0.01

    def test_min_ev_filter(self):
        result = self.engine.run_with_mock_data(
            self.mock_games, min_ev=5.0, max_parlays=50
        )
        for parlay in result.parlays:
            assert parlay.true_ev_percent >= 5.0

    def test_max_legs_respected(self):
        result = self.engine.run_with_mock_data(
            self.mock_games, max_legs=2, max_parlays=50
        )
        for parlay in result.parlays:
            assert len(parlay.legs) <= 2

    def test_cross_sport_parlays_exist(self):
        result = self.engine.run_with_mock_data(self.mock_games, max_parlays=50, max_legs=4)
        cross_sport = [p for p in result.parlays if p.is_cross_sport]
        assert len(cross_sport) > 0
