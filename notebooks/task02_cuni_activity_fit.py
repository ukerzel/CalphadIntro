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
# # Task 02 · Two Cu–Ni interaction values from nine Ni activities
#
# **Learning question:** nine measured Ni activities at 1000 K are compared
# with the published Cu–Ni description. How do you adjust its two FCC
# interaction values to match them better, which points still disagree, and what
# can one temperature not tell you?
#
# Used in: Task 02 ([task text](../course/materials/cuni/fitting.md)). Do
# [f6](f6_fitting_synthetic.ipynb) first if residuals and least squares are new;
# without a database download, f6 alone covers the method.
#
# This notebook runs with or without the published Cu–Ni database. Without it,
# the pinned model's values at the nine compositions come from the saved run.
#
# **How this notebook works.** Run the cells from top to bottom (Shift + Enter).
# In each "Your turn" cell, replace `None` with your value and run the cell:
# `check(your_value, key)` (key: the name of the stored answer, in quotes) prints "✓ matches", "close" or "not yet" without
# showing the stored answer. The "After your attempt" cells use
# `confirm(value, expected, "what", tol=...)`, which prints a ✓ line when a
# calculation reproduces the lesson value within `tol` and stops with an error
# otherwise.
#
# The steps: read the measurements (1), write the model change as a linear
# formula (2), get the published model's predictions (3), fit two numbers by
# least squares (4), see what one temperature cannot decide (5), and name the
# result correctly (6).

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.3"
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
# ## 1. The data and their units
#
# S. Srikanth and K. T. Jacob, "Thermodynamic properties of Cu–Ni alloys:
# Measurements and assessment," *Mater. Sci. Technol.* 5 (1989) 427–434,
# [doi:10.1179/mst.1989.5.5.427](https://doi.org/10.1179/mst.1989.5.5.427),
# Table 1: Ni activity from EMF measurements at **1000 K**, $x_{Ni}$ = 0.1 … 0.9.
# The course file holds the reported numbers; there are no error bars per row.
#
# | Quantity | Unit / basis |
# |---|---|
# | $x_{Ni}$ | Ni atom fraction |
# | EMF | mV (as reported; not used in the fit) |
# | $a_{Ni}$ | dimensionless, relative to pure FCC Ni at 1000 K |
# | $RT\ln a_{Ni}$ | J/mol of atoms, with R = 8.3145 J/(mol K) |
#
# The fit compares $RT\ln a_{Ni}$, the Ni chemical potential relative to pure Ni,
# because the model changes are linear in it.
#
# **What an activity is.** The chemical potential $\mu_{Ni}$ is the Gibbs energy
# change per mole of Ni added to a large amount of alloy (J/mol). The activity
# compares it with pure Ni at the same temperature:
#
# $$RT\ln a_{Ni}=\mu_{Ni}-\mu^{\rm pure}_{Ni},\qquad\text{so}\qquad a_{Ni}=1 \text{ for pure Ni}.$$
#
# In an *ideal* solution $a_{Ni}=x_{Ni}$. Values below $x_{Ni}$ mean Ni is held
# more strongly in the alloy than in an ideal mix (negative deviation), values
# above mean it is held less strongly (positive deviation). Since $a<1$ in an
# alloy, $RT\ln a_{Ni}$ is negative.
#
# **Where the numbers come from.** In an EMF (electromotive force) measurement
# an electrochemical cell compares Ni in the alloy with pure Ni; its voltage $E$
# gives the chemical potential difference directly, $RT\ln a_{Ni}=-2FE$, with
# $F$ the Faraday constant and 2 the charge of a Ni²⁺ ion. The notebook uses the
# activities as reported.
#
# **The code.** `csv.DictReader` reads the table file row by row, each row as a
# dictionary keyed by the column names (all values arrive as text, hence
# `float(...)`). `np.array([...])` turns a Python list into a numpy array, so
# that `RT * np.log(a_obs)` acts on all nine numbers at once.

