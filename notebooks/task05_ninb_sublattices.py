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
# # Task 05: Ni–Nb, sublattices and the amount basis
#
# **Learning question:** how do sublattices fix the composition of an ordered
# phase, and is each number from a database calculation per mole of formula
# units or per mole of atoms?
#
# Used in: Task 05, self-study step 06. Run [setup_check](setup_check.ipynb) first
# if you want to use the published database; everything also works without it,
# from the saved results. Work each "your turn" on paper first, then type your value.
#
# **How this notebook works.** Run the cells from top to bottom (Shift + Enter).
# In each "Your turn" cell, replace `None` with your value and run the cell:
# `check(your_value, key)` (key: the name of the stored answer, in quotes) prints "✓ matches", "close" or "not yet" without
# showing the stored answer. The "After your attempt" cells use
# `confirm(value, expected, "what", tol=...)`, which prints a ✓ line when a
# calculation reproduces the lesson value within `tol` and stops with an error
# otherwise.
#
# The steps: count atoms on sublattices (1), get the database (2), see how it
# describes δ and μ (3), convert between formula and atom amounts (4), check
# the balances of a two-phase sample (5), read the phase diagram (6), and match
# the μ sublattices to a crystal structure (7).

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
# ## 1. Sublattices by counting (no database needed)
#
# In the Ni–Nb database, μ and δ are the **names of two phases**, not a chemical
# potential or a boundary preference.
#
# An ordered phase is described by **sublattices**: groups of sites, each with a
# fixed number of sites per formula unit. Every site here holds one Nb or one Ni
# atom, so the number of atoms per formula is the sum of the site counts.
#
# | Phase | Sites per formula on each sublattice | Ideal formula |
# |---|---|---|
# | δ (`DELTA`) | 1 : 1 : 2 | NbNi₃ |
# | μ (`MU_PHASE`) | 2 : 2 : 2 : 6 : 1 | Nb₇Ni₆ |
#
# Let $a_s$ be the sites per formula on sublattice $s$ and $y_s$ the fraction of
# those sites that hold Nb. Then
#
# $$x(\mathrm{Nb})=\frac{\sum_s a_s\,y_s}{\sum_s a_s}
# =\frac{\text{Nb atoms per formula}}{\text{atoms per formula}} .$$
#
# A filling with one element on each sublattice is an **endmember**: a building
# block of the model, not necessarily a material that exists. Because sites can
# hold either element, each phase covers a range of compositions around its ideal
# formula.
#
# **Why sublattices.** In an ordered compound the atoms are not spread at
# random: in a crystal of NbNi₃, certain sites are mostly Nb and others mostly
# Ni. A sublattice model keeps track of each kind of site separately. The *site
# fraction* $y_s$ (a number between 0 and 1) says how much of sublattice $s$ is
# Nb; the Ni fraction on that sublattice is $1-y_s$. Reading the formula above:
# sublattice $s$ contributes $a_s y_s$ Nb atoms per formula unit; add them up and
# divide by all atoms per formula unit.
#
# **The code.** `x_nb(sites, nb_fraction)` evaluates that formula.
# `zip(sites, nb_fraction)` walks through the two lists in step, giving one
# pair $(a_s, y_s)$ per sublattice. `show(...)` prints each sublattice as a row
# of boxes, one box per site per formula: `"[Nb]" * 2` repeats a text twice.
# `enumerate(..., start=1)` numbers the sublattices from 1. Two example fillings
# are shown; neither is an ideal formula.

# %%
DELTA_SITES = [1, 1, 2]        # sites per formula on each δ sublattice
MU_SITES = [2, 2, 2, 6, 1]     # sites per formula on each μ sublattice

def x_nb(sites, nb_fraction):
    """Nb atom fraction from site counts a_s and Nb site fractions y_s."""
    nb_atoms = sum(a * y for a, y in zip(sites, nb_fraction))   # Nb atoms per formula
    return nb_atoms / sum(sites)                                # every site holds one atom

def show(name, sites, nb_fraction):
    """Draw each sublattice as boxes, one box per site per formula."""
    print(f"{name}: {sum(sites)} atoms per formula")
    for s, (a, y) in enumerate(zip(sites, nb_fraction), start=1):
        # all Nb → [Nb], all Ni → [Ni], otherwise the Nb site fraction in the box
        box = "[Nb]" if y == 1 else "[Ni]" if y == 0 else f"[{y:.2f} Nb]"
        # {box * a:<26}: the box repeated a times, left-aligned in 26 characters; :g drops trailing zeros
        print(f"  sublattice {s}, {a} site{'s' if a > 1 else ' '}: {box * a:<26} Nb atoms per formula = {a * y:g}")
    print(f"  x(Nb) = {x_nb(sites, nb_fraction):.4f}")

