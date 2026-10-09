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
# # f4g · The dual view: Lagrangian bound, cutting planes and stabilisation
#
# **Learning question:** the floors of step 14 come from a line slid down
# under the curves. What is that line in the language of optimisation, why is
# column generation the same thing as a cutting-plane method, and does a
# standard trick against its wobbling help on the course's own problems?
#
# Used in: self-study steps 14 and 15 (optional), after step 13. Written for readers from
# operations research; materials readers are welcome, and every idea is also
# said in the words of the g–x plot.
#
# **Learning goals.** After this notebook you can
#
# 1. write the dual function $d(\Delta\mu)$ of the melting lens, say why every
#    value is a floor, and find its highest point;
# 2. show that every floor of step 14 is one value of $d$;
# 3. see column generation as Kelley's cutting-plane method on $d$, and name
#    the duality gap of the problem "the sample stays one homogeneous state";
# 4. run plain column generation and a box-step variant on the regular solution
#    of steps 15–17 and compare their rounds honestly.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | The dual function | main | 15 min |
# | 2 | Floors are dual values | main | 10 min |
# | 3 | Column generation is a cutting-plane method | main | 15 min |
# | 4 | Why the floor wobbles, and a box step | dive deeper | 20 min |
# | 5 | Exercises | both | 20 min |
# | 6 | Limits | — | 3 min |
#
# **What you need.** Steps 10–14 (the menu, its line, the gap curve, column
# generation, ceiling and floor), or notebooks f4c and f4d. Section 4 uses the
# regular solution of steps 15–17 (notebook f4e).
#
# **Coming from operations research.** Here is the dictionary. The master of
# step 10 is a restricted master problem with two equality rows (amounts add to
# 1, B atoms add to $z$); its multipliers are $\mu_A$ and $\Delta\mu$. Pricing
# is the Lagrangian subproblem, which has a formula for the ideal phases; the floor is the
# Lagrangian bound.
#
# **Coming from materials.** $\mu_A$ and $\Delta\mu=\mu_B-\mu_A$ describe the
# straight line under the curves: its height at $x=0$ and its slope. "Dual" just
# means: look at the lines, not at the mixtures.
#
# **What is invented.** Both models are the course's invented teaching
# models (the melting lens of step 03 part C and the regular solution of step 03
# part B). No published database is used.
#
# **How to work.** Run the cells from top to bottom. In each "Your turn" cell,
# replace `None` with your value and run it: `check` says whether you match,
# without showing the answer. Cells marked *After your attempt* hold worked
# solutions.

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
# Leave these as they are for the first run: the "Your turn" checks expect
# them. Later, change one number at a time and rerun everything below it.
#
# - `T_LENS`, `Z_LENS`, `MENU_X`: the melting lens at 1400 K, the sample's
#   overall B atom fraction 0.40, and the dots of step 10's menu (the same five
#   compositions for SOLID and for LIQUID, ten dots in all);
# - `T_REG`, `Z_REG`: the regular solution of steps 15–17 at 800 K and
#   $z=0.15$ ($\Omega=20000$ J/mol is fixed in the course model);
# - `TOL`: stop when ceiling minus best floor is at most this, J/mol atoms;
# - `BOX`: the half-width of the box in section 4, J/mol.

# %%
T_LENS, Z_LENS = 1400.0, 0.40           # K; overall B atom fraction
MENU_X = [0.1, 0.3, 0.5, 0.7, 0.9]      # step 10's menu, for both phase models
T_REG, Z_REG = 800.0, 0.15              # K; overall B atom fraction
TOL = 1e-3                              # J/mol atoms
BOX = 1000.0                            # J/mol, half-width of the box on Δμ
DEFAULTS = (T_LENS, Z_LENS, MENU_X, T_REG, Z_REG, TOL, BOX) == (1400.0, 0.40, [0.1, 0.3, 0.5, 0.7, 0.9], 800.0, 0.15, 1e-3, 1000.0)

# %% [markdown]
# `day3_core` is the small library behind every number on the advanced steps:
# the phase models (`lens_models`, `regular_models`), the master
# (`solve_master`), the pricing step (`deepest`, closed form for ideal phases,
# a full scan for the regular solution) and the loop (`column_generation`).
# Nothing is re-derived here; we only look at the same numbers from the side of
# the lines.

# %%
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog, minimize_scalar
from course.self_study import day3_core as d
from course.self_study import two_phase_export as tp

SOLID_C, LIQUID_C, LINE_C, DIP_C = "#2445c4", "#cf4418", "#8f6400", "#6b6b6b"   # the website's colours
COLOUR = {"SOLID": SOLID_C, "LIQUID": LIQUID_C}
lens = d.lens_models(T_LENS)            # {'SOLID': model, 'LIQUID': model}; model.g(x) in J/mol atoms

