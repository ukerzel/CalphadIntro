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
# # f5 · A binary in pycalphad
#
# **Learning question:** how does pycalphad represent the invented A–B model from
# f3 and f4, and how do you read what `equilibrium` returns, before using it on a
# real alloy?
#
# Used in: Lesson 8; before Task 01 (Cu–Ni); self-study before step 05 (optional).
# Do [f4](f4_two_phases_and_diagrams.ipynb) first: here pycalphad must reproduce it.
#
# **The route through the notebook.** In f3 and f4 you calculated the A–B model with your own formulas.
# Here the same model is handed to pycalphad, and every pycalphad number is
# compared with a value you already know. You will
#
# 1. read the database file and recognise each term of the model in it;
# 2. evaluate one phase at one composition with `calculate`;
# 3. find an equilibrium with `equilibrium` and learn to read its result;
# 4. scan temperature and draw a small miscibility gap.
#
# Only once the tool reproduces known numbers is it used on a real alloy (Task 01).
#
# Run the setup cell first; it makes the course code and the helper `check` available.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.4"
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
# ## 1. Read the database before solving anything
#
# Each phase has one set of sites that A or B can occupy, so the site fraction of B
# is the B atom fraction x. Compare the lines with f3: ALPHA's pure-A and pure-B
# energies are 1000 − 10T and 13000 − 10T (−9000 and +3000 J/mol at 1000 K); BETA
# has them swapped. `L(ALPHA,A,B;0)` is the interaction Ω, set by the function
# `LZERO` (0 in the file; the regular solution of f4 uses 20000 J/mol). The ideal
# mixing term RT·q(x) is added by pycalphad's phase model; it is not in the file.
#
# **How to read a TDB file.** A database (TDB) file is plain text. Each command
# ends with `!`; lines starting with `$` are comments.
#
# - `ELEMENT A ...` declares an element (here an invented one; its mass and
#   reference data are placeholders).
# - `FUNCTION LZERO 600 0; 1800 N !` defines a named function: from 600 K to
#   1800 K its value is `0`. `N` after the upper limit means "no further
#   temperature range".
# - `PHASE ALPHA % 1 1 !` declares a phase with **1** sublattice (set of sites)
#   carrying **1** site per formula unit.
# - `CONSTITUENT ALPHA :A,B: !` says that A or B can sit on that sublattice.
# - `PARAMETER G(ALPHA,A;0) 600 1000-10*T; 1800 N !` is the Gibbs energy of pure
#   A in the ALPHA structure, in J/mol, valid from 600 to 1800 K.
# - `PARAMETER L(ALPHA,A,B;0) ...` is the interaction parameter of A and B in
#   ALPHA; the `;0` marks the composition-independent (zeroth-order) term.
#
# From these entries pycalphad builds the molar Gibbs energy of ALPHA at B fraction
# x (J/mol of atoms):
#
# $$g_{\rm ALPHA}(x)=(1-x)\,G_{\rm A}+x\,G_{\rm B}+RT\,[x\ln x+(1-x)\ln(1-x)]+\Omega\,x(1-x),$$
#
# the weighted pure-element energies, plus the ideal mixing term, plus the
# interaction term. This is the same formula you used in f3 and f4.
#
# The cell below only prints the file. `Path` (from Python's `pathlib`) represents a
# file location; `.read_text()` returns the whole file as one string.

# %%
from pathlib import Path

TDB = Path("course/foundations/binary_family.tdb")   # relative to the course folder (the setup cell moved there)
print(TDB.read_text())

# %% [markdown]
# Find in the printout: the two `PHASE` lines, the four pure-element `G`
# parameters, the one `L` parameter, and the function `LZERO` it refers to.
# BETA has no `L` line, so it is always an ideal solution here.
#
# ## 2. One phase at one composition: `calculate`
#
# `calculate` evaluates a phase at the compositions you give (`points` are site
# fractions [A, B]), stable or not. At 1000 K and x = 0.20 ALPHA should give the
# step 02 value.
#
# First the file is read into a pycalphad `Database` object. Then the arguments
# of `calculate`, in order:
#
# | Argument | Meaning |
# |---|---|
# | `database` | the model, as read from the TDB file |
# | `["A", "B"]` | the components to include |
# | `"ALPHA"` | the phase to evaluate (one name, or a list) |
# | `T=1000, P=100000` | temperature in K and pressure in Pa |
# | `N=1` | total amount: 1 mol of atoms |
# | `points=np.array([[0.8, 0.2]])` | the states to evaluate: one row per state, one column per constituent in the order of the `CONSTITUENT` line (A, B); each row must add up to 1 |
# | `output="GM"` | the property to compute: molar Gibbs energy, J/mol of atoms |
# | `fake_points=False` | return only the points you asked for (no extra helper points) |
#
# The result is an **xarray Dataset**: a set of named arrays whose axes have names
# (here `N`, `P`, `T` and `points`) instead of only numbers. `point.GM` is the
# GM array; `.values` turns it into a plain numpy array; `.squeeze()` removes all
# axes of length 1, leaving a single number that `float(...)` prints.