# Two example fillings (not the ideal formulas):
# the list gives the Nb site fraction y_s on each sublattice, in order (1 = all Nb, 0 = all Ni)
show("δ, Nb on the 2-site sublattice only", DELTA_SITES, [0, 0, 1])
show("μ, Nb on the 1-site sublattice only", MU_SITES, [0, 0, 0, 0, 1])

# %% [markdown]
# ### Your turn
#
# 1. Find a δ filling that gives the ideal NbNi₃ (try it with `show`). What is
#    x(Nb)?
# 2. Find a μ filling that gives Nb₇Ni₆, with Nb only on whole sublattices. What
#    is x(Nb)?
# 3. How many atoms per formula do δ and μ have?
#
# To try a filling, add a code cell and call for example
# `show("my δ", DELTA_SITES, [1, 1, 0])` with your own list of $y_s$.

# %%
x_nbni3 = None           # x(Nb) of ideal δ-NbNi₃
x_nb7ni6 = None          # x(Nb) of ideal μ-Nb₇Ni₆
atoms_per_delta = None   # atoms per δ formula
atoms_per_mu = None      # atoms per μ formula
check(x_nbni3, "task05_x_nbni3")
check(x_nb7ni6, "task05_x_nb7ni6")
check(atoms_per_delta, "task05_atoms_delta")
check(atoms_per_mu, "task05_atoms_mu")

# %% [markdown]
# ## 2. Get the database (optional)
#
# The counting above needs no data. From here on, the published Ni–Nb database
# supplies energies and phase equilibria (or the saved results stand in for it).
#
# The published input is the database in the supplement of H. Sun et al.,
# “Thermodynamic modeling of the Nb-Ni system with uncertainty quantification
# using PyCalphad and ESPEI,” *Calphad* 82 (2023) 102563,
# [doi:10.1016/j.calphad.2023.102563](https://doi.org/10.1016/j.calphad.2023.102563)
# ([manuscript](https://www.osti.gov/servlets/purl/2205728)). Cite it when you use it.
#
# | | |
# |---|---|
# | Supplement | [ZIP from the publisher](https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip) |
# | File inside | `calpha_102563_Nb-Ni_new_mmc1.tdb`, 13,087 bytes |
# | SHA-256 | `ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a` |
#
# The cell below looks for a checked copy; with `DOWNLOAD = True` it tries to
# fetch the ZIP. The publisher may refuse downloads from a script: then the
# message tells you to download the ZIP in your browser and either upload the
# file (Colab) or save it where the message says. The file stays outside the
# course folder; please do not share it. Set `USE_DATABASE = False` to work only
# with the saved results.
#
# The SHA-256 is a fingerprint of the file's bytes: a match proves that you have
# exactly the published file. `database(...)` returns the path to the checked
# file, or `None`; the line `... if USE_DATABASE else None` skips the search when
# you switch the database off. `TDB` then decides the mode of every later cell.

# %%
DOWNLOAD = False       # True: try to fetch the supplement ZIP
USE_DATABASE = True    # False: no-database mode, saved results only
TDB = database("ninb", download=DOWNLOAD) if USE_DATABASE else None  # path to the checked file, or None
print("Mode:", "with the published database" if TDB else "no database (saved results)")

# %% [markdown]
# ## 3. What the database says about δ and μ
#
# With the database, pycalphad lists each phase's sublattices, sites per formula
# and allowed elements. This reads the phase description only; no energy is
# printed. Without the database the cell says so and you can continue.
#
# **The code.** `ninb.load_source(TDB)` checks the file and the pycalphad version
# and reads it into a pycalphad `Database` object, `db`. `db.phases` is a
# dictionary of the phases by name. For one phase, `.sublattices` holds the
# number of sites per formula on each sublattice and `.constituents` the species
# allowed on each one; `zip` pairs them up, sublattice by sublattice.

# %%
if TDB is not None:
    from course.materials.ninb import worked_example as ninb
    db = ninb.load_source(TDB)   # checks the file and the pycalphad version again
    for name in ("DELTA", "MU_PHASE"):
        phase = db.phases[name]
        print(f"{name}: {sum(phase.sublattices):g} atoms per formula")
        # sites per formula and the set of species allowed, for each sublattice
        for s, (sites, elements) in enumerate(zip(phase.sublattices, phase.constituents), start=1):
            print(f"  sublattice {s}: {sites:g} site{'s' if sites > 1 else ''}, may hold {', '.join(sorted(e.name for e in elements))}")
else:
    print("No database: the table in section 1 has the same sites per formula. Skip to section 4.")