# %%
import csv
import json
from pathlib import Path

import numpy as np

T = 1000.0             # K
R = 8.3145             # J/(mol K), the value pycalphad uses
RT = R * T             # J/mol
DATA = Path("course/materials/cuni/srikanth_jacob1989_ni_activity.csv")

rows = list(csv.DictReader(DATA.open()))  # nine rows, each a dict {column name: text}
x = np.array([float(r["x_NI_mole_fraction"]) for r in rows])     # Ni atom fraction
a_obs = np.array([float(r["a_NI_dimensionless"]) for r in rows])  # Ni activity
mu_obs = RT * np.log(a_obs)                                       # J/mol of atoms
print(" x_Ni   EMF (mV)   a_Ni")
for r in rows:
    print(f" {float(r['x_NI_mole_fraction']):.1f}    {float(r['emf_mV']):5.1f}     {float(r['a_NI_dimensionless']):.4f}")
print("The fit uses RT ln a_Ni at each point (mu_obs, J/mol); work out the one at x = 0.5 yourself below.")

# %% [markdown]
# ## 2. The model being fitted
#
# The published description (S. an Mey, 1992) treats Cu–Ni FCC as one phase
# with Cu and Ni on one set of sites; a second "VA" sublattice is always empty
# and holds no atoms. At each measured composition we evaluate **homogeneous**
# FCC: one solution at that x, not an equilibrium mixture. With $x=x_{Ni}$ and
# $g(x)$ the molar Gibbs energy (J/mol of atoms),
#
# $$\mu_{Ni}=g+(1-x)\frac{dg}{dx},\qquad
# RT\ln a_{Ni}=\mu_{Ni}-g^{FCC}_{Ni}.$$
#
# **Why $\mu_{Ni}$ has this form (tangent construction).** For a binary,
# $g=(1-x)\,\mu_{Cu}+x\,\mu_{Ni}$, and the slope of the curve is
# $dg/dx=\mu_{Ni}-\mu_{Cu}$. Put the second into the first and solve for
# $\mu_{Ni}$: you get the formula above. In a picture: draw the tangent to
# $g(x)$ at the composition $x$; where it meets the line $x=1$ is $\mu_{Ni}$,
# where it meets $x=0$ is $\mu_{Cu}$. $g^{FCC}_{Ni}$ is the Gibbs energy of pure
# FCC Ni, i.e. $g$ at $x=1$.
#
# Pure-element, ideal and magnetic terms stay as published. Only the two
# interaction values at 1000 K, $L_0$ and $L_1$, are changed by $\delta L_0$ and
# $\delta L_1$. In the source's sign convention (order $x_{Cu}-x_{Ni}=1-2x$),
#
# $$\delta g=x(1-x)\,[\delta L_0+\delta L_1(1-2x)],$$
# $$\delta\mu_{Ni}=(1-x)^2\,[\delta L_0+\delta L_1(1-4x)].$$
#
# The first line is the Redlich–Kister excess term of Task 01 with $L_0$ and
# $L_1$ replaced by their changes; the factor $x(1-x)=x_{Ni}x_{Cu}$ makes it
# vanish for the pure elements. The second line is the tangent formula applied
# to $\delta g$; you can check it yourself by differentiating.
#
# So each prediction is the pinned value plus a **linear** combination of the
# two unknowns: a 9 × 2 matrix $M$ with columns $(1-x)^2$ and $(1-x)^2(1-4x)$.
#
# **Why "linear" matters.** The unknowns $\delta L_0$, $\delta L_1$ appear only
# multiplied by known numbers (the columns of $M$ at each composition). Then the
# best fit can be found in one step with matrix algebra, with no trial and error.
#
# In the code, `np.column_stack` puts the two columns side by side to make the
# 9 × 2 array, and `M.shape` is its (rows, columns) size. `**2` is a square.

