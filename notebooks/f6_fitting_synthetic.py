# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: cellView,-all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: kernelspec,jupytext,-all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # f6 · Fitting a model parameter: identifiability, residuals, calibration vs validation
#
# **Learning question:** you have a handful of observations and one adjustable
# number Ω in a model. How do you define the mismatch, find the best Ω, check the
# result on points you did not use, and recognise data that cannot determine Ω
# at all?
#
# Used in: Lesson 9 (worksheet A1–A4, B1–B4); Task 02 when no download is
# possible. The data are invented on purpose: they were made without noise from
# the same equation that is fitted, so the method can be tested against the value
# used to make them (named in the Limits, after your attempt).
#
# **Why fitting matters in CALPHAD.** The parameters in a database (such as the
# interaction Ω of f3–f5) are not calculated from first principles; they are
# chosen so that the model reproduces measurements. This notebook shows that step
# with the smallest possible example: one parameter, one kind of data, one
# temperature. The route through the notebook:
#
# 1. the data and what exactly they measure;
# 2. residuals and the objective: how to put "mismatch" into one number;
# 3. the best Ω, by a formula and by a numerical solver;
# 4. a test on points that were not used for the fit;
# 5. what goes wrong when the observable is not the one the model predicts;
# 6. data that cannot determine a parameter at all.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.2"
import os, pathlib, subprocess, sys, time
ROOT = next((p for p in (pathlib.Path.cwd(), *pathlib.Path.cwd().parents)
             if (p / "pyproject.toml").is_file() and (p / "course").is_dir()), None)
if ROOT is None and "google.colab" in sys.modules:
    ROOT = pathlib.Path("/content/CalphadIntro")
    if not ROOT.is_dir():
        clone = ["git", "clone", "-q", "--depth", "1", "--branch", RELEASE,
                 "https://github.com/ukerzel/CalphadIntro.git", str(ROOT)]
        git = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        if subprocess.run(clone, env=git, capture_output=True).returncode:
            raise SystemExit(f"Could not download course release {RELEASE}: check the internet "
                             "connection and run this cell again.")
    if not (ROOT / ".colab-ready").exists():
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r",
                           str(ROOT / "notebooks" / "requirements-colab.txt")]).returncode:
            raise SystemExit("Installing the course packages failed; run this cell again.")
        (ROOT / ".colab-ready").touch()
        # Colab has already loaded its own numpy; a fresh session is needed to use the installed versions.
        print("Installed the course's package versions. Colab now restarts this session and"
              " reports a crash; that is expected. When it has reconnected, run this cell again"
              " (it will not install twice), then the rest of the notebook.", flush=True)
        time.sleep(3)
        os.kill(os.getpid(), 9)
if ROOT is None:
    raise SystemExit("Open this notebook from the course folder (poetry run jupyter lab) or in Colab.")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from notebooks.helpers import check, confirm, database, show_versions
show_versions(RELEASE)

