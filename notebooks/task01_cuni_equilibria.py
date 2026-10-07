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
# # Task 01 · Cu–Ni phase equilibria with a published database
#
# **Learning question:** what does a published Cu–Ni assessment predict for the
# phases, their compositions and amounts, and how much of the low-temperature
# demixing comes from the magnetic term?
#
# Used in: Task 01, self-study step 05. Do [f5](f5_binary_pycalphad.ipynb) first:
# reading Phase, NP and X works exactly as there. Work each "your turn" on paper
# or in a scratch cell first, then type your value.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.1"
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
# ## 1. Get the database
#
# The calculation uses S. an Mey's assessment of Cu–Ni as adapted in B. Hallstedt's
# SGTE collection of binary datasets, published as the file `CuNi-92Mey-LB.tdb`
# ([direct download](https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb),
# [listing on phasediagrams.org](https://phasediagrams.org/phase-diagram/CuNi-92Mey-LB.tdb)).
# You fetch it into your own session; it is not part of the course files. Cite:
#
# - S. an Mey, "Thermodynamic re-evaluation of the Cu–Ni system," *Calphad* 16
#   (1992) 255–260, [doi:10.1016/0364-5916(92)90022-P](https://doi.org/10.1016/0364-5916(92)90022-P)
# - B. Hallstedt, "The SGTE collection of binary datasets," *Calphad* 89 (2025)
#   102833, [doi:10.1016/j.calphad.2025.102833](https://doi.org/10.1016/j.calphad.2025.102833)
#
# Set `DOWNLOAD = True` to fetch the file (6,789 bytes); the cell checks its size
# and SHA-256 and keeps it outside the course folder. If you already have the
# file, set the environment variable `CALPHAD_CUNI_TDB` to its path. Without the
# file the notebook runs in **no-database mode**: every cell then reads the saved
# results of the course run, so the balances, the lever rule and the diagram
# still work. Only section 2 and the file column of section 7 need the file itself.

# %%
import json
from pathlib import Path

DOWNLOAD = False   # True: fetch CuNi-92Mey-LB.tdb into your session
TDB = database("cuni", download=DOWNLOAD)
LIVE = TDB is not None
SAVED = json.loads(Path("course/materials/cuni/results.json").read_text())
if LIVE:
    print("Live mode: the cells below calculate with your copy of the database.")
else:
    print("No-database mode: the cells below read the saved course results\n"
          "(course/materials/cuni/results.json and course/self_study/generated/cuni_grid.json).")

# %% [markdown]
# ## 2. Read one database branch by hand (exercise 1)
#
# A database is a text file. Each `FUNCTION` or `PARAMETER` (`PAR`) statement ends
# with `!` and gives a lower temperature limit, then an expression in T ending in
# `;`, then the upper limit of that range and `Y` (another range follows) or `N`
# (last range). A blank limit, as in `,,` right after the parameter name, means
# "use the program's default": pycalphad then starts the range at 0.01 K, and a
# blank upper limit leaves the range open. A name inside an expression refers to
# another function in the file.
# `G(LIQUID,CU)` is the Gibbs energy of pure liquid Cu relative to the standard
# element reference (SER), in J/mol of atoms; `LN` is the natural logarithm.
#
# The cell prints only that parameter and the functions it refers to, read from
# **your** file at run time.

# %%
import re


def statements(path):
    """The file's statements (each up to its '!'), with comment lines ($) removed."""
    lines = [line for line in path.read_text().splitlines() if not line.lstrip().startswith("$")]
    return [" ".join(s.split()) + " !" for s in "\n".join(lines).split("!") if s.strip()]


if LIVE:
    STATEMENTS = statements(TDB)
    functions = {s.split()[1].upper(): s for s in STATEMENTS if s.upper().startswith("FUNCTION")}
    todo = [next(s for s in STATEMENTS if re.match(r"PAR\w*\s+G\(LIQUID,CU\)", s, re.I))]
    shown = []
    while todo:  # follow the function names the statement refers to
        statement = todo.pop(0)
        shown.append(statement)
        for name in re.findall(r"[A-Z_][A-Z0-9_]*", statement.upper()):
            if name in functions and functions[name] not in shown + todo:
                todo.append(functions[name])
    for statement in shown:
        print(statement, end="\n\n")
