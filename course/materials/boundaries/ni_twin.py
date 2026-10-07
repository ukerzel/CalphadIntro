"""Task 03: fit digitized Ni coherent-twin energy and count area/sites.

Fischer et al. (2019), Fig3, DOI 10.1016/j.actamat.2019.06.027.
Eight approximate samples of an integrated EAM formation-energy curve;
not measured data or independent observations. Geometry/bulk coupling are
teaching conventions. Published CuNi bulk TDB stays external and unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import time

import matplotlib.pyplot as plt
import numpy as np
import pycalphad
from pycalphad import Model

from course.materials.cuni.worked_example import COMPONENTS, SOURCE_SHA, evaluate, load_source

AVOGADRO = 6.02214076e23
LATTICE_PARAMETER_M = 0.352e-9  # Fixed teaching value, not source thermal expansion.
GRAIN_SIZE_M = 100e-9  # Equiaxed-cube teaching geometry.
AREA_TOL = 1e-8  # J/m², numerical recovery only.
ENERGY_TOL = 1e-7  # J on 1 mol Ni basis, or J/mol sites.
BALANCE_TOL = 1e-10
DATA_PATH = Path(__file__).with_name("ni_twin_curve.csv")


def fit_curve(temperatures, gamma):
    """Unweighted line fit with explicit fit-minus-reading residuals."""
    t, gamma = np.asarray(temperatures, dtype=float), np.asarray(gamma, dtype=float)
    if (t.ndim != 1 or gamma.shape != t.shape or len(t) < 2
            or not np.all(np.isfinite(t)) or not np.all(np.isfinite(gamma))
            or np.any(t <= 0) or np.any(gamma <= 0)):
        raise ValueError("Need finite positive temperatures/energies with matching shapes")
    design = np.column_stack((np.ones(len(t)), t))
    if np.linalg.matrix_rank(design) != 2:
        raise ValueError("Need distinct temperatures for an intercept and slope")
    a, b = np.linalg.lstsq(design, gamma, rcond=None)[0]
    predicted = a+b*t
    residual = predicted-gamma
    return {"A_J_per_m2": float(a), "B_J_per_m2_K": float(b),
            "predicted_J_per_m2": predicted, "residual_J_per_m2": residual,
            "sse_J2_per_m4": float(residual @ residual),
            "max_absolute_residual_J_per_m2": float(np.max(np.abs(residual)))}


def geometry(a, d):
    """Shared cube faces and two occupied {111} planes on a 1 mol Ni basis."""
    if not np.isfinite(a) or not np.isfinite(d) or a <= 0 or d <= 0:
        raise ValueError("Positive finite lattice parameter and grain size required")
    volume = AVOGADRO*a**3/4  # FCC, four real Ni atoms per unit cell.
    area = 3*volume/d  # Six cube faces, each shared by two grains.
    density = 2*4/(np.sqrt(3)*a*a)/AVOGADRO
    sites = density*area
    if not 0 < sites < 1:
        raise ValueError("Chosen two-plane convention exhausts the one-mole Ni inventory")
    return {"lattice_parameter_m": a, "grain_size_m": d,
            "molar_volume_m3_per_mol": volume, "area_m2_for_one_mol_NI": area,
            "site_density_mol_per_m2": density,
            "boundary_NI_mol": sites, "bulk_NI_mol": 1-sites}


def cell_energy(bulk_g, gamma, geom):
    """Prescribed boundary offset on the same real-Ni reference and amount basis."""
    epsilon = gamma/geom["site_density_mol_per_m2"]
    boundary_g = bulk_g+epsilon
    cell_g = geom["bulk_NI_mol"]*bulk_g+geom["boundary_NI_mol"]*boundary_g
    return {"bulk_g_J_per_mol_NI": bulk_g,
            "epsilon_J_per_mol_sites": epsilon,
            "boundary_g_J_per_mol_sites": boundary_g,
            "cell_G_J": cell_g, "excess_total_J": cell_g-bulk_g,
            "area_times_gamma_J": geom["area_m2_for_one_mol_NI"]*gamma}


def read_curve():
    with DATA_PATH.open() as handle:
        rows = list(csv.DictReader(handle))
    t = np.array([float(row["temperature_K"]) for row in rows])
    gamma = np.array([float(row["gamma_J_per_m2"]) for row in rows])
    if (not np.array_equal(t, np.arange(100., 801., 100.))
            or any(row["source_figure"] != "3" or row["source_printed_page"] != "224"
                   or float(row["reading_precision_J_per_m2"]) != 0.001 for row in rows)):
        raise ValueError("Expected the declared eight Fig3 curve readings and precision")
    return t, gamma


def run(source: Path, output: Path):
    started = time.monotonic()
    db = load_source(source)
    data_hash = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    t, gamma = read_curve()
    fitted = fit_curve(t, gamma)
    geom = geometry(LATTICE_PARAMETER_M, GRAIN_SIZE_M)
    if abs(geom["bulk_NI_mol"]+geom["boundary_NI_mol"]-1) > BALANCE_TOL:
        raise ValueError("Real Ni inventory balance failed")
    model = Model(db, COMPONENTS, "FCC_A1")
    rows = []
    for temperature in [300., 500., 800.]:
        # Never evaluate the external unary below its declared lower support.
        bulk_g = evaluate(model, model.GM, temperature, 1.0)
        gamma_fit = fitted["A_J_per_m2"]+fitted["B_J_per_m2_K"]*temperature
        energy = cell_energy(bulk_g, gamma_fit, geom)
        recovered = energy["epsilon_J_per_mol_sites"]*geom["site_density_mol_per_m2"]
        if abs(recovered-gamma_fit) > AREA_TOL:
            raise ValueError("Site-to-area energy recovery failed")
        if abs(energy["excess_total_J"]-energy["area_times_gamma_J"]) > ENERGY_TOL:
            raise ValueError("Total boundary excess energy failed")
        if abs(cell_energy(bulk_g, 0, geom)["cell_G_J"]-bulk_g) > ENERGY_TOL:
            raise ValueError("Empty-offset limit failed")
        rows.append({"T_K": temperature, "fitted_gamma_J_per_m2": gamma_fit,
                     "recovered_gamma_J_per_m2": recovered, **energy})
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("External source changed during run")
    if hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() != data_hash:
        raise ValueError("Curve excerpt changed during run")
    output.mkdir(parents=True, exist_ok=True)
    grid = np.linspace(100, 800, 101)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(t, gamma, label="Approximate Ni Sigma3 curve readings")
    axes[0].plot(grid, fitted["A_J_per_m2"]+fitted["B_J_per_m2_K"]*grid,
                 label="Linear teaching fit")
    axes[0].set(xlabel="Temperature (K)", ylabel="Formation energy (J/m²)",
                title="Fischer2019 Fig3; coherent {111} Ni twin")
    axes[0].legend(fontsize=8)
    axes[1].plot(t, fitted["residual_J_per_m2"]*1000, "o-")
    axes[1].axhline(0, color="gray", lw=0.8)
    axes[1].set(xlabel="Temperature (K)", ylabel="Fit minus reading (mJ/m²)",
                title="Residuals; readings have ±1 mJ/m² precision")
    fig.tight_layout()
    fig.savefig(output/"ni_twin.png", dpi=150)
    plt.close(fig)
    result = {"doi": "10.1016/j.actamat.2019.06.027", "figure": 3,
              "source_printed_page": 224, "source_pdf_page": 5,
              "supplied_paper_sha256": "eb3fe5b6c92f24ea9ea440132e0ab52e8082f03d14e789679284acaff90aaabd",
              "curve_csv_sha256": data_hash, "bulk_tdb_sha256": SOURCE_SHA,
              "python": platform.python_version(), "pycalphad": pycalphad.__version__,
              "input_role": "Rounded samples of blue Ni Sigma3 integrated formation-energy band midpoint, not independent observations",
              "temperature_K": t.tolist(), "gamma_read_J_per_m2": gamma.tolist(),
              "reading_precision_J_per_m2": 0.001,
              "fit": {k: val.tolist() if isinstance(val, np.ndarray) else val
                      for k, val in fitted.items()},
              "slope_entropy_like_coefficient_J_per_m2_K": -fitted["B_J_per_m2_K"],
              "geometry": geom, "energy_checks": rows,
              "bulk_pressure_Pa": 101325, "source_pressure": "no external pressure, source Eq7",
              "tolerances": {"area_energy_abs_J_per_m2": AREA_TOL,
                             "energy_abs_J_on_one_mol_basis": ENERGY_TOL,
                             "amount_balance_abs_mol": BALANCE_TOL},
              "limitations": "Digitized integrated EAM curve, no independent experimental fit/uncertainty inference. Fixed teaching area/sites and CALPHAD bulk copying assumed; no physical boundary assessment, exact entropy determination, transitions or extrapolation.",
              "elapsed_s": time.monotonic()-started}
    (output/"ni_twin_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"fit": result["fit"], "geometry": geom, "energy_checks": rows,
                      "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.tdb, args.output)
