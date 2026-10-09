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
# # Task 01, continued · The gap curve and the driving force in a published Cu–Ni database
#
# **Learning question:** the advanced steps drew a line under the dots, a gap
# curve and a driving force for invented phase models. Do the same pictures
# work for a published assessment, and what do they say about an FCC Cu–Ni
# alloy with x(Ni) = 0.5 at 600 K?
#
# Used in: self-study step 12 (sections 1–4) and step 14 (section 5), optional, after Task 01. This notebook
# extends [Task 01](task01_cuni_equilibria.ipynb) (step 05); do Task 01 first: the database, the conditions and the 600 K
# point are the same. From the advanced steps you need the menu of
# states, the line under the dots ($\mu_A$ and $\Delta\mu$), the gap curve, the
# driving force, and the ceiling and floor of step 14.
#
# **What is published and what is chosen.** Every Gibbs energy here comes from
# the published Cu–Ni assessment of Task 01; no phase model is invented. Chosen
# here are only the conditions, the composition grid, the finite-difference
# step and the menu of section 5. Read A as Cu and B as Ni: $x$ is the mole
# fraction of Ni, $\mu_A=\mu_{\rm Cu}$ and $\Delta\mu=\mu_{\rm Ni}-\mu_{\rm Cu}$.
#
# **How this notebook works.** Run the cells from top to bottom. In each "Your
# turn" cell, replace `None` with your value and run it: `check(your_value,
# key)` says "✓ matches", "close" or "not yet" without showing the stored
# answer. Cells marked *After your attempt* reproduce the course values with
# `confirm(value, expected, "what", tol=...)`, which prints a ✓ line or stops
# with an error.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Get the database | main | 5 min |
# | 2 | One equilibrium and its line | main | 10 min |
# | 3 | The gap curve of the answer | main | 10 min |
# | 4 | A quenched alloy: tangent, gap curve and driving force | main | 20 min |
# | 5 | The menu view: ceiling, floor and one more state | main | 20 min |
# | 6 | Above the gap: 650 K | dive deeper | 10 min |
# | 7 | Limits | main | 2 min |
#
# **Coming from materials.** The gap curve is the parallel-tangent construction
# drawn as a curve: the tangent becomes the horizontal axis, and the driving
# force for forming a new composition is how far the curve dips below it.
#
# **Coming from operations research.** The equilibrium line is the optimal dual
# of the menu LP over all states; the gap curve is the reduced cost of every
# possible column, here for a phase model that is not convex.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.2.1"
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
# ## 1. Get the database (main track, 5 min)
#
# The same file as in Task 01: S. an Mey's Cu–Ni assessment as adapted in
# B. Hallstedt's SGTE collection of binary datasets, `CuNi-92Mey-LB.tdb`
# ([direct download](https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb)).
# Cite S. an Mey, *Calphad* 16 (1992) 255–260,
# [doi:10.1016/0364-5916(92)90022-P](https://doi.org/10.1016/0364-5916(92)90022-P),
# and B. Hallstedt, *Calphad* 89 (2025) 102833,
# [doi:10.1016/j.calphad.2025.102833](https://doi.org/10.1016/j.calphad.2025.102833).
#
# Set `DOWNLOAD = True` to fetch the file into your own session; the cell checks
# its size and SHA-256. Without the file the notebook runs in **no-database
# mode**: every cell then reads the saved numbers of the course run,
# `course/materials/cuni/gap_curve.json` (made by `gap_curve.py` in the same
# folder), and all exercises still work. With the file, every cell calculates
# and compares its result with the saved numbers.

# %%
import json
from pathlib import Path

DOWNLOAD = False   # True: fetch CuNi-92Mey-LB.tdb into your session
TDB = database("cuni", download=DOWNLOAD)  # path to the checked file, or None
LIVE = TDB is not None                      # True with the database, False in no-database mode
SAVED = json.loads(Path("course/materials/cuni/gap_curve.json").read_text())  # the course run's numbers
if LIVE:
    print("Live mode: the cells below calculate with your copy of the database.")
else:
    print("No-database mode: the cells below read the saved course numbers (course/materials/cuni/gap_curve.json).")

