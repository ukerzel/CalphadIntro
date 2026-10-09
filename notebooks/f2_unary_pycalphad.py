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
# # f2 · The same model in pycalphad
#
# **Learning question:** how does a CALPHAD program store the f1 model, and what
# is the difference between *loading*, *calculating* and *finding the equilibrium*?
#
# Used in: Day 1 W7 (demonstration), Lesson 2, Task 00 (second part), self-study
# step 01 (optional). Do [f1](f1_unary_by_hand_and_code.ipynb) first.
# Labels such as (W4), (D1), (Lesson 5) or Clinic D point to the printed one-day
# primers (Day 1 and Day 2 worksheets) and the detailed lessons of the classroom
# course in the repository. Working alone on the website, you only need the step
# numbers.
#
# **The plan.** In f1 you wrote the two Gibbs lines yourself in Python. A CALPHAD
# program does the same job, but reads the model from a *database file* (a TDB
# file) instead of from your code. Here the database holds exactly the f1 model,
# so every number pycalphad gives must agree with f1. That makes this notebook a
# safe place to learn the three pycalphad steps before they are used on real
# databases: load the model, evaluate one phase, and minimise over all phases.

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
# ## 1. A database can be very small (W7)
#
# The course's invented model is stored as a TDB file. Each `PARAMETER` line holds
# one phase's Gibbs energy: a lower temperature limit, the expression, the upper
# limit, `N` (no further range) and `!` (end of record). Compare with f1:
# SOLID 1000 − 10T, LIQUID 7000 − 16T.
#
# **The Python.** `Path` (from Python's built-in `pathlib`) represents a file name.
# The path is relative to the course folder, which the setup cell made the working
# folder. `TDB.read_text()` reads the whole file as text and `print` shows it.
#
# **How to read the file.** A TDB file is plain text made of *records*, each ending
# with `!`.
#
# - Lines starting with `$` are comments.
# - `ELEMENT A …` declares the element A. The other entries on that line (a
#   reference phase name, an atomic mass and two reference values) are
#   placeholders here.
# - `TYPE_DEFINITION % …` defines the code letter `%` that the PHASE lines refer
#   to; here it adds nothing special.
# - `PHASE SOLID % 1 1 !` declares a phase named SOLID with one *sublattice* (a set
#   of equivalent atom sites) holding 1 site per formula unit.
# - `CONSTITUENT SOLID :A: !` says which species may sit on that sublattice: only A.
# - `PARAMETER G(SOLID,A;0) 800 1000-10*T; 1200 N !` gives the Gibbs energy G of
#   SOLID filled with A, in J/mol, as the expression `1000-10*T`, valid from 800 K
#   to 1200 K. The `;0` is an order number, which matters only for mixtures (f3
#   onwards).

# %%
from pathlib import Path

TDB = Path("course/foundations/one_component_model.tdb")   # relative to the course folder
print(TDB.read_text())   # show the database file exactly as stored

# %% [markdown]
# ## 2. Load, calculate, minimise
#
# | Action | pycalphad | What it does here |
# |---|---|---|
# | Load | `Database` | reads the two phase models; no equilibrium yet |
# | Evaluate | `calculate` | one phase's property at given conditions, even the higher branch |
# | Minimise | `equilibrium` | the lowest total G over the allowed phases and amounts |
#
# Conditions: T in K, p = 100000 Pa, N = 1 mol of atoms. `GM` is the molar Gibbs
# energy in J/mol. The first pycalphad call takes a few seconds.
#
# **The pycalphad names in the next cell.**
#
# - `Database(str(TDB))` reads the file into a Python object that holds the phase
#   models. (`str(...)` turns the `Path` into a plain text file name.)
# - `components` lists the elements taking part, `phases` the phase names to
#   consider. Both must match names in the database.
# - `calculate(database, components, "SOLID", T=..., P=..., output="GM")` evaluates
#   the molar Gibbs energy of the SOLID phase at each listed temperature, at
#   P = 100000 Pa. It does **not** ask which phase is stable; it simply evaluates
#   the one phase it is given. pycalphad writes pressure as `P` (in Pa).
# - The result is an *xarray Dataset*: a set of labelled arrays. `solid_result.GM`
#   picks the array of molar Gibbs energies. Its dimensions are named
#   `(N, P, T, points)`: one entry per amount, pressure, temperature and sampled
#   internal state of the phase. Here the shape is (1, 1, 5, 1), because only the
#   temperature takes several values. `.values` gives the plain NumPy array and
#   `.reshape(-1)` flattens it to a simple row of 5 numbers.

