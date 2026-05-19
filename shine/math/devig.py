"""Vig (overround) removal methods.

All functions take a list of implied probabilities (each = 1 / decimal odds)
that sum to > 1.0 because of the bookmaker margin, and return a list of
"fair" probabilities that sum to exactly 1.0.

Three established methods are implemented:

* ``multiplicative`` — divide every implied probability by the overround.
  Simple and very common. Slightly biased toward favorites.
* ``power`` — find an exponent ``k`` such that ``sum(p_i ** k) == 1``.
  Removes more vig from longshots than the multiplicative method does.
* ``shin`` — solves Shin's (1992) insider-trading model. Generally
  considered the most accurate for two-way markets.

A high-level :func:`devig` dispatch is also provided.
"""

from __future__ import annotations

from typing import List


def devig_multiplicative(implied: List[float]) -> List[float]:
    total = sum(implied)
    if total <= 0:
        raise ValueError("Implied probabilities must sum to > 0")
    return [p / total for p in implied]


def devig_power(implied: List[float], tol: float = 1e-9, max_iter: int = 100) -> List[float]:
    """Find k so that sum(p_i ** k) = 1 via bisection."""
    if any(p <= 0 or p >= 1 for p in implied):
        # Fall back to multiplicative for degenerate inputs.
        return devig_multiplicative(implied)

    lo, hi = 0.5, 5.0

    def s(k: float) -> float:
        return sum(p**k for p in implied)

    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        val = s(mid)
        if abs(val - 1.0) < tol:
            break
        if val > 1.0:
            lo = mid
        else:
            hi = mid
    k = (lo + hi) / 2.0
    return [p**k for p in implied]


def devig_shin(implied: List[float], tol: float = 1e-10, max_iter: int = 200) -> List[float]:
    """Shin's method (works best for two-way markets).

    Solves for ``z`` (proportion of insider trading) such that:
        sum_i sqrt(z^2 + 4 * (1 - z) * pi_i^2 / S) - 2 = z * (n - 2)
    where ``S = sum(pi)`` (the overround) and ``pi`` are book implied probs.
    """
    n = len(implied)
    S = sum(implied)
    if S <= 0:
        raise ValueError("Implied probabilities must sum to > 0")

    if n != 2:
        # Shin in closed form is for n=2; for larger n iterate.
        # Approximate via numeric solve of the same equation.
        lo, hi = 0.0, 0.5

        def f(z: float) -> float:
            return sum(
                ((z**2 + 4 * (1 - z) * (pi**2) / S) ** 0.5) for pi in implied
            ) - 2 - z * (n - 2)

        f_lo, f_hi = f(lo), f(hi)
        if f_lo * f_hi > 0:
            # Cannot bracket — fall back.
            return devig_power(implied)
        for _ in range(max_iter):
            mid = (lo + hi) / 2.0
            f_mid = f(mid)
            if abs(f_mid) < tol:
                break
            if f_lo * f_mid < 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid
        z = (lo + hi) / 2.0
    else:
        a, b = implied
        # Closed-form for two-way Shin:
        # z = ((S - 1) * (a^2 - b^2 + S) + ... ) — easier numerically.
        lo, hi = 0.0, 0.5

        def f2(z: float) -> float:
            return (
                ((z**2 + 4 * (1 - z) * a**2 / S) ** 0.5)
                + ((z**2 + 4 * (1 - z) * b**2 / S) ** 0.5)
                - 2
            )

        if f2(lo) * f2(hi) > 0:
            return devig_power(implied)
        for _ in range(max_iter):
            mid = (lo + hi) / 2.0
            v = f2(mid)
            if abs(v) < tol:
                break
            if f2(lo) * v < 0:
                hi = mid
            else:
                lo = mid
        z = (lo + hi) / 2.0

    fair = []
    for pi in implied:
        num = ((z**2 + 4 * (1 - z) * pi**2 / S) ** 0.5) - z
        fair.append(num / (2 * (1 - z)) if z < 1 else pi / S)
    total = sum(fair)
    return [p / total for p in fair]


def devig(implied: List[float], method: str = "shin") -> List[float]:
    method = method.lower()
    if method in {"mult", "multiplicative", "basic"}:
        return devig_multiplicative(implied)
    if method == "power":
        return devig_power(implied)
    if method == "shin":
        return devig_shin(implied)
    raise ValueError(f"Unknown devig method: {method}")