else:
    print("Skipped: this exercise needs your copy of the database; the rest of the notebook runs without it.")

# %% [markdown]
# ### Your turn
#
# Pick the temperature range of the liquid Cu branch that contains 1500 K, set
# T = 1500 and evaluate it with a calculator or a scratch cell. If that range
# refers to another function, evaluate that one at 1500 K as well and add it.

# %%
g_liquid_cu_1500 = None  # J/mol of atoms, pure liquid Cu at 1500 K, to 0.01 J/mol (a neighbouring range differs by a few J/mol)
if LIVE:
    check(g_liquid_cu_1500, "task01_liquid_cu_1500")
else:
    print("Skipped: this exercise needs your copy of the database.")

# %% [markdown]
# ## 3. Phases, conditions and units; one equilibrium point
#
# | Setting | Value |
# |---|---|
# | phases allowed | LIQUID, FCC_A1, BCC_A2, HCP_A3 |
# | components | CU, NI and VA (vacancy) |
# | pressure | 101325 Pa |
# | amount | N = 1 mol of atoms |
# | overall composition | x(Ni), atom fraction |
# | sampling setting | `pdens = 60` (trial points per degree of freedom in the starting grid) |
#
# Output as in f5: `GM` is the Gibbs energy of the whole sample in J/mol of atoms,
# `NP` is each phase's amount as a fraction of the atoms, `X` is the composition
# inside each phase. FCC_A1 is written with a second, interstitial sublattice that
# holds only vacancies here (so that C or N can be added later); empty sites add no
# atoms, so FCC energies are per one mole of atoms, not two.
#
# One point: T = 600 K, overall x(Ni) = 0.5, all four phases allowed.

# %%
import numpy as np
from pycalphad import Model, equilibrium, variables as v
from course.materials.cuni import worked_example as cuni  # the Task 01 course script

PHASES = cuni.PHASES          # LIQUID, FCC_A1, BCC_A2, HCP_A3
COMPONENTS = cuni.COMPONENTS  # CU, NI, VA
P = cuni.PRESSURE             # Pa
PDENS = 60
SAVED_KEY = {600: "600", 1500: "1500", 1540: "FCC_liquid_example", 1600: "1600"}
if LIVE:
    db = cuni.load_source(TDB)  # checks the pycalphad version and the file, then reads it


def rows_at(T, magnetic=True):
    """[(phase, amount NP, x(Ni) in that phase)] at T (K) and overall x(Ni) = 0.5."""
    if LIVE:
        options = {} if magnetic else {"model": cuni.MagneticOffModel}
        eq = equilibrium(db, COMPONENTS, PHASES, {v.T: T, v.X("NI"): 0.5, v.P: P, v.N: 1},
                         calc_opts={"pdens": PDENS}, **options)
        return [(str(p), float(n), float(x)) for p, n, x in
                zip(eq.Phase.values.squeeze(), eq.NP.values.squeeze(), eq.X.sel(component="NI").values.squeeze())
                if p and n > 1e-8]
    if T not in SAVED_KEY:
        raise ValueError(f"No saved results at {T} K in no-database mode. Saved temperatures: "
                         f"{', '.join(map(str, SAVED_KEY))} K. Fetch the database to calculate other temperatures.")
    mode = "magnetic_on" if magnetic else "magnetic_off"
    sample = SAVED["equilibrium"][mode]["samples"][SAVED_KEY[T]]
    return [(r["phase"], r["atom_mole_fraction"], r["x_NI"]) for r in sample["phases"]]


def show(rows, title):
    print(title)
    print(f"  {'phase':<8} {'amount NP':>20} {'x(Ni) in phase':>20}")
    for phase, amount, x in rows:
        print(f"  {phase:<8} {amount:20.15f} {x:20.15f}")


if LIVE:
    point = equilibrium(db, COMPONENTS, PHASES, {v.T: 600, v.X("NI"): 0.5, v.P: P, v.N: 1},
                        calc_opts={"pdens": PDENS})
    print("GM    :", float(point.GM.values.squeeze()), "J/mol of atoms")
    print("Phase :", point.Phase.values.squeeze())
    print("NP    :", point.NP.values.squeeze())
    print("X(NI) :", point.X.sel(component="NI").values.squeeze(), "\n")
