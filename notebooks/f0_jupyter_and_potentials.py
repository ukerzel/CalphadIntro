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
#
# **What you will do here.** You will meet the four energies that thermodynamics
# uses: the internal energy U, the enthalpy H, the Helmholtz energy F and the
# Gibbs energy G. Each is calculated once in code, and then you calculate one
# yourself. At the end you will know why every later notebook compares Gibbs
# energies. No Python knowledge is assumed; each new piece of Python is explained
# the first time it appears.
#
# The first code cell below prepares the notebook. You do not need to read it:
# it finds the course files, (in Colab) installs the course's package versions,
# and prints the versions it is using.

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
# **What the setup cell printed.** One line per package with its version number.
# If a line ends with "← locked run used …", your computer has a different version
# from the one the course was tested with; the notebook usually still works, but
# mention it if a later number disagrees.
#
# The setup cell also made two small helper functions available, which you will
# see in almost every cell:
#
# - `check(your_value, key)` (key: the name of the stored answer, in quotes) compares *your* answer with a stored answer
#   without showing it. It prints "not attempted" while your value is still
#   `None`, "✓ matches" when you are right, and a hint when you are not.
# - `confirm(value, expected, "what", tol=...)` is used in the worked cells. It
#   makes sure the code reproduces the number given in the lesson, to within the
#   tolerance `tol`, and prints a ✓ line. If it ever stops with an error, the
#   calculation and the lesson disagree; check the package versions first.

# %% [markdown]
# ## 1. Numbers with units
#
# Python does not know units, so we keep them in the variable names and comments.
# Pressure times volume is an energy: 1 Pa·m³ = 1 J.
#
# **The physics.** The *internal energy* U is all the energy stored inside the
# sample: the motion of its atoms and the energy of the bonds between them. A
# sample also takes up space: at pressure p, making room for a volume V means
# pushing the surroundings back, which costs the work pV. The *enthalpy* adds that
# work to U:
#
# $$H = U + pV.$$
#
# Units: a pascal is a force per area, 1 Pa = 1 N/m², so Pa·m³ = N·m = J. For a
# solid or liquid at normal pressure the pV term is tiny compared with U (here
# 1 J out of 1000 J), which is why H and U are often almost equal for condensed
# matter.
#
# **The Python.** `U = 999.0` is an *assignment*: it stores the number 999.0
# under the name `U`. Writing `999.0` (with a decimal point) makes it a
# floating-point number. `*` multiplies, `+` adds. Everything after `#` on a line
# is a comment, ignored by Python; we use comments to note units.
# `print(f"...")` prints an *f-string*: the text between the quotes is printed
# as it is, except that `{pV:.0f}` is replaced by the value of `pV`, written with
# 0 digits after the decimal point (`.2f` would give two digits).

# %%
U = 999.0        # internal energy, J
p = 100000.0     # pressure, Pa
V = 0.00001      # volume, m³
pV = p * V       # J  (Pa · m³ = N/m² · m³ = N·m = J)
H = U + pV       # enthalpy, J
print(f"pV = {pV:.0f} J, H = {H:.0f} J")   # the f-string fills in the values, rounded to whole J
confirm(H, 1000.0, "H = U + pV for the W1 worked state", tol=1e-9)   # stops with an error if H is not 1000 J

# %% [markdown]
# ### Your turn (W1)
#
# A sample receives 80 J of heat and does 10 J of work, so the work *on* the sample
# is −10 J. Find ΔU = q + w_on. Replace `None` with your value (in J) and run the cell.
#
# **Sign convention.** This is the first law of thermodynamics: the internal energy
# changes by the heat q that flows *into* the sample plus the work w_on done *on*
# the sample. Energy that enters the sample counts as positive, energy that leaves
# counts as negative. When the sample pushes on its surroundings it *does* work,
# so the work done *on* it is negative.
#
# You may type a number, or the arithmetic itself (for example `3 + 4`): Python
# evaluates it before `check` compares it. `None` is Python's word for "no value
# yet".

# %%
delta_U = None  # J
check(delta_U, "f0_delta_u")   # compares with the stored answer; prints a hint if it differs

# %% [markdown]
# ## 2. Entropy (W2)
#
# Entropy S has units J/K. For a reversible heat transfer at constant absolute
# temperature, $\Delta S = q_{rev}/T$ (T in kelvin). A reversible 600 J input at
# 300 K gives ΔS = 2 J/K. Entropy is a state property, not a synonym for heat.
#
# **What the symbols mean.** $q_{rev}$ is heat delivered *reversibly*, that is so
# slowly and gently that the sample stays in equilibrium the whole time. T must be
# the *absolute* temperature in kelvin (T/K = θ/°C + 273.15): dividing by a Celsius
# temperature would give nonsense, and at 0 °C would even divide by zero. Entropy
# measures how many microscopic arrangements are compatible with what we see
# from outside; adding heat lets the atoms explore more of them. The same amount of
# heat raises the entropy more at a low temperature than at a high one, which is
# why T is in the denominator. In Python, `/` divides.

# %%
q_rev = 600.0      # reversible heat received, J
T_bath = 300.0     # K
delta_S = q_rev / T_bath   # J/K  (J divided by K)
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
#
# **Why subtract TS?** F (the *Helmholtz energy*) and G (the *Gibbs energy*) are the
# energies that matter when the sample sits in surroundings at a fixed temperature.
# The product TS has units K · J/K = J, so it can be subtracted from an energy. At a
# high temperature the −TS term is large, so states with much entropy (much
# disorder) become favourable; at a low temperature the energy term U or H
# dominates. The second equality follows by substitution:
# $G = H - TS = (U + pV) - TS = (U - TS) + pV = F + pV$.
#
# **The Python.** `T, S = 300.0, 10.0` assigns two values at once: the first goes to
# `T`, the second to `S`. The cell reuses `U`, `H` and `pV` from section 1, because
# a notebook remembers every variable from cells you have already run.