# %% [markdown]
# ## 1. The dual function (main track, 15 min)
#
# Fix a slope $\Delta\mu$ and ask: how high can a straight line of that slope
# sit while staying on or below both curves everywhere? Its height at $x=0$ is
#
# $$\mu_A(\Delta\mu)=\min_{p,\;x}\,\bigl[g_p(x)-\Delta\mu\,x\bigr],$$
#
# the lowest point of "curve minus a line of slope $\Delta\mu$", over both phase models $p$
# and all compositions $x$. Read that line at the sample's composition $z$:
#
# $$d(\Delta\mu)=\mu_A(\Delta\mu)+\Delta\mu\,z .$$
#
# **In materials words:** $d(\Delta\mu)$ is the height at $z$ of the lowest line of
# slope $\Delta\mu$ that touches the curves. **In optimisation words:** it is the
# *Lagrangian dual function*. A *Lagrangian* moves a hard rule (here: the B atoms
# must add up to $z$) into the objective with a price $\Delta\mu$; minimising
# what is left gives $d(\Delta\mu)$, and the *dual* problem is to choose the
# price that makes this as high as possible.
#
# Three facts, each one line of reasoning:
#
# - **Every value is a floor** (weak duality). Any mixture that makes the sample
#   has energy $\sum_j f_j g_j \ge \sum_j f_j(\mu_A+\Delta\mu\,x_j)=\mu_A+\Delta\mu\,z$,
#   because every state lies on or above the line, $\sum f_j=1$ and $\sum f_jx_j=z$.
# - **$d$ is concave.** For each state $(p,x)$, $g_p(x)+\Delta\mu\,(z-x)$ is a
#   straight line in $\Delta\mu$; $d$ is the lowest of all of them, so it bends down.
# - **Its highest value is the answer** (strong duality here). The best line is
#   the common tangent, and its height at $z$ is the convex envelope of the curves
#   at $z$: the equilibrium energy of step 03.
#
# The pricing step of step 13 already computes $\mu_A(\Delta\mu)$: it is the
# deepest dip of the gap curve against a line of height 0 at $x=0$. So `dual` is two lines.

# %%
def dual(models, z, d_mu):
    """d(Δμ) and the touching state: price against the line of slope Δμ and height 0, then read at z."""
    best, _ = d.deepest(models, 0.0, d_mu)        # best.depth = min over p, x of g_p(x) - Δμ x
    return best.depth + d_mu * z, best

for slope in (-3000.0, -1000.0, 0.0):
    value, touch = dual(lens, Z_LENS, slope)
    print(f"Δμ = {slope:7.1f} J/mol:  d = {value:10.2f} J/mol atoms   (touches {touch.phase} at x = {touch.x:.4f})")

# %% [markdown]
# Now the highest point. SciPy's bounded search for the maximum of a concave
# function of one variable is enough. Two independent checks follow: the
# common tangent from the closed-form coexistence of step 03 part C
# (`two_phase_export.lens_coexistence`), and the converged column generation of
# step 13.

# %%
best = minimize_scalar(lambda s: -dual(lens, Z_LENS, s)[0], bounds=(-4000.0, 0.0), method="bounded",
                       options={"xatol": 1e-9})
d_mu_star, d_star = float(best.x), -float(best.fun)
mu_A_star = d_star - d_mu_star * Z_LENS
print(f"highest point of d: Δμ* = {d_mu_star:.2f} J/mol, μA* = {mu_A_star:.2f} J/mol, d(Δμ*) = {d_star:.4f} J/mol atoms")

x_S, x_L = tp.lens_coexistence(T_LENS)              # the touching compositions of the common tangent
f_S, f_L = (Z_LENS - x_L) / (x_S - x_L), (x_S - Z_LENS) / (x_S - x_L)   # lever rule
G_tangent = f_S * float(lens["SOLID"].g(x_S)) + f_L * float(lens["LIQUID"].g(x_L))
history = d.column_generation(lens, d.menu_states(lens, MENU_X), Z_LENS, tol=1e-9, max_iter=40)
G_cg = history[-1].master.G_up
print(f"common tangent touches LIQUID at x_L = {x_L:.4f} and SOLID at x_S = {x_S:.4f}")
print(f"lever rule on the common tangent: {G_tangent:.4f};  converged column generation: {G_cg:.4f}")
if DEFAULTS:
    confirm(d_star, -20473.1242, "The highest value of d (the lens answer of step 03)", tol=1e-4)
    confirm(d_mu_star, -1782.77, "The slope of the common tangent", tol=0.01)
    confirm(mu_A_star, -19760.02, "Its height at x = 0", tol=0.01)
assert abs(d_star - G_tangent) < 1e-6 and abs(d_star - G_cg) < 1e-6, "the highest value of d is not the answer"

# %% [markdown]
# A picture of both views. Left: the g–x plot with every energy measured from
# the common tangent, so the tangent is the axis and both curves touch it at
# $x_L=0.3124$ and $x_S=0.4405$. Three lines of other slopes each touch the curves from below;
# where they cross $z$ is their value of $d$. Right: $d(\Delta\mu)$ itself, with the
# same three points. All lie below the answer; the top is the answer.