# %%
def basis(x):
    x = np.asarray(x, dtype=float)  # accept a list or a single value as well as an array
    return np.column_stack(((1 - x)**2, (1 - x)**2 * (1 - 4 * x)))   # dimensionless, 9 × 2

M = basis(x)  # row i: the two factors at composition x[i]
print("M has", M.shape[0], "rows (one per composition) and", M.shape[1], "columns; its values are printed after your turn.")

# %% [markdown]
# ### Your turn (exercise 1 and the start of 2)
#
# 1. FCC_A1 here is (Cu,Ni)₁(Va)₁. How many moles of real atoms per mole of
#    formula units? Is an equilibrium mixture at the same overall composition the
#    same observable as homogeneous FCC (True or False)?
# 2. Work out $\delta\mu_{Ni}$ at x = 0.5 from $\delta g$ and its derivative.
#    Give the factors in $\delta\mu_{Ni}=c_0\,\delta L_0+c_1\,\delta L_1$.
# 3. Units drill: $RT\ln a_{Ni}$ at x = 0.5 (J/mol).
#
# The notation (Cu,Ni)₁(Va)₁ lists the sublattices: the first bracket is one
# site per formula unit that holds Cu or Ni, the second is one site that holds
# only vacancies (Va, an empty site).

# %%
atoms_per_formula_unit = None   # mol atoms per mol formula units
equilibrium_same_observable = None  # True or False
c0_at_05 = None                 # dimensionless
c1_at_05 = None                 # dimensionless
rt_ln_a_05 = None               # J/mol
check(atoms_per_formula_unit, "task02_atoms_per_formula")
check(equilibrium_same_observable, "task02_equilibrium_same")
check(c0_at_05, "task02_c0_05")
check(c1_at_05, "task02_c1_05")
check(rt_ln_a_05, "task02_rtlna_05")

# %% cellView="form"
#@title After your attempt: RT ln a_Ni and the two basis columns at each composition
print(" x_Ni   RT ln a_Ni (J/mol)   (1−x)²     (1−x)²(1−4x)")
for xi, m, (c0, c1) in zip(x, mu_obs, M):  # each row of M unpacks into its two columns
    print(f" {xi:.1f}   {m:12.2f}         {c0:.4f}    {c1:8.4f}")

# %% [markdown]
# ## 3. The pinned model before fitting
#
# Before changing anything we need the published model's own prediction
# $\mu_{\rm before}$ at the nine compositions: the fit then adds a correction to
# it.
#
# With the published database, the course code builds $g(x)$ from it and
# differentiates. Without it, the pinned model's activities at the nine
# compositions come from the saved run
# ([activity_fit_results.json](../course/materials/cuni/activity_fit_results.json)),
# which was made with the same file. To fetch the database (6,789 bytes, checked
# by size and SHA-256; it is kept outside the course folder), set
# `DOWNLOAD = True`. Building the model takes a few seconds.
#
# Database: S. an Mey, *Calphad* 16 (1992) 255–260,
# [doi:10.1016/0364-5916(92)90022-P](https://doi.org/10.1016/0364-5916(92)90022-P),
# from B. Hallstedt's SGTE collection, *Calphad* 89 (2025) 102833,
# [doi:10.1016/j.calphad.2025.102833](https://doi.org/10.1016/j.calphad.2025.102833).
#
# **The code.** `database("cuni", download=DOWNLOAD)` returns the path of a
# checked copy, or `None` (no-database mode). With the file,
# `make_forward_model` turns pycalphad's symbolic FCC Gibbs energy into $g(x)$
# at 1000 K, differentiates it, and returns a dictionary; its entry
# `forward["mu_relative"]` is a *function* that you call with compositions and
# that returns $\mu_{Ni}-g^{FCC}_{Ni}$ in J/mol. `baseline_L_J_per_mol` holds the
# published $L_0$ and $L_1$ at 1000 K. Without the file, the saved activities are
# turned back into $RT\ln a$.