# %% [markdown]
# ## 2. One equilibrium and its line (main track, 10 min)
#
# | Setting | Value |
# |---|---|
# | phases allowed | FCC_A1 and LIQUID (Task 01 showed that BCC_A2 and HCP_A3 do not appear here) |
# | components | CU, NI and VA (vacancy, on FCC's empty second sublattice) |
# | pressure | 101325 Pa |
# | amount | N = 1 mol of atoms |
# | temperature | 600 K |
# | overall composition | z = x(Ni) = 0.5 |
# | sampling setting | `pdens = 60`, as in Task 01 |
#
# Energies are in J/mol of atoms. `equilibrium` returns, besides `GM`, `NP` and
# `X`, the chemical potentials `MU` of Cu and Ni (J/mol). They are the line
# under the answer:
#
# $$\text{line}(x)=\mu_{\rm Cu}(1-x)+\mu_{\rm Ni}\,x=\mu_A+\Delta\mu\,x .$$
#
# `point(T)` returns the equilibrium at T and z = 0.5: `GM`, a dictionary `MU`
# and one row `(phase, NP, x(Ni) in the phase, GM of that phase at that x)` per
# phase present, sorted by x(Ni). The last entry comes from `calculate`, which
# only evaluates a phase at the composition you give it (section 3).

# %%
import numpy as np
import matplotlib.pyplot as plt
from pycalphad import calculate, equilibrium, variables as v
from course.materials.cuni import worked_example as cuni  # the Task 01 course script

PHASES = ["FCC_A1", "LIQUID"]  # the phases allowed here
COMPONENTS = cuni.COMPONENTS   # CU, NI, VA
P = cuni.PRESSURE              # Pa
Z = 0.5                        # overall x(Ni)
COLOUR = {"FCC_A1": "#2445c4", "LIQUID": "#cf4418"}
if LIVE:
    db = cuni.load_source(TDB)  # checks the pycalphad version and the file, then reads it


def site_fractions(phase, x):
    """Rows for calculate(): FCC_A1 (y_Cu, y_Ni, y_Va = 1), LIQUID (x_Cu, x_Ni)."""
    x = np.atleast_1d(np.asarray(x, dtype=float))
    return np.column_stack([1 - x, x, np.ones_like(x)] if phase == "FCC_A1" else [1 - x, x])


def gm(phase, x, T):
    """GM of one phase at the given x(Ni), J/mol of atoms (no minimisation)."""
    return calculate(db, COMPONENTS, phase, T=T, P=P, N=1, points=site_fractions(phase, x)).GM.values.ravel()


def point(T):
    """Equilibrium at T (K) and x(Ni) = 0.5: GM, {component: MU}, [(phase, NP, x, GM of the phase)]."""
    if LIVE:
        eq = equilibrium(db, COMPONENTS, PHASES, {v.T: T, v.X("NI"): Z, v.P: P, v.N: 1}, calc_opts={"pdens": 60})
        rows = [(str(p), float(n), float(x)) for p, n, x in
                zip(eq.Phase.values.squeeze(), eq.NP.values.squeeze(), eq.X.sel(component="NI").values.squeeze())
                if p and n > 1e-8]  # keep only real phases with a positive amount
        rows = sorted(((p, n, x, float(gm(p, x, T)[0])) for p, n, x in rows), key=lambda row: row[2])  # by x(Ni)
        mu = {c: float(eq.MU.sel(component=c).values.squeeze()) for c in ("CU", "NI")}
        return float(eq.GM.values.squeeze()), mu, rows
    saved = SAVED["equilibrium"][f"{T:.0f}"]
    return saved["GM"], saved["MU"], [(r["phase"], r["NP"], r["x_NI"], r["GM_phase"]) for r in saved["vertices"]]


GM600, MU600, ROWS600 = point(600)
print(f"600 K, z = {Z}: GM = {GM600:.4f} J/mol of atoms")
print(f"  MU(Cu) = {MU600['CU']:.4f} J/mol   MU(Ni) = {MU600['NI']:.4f} J/mol")
print(f"  {'phase':<8} {'NP':>10} {'x(Ni)':>10} {'GM of the phase':>18}")
for phase, n, x, g in ROWS600:
    print(f"  {phase:<8} {n:10.6f} {x:10.6f} {g:18.4f}")

# %% [markdown]
# Two FCC_A1 rows: one phase model at two compositions, the miscibility gap of
# Task 01. First the balances: the amounts must add up to one mole of atoms and
# the Ni in the two rows must add up to z.

