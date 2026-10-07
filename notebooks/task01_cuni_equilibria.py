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
#
# **How this notebook works.** Run the cells from top to bottom (Shift + Enter
# runs one cell and moves to the next). Later cells use variables made by
# earlier ones, so if you restart the kernel, run everything above the cell you
# want again. Two helper functions appear throughout:
#
# - `check(your_value, key)` (key: the name of the stored answer, in quotes) compares your answer with a stored value without
#   showing it. It prints "✓ matches", "close" or "not yet". A variable that is
#   still `None` is reported as "not attempted yet".
# - `confirm(value, expected, "what", tol=...)` is used in the "After your
#   attempt" cells. It prints a ✓ line when a calculation reproduces the lesson
#   value within the tolerance `tol`, and stops with an error otherwise.
#
# The steps: get the database (1), read one Gibbs energy expression by hand
# (2), calculate one equilibrium point and check its balances (3), switch the
# magnetic term off (4), apply the lever rule where liquid and solid coexist
# (5), draw the whole phase diagram (6) and compare the paper's coefficients with
# the file's (7).

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
# The setup cell printed the versions of numpy, scipy, matplotlib, xarray and
# pycalphad. The course values were made with exactly these versions; if a
# result later differs, compare the versions first. It also moved the working
# folder to the course folder, so paths such as `course/materials/...` below are
# relative to it.
#
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
#
# A **TDB file** ("thermodynamic database") is a plain text file with the Gibbs
# energy of every phase as a function of temperature, pressure and composition.
# The **SHA-256** is a fingerprint of the file's bytes: if a single character
# differs, the fingerprint differs, so a match proves that you have exactly the
# published file.
#
# **What the cell does.** `database("cuni", download=DOWNLOAD)` returns the path
# of a checked copy of the file, or `None` if there is none. `LIVE` records which
# of the two modes you are in; later cells test `if LIVE:` and either calculate
# or read the saved results. `SAVED` is the saved course run: `json.loads` turns
# the text of a JSON file into nested Python dictionaries and lists, which you
# read with keys, for example `SAVED["equilibrium"]`.

# %%
import json
from pathlib import Path

DOWNLOAD = False   # True: fetch CuNi-92Mey-LB.tdb into your session
TDB = database("cuni", download=DOWNLOAD)  # path to the checked file, or None
LIVE = TDB is not None                      # True with the database, False in no-database mode
SAVED = json.loads(Path("course/materials/cuni/results.json").read_text())  # the course run's results
if LIVE:
    print("Live mode: the cells below calculate with your copy of the database.")
else:
    print("No-database mode: the cells below read the saved course results\n"
          "(course/materials/cuni/results.json and course/self_study/generated/cuni_grid.json).")

# %% [markdown]
# ## 2. Read one database branch by hand (exercise 1)
#
# Before letting a program use the database, read one entry yourself, so that
# the numbers pycalphad works with are not a black box.
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
# Schematically, a statement with two temperature ranges reads
#
# `PARAMETER G(PHASE,EL;0)  T1  expression-1;  T2  Y  expression-2;  T3  N  reference !`
#
# so expression-1 applies for T1 ≤ T < T2 and expression-2 for T2 ≤ T ≤ T3.
# In the expressions, `*` is multiplication, `**` a power (`T**(-1)` is 1/T)
# and `LN(T)` is ln T. Each range usually has the form
# $a+bT+cT\ln T+dT^2+\dots$: it belongs to a heat capacity $C_p(T)$ that is a
# simple function of T, from which $H$ and $S$ follow by integration and
# $G=H-TS$.
#
# **SER** means: the enthalpy of the element in its stable state at 298.15 K and
# 1 bar (for Cu, solid FCC Cu) is set to zero. Absolute Gibbs energies cannot be
# measured, only differences, so every database fixes such a reference; the
# printed number is $G-H^{\rm SER}_{\rm Cu}$.
#
# The cell prints only that parameter and the functions it refers to, read from
# **your** file at run time. How the code works:
#
# - `statements(path)` reads the file, drops comment lines (they start with `$`),
#   splits the text at every `!` and squeezes repeated spaces, so each list entry
#   is one complete statement.
# - `re` is Python's module for *regular expressions*, small search patterns
#   for text. `re.match(r"PAR\w*\s+G\(LIQUID,CU\)", s, re.I)` asks: does `s`
#   start with `PAR` plus any further letters (`\w*`, so also `PARAMETER`), then
#   spaces (`\s+`), then `G(LIQUID,CU)`? `re.I` ignores upper/lower case;
#   `\(` means a literal bracket.
# - The `while` loop then follows every name in the statement that is also a
#   `FUNCTION` in the file, so the functions it calls are printed too.