# %%
from pycalphad import Database, calculate, equilibrium, variables as v   # v holds the condition names v.T, v.P, v.N

database = Database(str(TDB))            # load: read the phase models, nothing calculated yet
components = ["A"]                       # the only element
phases = ["SOLID", "LIQUID"]             # the phases the minimiser may use later
temperatures = [800.0, 900.0, 1000.0, 1100.0, 1200.0]   # K

# evaluate SOLID only: molar Gibbs energy GM (J/mol) at each temperature, P in Pa
solid_result = calculate(database, components, "SOLID", T=temperatures, P=100000, output="GM")
print("SOLID GM:", solid_result.GM.values.reshape(-1))   # shape (1, 1, 5, 1) flattened to 5 values

# %% [markdown]
# **What to look at.** The five numbers are J/mol, one per temperature from 800 K
# to 1200 K. Compare them with the SOLID column of the table in f1 section 2.
#
# ### Your turn
#
# Before running the next cell, predict the LIQUID value at 1200 K (J/mol).
# Why is it fine to *evaluate* the liquid at 900 K, where it is not stable?

# %%
liquid_1200 = None  # J/mol
check(liquid_1200, "f2_gl_1200")

# %% [markdown]
# The next cell is the same `calculate` call for the LIQUID phase. It prints
# LIQUID values at all five temperatures, including those where LIQUID is not the
# lower of the two.

# %%
liquid_result = calculate(database, components, "LIQUID", T=temperatures, P=100000, output="GM")
print("LIQUID GM:", liquid_result.GM.values.reshape(-1))   # J/mol, 800 … 1200 K

# %% [markdown]
# ## 3. Ask for the equilibrium
#
# `equilibrium` returns the minimum molar Gibbs energy and the phases it uses, with
# their amounts `NP`. With N = 1 mol the amounts are also the fractions.
#
# **From evaluating to minimising.** `calculate` answered "what is g of this phase
# here?". `equilibrium` answers the f1 question "which combination of the allowed
# phases, in which amounts, gives the lowest total G?", like the `linprog` step in
# f1.
#
# **The arguments.** The conditions are given as a *dictionary* `{key: value, ...}`.
# The keys are pycalphad's state variables: `v.T` temperature (K), `v.P` pressure
# (Pa) and `v.N` total amount of atoms (mol). The phases argument lists which
# phases the minimiser may use.
#
# **The result** is again an xarray Dataset. The ones used here:
#
# - `GM`: the minimum molar Gibbs energy (J/mol), with dimensions `(N, P, T)`, here
#   shape (1, 1, 1). `.squeeze()` drops the length-1 dimensions, and `float(...)`
#   turns the single remaining value into an ordinary number.
# - `Phase`: the name of each phase present, one per *vertex*. pycalphad reserves
#   room for several coexisting phases; unused slots hold an empty name `''`.
# - `NP`: the amount of each of those phases, in the same order (NaN, "not a
#   number", in unused slots).
#
# The loop uses `zip`, which walks through two arrays in step, giving one
# (phase, amount) pair at a time. `if phase:` skips the empty names, because an
# empty text counts as False in Python.

# %%
conditions = {v.T: 900.0, v.P: 100000.0, v.N: 1.0}   # K, Pa, mol of atoms
answer = equilibrium(database, components, phases, conditions)   # minimise G over SOLID and LIQUID
print("GM at 900 K:", float(answer.GM.values.squeeze()), "J/mol")
for phase, amount in zip(answer.Phase.values.reshape(-1), answer.NP.values.reshape(-1)):
    if phase:                      # skip unused slots (empty name)
        print(" ", phase, float(amount))   # phase name and its amount in mol (= fraction, since N = 1)

# %% [markdown]
# **What to look at.** The minimum GM and the phase list. Compare them with f1: at
# 900 K the minimiser should report the phase you found to be lower there, with
# the whole mole of atoms in it.
#
# ### Your turn (W7)
#
# What happens at 1100 K if LIQUID is **not allowed**? Predict the minimum GM
# (J/mol) with only SOLID, then run the next cell. Why is that not the equilibrium
# of the full model?