# %%
DOWNLOAD = False
tdb = database("cuni", download=DOWNLOAD)  # path to the checked file, or None
saved = json.loads(Path("course/materials/cuni/activity_fit_results.json").read_text())  # the course run

if tdb is not None:
    from course.materials.cuni.fit_activity import make_forward_model
    from course.materials.cuni.worked_example import load_source
    forward = make_forward_model(load_source(tdb))  # load_source checks the file and pycalphad version
    mu_before = forward["mu_relative"](x)                  # J/mol, μ_Ni − g_Ni(FCC)
    L_before = forward["baseline_L_J_per_mol"]             # J/mol at 1000 K
    print("Pinned model built from the database.")
else:
    forward = None
    a_saved = np.array([o["a_NI_before"] for o in saved["observations"]])
    mu_before = RT * np.log(a_saved)                       # J/mol, from the saved activities
    L_before = np.array(saved["baseline_L_J_per_mol"])     # J/mol at 1000 K
    print("No-database mode: pinned values at the nine compositions from the saved run.")
print(f"L0(1000 K) = {L_before[0]:.2f} J/mol, L1(1000 K) = {L_before[1]:.2f} J/mol")

# %% [markdown]
# ## 4. The least-squares fit
#
# Now the two corrections are chosen so that the model follows the nine
# measurements as closely as possible.
#
# Residual = prediction − observation, in $RT\ln a_{Ni}$ (J/mol):
#
# $$r=\underbrace{\mu_{\rm before}+M\,\delta L}_{\text{prediction}}-\mu_{\rm obs}.$$
#
# Minimising the unweighted sum $J=r^{\mathsf T}r$ over the two unknowns gives the
# **normal equations**
#
# $$(M^{\mathsf T}M)\,\delta L=M^{\mathsf T}(\mu_{\rm obs}-\mu_{\rm before}),$$
#
# two linear equations in two unknowns, no iteration. They have one solution
# because the two columns of $M$ are not proportional.
#
# **Where the normal equations come from.** $J=r^{\mathsf T}r=\sum_i r_i^2$ is
# the sum of squared residuals (J²/mol²); squaring makes positive and negative
# misses count the same. At the minimum the derivative of $J$ with respect to
# each unknown is zero: $\partial J/\partial\,\delta L=2M^{\mathsf T}r=0$.
# Inserting $r$ and moving the known part to the right gives the line above.
# "Unweighted" means every point counts equally, since the source gives no error
# bar per point.
#
# **The code.** `@` is matrix multiplication and `.T` the transpose, so
# `M.T @ M` is the 2 × 2 matrix $M^{\mathsf T}M$. `np.linalg.solve(A, b)` solves
# the linear system $A\,u=b$ for $u$. `r_before` and `r_after` are the residuals
# without and with the correction; `r @ r` is the sum of their squares.
#
# What to look at: the two corrections, the drop in $J$, and the residuals point
# by point.

# %%
target = mu_obs - mu_before                           # J/mol
normal_matrix = M.T @ M                               # 2 × 2
delta_L = np.linalg.solve(normal_matrix, M.T @ target)  # J/mol
r_before = mu_before - mu_obs                         # J/mol
r_after = mu_before + M @ delta_L - mu_obs            # J/mol
sse_before, sse_after = float(r_before @ r_before), float(r_after @ r_after)  # (J/mol)², the sum J

print(f"δL0 = {delta_L[0]:.6f} J/mol, δL1 = {delta_L[1]:.6f} J/mol")
print(f"J before = {sse_before:.1f} (J/mol)², J after = {sse_after:.1f} (J/mol)²")
print(" x_Ni   residual before   residual after   (J/mol)")
for xi, rb, ra in zip(x, r_before, r_after):
    print(f" {xi:.1f}   {rb:12.2f}     {ra:12.2f}")