# %%
import re


def statements(path):
    """The file's statements (each up to its '!'), with comment lines ($) removed."""
    lines = [line for line in path.read_text().splitlines() if not line.lstrip().startswith("$")]
    return [" ".join(s.split()) + " !" for s in "\n".join(lines).split("!") if s.strip()]


if LIVE:
    STATEMENTS = statements(TDB)  # list of strings, one per statement
    # {function name: its statement}, for looking up the names used inside expressions
    functions = {s.split()[1].upper(): s for s in STATEMENTS if s.upper().startswith("FUNCTION")}
    # next(...) returns the first statement that matches: the parameter for pure liquid Cu
    todo = [next(s for s in STATEMENTS if re.match(r"PAR\w*\s+G\(LIQUID,CU\)", s, re.I))]
    shown = []
    while todo:  # follow the function names the statement refers to
        statement = todo.pop(0)  # take the first waiting statement off the list
        shown.append(statement)
        # every word that looks like a name (letters, digits, underscores, starting with a letter or _)
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
#
# Tip for a scratch cell (add an empty code cell with the + button): write
# `import math`, `T = 1500.0`,
# then type the expression with `math.log(T)` for `LN(T)` and `T**(-1)` as it
# stands. Keep all digits until the end.

# %%
g_liquid_cu_1500 = None  # J/mol of atoms, pure liquid Cu at 1500 K, to 0.01 J/mol (a neighbouring range differs by a few J/mol)
if LIVE:
    check(g_liquid_cu_1500, "task01_liquid_cu_1500")
else:
    print("Skipped: this exercise needs your copy of the database.")

# %% [markdown]
# ## 3. Phases, conditions and units; one equilibrium point
#
# From a single expression to a full calculation: pycalphad now combines all the
# Gibbs energies in the file and finds the state of lowest total Gibbs energy.
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
# **Phase names.** The names follow the usual CALPHAD convention: the crystal
# structure plus its *Strukturbericht* symbol. FCC_A1 is face-centred cubic (the
# Cu structure, A1), BCC_A2 body-centred cubic (the W structure, A2), HCP_A3
# hexagonal close-packed (the Mg structure, A3). LIQUID is the melt. Both Cu and
# Ni are FCC in the solid state; BCC and HCP are allowed so that pycalphad can
# check that they do not win.
#
# **Equilibrium.** At fixed T, P and overall composition the stable state is the
# one with the lowest total Gibbs energy. pycalphad searches over all ways of
# splitting the sample into the allowed phases, each with its own composition.
# It first evaluates every phase at many trial compositions (the starting grid,
# set by `pdens`) and then refines the best combination.
#
# Output as in f5: `GM` is the Gibbs energy of the whole sample in J/mol of atoms,
# `NP` is each phase's amount as a fraction of the atoms, `X` is the composition
# inside each phase. FCC_A1 is written with a second, interstitial sublattice that
# holds only vacancies here (so that C or N can be added later); empty sites add no
# atoms, so FCC energies are per one mole of atoms, not two.
#
# One point: T = 600 K, overall x(Ni) = 0.5, all four phases allowed.
#
# **The pycalphad call.** `equilibrium(db, COMPONENTS, PHASES, conditions, ...)`
# needs the database, the components, the phases allowed and a *conditions
# dictionary*. Its keys come from `pycalphad.variables`, imported as `v`:
# `v.T` temperature in K, `v.P` pressure in Pa, `v.N` total amount in mol of
# atoms and `v.X("NI")` the overall mole fraction of Ni. In a binary one mole
# fraction fixes the composition, since x(Cu) = 1 − x(Ni).
#
# The result is an **xarray Dataset**: a set of labelled numpy arrays, one for
# each output (`GM`, `NP`, `X`, `Phase`, ...). Each array has one axis per
# condition (N, P, T, X_NI) and an axis `vertex` with one slot per phase that
# could coexist. Here every condition has a single value, so
# `.squeeze()` removes those length-1 axes; `.values` turns the result into an
# ordinary numpy array; `.sel(component="NI")` picks the Ni entry of `X`.
# Slots that are not used hold an empty phase name `''` and `NaN` ("not a
# number") amounts; the code filters them out.
#
# **What the code cell defines.**
#
# - `rows_at(T, magnetic=True)` returns a list of rows `(phase, NP, x(Ni) in the
#   phase)` at temperature T and overall x(Ni) = 0.5. With the database it
#   calculates; without it, it reads the saved course run (available only at
#   600, 1500, 1540 and 1600 K, the keys of `SAVED_KEY`).
# - `show(rows, title)` prints such a list as a table.
# - At the end it calculates the 600 K point once directly, printing the raw
#   pycalphad arrays (live mode), and then the cleaned-up table.
#
# What to look at: how many rows (phases) appear, their amounts, and their
# compositions.

