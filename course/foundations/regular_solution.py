"""Synthetic regular solution for the supplementary exercise lesson_01.md.

Never a material model.

Energy is J per mole of real atoms; temperature is K and x is mole fraction B.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# NIST 2022 CODATA, J mol^-1 K^-1, rounded for ordinary double precision.
R_GAS = 8.31446261815324


def _composition(x: float, *, interior: bool) -> None:
    """Reject non-finite and inadmissible mole fractions."""
    if not math.isfinite(x) or not (0 < x < 1 if interior else 0 <= x <= 1):
        domain = "0 < x < 1" if interior else "0 <= x <= 1"
        raise ValueError(f"x_B must be finite and satisfy {domain}")


@dataclass(frozen=True)
class BinaryRegularSolution:
    """One-mole synthetic binary model with constant pure energies and Omega."""

    temperature: float
    omega: float
    g_a0: float = 0.0
    g_b0: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.temperature) or self.temperature <= 0:
            raise ValueError("temperature must be positive and finite K")
        if not all(math.isfinite(value) for value in (self.omega, self.g_a0, self.g_b0)):
            raise ValueError("energies must be finite J/mol")

    def gibbs(self, x: float) -> float:
        """Return molar Gibbs energy, including continuous pure-state limits."""
        _composition(x, interior=False)
        ideal = 0.0 if x in (0, 1) else x * math.log(x) + (1 - x) * math.log1p(-x)
        return ((1 - x) * self.g_a0 + x * self.g_b0
                + R_GAS * self.temperature * ideal + self.omega * x * (1 - x))

    def slope(self, x: float) -> float:
        """Return the interior derivative dg/dx in J/mol."""
        _composition(x, interior=True)
        return (self.g_b0 - self.g_a0
                + R_GAS * self.temperature * (math.log(x) - math.log1p(-x))
                + self.omega * (1 - 2 * x))

    def curvature(self, x: float) -> float:
        """Return the interior second derivative d2g/dx2 in J/mol."""
        _composition(x, interior=True)
        return R_GAS * self.temperature / (x * (1 - x)) - 2 * self.omega

    def chemical_potentials(self, x: float) -> tuple[float, float]:
        """Return (mu_A, mu_B) for an interior binary composition, J/mol."""
        _composition(x, interior=True)
        energy, derivative = self.gibbs(x), self.slope(x)
        return energy - x * derivative, energy + (1 - x) * derivative

    @property
    def critical_temperature(self) -> float:
        """Return Omega/(2R); a positive miscibility-gap limit only for Omega>0."""
        return self.omega / (2 * R_GAS)

    def binodal(self) -> tuple[float, float]:
        """Return symmetric coexistence compositions below the critical point.

        Only this regular-solution model is supported. Bisection isolates the
        lower branch below its spinodal, avoiding the central stationary point.
        """
        if self.temperature >= self.critical_temperature:
            raise ValueError("no two-phase miscibility gap at this temperature")
        ratio = 2 * R_GAS * self.temperature / self.omega
        spinodal_left = ratio / (2 * (1 + math.sqrt(1 - ratio)))
        lower = math.nextafter(0.0, 1.0)
        upper = spinodal_left

        def mixing_slope(x: float) -> float:
            return (R_GAS * self.temperature * (math.log(x) - math.log1p(-x))
                    + self.omega * (1 - 2 * x))

        if not 0 < upper < 0.5 or mixing_slope(lower) >= 0 or mixing_slope(upper) <= 0:
            raise ValueError("coexistence branch is not representably bracketed")
        while True:
            midpoint = (lower + upper) / 2
            if midpoint == lower or midpoint == upper:
                break
            if mixing_slope(midpoint) < 0:
                lower = midpoint
            else:
                upper = midpoint
        left = (lower + upper) / 2
        return left, 1 - left


def lever_fraction(z: float, left: float, right: float) -> float:
    """Return high-composition phase fraction from the binary atom balance."""
    for value in (z, left, right):
        _composition(value, interior=False)
    if left >= right or not left <= z <= right:
        raise ValueError("require left < right and left <= z <= right")
    return (z - left) / (right - left)
