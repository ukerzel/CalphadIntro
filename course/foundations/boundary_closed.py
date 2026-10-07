"""Closed-cell (fixed-inventory) version of the one-state boundary-site model.

See boundary_closed_contract.md for geometry, energy reference and domain.
"""

from typing import Any

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from course.foundations.binary_family import R, ideal_properties
from course.foundations.boundary_one_state import AVOGADRO, AREA_PER_BOUNDARY_M2

TEMPERATURE = 1000.0
BOUNDARY_SITES = 200.0  # two equivalent 100-site boundaries
SITES_PER_BOUNDARY = 100.0
SIZES = (8000, 80000, 800000)


def _scalar(value: Any, name: str, lower: float, upper: float) -> float:
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite scalar") from exc
    if array.ndim != 0 or not np.isfinite(array) or not lower <= array <= upper:
        raise ValueError(f"{name} must be a finite scalar in [{lower}, {upper}]")
    return float(array)


def _bulk_sites(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value not in SIZES:
        raise ValueError("bulk_sites must be one of 8000, 80000, 800000")
    return int(value)


def _bulk_fraction(theta: float, total_b: float, bulk_sites: int) -> float:
    xb = (total_b-BOUNDARY_SITES*theta)/bulk_sites
    if not 0 <= xb <= 1:
        raise ValueError("trial violates fixed B inventory or bulk capacity")
    return xb


def closed_trial(theta: Any, total_b: Any, preference: Any,
                 bulk_sites: Any = 8000) -> dict[str, float]:
    """Return constrained total energy at one feasible trial occupancy.

    ``G_molar`` is per mole of all occupied cell sites; ``G_cell`` is joules
    for this finite cell. Neither is an open-system grand potential.
    """
    nb = _bulk_sites(bulk_sites)
    y = _scalar(theta, "theta", 0.0, 1.0)
    b = _scalar(total_b, "total_b", 0.0, nb+BOUNDARY_SITES)
    delta = _scalar(preference, "preference", -10000.0, 10000.0)
    xb = _bulk_fraction(y, b, nb)
    gb = float(ideal_properties(TEMPERATURE, xb, "ALPHA")["GM"])
    gs = float(ideal_properties(TEMPERATURE, y, "ALPHA")["GM"]) + delta*y
    numerator = nb*gb+BOUNDARY_SITES*gs
    return {"x_bulk": xb, "G_molar_J_per_mol_sites": numerator/(nb+BOUNDARY_SITES),
            "G_cell_J": numerator/AVOGADRO}


def closed_equilibrium(x_initial: Any, preference: Any,
                       bulk_sites: Any = 8000) -> dict[str, float | int | bool]:
    """Cross-check a bounded total-energy minimum with the exchange root."""
    nb = _bulk_sites(bulk_sites)
    x0 = _scalar(x_initial, "x_initial", 0.10, 0.90)
    delta = _scalar(preference, "preference", -10000.0, 10000.0)
    total_b = nb*x0+BOUNDARY_SITES*0.25
    rt = R*TEMPERATURE

    def residual(theta: float) -> float:
        xb = _bulk_fraction(theta,total_b,nb)
        return float(delta+rt*(np.log(theta)-np.log1p(-theta)
                               -np.log(xb)+np.log1p(-xb)))

    theta_root, root_info = brentq(residual,1e-12,1-1e-12,
                                   xtol=1e-13,rtol=1e-14,
                                   full_output=True,disp=False)
    if (not root_info.converged or not np.isfinite(theta_root)
            or not 0 < theta_root < 1 or root_info.iterations < 1
            or abs(residual(theta_root)) > 1e-6):
        raise RuntimeError("closed exchange root failed qualification")
    result = minimize_scalar(
        lambda theta: closed_trial(theta,total_b,delta,nb)["G_molar_J_per_mol_sites"],
        bounds=(0.0,1.0),method="bounded",options={"xatol":1e-12},
    )
    if not result.success:
        raise RuntimeError(f"closed total-energy minimization failed: {result.message}")
    if not np.isscalar(result.x) or not np.isscalar(result.fun):
        raise RuntimeError("closed minimization returned malformed output")
    try:
        theta, gm, nfev = float(result.x), float(result.fun), int(result.nfev)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("closed minimization returned malformed output") from exc
    if (not np.isfinite(theta) or not 0 <= theta <= 1 or not np.isfinite(gm)
            or nfev < 1 or abs(theta-theta_root) > 2e-6):
        raise RuntimeError("closed minimization returned an invalid state")
    trial = closed_trial(theta,total_b,delta,nb)
    root_trial = closed_trial(theta_root,total_b,delta,nb)
    if (abs(gm-trial["G_molar_J_per_mol_sites"]) > 1e-8
            or abs(gm-root_trial["G_molar_J_per_mol_sites"]) > 1e-6):
        raise RuntimeError("closed minimization returned an inconsistent energy")
    xb = trial["x_bulk"]
    gamma = SITES_PER_BOUNDARY*(theta-xb)/(AREA_PER_BOUNDARY_M2*AVOGADRO)
    return {"theta": theta, "theta_root": float(theta_root), "x_bulk": xb,
            "total_B_atoms": total_b, "G_molar_J_per_mol_sites": gm,
            "G_cell_J": trial["G_cell_J"], "gamma_B_mol_per_m2": gamma,
            "nfev": nfev, "solver_success": bool(result.success),
            "root_iterations": int(root_info.iterations),
            "root_converged": bool(root_info.converged)}
