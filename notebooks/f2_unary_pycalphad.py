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
# ## 1. A database can be very small (W7)
#
# The course's invented model is stored as a TDB file. Each `PARAMETER` line holds
# one phase's Gibbs energy: a lower temperature limit, the expression, the upper
# limit, `N` (no further range) and `!` (end of record). Compare with f1:
# SOLID 1000 − 10T, LIQUID 7000 − 16T.

# %%
from pathlib import Path

TDB = Path("course/foundations/one_component_model.tdb")
print(TDB.read_text())

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

# %%
from pycalphad import Database, calculate, equilibrium, variables as v

database = Database(str(TDB))
components = ["A"]
phases = ["SOLID", "LIQUID"]
temperatures = [800.0, 900.0, 1000.0, 1100.0, 1200.0]

solid_result = calculate(database, components, "SOLID", T=temperatures, P=100000, output="GM")
print("SOLID GM:", solid_result.GM.values.reshape(-1))

# %% [markdown]
# ### Your turn
#
# Before running the next cell, predict the LIQUID value at 1200 K (J/mol).
# Why is it fine to *evaluate* the liquid at 900 K, where it is not stable?

# %%
liquid_1200 = None  # J/mol
check(liquid_1200, "f2_gl_1200")

# %%
liquid_result = calculate(database, components, "LIQUID", T=temperatures, P=100000, output="GM")
print("LIQUID GM:", liquid_result.GM.values.reshape(-1))

# %% [markdown]
# ## 3. Ask for the equilibrium
#
# `equilibrium` returns the minimum molar Gibbs energy and the phases it uses, with
# their amounts `NP`. With N = 1 mol the amounts are also the fractions.

# %%
conditions = {v.T: 900.0, v.P: 100000.0, v.N: 1.0}
answer = equilibrium(database, components, phases, conditions)
print("GM at 900 K:", float(answer.GM.values.squeeze()), "J/mol")
for phase, amount in zip(answer.Phase.values.reshape(-1), answer.NP.values.reshape(-1)):
    if phase:
        print(" ", phase, float(amount))

# %% [markdown]
# ### Your turn (W7)
#
# What happens at 1100 K if LIQUID is **not allowed**? Predict the minimum GM
# (J/mol) with only SOLID, then run the next cell. Why is that not the equilibrium
# of the full model?

# %%
solid_only_1100 = None  # J/mol
check(solid_only_1100, "f2_solid_only_1100")

# %%
for allowed in (["SOLID", "LIQUID"], ["SOLID"]):
    result = equilibrium(database, components, allowed, {v.T: 1100.0, v.P: 100000.0, v.N: 1.0})
    print(f"1100 K with {allowed}: GM = {float(result.GM.values.squeeze()):.1f} J/mol")

# %% [markdown]
# ## After your attempt: compare pycalphad with the plain model
#
# Both routes use the same model, so they must agree at every temperature: the
# phase energies, the minimum, and HM and SM (1000 and 7000 J/mol; 10 and 16 J/(mol K)).

# %% cellView="form"
#@title After your attempt: run to compare pycalphad with f1's plain model
from course.foundations import one_component_manual as plain
from course.foundations import one_component_tools as tools
import numpy as np

properties = tools.phase_properties(temperatures)
print(" T (K)   SOLID GM   LIQUID GM   minimum   pycalphad minimum")
for i, T in enumerate(temperatures):
    gs, gl = plain.gibbs(T)
    found = tools.equilibrium_at(T)
    print(f"{T:6.0f} {gs:10.0f} {gl:11.0f} {min(gs, gl):9.0f} {found['GM']:12.1f}  {found['fractions']}")
    confirm(found["GM"], min(gs, gl), f"pycalphad minimum at {T:.0f} K", tol=1e-6)
confirm(float(np.max(np.abs(properties["GM"] - plain.gibbs(temperatures)))), 0.0, "GM of both phases at all five temperatures", tol=1e-7)
print("HM (J/mol):", properties["HM"][0], " SM (J/(mol K)):", properties["SM"][0])
confirm(float(np.max(np.abs(properties["HM"] - [1000.0, 7000.0]))), 0.0, "HM of SOLID and LIQUID at all five temperatures", tol=1e-7)
confirm(float(np.max(np.abs(properties["SM"] - [10.0, 16.0]))), 0.0, "SM of SOLID and LIQUID at all five temperatures", tol=1e-7)

# %% [markdown]
# At 1000 K pycalphad reports one phase, but every balanced split of SOLID and LIQUID
# has the same energy there: the returned fractions are one valid answer, not *the* answer.
#
# **Limits.** The database is the invented f1 model, valid only for 800–1200 K at
# 100000 Pa; its element data are placeholders. Loading a database does not by
# itself give an equilibrium. Next: [f3 · binary mixtures](f3_binary_mixing_potentials.ipynb).
