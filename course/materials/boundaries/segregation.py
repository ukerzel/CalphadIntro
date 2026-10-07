"""Task 04: illustrative boundary segregation coupled to published CuNi FCC.

One fixed occupied-site state at 1000 K. Boundary preference/capacity are
invented; neither a measured boundary nor a physical segregation assessment.
Run as a module; the unchanged published bulk TDB remains external.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time

import matplotlib.pyplot as plt
import numpy as np
import pycalphad
from pycalphad import Model, variables as v
from scipy.optimize import brentq
from symengine import Symbol

from course.materials.cuni.worked_example import COMPONENTS, SOURCE_SHA, load_source

TEMPERATURE = 1000.0
PRESSURE = 101325.0
R = float(v.R)
AVOGADRO = 6.02214076e23
PREFERENCE = 6000.0  # Invented Ni-minus-Cu site preference, J/mol sites.
BOUNDARY_FRACTION = 0.02  # Invented occupied-site amount, total basis 1 mol.
SITE_DENSITY = 10.0  # Invented occupied sites per nm², total boundary area.
FRACTION_TOL = 1e-10
EXCHANGE_TOL = 1e-6  # J/mol occupied sites.
EPS = 1e-9  # Avoid logarithmic pure endpoints; not a model regularization.


def make_bulk_model(db):
    """Full homogeneous FCC energy on the one-metal-atom/site basis.