# %% [markdown]
# ## 1. What was observed, and what is fitted
#
# The invented A–B model of f3–f5, phase ALPHA, at T = 1000 K and
# p = 100000 Pa. The observable is the **homogeneous ALPHA mixing enthalpy** per
# mole of all atoms at a given B fraction x: the enthalpy of one ALPHA solution
# at that composition minus the same phase's pure A and pure B enthalpies,
#
# $$h_{\rm mix}(x)=h_{\rm ALPHA}(x)-[(1-x)\,1000+x\,13000]=\Omega\,x(1-x)\quad\mathrm{J/mol}.$$
#
# "Homogeneous" means one composition, whether or not that state is stable. It is
# not what an equilibrium calculation returns (section 5).
#
# Where the numbers 1000 and 13000 come from: in the database, pure A in ALPHA has
# $G=1000-10T$ and pure B has $G=13000-10T$ (J/mol). For a Gibbs energy of the
# form $a+bT$ the enthalpy $H=G-T\,dG/dT$ is the constant $a$ (the $bT$ term is
# $-TS$ with entropy $S=-b$), so the pure enthalpies are 1000 and 13000 J/mol. The ideal mixing term $RT[x\ln x+(1-x)\ln(1-x)]$ is pure entropy
# and contributes no enthalpy. What is left after subtracting the weighted pure
# enthalpies is only the interaction term $\Omega\,x(1-x)$.
#
# Everything else in the model stays fixed (temperature, pressure, pure-element
# functions, ideal entropy). The only fitted number is the interaction **Ω**,
# allowed in 0 … 24000 J/mol.
#
# | Quantity | Value | Unit |
# |---|---:|---|
# | temperature T | 1000 | K |
# | pressure p | 100000 | Pa |
# | observable | homogeneous ALPHA $h_{\rm mix}$ | J/mol of atoms |
# | composition x | B atom fraction | — |
# | parameter Ω | 0 … 24000 | J/mol |
#
# The data file has two groups. The **training** points are used to choose Ω.
# The **held-out** points at x = 0.2, 0.4, 0.6, 0.8 are kept closed until Ω is
# fixed; then they test the prediction (section 4).
#
# The data are stored in a JSON file, a common text format for structured data.
# `json.loads(...)` turns its text into nested Python dictionaries and lists, so
# `data["training"]["x_B"]` is the list of training compositions. `np.array(...,
# dtype=float)` turns each list into a numpy array of decimal numbers, so that
# arithmetic works on all points at once. The held-out enthalpies are deliberately
# **not** read yet.

# %%
import json
from pathlib import Path

import numpy as np

data = json.loads(Path("course/foundations/binary_fit_data.json").read_text())   # nested dicts and lists
x_train = np.array(data["training"]["x_B"], dtype=float)      # B atom fraction
h_train = np.array(data["training"]["H_mix"], dtype=float)    # J/mol of atoms
x_held = np.array(data["held_out"]["x_B"], dtype=float)       # values stay closed for now
OMEGA_BOUNDS = (0.0, 24000.0)                                 # J/mol
# A name in capitals marks a constant: it is set once and not changed later.

print(f"T = {data['T_K']} K, p = {data['P_Pa']} Pa, basis: {data['amount_basis']}")
print("training:   x      h_mix (J/mol)")
for x, h in zip(x_train, h_train):        # walk through the pairs (x, h) together
    print(f"          {x:.1f}   {h:8.0f}")   # :8.0f = 8 characters wide, 0 decimals
print("held-out compositions (values not used yet):", x_held)

# %% [markdown]
# Look at the printed table: the values are symmetric about x = 0.5 and largest
# there, as $x(1-x)$ is. All five are positive, so mixing A and B in ALPHA costs
# enthalpy (Ω > 0).
#
# ## 2. Residuals and the objective (A1, A2)
#
# A **forward model** predicts the observable at a given x for a trial Ω:
# $\hat h(x;\Omega)=\Omega\,a(x)$ with $a(x)=x(1-x)$ (dimensionless). The
# **residual** is prediction minus observation, in J/mol:
#
# $$r_i=\Omega\,a_i-h_i .$$
#
# A positive residual means the model predicts too much. The **objective** is
# the unweighted sum of squared residuals over the training points,
#
# $$J(\Omega)=\sum_i r_i^2,\qquad [J]=(\mathrm{J/mol})^2 .$$
#
# (J the objective, not J the joule; the units tell them apart.)
#
# Notation: the hat in $\hat h$ marks a model prediction, and the index $i$ numbers
# the training points (i = 1 … 5), so $a_i=a(x_i)$ and $h_i$ is the observed value
# at $x_i$. The factor $a(x)$ is called the **sensitivity**: it says how much the
# prediction at x changes when Ω changes by 1 J/mol. It is largest at x = 0.5,
# where it is 0.25.
#
# The cell defines these four quantities as small Python functions. `def name(...):`
# starts a function, and `return` gives back its result. Because x can be a whole
# numpy array, each function works on one point or on all points at once. In
# `objective`, `r @ r` is the dot product of the residual array with itself,
# $\sum_i r_i\,r_i$, which is exactly the sum of squares.
#
# Worked trial Ω = 18000 J/mol:

