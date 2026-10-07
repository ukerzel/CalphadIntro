"""Two invented structural branches in the cell of the closed-cell contract.

See boundary_two_state_contract.md. A model branch crossing is not a real
interface-phase claim or a mixed-state equilibrium calculation.
"""

from typing import Any

import numpy as np
from scipy.optimize import brentq

from course.foundations.boundary_closed import closed_equilibrium
from course.foundations.boundary_one_state import AVOGADRO

BULK_SITES = 8000
BOUNDARY_SITES = 200
CELL_SITES = BULK_SITES+BOUNDARY_SITES
BRACKET = (0.10, 0.25)


def _initial(value: Any) -> float:
    try:
        array = np.asarray(value,dtype=float)
    except (TypeError,ValueError) as exc:
        raise ValueError("x_initial must be a finite scalar") from exc
    if array.ndim != 0 or not np.isfinite(array) or not 0.10 <= array <= 0.90:
        raise ValueError("x_initial must be a finite scalar in [0.10, 0.90]")
    return float(array)


def _baseline(value: Any) -> float:
    try:
        array = np.asarray(value,dtype=float)
    except (TypeError,ValueError) as exc:
        raise ValueError("eta_II must be one of 1900, 2000, 2100") from exc
    if array.ndim != 0 or not np.isfinite(array) or float(array) not in (1900,2000,2100):
        raise ValueError("eta_II must be one of 1900, 2000, 2100")
    return float(array)


def state_at(x_initial: Any, state: str, eta_II: Any = 2000) -> dict[str, float]:
    """Minimize one uniform state at one fixed B inventory and energy reference."""
    x0, eta2 = _initial(x_initial), _baseline(eta_II)
    if state not in ("I","II"):
        raise ValueError("state must be I or II")
    delta, eta = (-5000.0,0.0) if state == "I" else (-10000.0,eta2)
    out = closed_equilibrium(x0,delta,BULK_SITES)
    theta, xb = out["theta"], out["x_bulk"]
    total_b = BULK_SITES*x0+50
    if (not np.isfinite(theta) or not np.isfinite(xb)
            or not 0 <= theta <= 1 or not 0 <= xb <= 1
            or abs(BULK_SITES*xb+BOUNDARY_SITES*theta-total_b) > 1e-9
            or abs(out["total_B_atoms"]-total_b) > 1e-9):
        raise RuntimeError("state minimum violates common cell inventory")
    gm = out["G_molar_J_per_mol_sites"]+BOUNDARY_SITES*eta/CELL_SITES
    gj = out["G_cell_J"]+BOUNDARY_SITES*eta/AVOGADRO
    if not np.isfinite(gm) or not np.isfinite(gj):
        raise RuntimeError("state minimum has nonfinite energy")
    return {"theta": theta, "x_bulk": xb, "total_B_atoms": total_b,
            "G_molar_J_per_mol_sites": gm, "G_cell_J": gj,
            "gamma_B_mol_per_m2": out["gamma_B_mol_per_m2"],
            "preference_J_per_mol_sites": delta, "baseline_J_per_mol_sites": eta}


def compare_states(x_initial: Any, eta_II: Any = 2000) -> dict[str, Any]:
    """Compare separately minimized state energies at one closed inventory."""
    x0, eta2 = _initial(x_initial), _baseline(eta_II)
    first, second = state_at(x0,"I",eta2), state_at(x0,"II",eta2)
    return {"x_initial": x0, "eta_II": eta2, "I": first, "II": second,
            "difference_J_per_mol_sites": second["G_molar_J_per_mol_sites"]
                                          -first["G_molar_J_per_mol_sites"]}


def crossing(eta_II: Any = 2000) -> dict[str, Any]:
    """Bracket and check the uniform-state ordering switch in x_initial."""
    eta2 = _baseline(eta_II)

    def difference(x0: float) -> float:
        return float(compare_states(x0,eta2)["difference_J_per_mol_sites"])

    left, right = map(difference,BRACKET)
    if not np.isfinite(left) or not np.isfinite(right) or not left > 0 > right:
        raise RuntimeError("two-state crossing is not bracketed")
    x0, info = brentq(difference,*BRACKET,xtol=1e-12,rtol=1e-14,
                      full_output=True,disp=False)
    if (not info.converged or not np.isfinite(x0)
            or not BRACKET[0] < x0 < BRACKET[1] or info.iterations < 1):
        raise RuntimeError("two-state crossing root failed qualification")
    out = compare_states(x0,eta2)
    if (not np.isfinite(out["difference_J_per_mol_sites"])
            or abs(out["difference_J_per_mol_sites"]) > 1e-6):
        raise RuntimeError("two-state crossing residual is inconsistent")
    return {**out, "root_iterations": int(info.iterations),
            "root_converged": bool(info.converged)}