The invented boundary copies this entire function, including magnetic terms,
then adds only its declared preference. No additional magnetic contribution.
"""
    model = Model(db, COMPONENTS, "FCC_A1")
    x = Symbol("x_Ni")
    replacements = {v.T: TEMPERATURE, v.P: PRESSURE, v.N: 1}
    replacements.update({y: (1 if y.species.name == "VA" else
                             x if y.species.name == "NI" else 1-x)
                         for y in model.site_fractions})
    g = model.GM.subs(replacements)
    def evaluate(expression):
        return lambda z: float(expression.subs({x: float(z)}))
    return {"g": evaluate(g), "dg": evaluate(g.diff(x)),
            "d2g": evaluate(g.diff(x, 2))}


def check_inputs(composition, delta):
    if (not np.isfinite(composition) or not EPS < composition < 1-EPS
            or not np.isfinite(delta)):
        raise ValueError("Need finite interior composition and finite preference")


def open_occupancy(bulk, x, delta):
    """Solve g_s'(y)=mu_Ni-mu_Cu=g_b'(x) at fixed reservoir x."""
    check_inputs(x, delta)
    exchange = bulk["dg"](x)
    return brentq(lambda y: bulk["dg"](y)+delta-exchange,
                  EPS, 1-EPS, xtol=1e-14, rtol=1e-14)


def closed_occupancy(bulk, z, f, delta):
    """Conserve both species: z=(1-f)x+fy; return final bulk x and sites y."""
    check_inputs(z, delta)
    if not np.isfinite(f) or not 0 < f < 1:
        raise ValueError("Boundary occupied-site fraction must lie between zero and one")
    # Intersection of valid bulk and boundary interior compositions. In a
    # solute-limited cell the boundary cannot acquire more Ni than is present.
    low = max(EPS, (z-(1-f)*(1-EPS))/f)
    high = min(1-EPS, (z-(1-f)*EPS)/f)
    if low >= high:
        raise ValueError("No feasible interior occupied-site allocation")
    def exchange(y):
        x = (z-f*y)/(1-f)
        return bulk["dg"](y)+delta-bulk["dg"](x)
    y = brentq(exchange, low, high, xtol=1e-14, rtol=1e-14)
    return (z-f*y)/(1-f), y


def cu_excess(x, y, density):
    """Equal occupied-site Cu excess, not an arbitrary Gibbsian dividing surface."""
    atoms = density*(x-y)  # Cu: (1-y)-(1-x), the opposite sign to Ni.
    return {"atoms_per_nm2": atoms, "mol_per_m2": atoms*1e18/AVOGADRO}


def run(source: Path, output: Path):
    started = time.monotonic()
    bulk = make_bulk_model(load_source(source))
    compositions = np.linspace(0.01, 0.99, 101)
    curvatures = [bulk["d2g"](x) for x in compositions]
    if not np.all(np.isfinite(curvatures)) or min(curvatures) <= 0:
        raise ValueError("Declared homogeneous branch fails the sampled convexity screen")
    occupancies = np.array([open_occupancy(bulk, x, PREFERENCE) for x in compositions])
    residuals = [abs(bulk["dg"](y)+PREFERENCE-bulk["dg"](x))
                 for x, y in zip(compositions, occupancies)]
    rows = []
    zero_errors = []
    for z in [0.2, 0.5, 0.8]:
        opened = open_occupancy(bulk, z, PREFERENCE)
        x, y = closed_occupancy(bulk, z, BOUNDARY_FRACTION, PREFERENCE)
        ni = (1-BOUNDARY_FRACTION)*x+BOUNDARY_FRACTION*y
        cu = (1-BOUNDARY_FRACTION)*(1-x)+BOUNDARY_FRACTION*(1-y)
        residuals.append(abs(bulk["dg"](y)+PREFERENCE-bulk["dg"](x)))
        if abs(ni-z) > FRACTION_TOL or abs(cu-(1-z)) > FRACTION_TOL:
            raise ValueError("Closed Ni/Cu inventory balance failed")
        if not y < x or not x > z or not y > opened:
            raise ValueError("Expected illustrative Cu-enrichment/finite-inventory sign failed")
        zero_x, zero_y = closed_occupancy(bulk, z, BOUNDARY_FRACTION, 0)
        zero_errors += [abs(open_occupancy(bulk, z, 0)-z), abs(zero_x-z), abs(zero_y-z)]
        exchange = bulk["dg"](z)
        open_phi = bulk["g"](opened)+PREFERENCE*opened-bulk["g"](z)-(opened-z)*exchange
        closed_g = ((1-BOUNDARY_FRACTION)*bulk["g"](x)
                    + BOUNDARY_FRACTION*(bulk["g"](y)+PREFERENCE*y))
        rows.append({"overall_or_open_reservoir_x_NI": z,
                     "open_y_NI": opened, "closed_bulk_x_NI": x, "closed_y_NI": y,
                     "closed_total_NI_mol": ni, "closed_total_CU_mol": cu,
                     "open_CU_excess": cu_excess(z, opened, SITE_DENSITY),
                     "closed_CU_excess": cu_excess(x, y, SITE_DENSITY),
                     "open_phi_J_per_mol_boundary_sites": open_phi,
                     "closed_g_J_per_mol_all_sites": closed_g})
    if max(residuals) > EXCHANGE_TOL or max(zero_errors) > FRACTION_TOL:
        raise ValueError("Exchange or zero-preference limit check failed")
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source TDB changed during run")
    output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(compositions, 1-occupancies, label="Open boundary")
    axes[0].plot(compositions, 1-compositions, "--", label="Reservoir Cu fraction")
    axes[0].scatter([row["overall_or_open_reservoir_x_NI"] for row in rows],
                    [1-row["closed_y_NI"] for row in rows], color="black",
                    label="Closed boundary; x-axis = overall Ni")
    axes[0].set(xlabel="Reservoir Ni (open) / overall Ni (closed)",
                ylabel="Cu fraction", title="Illustrative boundary, published FCC bulk")
    axes[0].legend(fontsize=8)
    axes[1].plot(compositions, SITE_DENSITY*(compositions-occupancies), label="Open")
    axes[1].scatter([row["overall_or_open_reservoir_x_NI"] for row in rows],
                    [row["closed_CU_excess"]["atoms_per_nm2"] for row in rows],
                    color="black", label="Closed; excess uses final bulk fraction")
    axes[1].set(xlabel="Reservoir Ni (open) / overall Ni (closed)",
                ylabel="Equal-site Cu excess (atoms/nm²)", title="1000 K; invented 10 sites/nm²")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output/"segregation.png", dpi=150)
    plt.close(fig)
    result = {"source_sha256": SOURCE_SHA, "python": platform.python_version(),
              "pycalphad": pycalphad.__version__, "T_K": TEMPERATURE, "P_Pa": PRESSURE,
              "bulk_phase": "homogeneous FCC_A1, conditionally restricted",
              "basis": "one atom per occupied site; total closed cell 1 mol sites",
              "invented_boundary": {"function": "g_s(y_NI)=g_bulk(y_NI)+delta*y_NI",
                                    "delta_J_per_mol_sites": PREFERENCE,
                                    "boundary_site_fraction": BOUNDARY_FRACTION,
                                    "sites_per_nm2": SITE_DENSITY},
              "magnetic_assumption": "Entire bulk function copied once into invented boundary",
              "rows": rows,
              "checks": {"max_exchange_abs_J_per_mol_sites": max(residuals),
                         "max_zero_preference_fraction_error": max(zero_errors),
                         "min_sampled_bulk_curvature_J_per_mol": min(curvatures),
                         "hand_excess_CU_atoms_per_nm2_at_x05_y03": cu_excess(0.5, 0.3, 10)["atoms_per_nm2"]},
              "tolerances": {"fraction_balance_abs": FRACTION_TOL,
                             "exchange_abs_J_per_mol_sites": EXCHANGE_TOL},
              "limitations": "Invented one-state boundary; no physical boundary fit, absolute boundary energy, transition, full phase equilibrium or global certification. Convexity screen sampled only.",
              "elapsed_s": time.monotonic()-started}
    (output/"segregation_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"rows": rows, "checks": result["checks"], "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.tdb, args.output)