# %%
def a_sens(x):
    return x * (1 - x)                       # dimensionless sensitivity to Ω

def predict(omega, x):
    return omega * a_sens(x)                 # J/mol of atoms

def residuals(omega, x, h):
    return predict(omega, x) - h             # prediction − observation, J/mol

def objective(omega, x, h):
    r = residuals(omega, x, h)
    return float(r @ r)                      # (J/mol)²

trial = 18000.0   # J/mol, a trial value, not yet the best one
print("  x    prediction  observation  residual  squared residual")
for x, h in zip(x_train, h_train):
    r = residuals(trial, x, h)   # one point at a time, for the table
    print(f" {x:.1f}  {predict(trial, x):9.0f}  {h:10.0f}  {r:9.0f}  {r * r:12.0f}")
print(f"J(18000) = {objective(trial, x_train, h_train):.0f} (J/mol)²")

# %% [markdown]
# All five residuals are negative: Ω = 18000 J/mol predicts too little at every
# point, so the best Ω is larger. The biggest squared residual sits at x = 0.5,
# where the sensitivity is largest.
#
# Why not minimise the plain sum of residuals? Two residuals of +500 and −500 add
# to zero although both points are badly predicted. Squaring stops errors of
# opposite sign from cancelling.
#
# ### Your turn (A2)
#
# Try Ω = 16000 J/mol by hand or with the functions above. Give the residual at
# x = 0.5 and the objective. Then the objective at Ω = 22000. Do the bounds
# 0 … 24000 alone tell you which Ω is right (True or False)?
#
# A3, to think about: an equilibrium calculation varies phase amounts and
# compositions at a **fixed** model. What varies here, and what stays fixed?
# Would moving each observation's x until its energy drops be a valid fit?
#
# To use the functions, type for example `residuals(16000.0, 0.5, 5000.0)` or
# `objective(16000.0, x_train, h_train)` in a new cell or in the cell below. Then
# replace each `None` by your value (`True`/`False` without quotes for the last one)
# and run the cell; `check` tells you whether each value matches.

# %%
residual_16000_at_05 = None   # J/mol
objective_16000 = None        # (J/mol)²
objective_22000 = None        # (J/mol)²
bounds_decide_omega = None    # True or False
check(residual_16000_at_05, "f6_a2_residual_05")
check(objective_16000, "f6_a2_objective")
check(objective_22000, "f6_a2_j_22000")
check(bounds_decide_omega, "f6_a2_bounds_enough")

# %% [markdown]
# ## 3. Solve the one-parameter fit (A4)
#
# J is a parabola in Ω: $J=\sum_i(\Omega a_i-h_i)^2$. Setting $dJ/d\Omega=0$ gives
#
# $$\Omega_*=\frac{\sum_i a_i h_i}{\sum_i a_i^2}.$$
#
# Step by step: expanding the square gives
# $J=\Omega^2\sum_i a_i^2-2\Omega\sum_i a_i h_i+\sum_i h_i^2$, a parabola in Ω that
# opens upwards because $\sum_i a_i^2>0$. Its slope is
# $dJ/d\Omega=2\Omega\sum_i a_i^2-2\sum_i a_ih_i$; the minimum is where the slope is
# zero, which gives the formula above. A model that is linear in its parameter, as
# here, always leads to such a closed formula ("linear least squares").
#
# The denominator is positive as long as at least one training point has
# $0<x<1$, so the minimum is unique. If $\Omega_*$ fell outside the bounds, the
# bounds would decide the answer instead, and that would be worth a closer look.
#
# ### Your turn (A4)
#
# Given $\sum a_i^2=0.1669$ and $\sum a_i h_i=3338$ J/mol, what is $\Omega_*$
# (J/mol)? Is a bound active (True or False)?
#
# A bound is **active** when the best value lies on it (here at 0 or at
# 24000 J/mol), so that the bound, not the data, decides the result.

