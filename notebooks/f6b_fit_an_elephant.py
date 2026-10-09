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
# # f6b · Fit an elephant: calibration against prediction (advanced step 17, optional)
#
# **In plain words.** The advanced steps showed how to solve a declared model so well that
# the answer is pinned down to a few thousandths of a J/mol. This notebook asks
# the other question: is the model good enough? You fit four models of growing
# flexibility to the same synthetic measurements and compare how well they fit
# the data they saw with how well they predict data they did not see. "With four
# parameters I can fit an elephant", John von Neumann is said to have joked:
# more parameters always fit better, but do they predict better?
#
# **Learning goals.** After this notebook you can
#
# 1. compute the edges of a miscibility gap (the binodal) for a regular solution
#    with extra Redlich–Kister terms;
# 2. fit models of growing flexibility to calibration data and read their
#    calibration error;
# 3. judge each model on held-out data it never saw, including temperatures
#    outside the calibration range;
# 4. say why a perfect fit to the calibration data does not show that a model is
#    right, and how that relates to the two questions of step 17.
#
# **What you need.** Step 17 of the course ("Did we solve the model?"
# against "Is the model good enough?"), notebook f6 (calibration, then
# validation) and the cards "What does Ω do?" and "What are CALPHAD and a
# database?". The regular solution of step 03 part B is the true model here.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | The true model and the synthetic measurements | main | 10 min |
# | 2 | The edges of a gap, for any model | main | 15 min |
# | 3 | Four models of growing flexibility | main | 10 min |
# | 4 | Fit on the calibration temperatures | main | 15 min |
# | 5 | Open the held-out temperatures | main | 10 min |
# | 6 | Back to the two questions | main | 5 min |
# | 7 | Exercises | both | 20 min |
#
# **Coming from materials.** This is what a CALPHAD assessment does: choose a
# model form, fit its parameters to measurements, and use it where nothing was
# measured. The new part is to keep some data back and look at it only at the
# end.
#
# **Coming from operations research.** This is model selection with a train/test split. The
# fitting itself is a small nonlinear least-squares problem whose residuals
# need an inner solve (a common tangent) for every parameter vector.
#
# **How to work.** Run the cells from top to bottom. In each "Your turn" cell,
# replace `None` with your value and run it: `check` says whether you match,
# without showing the answer. Cells marked *After your attempt* hold worked
# solutions. All measurements here are **synthetic**: made with the course's
# invented regular solution plus seeded noise. Nothing here describes a real
# alloy.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.2.0"
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
# ## 0. Numbers you may change, and the tools
#
# Leave these as they are for the first run: the "Your turn" checks expect them.
# Later change one at a time and rerun everything below.
#
# - `T_CAL`: the calibration temperatures, whose data the fits may use;
# - `T_HELD`: the held-out temperatures, opened only in section 5. Two lie below
#   the calibration range and two above it, closer to where the gap closes;
# - `SIGMA`: the size of the synthetic measurement noise, as a B atom fraction;
# - `SEED`: the seed of the random numbers, so every run makes the same noise.

# %%
T_CAL = [700.0, 750.0, 800.0, 850.0, 900.0, 950.0, 1000.0]   # K
T_HELD = [600.0, 650.0, 1100.0, 1150.0]                     # K, kept closed until section 5
SIGMA = 0.004                                               # synthetic noise, B atom fraction
SEED = 2026

# %% [markdown]
# numpy for arrays, SciPy for the equation solver and the least-squares fit,
# matplotlib for plots, and the course's invented regular solution
# (`binary_family`), which is the true model of this notebook.

# %%
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
from scipy.optimize import fsolve, least_squares
from course.foundations import binary_family as bf

R = bf.R                 # 8.3145 J/(mol K)
OMEGA_TRUE = 20000.0     # J/mol, the regular solution of step 03 part B