# %%
def tangent(x):
    return mu_A_star + d_mu_star * np.asarray(x)        # the common tangent, used as zero

xs = np.linspace(0.2, 0.6, 801)
slopes = [-2400.0, d_mu_star, -1389.0]
fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.6))
for phase, model in lens.items():
    left.plot(xs, model.g(xs) - tangent(xs), color=COLOUR[phase], label=phase)
for s, ls in zip(slopes, (":", "-", "--")):
    value, touch = dual(lens, Z_LENS, s)
    left.plot(xs, value + s * (xs - Z_LENS) - tangent(xs), color=LINE_C, ls=ls, lw=1, label=f"Δμ = {s:.0f}")
    left.plot(Z_LENS, value - d_star, "o", color=LINE_C)
left.axvline(Z_LENS, color=DIP_C, lw=0.6)
left.set(xlim=(0.2, 0.6), ylim=(-70, 60), xlabel="B atom fraction x",
         ylabel="g − common tangent (J/mol atoms)", title="Lowest lines of three slopes")
left.legend(fontsize=8)
grid = np.linspace(-4000.0, 0.0, 401)
right.plot(grid, [dual(lens, Z_LENS, s)[0] for s in grid], color=LINE_C)
for s in slopes:
    right.plot(s, dual(lens, Z_LENS, s)[0], "o", color=LINE_C)
right.axhline(d_star, color=DIP_C, lw=0.6)
right.set(xlabel="Δμ = μB − μA (J/mol)", ylabel="d(Δμ) (J/mol atoms)", ylim=(-20700, -20450),
          title="The dual function: every value is a floor")
plt.tight_layout(); plt.show()

# %% [markdown]
# **Why the top sits at a kink.** Change $\Delta\mu$ a little and the touching
# state $x^*(\Delta\mu)$ stays put to first order, so the slope of $d$ is $z-x^*(\Delta\mu)$:
# how far the touching state is from the sample. When one SOLID state
# touches ($x^*>z$), $d$ falls as $\Delta\mu$ grows; when one LIQUID state touches
# ($x^*<z$), it rises. At the top both touch, the slope jumps from
# $z-x_L>0$ to $z-x_S<0$, and the lever rule is the statement that the amounts
# $f_L,f_S$ average these two slopes to zero.

# %%
print(f"slopes on the two sides of the top: z - x_L = {Z_LENS - x_L:+.4f}, z - x_S = {Z_LENS - x_S:+.4f}")
print(f"lever-rule average f_L (z - x_L) + f_S (z - x_S) = {f_L * (Z_LENS - x_L) + f_S * (Z_LENS - x_S):.1e}")
grid_values = np.array([dual(lens, Z_LENS, s)[0] for s in grid])
assert np.all(grid_values <= d_star + 1e-9), "a value of d lies above the answer (weak duality broken)"
assert np.all(np.diff(grid_values, 2) <= 1e-6), "d is not concave on the grid"
print(f"all {grid.size} grid values lie at or below {d_star:.4f}, and d bends down")

# %% [markdown]
# ### Your turn: the value of $d$ at step 10's slope
#
# Step 10's menu gave the line $\mu_A=-19873.9$, $\Delta\mu=-1389.0$ J/mol and the
# ceiling $-20429.54$. Use `dual` (or the formula of notebook f4d for the
# touching state) to find $d(-1389.0)$, to two decimals.

# %%
d_menu = None    # J/mol atoms
check(d_menu, "f4g_dual_menu_slope")

# %% cellView="form"
#@title After your attempt: d at step 10's slope
value, touch = dual(lens, Z_LENS, -1389.0)
print(f"d(-1389.0) = {value:.2f} J/mol atoms; the lowest line of that slope touches {touch.phase} at x = {touch.x:.4f}")
if DEFAULTS:
    confirm(value, -20490.7222, "d at step 10's slope", tol=1e-3)

# %% [markdown]
# ## 2. Floors are dual values (main track, 10 min)
#
# Step 14's floor was "the line at $z$, lowered by the deepest dip":
# $G_{\text{low}}=\mu_A^{(k)}+\Delta\mu^{(k)}z+\text{dip}_k$. The deepest dip is
# $\min_{p,x}[g_p(x)-\mu_A^{(k)}-\Delta\mu^{(k)}x]=\mu_A(\Delta\mu^{(k)})-\mu_A^{(k)}$, so
# $\mu_A^{(k)}$ cancels:
#
# $$G_{\text{low}}^{(k)}=\mu_A(\Delta\mu^{(k)})+\Delta\mu^{(k)}z=d(\Delta\mu^{(k)}).$$
#
# The floor is the dual function at the master's slope. The master's height
# $\mu_A^{(k)}$ does not matter for the floor; only its slope does. Since the
# master's line passes through the ceiling at $z$, the floor is also
# ceiling + deepest dip.