rows_600 = rows_at(600)
show(rows_600, "600 K, overall x(Ni) = 0.5, magnetic contribution on")

# %% [markdown]
# ### Your turn
#
# Reconstruct the overall composition from the rows above: weight each phase's
# composition by its amount, $\sum_i NP_i\,x_i(\mathrm{Ni})$, and the same for Cu
# with $1-x_i(\mathrm{Ni})$. Why can both rows be called FCC_A1?

# %%
ni_from_phases = None        # Σ NP·x(Ni)
cu_from_phases = None        # Σ NP·(1 − x(Ni))
one_phase_two_compositions = None  # True or False: is this one phase model at two compositions?
check(ni_from_phases, "task01_ni_balance_600")
check(cu_from_phases, "task01_cu_balance_600")
check(one_phase_two_compositions, "task01_same_fcc_600")

# %% [markdown]
# ## 4. Magnetic contribution on and off
#
# Ni-rich FCC is ferromagnetic, and the database adds a magnetic Gibbs energy term
# to FCC_A1. The magnetic contribution is the lowering of the Gibbs energy by the
# ordering of the atomic magnetic moments, mostly below the Curie temperature; the
# database gives it through each phase's Curie temperature `TC` and mean magnetic
# moment `BM`. `MagneticOffModel` in the course script is pycalphad's `Model` with
# only that term set to zero; the chemical terms, the phases and the conditions
# stay the same. It is a comparison, not a real nonmagnetic alloy. The total
# energy already contains the magnetic part, so it is never added a second time.

# %%
import inspect

print(inspect.getsource(cuni.MagneticOffModel))
rows_600_off = rows_at(600, magnetic=False)
show(rows_600_off, "600 K, overall x(Ni) = 0.5, magnetic contribution off")

# %% [markdown]
# ### Your turn
#
# Does switching the magnetic contribution off make the demixing at 600 K
# disappear? Compare the two tables.

# %%
demixing_disappears = None  # True or False
check(demixing_disappears, "task01_demixing_disappears")

# %% [markdown]
# ## 5. The lever rule where FCC and liquid coexist (exercise 3)
#
# On the 20 K grid, 1540 K is the first temperature at overall x(Ni) = 0.5 with
# both liquid and FCC present. The cell prints which phases are present at 1500,
# 1540 and 1600 K, and their compositions (magnetic contribution on).

# %%
for T in (1500, 1540, 1600):
    print(f"{T} K:", ", ".join(f"{phase} at x(Ni) = {x:.15f}" for phase, _, x in rows_at(T)))

# %% [markdown]
# ### Your turn
#
# With overall composition $z = 0.5$ and the two phase compositions at 1540 K,
# the balance $f_L + f_{FCC} = 1$ and $f_L x_L + f_{FCC} x_{FCC} = z$ gives the
# lever rule
#
# $$f_L=\frac{x_{FCC}-z}{x_{FCC}-x_L}.$$
#
# Compute both amounts (fractions of the atoms). Which single phase is present at
# 1600 K?

# %%
f_liquid_1540 = None  # fraction of atoms in LIQUID
f_fcc_1540 = None     # fraction of atoms in FCC_A1
phase_1600 = None     # phase name, e.g. "FCC_A1"
check(f_liquid_1540, "task01_lever_liquid_1540")
check(f_fcc_1540, "task01_lever_fcc_1540")
check(phase_1600, "task01_phase_1600")

# %% [markdown]
# ## 6. The phase diagram
#
# The full grid of the course run: 81 temperatures from 300 to 1900 K (20 K steps)
# times 61 overall compositions x(Ni) from 0.005 to 0.995, both magnetic settings,
# with the settings of section 3. With your database the cell recomputes it with
# the course export code, which also checks it against the saved samples (up to
# about 1 minute on a laptop); without it, the cell reads the saved grid.
#
# **Reading the plot:** each marker is the composition of a phase found at one grid
# temperature. Where the sample is one phase, the markers fill the area; in a
# two-phase region no single phase has that composition, so the area stays empty,
# and at one temperature the markers on its two sides are the ends of a tie line.
# The empty band near the top is the liquid/FCC lens; the empty dome at the bottom
# is the FCC miscibility gap. A second figure zooms on the thin lens.