# %%
import numpy as np
from pycalphad import Model, equilibrium, variables as v
from course.materials.cuni import worked_example as cuni  # the Task 01 course script

PHASES = cuni.PHASES          # LIQUID, FCC_A1, BCC_A2, HCP_A3
COMPONENTS = cuni.COMPONENTS  # CU, NI, VA
P = cuni.PRESSURE             # Pa
PDENS = 60                    # sampling density of the starting grid
SAVED_KEY = {600: "600", 1500: "1500", 1540: "FCC_liquid_example", 1600: "1600"}  # T (K) → name in SAVED
if LIVE:
    db = cuni.load_source(TDB)  # checks the pycalphad version and the file, then reads it


def rows_at(T, magnetic=True):
    """[(phase, amount NP, x(Ni) in that phase)] at T (K) and overall x(Ni) = 0.5."""
    if LIVE:
        # model=MagneticOffModel switches the magnetic term off (section 4); {} keeps pycalphad's default Model
        options = {} if magnetic else {"model": cuni.MagneticOffModel}
        # conditions: T in K, overall x(Ni) = 0.5, P in Pa, 1 mol of atoms; **options passes the dict as keyword arguments
        eq = equilibrium(db, COMPONENTS, PHASES, {v.T: T, v.X("NI"): 0.5, v.P: P, v.N: 1},
                         calc_opts={"pdens": PDENS}, **options)
        # zip walks through the phase slots; keep only real phases with a positive amount
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
    # f-string formats: <8 = left-aligned in 8 characters; >20 = right-aligned in 20; 20.15f = 15 decimals
    print(f"  {'phase':<8} {'amount NP':>20} {'x(Ni) in phase':>20}")
    for phase, amount, x in rows:
        print(f"  {phase:<8} {amount:20.15f} {x:20.15f}")


if LIVE:
    point = equilibrium(db, COMPONENTS, PHASES, {v.T: 600, v.X("NI"): 0.5, v.P: P, v.N: 1},
                        calc_opts={"pdens": PDENS})
    print("GM    :", float(point.GM.values.squeeze()), "J/mol of atoms")    # one number for the whole sample
    print("Phase :", point.Phase.values.squeeze())                          # one name per slot ('' = unused)
    print("NP    :", point.NP.values.squeeze())                             # amount per slot (nan = unused)
    print("X(NI) :", point.X.sel(component="NI").values.squeeze(), "\n")    # x(Ni) inside each slot's phase