# %%
print(" round   μA (J/mol)   Δμ (J/mol)    ceiling      deepest dip    floor (step 14)    d(Δμ)")
for it in history[:4]:
    m = it.master
    value, _ = dual(lens, Z_LENS, m.d_mu)
    if it.k == 2:      # round 2 is your turn below: only its slope is shown
        print(f"{it.k:5d}  {'':10s}  {m.d_mu:10.2f}  {'(your turn)':>11s}")
    else:
        print(f"{it.k:5d}  {m.mu_A:10.1f}  {m.d_mu:10.2f}  {m.G_up:11.2f}  {it.best.depth:12.4f}  {it.G_low_raw:15.4f}  {value:11.4f}")
    assert abs(it.G_low_raw - value) < 1e-8, f"round {it.k}: the floor is not d at the master's slope"
    assert abs(it.G_low_raw - (m.G_up + it.best.depth)) < 1e-8, f"round {it.k}: floor is not ceiling + dip"
if DEFAULTS:
    for it, up, dip in zip(history, (-20429.54, -20470.64, -20472.07, -20473.12), (-61.18, -3.99, -1.55, -0.0027)):
        confirm(it.master.G_up, up, f"Round {it.k} ceiling", tol=0.006)
        confirm(it.best.depth, dip, f"Round {it.k} deepest dip", tol=0.006)

# %% [markdown]
# ### Your turn: the round-2 floor as a dual value
#
# Round 2's master has the slope printed in the table, $\Delta\mu^{(2)}=-1770.76$ J/mol.
# Compute $d(\Delta\mu^{(2)})$ with `dual`, using the master's slope
# `history[2].master.d_mu`, to two decimals.

# %%
floor_round2 = None   # J/mol atoms
check(floor_round2, "f4g_floor_round2")

# %% cellView="form"
#@title After your attempt: round 2
value, touch = dual(lens, Z_LENS, history[2].master.d_mu)
print(f"d(Δμ2) = {value:.4f} J/mol atoms (touches {touch.phase} at {touch.x:.4f}); step 14's floor {history[2].G_low_raw:.4f}")
if DEFAULTS:
    confirm(value, -20473.6125, "The round-2 floor", tol=1e-3)

# %% [markdown]
# ## 3. Column generation is a cutting-plane method (main track, 15 min)
#
# Each state $j$ on the menu gives one straight line in $\Delta\mu$, a *cut*:
#
# $$c_j(\Delta\mu)=g_j+\Delta\mu\,(z-x_j)\ \ge\ d(\Delta\mu)\quad\text{for every }\Delta\mu .$$
#
# The lowest of the menu's cuts, $m(\Delta\mu)=\min_j c_j(\Delta\mu)$, is a
# piecewise-straight *model* of $d$ from above. Maximising it is a small LP in
# $(\mu_A,\Delta\mu)$: make $\mu_A+\Delta\mu\,z$ as large as possible while
# $\mu_A+\Delta\mu\,x_j\le g_j$ for every menu state. That is the dual of the
# master, so its maximum is the ceiling and its maximiser is the master's slope.
#
# Then pricing at that slope finds the touching state $x^*$, whose cut touches
# $d$ exactly there; adding $x^*$ to the menu adds that cut, and the model gets lower
# where it was too high. This loop (maximise a cutting-plane model, evaluate the
# function and its slope there, add the new cut) is *Kelley's cutting-plane
# method* (Kelley 1960). Column generation on the master is Kelley's method on
# $d$, written from the other side.
#
# The next cell solves the model's LP directly, without the master's
# multipliers, and compares.

# %%
def kelley_step(states, z, lo=None, hi=None):
    """Maximise the cut model min_j [g_j + Δμ (z - x_j)], with Δμ kept in [lo, hi] if given.

    Variables (μA, Δμ): maximise μA + Δμ z subject to μA + Δμ x_j <= g_j.
    Returns (Δμ, model value).
    """
    A = [[1.0, s.x] for s in states]
    b = [s.g for s in states]
    r = linprog([-1.0, -z], A_ub=A, b_ub=b, bounds=[(None, None), (lo, hi)], method="highs-ds")
    return float(r.x[1]), -float(r.fun)

print(" round   model maximiser   master's Δμ     model maximum    ceiling")
for it in history[:4]:
    s_k, top = kelley_step(it.master.states, Z_LENS)
    print(f"{it.k:5d}  {s_k:15.4f}  {it.master.d_mu:12.4f}  {top:15.4f}  {it.master.G_up:11.4f}")
    assert abs(s_k - it.master.d_mu) < 1e-6 and abs(top - it.master.G_up) < 1e-6, f"round {it.k}: model and master differ"
    new = it.best                                  # the state pricing adds after this round
    cut_at_k = float(lens[new.phase].g(new.x)) + it.master.d_mu * (Z_LENS - new.x)
    assert abs(cut_at_k - it.G_low_raw) < 1e-8, "the new cut does not touch d at the master's slope"
print("the model's maximiser is the master's slope, its maximum the ceiling; each new cut touches d there")

# %% [markdown]
# The picture: $d$ (solid) and the cut model of rounds 0–3 (dashed). Each round
# adds one cut and the model drops onto $d$ near its top. The dots are the
# ceilings (model maxima); the crosses directly below them are the floors $d(\Delta\mu^{(k)})$.