# %% [markdown]
# ### Your turn (with the database): one endmember by hand
#
# Open your copy of the file in a text editor (its path was printed in section 2)
# and find the line `PARAMETER G(DELTA,NB:NB:NB;0)`: the δ endmember with Nb on
# all three sublattices. Its expression uses a named function of temperature.
# Inside an expression a function name ends with `#` (written `NAME#`); the `#`
# only marks it as a function, so search for `FUNCTION NAME` without it. A
# function has temperature ranges separated by
# `;`, each with its own expression; use the range that contains 1000 K.
#
# Most branches have the form
#
# $$G(T)=a+bT+cT\ln T+dT^2+eT^3+f\,T^{-1}+g\,T^{7}+h\,T^{-9}\quad(\mathrm{J/mol}),$$
#
# so `gibbs_branch` below takes those eight coefficients (missing ones are 0).
# Evaluate the branch at 1000 K, then the whole endmember expression. The result
# is per mole of **formula units** (four atoms). The file stays on your computer;
# do not paste its numbers into anything you share.
#
# **Reading the notation.** `G(DELTA,NB:NB:NB;0)` names the Gibbs energy of the
# phase DELTA with NB on sublattices 1, 2 and 3 (the colons separate the
# sublattices); `;0` is the order of the parameter (0 for an endmember). In the
# file, `*` means multiply, `**` a power, `LN(T)` the natural logarithm, and a
# range reads `T_low  expression;  T_high  Y` (more ranges follow) or `N` (last
# range). The numbers are relative to the elements' reference states (SER), as
# in Task 01.
#
# **Using `gibbs_branch`.** Its arguments have default values 0, so you pass
# only the coefficients that appear, by name, for example
# `gibbs_branch(1000.0, a=..., b=..., c=...)`. Match each term of the file to its
# coefficient: `T*LN(T)` goes to `c`, `T**2` to `d`, `T**(-1)` to `f`, and so
# on. Then add whatever else the endmember expression contains.

# %%
import math

def gibbs_branch(T, a=0.0, b=0.0, c=0.0, d=0.0, e=0.0, f=0.0, g=0.0, h=0.0):
    """One temperature branch in the usual polynomial form, J/mol."""
    return a + b * T + c * T * math.log(T) + d * T**2 + e * T**3 + f / T + g * T**7 + h * T**-9

T_HAND = 1000.0   # K
delta_nb_1000_hand = None   # J/mol formula, G(DELTA,NB:NB:NB;0) at 1000 K
if TDB is not None:
    check(delta_nb_1000_hand, "task05_delta_hand_1000")
else:
    print("Skipped: this exercise needs your copy of the database.")

# %% [markdown]
# ## 4. Formula basis and atom basis
#
# The hand result is per formula unit; pycalphad reports per atom. Mixing the
# two is one of the most common mistakes with ordered phases, so this section
# makes the conversion explicit.
#
# A database parameter for δ or μ is an energy per mole of **formula units**.
# pycalphad reports `GM` per mole of **atoms** (it has already divided by the
# atoms per formula), and phase amounts `NP` are also per mole of atoms. To go
# from a formula energy to an atom energy, divide **once**:
#
# $$G_m=\frac{G_\text{formula}}{\text{atoms per formula}} .$$
#
# Two endmember energies at 1000 K, from the course's own run of the database:
#
# | Endmember | Energy (J/mol formula) | Atoms per formula |
# |---|---:|---:|
# | δ, all Nb | your value from section 3; the variable `delta_formula` holds the course run's | 4 |
# | μ, all Ni | −368073.0553770607 | 13 |
#
# These are building blocks: an energy for all-Nb δ does not mean all-Nb δ is
# stable.
#
# Why divide: one mole of δ formula units contains 4 moles of atoms, so the
# energy per mole of atoms is a quarter of the energy per mole of formula units.
# The cell only stores the two numbers; it prints nothing.

# %%
import json
from pathlib import Path

ENERGIES = json.loads(Path("course/materials/ninb/results.json").read_text())["energy_checks"]  # saved course run
delta_formula = ENERGIES["delta_NB_NB_NB"]["formula_J_per_mol"]   # J/mol formula, δ all Nb, 1000 K (not printed)
mu_formula = -368073.0553770607       # J/mol formula, μ all Ni, 1000 K

# %% [markdown]
# ### Your turn
#
# 1. Convert both energies to J/mol of atoms (to at least 4 significant figures).
# 2. Someone takes `GM` for δ from pycalphad and divides it by 4. Is that right?
#    Answer `True` or `False`, and say in one sentence what the result would be.

# %%
delta_atom = None      # J/mol atoms, δ all Nb
mu_atom = None         # J/mol atoms, μ all Ni
divide_gm_by_4 = None  # True or False
check(delta_atom, "task05_delta_atom")
check(mu_atom, "task05_mu_atom")
check(divide_gm_by_4, "task05_divide_gm_again")

# %% [markdown]
# ## 5. A two-phase sample at 1200 K
#
# Amounts follow the same rule as energies. Here a sample made of two ordered
# phases is counted both ways.
#
# The saved calculation used one mole of atoms at 101325 Pa. At 1200 K and overall
# x(Nb) = 0.3416 (the grid point nearest to 0.35) it gives μ and δ side by side.
# `NP` is the amount of each phase in mol of atoms per mol of atoms; x(Nb) is the
# Nb fraction inside that phase.
#
# In the code, `saved["sample"]` is a dictionary read from the saved results;
# `sample["phases"]` is a list with one dictionary per phase. The format `!r`
# prints a number with all its digits.

