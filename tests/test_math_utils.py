import unittest

from shine.math_utils import (
    american_to_decimal_multiplier,
    american_to_implied_probability,
    parlay_payout_multiplier,
    remove_vig,
)


class TestMathUtils(unittest.TestCase):
    def test_american_to_implied_probability_positive(self) -> None:
        self.assertAlmostEqual(american_to_implied_probability(+100), 0.5, places=5)
        self.assertAlmostEqual(american_to_implied_probability(+150), 0.4, places=5)

    def test_american_to_implied_probability_negative(self) -> None:
        self.assertAlmostEqual(american_to_implied_probability(-110), 0.523809, places=5)
        self.assertAlmostEqual(american_to_implied_probability(-200), 0.666666, places=5)

    def test_remove_vig(self) -> None:
        no_vig = remove_vig([0.523809, 0.523809])
        self.assertAlmostEqual(no_vig[0], 0.5, places=5)
        self.assertAlmostEqual(no_vig[1], 0.5, places=5)
        self.assertAlmostEqual(sum(no_vig), 1.0, places=5)

    def test_parlay_payout_multiplier(self) -> None:
        payout = parlay_payout_multiplier([-110, +150])
        expected = american_to_decimal_multiplier(-110) * american_to_decimal_multiplier(+150)
        self.assertAlmostEqual(payout, expected, places=6)


if __name__ == "__main__":
    unittest.main()