# %%
grid3 = np.linspace(-2300.0, -1100.0, 241)
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(grid3, [dual(lens, Z_LENS, s)[0] for s in grid3], color="black", lw=1.5, label="d(Δμ)")
for it, shade in zip(history[:4], ("#c9d2f2", "#8fa0e0", "#5a6fcf", SOLID_C)):
    states = it.master.states
    model_vals = [min(st.g + s * (Z_LENS - st.x) for st in states) for s in grid3]
    ax.plot(grid3, model_vals, ls="--", color=shade, label=f"model, round {it.k}")
    ax.plot(it.master.d_mu, it.master.G_up, "o", color=shade)
    ax.plot(it.master.d_mu, it.G_low_raw, "x", color=shade)
ax.set(xlabel="Δμ (J/mol)", ylabel="J/mol atoms", ylim=(-20500, -20420), title="Kelley's model of d, round by round")
ax.legend(fontsize=8); plt.show()

# %% [markdown]
# **The duality gap of the one-state problem.** Take the harder-looking
# problem "the sample stays one homogeneous state": choose one phase model $p$
# and $x=z$, at the lowest $g_p(z)$. Pricing the rule $x=z$ with $\Delta\mu$ gives
# exactly the same $d(\Delta\mu)$ as above. But now the best single state is
# higher than the top of $d$: the difference is the *duality gap* (not step 14's
# remaining uncertainty, which is ceiling minus floor of one run), and here it
# has a physical name, the energy gained by splitting into two phases. A
# Lagrangian dual cannot see whether a mixture is allowed; it always answers
# for the mixture problem (its convex envelope).
#
# For SOLID alone the curve is convex (ideal mixing bends up everywhere), so
# its own dual has no gap: the best line of slope $g_S'(z)$ touches at $z$.

# %% [markdown]
# A single phase model with a hump does have a gap of its own: the regular
# solution of step 15 at $z=0.15$. Its curve at $0.15$ lies above the common
# tangent of 0.070 and 0.930 (the coexisting compositions of `binary_family`).

# %%
from course.foundations import binary_family as bf
alpha = d.regular_models(T_REG)["ALPHA"]
x_a, x_b = bf.regular_binodal(T_REG)["compositions"]
G_reg = float(alpha.g(x_a)) + (Z_REG - x_a) / (x_b - x_a) * float(alpha.g(x_b) - alpha.g(x_a))
print(f"g(0.15) = {float(alpha.g(Z_REG)):.2f}, convex envelope {G_reg:.4f}, gap {float(alpha.g(Z_REG)) - G_reg:.2f} J/mol atoms")

# %% [markdown]
# ### Your turn: the duality gap at 0.40
#
# For the lens at $z=0.40$, what is the duality gap of the one-state problem:
# the best single homogeneous state minus the top of $d$?

# %%
gap_one_state = None   # J/mol atoms, positive
check(gap_one_state, "f4g_onestate_gap")

# %% cellView="form"
#@title After your attempt: the duality gap
g_S, g_L = float(lens["SOLID"].g(Z_LENS)), float(lens["LIQUID"].g(Z_LENS))
one_state = min(g_S, g_L)
print(f"one homogeneous state at z: SOLID {g_S:.4f}, LIQUID {g_L:.4f}  ->  best {one_state:.4f} J/mol atoms")
print(f"top of d {d_star:.4f}  ->  duality gap (phase-separation gain) {one_state - d_star:.4f} J/mol atoms")
solid_only = {"SOLID": lens["SOLID"]}
own = dual(solid_only, Z_LENS, float(lens["SOLID"].slope(Z_LENS)))[0]
print(f"SOLID alone: g_S(z) = {g_S:.4f}, its dual at the tangent slope {own:.4f}, gap {g_S - own:.1e}")
assert abs(g_S - own) < 1e-8, "SOLID alone should have no duality gap"
if DEFAULTS:
    confirm(g_S - d_star, 39.0665, "The one-state duality gap at 0.40", tol=1e-3)

# %% [markdown]
# ## 4. Why the floor wobbles, and a box step (dive deeper, 20 min)
#
# Kelley's method jumps to the top of the current model. Where the model has
# few cuts, its top can be far from the top of $d$, or not unique at all. Then
# the next slope is far off, and the raw floor $d(\Delta\mu^{(k)})$ can fall
# even though the ceiling never rises. Notebook f4d showed this for the lens
# started from the two pure ends; the slopes tell why. (Round counts here stop
# at a remaining uncertainty of `TOL`; f4d runs that start to 1e-9, so it
# counts more rounds.)

# %%
from_ends = d.column_generation(lens, d.menu_states(lens, [0.0, 1.0]), Z_LENS, tol=TOL, max_iter=40)
for it in from_ends:
    print(f"round {it.k}: Δμ {it.master.d_mu:9.1f}   raw floor {it.G_low_raw:10.2f}   ceiling {it.master.G_up:10.2f}")