# %%
np_sum = sum(n for _, n, _, _ in ROWS600)
ni_sum = sum(n * x for _, n, x, _ in ROWS600)
print(f"Σ NP = {np_sum:.9f}   Σ NP·x(Ni) = {ni_sum:.9f}")
confirm(np_sum, 1.0, "The amounts add up to one mole of atoms", tol=1e-6)
confirm(ni_sum, Z, "The Ni balance", tol=1e-6)
if LIVE:  # your calculation against the saved course run
    for (p, n, x, g), saved in zip(ROWS600, SAVED["equilibrium"]["600"]["vertices"]):
        assert p == saved["phase"], f"{p} where the course run has {saved['phase']}"
        confirm(n, saved["NP"], f"  {p} amount", tol=1e-6)
        confirm(x, saved["x_NI"], f"  {p} x(Ni)", tol=1e-6)
    confirm(GM600, SAVED["equilibrium"]["600"]["GM"], "GM at 600 K", tol=1e-4)

# %%
mu_A = MU600["CU"]             # the line's height at x = 0
d_mu = MU600["NI"] - MU600["CU"]  # its slope


def line(x):
    """The equilibrium line under the answer, J/mol of atoms."""
    return mu_A + d_mu * x


print(f"mu_A = {mu_A:.4f}   d_mu = {d_mu:.4f}   (J/mol)")

# %% [markdown]
# ### Your turn
#
# What is the line's height at the overall composition $x=z=0.5$? Compare it
# with `GM` above. Why must the two agree?

# %%
line_at_half = None  # J/mol of atoms, to 0.01
check(line_at_half, "task01b_line_at_half")

# %% cellView="form"
#@title After your attempt: the line at z
print(f"line(0.5) = {line(Z):.4f}   GM = {GM600:.4f}")
confirm(line(Z), GM600, "The line at z equals the answer's energy", tol=1e-6)
print("Each phase in the answer sits on the line, so their mixture does too: G = mu_Cu (1 − z) + mu_Ni z.\n"
      "In LP words: the cheapest mixture equals the dual value at z (no remaining uncertainty).")

# %% [markdown]
# ## 3. The gap curve of the answer (main track, 10 min)
#
# The **gap curve** of a phase is its Gibbs energy minus the line:
# $\text{gap}(x)=G_\varphi(x)-\text{line}(x)$. A state below zero would lower the
# energy if it were added; a state at zero is in use or could be.
#
# `calculate` evaluates a phase at the internal compositions in `points`
# without looking for a minimum. With explicit site fractions the compositions
# are exactly the ones we ask for: an even grid of 1001 values of x(Ni), step
# 0.001. `curves(T)` returns `{phase: GM on the grid}`.

# %%
X = np.linspace(0.0, 1.0, 1001)  # x(Ni), step 0.001
STEP = X[1] - X[0]


def curves(T):
    """{phase: GM (J/mol of atoms) at every grid x}, calculated or saved."""
    if LIVE:
        return {phase: gm(phase, X, T) for phase in PHASES}
    return {phase: np.array(SAVED["curves"][f"{T:.0f}"][phase]) for phase in PHASES}


G600 = curves(600)
if LIVE:
    largest = max(np.abs(G600[p] - np.array(SAVED["curves"]["600"][p])).max() for p in PHASES)
    confirm(largest, 0.0, "Your curves against the saved curves (saved to 1e-9 J/mol)", tol=1e-5)