# %%
omega_star = None         # J/mol
bound_active = None       # True or False
check(omega_star, "f6_a4_omega")
check(bound_active, "f6_a4_bound_active")

# %% [markdown]
# ## After your attempt: the formula, the course fit and the objective curve
#
# The course module `binary_fit` solves the same problem numerically
# (`scipy.optimize.least_squares` with the bounds) by two routes: the plain
# formula, and pycalphad's `calculate` on `binary_family.tdb` (f5). Both use the
# same observable, residual, training data and bounds. The tool route takes about
# 1 s.
#
# `scipy.optimize.least_squares` is a general solver: you give it a function that
# returns the residual array for a trial parameter, a starting value and the
# bounds; it changes the parameter step by step until the sum of squares stops
# decreasing. It does not need the closed formula, so it also works for models
# where no formula exists. Its `status` number says why it stopped: a positive
# value (1–4) means one of its convergence tests was met, 0 means it ran out of
# steps. A solver that converged has found the minimum of J; whether the model is
# good is a separate question that only the residuals can answer.
#
# What the cell does:
#
# 1. `confirm` checks your A2 values and the A4 formula.
# 2. `fits[route] = fit_interaction(...)` fits Ω by both routes, using **only** the
#    training points. `fits` is a dictionary with one entry per route.
# 3. The plot shows J over the whole allowed range (solid curve), your three
#    trial values (triangles) and the minimum (open circle). The dotted lines are
#    the bounds.

# %% cellView="form"
#@title After your attempt: run to check the fit and plot J(Ω)
import matplotlib.pyplot as plt
from course.foundations.binary_fit import fit_interaction, predict_hmix

# Worksheet values of J at four trial Ω (J/mol), and the A2 residual.
for omega, expected in ((16000.0, 2670400.0), (18000.0, 667600.0), (20000.0, 0.0), (22000.0, 667600.0)):
    confirm(objective(omega, x_train, h_train), expected, f"J({omega:.0f})", tol=1e-6)
confirm(residuals(16000.0, 0.5, 5000.0), -1000.0, "Residual at x = 0.5 for Ω = 16000", tol=1e-9)

# The closed formula Ω* = Σa·h / Σa² (section 3).
a = a_sens(x_train)                                     # sensitivities of the five training points
denominator, numerator = float(a @ a), float(a @ h_train)   # Σa² (dimensionless), Σa·h (J/mol)
omega_formula = numerator / denominator                 # J/mol
print(f"Σa² = {denominator:.4f}, Σa·h = {numerator:.1f} J/mol, Ω* = {omega_formula:.6f} J/mol")
confirm(denominator, 0.1669, "Σa²", tol=1e-12)
confirm(numerator, 3338.0, "Σa·h", tol=1e-9)
confirm(omega_formula, 20000.0, "Ω* from the formula", tol=1e-5)

# The numerical fit, by the plain route and by the pycalphad ("tool") route.
fits = {}
for route in ("plain", "tool"):
    fits[route] = fit_interaction(x_train, h_train, route)   # training data only
    print(f"{route:5s} route: Ω = {fits[route]['omega']:.6f} J/mol, J = {fits[route]['sse']:.6f} (J/mol)², "
          f"solver status {fits[route]['solver_status']}")
    confirm(fits[route]["omega"], 20000.0, f"Ω from the {route} route", tol=1e-5)