# %%
import numpy as np
from pycalphad import Database, calculate, equilibrium, variables as v

database = Database(str(TDB))        # parse the TDB text into a model pycalphad can evaluate
point = calculate(database, ["A", "B"], "ALPHA", T=1000, P=100000, N=1,
                  points=np.array([[0.8, 0.2]]), output="GM", fake_points=False)   # site fractions y_A = 0.8, y_B = 0.2
print("ALPHA at x = 0.20, 1000 K: GM =", float(point.GM.values.squeeze()), "J/mol")

# %% [markdown]
# You can check this number by hand with the formula of section 1 (Ω = 0 here):
# weighted pure energies $0.8(-9000)+0.2(3000)=-6600$ J/mol, ideal mixing
# $8314.5\,[0.2\ln0.2+0.8\ln0.8]\approx-4161$ J/mol, total about −10761 J/mol.
#
# ### Your turn
#
# Predict GM for **homogeneous** ALPHA at x = 0.5 and 1000 K with Ω = 0, in J/mol
# to 4 significant figures. Use R = 8.3145 J/(mol K). Then change `points` above
# to check.
#
# "Homogeneous" means one single ALPHA solution at exactly this composition,
# whether or not it is the stable state; that is what `calculate` gives.
#
# In the cell below, replace `None` by your number and run it. `check` says whether
# your value matches the stored one (to about four significant figures) without
# showing the stored value; with `None` it only reminds you to try.

# %%
alpha_half = None  # J/mol
check(alpha_half, "f5_alpha_half")

# %% [markdown]
# ## 3. Reading an equilibrium result
#
# `calculate` evaluates a phase where you tell it to. `equilibrium` instead searches
# for the state of lowest total Gibbs energy: it decides which phases are present,
# how much of each, and at which compositions.
#
# `equilibrium` minimises G at fixed T, p, amount and overall composition z (here
# `v.X("B")`). The result is a labelled array (xarray) with one slot per
# **vertex**, a possible coexisting phase. pycalphad keeps one slot more than the
# number of components, so a binary has 3 vertex slots; slots that are not used
# have an empty phase name.
#
# - `Phase`: phase name per vertex; an empty name `''` is an unused slot, not a phase
# - `NP`: amount of each phase, per mole of atoms
# - `X`: composition inside each phase
# - `GM`: the minimum molar Gibbs energy of the whole sample
#
# The result also holds `MU`, the chemical potential of each component (J/mol),
# and `Y`, the site fractions inside each phase; they are not used in this
# notebook.
#
# **The conditions dictionary.** The fourth argument is a Python dictionary
# `{key: value, ...}` that fixes the state. The keys come from
# `pycalphad.variables`, imported as `v`:
#
# | Key | Meaning | Value here |
# |---|---|---|
# | `v.T` | temperature, K | 1000 |
# | `v.P` | pressure, Pa | 100000 (1 bar) |
# | `v.N` | total amount of atoms, mol | 1 |
# | `v.X("B")` | overall mole fraction of B in the whole sample, z | 0.5 |
#
# For a binary these four conditions fix the state completely; the overall
# fraction of A is then 1 − z. The third argument, `["ALPHA", "BETA"]`, lists the
# phases the search may use. A phase left out of this list can never appear in the
# answer.
#
# **Shape of the result.** Every array has one axis per condition (`N`, `P`, `T`,
# `X_B`), each of length 1 here, then `vertex` (length 3) and, for `X`, also
# `component` (A, B). The first `print` shows these lengths. `.sel(component="B")`
# picks the B entries by name. `NP` is `nan` ("not a number") in an unused slot.
#
# Two ideal phases ALPHA and BETA at z = 0.5 and 1000 K (f4 part A):

# %%
result = equilibrium(database, ["A", "B"], ["ALPHA", "BETA"],
                     {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5})   # K, Pa, mol, overall B fraction
# Pair each axis name with its length, e.g. {'N': 1, 'P': 1, ...}.
print("dimensions:", dict(zip(result.Phase.dims, result.Phase.shape)))
print("GM    :", float(result.GM.values.squeeze()))              # J/mol of atoms, whole sample
print("Phase :", result.Phase.values.squeeze())                  # one name per vertex slot
print("NP    :", result.NP.values.squeeze())                     # mol of each phase per mol of atoms
print("X(B)  :", result.X.sel(component="B").values.squeeze())   # B fraction inside each phase

