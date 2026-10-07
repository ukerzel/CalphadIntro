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
# ## 1. Read the database before solving anything
#
# Each phase has one set of sites that A or B can occupy, so the site fraction of B
# is the B atom fraction x. Compare the lines with f3: ALPHA's pure-A and pure-B
# energies are 1000 − 10T and 13000 − 10T (−9000 and +3000 J/mol at 1000 K); BETA
# has them swapped. `L(ALPHA,A,B;0)` is the interaction Ω, set by the function
# `LZERO` (0 in the file; the regular solution of f4 uses 20000 J/mol). The ideal
# mixing term RT·q(x) is added by pycalphad's phase model; it is not in the file.

# %%
from pathlib import Path

TDB = Path("course/foundations/binary_family.tdb")
print(TDB.read_text())

# %% [markdown]
# ## 2. One phase at one composition: `calculate`
#
# `calculate` evaluates a phase at the compositions you give (`points` are site
# fractions [A, B]), stable or not. At 1000 K and x = 0.20 ALPHA should give the
# step 02 value.

# %%
import numpy as np
from pycalphad import Database, calculate, equilibrium, variables as v

database = Database(str(TDB))
point = calculate(database, ["A", "B"], "ALPHA", T=1000, P=100000, N=1,
                  points=np.array([[0.8, 0.2]]), output="GM", fake_points=False)
print("ALPHA at x = 0.20, 1000 K: GM =", float(point.GM.values.squeeze()), "J/mol")

# %% [markdown]
# ### Your turn
#
# Predict GM for **homogeneous** ALPHA at x = 0.5 and 1000 K with Ω = 0, in J/mol
# to 4 significant figures. Use R = 8.3145 J/(mol K). Then change `points` above
# to check.

# %%
alpha_half = None  # J/mol
check(alpha_half, "f5_alpha_half")

# %% [markdown]
# ## 3. Reading an equilibrium result
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
# Two ideal phases ALPHA and BETA at z = 0.5 and 1000 K (f4 part A):

# %%
result = equilibrium(database, ["A", "B"], ["ALPHA", "BETA"],
                     {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5})
print("dimensions:", dict(zip(result.Phase.dims, result.Phase.shape)))
print("GM    :", float(result.GM.values.squeeze()))
print("Phase :", result.Phase.values.squeeze())
print("NP    :", result.NP.values.squeeze())
print("X(B)  :", result.X.sel(component="B").values.squeeze())

# %% [markdown]
# ### Your turn
#
# Now allow **only ALPHA** but give it Ω = 20000 J/mol
# (`parameters={"LZERO": 20000}`), at the same T and z. Before running: how many
# used vertices will there be, and what phase name will they have?

# %%
used_vertices = None  # how many non-empty Phase entries
check(used_vertices, "f5_r1_vertices")

# %%
regular = equilibrium(database, ["A", "B"], ["ALPHA"],
                      {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5},
                      parameters={"LZERO": 20000})
for phase, amount, x in zip(regular.Phase.values.squeeze(), regular.NP.values.squeeze(),
                            regular.X.sel(component="B").values.squeeze()):
    if phase:
        print(f"{phase}: amount {amount:.4f}, x(B) = {x:.6f}")

# %% [markdown]
# Two rows with the same name ALPHA: one phase model, two compositions (the
# miscibility gap of f4). Storing results in a dictionary keyed by phase name would
# silently keep only one of them. The energy GM belongs to the whole sample: do not
# add it once per row.

# %% [markdown]
# ## 4. From one point to a scan to a small diagram
#
# Conditions can be arrays. One call scans temperature at z = 0.3; collecting the
# two compositions at each temperature draws the gap you built by hand in f4.

# %%
temperatures = np.arange(600.0, 1201.0, 50.0)
scan = equilibrium(database, ["A", "B"], ["ALPHA"],
                   {v.T: temperatures, v.P: 100000, v.N: 1, v.X("B"): 0.3},
                   parameters={"LZERO": 20000})
