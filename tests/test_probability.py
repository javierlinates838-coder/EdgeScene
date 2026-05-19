"""Tests for probability math — the foundation of Shine."""

import pytest

from shine.core.probability import (
    VigAnalysis,
    american_to_implied,
    calculate_ev_percent,
    implied_to_american,
    median_probability,
    parlay_probability,
    remove_vig_additive,
    remove_vig_best,
    remove_vig_power,
)


class TestAmericanToImplied:
    def test_favorite(self):
        prob = american_to_implied(-150)
        assert abs(prob - 0.6) < 0.01

    def test_underdog(self):
        prob = american_to_implied(150)
        assert abs(prob - 0.4) < 0.01

    def test_even(self):
        prob = american_to_implied(100)
        assert abs(prob - 0.5) < 0.01

    def test_heavy_favorite(self):
        prob = american_to_implied(-300)
        assert prob > 0.7

    def test_heavy_underdog(self):
        prob = american_to_implied(300)
        assert prob < 0.3


class TestImpliedToAmerican:
    def test_favorite(self):
        odds = implied_to_american(0.6)
        assert odds < 0

    def test_underdog(self):
        odds = implied_to_american(0.4)
        assert odds > 0

    def test_even(self):
        odds = implied_to_american(0.5)
        assert abs(odds) == 100

    def test_roundtrip(self):
        for original in [-200, -150, -110, 150, 200, 300]:
            implied = american_to_implied(original)
            back = implied_to_american(implied)
            assert abs(back - original) <= 2

    def test_roundtrip_even(self):
        implied = american_to_implied(100)
        back = implied_to_american(implied)
        assert abs(back) == 100


class TestVigRemoval:
    def test_additive_basic(self):
        fair_a, fair_b = remove_vig_additive(0.55, 0.50)
        assert abs(fair_a + fair_b - 1.0) < 0.001

    def test_power_basic(self):
        fair_a, fair_b = remove_vig_power(0.55, 0.50)
        assert abs(fair_a + fair_b - 1.0) < 0.001

    def test_no_vig_passthrough(self):
        fair_a, fair_b = remove_vig_additive(0.50, 0.50)
        assert abs(fair_a - 0.50) < 0.001
        assert abs(fair_b - 0.50) < 0.001

    def test_vig_reduces_probabilities(self):
        vigged_a = american_to_implied(-110)
        vigged_b = american_to_implied(-110)
        assert vigged_a + vigged_b > 1.0
        fair_a, fair_b = remove_vig_best(vigged_a, vigged_b)
        assert abs(fair_a + fair_b - 1.0) < 0.001

    def test_best_method_skewed(self):
        fair_a, fair_b = remove_vig_best(0.85, 0.20)
        assert abs(fair_a + fair_b - 1.0) < 0.01


class TestParlayMath:
    def test_two_leg(self):
        prob = parlay_probability([0.6, 0.7])
        assert abs(prob - 0.42) < 0.001

    def test_three_leg(self):
        prob = parlay_probability([0.5, 0.5, 0.5])
        assert abs(prob - 0.125) < 0.001

    def test_single_leg(self):
        prob = parlay_probability([0.6])
        assert abs(prob - 0.6) < 0.001


class TestEV:
    def test_positive_ev(self):
        ev = calculate_ev_percent(0.55, 0.50)
        assert ev > 0

    def test_negative_ev(self):
        ev = calculate_ev_percent(0.45, 0.50)
        assert ev < 0

    def test_zero_ev(self):
        ev = calculate_ev_percent(0.50, 0.50)
        assert abs(ev) < 0.01


class TestMedian:
    def test_odd_count(self):
        assert abs(median_probability([0.4, 0.5, 0.6]) - 0.5) < 0.001

    def test_even_count(self):
        result = median_probability([0.4, 0.6])
        assert abs(result - 0.5) < 0.001

    def test_single(self):
        assert abs(median_probability([0.7]) - 0.7) < 0.001

    def test_empty(self):
        assert abs(median_probability([]) - 0.5) < 0.001


class TestVigAnalysis:
    def test_standard_line(self):
        analysis = VigAnalysis.analyze(-110, -110)
        assert analysis.vig_percent > 0
        assert abs(analysis.fair_a - 0.5) < 0.01
        assert abs(analysis.fair_b - 0.5) < 0.01

    def test_skewed_line(self):
        analysis = VigAnalysis.analyze(-200, 170)
        assert analysis.fair_a > 0.5
        assert analysis.fair_b < 0.5
        assert abs(analysis.fair_a + analysis.fair_b - 1.0) < 0.01
