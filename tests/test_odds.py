from shine.math.odds import american_to_decimal, decimal_to_american, decimal_to_prob


def test_american_to_decimal_underdog():
    assert american_to_decimal(+150) == 2.5


def test_american_to_decimal_favorite():
    assert abs(american_to_decimal(-200) - 1.5) < 1e-9


def test_round_trip():
    for a in (-300, -150, +110, +250, +500):
        d = american_to_decimal(a)
        assert decimal_to_american(d) == a


def test_implied_prob():
    assert abs(decimal_to_prob(2.0) - 0.5) < 1e-9
