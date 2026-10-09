"""Gap curves and driving forces from the published Cu-Ni database (Task 06).

Pinned pycalphad 0.11.2 and the unchanged CuNi-92Mey-LB.tdb (checked by
worked_example.load_source). Writes gap_curve.json, the saved numbers that the
notebook task01b_cuni_gap_curve reads in no-database mode. Only computed numbers
are saved, never database text.

Conditions: phases FCC_A1 and LIQUID only, components CU, NI, VA, 101325 Pa,
one mole of atoms; 600 K (inside the FCC miscibility gap) and 650 K (above it);
overall x(Ni) = 0.5.

What is computed, and how:
- equilibrium() at both temperatures (pdens 60): phases, NP, X(Ni), MU, GM;
- calculate() on an even grid of 1001 compositions for both phases and both
  temperatures (the curves the notebook works with);
- "derived" numbers by a second route: pycalphad's symbolic Model.GM evaluated
  with symengine, analytic first and second derivatives in x, and continuous
  minimisation (scipy minimize_scalar, brentq). The notebook finds the same
  numbers with finite differences and grid minima and compares.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pycalphad
import scipy
import symengine as se
from pycalphad import Model, calculate, equilibrium, variables as v
from scipy.optimize import brentq, linprog, minimize_scalar

from course.materials.cuni import worked_example as cuni

PHASES = ["FCC_A1", "LIQUID"]
COMPONENTS = cuni.COMPONENTS          # CU, NI, VA
PRESSURE = cuni.PRESSURE              # Pa
PDENS = 60
Z = 0.5                               # overall x(Ni)
TEMPERATURES = (600.0, 650.0)         # K
X_GRID = np.linspace(0.0, 1.0, 1001)  # even grid, step 0.001
H = 1e-3                              # finite-difference step the notebook uses (one grid step)
MENU_X = [0.1, 0.3, 0.7, 0.9]         # the coarse menu, both phases at each x
OUTPUT = Path(__file__).with_name("gap_curve.json")


def points(phase: str, x) -> np.ndarray:
    """Site-fraction rows for calculate(): FCC_A1 (y_Cu, y_Ni, y_Va = 1), LIQUID (x_Cu, x_Ni)."""
    x = np.atleast_1d(np.asarray(x, dtype=float))
    return np.column_stack([1 - x, x, np.ones_like(x)] if phase == "FCC_A1" else [1 - x, x])


def gm_calculate(db, phase: str, x, T: float) -> np.ndarray:
    return calculate(db, COMPONENTS, phase, T=T, P=PRESSURE, N=1, points=points(phase, x)).GM.values.ravel()


def equilibrium_point(db, T: float) -> dict:
    eq = equilibrium(db, COMPONENTS, PHASES, {v.T: T, v.X("NI"): Z, v.P: PRESSURE, v.N: 1},
                     calc_opts={"pdens": PDENS})
    rows = [(str(p), float(n), float(x)) for p, n, x in
            zip(eq.Phase.values.squeeze(), eq.NP.values.squeeze(), eq.X.sel(component="NI").values.squeeze())
            if p and n > 1e-8]
    rows.sort(key=lambda row: row[2])
    mu = eq.MU.values.squeeze()
    out = {"GM": float(eq.GM.values.squeeze()), "MU": {"CU": float(mu[0]), "NI": float(mu[1])},
           "vertices": [{"phase": p, "NP": n, "x_NI": x, "GM_phase": float(gm_calculate(db, p, x, T)[0])}
                        for p, n, x in rows]}
    balance = {"NP_sum": sum(n for _, n, _ in rows), "Ni": sum(n * x for _, n, x in rows),
               "Cu": sum(n * (1 - x) for _, n, x in rows)}
    if abs(balance["NP_sum"] - 1) > 1e-6 or abs(balance["Ni"] - Z) > 1e-6 or abs(balance["Cu"] - (1 - Z)) > 1e-6:
        raise ValueError(f"balance failed at {T} K: {balance}")
    line_at_z = out["MU"]["CU"] * (1 - Z) + out["MU"]["NI"] * Z
    if abs(line_at_z - out["GM"]) > 1e-6:
        raise ValueError(f"the line at z is not GM at {T} K")
    return out


class Symbolic:
    """GM(x) of one phase at fixed T from pycalphad's symbolic model, with analytic derivatives in x."""

    def __init__(self, db, phase: str, T):
        model = Model(db, COMPONENTS, phase)
        self.x = se.Symbol("x")
        values = {}
        for y in model.site_fractions:
            values[y] = 1.0 if y.species.name == "VA" else (self.x if y.species.name == "NI" else 1 - self.x)
        values.update({v.P: PRESSURE, v.N: 1})
        if T is not None:
            values[v.T] = T
        self.g0 = se.sympify(model.GM).subs(values)
        self.g1 = se.diff(self.g0, self.x)
        self.g2 = se.diff(self.g1, self.x)

    def g(self, x):
        return float(self.g0.subs({self.x: x}))

    def slope(self, x):
        return float(self.g1.subs({self.x: x}))

    def curvature(self, x):
        return float(self.g2.subs({self.x: x}))