# %% [markdown]
# The slope swings from $+3400$ to $-9169$ and back before it settles near
# $-1783$; each swing to a far slope gives a low raw floor.
#
# **The regular solution of steps 15–17.** The course's local–global rounds
# start from the single state at $z=0.15$. Round 0 uses the tangent at 0.15
# (chosen by hand, as on step 15). After the state near 0.958 is added, the menu
# still has nothing left of 0.15, so the only mixture is the 0.15 state itself,
# and every slope up to that of the line through both dots is an equally good
# top of the model: the master is degenerate. The solver returns the flat line,
# $\Delta\mu=0$.

# %%
reg = {"ALPHA": alpha}
d_mu_t = float(alpha.slope(Z_REG)); g_z = float(alpha.g(Z_REG)); mu_A_t = g_z - d_mu_t * Z_REG
seed = [d.State("ALPHA", Z_REG, g_z)]
plain = d.column_generation(reg, seed, Z_REG, tol=TOL, max_iter=40,
                            line=lambda master, k: (mu_A_t, d_mu_t) if k == 0 else (master.mu_A, master.d_mu))
for it in plain:
    print(f"round {it.k}: Δμ {it.master.d_mu + 0.0:9.1f}   deepest dip {it.best.depth:10.4f} at {it.best.x:.4f}"
          f"   raw floor {it.G_low_raw:9.2f}   ceiling {it.master.G_up:9.2f}   remaining {it.gap:.2e}")
two = plain[1].master.states
slope_two = (two[1].g - two[0].g) / (two[1].x - two[0].x)
flat = [min(st.g + s * (Z_REG - st.x) for st in two) for s in (0.0, slope_two / 2, slope_two)]
print(f"round 1 model top: {flat[0]:.2f} at Δμ = 0, {flat[1]:.2f} at {slope_two / 2:.0f}, {flat[2]:.2f} at {slope_two:.0f}: flat")
if DEFAULTS:
    confirm(plain[1].master.d_mu, 0.0, "Round 1 slope (the flat line)", tol=1e-9)
    confirm(plain[1].best.depth, -1593.6, "Round 1 deepest dip", tol=0.05)
    confirm(plain[1].best.x, 0.0085, "Where it lies", tol=5e-5)

# %% [markdown]
# On this problem the raw floor happens not to fall, but the slope of round 1
# is a whole $12000$ J/mol away from the answer: the common tangent of the
# regular solution has slope $\Delta\mu=12000$ J/mol at 800 K, the rise of its
# end line, because the rest of the model is symmetric about $x=0.5$.

# %%
print(f"slope of the common tangent: {float(alpha.slope(x_a)):.4f} J/mol at x = {x_a:.4f} and"
      f" {float(alpha.slope(x_b)):.4f} at x = {x_b:.4f}; end-line rise b = {alpha.b:.0f} J/mol")

# %% [markdown]
# **A box step.** The classic remedy is stabilisation: keep the next slope near
# a trusted one. We implement this simple variant of the box step of
# Marsten, Hogan and Blankenship (1975):
#
# 1. keep a centre $\Delta\mu_c$: the slope with the highest dual value $d$ so far
#    (round 0: the tangent at 0.15, as in the plain run);
# 2. each round, maximise the cut model only over $[\Delta\mu_c-\delta,\ \Delta\mu_c+\delta]$
#    (`kelley_step` with bounds), with $\delta$ = `BOX`;
# 3. price at that slope with the same full-scan pricer as the plain run, and add the touching state;
# 4. move the centre there if its $d$ is higher than the centre's;
# 5. the ceiling is always the unboxed master's best mixture (`solve_master`),
#    the floor the best $d$ so far; stop when ceiling minus floor is at most `TOL`.
#
# The box does not change what is proved: every $d$ is a floor and every
# ceiling a real mixture, whatever slopes are tried.

# %%
def box_step(models, seed, z, first_slope, delta, tol=TOL, max_rounds=80):
    """Box-stabilised column generation; returns one row per round."""
    states, centre, best, rows = list(seed), first_slope, -math.inf, []
    for k in range(max_rounds):
        slope = first_slope if k == 0 else kelley_step(states, z, centre - delta, centre + delta)[0]
        value, touch = dual(models, z, slope)         # exact pricing at the chosen slope
        if value > best:
            best, centre = value, slope
        ceiling = d.solve_master(states, z).G_up
        rows.append({"k": k, "slope": slope, "d": value, "ceiling": ceiling, "remaining": ceiling - best})
        if ceiling - best <= tol:
            break
        states.append(d.State(touch.phase, touch.x, float(models[touch.phase].g(touch.x))))
    return rows

boxed = box_step(reg, seed, Z_REG, d_mu_t, BOX)
for r in boxed:
    print(f"round {r['k']}: Δμ {r['slope']:9.1f}   d {r['d']:9.2f}   ceiling {r['ceiling']:9.2f}   remaining {r['remaining']:.2e}")