# %%
import json
from pathlib import Path

saved = json.loads(Path("course/materials/ninb/results.json").read_text())  # the course run's results
sample = saved["sample"]
print(f"T = {sample['T_K']} K, overall x(Nb) = {sample['X_NB']:.4f}")
print(" phase      NP (mol atoms)          x(Nb) in the phase")
for row in sample["phases"]:
    print(f" {row['phase']:<9}  {row['atom_mole_fraction']!r:<22}  {row['x_NB']!r}")

# %% [markdown]
# ### Your turn
#
# 1. Amount balance: add the two `NP` values.
# 2. Nb balance: $\sum_\text{phases} NP\cdot x(\mathrm{Nb})$. Ni balance: the same with
#    $1-x(\mathrm{Nb})$. Do they give the overall composition?
# 3. Another way of counting the same sample: mol of **formula units** of each phase,
#    $NP/(\text{atoms per formula})$, to at least 4 significant figures.
# 4. If you weighted the phase compositions with those formula-unit amounts
#    (normalised to sum to one) instead of `NP`, would you get x(Nb) = 0.3416?
#
# "Normalised to sum to one" means: divide each formula-unit amount by the sum
# of both, so that the two weights add up to 1.

# %%
amount_sum = None           # mol atoms per mol atoms
nb_balance = None           # x(Nb) rebuilt from the phases
ni_balance = None           # x(Ni) rebuilt from the phases
delta_formula_units = None  # mol δ formula units in the 1 mol-atom sample
mu_formula_units = None     # mol μ formula units in the 1 mol-atom sample
formula_weights_ok = None   # True or False
check(amount_sum, "task05_amount_sum")
check(nb_balance, "task05_nb_balance")
check(ni_balance, "task05_ni_balance")
check(delta_formula_units, "task05_delta_formula_units")
check(mu_formula_units, "task05_mu_formula_units")
check(formula_weights_ok, "task05_formula_weights_balance")

# %% [markdown]
# ## 6. The phase diagram
#
# One sample is one point; repeating the calculation over many temperatures and
# compositions gives the whole phase diagram.
#
# Conditions: 61 temperatures from 300 to 3000 K (45 K apart), 51 overall
# compositions x(Nb) from 0.005 to 0.995, 101325 Pa, one mole of atoms, and all
# eight phases of the database allowed (LIQUID, FCC_A1, BCC_A2, HCP_A3, DELTA,
# MU_PHASE, NBNI8, BCC_B2), sampling density `pdens = 60`.
#
# With the database this cell computes the whole grid (10–25 s measured
# locally; it also checks every amount and component balance to 10⁻⁶). Without
# it, the cell reads the same grid saved by the course
# (`course/self_study/generated/ninb_grid.json`, amounts rounded to six digits).
#
# Each point is the composition of a phase found at one grid temperature; empty
# areas between points are two-phase regions. Each phase has its own marker shape.
#
# **Phase names.** LIQUID is the melt; FCC_A1, BCC_A2 and HCP_A3 are the
# face-centred cubic, body-centred cubic and hexagonal close-packed solutions
# (Ni is FCC, Nb is BCC); BCC_B2 is an ordered form of BCC; DELTA, MU_PHASE and
# NBNI8 are the intermetallic compounds.
#
# **The pycalphad call.** `equilibrium(db, components, phases, conditions,
# calc_opts=...)` takes a *conditions dictionary* whose keys come from
# `pycalphad.variables` (imported as `v`): `v.T` temperature in K, `v.X("NB")`
# overall mole fraction of Nb, `v.P` pressure in Pa, `v.N` total moles of atoms.
# When a condition is given as an array, pycalphad computes every combination:
# here 61 × 51 equilibria in one call. The result `eq` is an xarray Dataset with
# fields such as `Phase` (phase names), `NP` (phase amounts) and `X` (phase
# compositions); `grid_rows(...)` turns it into the compact list format below
# and runs the balance checks.
#
# **The grid format.** `ROWS[i_T][i_x]` is the *cell* at temperature number
# `i_T` and composition number `i_x`: a list with one entry
# `[phase index, NP, x(Nb) in the phase]` per phase present. The phase index
# points into `PHASES`.
#
# **The functions.** `phase_points(name)` collects all (x(Nb), T) points of one
# phase; `draw_diagram(ax)` plots them for every phase; `column(x_target)` prints
# the phases at the grid composition nearest to `x_target` for temperatures
# between 1300 and 1700 K. The last line runs it at x(Nb) ≈ 0.25 as an example.

# %%
import time
import matplotlib.pyplot as plt