# %%
import matplotlib.pyplot as plt
from course.self_study.grid_export import export_cuni

if LIVE:
    print("Computing 2 × 81 × 61 equilibria (up to about 1 minute) ...")
    grid = export_cuni(TDB)
else:
    grid = json.loads(Path("course/self_study/generated/cuni_grid.json").read_text())
T_GRID = np.array(grid["T_K"])
X_GRID = np.array(grid["x"])
STYLE = {"LIQUID": dict(marker="o", color="C0"), "FCC_A1": dict(marker="s", color="C1"),
         "BCC_A2": dict(marker="^", color="C2"), "HCP_A3": dict(marker="D", color="C3")}


def phase_points(mode):
    """{phase: (x(Ni) in the phase, T)} for every phase with a positive amount on the grid."""
    out = {}
    for it, row in enumerate(grid["modes"][mode]):
        for cell in row:  # one overall composition
            for index, amount, x in cell:
                out.setdefault(grid["phases"][index], []).append((x, T_GRID[it]))
    return {phase: np.array(xy) for phase, xy in out.items()}


def tie_lines(mode, it):
    """Distinct two-phase samples at grid row it: ((phase, x(Ni)), (phase, x(Ni)))."""
    return sorted({tuple((grid["phases"][i], round(x, 3)) for i, n, x in cell)
                   for cell in grid["modes"][mode][it] if len(cell) == 2})


fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, mode in zip(axes[:2], ("magnetic_on", "magnetic_off")):
    for phase, xy in phase_points(mode).items():
        ax.scatter(xy[:, 0], xy[:, 1], s=6, label=phase, **STYLE[phase])
    ax.set(title=mode.replace("_", " "), xlabel="x(Ni) in the phase", ylabel="T (K)",
           xlim=(0, 1), ylim=(300, 1900))
    ax.legend(markerscale=2)
for mode, style in (("magnetic_on", dict(ls="-", marker="o", color="C1")),
                    ("magnetic_off", dict(ls="--", marker="s", mfc="none", color="k"))):
    ends = [(T_GRID[it], *[x for p, x in pair])  # the two FCC compositions at each row
            for it in range(len(T_GRID)) if T_GRID[it] <= 720
            for pair in tie_lines(mode, it)[:1] if all(p == "FCC_A1" for p, x in pair)]
    T_ends, x_left, x_right = np.array(ends).T
    axes[2].plot(x_left, T_ends, label=f"two FCC_A1, {mode.replace('_', ' ')}", **style)
    axes[2].plot(x_right, T_ends, **style)
axes[2].set(title="Zoom: ends of the two-FCC tie lines", xlabel="x(Ni) in the phase", ylabel="T (K)",
            xlim=(0, 1), ylim=(290, 730), yticks=np.arange(300, 721, 20))
axes[2].tick_params(axis="y", labelsize=8)
axes[2].grid(ls=":")
axes[2].legend(loc="lower center")
fig.suptitle("Cu–Ni, 101325 Pa: phase compositions found on the grid")
fig.tight_layout()
plt.show()

print("Table: two-phase samples (tie-line ends, x(Ni) in each phase) at selected temperatures")
for T in (400, 500, 1400, 1500, 1600, 1700):
    it = int(np.argmin(np.abs(T_GRID - T)))
    for mode in ("magnetic_on", "magnetic_off"):
        ends = tie_lines(mode, it)
        text = "; ".join(" + ".join(f"{p} {x:.3f}" for p, x in pair) for pair in ends) or "one phase at every x(Ni)"
        print(f"  {T_GRID[it]:6.0f} K  {mode:<13} {text}")

# Zoom on the thin liquid/FCC lens (magnetic contribution on): the two ends of the
# liquid + FCC tie line at each grid temperature where the grid found one.
lens = [(T_GRID[it], dict(pair)["LIQUID"], dict(pair)["FCC_A1"]) for it in range(len(T_GRID))
        for pair in tie_lines("magnetic_on", it)[:1] if {p for p, x in pair} == {"LIQUID", "FCC_A1"}]