def deepest(f, lo: float, hi: float, grid: int = 400) -> tuple[float, float]:
    """Global minimum of a smooth 1-D function on [lo, hi]: coarse scan, then bounded refinement."""
    xs = np.linspace(lo, hi, grid + 1)
    values = [f(x) for x in xs]
    i = int(np.argmin(values))
    a, b = xs[max(i - 1, 0)], xs[min(i + 1, grid)]
    r = minimize_scalar(f, bounds=(a, b), method="bounded", options={"xatol": 1e-11})
    return (float(r.x), float(r.fun)) if r.fun <= values[i] else (float(xs[i]), float(values[i]))


def menu_lp(states: list[tuple[str, float, float]]) -> dict:
    """Cheapest mixture of listed states (phase, x, g) at overall x = Z; the line from the duals."""
    c = [g for _, _, g in states]
    a_eq = [[1.0] * len(states), [x for _, x, _ in states]]
    r = linprog(c, A_eq=a_eq, b_eq=[1.0, Z], bounds=(0, None), method="highs-ds")
    if r.status != 0:
        raise ValueError(r.message)
    mu_a, d_mu = (float(m) for m in r.eqlin.marginals)
    return {"ceiling": float(r.fun), "mu_A": mu_a, "d_mu": d_mu,
            "used": [{"phase": p, "x": x, "f": float(f)} for (p, x, _), f in zip(states, r.x) if f > 1e-12]}