# %% [markdown]
# ### Your turn (exercises 2 and 3)
#
# 1. The fitted values at 1000 K: $L_0+\delta L_0$ and $L_1+\delta L_1$ (J/mol).
# 2. Your hand formula from section 2 with these corrections: $\delta\mu_{Ni}$ at
#    x = 0.5 (J/mol).
# 3. At which $x_{Ni}$ does the size of the residual grow after fitting?
# 4. Turn the fitted residual at x = 0.3 back into the fitted model's activity
#    ($a=a_{\rm obs}\exp(r/RT)$).
# 5. Does a lower total J guarantee that every point improves (True or False)?
#
# For item 4: the residual is $r=RT\ln a_{\rm fit}-RT\ln a_{\rm obs}$, so
# $\ln(a_{\rm fit}/a_{\rm obs})=r/RT$; take the exponential of both sides.
# `np.exp` is the exponential function.

# %%
L0_fitted = None              # J/mol
L1_fitted = None              # J/mol
delta_mu_05 = None            # J/mol
x_worse = None                # Ni atom fraction
a_fitted_03 = None            # dimensionless
every_point_improves = None   # True or False
check(L0_fitted, "task02_l0_fit")
check(L1_fitted, "task02_l1_fit")
check(delta_mu_05, "task02_dmu_05")
check(x_worse, "task02_worse_x")
check(a_fitted_03, "task02_a03_fit")
check(every_point_improves, "task02_every_point_better")

# %% [markdown]
# ## After your attempt: the saved run, the course code and the plots
#
# The packet's checks are arithmetic: 10⁻⁷ J/mol for chemical potentials and
# corrections, 10⁻¹⁰ for activities. They catch implementation mistakes; there
# is no tolerance for agreement with the measurements.
#
# The cell below compares every number of this notebook with the saved run and
# with the course module `fit_activity` (which solves the same problem with
# `numpy.linalg.lstsq`), checks that $M^{\mathsf T}r=0$ after the fit (the
# condition for a minimum), and then prints a table and draws two panels: the
# activities against $x_{Ni}$ (left) and the residuals before and after (right).
# In the left panel, the dotted line $a=x$ is the ideal solution.

# %% cellView="form"
#@title After your attempt: run to compare with the saved run and the course code
import matplotlib.pyplot as plt
from course.materials.cuni.fit_activity import fit_isothermal, interaction_basis, predict_activity

ARITH, ACT = saved["tolerances"]["arithmetic_J_per_mol"], saved["tolerances"]["activity_abs"]  # J/mol; activity
fit = saved["fit"]
a_saved_before = np.array([o["a_NI_before"] for o in saved["observations"]])
a_saved_after = np.array([o["a_NI_after"] for o in saved["observations"]])
confirm(R, saved["R_J_per_mol_K"], "Gas constant", tol=0)
confirm(float(np.max(np.abs(M - interaction_basis(x)))), 0.0, "Basis matrix against the course code", tol=1e-15)
if forward is not None:
    confirm(float(np.max(np.abs(np.exp(mu_before / RT) - a_saved_before))), 0.0, "Pinned activities from the database", tol=ACT)
for k in (0, 1):  # k = Redlich–Kister order
    confirm(L_before[k], saved["baseline_L_J_per_mol"][k], f"Pinned L{k}(1000 K)", tol=ARITH)
    confirm(delta_L[k], fit["delta_L_J_per_mol"][k], f"Correction δL{k}", tol=ARITH)
    confirm(L_before[k] + delta_L[k], fit["fitted_L_J_per_mol"][k], f"Fitted L{k}(1000 K)", tol=ARITH)
