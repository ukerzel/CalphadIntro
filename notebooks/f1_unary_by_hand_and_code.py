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
# # f1 · One component, two phases: by hand and in code
#
# **Learning question:** for one invented component A that can be SOLID or LIQUID,
# which phase is stable at a given temperature, and what may an optimiser change?
#
# Used in: Day 1 W4–W6 and W8 (W5 is the demonstration), Lesson 1, self-study step 01.
# Work each "your turn" on paper first, then type your value.
# Labels such as (W4), (D1), (Lesson 5) or Clinic D point to the printed one-day
# primers (Day 1 and Day 2 worksheets) and the detailed lessons of the classroom
# course in the repository. Working alone on the website, you only need the step
# numbers.
#
# **The plan.** f0 showed that at fixed T and p the equilibrium state has the lowest
# Gibbs energy G. Here that idea is used on the simplest possible case: one kind of
# atom that can be either solid or liquid. You will (1) write down each phase's
# Gibbs energy as a straight line in T, (2) compare the two lines at several
# temperatures, first by hand and then with NumPy, and (3) see what a computer
# "optimiser" is allowed to change when it looks for the minimum.
#
# Run the setup cell first (see f0 for what it prints and for the `check` and
# `confirm` helpers).

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
# ## 1. The whole model (W4)
#
# Closed bulk sample, one mole of A atoms, p = 100000 Pa, 800–1200 K, only SOLID and
# LIQUID. A is invented, not a real element. With constant h and s in each phase,
# g = h − Ts:
#
# | Phase | h (J/mol) | s (J/(mol K)) | g (J/mol) |
# |---|---:|---:|---|
# | SOLID | 1000 | 10 | 1000 − 10T |
# | LIQUID | 7000 | 16 | 7000 − 16T |
#
# **Reading the table.** Lower-case letters are *molar* quantities, per mole of
# atoms: h is the molar enthalpy (J/mol), s the molar entropy (J/(mol K)) and
# g = h − Ts the molar Gibbs energy (J/mol). The words in the setup matter:
# *closed* means no atoms enter or leave, *bulk* means the sample is large enough
# that surfaces do not matter.
#
# The numbers make physical sense. The LIQUID has the higher h, because melting
# breaks bonds and that costs energy (here 7000 − 1000 = 6000 J/mol, the heat of
# melting). The LIQUID also has the higher s, because its atoms are more disordered.
# Each g is a straight line in T: it starts at h when T = 0 and falls with slope
# −s. The LIQUID line starts higher but falls faster, so at some temperature the
# two lines cross. Below the crossing one phase has the lower g; above it, the
# other.
#
# **The Python.** `def g_solid(T):` defines a *function*: a named recipe that takes
# an input T and `return`s a result. The indented line is the body of the
# function. Calling `g_solid(900)` runs the recipe with T = 900.

# %%
def g_solid(T):
    return 1000.0 - 10.0 * T   # J/mol, T in K  (h = 1000 J/mol, s = 10 J/(mol K))

def g_liquid(T):
    return 7000.0 - 16.0 * T   # J/mol  (h = 7000 J/mol, s = 16 J/(mol K))

# Call both functions at 900 K and print the results with 0 decimals.
print(f"900 K: g_SOLID = {g_solid(900):.0f} J/mol, g_LIQUID = {g_liquid(900):.0f} J/mol")

# %% [markdown]
# **What to look at.** Both energies are negative, and the *lower* (more negative)
# one belongs to the phase that is stable at 900 K. A negative Gibbs energy is
# normal: only differences between Gibbs energies have a physical meaning.
#
# ### Your turn
#
# Fill the 1000 K and 1100 K rows, then solve 1000 − 10T = 7000 − 16T for the
# crossing temperature (K).
#
# To solve the equation, collect the T terms on one side and the numbers on the
# other. You may type the arithmetic itself as your answer.