T_lens, x_liquid, x_solid = np.array(lens).T
fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.plot(x_liquid, T_lens, ls="-", marker="o", color="C0", label="LIQUID end (liquidus)")
ax.plot(x_solid, T_lens, ls="--", marker="s", color="C1", label="FCC_A1 end (solidus)")
ax.set(title="Zoom: the liquid/FCC lens, magnetic on", xlabel="x(Ni) in the phase", ylabel="T (K)",
       xlim=(0, 1), ylim=(T_lens.min() - 40, T_lens.max() + 40))
ax.grid(ls=":")
ax.legend()
fig.tight_layout()
plt.show()
print("Table: lens tie-line ends (magnetic on)")
for T, xl, xs in lens:
    print(f"  {T:6.0f} K  LIQUID {xl:.3f}  FCC_A1 {xs:.3f}")

# %% [markdown]
# ### Your turn
#
# Use the zoomed panel (each marker row is one grid temperature) or the `grid`
# data, where a cell with two FCC_A1 entries is a two-FCC sample. What is the highest grid temperature with two FCC compositions,
# with and without the magnetic contribution? Why does the difference between the
# two not measure the magnetic shift of the critical temperature exactly?

# %%
top_two_fcc_on = None   # K, magnetic on
top_two_fcc_off = None  # K, magnetic off
check(top_two_fcc_on, "task01_gap_top_on")
check(top_two_fcc_off, "task01_gap_top_off")

# %% [markdown]
# ## 7. The paper's numbers and the file's numbers (exercise 5)
#
# The course ships a transcription of four interaction rows from Mey's Table 2
# (printed p. 257): $L_\nu(T)=a_\nu+b_\nu T$ in J/mol, with the excess term
# $x_{Cu}x_{Ni}\sum_\nu L_\nu (x_{Cu}-x_{Ni})^\nu$. With your database the cell
# also prints the same four parameters from your file.

# %%
import csv

with open("course/materials/cuni/mey1992_binary_parameters.csv") as handle:
    PAPER = list(csv.DictReader(handle))
print("Mey (1992), Table 2, as printed:")
print(f"  {'phase':<8} {'order':>5} {'a (J/mol)':>12} {'b (J/(mol K))':>14}")
for row in PAPER:
    print(f"  {row['phase']:<8} {row['rk_order']:>5} {float(row['a_J_per_mol']):12.2f} {float(row['b_J_per_mol_K']):14.5f}")
if LIVE:
    print("\nYour file:")
    for statement in STATEMENTS:
        if re.match(r"PAR\w*\s+L\((LIQUID|FCC_A1),CU,NI(:VA)?;[01]\)", statement, re.I):
            print(" ", statement)

# %% [markdown]
# ### Your turn
#
# Compare the two sets row by row. The coefficients were fitted to measured data.
# If a calculation reproduces them, has the model been checked independently
# against experiment? Why should the paper's numbers and the file's numbers keep
# separate labels?

# %%
independent_validation = None  # True or False
check(independent_validation, "task01_independent_validation")

# %% [markdown]
# ## 8. After your attempt
#
# The cells below reproduce the course values. With your database they recompute
# them; without it they check the saved files against each other. Full answers:
# [course/materials/cuni/answers.md](../course/materials/cuni/answers.md).

# %% cellView="form"
#@title After your attempt: the liquid Cu branch and the magnetic term
energies = SAVED["energy_checks"]
if LIVE:
    liquid = Model(db, COMPONENTS, "LIQUID")
    g_cu = cuni.evaluate(liquid, liquid.GM, 1500, 0.0)  # x(Ni) = 0: pure Cu
    print(f"pycalphad, pure liquid Cu at 1500 K: {g_cu:.8f} J/mol of atoms")
    confirm(g_cu, energies["hand_pure_Cu_liquid_J_per_mol_atoms"], "Pure liquid Cu at 1500 K (hand value)", tol=1e-8)
    g_ni = cuni.evaluate(liquid, liquid.GM, 1500, 1.0)
    confirm(g_ni, energies["pure_liquid_1500K_J_per_mol_atoms"]["NI"], "Pure liquid Ni at 1500 K", tol=1e-8)
    live = cuni.energy_checks(db)  # stops if a check fails
    print(f"largest |GM(on) − GM(off) − magnetic term| over 16 FCC states: "
          f"{live['max_magnetic_control_abs_difference']:.2e} J/mol")
    confirm(live["max_magnetic_control_abs_difference"], 0.0, "Magnetic on − off equals the magnetic term", tol=1e-8)
    print("FCC_A1: G per formula unit equals GM per mole of atoms (the vacancy sites add no atoms).")