confirm(float(np.max(np.abs(r_before - fit["residual_before_J_per_mol"]))), 0.0, "Residuals before", tol=ARITH)
confirm(float(np.max(np.abs(r_after - fit["residual_after_J_per_mol"]))), 0.0, "Residuals after", tol=ARITH)
confirm(float(np.max(np.abs(M.T @ r_after))), 0.0, "Normal equations Mᵀr = 0 at the minimum", tol=ARITH)
print(f"J before {sse_before:.6f}, after {sse_after:.6f} (J/mol)²")
confirm(sse_after, fit["sse_after_J2_per_mol2"], "J after the fit", tol=1e-6)

hand = 0.5 * 0.5 * (delta_L[0] + delta_L[1] * 0.0) + 0.5 * (-0.5 * delta_L[1])   # δg + (1 − x)·dδg/dx at x = 0.5
confirm(hand, saved["checks"]["hand_mu_correction_J_per_mol"], "Hand δμ_Ni at x = 0.5", tol=ARITH)
confirm(float(basis([0.5])[0] @ delta_L), hand, "δμ_Ni at x = 0.5 from the basis", tol=ARITH)

a_before = np.exp(mu_before / RT)                 # activities of the pinned model
a_after = np.exp((mu_before + M @ delta_L) / RT)  # activities after the fit
confirm(float(np.max(np.abs(a_after - a_saved_after))), 0.0, "Fitted activities", tol=ACT)
# without the database, a stand-in dictionary that returns the saved μ_before plays the role of `forward`
course_fit = fit_isothermal(forward if forward is not None else
                            {"mu_relative": lambda z: mu_before, "baseline_L_J_per_mol": L_before}, x, a_obs)
confirm(float(np.max(np.abs(course_fit["delta_L_J_per_mol"] - delta_L))), 0.0, "Corrections from fit_isothermal", tol=ARITH)
if forward is not None:
    confirm(float(predict_activity(forward, [1.0], delta_L)[0]), 1.0, "Pure FCC Ni activity", tol=ACT)
else:
    print("Pure Ni: both basis columns vanish at x = 1, so the fit leaves a_Ni = 1 unchanged there.")

print("\n x_Ni   reported   before     after      |r| before  |r| after (J/mol)")
for i, xi in enumerate(x):
    flag = "  worse" if abs(r_after[i]) > abs(r_before[i]) else ""
    print(f" {xi:.1f}    {a_obs[i]:.4f}    {a_before[i]:.6f}  {a_after[i]:.6f}  {abs(r_before[i]):8.2f}   {abs(r_after[i]):8.2f}{flag}")

fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2))  # two panels side by side
left.plot(x, a_obs, "ko", ms=7, label="reported (Srikanth and Jacob 1989)")  # "ko": black circles
if forward is not None:
    curve = np.linspace(0.01, 0.99, 201)  # smooth curve between the measured points
    left.plot(curve, predict_activity(forward, curve, [0, 0]), "--", label="pinned input")
    left.plot(curve, predict_activity(forward, curve, delta_L), "-", label="two-value fit")
else:
    left.plot(x, a_before, "^--", label="pinned input (nine compositions)")
    left.plot(x, a_after, "s-", mfc="none", label="two-value fit (nine compositions)")
left.plot([0, 1], [0, 1], ":", color="0.6", label="a = x (ideal)")
left.set(xlabel="Ni atom fraction x_Ni", ylabel="Ni activity (pure FCC Ni = 1)",
         title="Homogeneous FCC, 1000 K", xlim=(0, 1), ylim=(0, 1))
left.legend(fontsize=8)
right.axhline(0, color="0.5", lw=0.8)  # zero line: a perfect match
right.plot(x, r_before, "^--", label="before")
right.plot(x, r_after, "s-", mfc="none", label="after")
right.set(xlabel="Ni atom fraction x_Ni", ylabel="RT ln a residual (J/mol of atoms)",
          title="Prediction minus observation")
right.legend(fontsize=8)
fig.tight_layout()
plt.show()