# %% [markdown]
# Read the output column by column: slot 0 and slot 1 are used (ALPHA and BETA),
# slot 2 is empty. The amounts `NP` of the used slots add up to 1 mol, and the
# two `X(B)` values lie on either side of z = 0.5. That is the two-phase split you
# found in f4 part A. A mass balance check you can do in your head: the amounts
# times the compositions must add up to z.
#
# ### Your turn
#
# Now allow **only ALPHA** but give it Ω = 20000 J/mol
# (`parameters={"LZERO": 20000}`), at the same T and z. Before running: how many
# used vertices will there be, and what phase name will they have?
#
# Think back to the regular solution of f4 at 1000 K before you answer. Enter your
# count in the next cell; the cell after it runs the calculation.

# %%
used_vertices = None  # how many non-empty Phase entries
check(used_vertices, "f5_r1_vertices")

# %% [markdown]
# The next cell runs that calculation. `parameters={"LZERO": 20000}` replaces the
# value of the function `LZERO` for this one call; the file itself is not changed.
#
# The `for` loop walks through the three vertex slots together: `zip(a, b, c)`
# hands out the first entries of the three arrays, then the second entries, and
# so on. `if phase:` skips the unused slots, because an empty text `''` counts as
# False in Python.

# %%
regular = equilibrium(database, ["A", "B"], ["ALPHA"],
                      {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5},
                      parameters={"LZERO": 20000})   # Ω = 20000 J/mol for this call only
for phase, amount, x in zip(regular.Phase.values.squeeze(), regular.NP.values.squeeze(),
                            regular.X.sel(component="B").values.squeeze()):
    if phase:   # skip empty slots
        print(f"{phase}: amount {amount:.4f}, x(B) = {x:.6f}")

# %% [markdown]
# Two rows with the same name ALPHA: one phase model, two compositions (the
# miscibility gap of f4). Storing results in a dictionary keyed by phase name would
# silently keep only one of them. The energy GM belongs to the whole sample: do not
# add it once per row.
#
# The two compositions lie symmetrically about 0.5 because this model is symmetric
# in A and B apart from the linear term, which does not affect where the gap is.

# %% [markdown]
# ## 4. From one point to a scan to a small diagram
#
# Conditions can be arrays. One call scans temperature at z = 0.3; collecting the
# two compositions at each temperature draws the gap you built by hand in f4.
#
# `np.arange(600.0, 1201.0, 50.0)` gives 600, 650, …, 1200 K (the stop value 1201
# itself is not included). Passing this array as `v.T` makes pycalphad solve all
# 13 temperatures in one call; the `T` axis of the result then has length 13.
#
# To read one temperature, the loop indexes the arrays by position:
# `scan.Phase.values[0, 0, i, 0]` means N slot 0, P slot 0, temperature number `i`,
# X_B slot 0, and all vertex slots. `enumerate(temperatures)` gives the position
# `i` together with the value `T`.
#
# For every temperature with two used slots, the loop stores the lower and the
# higher composition in the list `gap` as a tuple `(T, x_low, x_high)`; these are
# the two sides of the miscibility gap at that temperature.

# %%
temperatures = np.arange(600.0, 1201.0, 50.0)   # K: 600, 650, …, 1200
scan = equilibrium(database, ["A", "B"], ["ALPHA"],
                   {v.T: temperatures, v.P: 100000, v.N: 1, v.X("B"): 0.3},
                   parameters={"LZERO": 20000})
gap = []   # will hold (T, lower x(B), upper x(B)) wherever two compositions coexist
print(" T (K)   phases and compositions x(B)")
for i, T in enumerate(temperatures):
    phases = scan.Phase.values[0, 0, i, 0]                   # 3 phase names (vertex slots) at this T
    xs = scan.X.sel(component="B").values[0, 0, i, 0]        # B fraction in each slot
    used = [(str(p), float(x)) for p, x in zip(phases, xs) if p]   # keep only the used slots
    print(f"{T:6.0f}   " + ", ".join(f"{p} {x:.4f}" for p, x in used))
    if len(used) == 2:   # two coexisting compositions: a point on each side of the gap
        gap.append((T, min(x for _, x in used), max(x for _, x in used)))

# %% [markdown]
# Read the table from the top: at low temperature z = 0.3 splits into two
# compositions; as T rises, the two compositions move towards each other.
#
# ### Your turn
#
# Above which temperature in this scan is z = 0.3 a single phase? (Give the lowest
# scanned temperature with one phase, in K.) Why is that below the critical
# temperature of about 1203 K, where the gap closes at x = 0.5?
#
# The critical temperature of the regular solution is $T_c=\Omega/(2R)$; with
# Ω = 20000 J/mol this is about 1203 K.

# %%
first_single_phase = None  # K
check(first_single_phase, "f5_single_phase_t")