# %% [markdown]
# ## 1. The true model and the synthetic measurements (main track, 10 min)
#
# The true model is the regular solution of step 03 part B: one phase model
# whose curve has a hump, so that below a critical temperature it splits into
# an A-rich and a B-rich phase. The two touching compositions of the common
# tangent are the binodal. `bf.regular_binodal(T)` returns them.
#
# The gap closes where $\Omega=2RT$, at the critical temperature
# $T_c=\Omega/2R$.
#
# ### Your turn: where does the gap close?
#
# Give $T_c$ for $\Omega=20000$ J/mol, in K.

# %%
T_c = None   # K
check(T_c, "f6b_tc")

# %% [markdown]
# Now the synthetic "measurements": the true binodal at each temperature, plus
# a small random error drawn from a normal distribution of width `SIGMA`. The
# seed makes the same numbers every run. Real data would come from experiments;
# these are invented, and labelled so.

# %%
rng = np.random.default_rng(SEED)

def true_binodal(T):
    return np.array(bf.regular_binodal(T)["compositions"])

data_cal = np.array([true_binodal(T) + rng.normal(0, SIGMA, 2) for T in T_CAL])    # synthetic
data_held = np.array([true_binodal(T) + rng.normal(0, SIGMA, 2) for T in T_HELD])  # synthetic, kept closed
for T, (left, right) in zip(T_CAL, data_cal):
    print(f"T = {T:6.0f} K   synthetic gap edges {left:.4f} and {right:.4f}")

# %% [markdown]
# Two numbers per temperature: the left and the right edge of the gap.

# %%
assert data_cal.shape == (len(T_CAL), 2), "expected two edges per calibration temperature"
assert np.all((0 < data_cal) & (data_cal < 1)), "a synthetic edge left the range 0 to 1"
print(f"{data_cal.size} calibration numbers from {len(T_CAL)} temperatures")

# %% [markdown]
# ## 2. The edges of a gap, for any model (main track, 15 min)
#
# To fit, we must compute the gap edges for any candidate model, not only the
# true one. The models are Redlich–Kister series: the mixing part of $g$ is
#
# $$g_{\rm mix}(x)=RT\,[x\ln x+(1-x)\ln(1-x)]+x(1-x)\sum_\nu L_\nu\,(1-2x)^\nu ,$$
#
# where $L_0$ plays the role of $\Omega$ and $L_1, L_2,\dots$ make the curve
# lopsided or flatter. (Step 02's end line is left out: a straight line moves no
# touching point.) The two edges $a<b$ satisfy the common-tangent conditions:
# the same slope, and the same height of the tangent at $x=0$,
#
# $$g'(a)=g'(b),\qquad g(a)-a\,g'(a)=g(b)-b\,g'(b).$$
#
# The cell builds each term $x(1-x)(1-2x)^\nu$ as a polynomial, so that its
# slope is exact.

# %%
X = Polynomial([0, 1])
TERMS = [X * (1 - X) * (1 - 2 * X) ** n for n in range(3)]   # x(1-x)(1-2x)^nu for nu = 0, 1, 2
SLOPES = [t.deriv() for t in TERMS]

def g_mix(x, T, L):
    return R * T * (x * np.log(x) + (1 - x) * np.log(1 - x)) + sum(l * t(x) for l, t in zip(L, TERMS))

def g_slope(x, T, L):
    return R * T * np.log(x / (1 - x)) + sum(l * s(x) for l, s in zip(L, SLOPES))

# %% [markdown]
# An equation solver needs a starting guess. We get one from a picture you know:
# pull a string tight under the curve (the lower convex envelope); where the
# string leaves the curve over a wide stretch, its two ends are close to the
# gap edges. The cell finds that stretch on a grid of 801 points.

# %%
GRID = np.linspace(1e-4, 1 - 1e-4, 801)