gap_eq = {phase: G600[phase] - line(X) for phase in PHASES}
for phase in PHASES:
    k = int(np.argmin(gap_eq[phase]))
    print(f"{phase:<7}: lowest gap on the grid {gap_eq[phase][k]:12.6f} J/mol of atoms at x(Ni) = {X[k]:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
for phase in PHASES:
    axes[0].plot(X, gap_eq[phase], color=COLOUR[phase], label=phase)
axes[1].plot(X, gap_eq["FCC_A1"], color=COLOUR["FCC_A1"], label="FCC_A1")
for ax in axes:
    ax.axhline(0, color="black", lw=0.8)
    for _, _, x, _ in ROWS600:
        ax.axvline(x, ls=":", color="0.4")
    ax.set(xlabel="x(Ni)", ylabel="gap (J/mol of atoms)", xlim=(0, 1))
    ax.legend()
axes[0].set_title("600 K: gap against the equilibrium line")
axes[1].set(title="Zoom on FCC_A1 (dotted: the two FCC compositions)", ylim=(-5, 60))
fig.tight_layout()
plt.show()

# %% [markdown]
# The FCC_A1 gap curve never goes below zero (up to rounding) and touches zero
# twice, at the two FCC compositions: the line is the common tangent. LIQUID
# lies thousands of J/mol of atoms above the line everywhere, so no liquid can
# form at 600 K.
#
# ### Your turn
#
# How far above the line is a liquid of the alloy's own composition? Compute
# the LIQUID gap at x(Ni) = 0.5 from the grid: `G600["LIQUID"]` at the grid
# index of 0.5, minus `line(0.5)`.

# %%
gap_liquid_half = None  # J/mol of atoms
check(gap_liquid_half, "task01b_gap_liquid_half")

# %% cellView="form"
#@title After your attempt: the gap curve of the answer
saved = SAVED["derived"]["eq_line_600"]
i_half = int(round(Z / STEP))  # grid index of x(Ni) = 0.5
print(f"LIQUID gap at x(Ni) = 0.5: {G600['LIQUID'][i_half] - line(Z):.4f} J/mol of atoms")
confirm(G600["LIQUID"][i_half] - line(Z), saved["liquid_gap_at_half"], "LIQUID gap at 0.5", tol=1e-5)
for phase, n, x, g in ROWS600:
    print(f"{phase} at x(Ni) = {x:.6f}: gap = {g - line(x):.2e} J/mol of atoms")
    confirm(g - line(x), 0.0, "  the line touches the curve here", tol=1e-6)
lowest_fcc = gap_eq["FCC_A1"].min()
confirm(min(lowest_fcc, 0.0), 0.0, "No FCC_A1 grid state lies below the line", tol=1e-6)
lowest_liquid = gap_eq["LIQUID"].min()
print(f"LIQUID: lowest gap on the grid {lowest_liquid:.2f} J/mol of atoms; continuous minimum "
      f"{saved['liquid_lowest_gap']['gap']:.2f} J/mol of atoms at x(Ni) = {saved['liquid_lowest_gap']['x']:.4f}")
confirm(lowest_liquid, saved["liquid_lowest_gap"]["gap"], "LIQUID's lowest gap (grid against continuous)", tol=0.05)

# %% [markdown]
# ## 4. A quenched alloy: tangent, gap curve and driving force (main track, 20 min)
#
# Now take a state that is *not* the answer: the alloy as one homogeneous FCC
# phase at x(Ni) = 0.5, as if quenched from above the gap. Its own line is the
# tangent to the FCC curve at 0.5, so its chemical potentials are
#
# $$\Delta\mu=G'(0.5),\qquad \mu_A=G(0.5)-0.5\,G'(0.5),\qquad \mu_B=\mu_A+\Delta\mu .$$
#
# The slope $G'$ comes from a **central finite difference** with the grid step
# $h=0.001$: $G'(x)\approx[G(x+h)-G(x-h)]/(2h)$. The curvature uses
# $G''(x)\approx[G(x+h)-2G(x)+G(x-h)]/h^2$. Against this tangent, the gap curve
# shows which compositions could form from the quenched alloy; minus its
# deepest dip is the **driving force** (the parallel tangent of step 07 or 09).
#
# `X_START` is the quenched composition. Keep 0.5 for the checks; the
# exercise at the end of the section changes it.

# %%
X_START = 0.5                         # composition of the homogeneous FCC state
i = int(round(X_START / STEP))        # its grid index
g_fcc = G600["FCC_A1"]
g_start = g_fcc[i]
slope = (g_fcc[i + 1] - g_fcc[i - 1]) / (2 * STEP)              # G'(x_start), J/mol
curvature = (g_fcc[i + 1] - 2 * g_fcc[i] + g_fcc[i - 1]) / STEP**2  # G''(x_start), J/mol


def second_difference(g):
    """G'' at every interior grid point X[1:-1], J/mol of atoms."""
    return (g[2:] - 2 * g[1:-1] + g[:-2]) / STEP**2


INNER = (X[1:-1] > 0.05) & (X[1:-1] < 0.95)  # interior points away from the pure ends
t_mu_A, t_d_mu = g_start - X_START * slope, slope
gap_t = g_fcc - (t_mu_A + t_d_mu * X)  # gap curve against the tangent
k = int(np.argmin(gap_t))
print(f"homogeneous FCC at x(Ni) = {X_START}: G = {g_start:.4f} J/mol of atoms")
print(f"tangent: mu_Cu = {t_mu_A:.4f}, mu_Ni = {t_mu_A + t_d_mu:.4f}, d_mu = {t_d_mu:.4f} J/mol")
print(f"deepest dip on the grid: {gap_t[k]:.4f} J/mol of atoms at x(Ni) = {X[k]:.3f}")

fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(X, gap_t, color=COLOUR["FCC_A1"], label="FCC_A1 against the tangent at the quenched state")
ax.plot(X, gap_eq["FCC_A1"], color="0.6", ls="--", label="FCC_A1 against the equilibrium line")
ax.plot([X_START], [0], "o", color="black", label="quenched state")
ax.plot([X[k]], [gap_t[k]], "v", color=COLOUR["FCC_A1"], label="deepest dip")
ax.axhline(0, color="black", lw=0.8)
ax.set(xlabel="x(Ni)", ylabel="gap (J/mol of atoms)", xlim=(0, 1), ylim=(-60, 120),
       title="600 K: gap curve of the quenched FCC alloy")
ax.legend(fontsize=8)
plt.show()

# %% [markdown]
# ### Your turn
#
# 1. The driving force for forming the deepest-dip composition from the quenched
#    alloy, as a positive number in J/mol of atoms.
# 2. How much lower is the equilibrium pair of section 2 than the homogeneous
#    alloy, per mole of atoms of the alloy ($G(0.5)-GM$)?

# %%
driving_force = None    # J/mol of atoms, positive
full_split_gain = None  # J/mol of atoms, positive
check(driving_force, "task01b_driving_force")
check(full_split_gain, "task01b_full_split_gain")

# %% cellView="form"
#@title After your attempt: the driving force
start = SAVED["derived"]["homogeneous_start_600"]
if X_START == 0.5:
    print(f"driving force {-gap_t[k]:.4f} J/mol of atoms (grid); continuous minimum {start['driving_force']:.4f} "
          f"at x(Ni) = {start['deepest_dip']['x']:.4f}")
    confirm(-gap_t[k], start["driving_force"], "Driving force: grid against analytic slope + continuous minimum", tol=0.01)
    confirm(t_d_mu, start["slope_d_mu"], "Slope: finite difference against the analytic derivative", tol=0.01)
    if LIVE:  # refine the grid minimum with your database: scipy searches between the neighbouring grid points
        from scipy.optimize import minimize_scalar
        refined = minimize_scalar(lambda x: gm("FCC_A1", x, 600)[0] - (t_mu_A + t_d_mu * x),
                                  bounds=(X[k - 1], X[k + 1]), method="bounded", options={"xatol": 1e-9})
        print(f"refined with minimize_scalar: dip {refined.fun:.4f} at x(Ni) = {refined.x:.5f}")
        confirm(-refined.fun, start["driving_force"], "Driving force, refined in this notebook", tol=0.002)
    print(f"G(0.5) − GM = {g_start - GM600:.4f} J/mol of atoms")
    confirm(g_start - GM600, start["full_split_gain"], "Energy released by the full split", tol=1e-5)
print("The two numbers answer different questions. The driving force is the gain per mole of atoms of a small\n"
      "amount of the new composition, formed from the quenched alloy at its own prices. The full split is the\n"
      "gain per mole of atoms of the whole alloy once it has become the equilibrium pair.")

# %% [markdown]
# ### Metastable or unstable?
#
# A uniform state that a split could lower is **metastable** while small
# composition changes raise its energy (the curve bends up, $G''>0$), and
# **unstable** where they lower it ($G''<0$, inside the spinodal). The FCC
# compositions of the equilibrium pair are the **binodal**; the points where
# $G''$ changes sign are the **spinodal**.
#
# ### Your turn
#
# Read the printed curvature at x(Ni) = 0.5. Is the quenched alloy at 600 K
# inside the spinodal (True or False)?

# %%
print(f"G''({X_START}) ≈ {curvature:.1f} J/mol of atoms")
inside_spinodal = None  # True or False
check(inside_spinodal, "task01b_inside_spinodal")

# %% cellView="form"
#@title After your attempt: binodal and spinodal at 600 K
xs, cs = X[1:-1][INNER], second_difference(g_fcc)[INNER]
signs = np.flatnonzero(np.diff(np.sign(cs)))                    # where G'' changes sign between grid points
spinodal = [xs[j] - cs[j] * (xs[j + 1] - xs[j]) / (cs[j + 1] - cs[j]) for j in signs]  # straight-line crossing
binodal = [x for _, _, x, _ in ROWS600]
print(f"binodal  x(Ni) = {binodal[0]:.4f} and {binodal[1]:.4f}")
print(f"spinodal x(Ni) = {spinodal[0]:.4f} and {spinodal[1]:.4f}")
for got, expected in zip(spinodal, start["spinodal_x"]):
    confirm(got, expected, "Spinodal point: grid against the analytic second derivative", tol=1e-3)
if X_START == 0.5:
    confirm(curvature, start["curvature"], "Curvature at 0.5: finite difference against analytic", tol=0.5)
print("x(Ni) = 0.5 lies just inside the spinodal: the quenched alloy is unstable at 600 K, not merely metastable.\n"
      "Any small composition wave lowers its energy (spinodal decomposition). Between the binodal and the\n"
      "spinodal, for example at 0.45, a homogeneous alloy would be metastable: it needs a nucleus first.")

# %% [markdown]
# **Exercise (materials flavour).** Set `X_START = 0.45` at the top of this
# section and rerun the cells down to here. Near 0.45 the gap curve now rises on
# both sides (metastable), yet it still dips below zero further away: which
# composition would nucleate, and with what driving force? Try 0.35 as well,
# outside the binodal. Set it back to 0.5 before going on.
#
# ## 5. The menu view: ceiling, floor and one more state (main track, 20 min)
#
# Step 10's way to the answer: list a few states, find their cheapest mixture
# at z, read the line from the LP, then use the gap curve to see how far off the
# menu can still be. The menu here: FCC_A1 and LIQUID, each at x(Ni) = 0.1,
# 0.3, 0.7 and 0.9, with their energies from the grid. The LP is the one of the
# LP primer and f4c: minimise $\sum_j f_j g_j$ with $\sum_j f_j=1$,
# $\sum_j f_j x_j=z$, $f_j\ge0$. Its multipliers `eqlin.marginals` are $\mu_A$
# and $\Delta\mu$.

# %%
from scipy.optimize import linprog

MENU_X = [0.1, 0.3, 0.7, 0.9]


def state(phase, x):
    """A menu state (phase, x, g) read from the 600 K grid."""
    return (phase, x, float(G600[phase][int(round(x / STEP))]))


def solve_menu(states):
    """Cheapest mixture at z: (ceiling, mu_A, d_mu, [(state, amount) in use])."""
    c = [g for _, _, g in states]
    A_eq = [[1.0] * len(states), [x for _, x, _ in states]]
    r = linprog(c, A_eq=A_eq, b_eq=[1.0, Z], bounds=(0, None), method="highs-ds")
    m_A, m_d = r.eqlin.marginals
    return float(r.fun), float(m_A), float(m_d), [(s, f) for s, f in zip(states, r.x) if f > 1e-12]


def deepest_dip(m_A, m_d):
    """The deepest grid state of both phases below the line m_A + m_d x: (gap, phase, x)."""
    return min((float((G600[p] - (m_A + m_d * X)).min()), p, float(X[np.argmin(G600[p] - (m_A + m_d * X))]))
               for p in PHASES)


menu = [state(p, x) for p in PHASES for x in MENU_X]
ceiling, m_A, m_d, used = solve_menu(menu)
dip, dip_phase, dip_x = deepest_dip(m_A, m_d)
floor = ceiling + min(0.0, dip)
for (p, x, g), f in used:
    print(f"uses {p} at x(Ni) = {x}: amount {f:.4f}")
print(f"ceiling {ceiling:.4f}; line mu_A = {m_A:.4f}, d_mu = {m_d:.4f}")
print(f"deepest dip below this line: {dip:.4f} J/mol of atoms ({dip_phase} at x(Ni) = {dip_x:.3f})")
print(f"floor {floor:.4f} <= answer {GM600:.4f} <= ceiling {ceiling:.4f}")
assert floor <= GM600 <= ceiling, "the answer is not between floor and ceiling"

fig, ax = plt.subplots(figsize=(7, 3.6))
for p in PHASES:
    ax.plot(X, G600[p] - (m_A + m_d * X), color=COLOUR[p], label=p)
    ax.plot(MENU_X, [g - (m_A + m_d * x) for q, x, g in menu if q == p], "o", color=COLOUR[p])
ax.plot([dip_x], [dip], "v", color="black", label="deepest dip")
ax.axhline(0, color="black", lw=0.8)
ax.set(xlabel="x(Ni)", ylabel="gap (J/mol of atoms)", xlim=(0, 1), ylim=(-30, 120),
       title="600 K: gap curve against the menu's line (dots: the menu)")
ax.legend(fontsize=8)
plt.show()

# %% [markdown]
# A floor needs the deepest dip of the *whole* curve. Here it is the deepest grid
# state; the after-your-attempt cell below compares it with the continuous
# minimum.
#
# ### Your turn
#
# What is the remaining uncertainty of this menu, ceiling minus floor, in J/mol
# of atoms?

# %%
menu_uncertainty = None  # J/mol of atoms
check(menu_uncertainty, "task01b_menu_uncertainty")

# %% cellView="form"
#@title After your attempt: the menu's bracket
menu_saved = SAVED["derived"]["menu_600"]
print(f"ceiling − floor = {ceiling - floor:.4f} J/mol of atoms")
confirm(ceiling, menu_saved["ceiling"], "Ceiling of the menu", tol=1e-5)
confirm(m_d, menu_saved["d_mu"], "Slope of the menu's line", tol=1e-5)
confirm(ceiling - floor, menu_saved["remaining_uncertainty"],
        "Remaining uncertainty: grid dip against the continuous minimum", tol=0.01)

# %% [markdown]
# Now add the deepest state to the menu and solve again: one round of column
# generation (step 13). The cell keeps going until no grid state lies below the
# line, printing ceiling, floor and the remaining uncertainty in every round.
# The search set is a fixed set of sampled states, the 1001-point grid, like
# pycalphad's (whose set is coarser, pdens 60). As in step 14, the floor kept is
# the best (highest) one so far, and the remaining uncertainty is the ceiling
# minus that best floor.

# %%
states = list(menu)
best = -np.inf  # best floor so far
print(" round    ceiling     raw floor    best floor   remaining   added")
for rnd in range(10):
    c_up, a, b, in_use = solve_menu(states)
    d, p, x = deepest_dip(a, b)
    low = c_up + min(0.0, d)  # this round's raw floor
    best = max(best, low)
    print(f"{rnd:5d}  {c_up:11.4f}  {low:11.4f}  {best:11.4f}  {c_up - best:10.4f}   "
          + (f"{p} {x:.3f}" if d < -1e-9 else "none"))
    if d >= -1e-9:
        break
    states.append(state(p, x))
for (p, x, g), f in in_use:
    print(f"in use at the end: {p} at x(Ni) = {x:.3f}, amount {f:.4f}")
print(f"final ceiling {c_up:.4f}; equilibrium GM {GM600:.4f} J/mol of atoms")
confirm(c_up, GM600, "Column generation on the grid reaches the equilibrium energy", tol=1e-3)

# %% [markdown]
# The raw floor of a round can fall (round 1 here), because the line moves; the
# best one so far is kept. These floors use the deepest state of the 1001-point
# grid, so they are grid floors: the last one sits 0.0001 J/mol above the true
# equilibrium energy. Only the deepest point of the continuous curve gives a
# guaranteed floor (step 14).
#
# The first added state is FCC near 0.388, the second FCC near 0.803; after a
# few rounds the two states in use are the grid points nearest the two FCC
# compositions of section 2, and the line is the common tangent. The menu at
# 0.3 and 0.7 could not see the split: its best mixture, FCC at 0.3 and 0.7, even
# lies 5.8 J/mol above the homogeneous alloy, as step 10's menu lies above step
# 03 part D's single SOLID. Two FCC dots on both sides of the gap are not the
# split; the gap curve found it.
#
# **Dive deeper: why 0.5 is not on the menu.** With the quenched state itself
# on the menu, the LP's best is that one state alone: none of the menu's pairs
# beats it. One state in use does not fix the line ([f4c](f4c_master_and_dual.ipynb), section 6), so the
# multipliers are only one of many valid lines.

# %%
with_half = solve_menu(menu + [state("FCC_A1", 0.5)])
print(f"menu + FCC 0.5: ceiling {with_half[0]:.4f}, uses " +
      ", ".join(f"{p} {x} ({f:.3f})" for (p, x, g), f in with_half[3]))
confirm(with_half[0], SAVED["derived"]["menu_600"]["with_x_half"]["ceiling"], "Ceiling with x = 0.5 on the menu", tol=1e-5)

# %% [markdown]
# ## 6. Above the gap: 650 K (dive deeper, 10 min)
#
# Repeat sections 2 and 3 at 650 K. Predict first: how many FCC compositions,
# and does any FCC state lie below the line?

# %%
GM650, MU650, ROWS650 = point(650)
G650 = curves(650)
if LIVE:
    largest = max(np.abs(G650[p] - np.array(SAVED["curves"]["650"][p])).max() for p in PHASES)
    confirm(largest, 0.0, "Your 650 K curves against the saved curves", tol=1e-5)
line650 = MU650["CU"] + (MU650["NI"] - MU650["CU"]) * X
gap650 = G650["FCC_A1"] - line650
for phase, n, x, g in ROWS650:
    print(f"650 K: {phase} NP = {n:.6f} at x(Ni) = {x:.6f}")
print(f"lowest FCC_A1 gap on the grid: {gap650.min():.2e} J/mol of atoms at x(Ni) = {X[np.argmin(gap650)]:.3f}")
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(X, gap650, color=COLOUR["FCC_A1"], label="650 K")
ax.plot(X, gap_eq["FCC_A1"], color="0.6", ls="--", label="600 K (section 3)")
ax.axhline(0, color="black", lw=0.8)
ax.set(xlabel="x(Ni)", ylabel="gap (J/mol of atoms)", xlim=(0, 1), ylim=(-5, 120), title="FCC_A1 against its equilibrium line")
ax.legend()
plt.show()

# %% [markdown]
# ### Your turn
#
# 1. How many FCC_A1 rows does the 650 K equilibrium have?
# 2. The smallest curvature $G''$ of FCC_A1 at 650 K between x(Ni) = 0.05 and
#    0.95, in J/mol of atoms: use `second_difference` and `INNER` from section 4
#    on `G650["FCC_A1"]`.

# %%
fcc_rows_650 = None  # a whole number
min_curvature_650 = None  # J/mol of atoms
check(fcc_rows_650, "task01b_fcc_rows_650")
check(min_curvature_650, "task01b_min_curvature_650")

# %% cellView="form"
#@title After your attempt: 650 K and the top of the gap
confirm(len(ROWS650), 1, "One phase at 650 K", tol=0)
confirm(min(gap650.min(), 0.0), 0.0, "No FCC_A1 grid state below the 650 K line", tol=1e-6)
low600 = second_difference(G600["FCC_A1"])[INNER].min()
low650 = second_difference(G650["FCC_A1"])[INNER].min()
print(f"smallest G'' between x(Ni) = 0.05 and 0.95: {low600:.1f} at 600 K, {low650:.1f} at 650 K (J/mol of atoms)")
confirm(low650, SAVED["derived"]["high_650"]["lowest_curvature"], "Smallest curvature at 650 K: grid against analytic", tol=0.1)
confirm(min(low650, 0.0), 0.0, "The FCC curve bends up everywhere at 650 K", tol=1e-9)
top = SAVED["derived"]["gap_top_K"]
top_task01 = json.loads(Path("course/materials/cuni/results.json").read_text())["equilibrium"]["magnetic_on"]
top_task01 = top_task01["highest_sampled_T_with_two_FCC_K"]  # Task 01's 20 K grid, all four phases allowed
print(f"top of the miscibility gap (where the smallest G'' reaches zero): {top:.1f} K")
print(f"Task 01's grid last found two FCC compositions at {top_task01:.0f} K; the next grid row is {top_task01 + 20:.0f} K.")
assert 600 < top < 650 and top_task01 <= top < top_task01 + 20, "the gap top does not fit the curvatures or Task 01's grid"

# %% [markdown]
# The top of the gap printed above was found by the course script
# `gap_curve.py` from the analytic second derivative of the database's FCC
# energy: the temperature where the smallest $G''$ first reaches zero.
#
# ## 7. Limits (main track, 2 min)
#
# - **An assessed model, not an experiment.** Every number is what the
#   published Cu–Ni assessment predicts. The miscibility gap below about 642 K,
#   the spinodal and the driving force are predictions of that model, not
#   measurements.
# - **The magnetic term.** FCC_A1 includes the database's magnetic contribution;
#   Task 01, section 4, shows how much of the demixing it carries.
# - **Grid and finite differences.** Dips, slopes and spinodal points come from
#   a 0.001 grid and a step of 0.001; the after-your-attempt cells show they
#   agree with analytic derivatives and continuous minima to about 0.01 J/mol
#   of atoms and 0.001 in x(Ni).
# - **Bulk energies only.** The driving force is per mole of atoms of bulk new
#   phase; interfaces, elastic strain and kinetics are not in the model.
# - **One temperature and one composition** for the main example; the phases
#   allowed are FCC_A1 and LIQUID only.
#
# **Recap.** The equilibrium line of a published database is the common
# tangent, and its gap curve touches zero exactly at the phases in use. The
# quenched alloy's tangent gives a gap curve whose deepest dip is the driving
# force; the menu, its line and the gap curve bracket the answer, and adding the
# deepest state closes the bracket.
#
# Next: steps 13 and 14 of the advanced track, or
# [f4d · column generation](f4d_column_generation.ipynb) for the loop on the
# invented lens.