# J(Ω) over the allowed range: 241 values from 0 to 24000 J/mol (steps of 100).
grid = np.linspace(*OMEGA_BOUNDS, 241)   # *OMEGA_BOUNDS unpacks the tuple into (0.0, 24000.0)
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(grid / 1000, [objective(w, x_train, h_train) / 1e6 for w in grid], "-", color="0.3", label="J(Ω), training points")   # kJ/mol on x, 10⁶ (J/mol)² on y
trials = [16000.0, 18000.0, 22000.0]
ax.plot([w / 1000 for w in trials], [objective(w, x_train, h_train) / 1e6 for w in trials], "^", ms=8, label="worksheet trials")
ax.plot([omega_formula / 1000], [0.0], "o", ms=9, mfc="none", mew=2, label="minimum Ω*")   # mfc="none": open marker
for edge in OMEGA_BOUNDS:
    ax.axvline(edge / 1000, ls=":", color="0.5")   # dotted vertical line at each bound
ax.set(xlabel="Ω (kJ/mol)", ylabel="J (10⁶ (J/mol)²)", title="Objective over the allowed range (dotted: bounds)")
ax.legend()
plt.show()
print(" Ω (J/mol)   J ((J/mol)²)")
for w in (12000.0, 16000.0, 18000.0, 20000.0, 22000.0, 24000.0):
    print(f" {w:8.0f}   {objective(w, x_train, h_train):12.0f}")

# %% [markdown]
# The curve is a parabola with its lowest point inside the bounds, and the two
# routes agree. J at the minimum is zero (up to rounding) only because the data
# contain no noise; with real data it stays positive.
#
# ## 4. Calibration, then validation (B2, B4)
#
# **Calibration** chose Ω from the training points. **Validation** asks whether
# the calibrated model predicts points that took no part in choosing Ω. That only
# works if those points stay untouched: if you change Ω or the model after seeing
# them, they become training data and you need a new, honest test.
#
# Here the held-out values were made with the same equation as the training
# values. A good match therefore checks the method and the code (recovery of a
# known value), not how well this equation describes a real alloy.
#
# ### Your turn (B2)
#
# With Ω fixed at your fitted value, predict $h_{\rm mix}$ at x = 0.4 (J/mol).
# Then: may you keep tuning Ω on the held-out points and still call them
# untouched (True or False)?
#
# ### Your turn (B4, a fresh example)
#
# A separate noiseless observation: x = 0.25, $h_{\rm mix}$ = 3750 J/mol. Infer
# Ω from this one equation, then predict at x = 0.4 without fitting again.
#
# For B4, one observation and one unknown give one equation,
# $h_{\rm mix}=\Omega\,x(1-x)$, which you can solve for Ω directly. Use the
# function `predict(omega, x)` from section 2 for the predictions if you like.

# %%
held_prediction_04 = None   # J/mol
retune_on_held_out = None   # True or False
fresh_omega = None          # J/mol, from x = 0.25 only
fresh_prediction_04 = None  # J/mol
check(held_prediction_04, "f6_b2_pred_04")
check(retune_on_held_out, "f6_b2_retune_ok")
check(fresh_omega, "f6_b4_omega")
check(fresh_prediction_04, "f6_b4_pred_04")

# %% [markdown]
# ## After your attempt: open the held-out values and plot data, model and residuals
#
# Only now are the held-out enthalpies read from the file. The cell prints them
# next to the predictions of both fitted routes, then draws two panels:
#
# - **left:** the fitted model curve, the trial Ω = 18000 J/mol (dashed), the
#   training points (filled circles) and the held-out points (open squares);
# - **right:** the residuals, prediction minus observation. A good fit has
#   residuals scattered around zero; residuals that all have the same sign (as for
#   Ω = 18000) show that the parameter is off. A residual plot often shows a
#   problem more clearly than the curve plot, because it removes the large
#   common shape of the data.

