"""Task 01: unchanged Hallstedt Cu-Ni input, with a magnetic-off illustration.

Pinned pycalphad 0.11.2. External TDB required; source/units/limits in README.
The curated paper coefficient CSV is reading context, not a replacement database.
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
from pycalphad import Database, Model, calculate, equilibrium, variables as v
from symengine import S

SOURCE_SHA = "7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1"
PHASES = ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3"]
COMPONENTS = ["CU", "NI", "VA"]
TEMPERATURES = np.linspace(300.0, 1900.0, 81)
COMPOSITIONS = np.linspace(0.005, 0.995, 61)
PRESSURE = 101325.0
ABS_ENERGY = 1e-8
REL_ENERGY = 1e-12
BALANCE_TOL = 1e-6
HAND_CU_LIQUID = -83457.60262034053


class MagneticOffModel(Model):
    """Demonstration variant: suppress only magnetic_energy during assembly."""
    def magnetic_energy(self, dbe):
        return S.Zero


def load_source(path: Path) -> Database:
    if pycalphad.__version__ != "0.11.2":
        raise ValueError("Use pinned pycalphad 0.11.2")
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source SHA-256 mismatch")
    db = Database(str(path))
    if set(db.phases) != set(PHASES):
        raise ValueError("Expected all four source phases")
    return db


def evaluate(model: Model, expression, temperature: float, x_ni: float) -> float:
    """At fixed vacancy sites VA=1; fractions on the metal site sum to one."""
    replacements = {v.T: temperature, v.P: PRESSURE, v.N: 1}
    replacements.update({y: (1.0 if y.species.name == "VA" else
                            x_ni if y.species.name == "NI" else 1 - x_ni)
                         for y in model.site_fractions})
    return float(expression.subs(replacements))


def energy_checks(db: Database) -> dict:
    liquid = Model(db, COMPONENTS, "LIQUID")
    hand_value = evaluate(liquid, liquid.GM, 1500, 0)
    if not np.isclose(hand_value, HAND_CU_LIQUID, atol=ABS_ENERGY, rtol=REL_ENERGY):
        raise ValueError("Pure Cu liquid hand check failed")
    full = Model(db, COMPONENTS, "FCC_A1")
    off = MagneticOffModel(db, COMPONENTS, "FCC_A1")
    errors = []
    for temperature in [500, 600, 800, 1600]:
        for x in [0.2, 0.5, 0.8, 1.0]:
            difference = evaluate(full, full.GM, temperature, x) - evaluate(off, off.GM, temperature, x)
            magnetic = evaluate(full, full.models["mag"], temperature, x)
            if not np.isclose(difference, magnetic, atol=ABS_ENERGY, rtol=REL_ENERGY):
                raise ValueError("Magnetic control difference failed")
            if not np.isclose(evaluate(full, full.G, temperature, x),
                              evaluate(full, full.GM, temperature, x), atol=ABS_ENERGY, rtol=REL_ENERGY):
                raise ValueError("FCC fixed vacancy normalization failed")
            errors.append(abs(difference - magnetic))
    pure = {species: evaluate(liquid, liquid.GM, 1500, x) for species, x in [("CU", 0), ("NI", 1)]}
    if not all(np.isfinite(g) for g in pure.values()):
        raise ValueError("Nonfinite pure energies")
    return {"hand_T_K": 1500, "hand_pure_Cu_liquid_J_per_mol_atoms": HAND_CU_LIQUID,
            "evaluator_pure_Cu_liquid_J_per_mol_atoms": hand_value,
            "hand_abs_difference": abs(hand_value - HAND_CU_LIQUID),
            "max_magnetic_control_abs_difference": max(errors), "pure_liquid_1500K_J_per_mol_atoms": pure}


def balance_checks(eq) -> dict:
    amounts = eq.NP.values
    occupied = eq.Phase.values != ""
    if not np.all(np.isfinite(amounts[occupied])) or not np.all(np.isfinite(eq.GM.values)):
        raise ValueError("Nonfinite equilibrium solution")
    if np.any(amounts[occupied] < -BALANCE_TOL):
        raise ValueError("Negative phase amount")
    weights = np.where(occupied, amounts, 0.0)
    amount_error = float(np.max(np.abs(weights.sum(axis=-1) - 1)))
    errors = {}
    for component in ["NI", "CU"]:
        fractions = eq.X.sel(component=component).values
        if not np.all(np.isfinite(fractions[occupied])):
            raise ValueError("Nonfinite phase composition")
        reconstructed = (weights * np.where(occupied, fractions, 0.0)).sum(axis=-1)
        target = eq.X_NI.values if component == "NI" else 1 - eq.X_NI.values
        errors[component] = float(np.max(np.abs(reconstructed - target)))
    if max(amount_error, *errors.values()) > BALANCE_TOL:
        raise ValueError("Amount/component balance failed")
    return {"max_amount_error": amount_error, "max_component_error": errors}


def phase_rows(sample) -> list[dict]:
    return [{"phase": str(p), "atom_mole_fraction": float(n), "x_NI": float(x)}
            for p, n, x in zip(sample.Phase.values.ravel(), sample.NP.values.ravel(),
                               sample.X.sel(component="NI").values.ravel())
            if p and np.isfinite(n) and n > 1e-8]


def run(source: Path, output: Path) -> None:
    started = time.monotonic()
    db = load_source(source)
    checks = energy_checks(db)
    output.mkdir(parents=True, exist_ok=True)
    conditions = {v.T: TEMPERATURES, v.X("NI"): COMPOSITIONS, v.P: PRESSURE, v.N: 1}
    solutions = {"magnetic_on": equilibrium(db, COMPONENTS, PHASES, conditions, calc_opts={"pdens": 60}),
                 "magnetic_off": equilibrium(db, COMPONENTS, PHASES, conditions, model=MagneticOffModel,
                                             calc_opts={"pdens": 60})}
    summaries = {}
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharex=True, sharey=True)
    for ax, (mode, eq) in zip(axes, solutions.items()):
        balances = balance_checks(eq)
        phases = eq.Phase.values
        positive = eq.NP.values > 1e-8
        ts = np.broadcast_to(TEMPERATURES[:, None, None], phases.shape[2:])
        ts = np.broadcast_to(ts, phases.shape)
        xs = eq.X.sel(component="NI").values
        for phase in PHASES:
            mask = (phases == phase) & positive
            if np.any(mask):
                ax.scatter(xs[mask], ts[mask], s=2, label=phase)
        ax.set(title=mode.replace("_", " "), xlabel="Mole fraction Ni", xlim=(0, 1), ylim=(300, 1900))
        ax.legend(fontsize=8, markerscale=3)
        two_fcc = (((phases == "FCC_A1") & positive).sum(axis=-1) >= 2).any(axis=-1).ravel()
        gap_ts = TEMPERATURES[two_fcc]
        samples = {}
        for target_t in [600, 1500, 1600]:
            sample = eq.sel(T=target_t, X_NI=0.5, method="nearest")
            samples[str(target_t)] = {"T_K": float(sample.T), "X_NI": float(sample.X_NI), "phases": phase_rows(sample)}
        spectrum = eq.sel(X_NI=0.5, method="nearest")
        active = spectrum.NP.values > 1e-8
        both = ((spectrum.Phase.values == "FCC_A1") & active).any(axis=-1) & ((spectrum.Phase.values == "LIQUID") & active).any(axis=-1)
        indices = np.flatnonzero(both.ravel())
        if not len(indices):
            raise ValueError("No sampled FCC/liquid example at x(Ni)=0.5")
        sample = eq.sel(T=TEMPERATURES[indices[0]], X_NI=0.5, method="nearest")
        samples["FCC_liquid_example"] = {"T_K": float(sample.T), "X_NI": float(sample.X_NI), "phases": phase_rows(sample)}
        summaries[mode] = {"balance_checks": balances,
                           "phases_observed": sorted(set(phases[positive]) - {""}),
                           "highest_sampled_T_with_two_FCC_K": float(gap_ts[-1]) if len(gap_ts) else None,
                           "samples": samples,
                           "near_pure_phase_sets": {str(x): sorted(set(eq.sel(X_NI=x).Phase.values[eq.sel(X_NI=x).NP.values > 1e-8]) - {""}) for x in [COMPOSITIONS[0], COMPOSITIONS[-1]]}}
    axes[0].set_ylabel("Temperature (K)")
    fig.suptitle("Hallstedt Cu-Ni input: sampled phase compositions (all four phases enabled)")
    fig.tight_layout()
    fig.savefig(output / "phase_diagram.png", dpi=150)
    plt.close(fig)
    xs = np.linspace(0, 1, 201)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, temperature in zip(axes[:2], [600, 1600]):
        for phase in ["FCC_A1", "LIQUID"]:
            for cls, style, label in [(Model, "-", "on"), (MagneticOffModel, "--", "off")]:
                points = np.array([[1-x, x, 1] if phase == "FCC_A1" else [1-x, x] for x in xs])
                data = calculate(db, COMPONENTS, phase, T=temperature, P=PRESSURE, points=points, model=cls)
                ax.plot(xs, data.GM.values.ravel(), style, label=f"{phase}, mag {label}")
        ax.set(title=f"{temperature} K", xlabel="Mole fraction Ni", ylabel="Gm (J/mol atoms)")
        ax.legend(fontsize=7)
    nickel = Model(db, COMPONENTS, "FCC_A1")
    ts = np.linspace(300, 1000, 101)
    axes[2].plot(ts, [evaluate(nickel, nickel.models["mag"], t, 1) for t in ts])
    axes[2].axvline(633, color="gray", linestyle=":", label="source Tc = 633 K")
    axes[2].set(title="Pure FCC Ni magnetic term", xlabel="Temperature (K)", ylabel="Gmag (J/mol atoms)")
    axes[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(output / "energy_magnetism.png", dpi=150)
    plt.close(fig)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source changed during run")
    result = {"source_sha256": SOURCE_SHA, "python": platform.python_version(), "pycalphad": pycalphad.__version__,
              "phases_requested": PHASES, "T_K": TEMPERATURES.tolist(), "X_NI": COMPOSITIONS.tolist(),
              "P_Pa": PRESSURE, "N_mol_atoms": 1, "pdens": 60,
              "tolerances": {"energy_abs": ABS_ENERGY, "energy_rel": REL_ENERGY, "balance_abs": BALANCE_TOL},
              "comparison": "Mey Fig.1 printed256/PDF2, Fig.7 printed259/PDF5",
              "energy_checks": checks, "equilibrium": summaries, "elapsed_s": time.monotonic()-started}
    (output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"energy_checks": checks, "equilibrium": summaries, "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.tdb, args.output)