grid = json.loads(Path("course/self_study/generated/ninb_grid.json").read_text())  # the saved grid
if TDB is not None:
    from pycalphad import equilibrium, variables as v
    from course.self_study.grid_export import grid as grid_rows
    started = time.monotonic()  # a clock reading in seconds, to time the calculation
    # T and X(NB) are arrays: pycalphad computes every combination of the two
    eq = equilibrium(db, ninb.COMPONENTS, ninb.PHASES,
                     {v.T: ninb.TEMPERATURES, v.X("NB"): ninb.COMPOSITIONS, v.P: ninb.PRESSURE, v.N: 1},
                     calc_opts={"pdens": 60})
    computed = grid_rows(eq, "NB", ninb.PHASES, ninb.balance_checks)   # stops if a balance fails
    # count the cells that are identical to the saved grid
    same = sum(a == b for row_a, row_b in zip(computed, grid["modes"]["model"]) for a, b in zip(row_a, row_b))
    print(f"Computed {len(grid['T_K'])} × {len(grid['x'])} grid in {time.monotonic() - started:.1f} s; "
          f"{same} of {len(grid['T_K']) * len(grid['x'])} cells equal the saved grid.")
    grid["modes"]["model"] = computed  # use your own calculation from here on
else:
    print("No database: using the saved grid.")

PHASES = grid["phases"]
TEMPS = grid["T_K"]
XS = grid["x"]
ROWS = grid["modes"]["model"]   # ROWS[i_T][i_x] = [[phase index, NP, x(Nb) in phase], ...]
MARKERS = {"LIQUID": ".", "FCC_A1": "s", "BCC_A2": "D", "HCP_A3": "h",
           "DELTA": "^", "MU_PHASE": "v", "NBNI8": "P", "BCC_B2": "X"}  # matplotlib marker codes

def phase_points(name):
    """(x(Nb) in phase, T) for every grid cell where the phase is present."""
    k = PHASES.index(name)  # the phase's index in PHASES
    return [(c[2], T) for T, row in zip(TEMPS, ROWS) for cell in row for c in cell if c[0] == k]

def draw_diagram(ax):
    for name in PHASES:
        points = phase_points(name)
        if points:  # phases never found on the grid are left out
            # zip(*points) splits the (x, T) pairs into one list of x and one list of T
            ax.plot(*zip(*points), MARKERS[name], ms=4, ls="none", label=name)
    ax.set(xlabel="x(Nb), mole fraction of atoms", ylabel="T (K)", xlim=(0, 1))
    ax.legend(fontsize=9, ncol=2, loc="lower right")

fig, ax = plt.subplots(figsize=(7, 5.5))
draw_diagram(ax)
ax.set(ylim=(300, 3000), title="Ni–Nb, Sun et al. database: phases at each grid point")
plt.show()

def column(x_target, t_min=1300, t_max=1700):
    """Table of the phases at the grid composition nearest to x_target."""
    i = min(range(len(XS)), key=lambda j: abs(XS[j] - x_target))  # index of the nearest grid composition
    print(f"overall x(Nb) = {XS[i]:.4f}")
    print("  T (K)   phase: NP (mol atoms), x(Nb) in phase")
    for T, row in zip(TEMPS, ROWS):
        if t_min <= T <= t_max:
            print(f"  {T:6.0f}  " + ";  ".join(f"{PHASES[c[0]]}: {c[1]:.4f}, {c[2]:.4f}" for c in row[i]))

column(0.25)   # an example column, through δ

# %% [markdown]
# ### Your turn: two eutectics
#
# Where the liquid region narrows to a point between two liquid + solid regions,
# a **eutectic** sits at the tip: on cooling, the liquid turns into two solids at
# one temperature. In a binary at fixed pressure three phases coexist only at
# that single temperature, so a 45 K grid never lands exactly on it.
#
# Use `column(...)` at x(Nb) ≈ 0.40 and at x(Nb) ≈ 0.16:
#
# 1. At x ≈ 0.40: the lowest grid temperature that is still all liquid, and the
#    highest one with no liquid. The eutectic lies between them.
# 2. At x ≈ 0.16: the same two temperatures, and the name of the **Nb-richer**
#    solid phase just below (as written in the table).
#
# Why only one temperature: Gibbs's phase rule at fixed pressure gives the
# number of conditions you can still change freely as $F=C-P_h+1$, with $C$
# components and $P_h$ coexisting phases. For $C=2$ and $P_h=3$, $F=0$: nothing
# can vary, so temperature and all three compositions are fixed. Add a code
# cell for each `column(...)` call; `column(0.40, 1200, 1800)` widens the
# temperature window if you need it.

# %%
eut040_liquid = None     # K, lowest all-liquid grid temperature at x ≈ 0.40
eut040_solid = None      # K, highest grid temperature without liquid at x ≈ 0.40
eut016_liquid = None     # K, lowest all-liquid grid temperature at x ≈ 0.16
eut016_solid = None      # K, highest grid temperature without liquid at x ≈ 0.16
eut016_nb_richer = None  # phase name in quotes, exactly as written in the table
check(eut040_liquid, "task05_eut040_liquid")
check(eut040_solid, "task05_eut040_solid")
check(eut016_liquid, "task05_eut016_liquid")
check(eut016_solid, "task05_eut016_solid")
check(eut016_nb_richer, "task05_eut016_nb_richer")