# %% cellView="form"
#@title After your attempt: run to compare with the held-out points
h_held = np.array(data["held_out"]["H_mix"], dtype=float)   # opened only now, after the fit
omega_fit = fits["plain"]["omega"]                          # J/mol, from the training points only
print(" x    stored h_mix   plain prediction   tool prediction   (J/mol)")
# Predictions at the held-out compositions with each route's fitted Ω, J/mol.
predicted = {route: predict_hmix(fits[route]["omega"], x_held, route) for route in ("plain", "tool")}
for i, x in enumerate(x_held):
    print(f" {x:.1f}  {h_held[i]:10.0f}   {predicted['plain'][i]:14.6f}   {predicted['tool'][i]:14.6f}")
for route in ("plain", "tool"):
    # The largest absolute held-out residual must be zero (noise-free data).
    confirm(float(np.max(np.abs(predicted[route] - h_held))), 0.0, f"Largest held-out residual, {route} route", tol=1e-6)
confirm(predict(omega_fit, 0.4), 4800.0, "Prediction at x = 0.4", tol=1e-6)
confirm(3750.0 / a_sens(0.25), 20000.0, "Ω from the single point x = 0.25", tol=1e-9)

x_line = np.linspace(0, 1, 201)   # a fine composition grid for smooth curves
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))   # two panels side by side
left.plot(x_line, predict(omega_fit, x_line), "-", color="0.3", label=f"model, Ω = {omega_fit:.0f} J/mol")
left.plot(x_line, predict(18000.0, x_line), "--", color="0.6", label="trial Ω = 18000 J/mol")
left.plot(x_train, h_train, "o", ms=8, label="training (used in the fit)")
left.plot(x_held, h_held, "s", ms=8, mfc="none", mew=2, label="held out (not used)")
left.set(xlabel="B atom fraction x", ylabel="h_mix (J/mol of atoms)", title="Homogeneous ALPHA, 1000 K")
left.legend(fontsize=10)
right.axhline(0, color="0.5", lw=0.8)   # zero line: perfect prediction
right.plot(x_train, residuals(omega_fit, x_train, h_train), "o", ms=8, label="training, fitted Ω")
right.plot(x_held, residuals(omega_fit, x_held, h_held), "s", ms=8, mfc="none", mew=2, label="held out, fitted Ω")
right.plot(x_train, residuals(18000.0, x_train, h_train), "^--", label="training, Ω = 18000")
right.set(xlabel="B atom fraction x", ylabel="residual (J/mol of atoms)", title="Prediction minus observation")
right.legend(fontsize=10)
fig.tight_layout()   # adjust spacing so labels do not overlap
plt.show()

# %% [markdown]
# ## 5. The wrong observable (B1)
#
# At 1000 K and x = 0.5 with Ω = 20000 J/mol, a tool reports the total
# homogeneous enthalpy $H = 12000$ J/mol. An equilibrium calculation at the same
# overall composition instead lets ALPHA split into two compositions (the
# miscibility gap of f4 and f5); after the same reference subtraction its mixture
# gives 2810.686236 J/mol.
#
# The point of this section: a fit is only meaningful if the model calculates the
# same quantity that was measured. The model's $\Omega\,x(1-x)$ describes a
# homogeneous solution. If the measured number belonged to a two-phase mixture
# instead, comparing the two would fit Ω to the wrong thing.
#
# ### Your turn (B1)
#
# Subtract the reference to get the homogeneous $h_{\rm mix}$ at x = 0.5 (J/mol),
# and give how far the equilibrium-mixture value lies below it (J/mol, positive;
# the nearest J/mol is enough).
#
# The reference is the same as in section 1: $(1-x)\,1000+x\,13000$ J/mol.

# %%
hmix_homogeneous_05 = None   # J/mol
equilibrium_shortfall = None # J/mol
check(hmix_homogeneous_05, "f6_b1_hmix")
check(equilibrium_shortfall, "f6_b1_error")