# %% [markdown]
# The total J falls by about two thirds, the fit improves eight of nine points,
# and at x = 0.3, which the pinned model already matched closely, it gets
# worse. The residuals after the fit still reach about 250 J/mol and change
# sign along x: two numbers at one temperature cannot follow every point.
#
# For scale: 250 J/mol in $RT\ln a$ at 1000 K is a factor
# $\exp(250/8314.5)\approx1.03$ in the activity, about 3 %.

# %% [markdown]
# ## 5. What one temperature cannot determine (exercise 4)
#
# The fit gave two numbers at 1000 K. A database, however, stores each
# interaction as a function of temperature. This section shows why nine points
# at a single temperature cannot fix that function.
#
# In the database each interaction depends on temperature, $L_k(T)=A_k+B_kT$.
# The published FCC values (S. an Mey 1992, as in the course file
# [mey1992_binary_parameters.csv](../course/materials/cuni/mey1992_binary_parameters.csv))
# give $L_0(1000)$ and $L_1(1000)$ above. Replace $A_k$ by $A_k+1000c$ and $B_k$ by
# $B_k-c$ for any c (J/(mol K)):
#
# $$(A_k+1000c)+(B_k-c)\cdot1000=A_k+1000B_k .$$
#
# The value at 1000 K, the only thing these data see, does not change.
#
# Here $A_k$ (J/mol) acts like an enthalpy part and $-B_k$ (J/(mol K)) like an
# entropy part of the interaction, since $L=A+BT$ has the same shape as
# $H-TS$. Data at one temperature fix only the sum, not how it is split.
#
# ### Your turn (exercise 4)
#
# With c = 5 J/(mol K): the change in $L_0$ at 1000 K and at 1500 K (J/mol).
# If you try to fit all four numbers $A_0,B_0,A_1,B_1$ to the nine points, the
# matrix has columns $M_0,\ 1000M_0,\ M_1,\ 1000M_1$: what is its rank? Would
# more compositions at 1000 K separate A from B (True or False)?
#
# The **rank** of a matrix is the number of its columns that are linearly
# independent, i.e. that cannot be made from the other columns by multiplying
# and adding. It is the number of unknowns the data can determine.

# %%
shift_at_1000 = None          # J/mol
shift_at_1500 = None          # J/mol
rank_four_unknowns = None     # integer
more_x_separates = None       # True or False
check(shift_at_1000, "task02_shift_1000")
check(shift_at_1500, "task02_shift_1500")
check(rank_four_unknowns, "task02_rank_ab")
check(more_x_separates, "task02_more_x_helps")

# %% [markdown]
# The next cell builds a second (A, B) pair shifted by c = 5 J/(mol K), shows
# that both pairs give the same predictions at 1000 K, and uses
# `np.linalg.matrix_rank` to count the independent columns of the four-unknown
# matrix, with one temperature and with an imagined second one.

# %% cellView="form"
#@title After your attempt: run to see the shift leave the fit unchanged
# the FCC_A1 rows of the transcribed table (orders 0 and 1)
params = [r for r in csv.DictReader(Path("course/materials/cuni/mey1992_binary_parameters.csv").open())
          if r["phase"] == "FCC_A1"]
A = np.array([float(r["a_J_per_mol"]) for r in params])         # J/mol, orders 0 and 1
B = np.array([float(r["b_J_per_mol_K"]) for r in params])       # J/(mol K)
confirm(float(np.max(np.abs(A + B * T - L_before))), 0.0, "A + 1000·B equals the pinned L(1000 K)", tol=1e-6)

c = 5.0                                                         # J/(mol K)
A_shift, B_shift = A + 1000 * c, B - c
L_fit = L_before + delta_L                                      # fitted values at 1000 K
print(" pair        A0 (J/mol)  B0 (J/(mol K))  L0(1000)   L0(1500)")
for name, a_, b_ in (("published", A, B), ("shifted", A_shift, B_shift)):
    print(f" {name:10s}  {a_[0]:9.2f}   {b_[0]:9.5f}     {a_[0] + b_[0] * 1000:9.2f}  {a_[0] + b_[0] * 1500:9.2f}")
