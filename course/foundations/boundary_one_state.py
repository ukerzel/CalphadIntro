"""Synthetic one-state boundary in a fixed binary-family I1 open reservoir.

The physical and numerical domain is fixed in boundary_one_state_contract.md.
Potentials are per mole of boundary sites; excesses are per boundary area.
"""

from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import expit

from course.foundations.binary_family import R, ideal_derivatives, ideal_properties

TEMPERATURE = 1000.0  # K; fixed hydrostatic state of the boundary geometry contract
SITES_PER_BOUNDARY = 100.0
AREA_PER_BOUNDARY_M2 = 20e-18
AVOGADRO = 6.02214076e23  # exact SI defining constant, mol^-1


def _scalar(value: Any, name: str, lower: float, upper: float) -> float:
    """Require one finite scalar in the declared closed interval; never clip."""
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite scalar") from exc
    if array.ndim != 0 or not np.isfinite(array) or not lower <= array <= upper:
        raise ValueError(f"{name} must be a finite scalar in [{lower}, {upper}]")
    return float(array)


def _inputs(x_bulk: Any, preference: Any) -> tuple[float, float]:
    return (_scalar(x_bulk, "x_bulk", 0.01, 0.99),
            _scalar(preference, "preference", -10000.0, 10000.0))


def grand_potential(theta: Any, x_bulk: Any, preference: Any) -> float:
    """Full boundary-site Gibbs energy minus both binary-family bulk reservoir terms."""
    occupancy = _scalar(theta, "theta", 0.0, 1.0)
    x, delta = _inputs(x_bulk, preference)
    g_site = float(ideal_properties(TEMPERATURE, occupancy, "ALPHA")["GM"])
    bulk = ideal_derivatives(TEMPERATURE, x, "ALPHA")
    mu_a, mu_b = float(bulk["mu_A"]), float(bulk["mu_B"])
    return g_site + delta * occupancy - (1-occupancy)*mu_a - occupancy*mu_b


def open_equilibrium(x_bulk: Any, preference: Any) -> dict[str, float | int | bool]:
    """Check direct bounded minimization against the independent logit solution."""
    x, delta = _inputs(x_bulk, preference)
    rt = R * TEMPERATURE
    theta_analytic = float(expit(np.log(x)-np.log1p(-x)-delta/rt))
    phi_analytic = float(-rt*np.log1p(x*np.expm1(-delta/rt)))
    result = minimize_scalar(
        grand_potential, args=(x, delta), bounds=(0.0, 1.0), method="bounded",
        options={"xatol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"boundary minimization failed: {result.message}")
    if not np.isscalar(result.x) or not np.isscalar(result.fun):
        raise RuntimeError("boundary minimization returned malformed output")
    try:
        theta, phi, nfev = float(result.x), float(result.fun), int(result.nfev)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("boundary minimization returned malformed output") from exc
    if (not np.isfinite(theta) or not 0 <= theta <= 1
            or not np.isfinite(phi) or nfev < 1
            or abs(theta-theta_analytic) > 2e-6):
        raise RuntimeError("boundary minimization returned an invalid state")
    fresh_phi = grand_potential(theta, x, delta)
    if abs(phi-fresh_phi) > 1e-8 or abs(phi-phi_analytic) > 1e-6:
        raise RuntimeError("boundary minimization returned an inconsistent potential")
    gamma = SITES_PER_BOUNDARY*(theta-x)/(AREA_PER_BOUNDARY_M2*AVOGADRO)
    return {"theta": theta, "theta_analytic": theta_analytic,
            "phi_J_per_mol_sites": phi, "gamma_B_mol_per_m2": gamma,
            "nfev": nfev, "solver_success": bool(result.success)}
