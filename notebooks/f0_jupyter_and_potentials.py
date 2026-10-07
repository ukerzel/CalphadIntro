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
# # f0 · Jupyter and the thermodynamic potentials
#
# **Learning question:** which energy does a sample minimise, and how do U, H, F
# and G follow from each other?
#
# Used in: Day 1 W1–W3 (optional), Lesson 0, self-study step 00.
#
# **How to use a notebook.** A notebook is a list of cells. Text cells (like this
# one) explain; code cells run Python. Click a code cell and press **Shift+Enter**
# to run it and move on. Run the cells from top to bottom. If something gets
# muddled, use *Kernel → Restart* (Colab: *Runtime → Restart session*) and run
# from the top again.

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
# ## 1. Numbers with units
#
# Python does not know units, so we keep them in the variable names and comments.
# Pressure times volume is an energy: 1 Pa·m³ = 1 J.

# %%
U = 999.0        # internal energy, J
p = 100000.0     # pressure, Pa
V = 0.00001      # volume, m³
pV = p * V       # J
H = U + pV       # enthalpy, J
print(f"pV = {pV:.0f} J, H = {H:.0f} J")
confirm(H, 1000.0, "H = U + pV for the W1 worked state", tol=1e-9)

# %% [markdown]
# ### Your turn (W1)
#
# A sample receives 80 J of heat and does 10 J of work, so the work *on* the sample
# is −10 J. Find ΔU = q + w_on. Replace `None` with your value (in J) and run the cell.

# %%
delta_U = None  # J
check(delta_U, "f0_delta_u")

# %% [markdown]
# ## 2. Entropy (W2)
#
# Entropy S has units J/K. For a reversible heat transfer at constant absolute
# temperature, $\Delta S = q_{rev}/T$ (T in kelvin). A reversible 600 J input at
# 300 K gives ΔS = 2 J/K. Entropy is a state property, not a synonym for heat.

# %%
q_rev = 600.0      # reversible heat received, J
T_bath = 300.0     # K
delta_S = q_rev / T_bath   # J/K
print(f"ΔS = {delta_S:.0f} J/K")
confirm(delta_S, 2.0, "ΔS for the W2 worked transfer", tol=1e-12)

# %% [markdown]
# ### Your turn (W2)
#
# A reversible 900 J input at 300 K. What is ΔS (J/K)? What are the units of TS?

# %%
delta_S_try = None  # J/K
check(delta_S_try, "f0_delta_s")

# %% [markdown]
# ## 3. From U to G
#
# $F = U - TS$ and $G = H - TS = F + pV$. Take the worked state from W1 at
# $T = 300$ K with $S = 10$ J/K.

# %%
T, S = 300.0, 10.0   # K, J/K
TS = T * S           # J
F = U - TS
G = H - TS
print(f"TS = {TS:.0f} J, F = {F:.0f} J, G = {G:.0f} J, G − F = {G - F:.0f} J (= pV)")
confirm(G - F, pV, "G − F equals pV", tol=1e-9)

# %% [markdown]
# ### Your turn (W3, self-study step 00 "Try it")
#
# The state U = 1498 J, p = 100000 Pa, V = 0.00002 m³, T = 300 K, S = 4 J/K.
# Compute H, F and G in J. Write the formulas, not just the numbers.

# %%
H_try = None  # J
F_try = None  # J
G_try = None  # J
check(H_try, "f0_try_h")
check(F_try, "f0_try_f")
check(G_try, "f0_try_g")

# %% [markdown]
# ## 4. Which energy is minimised?
#
# For a simple bulk sample with fixed amounts of each component:
#
# | Held fixed | The equilibrium state minimises |
# |---|---|
# | U and V (isolated) | it maximises S instead |
# | T and V | F = U − TS |
# | T and p | G = H − TS |
# | T, p and the chemical potentials of the exchanged elements (open to a reservoir) | G − Σ μᵢnᵢ, the grand potential (step 04) |
#
# Everything in this course is at fixed T and p, so we compare Gibbs energies.

# %% [markdown]
# ## 5. A first plot
#
# How do the four energies of the "Try it" state change with temperature, if U,
# p, V and S stay fixed? (Only T changes in this sketch, to show which terms
# contain T; a real sample's U and S would change too.)

# %%
import matplotlib.pyplot as plt
import numpy as np

U2, p2, V2, S2 = 1498.0, 100000.0, 0.00002, 4.0
temperatures = np.linspace(0, 600, 61)
fig, ax = plt.subplots(figsize=(5.5, 3.4))
ax.plot(temperatures, np.full_like(temperatures, U2), "-", label="U")
ax.plot(temperatures, np.full_like(temperatures, U2 + p2 * V2), ":", label="H = U + pV")
ax.plot(temperatures, U2 - temperatures * S2, "--", label="F = U − TS")
ax.plot(temperatures, U2 + p2 * V2 - temperatures * S2, "-.", label="G = H − TS")
ax.set_xlabel("T (K)")
ax.set_ylabel("energy (J)")
ax.legend()
plt.show()

# %% cellView="form"
#@title After your attempt: run to see the numbers behind the plot
for t in (0, 300, 600):
    print(f"T = {t:3d} K: U = {U2:.0f}, H = {U2 + p2 * V2:.0f}, F = {U2 - t * S2:.0f}, G = {U2 + p2 * V2 - t * S2:.0f} J")

# %% [markdown]
# **Limits.** These are invented definition exercises, not data for a material.
# Next: [f1 · one component, two phases](f1_unary_by_hand_and_code.ipynb).
