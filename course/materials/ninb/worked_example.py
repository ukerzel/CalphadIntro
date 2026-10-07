"""Task 05: bounded Sun Nb-Ni demonstration in pycalphad 0.11.2.

External unchanged TDB required. See README.md for source, units and limits.
This script evaluates the published input; it does not validate its physics.
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
from pycalphad import Database, Model, equilibrium, variables as v

SOURCE_SHA = "ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a"
PHASES = ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3", "DELTA", "MU_PHASE", "NBNI8", "BCC_B2"]
COMPONENTS = ["NB", "NI", "VA"]
TEMPERATURES = np.linspace(300.0, 3000.0, 61)
COMPOSITIONS = np.linspace(0.005, 0.995, 51)
PRESSURE = 101325.0
ABS_ENERGY = 1e-8
REL_ENERGY = 1e-12
BALANCE_TOL = 1e-6
# Original hand arithmetic result, not an imported TDB expression.
HAND_DELTA_FORMULA = -122000.0201618562


def load_source(path: Path) -> Database:
    """Reject changed inputs and evaluator versions before constructing models."""
    if pycalphad.__version__ != "0.11.2":
        raise ValueError("Use pinned pycalphad 0.11.2")
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source SHA-256 mismatch; do not substitute another TDB")
    db = Database(str(path))
    if set(db.phases) != set(PHASES):
        raise ValueError("Expected all eight source phases")
    return db


def endmember(db: Database, phase: str, species: str) -> dict[str, float]:
    """Evaluate Model.G (formula expression) and GM (J/mol real atoms)."""
    model = Model(db, COMPONENTS, phase)
    substitutions = {v.T: 1000.0, v.P: PRESSURE, v.N: 1.0}
    substitutions.update({y: float(y.species.name == species) for y in model.site_fractions})
    return {"formula_J_per_mol": float(model.G.subs(substitutions)),
            "atom_J_per_mol": float(model.GM.subs(substitutions)),
            "magnetic_J_per_mol_atoms": float(model.models["mag"].subs(substitutions))}


def energy_checks(db: Database) -> dict:
    """One hand result, two amount conversions and finite pure endmembers."""
    delta = endmember(db, "DELTA", "NB")
    mu = endmember(db, "MU_PHASE", "NI")
    if delta["magnetic_J_per_mol_atoms"] != 0.0:
        raise ValueError("Chosen hand endmember must be nonmagnetic")
    if not np.isclose(delta["formula_J_per_mol"], HAND_DELTA_FORMULA,
                      atol=ABS_ENERGY, rtol=REL_ENERGY):
        raise ValueError("Delta hand check failed")
    for result, divisor in [(delta, 4), (mu, 13)]:
        if not np.isclose(result["atom_J_per_mol"], result["formula_J_per_mol"] / divisor,
                          atol=ABS_ENERGY, rtol=REL_ENERGY):
            raise ValueError("Formula-to-atom conversion failed")
    pure = {species: endmember(db, "LIQUID", species) for species in ["NB", "NI"]}
    if not all(np.isfinite(value) for result in pure.values() for value in result.values()):
        raise ValueError("Nonfinite pure endmember")
    return {"temperature_K": 1000, "delta_NB_NB_NB": delta, "mu_all_NI": mu,
            "hand_delta_formula_J_per_mol": HAND_DELTA_FORMULA,
            "hand_abs_difference_J_per_mol": abs(delta["formula_J_per_mol"] - HAND_DELTA_FORMULA),
            "pure_liquid_endmembers": pure}


def balance_checks(eq) -> dict:
    """Detect empty solutions, unconverged energies and component/amount errors."""
    amounts = eq.NP.values
    occupied = (eq.Phase.values != "") & np.isfinite(amounts)
    if np.any((eq.Phase.values != "") & ~np.isfinite(amounts)):
        raise ValueError("Nonfinite occupied phase amount")
    if np.any(amounts[occupied] < -BALANCE_TOL) or not np.all(np.isfinite(eq.GM.values)):
        raise ValueError("Invalid amount or equilibrium energy")
    weights = np.where(occupied, amounts, 0.0)
    total_error = float(np.max(np.abs(weights.sum(axis=-1) - 1.0)))
    errors = {}
    for component in ["NB", "NI"]:
        fractions = eq.X.sel(component=component).values
        if not np.all(np.isfinite(fractions[occupied])):
            raise ValueError("Nonfinite occupied composition")
        reconstructed = (weights * np.where(occupied, fractions, 0.0)).sum(axis=-1)
        target = eq.coords["X_NB"].values if component == "NB" else 1.0 - eq.coords["X_NB"].values
        errors[component] = float(np.max(np.abs(reconstructed - target)))
    if max(total_error, *errors.values()) > BALANCE_TOL:
        raise ValueError(f"Mass balance failed: {total_error}, {errors}")
    return {"max_amount_error": total_error, "max_component_error": errors}


def run(source: Path, output: Path) -> None:
    """Run the declared grid once; caller supplies timeout and memory bounds."""
    started = time.monotonic()
    db = load_source(source)
    checks = energy_checks(db)
    eq = equilibrium(db, COMPONENTS, PHASES,
                     {v.T: TEMPERATURES, v.X("NB"): COMPOSITIONS, v.P: PRESSURE, v.N: 1},
                     calc_opts={"pdens": 60})
    balances = balance_checks(eq)
    phases = eq.Phase.values
    fractions = eq.X.sel(component="NB").values
    temperatures = np.broadcast_to(TEMPERATURES[:, None, None], phases.shape[2:])
    temperatures = np.broadcast_to(temperatures, phases.shape)
    fig, ax = plt.subplots(figsize=(8, 6))
    observed = sorted(set(phases.ravel()) - {""})
    for phase in PHASES:
        mask = (phases == phase) & (eq.NP.values > 1e-8)
        if np.any(mask):
            ax.scatter(fractions[mask], temperatures[mask], s=5, label=phase)
    ax.set(xlabel="Mole fraction Nb (real atoms)", ylabel="Temperature (K)",
           xlim=(0, 1), ylim=(300, 3000), title="Sun input in pycalphad 0.11.2: sampled equilibrium phase compositions")
    ax.legend(markerscale=2, fontsize=8)
    fig.tight_layout()
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "phase_diagram.png", dpi=150)
    plt.close(fig)
    # Example amounts at the closest declared grid point to 1200 K, x_Nb=0.35.
    sample = eq.sel(T=1200, X_NB=0.35, method="nearest")
    rows = []
    for phase, amount, composition in zip(sample.Phase.values.ravel(), sample.NP.values.ravel(),
                                         sample.X.sel(component="NB").values.ravel()):
        if phase and np.isfinite(amount) and amount > 1e-8:
            rows.append({"phase": str(phase), "atom_mole_fraction": float(amount), "x_NB": float(composition)})
    result = {"source_sha256": SOURCE_SHA, "python": platform.python_version(),
              "pycalphad": pycalphad.__version__, "phases_requested": PHASES,
              "phases_observed": observed, "P_Pa": PRESSURE, "N_mol_atoms": 1,
              "T_K": TEMPERATURES.tolist(), "X_NB": COMPOSITIONS.tolist(), "pdens": 60,
              "comparison": "Sun manuscript Fig. 8(a), printed p.42, PDF p.44",
              "tolerances": {"energy_abs": ABS_ENERGY, "energy_rel": REL_ENERGY, "balance_abs": BALANCE_TOL},
              "energy_checks": checks, "balance_checks": balances,
              "sample": {"T_K": float(sample.T), "X_NB": float(sample.X_NB), "phases": rows},
              "near_pure_phase_sets": {str(x): sorted(set(eq.sel(X_NB=x).Phase.values[eq.sel(X_NB=x).NP.values > 1e-8]) - {""}) for x in [COMPOSITIONS[0], COMPOSITIONS[-1]]},
              "elapsed_s": time.monotonic() - started}
    (output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"balances": balances, "phases_observed": observed, "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.tdb, args.output)