# %% [markdown]
# ## 7. What μ looks like as a crystal
#
# The database numbers the μ sublattices 1–5 but does not say which crystal sites
# they are. A crystal structure does. Here is a sketch built from the published μ
# prototype (Fe₇W₆ structure, space group R-3m, from the AFLOW prototype library:
# M. J. Mehl et al., *Comput. Mater. Sci.* 136 (2017) S1,
# [doi:10.1016/j.commatsci.2017.01.017](https://doi.org/10.1016/j.commatsci.2017.01.017)).
# It uses the prototype's cell size, not a Ni–Nb measurement.
#
# The file holds a block of 2 × 2 × 1 hexagonal cells. Each atom carries the label
# of its crystal site: `3a`, three different `6c` sites and `18h`.
#
# **Some words.** A *prototype* is a well-known compound whose crystal structure
# gives its name to every compound with the same arrangement of atoms (here
# Fe₇W₆ for the μ phase). The *space group* (R-3m) lists the symmetry
# operations of the crystal. Sites that symmetry maps onto each other form one
# *Wyckoff position*, labelled by a number and a letter such as `18h`; atoms on
# the same Wyckoff position are equivalent, so a sublattice model may treat them
# as one sublattice.
#
# **The code.** `Counter` (from Python's `collections`) counts how often each
# value occurs: here how many atoms of the block carry each site label.

# %%
from collections import Counter

mu = json.loads(Path("course/self_study/generated/mu_structure.json").read_text())
print(mu["name"], "·", mu["space_group"], "·", mu["supercell"])
counts = Counter(atom["site"] for atom in mu["atoms"])  # {site label: number of atoms in the block}
print(" site   atoms in the 2 × 2 × 1 block")
for site, n in counts.items():
    print(f" {site:<5}  {n}")
print(" total ", sum(counts.values()))

# %% [markdown]
# ### Your turn
#
# 1. How many atoms are in **one** hexagonal cell, and how many μ formula units
#    (13 atoms each) is that?
# 2. Per formula unit, how many atoms sit on `18h` sites? Which database
#    sublattice has that many sites per formula?
# 3. The three `6c` sites each give 2 atoms per formula, like sublattices 1, 2 and
#    3. Does the database tell you which `6c` site is sublattice 1?

# %%
atoms_per_cell = None      # atoms in one hexagonal cell
formula_per_cell = None    # μ formula units in one hexagonal cell
atoms_18h_per_formula = None
six_c_order_known = None   # True or False
check(atoms_per_cell, "task05_mu_atoms_per_cell")
check(formula_per_cell, "task05_mu_formula_per_cell")
check(atoms_18h_per_formula, "task05_mu_18h_per_formula")
check(six_c_order_known, "task05_mu_6c_order_known")

# %% [markdown]
# ## 8. After your attempt
#
# Full worked answers are in
# [course/materials/ninb/answers.md](../course/materials/ninb/answers.md).
#
# **First cell: counting, the hand endmember and the amount basis.** It shows
# the ideal fillings of δ and μ, recomputes the two endmember energies with the
# database (pycalphad's `Model.G` is per formula unit, `Model.GM` per mole of
# atoms), compares the δ value with the course's own hand calculation, and
# checks that formula energy / atoms per formula = `GM`.

# %% cellView="form"
#@title After your attempt: sublattice counting, the hand endmember and the amount basis
show("δ, Nb on sublattice 1", DELTA_SITES, [1, 0, 0])
show("μ, Nb on sublattices 1, 2, 3 and 5", MU_SITES, [1, 1, 1, 0, 1])
confirm(x_nb(DELTA_SITES, [1, 0, 0]), 1 / 4, "x(Nb) of δ-NbNi₃", tol=1e-12)
confirm(x_nb(MU_SITES, [1, 1, 1, 0, 1]), 7 / 13, "x(Nb) of μ-Nb₇Ni₆", tol=1e-12)

energies = saved["energy_checks"]
if TDB is not None:
    recomputed = ninb.energy_checks(db)   # pycalphad Model.G (formula) and Model.GM (atoms) at 1000 K
    for key, label in (("delta_NB_NB_NB", "δ all Nb"), ("mu_all_NI", "μ all Ni")):
        confirm(recomputed[key]["formula_J_per_mol"], energies[key]["formula_J_per_mol"],
                f"{label}, J/mol formula, recomputed from the database", tol=1e-8)
        confirm(recomputed[key]["atom_J_per_mol"], energies[key]["atom_J_per_mol"],
                f"{label}, J/mol atoms (GM), recomputed from the database", tol=1e-8)
    confirm(recomputed["delta_NB_NB_NB"]["formula_J_per_mol"], energies["hand_delta_formula_J_per_mol"],
            "δ all Nb: pycalphad against the course's hand calculation", tol=1e-8)
