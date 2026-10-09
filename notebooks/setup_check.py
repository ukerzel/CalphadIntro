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
# # Setup check
#
# Run this notebook **before the course** (and instructors: the day before). It
# checks that Python, the course code, pycalphad and plotting work, and tells you
# which parts of the course you are ready for. Nothing here is graded.
#
# - **On your own computer:** from the course folder run `poetry install --with dev`,
#   then `poetry run jupyter lab`, and open `notebooks/setup_check.ipynb`.
# - **In Colab:** use the "Open in Colab" link; the first cell installs what it needs
#   (a few minutes the first time) and then restarts the session, which Colab reports
#   as a crash. That is expected: run the first cell again, then the rest.
#
# Run the cells from top to bottom (in Jupyter: *Run → Run All Cells*).
#
# **How a notebook works.** A notebook is a list of *cells*. Text cells like this
# one explain; *code cells* (grey boxes) contain Python. Click into a code cell and
# press **Shift + Enter** to run it: its output appears below it and the cursor
# moves to the next cell. Cells share one running Python session (the *kernel*),
# so a name defined in one cell can be used in every later cell, but only after
# the defining cell has run. If you see `NameError: name '...' is not defined`,
# an earlier cell has not been run yet. Lines starting with `#` inside a code
# cell are comments: Python ignores them; they are there for you to read.
#
# The first code cell below is the same in every course notebook. It finds the
# course folder (or, in Colab, downloads it), makes the course code importable and
# prints the Python and package versions. A version that differs from the one the
# course was tested with is marked with `←`; that usually changes only the last
# digits of results.

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
# ## 1. The course code
#
# The first steps use an invented component A with two phases. The course code
# gives each phase's molar Gibbs energy in J/mol; at 900 K the solid has
# g = 1000 − 10·900 = −8000 J/mol (Day 1, W4).
#
# The model is two straight lines in temperature T (in K): $g_{\rm SOLID}=1000-10\,T$
# and $g_{\rm LIQUID}=7000-16\,T$, both in J/mol (joules per mole of A atoms).
# The cell below
#
# 1. imports the course module `one_component_manual` under the short name `unary`
#    (`import ... as ...` only gives it a shorter name);
# 2. calls `unary.gibbs(900.0)`, which returns the two energies at 900 K, and
#    stores them in two names at once (`a, b = ...` "unpacks" a pair of values);
# 3. prints them. In `f"...{g_solid:.0f}..."` (an *f-string*) the value inside
#    `{}` is inserted into the text, and `:.0f` rounds it to 0 decimals;
# 4. calls `confirm(value, expected, what, tol)`, a course helper that compares a
#    value with the number from the lesson. It prints a ✓ line if they agree
#    within the tolerance `tol` and stops with an error message if not.
#
# Expect a ✓ line. An error here means the course code cannot be found: check that
# the setup cell ran without an error.

# %%
from course.foundations import one_component_manual as unary

g_solid, g_liquid = unary.gibbs(900.0)   # both in J/mol at T = 900 K
print(f"g_SOLID(900 K) = {g_solid:.0f} J/mol, g_LIQUID(900 K) = {g_liquid:.0f} J/mol")
confirm(g_solid, -8000.0, "Solid Gibbs energy at 900 K", tol=1e-9)
# `ready` is a dictionary: it maps a name (the key) to True/False. Each section adds one entry.
ready = {"course code": True}

# %% [markdown]
# At 900 K the solid has the lower Gibbs energy (−8000 against −7400 J/mol), so the
# solid is the stable phase there.
#
# ## 2. pycalphad with the course's own invented database
#
# The same model is stored as a small database file in the course folder.
# pycalphad finds the equilibrium at 1100 K: all liquid, with g = −10600 J/mol.
# The first pycalphad call takes a few seconds.
#
# **pycalphad** is the open-source Python package the course uses for CALPHAD
# calculations. It reads phase descriptions from a database file (a *TDB* file)
# and finds the equilibrium: the phase amounts that give the lowest total Gibbs
# energy at the given temperature and pressure. Here it should agree with the
# hand calculation: at 1100 K the liquid line gives 7000 − 16·1100 = −10600 J/mol,
# lower than the solid's 1000 − 10·1100 = −10000 J/mol, so the sample is all liquid.
#
# `equilibrium_at` returns a dictionary; `result['fractions']` holds the amount
# of each phase (as fractions of the whole sample) and `result['GM']` the molar
# Gibbs energy of the equilibrium state in J/mol.

# %%
from course.foundations import one_component_tools as unary_pycalphad

result = unary_pycalphad.equilibrium_at(1100.0)   # T in K; runs pycalphad on the invented database
print(f"At 1100 K pycalphad finds {result['fractions']} with GM = {result['GM']:.1f} J/mol")
confirm(result["GM"], -10600.0, "Equilibrium Gibbs energy at 1100 K", tol=1e-6)
ready["pycalphad"] = True   # add a second entry to the dictionary

