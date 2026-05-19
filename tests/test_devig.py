from shine.math.devig import devig, devig_multiplicative, devig_power, devig_shin


def test_multiplicative_sums_to_one():
    out = devig_multiplicative([0.55, 0.50])
    assert abs(sum(out) - 1.0) < 1e-9


def test_power_sums_to_one():
    out = devig_power([0.55, 0.50])
    assert abs(sum(out) - 1.0) < 1e-6


def test_shin_sums_to_one_two_way():
    out = devig_shin([0.55, 0.50])
    assert abs(sum(out) - 1.0) < 1e-6
    # Shin should leave favorite still favored
    assert out[0] > out[1]


def test_dispatch():
    out = devig([0.6, 0.45], method="shin")
    assert abs(sum(out) - 1.0) < 1e-6