else:
    print("No database: checking the saved energies only.")
for key, atoms, label in (("delta_NB_NB_NB", 4, "δ all Nb"), ("mu_all_NI", 13, "μ all Ni")):
    formula, atom = energies[key]["formula_J_per_mol"], energies[key]["atom_J_per_mol"]
    print(f"{label}: {formula:.6f} J/mol formula / {atoms} = {formula / atoms:.6f} J/mol atoms")
    confirm(formula / atoms, atom, f"{label}: formula energy / {atoms} equals GM", tol=1e-8)
wrong = energies["delta_NB_NB_NB"]["atom_J_per_mol"] / 4  # the mistake: GM is already per atom
print(f"Dividing GM by 4 again gives {wrong:.3f} J: the energy of a quarter mole of atoms, "
      "neither per formula nor per atom.")

# %% [markdown]
# **Second cell: balances and the formula-unit recount.** It adds up the
# amounts and the Nb and Ni in the saved sample, converts `NP` into formula
# units, and shows what goes wrong when formula units are used as weights. It
# then checks the sample against the grid and, with the database, against your
# own calculation: `eq.sel(T=1200, X_NB=0.35, method="nearest")` picks the grid
# point nearest to those conditions out of the xarray Dataset, and `.ravel()`
# flattens an array to one dimension.

# %% cellView="form"
#@title After your attempt: balances at 1200 K and the formula-unit recount
rows = sample["phases"]
nb = sum(r["atom_mole_fraction"] * r["x_NB"] for r in rows)        # Σ NP·x(Nb)
ni = sum(r["atom_mole_fraction"] * (1 - r["x_NB"]) for r in rows)  # Σ NP·x(Ni)
total = sum(r["atom_mole_fraction"] for r in rows)                 # Σ NP
print(f"amounts: {total:.9f} mol atoms; Nb: {nb:.9f}; Ni: {ni:.9f}")
confirm(total, 1.0, "Amount balance (saved sample)", tol=1e-6)
confirm(nb, sample["X_NB"], "Nb balance (saved sample)", tol=1e-6)
confirm(ni, 1 - sample["X_NB"], "Ni balance (saved sample)", tol=1e-6)

per_formula = {"DELTA": 4, "MU_PHASE": 13}  # atoms per formula unit
units = {r["phase"]: r["atom_mole_fraction"] / per_formula[r["phase"]] for r in rows}  # mol formula units
print(" phase      NP (mol atoms)  atoms per formula  mol formula units")
for r in rows:
    print(f" {r['phase']:<9}  {r['atom_mole_fraction']:.6f}        {per_formula[r['phase']]:>2}"
          f"                 {units[r['phase']]:.6f}")
weights = {p: n / sum(units.values()) for p, n in units.items()}  # formula units, normalised to sum to 1
mixed_up = sum(weights[r["phase"]] * r["x_NB"] for r in rows)
print(f"Weighting x(Nb) with formula units instead of NP gives {mixed_up:.4f}, not {sample['X_NB']:.4f}:")
print("formula units are a recount for reporting; balances always use NP.")

# grid indices of 1200 K and of the composition nearest to the sample's x(Nb)
i_T, i_x = TEMPS.index(sample["T_K"]), min(range(len(XS)), key=lambda j: abs(XS[j] - sample["X_NB"]))
for cell in ROWS[i_T][i_x]:
    match = next(r for r in rows if r["phase"] == PHASES[cell[0]])  # the saved row of the same phase
    confirm(cell[1], match["atom_mole_fraction"], f"{PHASES[cell[0]]} amount in the grid against the saved sample", tol=1e-6)
    confirm(cell[2], match["x_NB"], f"{PHASES[cell[0]]} x(Nb) in the grid against the saved sample", tol=1e-6)
if TDB is not None:
    point = eq.sel(T=1200, X_NB=0.35, method="nearest")   # the same sample, freshly computed
    for name, amount, x in zip(point.Phase.values.ravel(), point.NP.values.ravel(),
                               point.X.sel(component="NB").values.ravel()):
        if name:  # skip unused phase slots (empty name)
            match = next(r for r in rows if r["phase"] == name)
            confirm(float(amount), match["atom_mole_fraction"], f"{name} NP recomputed from the database", tol=1e-6)
            confirm(float(x), match["x_NB"], f"{name} x(Nb) recomputed from the database", tol=1e-6)

# %% [markdown]
# **Third cell: the two eutectics.** It prints the four grid cells that bracket
# the two eutectics and circles them on a zoom of the diagram.

# %% cellView="form"
#@title After your attempt: the two eutectics on the diagram
cells = [(0.401, 1470), (0.401, 1425), (0.1634, 1560), (0.1634, 1515)]  # (x(Nb), T in K)
print(" x(Nb)   T (K)  phases (NP, x(Nb) in phase)")
for x0, T in cells:
    i = min(range(len(XS)), key=lambda j: abs(XS[j] - x0))
    print(f" {XS[i]:.4f}  {T:5.0f}  " + "; ".join(f"{PHASES[c[0]]} ({c[1]:.3f}, {c[2]:.3f})" for c in ROWS[TEMPS.index(T)][i]))