# %% [markdown]
# ## 3. A plot
#
# You should see two straight lines crossing at 1000 K (solid: full line,
# liquid: dashed). If no figure appears, plots are not working yet.
#
# The crossing is where the two energies are equal:
# $1000-10T=7000-16T$ gives $6T=6000$, so $T=1000$ K. Below it the solid line is
# lower, above it the liquid line.
#
# Three packages appear here for the first time:
#
# - **numpy** (imported as `np`) works with whole arrays of numbers at once.
#   `np.linspace(800, 1200, 41)` makes 41 evenly spaced values from 800 to 1200,
#   both ends included (steps of 10 K).
# - `unary.gibbs(temperatures)` accepts the whole array and returns a table with
#   one row per temperature and two columns (solid, liquid). `energies[:, 0]`
#   means "all rows, column 0" (Python counts from 0), that is the solid column.
# - **matplotlib** (`plt`) draws figures. `plt.subplots` creates a figure `fig`
#   with one set of axes `ax`; `ax.plot(x, y, style, label=...)` draws a line
#   (`"-"` full, `"--"` dashed); `ax.legend()` shows the labels and `plt.show()`
#   displays the figure.

# %%
import matplotlib.pyplot as plt
import numpy as np

temperatures = np.linspace(800, 1200, 41)          # K, 800, 810, …, 1200
energies = unary.gibbs(temperatures)               # shape (41, 2): columns SOLID, LIQUID, J/mol
fig, ax = plt.subplots(figsize=(5, 3.2))           # figure size in inches (width, height)
ax.plot(temperatures, energies[:, 0] / 1000, "-", label="SOLID")    # divide by 1000: J/mol → kJ/mol
ax.plot(temperatures, energies[:, 1] / 1000, "--", label="LIQUID")
ax.set_xlabel("T (K)")
ax.set_ylabel("g (kJ/mol)")
ax.legend()
plt.show()
ready["plots"] = True

# %% [markdown]
# ## 4. Published databases (for the full Task 01–05 calculations)
#
# The real-alloy tasks use two published databases. Tasks 01–04 use the Cu–Ni
# database when it is present (Task 01 for its whole calculation, Tasks 02–04 for
# optional parts); Task 05 uses the Ni–Nb database in the same way. Without them
# every task still runs in no-database mode from saved results. You fetch the
# databases yourself; they are kept outside the course folder and checked by size
# and SHA-256.
#
# | Database | Source |
# |---|---|
# | Cu–Ni, `CuNi-92Mey-LB.tdb` | [phasediagrams.org](https://phasediagrams.org/phase-diagram/CuNi-92Mey-LB.tdb); S. an Mey, *Calphad* 16 (1992) 255–260; B. Hallstedt, *Calphad* 89 (2025) 102833 |
# | Ni–Nb, `calpha_102563_Nb-Ni_new_mmc1.tdb` | [supplement of Sun et al.](https://doi.org/10.1016/j.calphad.2023.102563), *Calphad* 82 (2023) 102563 |
#
# Change `DOWNLOAD` to `True` to fetch them now. If a download is refused,
# the message says how to get the file in your browser instead.
#
# SHA-256 is a fingerprint of a file's contents: if even one character differs,
# the fingerprint differs. The check makes sure you calculate with exactly the
# file the course was tested with.
#
# The helper `database(name, download=...)` looks for a checked copy of the
# database. It returns the file's location if it finds (or downloads) one, and the
# special value `None` if not. `... is not None` turns that into True (database
# available) or False (no-database mode). With `DOWNLOAD = False` nothing is
# fetched; the cell only reports what is already there.

# %%
DOWNLOAD = False   # set to True (capital T) and run the cell again to fetch both databases
ready["Cu–Ni database"] = database("cuni", download=DOWNLOAD) is not None   # True if a checked copy was found
ready["Ni–Nb database"] = database("ninb", download=DOWNLOAD) is not None

# %% [markdown]
# ## 5. What you are ready for
#
# The last cell reads the `ready` dictionary and prints one line for the
# invented-model notebooks and one line for each group of tasks. Two Python
# details: `[item for item in basics if not ready.get(item)]` is a *list
# comprehension*, a compact loop that collects the basic checks that did not pass
# (`ready.get(item)` gives `None` for a check that never ran); and
# `a if condition else b` picks one of two texts.
#
# If a line says "not yet", go back to the section named in brackets and look at
# its error message. "Saved results" is enough to follow every task; the
# databases are needed only to repeat the full calculations yourself.

# %%
basics = ["course code", "pycalphad", "plots"]
missing = [item for item in basics if not ready.get(item)]   # basic checks that did not pass
print(f"{'ready' if not missing else 'not yet'}: Day 1 and Day 2 notebooks, Task 00"
      + (f"  (missing: {', '.join(missing)})" if missing else ""))
# One line per database: which tasks it serves, and whether you can run them in full.
for name, tasks in (("Cu–Ni database", "Tasks 01–04 (Cu–Ni)"), ("Ni–Nb database", "Task 05 (Ni–Nb)")):
    if missing:
        print(f"not yet: {tasks}  (missing: {', '.join(missing)})")
    elif ready[name]:
        print(f"ready (full calculation): {tasks}")
    else:
        print(f"ready (saved results; download the {name} for the full calculation): {tasks}")