rows_600 = rows_at(600)  # list of (phase, NP, x(Ni)) tuples
show(rows_600, "600 K, overall x(Ni) = 0.5, magnetic contribution on")

# %% [markdown]
# ### Your turn
#
# Reconstruct the overall composition from the rows above: weight each phase's
# composition by its amount, $\sum_i NP_i\,x_i(\mathrm{Ni})$, and the same for Cu
# with $1-x_i(\mathrm{Ni})$. Why can both rows be called FCC_A1?
#
# Why this check: the Ni atoms in all phases together must equal the Ni atoms of
# the sample, and the same for Cu. This is a **mass balance**; a result that
# fails it cannot be right, whatever program produced it. You can read the
# numbers from the table, or loop over `rows_600` in a scratch cell (each entry
# is a tuple `(phase, NP, x)`).

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
# The learning question asks how much the magnetic term matters. To find out,
# repeat the same calculation with that one term removed and compare.
#
# Ni-rich FCC is ferromagnetic, and the database adds a magnetic Gibbs energy term
# to FCC_A1. The magnetic contribution is the lowering of the Gibbs energy by the
# ordering of the atomic magnetic moments, mostly below the Curie temperature; the
# database gives it through each phase's Curie temperature `TC` and mean magnetic
# moment `BM`. `MagneticOffModel` in the course script is pycalphad's `Model` with
# only that term set to zero; the chemical terms, the phases and the conditions
# stay the same. It is a comparison, not a real nonmagnetic alloy. The total
# energy already contains the magnetic part, so it is never added a second time.
#
# In CALPHAD databases this term usually has the form
# $G_{\rm mag}=RT\ln(\beta+1)\,f(\tau)$ with $\tau=T/T_C$: $\beta$ is the mean
# magnetic moment per atom (in Bohr magnetons, `BM` in the file), $T_C$ the
# Curie temperature in K, and $f(\tau)$ a fixed function of $\tau$. The term
# lowers G; it is largest in size well below $T_C$ and becomes small above it.
# Both $T_C$ and $\beta$ depend on composition; pure Cu is not magnetic.
#
# **How the switch works in code.** pycalphad's `Model` builds a phase's Gibbs
# energy as a sum of parts (pure elements, ideal mixing, excess mixing,
# magnetic, ...), each made by its own method. A *subclass* (`class
# MagneticOffModel(Model)`) inherits everything and replaces one method: here
# `magnetic_energy` returns zero (`S.Zero`, the symbolic number 0).
# `inspect.getsource` prints that class's source code so you can see it. The
# modified model reaches `equilibrium` through its `model=` argument, as in
# `rows_at(600, magnetic=False)`.

# %%
import inspect

print(inspect.getsource(cuni.MagneticOffModel))  # show the source code of the class
rows_600_off = rows_at(600, magnetic=False)      # same point, magnetic term set to zero
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
# From low temperature to high: near the melting range a solid and a liquid can
# coexist, and the question becomes how much of each there is.
#
# On the 20 K grid, 1540 K is the first temperature at overall x(Ni) = 0.5 with
# both liquid and FCC present. The cell prints which phases are present at 1500,
# 1540 and 1600 K, and their compositions (magnetic contribution on).
#
# In the code, `", ".join(...)` glues the text pieces together with commas, and
# the `_` in `for phase, _, x in ...` is a placeholder for a value that is not
# needed here (the amount NP).