print(f"rounds to remaining <= {TOL} J/mol atoms: plain {plain[-1].k}, box step (δ = {BOX:.0f} J/mol) {boxed[-1]['k']}")

# %% [markdown]
# Before reading the comparison, **predict**: does a narrower box help or hurt
# here? The next cell runs several box widths.

# %%
widths = [250.0, 500.0, 1000.0, 2000.0, 5000.0]
counts = {w: box_step(reg, seed, Z_REG, d_mu_t, w)[-1]["k"] for w in widths}
print("rounds, plain column generation:", plain[-1].k)
for w, n in counts.items():
    print(f"rounds, box step δ = {w:6.0f} J/mol: {n}")
if DEFAULTS:
    confirm(plain[-1].k, 6, "Rounds of the plain run", tol=0)
    confirm(boxed[-1]["k"], 6, "Rounds of the box step with δ = 1000 J/mol", tol=0)

# %%
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.4))
a1.plot([it.k for it in plain], [it.master.d_mu for it in plain], "o-", color=LINE_C, label="plain")
a1.plot([r["k"] for r in boxed], [r["slope"] for r in boxed], "s--", color=SOLID_C, label=f"box δ = {BOX:.0f}")
a1.axhline(12000.0, color=DIP_C, lw=0.6)
a1.set(xlabel="round", ylabel="Δμ tried (J/mol)", title="The slope, round by round"); a1.legend()
a2.semilogy([it.k for it in plain], [it.gap for it in plain], "o-", color=LINE_C, label="plain")
a2.semilogy([r["k"] for r in boxed], [r["remaining"] for r in boxed], "s--", color=SOLID_C, label=f"box δ = {BOX:.0f}")
a2.set(xlabel="round", ylabel="ceiling − best floor (J/mol atoms)", title="Remaining uncertainty"); a2.legend()
plt.tight_layout(); plt.show()

# %% [markdown]
# **What this shows, honestly.** The box removes the jump to $\Delta\mu=0$: its
# slopes walk from 14462 towards 12000 in steps of at most $\delta$. But the
# plain run needs only six rounds, and the box step with $\delta=1000$ J/mol needs six as well.
# A narrow box (250 or 500 J/mol) costs more rounds, because the slope has to
# walk the whole way from the tangent at 0.15; wider boxes save at most one
# round here. The box's own model also has flat tops, and which point of a flat
# top the LP solver returns can change a count by one. No width is best in
# advance, and on this problem stabilisation does not pay off clearly.
#
# The reason is the size of the problem. The dual has one variable, the pricing
# is exact, and two or three good cuts already pin the top of a concave function
# of one variable. Stabilisation pays off where the dual has many variables (many
# elements, many rows), the master is degenerate round after round, and pricing
# is expensive: there Kelley's jumps cause long tails. Our problems are too small
# to show that.
#
# ## 5. Exercises (both tracks, 20 min)
#
# **Exercise 1 (main).** The Lagrangian bound for a given slope: give
# $d(-2000)$ for the lens at $z=0.40$, to two decimals. Use the closed form for
# the touching state of each phase, $x^*=1/(1+e^{-(\Delta\mu-b)/RT})$ with $b$ the
# rise of each model's end line (`lens[p].b`), or `dual`.

# %%
bound_2000 = None   # J/mol atoms
check(bound_2000, "f4g_bound_slope_2000")

# %% [markdown]
# **Exercise 2 (main).** The slope of $d$ at $\Delta\mu=-1389.0$ is $z-x^*$, with $x^*$ the
# touching state. Give it to four decimals. Does $d$ rise or fall if $\Delta\mu$ is
# made a little larger?

# %%
slope_of_d = None   # (B atom fraction, no unit)
check(slope_of_d, "f4g_slope_of_d")

# %% [markdown]
# **Exercise 3 (main).** Run the box step of section 4 on the regular solution
# with $\delta=750$ J/mol (`box_step(reg, seed, Z_REG, d_mu_t, 750.0)`). How many
# rounds does it need until ceiling minus best floor is at most `TOL`? Is that
# more or fewer than the plain run?

# %%
box750_rounds = None   # a whole number
check(box750_rounds, "f4g_box750_rounds")

# %% cellView="form"
#@title After your attempt: exercises 1–3
RT = d.R * T_LENS
for p, model in lens.items():
    x_star = 1 / (1 + math.exp(-(-2000.0 - model.b) / RT))
    print(f"{p:6s}: touching state x* = {x_star:.4f}, g - Δμ x = {float(model.g(x_star)) + 2000.0 * x_star:.2f}")