# %%
g_solid_1000 = None   # J/mol
g_liquid_1100 = None  # J/mol
T_crossing = None     # K
check(g_solid_1000, "f1_gs_1000")
check(g_liquid_1100, "f1_gl_1100")
check(T_crossing, "f1_crossing")

# %% [markdown]
# ## 2. The same arithmetic as a code cell (W5)
#
# This is the Lesson 1 cell, unchanged. The constants 1000, 10, 7000 and 16 are
# the **model**; the temperatures are the **question** we ask it.
#
# Instead of calling a function once per temperature, the cell puts all five
# temperatures into one NumPy array and computes every row of the table at once.
#
# - `np.array([...])` turns a Python list of numbers into an array.
# - `1000.0 - 10.0 * temperatures` acts on each element: the result is again an
#   array of five numbers, one g_SOLID per temperature.
# - `np.minimum(solid, liquid)` compares the two arrays element by element and
#   keeps the smaller value at each position: the lowest Gibbs energy at each T.
# - `np.column_stack([...])` places the four arrays side by side as the columns of
#   a table, so the printout has one row per temperature: T, g_SOLID, g_LIQUID and
#   the lower of the two (all in J/mol).

# %%
import numpy as np

temperatures = np.array([800.0, 900.0, 1000.0, 1100.0, 1200.0])   # K, the question
solid = 1000.0 - 10.0 * temperatures       # J/mol, one value per temperature
liquid = 7000.0 - 16.0 * temperatures      # J/mol
lowest = np.minimum(solid, liquid)         # J/mol, the smaller of the two at each T
print(np.column_stack([temperatures, solid, liquid, lowest]))   # columns: T, SOLID, LIQUID, lowest

# %% [markdown]
# **What to look at.** Compare the last column with the two before it: in each row
# it equals one of them. The phase whose value it copies is the stable phase at
# that temperature. Watch where the choice switches from one column to the other.
#
# ### Your turn
#
# Predict both energies at 950 K on paper, then change the temperatures in the
# cell above to check. Enter your predictions here.
#
# (To change the temperatures, edit the numbers inside `np.array([...])` above,
# for example add `950.0` to the list, and run that cell again with Shift+Enter.)

# %%
g_solid_950 = None   # J/mol
g_liquid_950 = None  # J/mol
check(g_solid_950, "f1_gs_950")
check(g_liquid_950, "f1_gl_950")

# %% [markdown]
# ## 3. What may an optimiser change? (W6)
#
# Let f_L be the liquid fraction and f_S = 1 − f_L, both between 0 and 1. At fixed
# T and p the optimiser minimises
# $g_{mix} = (1 - f_L)\,g_S + f_L\,g_L$. It may change the fractions, never the model.
# The cell below shows the idea at 1100 K; your turn is at 900 K.
#
# **Where the formula comes from.** Our one mole of atoms may split into two
# portions: f_L mol in the LIQUID and f_S = 1 − f_L mol in the SOLID. Each portion
# contributes its amount times its molar Gibbs energy, so the total is the
# weighted average above. ("mix" here means a mixture of two phases side by side,
# not atoms mixed within one phase.) The two fractions must add up to 1 because no
# atoms are created or lost, and neither may be negative because a phase cannot
# hold a negative amount of atoms.
#
# Note the division of roles. The *model* (the lines g_S and g_L) is fixed input.
# The *fractions* are the only thing the optimiser is allowed to vary. An optimiser
# that changed the model to lower the energy would be answering a different
# question.
#
# **The Python.** `g_mix` calls the two functions from section 1. The expression
# `[g_mix(1100, f) for f in (0, 0.5, 1)]` is a *list comprehension*: it evaluates
# `g_mix(1100, f)` for f = 0, then 0.5, then 1, and collects the three results in a
# list.

# %%
def g_mix(T, f_liquid):
    return (1 - f_liquid) * g_solid(T) + f_liquid * g_liquid(T)   # J/mol, weighted by the phase fractions

print("f_L:", [0, 0.5, 1], "→ g_mix(1100 K) =", [g_mix(1100, f) for f in (0, 0.5, 1)], "J/mol")