# %%
for T in (1500, 1540, 1600):  # K
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
#
# Where the formula comes from: put $f_{FCC}=1-f_L$ into the Ni balance,
# $f_L x_L+(1-f_L)\,x_{FCC}=z$, and solve for $f_L$. It is called the lever rule
# because, on the tie line from $x_L$ to $x_{FCC}$, the amount of each phase is
# proportional to the length of the segment on the *opposite* side of $z$, like
# the arms of a balanced lever. Here $f$ are fractions of the atoms, the same
# basis as `NP`.

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
# From single points to the whole map: repeat the equilibrium calculation on a
# grid of temperatures and compositions and plot what was found.
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
#
# A **tie line** is the horizontal line (one temperature) that joins the
# compositions of two phases in equilibrium with each other. A **miscibility
# gap** is a region where one phase (here FCC_A1) is more stable as two
# separate compositions than as one; it closes at a top, the critical
# temperature.
#
# **How the grid is stored.** `grid` is a dictionary. `grid["T_K"]` and
# `grid["x"]` are the grid temperatures and overall compositions,
# `grid["phases"]` the phase names, and
# `grid["modes"]["magnetic_on"][iT][ix]` is the *cell* at temperature number
# `iT` and composition number `ix`: a list with one entry
# `[phase index, NP, x(Ni) in the phase]` per phase present, sorted by x(Ni).
# The phase index points into `grid["phases"]` (0 = LIQUID, 1 = FCC_A1, ...).
#
# **What the code does.**
#
# - `phase_points(mode)` collects, for every phase, all its (x(Ni), T) points:
#   these are the markers of the first two panels.
# - `tie_lines(mode, it)` lists the different two-phase cells at grid row `it`,
#   each as its two `(phase, x(Ni))` ends, rounded to 3 decimals so that
#   repeats of the same tie line count once.
# - `plt.subplots(1, 3)` makes a figure with three panels (`axes`): magnetic on,
#   magnetic off, and a zoom on the ends of the two-FCC tie lines for both
#   settings. `ax.scatter` draws markers, `ax.plot` lines, `ax.set(...)` sets
#   titles, labels and axis limits.
# - Two tables follow: tie-line ends at a few temperatures, then the liquid/FCC
#   lens, drawn as a second figure.

# %%
import matplotlib.pyplot as plt
from course.self_study.grid_export import export_cuni

if LIVE:
    print("Computing 2 × 81 × 61 equilibria (up to about 1 minute) ...")
    grid = export_cuni(TDB)
else:
    grid = json.loads(Path("course/self_study/generated/cuni_grid.json").read_text())
T_GRID = np.array(grid["T_K"])   # K, 81 values
X_GRID = np.array(grid["x"])     # overall x(Ni), 61 values
# marker shape and colour for each phase ("C0", "C1", ... are matplotlib's default colours)
STYLE = {"LIQUID": dict(marker="o", color="C0"), "FCC_A1": dict(marker="s", color="C1"),
         "BCC_A2": dict(marker="^", color="C2"), "HCP_A3": dict(marker="D", color="C3")}


def phase_points(mode):
    """{phase: (x(Ni) in the phase, T)} for every phase with a positive amount on the grid."""
    out = {}
    for it, row in enumerate(grid["modes"][mode]):  # enumerate gives the row number it and the row
        for cell in row:  # one overall composition
            for index, amount, x in cell:
                # setdefault creates an empty list the first time a phase is met
                out.setdefault(grid["phases"][index], []).append((x, T_GRID[it]))
    return {phase: np.array(xy) for phase, xy in out.items()}  # each value: array with columns x, T


def tie_lines(mode, it):
    """Distinct two-phase samples at grid row it: ((phase, x(Ni)), (phase, x(Ni)))."""
    # a set {...} keeps each tie line once; sorted() puts them in order
    return sorted({tuple((grid["phases"][i], round(x, 3)) for i, n, x in cell)
                   for cell in grid["modes"][mode][it] if len(cell) == 2})


fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # figsize in inches (width, height)
for ax, mode in zip(axes[:2], ("magnetic_on", "magnetic_off")):
    for phase, xy in phase_points(mode).items():
        # xy[:, 0] = all x values, xy[:, 1] = all T values; **STYLE[phase] passes marker and colour
        ax.scatter(xy[:, 0], xy[:, 1], s=6, label=phase, **STYLE[phase])
    ax.set(title=mode.replace("_", " "), xlabel="x(Ni) in the phase", ylabel="T (K)",
           xlim=(0, 1), ylim=(300, 1900))
    ax.legend(markerscale=2)
