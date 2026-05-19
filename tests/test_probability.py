import math

from shine.probability import ev_tier, expected_value, implied_probability_from_decimal, remove_vig_from_outcomes


def test_implied_probability() -> None:
    assert math.isclose(implied_probability_from_decimal(2.0), 0.5)


def test_remove_vig_two_way_market() -> None:
    probs = remove_vig_from_outcomes([1.80, 2.20])
    assert math.isclose(sum(probs), 1.0, rel_tol=1e-9)
    assert probs[0] > probs[1]


def test_ev_and_tier() -> None:
    ev = expected_value(model_probability=0.40, decimal_payout_multiple=3.2)
    assert ev_tier(ev) in {"A", "B", "C", "S", "D"}