# %% [markdown]
# The next cell rebuilds the equilibrium-mixture value from the plain model. It
# finds the two gap compositions at 1000 K, uses the **lever rule** for their
# amounts, $f_{\rm right}=(z-x_{\rm left})/(x_{\rm right}-x_{\rm left})$ with
# z = 0.5, and averages the two homogeneous enthalpies with these amounts before
# subtracting the reference.

# %% cellView="form"
#@title After your attempt: run to compute the equilibrium-mixture value
from course.foundations import binary_family as plain

left_x, right_x = plain.regular_binodal(1000.0)["compositions"]     # the two gap compositions at 1000 K
f_right = (0.5 - left_x) / (right_x - left_x)                       # lever rule
# Homogeneous enthalpy (J/mol) of ALPHA at each gap composition, Ω = 20000 J/mol.
h_left, h_right = (float(plain.regular_properties(1000.0, x, 20000.0)["HM"]) for x in (left_x, right_x))
h_mixture = (1 - f_right) * h_left + f_right * h_right - (1000 + 12000 * 0.5)   # amount-weighted, minus reference
h_homogeneous = float(plain.regular_properties(1000.0, 0.5, 20000.0)["HM"]) - (1000 + 12000 * 0.5)
print(f"gap compositions {left_x:.6f} and {right_x:.6f}, each half the amount")
print(f"homogeneous h_mix = {h_homogeneous:.6f} J/mol; equilibrium mixture = {h_mixture:.6f} J/mol")
confirm(h_homogeneous, 5000.0, "Homogeneous h_mix at x = 0.5", tol=1e-6)
confirm(h_mixture, 2810.686236, "Equilibrium-mixture h_mix at x = 0.5", tol=1e-6)
confirm(h_homogeneous - h_mixture, 2189.313764, "Shortfall of the equilibrium mixture", tol=1e-6)

# %% [markdown]
# Why the mixture value is lower: each of the two gap compositions lies far from
# x = 0.5, where $x(1-x)$ is small, so each has a small mixing enthalpy. Their
# average is therefore well below the homogeneous value at x = 0.5. If you fitted
# Ω to the mixture value with the homogeneous formula, you would get an Ω that is
# too small.
#
# Restricting the phase list to ALPHA does not prevent the split. Do not change
# the observation, refit Ω or move the temperature to hide the gap: the fit would
# converge and still answer the wrong question. Decide what was measured first,
# then optimise.

# %% [markdown]
# ## 6. Data that cannot determine a parameter (B3)
#
# A parameter is **identifiable** from given data if different values of it give
# different predictions for those data.
#
# Two cases to test:
#
# - data only at pure A or pure B (x = 0 and x = 1), with $\hat h=\Omega\,x(1-x)$;
# - an interaction that depends on temperature,
#   $g_{\rm excess}=(A+BT)\,x(1-x)$, A in J/mol and B in J/(mol K), observed
#   only through the enthalpy $h=g-T\,\partial g/\partial T$.
#
# In the second case **A and B are two model coefficients**, not the elements A
# and B. The relation $h=g-T\,\partial g/\partial T$ follows from $g=h-Ts$ and
# $s=-\partial g/\partial T$ (the entropy is minus the temperature slope of g).
# The derivative $\partial g/\partial T$ is taken at fixed composition x.
#
# ### Your turn (B3)
#
# What does the model predict at x = 1 for Ω = 24000 (J/mol)? Is Ω identifiable
# from pure-end data only? Can enthalpy data, even at many temperatures,
# determine B (True or False for both)?

# %%
pure_end_prediction = None     # J/mol
omega_identifiable_pure = None # True or False
B_identifiable_from_h = None   # True or False
check(pure_end_prediction, "f6_b3_pure_pred")
check(omega_identifiable_pure, "f6_b3_identifiable")
check(B_identifiable_from_h, "f6_b3_B_identifiable")