def compute(db) -> dict:
    curves = {f"{T:.0f}": {phase: gm_calculate(db, phase, X_GRID, T) for phase in PHASES} for T in TEMPERATURES}
    eqs = {f"{T:.0f}": equilibrium_point(db, T) for T in TEMPERATURES}
    fcc, liquid = Symbolic(db, "FCC_A1", 600.0), Symbolic(db, "LIQUID", 600.0)

    # second route agrees with calculate() on the grid (interior and ends)
    probe = X_GRID[::50]
    route = max(abs(sym.g(x) - g) for sym, phase in ((fcc, "FCC_A1"), (liquid, "LIQUID"))
                for x, g in zip(probe, curves["600"][phase][::50]))
    if route > 1e-6:
        raise ValueError(f"symbolic and calculate() GM differ by {route} J/mol")

    e600 = eqs["600"]
    mu_a, d_mu = e600["MU"]["CU"], e600["MU"]["NI"] - e600["MU"]["CU"]
    line = lambda x: mu_a + d_mu * x  # noqa: E731
    vertex_gaps = [vx["GM_phase"] - line(vx["x_NI"]) for vx in e600["vertices"]]
    liquid_low = deepest(lambda x: liquid.g(x) - line(x), 1e-6, 1 - 1e-6)
    fcc_low = deepest(lambda x: fcc.g(x) - line(x), 1e-6, 1 - 1e-6)

    # homogeneous FCC at x = 0.5 and its tangent
    g_h, s_h, c_h = fcc.g(Z), fcc.slope(Z), fcc.curvature(Z)
    t_mu_a, t_d_mu = g_h - Z * s_h, s_h
    tangent_gap = lambda x: fcc.g(x) - (t_mu_a + t_d_mu * x)  # noqa: E731
    dip_x, dip = deepest(tangent_gap, 1e-6, 1 - 1e-6)
    scan = np.linspace(0.05, 0.95, 181)
    curv = np.array([fcc.curvature(x) for x in scan])
    spinodal = [float(brentq(fcc.curvature, scan[i], scan[i + 1], xtol=1e-12))
                for i in np.flatnonzero(np.diff(np.sign(curv)))]

    # the coarse menu, its line, the deepest dip of both continuous curves, the floor
    states = [(phase, float(x), float(sym.g(x))) for phase, sym in (("FCC_A1", fcc), ("LIQUID", liquid))
              for x in MENU_X]
    master = menu_lp(states)
    menu_line = lambda x: master["mu_A"] + master["d_mu"] * x  # noqa: E731
    dips = {phase: deepest(lambda x, s=sym: s.g(x) - menu_line(x), 1e-6, 1 - 1e-6)
            for phase, sym in (("FCC_A1", fcc), ("LIQUID", liquid))}
    menu_dip = min(d for _, d in dips.values())
    with_half = menu_lp(states + [("FCC_A1", Z, g_h)])

    # 650 K: tangent at the single FCC state, and the top of the gap from the curvature
    fcc650 = Symbolic(db, "FCC_A1", 650.0)
    e650 = eqs["650"]
    line650 = lambda x: e650["MU"]["CU"] + (e650["MU"]["NI"] - e650["MU"]["CU"]) * x  # noqa: E731
    low650 = deepest(lambda x: fcc650.g(x) - line650(x), 1e-6, 1 - 1e-6)
    fcc_t = Symbolic(db, "FCC_A1", None)

    def lowest_curvature(T):
        expression = fcc_t.g2.subs({v.T: T})
        r = minimize_scalar(lambda x: float(expression.subs({fcc_t.x: x})), bounds=(0.3, 0.95),
                            method="bounded", options={"xatol": 1e-10})
        return float(r.fun)
    critical_T = float(brentq(lowest_curvature, 600.0, 700.0, xtol=1e-6))

    derived = {
        "symbolic_vs_calculate_max_abs_J_per_mol": route,
        "eq_line_600": {"mu_A": mu_a, "d_mu": d_mu, "vertex_gaps": vertex_gaps,
                        "fcc_lowest_gap": {"x": fcc_low[0], "gap": fcc_low[1]},
                        "liquid_lowest_gap": {"x": liquid_low[0], "gap": liquid_low[1]},
                        "liquid_gap_at_half": liquid.g(Z) - line(Z)},
        "homogeneous_start_600": {"x": Z, "GM": g_h, "slope_d_mu": s_h, "curvature": c_h,
                                  "mu_CU": t_mu_a, "mu_NI": t_mu_a + t_d_mu,
                                  "deepest_dip": {"x": dip_x, "gap": dip},
                                  "driving_force": -dip,
                                  "full_split_gain": g_h - e600["GM"],
                                  "spinodal_x": spinodal},
        "menu_600": {"menu_x": MENU_X, **master,
                     "deepest_dip": {p: {"x": x, "gap": d} for p, (x, d) in dips.items()},
                     "floor": master["ceiling"] + min(0.0, menu_dip),
                     "remaining_uncertainty": -min(0.0, menu_dip),
                     "with_x_half": {"ceiling": with_half["ceiling"], "used": with_half["used"]}},
        "high_650": {"fcc_lowest_gap": {"x": low650[0], "gap": low650[1]},
                     "lowest_curvature": deepest(fcc650.curvature, 0.05, 0.95)[1]},
        "gap_top_K": critical_T,
    }
    return {"conditions": {"phases": PHASES, "components": COMPONENTS, "P_Pa": PRESSURE, "N_mol_atoms": 1,
                           "x_NI_overall": Z, "T_K": list(TEMPERATURES), "pdens": PDENS,
                           "x_grid": {"start": 0.0, "stop": 1.0, "num": len(X_GRID)}, "fd_step": H,
                           "units": "GM, MU, gaps in J/mol of atoms; x is the mole fraction of Ni"},
            "equilibrium": eqs,
            "curves": {T: {p: [round(float(g), 9) for g in c] for p, c in by_phase.items()}
                       for T, by_phase in curves.items()},
            "derived": derived}


def run(source: Path, output: Path) -> dict:
    db = cuni.load_source(source)  # pinned version and SHA-256
    result = {"source_sha256": cuni.SOURCE_SHA, "python": platform.python_version(),
              "pycalphad": pycalphad.__version__, "scipy": scipy.__version__, **compute(db)}
    if hashlib.sha256(source.read_bytes()).hexdigest() != cuni.SOURCE_SHA:
        raise ValueError("Source changed during run")
    output.write_text(json.dumps(result, indent=1, allow_nan=False) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    d = run(args.tdb, args.output)["derived"]
    print(json.dumps(d, indent=1))