# %% [markdown]
# **What to look at.** How does g_mix change as f_L goes from 0 to 0.5 to 1? Is the
# change steady (equal steps) or curved? Use that observation in your turn.
#
# ### Your turn
#
# What is g_mix at 900 K for f_L = 0.25? And which f_L minimises it?
# At f_L = −0.2 the formula gives a lower number; why must that be rejected?

# %%
g_mix_quarter = None  # J/mol
best_f_liquid = None
check(g_mix_quarter, "f1_gmix_025")
check(best_f_liquid, "f1_best_fl_900")

# %% [markdown]
# ## After your attempt: the optimiser and the plots
#
# The course code solves the same problem with SciPy's `linprog`: variables
# [f_S, f_L], objective [g_S, g_L], balance f_S + f_L = 1, bounds 0…1.
#
# **What `linprog` does.** SciPy is a package of scientific routines; `linprog`
# solves a *linear programme*: find the unknowns that make a weighted sum as small
# as possible, while some linear equations hold and each unknown stays within
# bounds. Here:
#
# - the unknowns are the fractions f_S and f_L;
# - the quantity to minimise is f_S g_S + f_L g_L, so the weights are the two
#   Gibbs energies at the chosen temperature;
# - the one equation is f_S + f_L = 1 (one mole of atoms in total);
# - the bounds are 0 ≤ f_S ≤ 1 and 0 ≤ f_L ≤ 1.
#
# The course function `unary.equilibrium_at(T)` sets this up and returns a
# *dictionary* (a lookup table of named entries): `result["GM"]` is the minimum
# molar Gibbs energy in J/mol, and `result["fractions"]` is another dictionary
# mapping each phase name to its fraction. `.items()` walks through its
# name/value pairs.
#
# The plotting part draws two panels side by side:
#
# - Left: the two Gibbs lines against T (divided by 1000 to show kJ/mol), with the
#   lower of the two drawn as a thick, faint line underneath.
# - Right: g_mix at 900 K against f_L, including values of f_L outside 0…1. The
#   line `inside = (f >= 0) & (f <= 1)` makes an array of True/False values, True
#   where f is allowed; `f[inside]` keeps only the allowed points and
#   `f[~inside]` (`~` means "not") the forbidden ones, which are drawn as crosses.

# %% cellView="form"
#@title After your attempt: run to check with the course code and plot
from course.foundations import one_component_manual as unary   # the course's plain-Python version of this model
import matplotlib.pyplot as plt

result = unary.equilibrium_at(900.0)   # dictionary with "GM" (J/mol) and "fractions"
print(f"900 K: GM = {result['GM']:.0f} J/mol, fractions",
      {phase: round(amount, 9) + 0.0 for phase, amount in result["fractions"].items()})  # + 0.0 shows −0 as 0
confirm(result["GM"], -8000.0, "Minimum at 900 K", tol=1e-6)
confirm(unary.transition_temperature(), 1000.0, "Crossing temperature", tol=1e-8)

T = np.linspace(800, 1200, 81)   # K, 81 temperatures in steps of 5 K
fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.6))   # 1 row, 2 panels
left.plot(T, g_solid(T) / 1000, "-", label="SOLID")           # / 1000: J/mol → kJ/mol
left.plot(T, g_liquid(T) / 1000, "--", label="LIQUID")
left.plot(T, np.minimum(g_solid(T), g_liquid(T)) / 1000, ":", lw=4, alpha=0.5, label="lower one")   # lw: line width, alpha: transparency
left.set(xlabel="T (K)", ylabel="g (kJ/mol)", title="Two Gibbs lines")
left.legend()
f = np.linspace(-0.3, 1.3, 33)       # trial liquid fractions, some outside 0…1 on purpose
inside = (f >= 0) & (f <= 1)         # True where the fraction is physically allowed
right.plot(f[inside], g_mix(900, f[inside]), "-", label="allowed 0 ≤ f_L ≤ 1")
right.plot(f[~inside], g_mix(900, f[~inside]), "x", label="not allowed")   # ~ flips True and False
right.set(xlabel="liquid fraction f_L", ylabel="g_mix (J/mol)", title="900 K: phase-fraction line")
right.legend()
plt.show()