value, touch = dual(lens, Z_LENS, -2000.0)
print(f"d(-2000) = {value:.2f} J/mol atoms (the lower of the two, plus Δμ z)")
_, touch_menu = dual(lens, Z_LENS, -1389.0)
print(f"slope of d at -1389.0: z - x* = {Z_LENS - touch_menu.x:.4f} (negative: d falls as Δμ grows)")
numeric = (dual(lens, Z_LENS, -1389.0 + 1e-3)[0] - dual(lens, Z_LENS, -1389.0 - 1e-3)[0]) / 2e-3
box750 = box_step(reg, seed, Z_REG, d_mu_t, 750.0)[-1]["k"]
print(f"numerical slope {numeric:.4f};  box step δ = 750 J/mol: {box750} rounds (plain: {plain[-1].k})")
if DEFAULTS:
    confirm(box750, 7, "Rounds of the box step with δ = 750 J/mol", tol=0)
    confirm(value, -20492.5859, "d(-2000)", tol=1e-3)
    confirm(Z_LENS - touch_menu.x, -0.04887, "The slope of d at step 10's slope", tol=1e-5)
assert abs(numeric - (Z_LENS - touch_menu.x)) < 1e-5, "the slope of d is not z - x*"

# %% [markdown]
# **Exercise 4 (dive deeper).** Run `box_step` on the lens started from the two
# pure ends (`d.menu_states(lens, [0.0, 1.0])`, first slope from its master,
# $\Delta\mu=3400$) with $\delta=1000$ J/mol. Compare the rounds with the plain
# run of section 4 (`from_ends`), and look at the slopes tried.
#
# **Exercise 5 (dive deeper).** Implement Wentges smoothing (Wentges 1997) instead of the box:
# price at $\alpha\,\Delta\mu_c+(1-\alpha)\,\Delta\mu^{(k)}$ with $\alpha=0.5$, where
# $\Delta\mu^{(k)}$ is the master's slope and $\Delta\mu_c$ the centre as above. On the
# regular solution, count the rounds to `TOL`.

# %% cellView="form"
#@title After your attempt: exercises 4 and 5
ends = d.menu_states(lens, [0.0, 1.0])
lens_box = box_step(lens, ends, Z_LENS, d.solve_master(ends, Z_LENS).d_mu, 1000.0)
print(f"lens from the pure ends: plain {from_ends[-1].k} rounds, box δ = 1000: {lens_box[-1]['k']} rounds")
print("box slopes:", [round(r["slope"]) for r in lens_box])

def wentges(models, seed, z, first_slope, a, tol=TOL, max_rounds=80):
    states, centre, best = list(seed), first_slope, -math.inf
    for k in range(max_rounds):
        master = d.solve_master(states, z)
        slope = first_slope if k == 0 else a * centre + (1 - a) * master.d_mu
        value, touch = dual(models, z, slope)
        if value > best:
            best, centre = value, slope
        if master.G_up - best <= tol:
            return k
        if all(abs(s.x - touch.x) > 1e-12 for s in states):   # a repeated state adds nothing
            states.append(d.State(touch.phase, touch.x, float(models[touch.phase].g(touch.x))))
    return None

print(f"regular solution: plain {plain[-1].k} rounds, Wentges α = 0.5: {wentges(reg, seed, Z_REG, d_mu_t, 0.5)} rounds")

# %% [markdown]
# *After your attempt.* From the pure ends the box walks from $+3400$ down in
# steps of 1000 J/mol and needs more rounds than the plain run, whose wild swings
# happen to land useful cuts. With a fixed $\alpha=0.5$ every round prices
# halfway between the centre and the master's slope, never at the master's slope
# itself; near the end the centre moves only when the halfway slope beats it, so
# the remaining uncertainty shrinks by about half per round and the last digits
# come slowly. Practical codes change $\alpha$ as they go. Neither result says
# stabilisation is useless, only that these one-variable problems do not need it.
#
# ## 6. Limits
#
# - One composition variable: the dual has a single slope $\Delta\mu$ (plus the
#   height $\mu_A$, which drops out). With more elements the dual has more
#   variables, the model of $d$ more facets, and the picture of section 3 does
#   not carry over directly.
# - Exact pricing is available here: a formula for the ideal lens and a full
#   scan of one variable for the regular solution. Where pricing is only
#   approximate, a "floor" is a floor only if the deepest dip is truly found.
# - Teaching scale: two invented models, a handful of rounds. The round counts
#   of section 4 are for these problems only and say nothing about solver speed
#   in general.
# - Floating point: all comparisons use small tolerances; nothing here is a
#   rigorous numerical certificate.
#
# ## Recap
#
# - $d(\Delta\mu)$ is the height at $z$ of the lowest line of slope $\Delta\mu$;
#   it is concave, every value is a floor, and its top is the equilibrium energy
#   (−20473.1242 J/mol atoms at $\Delta\mu=-1782.77$ J/mol for the lens).
# - Step 14's floor in every round is $d$ at the master's slope.
# - Column generation is Kelley's cutting-plane method on $d$: the master's
#   dual maximises the cut model, the ceiling is its maximum, pricing adds the
#   cut that touches $d$.
# - The one-state problem has a duality gap: the phase-separation gain,
#   39.07 J/mol atoms for the lens at 0.40.
# - A box step keeps the slopes calm; on these one-variable problems it does not
#   clearly save rounds.
#
# **On the website:** steps 13 (find a missing state), 14 (ceiling, floor and
# the remaining uncertainty) and 15 (local search can miss a valley).