else:
    confirm(energies["evaluator_pure_Cu_liquid_J_per_mol_atoms"], energies["hand_pure_Cu_liquid_J_per_mol_atoms"],
            "Saved pycalphad value against the saved hand value", tol=1e-8)
    print("Run with the database to recompute the energies.")

# %% cellView="form"
#@title After your attempt: balances, magnetic off and the lever rule
for magnetic, mode in ((True, "magnetic_on"), (False, "magnetic_off")):
    for T in (600, 1540):
        rows = rows_at(T, magnetic)
        ni = sum(n * x for _, n, x in rows)
        cu = sum(n * (1 - x) for _, n, x in rows)
        amounts = sum(n for _, n, _ in rows)
        print(f"{mode}, {T} K: Σ NP·x(Ni) = {ni:.9f}, Σ NP·x(Cu) = {cu:.9f}, Σ NP = {amounts:.9f}")
        confirm(ni, 0.5, f"Ni balance ({mode}, {T} K)", tol=1e-6)
        confirm(cu, 0.5, f"Cu balance ({mode}, {T} K)", tol=1e-6)
        saved = SAVED["equilibrium"][mode]["samples"][SAVED_KEY[T]]["phases"]
        for (phase, n, x), ref in zip(rows, saved):
            assert phase == ref["phase"], f"{phase} where the course run has {ref['phase']}"
            confirm(n, ref["atom_mole_fraction"], f"  {phase} amount", tol=1e-6)
            confirm(x, ref["x_NI"], f"  {phase} x(Ni)", tol=1e-6)
print("Both settings keep two FCC_A1 compositions at 600 K: the chemical terms alone already demix.")

composition = {phase: x for phase, _, x in rows_at(1540)}
x_l, x_fcc = composition["LIQUID"], composition["FCC_A1"]
f_l = (x_fcc - 0.5) / (x_fcc - x_l)
print(f"Lever rule at 1540 K: f_L = ({x_fcc:.6f} − 0.5)/({x_fcc:.6f} − {x_l:.6f}) = {f_l:.6f}, f_FCC = {1 - f_l:.6f}")
confirm(f_l, SAVED["equilibrium"]["magnetic_on"]["samples"]["FCC_liquid_example"]["phases"][0]["atom_mole_fraction"],
        "Liquid amount from the lever rule", tol=1e-6)

if LIVE:  # energy curves at 1600 K: the overall composition stays at 0.5
    from pycalphad import calculate
    xs = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for phase, points in (("FCC_A1", np.column_stack([1 - xs, xs, np.ones_like(xs)])),
                          ("LIQUID", np.column_stack([1 - xs, xs]))):
        for model, style, label in ((Model, dict(ls="-", marker="o"), "on"),
                                    (cuni.MagneticOffModel, dict(ls="--", marker="x"), "off")):
            curve = calculate(db, COMPONENTS, phase, T=1600, P=P, N=1, points=points, model=model)
            ax.plot(xs, curve.GM.values.ravel(), color="C1" if phase == "FCC_A1" else "C0",
                    markevery=25, label=f"{phase}, magnetic {label}", **style)
    ax.axvline(0.5, ls=":", color="0.5", label="overall x(Ni) = 0.5")
    ax.set(xlabel="x(Ni)", ylabel="GM (J/mol of atoms)",
           title="1600 K: homogeneous phases (on and off nearly coincide)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print("At 1600 K, x(Ni) = 0.5 lies outside that temperature's liquid/FCC tie line (table in section 6),\n"
          "so the sample is all liquid. The liquid curve's lowest point is at another composition, but the\n"
          "alloy's overall x(Ni) stays 0.5: equilibrium minimises G at fixed composition.")