# %% [markdown]
# **What to look at.** Left: the two lines cross at one temperature, and the faint
# "lower one" line follows SOLID on one side of it and LIQUID on the other. Right:
# g_mix is a straight line in f_L, so its lowest *allowed* point is at one end of
# the allowed range; the crosses beyond the ends would be lower still, but they
# need a negative amount of one phase.

# %% [markdown]
# ### At the crossing: does the solver's choice matter?
#
# At exactly 1000 K the two lines cross, so every split has the same energy
# (W6: a tie gives a segment). Two of SciPy's methods, the dual simplex
# (`"highs-ds"`) and the interior-point method (`"highs-ipm"`), may then return
# different fractions. The cell asks both and checks what still matters: the
# energy and the balance. Which fractions they return is something to look at,
# not to assume.

# %%
from scipy.optimize import linprog   # the linear-programme solver used by the course code

for method in ("highs-ds", "highs-ipm"):
    r = linprog([g_solid(1000), g_liquid(1000)], A_eq=[[1, 1]], b_eq=[1], bounds=[(0, 1), (0, 1)], method=method)
    print(f"{method:9s}: f_S = {r.x[0]:.3f}, f_L = {r.x[1]:.3f}, g_mix = {r.fun:.1f} J/mol")
    assert abs(r.fun - g_mix(1000, 0.5)) < 1e-9, "at the crossing every split must have the same energy"
    assert abs(r.x.sum() - 1) < 1e-12, "the fractions must add up to 1"

# %% [markdown]
# Both answers are right: any f_L between 0 and 1 gives the same g_mix at the
# crossing, so a solver may report either end or anything between. What a
# reader must check is the energy and the balance, never the particular split.
# The advanced steps read this same problem with many candidate states instead of
# two.

# %% [markdown]
# ## 4. Consolidate and catch an error (W8)
#
# At **1050 K**: compute both energies, decide which phase is lower and give the
# minimum energy. Then correct two fictional reports:
#
# - A: at 900 K, "g_S = −8 J/mol, g_L = −7.4 kJ/mol, so solid wins." Give the
#   correct g_S in J/mol.
# - B: at 900 K, "f_S = 0.8 and f_L = 0.4 satisfy the one-mole balance." Give the
#   reported sum f_S + f_L, and say whether the report satisfies the one-mole
#   balance (`True` or `False`).
#
# For the last answer type the Python word `True` or `False` (capital first
# letter, no quotes).

# %%
g_solid_1050 = None   # J/mol
g_liquid_1050 = None  # J/mol
minimum_1050 = None   # J/mol
g_solid_report_a = None    # the correct value in J/mol
sum_report_b = None        # f_S + f_L as reported
balanced_report_b = None   # True or False
check(g_solid_1050, "f1_gs_1050")
check(g_liquid_1050, "f1_gl_1050")
check(minimum_1050, "f1_min_1050")
check(g_solid_report_a, "f1_report_a")
check(sum_report_b, "f1_report_b_sum")
check(balanced_report_b, "f1_report_b_balanced")

# %% [markdown]
# ### More practice (self-study step 01)
#
# At 975 K, which phase is lower?

# %%
g_solid_975 = None   # J/mol
g_liquid_975 = None  # J/mol
check(g_solid_975, "f1_gs_975")
check(g_liquid_975, "f1_gl_975")

# %% [markdown]
# **Limits.** Invented lines with zero heat capacity, no pressure dependence and no
# interfaces; they predict nothing about a real element. At exactly 1000 K every
# balanced split has the same energy, so the fractions are not determined.
# Next: [f2 · the same model in pycalphad](f2_unary_pycalphad.ipynb).