for mode, style in (("magnetic_on", dict(ls="-", marker="o", color="C1")),
                    ("magnetic_off", dict(ls="--", marker="s", mfc="none", color="k"))):
    ends = [(T_GRID[it], *[x for p, x in pair])  # the two FCC compositions at each row
            for it in range(len(T_GRID)) if T_GRID[it] <= 720
            for pair in tie_lines(mode, it)[:1] if all(p == "FCC_A1" for p, x in pair)]
    T_ends, x_left, x_right = np.array(ends).T  # .T transposes: three arrays (T, left end, right end)
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
    it = int(np.argmin(np.abs(T_GRID - T)))  # index of the grid temperature nearest to T
    for mode in ("magnetic_on", "magnetic_off"):
        ends = tie_lines(mode, it)
        text = "; ".join(" + ".join(f"{p} {x:.3f}" for p, x in pair) for pair in ends) or "one phase at every x(Ni)"
        print(f"  {T_GRID[it]:6.0f} K  {mode:<13} {text}")

# Zoom on the thin liquid/FCC lens (magnetic contribution on): the two ends of the
# liquid + FCC tie line at each grid temperature where the grid found one.
# dict(pair) turns ((phase, x), (phase, x)) into {phase: x}, so each end is found by its phase name.
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
# In the lens figure, the **liquidus** (LIQUID end) is the line above which the
# alloy is completely liquid; the **solidus** (FCC_A1 end) is the line below
# which it is completely solid. Between them liquid and FCC coexist, as at
# 1540 K in section 5.
#
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
#
# **What the excess term means.** The Gibbs energy of a solution phase is built
# from three parts: the pure elements weighted by their fractions, the ideal
# mixing term $RT\,[x_{Cu}\ln x_{Cu}+x_{Ni}\ln x_{Ni}]$, and the *excess* term
# above, which holds everything ideal mixing leaves out. This sum is the
# Redlich–Kister form. $L_0$ ($\nu=0$) is symmetric in Cu and Ni; $L_1$
# ($\nu=1$) multiplies $(x_{Cu}-x_{Ni})$ and so makes the curve lopsided. A
# positive $L$ means Cu–Ni neighbours are less favourable than in an ideal
# solution, which favours demixing. $a_\nu$ (J/mol) and $b_\nu$ (J/(mol K)) are
# the numbers a CALPHAD assessment fits.
#
# In the file, the same parameters are named like `L(FCC_A1,CU,NI:VA;1)`:
# interaction between Cu and Ni on the first sublattice of FCC_A1, with VA on
# the second, order $\nu=1$.
#
# In the code, `csv.DictReader` reads the table file row by row, each row as a
# dictionary keyed by the column names, and the regular expression picks the
# four `L(...)` statements of LIQUID and FCC_A1 of order 0 or 1 from your file.

# %%
import csv

with open("course/materials/cuni/mey1992_binary_parameters.csv") as handle:
    PAPER = list(csv.DictReader(handle))  # list of dicts, one per printed row
print("Mey (1992), Table 2, as printed:")
print(f"  {'phase':<8} {'order':>5} {'a (J/mol)':>12} {'b (J/(mol K))':>14}")
for row in PAPER:
    print(f"  {row['phase']:<8} {row['rk_order']:>5} {float(row['a_J_per_mol']):12.2f} {float(row['b_J_per_mol_K']):14.5f}")
if LIVE:
    print("\nYour file:")
    for statement in STATEMENTS:
        # L(LIQUID,CU,NI;0), L(FCC_A1,CU,NI:VA;1) and so on; (:VA)? means ":VA" may or may not be there
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
#
# **First cell: the liquid Cu branch and the magnetic term.** `Model(db,
# COMPONENTS, "LIQUID")` builds pycalphad's symbolic Gibbs energy of one phase;
# `liquid.GM` is that energy per mole of atoms as a formula in T, P and the site
# fractions. `cuni.evaluate(model, expression, T, x_Ni)` substitutes numbers for
# all these symbols and returns a float. It compares your hand branch from
# section 2 with pycalphad, then checks at 16 FCC states that "magnetic on minus
# magnetic off" equals the magnetic term itself, so the switch in section 4
# removes exactly that term and nothing else.