# %% [markdown]
# ## After your attempt: pycalphad against the plain model, and three wrong problems
#
# The next cell does three things.
#
# 1. **Compare.** `confirm` checks the pycalphad numbers of this notebook against
#    the course's own plain-Python model (`binary_family`), which uses the formulas
#    of f3 and f4. `regular_binodal(T)` returns the two gap compositions at
#    temperature T.
# 2. **Three wrong problems** (Lesson 8.4). Each one gives a correct answer to a
#    different question:
#    - leaving BETA out of the phase list: pycalphad then finds the best state with
#      ALPHA alone, which is higher in energy than the true equilibrium with BETA;
#    - forgetting Ω: the homogeneous energy is lower by exactly
#      $\Omega\,x(1-x)=20000\cdot0.25=5000$ J/mol at x = 0.5;
#    - using the enthalpy of the equilibrium split as if it were the homogeneous
#      enthalpy (you meet this again in f6).
# 3. **Plot.** The grey lines are the gap from the plain model on a fine
#    temperature grid; the markers are the pycalphad compositions from the scan of
#    section 4. The dotted vertical line marks z = 0.3. Where the markers sit on
#    the lines, pycalphad and the plain model agree.

# %% cellView="form"
#@title After your attempt: run to compare and plot
import matplotlib.pyplot as plt
from course.foundations import binary_family as plain
from course.foundations.binary_family_tools import binary_equilibrium, homogeneous_properties

# 1. pycalphad results of this notebook against the lesson values (J/mol).
confirm(float(point.GM.values.squeeze()), -10760.595951, "ALPHA at x = 0.20 (step 02)", tol=1e-6)
confirm(float(result.GM.values.squeeze()), -10762.730017, "Two-phase minimum at z = 0.5 (step 03)", tol=1e-5)
# The two gap compositions found by pycalphad, sorted from low to high x(B).
xs = sorted(float(x) for p, x in zip(regular.Phase.values.squeeze(), regular.X.sel(component="B").values.squeeze()) if p)
reference = plain.regular_binodal(1000.0)["compositions"]   # the same gap from the plain formulas
confirm(xs[0], reference[0], "Gap composition at 1000 K, pycalphad vs plain model", tol=1e-6)

# 2. Three ways to answer a different question.
print("Three ways to answer a different question (Lesson 8.4):")
with_beta = binary_equilibrium(1000.0, 0.5, "I2")["GM"]   # "I2": ALPHA and BETA allowed, Ω = 0
alpha_only = equilibrium(database, ["A", "B"], ["ALPHA"], {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5})
print(f"  BETA left out: {float(alpha_only.GM.values.squeeze()):.6f} J/mol instead of {with_beta:.6f}")
confirm(float(alpha_only.GM.values.squeeze()), -8763.172233, "ALPHA-only result (a different question)", tol=1e-5)
with_omega = float(homogeneous_properties(1000.0, 0.5, "ALPHA", 20000.0)["GM"])   # homogeneous ALPHA, Ω = 20000
without_omega = float(homogeneous_properties(1000.0, 0.5, "ALPHA", 0.0)["GM"])    # homogeneous ALPHA, Ω = 0
print(f"  Ω forgotten: homogeneous GM {without_omega:.6f} instead of {with_omega:.6f} (lower by {with_omega - without_omega:.0f} J/mol)")
confirm(with_omega - without_omega, 5000.0, "Ω·x(1−x) at x = 0.5", tol=1e-6)
print("  Enthalpy of the equilibrium split is not the homogeneous enthalpy: equilibrium minimises G, not H.")

# 3. Plot: plain-model gap (lines) and pycalphad scan (markers).
T_fine = np.linspace(600, 1190, 60)                                 # K, stays below the critical temperature
pairs = [plain.regular_binodal(T)["compositions"] for T in T_fine]  # (left, right) gap edges at each T
fig, ax = plt.subplots(figsize=(5.5, 3.8))
ax.plot([p[0] for p in pairs], T_fine, "-", color="0.4", label="plain model (f4)")   # left edge; color "0.4" is a grey
ax.plot([p[1] for p in pairs], T_fine, "-", color="0.4")                             # right edge
ax.plot([g[1] for g in gap], [g[0] for g in gap], "o", label="pycalphad, z = 0.3")   # lower x(B) from the scan
ax.plot([g[2] for g in gap], [g[0] for g in gap], "s")                               # upper x(B) from the scan
ax.axvline(0.3, ls=":", color="0.5")   # vertical line at the overall composition z = 0.3
ax.set(xlabel="x(B)", ylabel="T (K)", title="Miscibility gap: pycalphad on the f4 model")
ax.legend()
plt.show()

# %% [markdown]
# **Limits.** The same invented model as f3/f4; agreement shows pycalphad reads it
# as intended, not that it describes a real alloy. The equilibrium search samples
# trial compositions and refines them (the `pdens` setting you will meet in Task 01).
# Next: [Task 01 · Cu–Ni equilibria](task01_cuni_equilibria.ipynb).