confirm(float(np.max(np.abs((A_shift + B_shift * T) - (A + B * T)))), 0.0, "Shifted pair at 1000 K", tol=1e-9)
confirm((A_shift[0] + B_shift[0] * 1500) - (A[0] + B[0] * 1500), -2500.0, "Shift of L0 at 1500 K", tol=1e-9)

def predicted_mu(A_, B_, extra=np.zeros(2)):
    """RT ln a at the nine points for L = A + B·T plus a fitted correction."""
    return mu_before + M @ ((A_ + B_ * T) - L_before + extra)

for name, (a_, b_) in (("published", (A, B)), ("shifted", (A_shift, B_shift))):
    r = predicted_mu(a_, b_, delta_L) - mu_obs
    print(f" fitted, {name} A/B pair: J = {float(r @ r):.6f} (J/mol)²")
difference = predicted_mu(A_shift, B_shift, delta_L) - predicted_mu(A, B, delta_L)
confirm(float(np.max(np.abs(difference))), 0.0, "Change of every prediction under the shift", tol=1e-9)

# columns for the unknowns A0, B0, A1, B1: B_k multiplies T times the column of A_k
four = np.column_stack((M[:, 0], T * M[:, 0], M[:, 1], T * M[:, 1]))
rank_one_T = np.linalg.matrix_rank(four)  # number of independent columns
print(f"\nRank for A0, B0, A1, B1 from the nine points at 1000 K: {rank_one_T} of 4")
confirm(rank_one_T, 2, "Rank with one temperature", tol=0)
# Structure only: the same compositions at a second temperature (no such data here).
T2 = 1200.0
stacked = np.vstack((four, np.column_stack((M[:, 0], T2 * M[:, 0], M[:, 1], T2 * M[:, 1]))))  # 18 × 4
print(f"Rank if the same compositions were also measured at {T2:.0f} K: {np.linalg.matrix_rank(stacked)} of 4")

# %% [markdown]
# Activities, or other data that depend on G, at a **second temperature** would
# separate $A_k$ from $B_k$. More compositions at 1000 K only add rows that are
# again combinations of the same two columns. That is why the fitted numbers are
# values at 1000 K only and are not written back into the database as new
# temperature functions.

# %% [markdown]
# ## 6. Calibration, not validation
#
# All nine points were used to choose $\delta L_0$ and $\delta L_1$; none was
# held back. This is **calibration**: it shows how well two numbers at 1000 K can
# follow these data. **Validation** would need independent observations that
# took no part in the fit. These 1989 measurements were published before the
# 1992 assessment and were available to it, so they cannot count as an
# independent test of it either. (In
# [f6](f6_fitting_synthetic.ipynb) the held-out points played that role for an
# invented model.)
#
# ### Your turn
#
# Is this fit an independent validation of the Mey assessment (True or False)?

# %%
independent_validation = None   # True or False
check(independent_validation, "task02_independent_validation")

# %% [markdown]
# Worked answers: [Task 02 answers](../course/materials/cuni/fitting_answers.md).
#
# ## 7. Limits
#
# One temperature, nine points, one phase. The fit changes only two interaction
# values at 1000 K inside this notebook; the database file is not changed, and
# the numbers are not a new Cu–Ni description. The source gives no uncertainty
# per point, so the fit is unweighted and no error bars or confidence ranges
# are given for the fitted values. Residuals remain after the fit. The measured
# activities are not independent of the assessment being adjusted. Pressure is
# set to 101325 Pa by course convention; the paper does not state it.
# Next: [f7 · a grain boundary in an open or closed cell](f7_boundary_open_closed.ipynb), the boundary
# basics for Tasks 03 and 04.