def envelope_guess(T, L):
    y, hull = g_mix(GRID, T, L), []
    for i in range(len(GRID)):                     # build the lower envelope from left to right
        while len(hull) >= 2 and (GRID[hull[-1]] - GRID[hull[-2]]) * (y[i] - y[hull[-2]]) <= (y[hull[-1]] - y[hull[-2]]) * (GRID[i] - GRID[hull[-2]]):
            hull.pop()
        hull.append(i)
    width, a, b = max((GRID[b] - GRID[a], a, b) for a, b in zip(hull, hull[1:]))
    return (GRID[a], GRID[b]) if width > 0.01 else None

# %% [markdown]
# Then `fsolve` polishes the guess until both conditions hold. If there is no
# wide stretch, or the solver does not satisfy both conditions to 1e-6 J/mol,
# the model has no gap at that temperature and the function returns `None`.

# %%
def gap_edges(T, L):
    guess = envelope_guess(T, L)
    if guess is None:
        return None
    def conditions(v):
        a, b = v
        return [g_slope(a, T, L) - g_slope(b, T, L),
                g_mix(a, T, L) - a * g_slope(a, T, L) - (g_mix(b, T, L) - b * g_slope(b, T, L))]
    a, b = fsolve(conditions, guess, xtol=1e-12)
    ok = 0 < a < b < 1 and b - a > 1e-3 and max(abs(c) for c in conditions((a, b))) < 1e-6
    return np.array([a, b]) if ok else None

# %% [markdown]
# Before trusting it, test it on the true model, where the answer is known.

# %%
for T in (700.0, 1000.0, 1150.0):
    ours, course = gap_edges(T, [OMEGA_TRUE]), true_binodal(T)
    assert np.allclose(ours, course, atol=1e-9), f"at {T} K our edges {ours} differ from the course's {course}"
print("gap_edges reproduces the course's binodal at 700, 1000 and 1150 K")

# %% [markdown]
# ## 3. Four models of growing flexibility (main track, 10 min)
#
# Each model turns its parameters `p` into the list $L=[L_0, L_1, L_2]$ at a
# temperature $T$:
#
# | Model | $L_0$ | $L_1$ | $L_2$ | parameters |
# |---|---|---|---|---|
# | Ω only | $p_0$ | — | — | 1 |
# | Ω + bT | $p_0+p_1T$ | — | — | 2 |
# | L0, L1 | $p_0$ | $p_1$ | — | 2 |
# | L0 + bT, L1, L2 | $p_0+p_1T$ | $p_2$ | $p_3$ | 4: the elephant |
#
# Each also has bounds, so the fit stays where the model has a gap, and a
# starting point near a sensible Ω.
#
# **Predict first.** Which model will fit the calibration data best? Which will
# predict the held-out temperatures best?

# %%
MODELS = {
    "Ω only": (lambda p, T: [p[0]], [19000.0], ([5000.0], [40000.0])),
    "Ω + bT": (lambda p, T: [p[0] + p[1] * T], [19000.0, 0.0], ([5000.0, -20.0], [60000.0, 20.0])),
    "L0, L1": (lambda p, T: [p[0], p[1]], [19000.0, 0.0], ([5000.0, -5000.0], [40000.0, 5000.0])),
    "L0 + bT, L1, L2": (lambda p, T: [p[0] + p[1] * T, p[2], p[3]], [19000.0, 0.0, 0.0, 0.0],
                        ([5000.0, -20.0, -5000.0, -5000.0], [60000.0, 20.0, 5000.0, 5000.0])),
}

# %% [markdown]
# ## 4. Fit on the calibration temperatures (main track, 15 min)
#
# For a parameter vector, `predict` computes both edges at each temperature.
# The residuals are predicted minus synthetic edges; a temperature where the
# model has no gap counts as a large residual of 1. `least_squares` changes the
# parameters, within their bounds, to make the sum of squared residuals small.

# %%
def predict(name, p, temperatures):
    to_L = MODELS[name][0]
    edges = [gap_edges(T, to_L(p, T)) for T in temperatures]
    return np.array([e if e is not None else [np.nan, np.nan] for e in edges])

