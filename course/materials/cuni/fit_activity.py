"""Task 02: two isothermal FCC interaction values fitted to Ni activity.

Srikanth and Jacob (1989), Table 1, DOI 10.1179/mst.1989.5.5.427.
At 1000 K only; homogeneous FCC, pure FCC Ni reference, J/mol real atoms.
Unary/magnetic contributions stay fixed. No uncertainty or physical assessment.
Run as a module from the repository root; published TDB remains external.
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
from pycalphad import Database, Model, variables as v
from symengine import Symbol

from course.materials.cuni.worked_example import COMPONENTS, SOURCE_SHA, load_source

TEMPERATURE = 1000.0
PRESSURE = 101325.0  # Lesson convention; the paper does not specify this pressure.
R = float(v.R)  # Pinned evaluator's constant, 8.3145 J/(mol K).
ARITHMETIC_TOL = 1e-7
ACTIVITY_TOL = 1e-10
DATA_PATH = Path(__file__).with_name("srikanth_jacob1989_ni_activity.csv")


def interaction_basis(x) -> np.ndarray:
    """Ni partial-molar responses for x_Ni and RK order (x_Cu-x_Ni)."""
    x = np.asarray(x, dtype=float)
    return np.column_stack(((1-x)**2, (1-x)**2*(1-4*x)))


def make_forward_model(db: Database) -> dict:
    """Assemble homogeneous FCC g(x), then μ_Ni=g+(1-x)g' relative to pure Ni.

    Fixed VA contributes no real atom. Site fractions are constrained before
    differentiating, so both metal fractions change during an exchange.
    The source is not mutated; fitted corrections are an in-memory isotherm.
    """
    model = Model(db, COMPONENTS, "FCC_A1")
    x = Symbol("x_Ni")
    replacements = {v.T: TEMPERATURE, v.P: PRESSURE, v.N: 1}
    replacements.update({y: (1 if y.species.name == "VA" else
                             x if y.species.name == "NI" else 1-x)
                         for y in model.site_fractions})
    g = model.GM.subs(replacements)
    pure_ni = float(g.subs({x: 1.0}))
    relative = g + (1-x)*g.diff(x) - pure_ni

    def values(expression, compositions):
        return np.array([float(expression.subs({x: float(z)}))
                         for z in np.atleast_1d(compositions)])

    chemical = model.models["xsmix"].subs(replacements)
    l0 = float(chemical.subs({x: 0.5})) / 0.25
    l1 = (float(chemical.subs({x: 0.25})) / (0.25*0.75)-l0) / 0.5
    # Detect a database with a different interaction structure before using
    # the two-parameter RK interpretation in the lesson.
    for z in [0.1, 0.4, 0.8]:
        expected = z*(1-z)*(l0+l1*(1-2*z))
        if abs(float(chemical.subs({x: z}))-expected) > ARITHMETIC_TOL:
            raise ValueError("FCC chemical interaction is not the expected RK orders 0–1")
    return {"g": lambda z: values(g, z),
            "mu_relative": lambda z: values(relative, z),
            "pure_ni_G": pure_ni,
            "baseline_L_J_per_mol": np.array([l0, l1])}


def predict_activity(forward: dict, x, delta_L) -> np.ndarray:
    """Homogeneous Ni activity with two chemical isothermal corrections."""
    relative = forward["mu_relative"](x) + interaction_basis(x) @ np.asarray(delta_L)
    return np.exp(relative/(R*TEMPERATURE))


def fit_isothermal(forward: dict, x, activity) -> dict:
    """Unweighted least squares in RT ln(a), without invented error bars.

    Fit interior observations only. Reject malformed and rank-deficient data;
    no independent A/B temperature coefficients can be inferred at one T.
    """
    x, activity = np.asarray(x, dtype=float), np.asarray(activity, dtype=float)
    if (x.ndim != 1 or activity.shape != x.shape or len(x) < 2
            or not np.all(np.isfinite(x)) or not np.all(np.isfinite(activity))
            or np.any((x <= 0) | (x >= 1)) or np.any(activity <= 0)):
        raise ValueError("Need finite interior fractions and positive matching activities")
    basis = interaction_basis(x)
    if np.linalg.matrix_rank(basis) != 2:
        raise ValueError("The observations do not identify both isothermal interactions")
    observed_mu = R*TEMPERATURE*np.log(activity)
    baseline_mu = forward["mu_relative"](x)
    delta, _, _, _ = np.linalg.lstsq(basis, observed_mu-baseline_mu, rcond=None)
    residual_before = baseline_mu-observed_mu
    residual_after = baseline_mu+basis @ delta-observed_mu
    return {"delta_L_J_per_mol": delta,
            "fitted_L_J_per_mol": forward["baseline_L_J_per_mol"]+delta,
            "residual_before_J_per_mol": residual_before,
            "residual_after_J_per_mol": residual_after,
            "sse_before_J2_per_mol2": float(residual_before @ residual_before),
            "sse_after_J2_per_mol2": float(residual_after @ residual_after)}


def read_observations(path: Path):
    """Read the cited nine-point table at the fixed lesson temperature."""
    rows = list(csv.DictReader(path.open()))
    if len(rows) != 9 or any(float(row["temperature_K"]) != TEMPERATURE for row in rows):
        raise ValueError("Expected the nine 1000 K activity observations")
    return (np.array([float(row["x_NI_mole_fraction"]) for row in rows]),
            np.array([float(row["a_NI_dimensionless"]) for row in rows]))


def run(source: Path, output: Path) -> None:
    started = time.monotonic()
    db = load_source(source)
    data_sha = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    x, activity = read_observations(DATA_PATH)
    forward = make_forward_model(db)
    fitted = fit_isothermal(forward, x, activity)
    delta = fitted["delta_L_J_per_mol"]
    before = predict_activity(forward, x, [0, 0])
    after = predict_activity(forward, x, delta)
    if not np.all(np.isfinite(after)) or not fitted["sse_after_J2_per_mol2"] < fitted["sse_before_J2_per_mol2"]:
        raise ValueError("Fit did not reduce the declared finite residual objective")
    if abs(predict_activity(forward, [1.0], delta)[0]-1) > ACTIVITY_TOL:
        raise ValueError("Pure FCC Ni activity reference failed")

    # A source-independent partial-molar check for the fitted correction.
    z = 0.5
    g_correction = z*(1-z)*(delta[0]+delta[1]*(1-2*z))
    derivative_correction = -0.5*delta[1]
    hand_mu_correction = g_correction+(1-z)*derivative_correction
    basis_mu_correction = float(interaction_basis([z])[0] @ delta)
    if abs(hand_mu_correction-basis_mu_correction) > ARITHMETIC_TOL:
        raise ValueError("Partial-molar hand check failed")
    residual = fitted["residual_after_J_per_mol"]
    if np.max(np.abs(interaction_basis(x).T @ residual)) > ARITHMETIC_TOL:
        raise ValueError("Linear least-squares stationarity check failed")

    output.mkdir(parents=True, exist_ok=True)
    curve_x = np.linspace(0.01, 0.99, 201)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(x, activity, color="black", label="Reported Ni activity")
    axes[0].plot(curve_x, predict_activity(forward, curve_x, [0, 0]), label="Pinned input")
    axes[0].plot(curve_x, predict_activity(forward, curve_x, delta), label="Two-value isothermal fit")
    axes[0].set(xlabel="Mole fraction Ni", ylabel="Ni activity relative to pure FCC Ni",
                title="Homogeneous FCC, 1000 K", xlim=(0, 1))
    axes[0].legend(fontsize=8)
    axes[1].plot(x, fitted["residual_before_J_per_mol"], "o-", label="Before")
    axes[1].plot(x, residual, "s-", label="After")
    axes[1].axhline(0, color="gray", lw=0.8)
    axes[1].set(xlabel="Mole fraction Ni", ylabel="RT ln(a) residual (J/mol atoms)",
                title="Prediction minus observation")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "activity_fit.png", dpi=150)
    plt.close(fig)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source TDB changed during run")
    if hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() != data_sha:
        raise ValueError("Observation table changed during run")
    result = {"source_sha256": SOURCE_SHA, "observation_sha256": data_sha,
              "python": platform.python_version(), "pycalphad": pycalphad.__version__,
              "phase": "FCC_A1", "T_K": TEMPERATURE, "P_Pa": PRESSURE,
              "R_J_per_mol_K": R, "basis": "J/mol real atoms; fixed VA is not an atom",
              "reference": "pure FCC Ni at the same temperature",
              "objective": "unweighted sum of squared RT ln(a) residuals",
              "baseline_L_J_per_mol": forward["baseline_L_J_per_mol"].tolist(),
              "fit": {k: val.tolist() if isinstance(val, np.ndarray) else val for k, val in fitted.items()},
              "observations": [{"x_NI": float(z), "a_NI_reported": float(a),
                                "a_NI_before": float(b), "a_NI_after": float(c)}
                               for z, a, b, c in zip(x, activity, before, after)],
              "checks": {"pure_Ni_activity": float(predict_activity(forward, [1.0], delta)[0]),
                         "hand_x_NI": z, "hand_mu_correction_J_per_mol": float(hand_mu_correction),
                         "basis_mu_correction_J_per_mol": basis_mu_correction,
                         "normal_equation_max_abs_J_per_mol": float(np.max(np.abs(interaction_basis(x).T @ residual)))},
              "tolerances": {"arithmetic_J_per_mol": ARITHMETIC_TOL, "activity_abs": ACTIVITY_TOL},
              "limitations": "Single-temperature calibration, no A/B slopes, no error bars or physical validation; source unchanged.",
              "elapsed_s": time.monotonic()-started}
    (output / "activity_fit_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"baseline_L_J_per_mol": result["baseline_L_J_per_mol"],
                      "fit": result["fit"], "checks": result["checks"], "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.tdb, args.output)