# %% cellView="form"
#@title After your attempt: the liquid Cu branch and the magnetic term
energies = SAVED["energy_checks"]  # saved energies of the course run
if LIVE:
    liquid = Model(db, COMPONENTS, "LIQUID")  # symbolic Gibbs energy of the liquid
    g_cu = cuni.evaluate(liquid, liquid.GM, 1500, 0.0)  # x(Ni) = 0: pure Cu
    print(f"pycalphad, pure liquid Cu at 1500 K: {g_cu:.8f} J/mol of atoms")
    confirm(g_cu, energies["hand_pure_Cu_liquid_J_per_mol_atoms"], "Pure liquid Cu at 1500 K (hand value)", tol=1e-8)
    g_ni = cuni.evaluate(liquid, liquid.GM, 1500, 1.0)  # x(Ni) = 1: pure Ni
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

# %% [markdown]
# **Second cell: balances, magnetic off and the lever rule.** For both magnetic
# settings at 600 and 1540 K it adds up Ni, Cu and the phase amounts (each must
# give 0.5, 0.5 and 1) and compares every row with the saved run. Then it
# applies the lever rule at 1540 K. With the database it also draws the Gibbs
# energy curves of FCC and liquid at 1600 K.
#
# Those curves use `calculate` instead of `equilibrium`: `calculate` only
# *evaluates* a phase's Gibbs energy at the internal compositions you give it in
# `points`, without looking for the minimum. Each row of `points` holds site
# fractions: for FCC_A1 three columns (Cu, Ni on the first sublattice, VA on the
# second), for LIQUID two (Cu, Ni). `np.column_stack` builds those columns from
# the 201 values of x(Ni) in `xs`.

# %% cellView="form"
#@title After your attempt: balances, magnetic off and the lever rule
for magnetic, mode in ((True, "magnetic_on"), (False, "magnetic_off")):
    for T in (600, 1540):
        rows = rows_at(T, magnetic)
        ni = sum(n * x for _, n, x in rows)        # Σ NP·x(Ni)
        cu = sum(n * (1 - x) for _, n, x in rows)  # Σ NP·x(Cu)
        amounts = sum(n for _, n, _ in rows)       # Σ NP, must be 1
        print(f"{mode}, {T} K: Σ NP·x(Ni) = {ni:.9f}, Σ NP·x(Cu) = {cu:.9f}, Σ NP = {amounts:.9f}")
        confirm(ni, 0.5, f"Ni balance ({mode}, {T} K)", tol=1e-6)
        confirm(cu, 0.5, f"Cu balance ({mode}, {T} K)", tol=1e-6)
        saved = SAVED["equilibrium"][mode]["samples"][SAVED_KEY[T]]["phases"]
        for (phase, n, x), ref in zip(rows, saved):  # row by row against the saved run
            assert phase == ref["phase"], f"{phase} where the course run has {ref['phase']}"
            confirm(n, ref["atom_mole_fraction"], f"  {phase} amount", tol=1e-6)
            confirm(x, ref["x_NI"], f"  {phase} x(Ni)", tol=1e-6)
print("Both settings keep two FCC_A1 compositions at 600 K: the chemical terms alone already demix.")

composition = {phase: x for phase, _, x in rows_at(1540)}  # {phase name: x(Ni) in that phase}
x_l, x_fcc = composition["LIQUID"], composition["FCC_A1"]
f_l = (x_fcc - 0.5) / (x_fcc - x_l)  # lever rule with z = 0.5
print(f"Lever rule at 1540 K: f_L = ({x_fcc:.6f} − 0.5)/({x_fcc:.6f} − {x_l:.6f}) = {f_l:.6f}, f_FCC = {1 - f_l:.6f}")
confirm(f_l, SAVED["equilibrium"]["magnetic_on"]["samples"]["FCC_liquid_example"]["phases"][0]["atom_mole_fraction"],
        "Liquid amount from the lever rule", tol=1e-6)