def residuals(p, name):
    r = (predict(name, p, T_CAL) - data_cal).ravel()
    return np.where(np.isfinite(r), r, 1.0)

def rms(a, b):
    """Root-mean-square difference, ignoring temperatures where a model has no gap."""
    return float(np.sqrt(np.nanmean((np.asarray(a) - np.asarray(b)) ** 2)))

# %% [markdown]
# The fits take a few seconds. Only the calibration data enter; the held-out
# data stay closed.

# %%
fits = {}
for name, (_, start, bounds) in MODELS.items():
    fits[name] = least_squares(residuals, start, bounds=bounds, args=(name,)).x
    error = rms(predict(name, fits[name], T_CAL), data_cal)
    print(f"{name:16s} parameters {np.round(fits[name], 2)}   calibration error {error:.4f}")

# %% [markdown]
# ### Your turn: read the fits
#
# 1. What value of Ω does the one-parameter model find (J/mol)?
# 2. How many synthetic numbers did every fit see?

# %%
omega_fit = None    # J/mol
n_numbers = None    # count
check(omega_fit, "f6b_omega_fit")
check(n_numbers, "f6b_n_cal")

# %% [markdown]
# ## 5. Open the held-out temperatures (main track, 10 min)
#
# Now, and only now, compare each fitted model with the held-out data. Two of
# them lie below the calibration range (600 and 650 K) and two above it (1100
# and 1150 K): every held-out prediction is an extrapolation.