gap = []
print(" T (K)   phases and compositions x(B)")
for i, T in enumerate(temperatures):
    phases = scan.Phase.values[0, 0, i, 0]
    xs = scan.X.sel(component="B").values[0, 0, i, 0]
    used = [(str(p), float(x)) for p, x in zip(phases, xs) if p]
    print(f"{T:6.0f}   " + ", ".join(f"{p} {x:.4f}" for p, x in used))
    if len(used) == 2:
        gap.append((T, min(x for _, x in used), max(x for _, x in used)))

# %% [markdown]
# ### Your turn
#
# Above which temperature in this scan is z = 0.3 a single phase? (Give the lowest
# scanned temperature with one phase, in K.) Why is that below the critical
# temperature of about 1203 K, where the gap closes at x = 0.5?

# %%
first_single_phase = None  # K
check(first_single_phase, "f5_single_phase_t")

# %% [markdown]
# ## After your attempt: pycalphad against the plain model, and three wrong problems

# %% cellView="form"
#@title After your attempt: run to compare and plot
import matplotlib.pyplot as plt
from course.foundations import binary_family as plain
from course.foundations.binary_family_tools import binary_equilibrium, homogeneous_properties

confirm(float(point.GM.values.squeeze()), -10760.595951, "ALPHA at x = 0.20 (step 02)", tol=1e-6)
confirm(float(result.GM.values.squeeze()), -10762.730017, "Two-phase minimum at z = 0.5 (step 03)", tol=1e-5)
xs = sorted(float(x) for p, x in zip(regular.Phase.values.squeeze(), regular.X.sel(component="B").values.squeeze()) if p)
reference = plain.regular_binodal(1000.0)["compositions"]
confirm(xs[0], reference[0], "Gap composition at 1000 K, pycalphad vs plain model", tol=1e-6)

print("Three ways to answer a different question (Lesson 8.4):")
with_beta = binary_equilibrium(1000.0, 0.5, "I2")["GM"]
alpha_only = equilibrium(database, ["A", "B"], ["ALPHA"], {v.T: 1000, v.P: 100000, v.N: 1, v.X("B"): 0.5})
print(f"  BETA left out: {float(alpha_only.GM.values.squeeze()):.6f} J/mol instead of {with_beta:.6f}")
confirm(float(alpha_only.GM.values.squeeze()), -8763.172233, "ALPHA-only result (a different question)", tol=1e-5)
with_omega = float(homogeneous_properties(1000.0, 0.5, "ALPHA", 20000.0)["GM"])
without_omega = float(homogeneous_properties(1000.0, 0.5, "ALPHA", 0.0)["GM"])
print(f"  Ω forgotten: homogeneous GM {without_omega:.6f} instead of {with_omega:.6f} (lower by {with_omega - without_omega:.0f} J/mol)")
confirm(with_omega - without_omega, 5000.0, "Ω·x(1−x) at x = 0.5", tol=1e-6)
print("  Enthalpy of the equilibrium split is not the homogeneous enthalpy: equilibrium minimises G, not H.")

T_fine = np.linspace(600, 1190, 60)
pairs = [plain.regular_binodal(T)["compositions"] for T in T_fine]
fig, ax = plt.subplots(figsize=(5.5, 3.8))
ax.plot([p[0] for p in pairs], T_fine, "-", color="0.4", label="plain model (f4)")
ax.plot([p[1] for p in pairs], T_fine, "-", color="0.4")
ax.plot([g[1] for g in gap], [g[0] for g in gap], "o", label="pycalphad, z = 0.3")
ax.plot([g[2] for g in gap], [g[0] for g in gap], "s")
ax.axvline(0.3, ls=":", color="0.5")
ax.set(xlabel="x(B)", ylabel="T (K)", title="Miscibility gap: pycalphad on the f4 model")
ax.legend()
plt.show()

# %% [markdown]
# **Limits.** The same invented model as f3/f4; agreement shows pycalphad reads it
# as intended, not that it describes a real alloy. The equilibrium search samples
# trial compositions and refines them (the `pdens` setting you will meet in Task 01).
# Next: [Task 01 · Cu–Ni equilibria](task01_cuni_equilibria.ipynb).