# %%
T, S = 300.0, 10.0   # K, J/K
TS = T * S           # J
F = U - TS           # Helmholtz energy, J
G = H - TS           # Gibbs energy, J
print(f"TS = {TS:.0f} J, F = {F:.0f} J, G = {G:.0f} J, G − F = {G - F:.0f} J (= pV)")
confirm(G - F, pV, "G − F equals pV", tol=1e-9)   # G − F must be exactly the pV of section 1

# %% [markdown]
# ### Your turn (W3, self-study step 00 "Try it")
#
# The state U = 1498 J, p = 100000 Pa, V = 0.00002 m³, T = 300 K, S = 4 J/K.
# Compute H, F and G in J. Write the formulas, not just the numbers.
#
# Tip: you can type each formula with the given numbers put in, for example
# `a * b + c` with numbers in place of the letters; Python does the arithmetic.
# The worked cell in section 3 shows which formula belongs to which energy.

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
# | T, p and the chemical potentials of the exchanged elements (open to a reservoir) | G − Σ μᵢnᵢ, summed over the exchanged elements only: a grand potential (step 04) |
#
# Everything in this course is at fixed T and p, so we compare Gibbs energies.
#
# **Why G at fixed T and p?** The basic law is the second law: the total entropy of
# the sample *plus* its surroundings cannot decrease. At constant pressure, heat
# q = ΔH flows from the surroundings into the sample when the sample's enthalpy
# changes by ΔH. The surroundings (a large bath at temperature T) lose that heat,
# so their entropy changes by −ΔH/T. The total change is
#
# $$\Delta S_{total} = \Delta S - \frac{\Delta H}{T} = -\frac{\Delta H - T\Delta S}{T} = -\frac{\Delta G}{T}.$$
#
# "Total entropy rises" is therefore the same statement as "the sample's G falls".
# A sample at fixed T and p keeps changing until G cannot go lower: that lowest-G
# state is the equilibrium. A CALPHAD program does exactly this search.

# %% [markdown]
# ## 5. A first plot
#
# How do the four energies of the "Try it" state change with temperature, if U,
# p, V and S stay fixed? (Only T changes in this sketch, to show which terms
# contain T; a real sample's U and S would change too.)
#
# **New Python in this cell.**
#
# - `import numpy as np` loads NumPy, the package for arrays of numbers, under the
#   short name `np`; `import matplotlib.pyplot as plt` loads the plotting package
#   as `plt`. Every notebook starts its calculations with lines like these.
# - `np.linspace(0, 600, 61)` makes an *array* of 61 evenly spaced numbers from 0
#   to 600, both ends included: 0, 10, 20, …, 600 K.
# - Arithmetic with an array acts on every element at once ("vectorised"):
#   `U2 - temperatures * S2` gives an array of 61 values of F, one per temperature,
#   without writing a loop.
# - `np.full_like(temperatures, U2)` makes an array of the same length filled
#   with the constant U2, so a constant can be plotted against T.
# - `plt.subplots(...)` creates a figure `fig` with one set of axes `ax`;
#   `figsize` is its size in inches. `ax.plot(x, y, style, label=...)` draws one
#   line; the style string `"-"`, `":"`, `"--"` or `"-."` gives a solid, dotted,
#   dashed or dash-dotted line. `ax.legend()` lists the labels, `plt.show()`
#   displays the figure.
#
# **What to look at.** U and H are horizontal lines, since neither contains T. F and
# G fall with slope −S. G stays above F by the constant pV (only 2 J here, so the
# two lines nearly overlap at this scale).

# %%
import matplotlib.pyplot as plt
import numpy as np

U2, p2, V2, S2 = 1498.0, 100000.0, 0.00002, 4.0   # J, Pa, m³, J/K: the "Try it" state
temperatures = np.linspace(0, 600, 61)            # K, 61 values 0, 10, ..., 600
fig, ax = plt.subplots(figsize=(5.5, 3.4))        # one figure with one set of axes (size in inches)
ax.plot(temperatures, np.full_like(temperatures, U2), "-", label="U")   # constant: U has no T in it
ax.plot(temperatures, np.full_like(temperatures, U2 + p2 * V2), ":", label="H = U + pV")
ax.plot(temperatures, U2 - temperatures * S2, "--", label="F = U − TS")   # one value per temperature
ax.plot(temperatures, U2 + p2 * V2 - temperatures * S2, "-.", label="G = H − TS")
ax.set_xlabel("T (K)")
ax.set_ylabel("energy (J)")
ax.legend()      # box naming each line
plt.show()

# %% [markdown]
# The next cell prints the numbers behind three points of the plot. Its code is
# hidden in Colab (a "form" cell); double-click it to see the code.
# `for t in (0, 300, 600):` is a *loop*: the indented line below it runs three
# times, with `t` set to 0, then 300, then 600. `{t:3d}` prints the whole number
# t three characters wide, so the columns line up.

# %% cellView="form"
#@title After your attempt: run to see the numbers behind the plot
for t in (0, 300, 600):   # t in K
    print(f"T = {t:3d} K: U = {U2:.0f}, H = {U2 + p2 * V2:.0f}, F = {U2 - t * S2:.0f}, G = {U2 + p2 * V2 - t * S2:.0f} J")

# %% [markdown]
# **Limits.** These are invented definition exercises, not data for a material.
# Next: [f1 · one component, two phases](f1_unary_by_hand_and_code.ipynb).