# %%
table = []
for name in MODELS:
    held = predict(name, fits[name], T_HELD)
    table.append((name, len(MODELS[name][1]), rms(predict(name, fits[name], T_CAL), data_cal), rms(held, data_held), int(np.isnan(held).sum() // 2)))
print("model             parameters  calibration error  held-out error  held-out T without a gap")
for name, k, cal, held, missing in table:
    print(f"{name:16s} {k:6d}       {cal:12.4f}      {held:12.4f}      {missing:6d}")

# %% [markdown]
# The two errors side by side, and the four models' gap edges against all the
# synthetic data (filled: calibration; open: held out).

# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
names = [row[0] for row in table]
ax1.bar(np.arange(4) - 0.2, [row[2] for row in table], 0.4, label="calibration")
ax1.bar(np.arange(4) + 0.2, [row[3] for row in table], 0.4, label="held out")
ax1.set(xticks=range(4), xticklabels=names, ylabel="rms error (B atom fraction)"); ax1.legend()
ax1.tick_params(axis="x", labelsize=8)
temps = np.arange(580.0, 1180.0, 10.0)
for name in MODELS:
    edges = predict(name, fits[name], temps)
    ax2.plot(edges[:, 0], temps, label=name); ax2.plot(edges[:, 1], temps, color=ax2.lines[-1].get_color())
ax2.plot(data_cal.ravel(), np.repeat(T_CAL, 2), "ko", ms=4); ax2.plot(data_held.ravel(), np.repeat(T_HELD, 2), "ko", mfc="none", ms=6)
ax2.set(xlabel="B atom fraction", ylabel="T (K)", title="Gap edges of the four fitted models"); ax2.legend(fontsize=7)
plt.tight_layout(); plt.show()

# %% [markdown]
# ### Your turn: judge the models
#
# 1. Which model has the lowest calibration error? Give its name as printed.
# 2. Does that model also have the lowest held-out error? (True or False)

# %%
best_calibration = None   # a model name, for example "Ω only"
also_best_held = None     # True or False
check(best_calibration, "f6b_best_cal")
check(also_best_held, "f6b_also_best_held")

# %% [markdown]
# Whether flexibility helped or hurt here is your finding, from your table. It
# can change with the noise, the seed or the choice of held-out temperatures
# (section 7). What does not change: a lower calibration error is guaranteed by
# extra parameters, a lower held-out error is not.
#
# ## 6. Back to the two questions (main track, 5 min)
#
# On steps 10–16 the question was "did we solve the declared model?", and the
# answer was a remaining uncertainty of 0.003 J/mol or less. This notebook asks
# "is the model good enough?". Several models fit the same synthetic data about
# equally well and still disagree away from it. The cell measures how far the
# four fitted models disagree about the left gap edge at 600 K, outside the
# calibration range.

# %%
left_600 = [predict(name, fits[name], [600.0])[0, 0] for name in MODELS]
spread = float(np.nanmax(left_600) - np.nanmin(left_600))
print("left gap edge at 600 K:", {name: round(float(v), 4) for name, v in zip(MODELS, left_600)})
print(f"the models disagree by {spread:.4f} in B atom fraction, from fits to the same data")

# %% [markdown]
# Solving each of these models more precisely would not shrink that spread: it
# comes from the model choice and the data, not from the solver. A database is
# trustworthy where its data are, and an equilibrium calculation inherits that
# trust, no more.
#
# ## 7. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Set `SIGMA = 0.0` in section 0 and rerun. What happens to the calibration
#   and held-out errors of each model, and why can a flexible model no longer
#   do worse?
# - Change `SEED` and rerun. Does your verdict from section 5 survive new noise?
# - Move 1100 K from `T_HELD` to `T_CAL`. Which model gains most?
#
# **Optimisation flavour: complete a function, then one deeper exercise.**
#
# Complete `n_parameters`: given a model name, return how many parameters the
# fit adjusts (read it from `MODELS`). Then use it for the four-parameter model.

# %%
def n_parameters(name):
    """Number of fitted parameters of a model in MODELS."""
    return None   # replace with the count

check(n_parameters("L0 + bT, L1, L2"), "f6b_n_parameters")

# %% cellView="form"
#@title After your attempt: a solution of n_parameters
def n_parameters_solution(name):
    return len(MODELS[name][1])      # one starting value per parameter

print({name: n_parameters_solution(name) for name in MODELS})

# %% [markdown]
# **Deeper exercise (operations research).** A single held-out split is one sample. Do
# leave-one-out cross-validation on the calibration temperatures: for each
# temperature, fit on the other six and predict the one left out; report the
# rms of those predictions for "Ω only" and for the four-parameter model. Does
# it agree with section 5?

# %% cellView="form"
#@title After your attempt: leave-one-out cross-validation
def leave_one_out(name):
    errors = []
    for k in range(len(T_CAL)):
        keep = [i for i in range(len(T_CAL)) if i != k]
        def r(p):
            out = (predict(name, p, [T_CAL[i] for i in keep]) - data_cal[keep]).ravel()
            return np.where(np.isfinite(out), out, 1.0)
        p = least_squares(r, MODELS[name][1], bounds=MODELS[name][2]).x
        errors.append(predict(name, p, [T_CAL[k]])[0] - data_cal[k])
    return rms(np.array(errors), 0.0)

for name in ("Ω only", "L0 + bT, L1, L2"):
    print(f"{name:16s} leave-one-out error {leave_one_out(name):.4f}")

# %% [markdown]
# ## Recap
#
# - More parameters always lower the calibration error, or keep it the same.
# - Only data that took no part in the fit, here the held-out temperatures,
#   test a prediction; extrapolation is the hardest test.
# - Models that fit equally well can disagree where nothing was measured; no
#   solver precision removes that spread.
# - The ceiling, floor and branch-and-bound of steps 13–16 answer "did we solve the
#   declared model?". "Is the model good enough?" needs data, held-out tests and
#   judgement, as in this notebook.
#
# **Next:** step 17 of the course (two questions, a joint case and back to
# operations research); notebook [f6](f6_fitting_synthetic.ipynb) for calibration and validation
# with one parameter; [Task 02](task02_cuni_activity_fit.ipynb) for a fit to
# published activity data.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers. A fit that reports a parameter at its bound
# means the model could not do better within its allowed range.