if LIVE:  # energy curves at 1600 K: the overall composition stays at 0.5
    from pycalphad import calculate
    xs = np.linspace(0, 1, 201)  # 201 evenly spaced x(Ni) values from 0 to 1
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # site fractions per row: FCC_A1 (y_Cu, y_Ni, y_Va = 1), LIQUID (x_Cu, x_Ni)
    for phase, points in (("FCC_A1", np.column_stack([1 - xs, xs, np.ones_like(xs)])),
                          ("LIQUID", np.column_stack([1 - xs, xs]))):
        for model, style, label in ((Model, dict(ls="-", marker="o"), "on"),
                                    (cuni.MagneticOffModel, dict(ls="--", marker="x"), "off")):
            # evaluate GM of this phase at the given points (no minimisation)
            curve = calculate(db, COMPONENTS, phase, T=1600, P=P, N=1, points=points, model=model)
            ax.plot(xs, curve.GM.values.ravel(), color="C1" if phase == "FCC_A1" else "C0",
                    markevery=25, label=f"{phase}, magnetic {label}", **style)  # .ravel(): flatten to 1-D
    ax.axvline(0.5, ls=":", color="0.5", label="overall x(Ni) = 0.5")  # vertical line at the alloy composition
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
    ax.imshow(plt.imread("course/materials/cuni/energy_magnetism.png"))  # show a saved image
    ax.axis("off")
    plt.show()

# %% [markdown]
# **Third cell: the top of the miscibility gap.** For each magnetic setting it
# collects the grid temperatures where some cell holds at least two FCC_A1
# entries and reports the highest one. With the database it also compares the
# recomputed grid with the saved grid, cell by cell.

# %% cellView="form"
#@title After your attempt: the top of the miscibility gap on the grid
for mode in ("magnetic_on", "magnetic_off"):
    rows = grid["modes"][mode]
    # temperatures where at least one cell of the row has two or more FCC_A1 entries
    two_fcc = [T for T, row in zip(T_GRID, rows)
               if any(sum(1 for i, n, x in cell if grid["phases"][i] == "FCC_A1") >= 2 for cell in row)]
    print(f"{mode}: highest grid temperature with two FCC_A1 compositions = {max(two_fcc):.0f} K")
    confirm(max(two_fcc), SAVED["equilibrium"][mode]["highest_sampled_T_with_two_FCC_K"],
            f"Top of the two-FCC region ({mode})", tol=1e-6)
print("Grid temperatures are 20 K apart, so each top lies somewhere up to 20 K above the value found.")
if LIVE:  # the recomputed grid against the saved one (both rounded to 6 digits)
    saved_grid = json.loads(Path("course/self_study/generated/cuni_grid.json").read_text())
    largest = 0.0  # largest difference in NP or x(Ni) found so far
    for mode in grid["modes"]:
        for row, saved_row in zip(grid["modes"][mode], saved_grid["modes"][mode]):
            for cell, saved_cell in zip(row, saved_row):
                assert [c[0] for c in cell] == [c[0] for c in saved_cell], "phase sets differ from the saved grid"
                largest = max([largest] + [abs(a - b) for c, ref in zip(cell, saved_cell) for a, b in zip(c[1:], ref[1:])])
    confirm(largest, 0.0, "Recomputed grid against the saved grid (rounded to 6 digits)", tol=2e-6)

# %% [markdown]
# **Fourth cell: paper and file side by side.** With the database, a regular
# expression pulls $a$ and $b$ out of each `L(...)` statement of the form
# `a+b*T` and prints them next to the transcribed table, with "yes" where both
# agree to $10^{-9}$.

# %% cellView="form"
#@title After your attempt: paper and file side by side
if LIVE:
    file_rows = {}  # {(phase, order): (a, b)} read from your file
    for statement in STATEMENTS:
        # groups: 1 = phase, 2 = order, 3 = a (J/mol), 4 = b (J/(mol K)) in "a+b*T"
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
