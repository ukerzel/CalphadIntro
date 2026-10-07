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

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
RELEASE = "v0.1.0"
import os, pathlib, subprocess, sys
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
        print("Installed the course's package versions. Colab now restarts this session;"
              " when it has reconnected, run this cell again (it will not install twice).")
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

# %%
def g_solid(T):
    return 1000.0 - 10.0 * T   # J/mol, T in K

def g_liquid(T):
    return 7000.0 - 16.0 * T   # J/mol

print(f"900 K: g_SOLID = {g_solid(900):.0f} J/mol, g_LIQUID = {g_liquid(900):.0f} J/mol")

# %% [markdown]
# ### Your turn
#
# Fill the 1000 K and 1100 K rows, then solve 1000 − 10T = 7000 − 16T for the
# crossing temperature (K).

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

# %%
import numpy as np

temperatures = np.array([800.0, 900.0, 1000.0, 1100.0, 1200.0])
solid = 1000.0 - 10.0 * temperatures
liquid = 7000.0 - 16.0 * temperatures
lowest = np.minimum(solid, liquid)
print(np.column_stack([temperatures, solid, liquid, lowest]))

# %% [markdown]
# ### Your turn
#
# Predict both energies at 950 K on paper, then change the temperatures in the
# cell above to check. Enter your predictions here.

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

# %%
def g_mix(T, f_liquid):
    return (1 - f_liquid) * g_solid(T) + f_liquid * g_liquid(T)

print("f_L:", [0, 0.5, 1], "→ g_mix(1100 K) =", [g_mix(1100, f) for f in (0, 0.5, 1)], "J/mol")

# %% [markdown]
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

# %% cellView="form"
#@title After your attempt: run to check with the course code and plot
from course.foundations import one_component_manual as unary
import matplotlib.pyplot as plt

result = unary.equilibrium_at(900.0)
print(f"900 K: GM = {result['GM']:.0f} J/mol, fractions",
      {phase: round(amount, 9) + 0.0 for phase, amount in result["fractions"].items()})  # + 0.0 shows −0 as 0
confirm(result["GM"], -8000.0, "Minimum at 900 K", tol=1e-6)
confirm(unary.transition_temperature(), 1000.0, "Crossing temperature", tol=1e-8)

T = np.linspace(800, 1200, 81)
fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.6))
left.plot(T, g_solid(T) / 1000, "-", label="SOLID")
left.plot(T, g_liquid(T) / 1000, "--", label="LIQUID")
left.plot(T, np.minimum(g_solid(T), g_liquid(T)) / 1000, ":", lw=4, alpha=0.5, label="lower one")
left.set(xlabel="T (K)", ylabel="g (kJ/mol)", title="Two Gibbs lines")
left.legend()
f = np.linspace(-0.3, 1.3, 33)
inside = (f >= 0) & (f <= 1)
right.plot(f[inside], g_mix(900, f[inside]), "-", label="allowed 0 ≤ f_L ≤ 1")
right.plot(f[~inside], g_mix(900, f[~inside]), "x", label="not allowed")
right.set(xlabel="liquid fraction f_L", ylabel="g_mix (J/mol)", title="900 K: phase-fraction line")
right.legend()
plt.show()

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