print("Eutectic near x ≈ 0.40 between 1425 and 1470 K (liquid → δ + μ);")
print("eutectic near x ≈ 0.16 between 1515 and 1560 K (liquid → FCC_A1 + δ).")

fig, ax = plt.subplots(figsize=(7, 5))
draw_diagram(ax)
for x0, T in cells:
    ax.plot([x0], [T], "o", ms=14, mfc="none", mec="black", mew=1.5)  # open black circle around the cell
ax.set(xlim=(0, 0.7), ylim=(1200, 1800),
       title="Zoom: the circled grid cells bracket the two eutectics")
plt.show()

# %% [markdown]
# **Fourth cell: the μ cell by site.** The number in a Wyckoff label is the
# number of equivalent positions in one conventional (here hexagonal) cell, so
# `18h` means 18 atoms per cell. Dividing by the formula units per cell gives
# atoms per formula unit, which can be compared with the database's sites per
# formula. The two pictures show the 2 × 2 × 1 block from above (along the
# hexagonal c axis) and from the side, with one marker shape and colour per
# site.

# %% cellView="form"
#@title After your attempt: the μ cell, coloured and shaped by site
print(" site   Wyckoff  atoms per cell  atoms per formula  database sublattice")
for s in mu["sites"]:
    print(f" {s['site']:<5}  {s['wyckoff']:<7}  {s['atoms_per_cell']:>14}  {s['atoms_per_cell'] / mu['formula_units_per_cell']:>17g}  {s['sublattice']}")
confirm(sum(s["atoms_per_cell"] for s in mu["sites"]), 39, "Atoms per hexagonal cell", tol=0)
confirm(sum(counts.values()) / 4, mu["atoms_per_hexagonal_cell"], "Block of 4 cells / 4", tol=0)
confirm(mu["atoms_per_hexagonal_cell"] / 13, 3, "Formula units per cell", tol=0)
print("By count: 3a ↔ the 1-site sublattice (3 atoms per cell = 1 per formula) and 18h ↔ the 6-site")
print("sublattice (18 per cell = 6 per formula). The three 6c sites match the three 2-site sublattices")
print("as a group, but the database does not say which is which.")

SITE_STYLE = {"3a": ("o", "tab:blue"), "6c_1": ("^", "tab:orange"), "6c_2": ("v", "tab:green"),
              "6c_3": ("D", "tab:red"), "18h": ("s", "tab:purple")}  # (marker, colour) per site
fig, (top, side) = plt.subplots(1, 2, figsize=(10, 6), gridspec_kw={"width_ratios": [1.3, 1]})
for site, (marker, colour) in SITE_STYLE.items():
    xyz = [a["xyz_A"] for a in mu["atoms"] if a["site"] == site]  # Cartesian coordinates in Å
    label = f"{site} ({'Ni' if site == '18h' else 'Nb'} in ideal Nb₇Ni₆)"
    top.plot([p[0] for p in xyz], [p[1] for p in xyz], marker, color=colour, ms=7, ls="none", label=label)  # x–y
    side.plot([p[0] for p in xyz], [p[2] for p in xyz], marker, color=colour, ms=7, ls="none")              # x–z
top.set(xlabel="x (Å)", ylabel="y (Å)", title="Looking down c (2 × 2 cells)", aspect="equal")
side.set(xlabel="x (Å)", ylabel="z along c (Å)", title="Side view")
top.legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
fig.tight_layout()
plt.show()

# %% [markdown]
# ## 9. Limits, and the end of the task notebooks
#
# **Limits.** The diagram shows what the published Ni–Nb database predicts on a
# 45 K × 0.0198 grid; it is not a measurement and does not give exact boundaries or
# eutectic temperatures. Comparing it with Fig. 8(a) of Sun's manuscript (printed
# p. 42) is a side-by-side look, not a fit. HCP_A3 and BCC_B2 were allowed but never
# appear on this grid; that alone does not prove they are never stable. The
# endmember energies are model building blocks, not stable materials. The
# database's magnetic terms (FCC_A1, BCC_A2, HCP_A3) are already in every energy;
# do not add another. The μ sketch uses the prototype's cell, and only two of the
# five μ sublattices can be matched to crystal sites by counting.
#
# **End note.** This is the last task notebook. From the invented one-component
# model in f1 to a published database with five sublattices here, the same habits
# carried every step: write down the amount basis, check balances by hand, and say
# what a calculation does not show.
#
# Worked answers: [course/materials/ninb/answers.md](../course/materials/ninb/answers.md).
# Task text and the exercise list: [course/materials/ninb/README.md](../course/materials/ninb/README.md).