else:  # the saved figure of the course run: 600 K and 1600 K curves, pure Ni magnetic term
    print("Saved energy curves from the course run (course/materials/cuni/energy_magnetism.png):")
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.imshow(plt.imread("course/materials/cuni/energy_magnetism.png"))
    ax.axis("off")
    plt.show()

# %% cellView="form"
#@title After your attempt: the top of the miscibility gap on the grid
for mode in ("magnetic_on", "magnetic_off"):
    rows = grid["modes"][mode]
    two_fcc = [T for T, row in zip(T_GRID, rows)
               if any(sum(1 for i, n, x in cell if grid["phases"][i] == "FCC_A1") >= 2 for cell in row)]
    print(f"{mode}: highest grid temperature with two FCC_A1 compositions = {max(two_fcc):.0f} K")
    confirm(max(two_fcc), SAVED["equilibrium"][mode]["highest_sampled_T_with_two_FCC_K"],
            f"Top of the two-FCC region ({mode})", tol=1e-6)
print("Grid temperatures are 20 K apart, so each top lies somewhere up to 20 K above the value found.")
if LIVE:  # the recomputed grid against the saved one (both rounded to 6 digits)
    saved_grid = json.loads(Path("course/self_study/generated/cuni_grid.json").read_text())
    largest = 0.0
    for mode in grid["modes"]:
        for row, saved_row in zip(grid["modes"][mode], saved_grid["modes"][mode]):
            for cell, saved_cell in zip(row, saved_row):
                assert [c[0] for c in cell] == [c[0] for c in saved_cell], "phase sets differ from the saved grid"
                largest = max([largest] + [abs(a - b) for c, ref in zip(cell, saved_cell) for a, b in zip(c[1:], ref[1:])])
    confirm(largest, 0.0, "Recomputed grid against the saved grid (rounded to 6 digits)", tol=2e-6)

# %% cellView="form"
#@title After your attempt: paper and file side by side
if LIVE:
    file_rows = {}
    for statement in STATEMENTS:
        match = re.match(r"PAR\w*\s+L\((LIQUID|FCC_A1),CU,NI(?::VA)?;([01])\),,\s*([+-]?[\d.]+)\s*([+-][\d.]+)\*T;",
                         statement, re.I)
        if match:
            file_rows[(match[1].upper(), match[2])] = (float(match[3]), float(match[4]))
    print(f"{'phase':<8} {'order':>5} {'a paper':>10} {'a file':>10} {'b paper':>9} {'b file':>9}  same?")
    for row in PAPER:
        a, b = float(row["a_J_per_mol"]), float(row["b_J_per_mol_K"])
        fa, fb = file_rows[(row["phase"], row["rk_order"])]
        print(f"{row['phase']:<8} {row['rk_order']:>5} {a:10.2f} {fa:10.2f} {b:9.5f} {fb:9.5f}  "
              f"{'yes' if abs(a - fa) < 1e-9 and abs(b - fb) < 1e-9 else 'no'}")
else:
    print("Run with the database to put the file's four parameters next to the paper's.")
print("Agreement with fitted coefficients is not a test against experiment: the coefficients were chosen\n"
      "to fit measurements. Where paper and file differ, both keep their own label; neither is corrected here.")

# %% [markdown]
# **Limits.** One published database in one pinned program (pycalphad 0.11.2).
# The diagram is sampled on a 20 K × 61-composition grid, so boundaries and the
# gap top are only as sharp as the grid; BCC_A2 and HCP_A3 were allowed but never
# appeared, which does not prove they are unstable everywhere. The magnetic-off
# run is a comparison, not a real alloy. Agreement with the paper's figures or
# coefficients is not a validation against experiment.
# Answers: [course/materials/cuni/answers.md](../course/materials/cuni/answers.md).
# Next: [f6 · fitting with synthetic data](f6_fitting_synthetic.ipynb), then
# [Task 02 · fitting two Cu–Ni interaction values](task02_cuni_activity_fit.ipynb).