# %%
solid_only_1100 = None  # J/mol
check(solid_only_1100, "f2_solid_only_1100")

# %% [markdown]
# The next cell runs `equilibrium` twice at 1100 K. The `for` loop goes through a
# tuple of two phase lists: first both phases are allowed, then only SOLID. Only
# the phases argument changes between the two runs.

# %%
for allowed in (["SOLID", "LIQUID"], ["SOLID"]):   # first both phases, then SOLID alone
    result = equilibrium(database, components, allowed, {v.T: 1100.0, v.P: 100000.0, v.N: 1.0})
    print(f"1100 K with {allowed}: GM = {float(result.GM.values.squeeze()):.1f} J/mol")

# %% [markdown]
# ## After your attempt: compare pycalphad with the plain model
#
# Both routes use the same model, so they must agree at every temperature: the
# phase energies, the minimum, and HM and SM (1000 and 7000 J/mol; 10 and 16 J/(mol K)).
#
# **How the comparison works.** Two small course modules do the work:
#
# - `plain.gibbs(T)` is the f1 model in plain Python; it returns the pair
#   (g_SOLID, g_LIQUID).
# - `tools.equilibrium_at(T)` runs pycalphad's `equilibrium` at one temperature and
#   returns a dictionary with `"GM"` and the phase `"fractions"`.
# - `tools.phase_properties(temperatures)` runs `calculate` for both phases and
#   returns a dictionary of tables for `"GM"`, `"HM"` (molar enthalpy, J/mol) and
#   `"SM"` (molar entropy, J/(mol K)). Each table has one row per temperature and
#   two columns, SOLID then LIQUID.
#
# `enumerate(temperatures)` gives a counter `i` together with each temperature.
# `np.max(np.abs(a - b))` is the largest difference between two tables, ignoring
# its sign; a value of 0 means they agree everywhere. In
# `properties["HM"] - [1000.0, 7000.0]` NumPy subtracts 1000 from the SOLID column
# and 7000 from the LIQUID column of every row ("broadcasting").

# %% cellView="form"
#@title After your attempt: run to compare pycalphad with f1's plain model
from course.foundations import one_component_manual as plain   # f1's model in plain Python
from course.foundations import one_component_tools as tools    # the same model through pycalphad
import numpy as np

properties = tools.phase_properties(temperatures)   # {"GM", "HM", "SM"}: rows = temperatures, columns = SOLID, LIQUID
print(" T (K)   SOLID GM   LIQUID GM   minimum   pycalphad minimum")
for i, T in enumerate(temperatures):
    gs, gl = plain.gibbs(T)               # J/mol, plain-Python values
    found = tools.equilibrium_at(T)       # pycalphad equilibrium at this T
    print(f"{T:6.0f} {gs:10.0f} {gl:11.0f} {min(gs, gl):9.0f} {found['GM']:12.1f}  {found['fractions']}")
    confirm(found["GM"], min(gs, gl), f"pycalphad minimum at {T:.0f} K", tol=1e-6)
# largest difference between the pycalphad and plain GM tables, over both phases and all temperatures
confirm(float(np.max(np.abs(properties["GM"] - plain.gibbs(temperatures)))), 0.0, "GM of both phases at all five temperatures", tol=1e-7)
print("HM (J/mol):", properties["HM"][0], " SM (J/(mol K)):", properties["SM"][0])   # row 0 = 800 K
confirm(float(np.max(np.abs(properties["HM"] - [1000.0, 7000.0]))), 0.0, "HM of SOLID and LIQUID at all five temperatures", tol=1e-7)
confirm(float(np.max(np.abs(properties["SM"] - [10.0, 16.0]))), 0.0, "SM of SOLID and LIQUID at all five temperatures", tol=1e-7)

# %% [markdown]
# At 1000 K pycalphad reports one phase, but every balanced split of SOLID and LIQUID
# has the same energy there: the returned fractions are one valid answer, not *the* answer.
#
# **Limits.** The database is the invented f1 model, valid only for 800–1200 K at
# 100000 Pa; its element data are placeholders. Loading a database does not by
# itself give an equilibrium. Next: [f3 · binary mixtures](f3_binary_mixing_potentials.ipynb).