# %% [markdown]
# The next cell tests both cases numerically. For the pure ends it evaluates J for
# three very different Ω and then asks the course fit to fit those data; the
# course fit refuses on purpose and raises an error. `try: ... except ValueError
# as error:` catches that error and prints its message instead of stopping the
# notebook.
#
# For the temperature-dependent interaction it computes $\partial g/\partial T$
# numerically with a **central difference**,
# $[g(T+\Delta T)-g(T-\Delta T)]/(2\Delta T)$ with $\Delta T=0.5$ K, and then the
# enthalpy for three values of B and two temperatures.

# %% cellView="form"
#@title After your attempt: run to see both cases numerically
print("Pure ends: a = x(1 − x) = 0 at x = 0 and x = 1, so every Ω predicts zero mixing enthalpy there.\n"
      "Temperature-dependent interaction: ∂g/∂T = B·x(1 − x), so h = g − T·∂g/∂T = A·x(1 − x);\n"
      "the B·T term cancels and enthalpy data carry no information about B.\n")
x_pure, h_pure = np.array([0.0, 1.0]), np.array([0.0, 0.0])   # two pure-end observations, J/mol
print(" Ω (J/mol)   J for pure-end data ((J/mol)²)")
for w in (0.0, 12000.0, 24000.0):
    print(f" {w:8.0f}   {objective(w, x_pure, h_pure):.1f}")
    confirm(objective(w, x_pure, h_pure), 0.0, f"J({w:.0f}) on pure-end data", tol=1e-12)
try:
    fit_interaction(x_pure, h_pure, "plain")
except ValueError as error:   # the course fit rejects data with zero sensitivity to Ω
    print("The course fit refuses these data:", error)

def g_excess(A, B, T, x):
    return (A + B * T) * x * (1 - x)              # J/mol

def h_excess(A, B, T, x, dT=0.5):   # g is linear in T, so a central difference is exact
    dgdT = (g_excess(A, B, T + dT, x) - g_excess(A, B, T - dT, x)) / (2 * dT)   # ∂g/∂T, J/(mol K)
    return g_excess(A, B, T, x) - T * dgdT        # J/mol

print("\n B (J/(mol K))   T (K)   h_excess at x = 0.3 (J/mol), A = 20000")
values = []
for B in (-5.0, 0.0, 5.0):          # three very different B, J/(mol K)
    for T in (800.0, 1200.0):       # two temperatures, K
        values.append(h_excess(20000.0, B, T, 0.3))
        print(f" {B:6.1f}          {T:6.0f}   {values[-1]:.6f}")   # values[-1] is the last entry added
confirm(max(values) - min(values), 0.0, "Spread of h_excess over B and T", tol=1e-6)
confirm(values[0], 20000.0 * 0.3 * 0.7, "h_excess = A·x(1−x)", tol=1e-6)

# %% [markdown]
# Every Ω fits pure-end data equally well, and every B gives the same
# enthalpies. An optimiser would still return *some* number; that number would
# be an accident of its starting point, not a result. Information that depends
# on entropy (for example data at several temperatures that involve G, not only
# H) is needed to determine B.
#
# In the J(Ω) picture of section 3: for pure-end data the curve is completely
# flat, so there is no lowest point to find. A flat (or nearly flat) objective is
# the sign of a parameter the data cannot determine.
#
# Worked answers: [instructor guide](../course/instructor/lesson_09_guide.md)
# (A1–B4); reading: [Lesson 9](../course/foundations/lesson_09_fitting.md).
#
# ## 7. Limits
#
# The data are invented and noise-free, generated with the same equation that
# is fitted. Recovering Ω = 20000 J/mol shows that the method and code work; it
# says nothing about any real alloy, and there is no uncertainty to report.
# Real measurements scatter, often have different uncertainties, and the model
# may not have the right form; then the residuals do not vanish and a held-out
# check can fail. One parameter at one temperature is the simplest case: a real
# assessment adjusts many parameters against several kinds of data.
# Next: [Task 02 · two Cu–Ni interaction values from nine Ni activities](task02_cuni_activity_fit.ipynb).
