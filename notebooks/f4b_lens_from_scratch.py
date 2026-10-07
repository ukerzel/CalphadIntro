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
# # f4b · One phase diagram from scratch, then with pycalphad
#
# **Learning question:** what does a CALPHAD program actually do when it
# "calculates an equilibrium"? We find out by doing every step ourselves for one
# small problem, with nothing but numpy and SciPy, and then let pycalphad solve
# the same problem and compare the numbers.
#
# **The problem.** Two invented components, A and B, can each be SOLID or LIQUID.
# In both phases A and B mix freely (an *ideal solution*). We ask:
#
# 1. At 1400 K, for a sample with overall B atom fraction z = 0.40: is it solid,
#    liquid, or a mixture of both? If a mixture: which compositions, and how much
#    of each?
# 2. Repeating that at many temperatures: what does the phase diagram look like?
#
# **The route.** Each section adds one idea, and every line of code is visible:
#
# | Section | What we do | Tool |
# |---|---|---|
# | 1 | Gibbs energy of the pure components | plain Python |
# | 2 | Gibbs energy of each phase as a function of composition | numpy |
# | 3 | Try every possible split of the sample into SOLID + LIQUID | numpy (brute force) |
# | 4 | The condition for the best split: equal chemical potentials | `scipy.optimize.fsolve` |
# | 5 | How CALPHAD programs search: a grid and a linear programme | `scipy.optimize.linprog` |
# | 6 | Repeat at many temperatures: the phase diagram | numpy loop |
# | 7 | The same model as a database, solved by pycalphad | pycalphad |
# | 8 | Compare: what pycalphad did for us | — |
#
# **Before you start.** You need the idea that a system at fixed temperature and
# pressure ends up in the state of lowest Gibbs energy (f0 and f1 introduce it).
# Everything else is explained here. f4 meets the same melting lens in its part C;
# this notebook builds it up one step at a time and then hands it to pycalphad.
#
# **How to work.** Run the cells from top to bottom. In each "Your turn" cell,
# work the answer out (on paper or with code in the cell), replace `None` with
# your value and run the cell: it tells you whether you match, without showing the
# answer.

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
# ## 0. Tools and units
#
# We use three libraries:
#
# - **numpy** (`np`): arrays of numbers and fast arithmetic on whole arrays at once.
#   `np.log(x)` works on a single number or on an array of a thousand numbers.
# - **SciPy** (`scipy.optimize`): ready-made solvers. We use two of them: one that
#   solves equations (`fsolve`) and one that minimises a linear function under
#   constraints (`linprog`).
# - **matplotlib** (`plt`): plots.
#
# Units throughout: temperature T in K, energies in J per mole of atoms (J/mol),
# entropies in J/(mol K), compositions as B atom fractions between 0 and 1. The
# gas constant is R = 8.3145 J/(mol K), the value pycalphad uses, so that our
# numbers and pycalphad's can agree to many digits in section 7.

# %%
import numpy as np                      # arrays and maths on arrays
import matplotlib.pyplot as plt         # plotting
from scipy.optimize import fsolve, linprog   # an equation solver and a linear-programme solver

R = 8.3145   # gas constant, J/(mol K)

# %% [markdown]
# ## 1. The pure components
#
# For a pure component in one phase we use the simplest possible model: a
# constant enthalpy h and a constant entropy s, so its molar Gibbs energy is a
# straight line in T:
#
# $$g^\circ(T) = h - T\,s .$$
#
# | Component | SOLID: h (J/mol), s (J/(mol K)) | LIQUID: h, s |
# |---|---|---|
# | A | 1000, 10 | 7000, 16 |
# | B | 2000, 10 | 20000, 20 |
#
# The liquid has the higher enthalpy (melting needs heat) and the higher entropy
# (the liquid is more disordered). At low T the −Ts term is small, so the lower h
# wins: SOLID. At high T the −Ts term dominates, so the higher s wins: LIQUID. The
# melting temperature is where the two lines cross.
#
# Below we store the numbers in two nested dictionaries: `H["B"]["LIQUID"]` reads
# "the enthalpy of B in the LIQUID phase". The function `g0` then evaluates
# h − Ts for any component, phase and temperature.

# %%
H = {"A": {"SOLID": 1000.0, "LIQUID": 7000.0},     # J/mol
     "B": {"SOLID": 2000.0, "LIQUID": 20000.0}}
S = {"A": {"SOLID": 10.0, "LIQUID": 16.0},          # J/(mol K)
     "B": {"SOLID": 10.0, "LIQUID": 20.0}}

def g0(component, phase, T):
    """Molar Gibbs energy of a pure component in one phase, J/mol."""
    return H[component][phase] - T * S[component][phase]

# Try it: pure A at 1000 K in both phases.
print("A at 1000 K: SOLID", g0("A", "SOLID", 1000.0), "J/mol, LIQUID", g0("A", "LIQUID", 1000.0), "J/mol")

# %% [markdown]
# Both values are −9000 J/mol: at 1000 K solid and liquid A have the same Gibbs
# energy, so **A melts at 1000 K**. In general the lines cross where
# h_S − T s_S = h_L − T s_L, that is at
#
# $$T_m = \frac{h_L - h_S}{s_L - s_S}.$$
#
# ### Your turn: the melting temperature of B
#
# Use the table above. Give T_m of pure B in K.

# %%
T_melt_B = None   # K
check(T_melt_B, "f4b_tm_B")

# %% [markdown]
# So B melts higher than A. Between the two melting temperatures we expect
# something in between: alloys that are partly solid and partly liquid.

# %% [markdown]
# ## 2. One phase, any composition
#
# Now mix the two components in one phase. Take one mole of atoms with B atom
# fraction x (so 1 − x mol of A and x mol of B). For an **ideal solution** the
# Gibbs energy per mole of atoms has two parts:
#
# $$g_\varphi(x, T) = \underbrace{(1-x)\,g^\circ_{A,\varphi}(T) + x\,g^\circ_{B,\varphi}(T)}_{\text{weighted average of the pure components}} \;+\; \underbrace{R T\,[\,x\ln x + (1-x)\ln(1-x)\,]}_{\text{ideal mixing}} .$$
#
# - The first part is a straight line between pure A (x = 0) and pure B (x = 1):
#   just the two unmixed components side by side.
# - The second part comes from the configurational entropy of placing A and B
#   atoms randomly: $-T\,\Delta s_{\rm mix}$ with
#   $\Delta s_{\rm mix} = -R\,[x\ln x + (1-x)\ln(1-x)]$. Because ln of a number
#   between 0 and 1 is negative, this part is always ≤ 0: mixing lowers g. It is
#   zero at the pure ends and most negative at x = 0.5.
# - "Ideal" means there is no extra energy for A–B neighbours compared with A–A
#   and B–B (no interaction term). f4 part B adds such a term (the regular
#   solution, with interaction parameter Ω).
#
# φ stands for either phase: SOLID or LIQUID use the same formula with their own
# g° values.
#
# In code, `g_phase` takes x as a single number **or** a numpy array; numpy
# applies the formula to every element of the array. The formula needs
# 0 < x < 1 because ln 0 is undefined (the mixing term goes to 0 at the ends, but
# the computer cannot evaluate 0 · ln 0 directly), so we keep x away from the ends.
#
# The cell also makes `x_grid`, an array of 999 compositions that later sections
# reuse. In "Your turn" cells, use new names for your own values (as the cells
# suggest), so that `x_grid`, `T`, `z` and the other results stay as they are.

# %%
def g_phase(phase, x, T):
    """Molar Gibbs energy of an ideal A–B solution in `phase`, J/mol of atoms. Needs 0 < x < 1."""
    pure = (1 - x) * g0("A", phase, T) + x * g0("B", phase, T)   # straight line between the pure ends
    mixing = R * T * (x * np.log(x) + (1 - x) * np.log(1 - x))  # ideal mixing, always ≤ 0
    return pure + mixing

T = 1400.0   # K, the temperature of our question
x_grid = np.linspace(0.001, 0.999, 999)   # 999 compositions from 0.001 to 0.999, spacing 0.001

plt.figure(figsize=(7, 4.2))
plt.plot(x_grid, g_phase("SOLID", x_grid, T) / 1000, label="SOLID")       # / 1000: plot in kJ/mol
plt.plot(x_grid, g_phase("LIQUID", x_grid, T) / 1000, "--", label="LIQUID")
plt.xlabel("B atom fraction x")
plt.ylabel("g (kJ/mol of atoms)")
plt.title(f"Both phases at {T:.0f} K")
plt.legend()
plt.show()

# %% [markdown]
# **Reading the plot.** At 1400 K pure A is above its melting point, so on the
# left (A-rich) the LIQUID curve is lower. Pure B is below its melting point, so
# on the right (B-rich) the SOLID curve is lower. The curves cross somewhere in
# between. A sample that is A-rich enough is liquid, one that is B-rich enough is
# solid. What happens in between is the subject of the next two sections.
#
# ### Your turn: one point on each curve
#
# Our sample has z = 0.40. Compute g of **homogeneous** SOLID and of homogeneous
# LIQUID at x = 0.40 and 1400 K (J/mol, four significant figures). You may type
# the arithmetic by hand or call `g_phase`. Which phase is lower on its own?

# %%
g_solid_040 = None    # J/mol
g_liquid_040 = None   # J/mol
check(g_solid_040, "f4b_g_solid_040")
check(g_liquid_040, "f4b_g_liquid_040")

# %% [markdown]
# ## 3. Splitting the sample: try every possibility
#
# A sample does not have to be one phase. It may split into a SOLID region with
# composition $x_S$ and a LIQUID region with composition $x_L$. Two bookkeeping
# rules fix how much of each forms. With $f_S$ and $f_L$ the mole fractions of
# atoms in each region:
#
# $$f_S + f_L = 1 \quad\text{(all atoms are somewhere)},\qquad f_S\,x_S + f_L\,x_L = z \quad\text{(all B atoms are somewhere)}.$$
#
# Solving these two equations gives the **lever rule**:
#
# $$f_L = \frac{z - x_S}{x_L - x_S},\qquad f_S = 1 - f_L .$$
#
# A split is physically possible only if both amounts lie between 0 and 1, which
# happens when z lies between $x_S$ and $x_L$. The Gibbs energy of the split
# sample is the amount-weighted sum of the two regions:
#
# $$G_{\rm split} = f_S\,g_S(x_S) + f_L\,g_L(x_L).$$
#
# The equilibrium state is the one with the lowest G. The most direct way to find
# it: **try every pair** $(x_S, x_L)$ on a grid, keep the possible ones, and pick
# the lowest. With 999 trial compositions per phase that is about a million pairs,
# which numpy handles in a second.
#
# Two numpy tools do the work:
#
# - `np.meshgrid(a, b, indexing="ij")` makes two 2-D arrays so that element
#   `[i, j]` holds `a[i]` and `b[j]`: every combination of a SOLID and a LIQUID
#   composition.
# - `np.where(condition, value, other)` picks `value` where the condition holds
#   and `other` elsewhere; we give impossible splits the energy +∞ so they never
#   win. `np.argmin` then finds the position of the smallest value.

# %%
def lever_liquid(z, x_solid, x_liquid):
    """Amount fraction of LIQUID from the lever rule (atoms in LIQUID / all atoms)."""
    return (z - x_solid) / (x_liquid - x_solid)

z = 0.40   # overall B atom fraction of the sample

XS, XL = np.meshgrid(x_grid, x_grid, indexing="ij")   # XS[i, j] = x_grid[i] (SOLID), XL[i, j] = x_grid[j] (LIQUID)
with np.errstate(divide="ignore", invalid="ignore"):   # x_S = x_L divides by 0; those pairs are dropped
    fL = lever_liquid(z, XS, XL)
    possible = (XS != XL) & (fL >= 0) & (fL <= 1)    # both amounts between 0 and 1
    G_split = np.where(possible, (1 - fL) * g_phase("SOLID", XS, T) + fL * g_phase("LIQUID", XL, T), np.inf)

i, j = np.unravel_index(np.argmin(G_split), G_split.shape)   # argmin counts through the table as one long list;
                                                             # unravel_index turns that count into (row, column)
print(f"best pair on the grid: x_S = {x_grid[i]:.3f}, x_L = {x_grid[j]:.3f}, f_L = {fL[i, j]:.4f}")
print(f"G of the best split:     {G_split[i, j]:.3f} J/mol")
print(f"homogeneous SOLID:       {g_phase('SOLID', z, T):.3f} J/mol")
print(f"homogeneous LIQUID:      {g_phase('LIQUID', z, T):.3f} J/mol")

# %% [markdown]
# **Reading the output.** The split into a B-rich SOLID and an A-rich LIQUID is
# lower than either phase alone, so at 1400 K our z = 0.40 sample is partly solid
# and partly liquid. The brute-force answer is only as fine as the grid (here
# 0.001 in x).
#
# ### Your turn: how much lower?
#
# By how many J/mol is the best split lower than the better of the two homogeneous
# phases? Give a positive number (four significant figures are enough; the grid
# answer is close enough).

# %%
split_lower_by = None   # J/mol, positive
check(split_lower_by, "f4b_split_lower_by")

# %% [markdown]
# ## 4. The condition for the best split: equal chemical potentials
#
# Brute force works for one temperature and two phases, but real programs need
# something sharper. Draw the straight line through the two points
# $(x_S, g_S(x_S))$ and $(x_L, g_L(x_L))$: $G_{\rm split}$ is the height of that
# line at x = z. The lowest such line is the one that just touches both curves
# from below, the **common tangent**. At the touching points the two curves have
# the same slope, and the tangent line meets x = 0 and x = 1 at the same heights
# for both phases.
#
# The heights of a tangent at x = 0 and x = 1 are the **chemical potentials**
# μ_A and μ_B. For any curve g(x):
#
# $$\mu_A = g - x\,\frac{dg}{dx},\qquad \mu_B = g + (1-x)\,\frac{dg}{dx}.$$
#
# So the equilibrium condition is two equations in two unknowns:
#
# $$\mu_{A}^{\rm SOLID}(x_S) = \mu_{A}^{\rm LIQUID}(x_L),\qquad \mu_{B}^{\rm SOLID}(x_S) = \mu_{B}^{\rm LIQUID}(x_L).$$
#
# For our ideal solutions the derivative is easy and the result is short (try it
# on paper: differentiate g_phase and insert):
#
# $$\mu_{A}^{\varphi} = g^\circ_{A,\varphi} + RT\ln(1-x),\qquad \mu_{B}^{\varphi} = g^\circ_{B,\varphi} + RT\ln x .$$
#
# First we check this formula against a numerical slope of g, so we don't have to
# take it on trust. `np.gradient(g, x)` estimates dg/dx at every grid point from
# the neighbouring points.

# %%
def mu_phase(phase, x, T):
    """(mu_A, mu_B) of an ideal solution in `phase` at B atom fraction x, J/mol."""
    mu_A = g0("A", phase, T) + R * T * np.log(1 - x)
    mu_B = g0("B", phase, T) + R * T * np.log(x)
    return mu_A, mu_B

g_S = g_phase("SOLID", x_grid, T)
slope = np.gradient(g_S, x_grid)                 # numerical dg/dx, J/mol per unit x
mu_A_numeric = g_S - x_grid * slope          # tangent height at x = 0
mu_B_numeric = g_S + (1 - x_grid) * slope    # tangent height at x = 1
mu_A_formula, mu_B_formula = mu_phase("SOLID", x_grid, T)
k = 400                                     # look at one grid point, x = 0.401
print(f"x = {x_grid[k]:.3f}: mu_A numeric {mu_A_numeric[k]:.2f}, formula {mu_A_formula[k]:.2f} J/mol")
print(f"          mu_B numeric {mu_B_numeric[k]:.2f}, formula {mu_B_formula[k]:.2f} J/mol")

# %% [markdown]
# The numerical slope and the formula agree to a small fraction of a J/mol (the
# difference comes from estimating the slope from neighbouring points).
#
# **Solving the two equations.** `fsolve(f, guess)` looks for the values that make
# every entry of `f(...)` zero. We write a function that takes the two unknowns
# `[x_S, x_L]` and returns the two differences μ(SOLID) − μ(LIQUID). Like most
# equation solvers, `fsolve` starts from a guess and improves it step by step, so
# it needs a reasonable starting point: we use the brute-force pair from section 3.

# %%
def mu_difference(unknowns, T):
    """The two equilibrium conditions; both entries are 0 at the common tangent."""
    x_S, x_L = unknowns
    mu_A_S, mu_B_S = mu_phase("SOLID", x_S, T)
    mu_A_L, mu_B_L = mu_phase("LIQUID", x_L, T)
    return [mu_A_S - mu_A_L, mu_B_S - mu_B_L]

guess = [x_grid[i], x_grid[j]]               # start from the brute-force answer
x_S, x_L = fsolve(mu_difference, guess, args=(T,))   # args passes T on to mu_difference
f_L = lever_liquid(z, x_S, x_L)
f_S = 1 - f_L
G_best = f_S * g_phase("SOLID", x_S, T) + f_L * g_phase("LIQUID", x_L, T)

print(f"x_S = {x_S:.6f}, x_L = {x_L:.6f}")
residual = mu_difference([x_S, x_L], T)
print(f"remaining mu differences: {residual[0]:.1e}, {residual[1]:.1e} J/mol")
print(f"f_S = {f_S:.6f}, f_L = {f_L:.6f}, G = {G_best:.4f} J/mol")
print("checks: f_S + f_L =", f_S + f_L, "| B balance f_S x_S + f_L x_L =", f_S * x_S + f_L * x_L)

# %% [markdown]
# The remaining differences are tiny (well below 1e-6 J/mol): the equations are
# solved. The two balance checks give back 1 and z = 0.40, and G is slightly lower
# than the best brute-force pair because x_S and x_L are no longer limited to the
# grid.
#
# The touching points are called the **solidus** composition (x_S, the solid that
# can coexist with liquid) and the **liquidus** composition (x_L).
#
# ### Your turn: the amounts
#
# What fraction of the atoms is in the LIQUID at 1400 K? Then find out what happens
# at 1600 K. Solve again at 1600 K, using new variable names so the 1400 K values
# stay as they are:
# `x_S_1600, x_L_1600 = fsolve(mu_difference, [x_S, x_L], args=(1600.0,))`.
# Compute `f_L_1600 = lever_liquid(z, x_S_1600, x_L_1600)` and decide which phase the z = 0.40 sample is at
# 1600 K: `"SOLID"`, `"LIQUID"` or `"both"`. (Hint: what does an amount below 0 or
# above 1 tell you?)

# %%
liquid_fraction_1400 = None   # between 0 and 1
phase_at_1600 = None          # "SOLID", "LIQUID" or "both"
check(liquid_fraction_1400, "f4b_f_liquid_1400")
check(phase_at_1600, "f4b_phase_1600")

# %% [markdown]
# ## 5. How CALPHAD programs search: a grid and a linear programme
#
# Section 4 needed a good starting guess, and it assumed we already knew that the
# answer is SOLID + LIQUID. A program for real alloys cannot assume either: there
# may be ten phases, and a bad guess can lead an equation solver to the wrong
# answer. CALPHAD programs therefore work in two stages:
#
# 1. **Global stage.** Sample every phase at many compositions. Each sample is a
#    candidate region with a known g. Find the amounts $f_k \ge 0$ of the
#    candidates that give the lowest total energy while keeping all atoms and all
#    B atoms: minimise $\sum_k f_k g_k$ subject to $\sum_k f_k = 1$ and
#    $\sum_k f_k x_k = z$. The objective and both constraints are *linear* in the
#    unknown amounts, so this is a **linear programme**, which has a reliable
#    solver that needs no starting guess.
# 2. **Local stage.** Use the best candidates as the starting guess for the
#    equations of section 4 and refine.
#
# `linprog(c, A_eq=..., b_eq=..., bounds=...)` minimises `c @ f` (the sum of
# c[k] f[k]) subject to `A_eq @ f = b_eq` and the bounds. Our `c` is the list of
# candidate energies, the two rows of `A_eq` are "1 for every candidate" (total
# amount) and "x of every candidate" (B balance), and `b_eq = [1, z]`.

# %%
grid = np.linspace(0.001, 0.999, 201)                     # 201 trial compositions per phase
candidate_x = np.concatenate([grid, grid])                 # SOLID candidates, then LIQUID candidates
candidate_g = np.concatenate([g_phase("SOLID", grid, T), g_phase("LIQUID", grid, T)])   # J/mol
candidate_phase = ["SOLID"] * len(grid) + ["LIQUID"] * len(grid)

result = linprog(candidate_g,
                 A_eq=[np.ones_like(candidate_x), candidate_x],   # total amount, B balance
                 b_eq=[1.0, z],
                 bounds=(0, None),                                 # amounts cannot be negative
                 method="highs")
print("solver finished:", result.success)
for k in np.flatnonzero(result.x > 1e-9):                          # candidates with a non-zero amount
    print(f"  {candidate_phase[k]:6s} x = {candidate_x[k]:.4f}  amount = {result.x[k]:.4f}")
print(f"grid energy {result.fun:.4f} J/mol (best split from section 4: {G_best:.4f})")

# %% [markdown]
# The linear programme picks one SOLID and one LIQUID candidate, each a grid
# point next to the true touching point, and gives an energy just above the
# exact one: a feasible split on a grid can never be lower than the true minimum.
# It found this without any guess and without being told which phases appear.
#
# Now the local stage: start `fsolve` from the two chosen candidates.

# %%
chosen = np.flatnonzero(result.x > 1e-9)
start = {candidate_phase[k]: candidate_x[k] for k in chosen}       # a dict built in one line: {"SOLID": x, "LIQUID": x}
refined = fsolve(mu_difference, [start["SOLID"], start["LIQUID"]], args=(T,))
print(f"grid start: x_S = {start['SOLID']:.4f}, x_L = {start['LIQUID']:.4f}"
      f"  →  refined: x_S = {refined[0]:.6f}, x_L = {refined[1]:.6f}")

# %% [markdown]
# Same answer as section 4, now reached the way a CALPHAD program reaches it.

# %% [markdown]
# ## 6. Many temperatures: the phase diagram
#
# A binary phase diagram shows, for every temperature, which compositions are
# single-phase and which split. For our two phases that means: at each T between
# the melting points of A (1000 K) and B (1800 K), solve for x_S and x_L. Plotted
# against T, the x_S values form the **solidus** line and the x_L values the
# **liquidus** line. Above the liquidus everything is LIQUID, below the solidus
# everything is SOLID, and in between the sample splits.
#
# We already know the answer at 1400 K. From there we walk up in 10 K steps to
# 1790 K and down to 1010 K, each time using the previous answer as the starting
# guess for `fsolve`. Neighbouring temperatures have nearly the same answer, so the
# guess is always close (this is called *continuation*).
#
# For ideal solutions the two equations can also be solved on paper (f4 part C
# shows how). The closed form is a good independent check of the numerical loop:
# with $a = e^{(g^\circ_{A,S}-g^\circ_{A,L})/RT}$ and
# $b = e^{(g^\circ_{B,S}-g^\circ_{B,L})/RT}$,
# $x_S = (1-a)/(b-a)$ and $x_L = b\,x_S$.

# %%
def walk(temperatures, guess):
    """Solve for (x_S, x_L) at each temperature in turn, starting each solve from the previous answer."""
    rows = []
    for T_i in temperatures:
        guess = fsolve(mu_difference, guess, args=(T_i,))
        rows.append((T_i, guess[0], guess[1]))
    return rows

up = walk(np.arange(1400.0, 1800.0, 10.0), [x_S, x_L])     # 1400 → 1790 K
down = walk(np.arange(1390.0, 1000.0, -10.0), [x_S, x_L])  # 1390 → 1010 K
lens = np.array(sorted(down + up))                           # columns: T, x_S, x_L; sorted by T
# lens[:, 0] is the T column (":" means all rows), lens[:, 1:] the x_S and x_L columns

def closed_form(T):
    """x_S and x_L of the ideal lens from the formulas above."""
    a = np.exp((g0("A", "SOLID", T) - g0("A", "LIQUID", T)) / (R * T))
    b = np.exp((g0("B", "SOLID", T) - g0("B", "LIQUID", T)) / (R * T))
    x_solidus = (1 - a) / (b - a)
    return x_solidus, b * x_solidus

exact = np.array([closed_form(T_i) for T_i in lens[:, 0]])
print(f"{len(lens)} temperatures from {lens[0, 0]:.0f} to {lens[-1, 0]:.0f} K;",
      f"largest difference to the closed form: {np.abs(lens[:, 1:] - exact).max():.1e}")

fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.plot(lens[:, 2], lens[:, 0], "-", lw=2, label="liquidus (x_L)")
ax.plot(lens[:, 1], lens[:, 0], "--", lw=2, label="solidus (x_S)")
ax.plot([0, 1], [1000, 1800], "ko", label="pure A and pure B melt")
ax.plot([x_L, x_S], [1400, 1400], "k:|", label="tie line at 1400 K")
ax.plot([z], [1400], "r*", ms=12, label="our sample, z = 0.40")
ax.text(0.15, 1550, "LIQUID", ha="center")
ax.text(0.85, 1400, "SOLID", ha="center")
ax.annotate("SOLID + LIQUID", xy=(0.65, 1600), xytext=(0.25, 1740), fontsize=9,
            arrowprops=dict(arrowstyle="->"))   # text at xytext, arrow pointing into the lens at xy
ax.set(xlabel="B atom fraction", ylabel="T (K)", xlim=(0, 1), title="Our phase diagram, from scratch")
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1))   # legend outside, right of the plot
plt.show()

# %% [markdown]
# **Reading the diagram.** This shape is called a **lens**. The horizontal
# dotted line at 1400 K is a **tie line**: its ends are x_L (left) and x_S
# (right), and our sample (red star) lies on it, so it splits into those two
# compositions, with amounts from the lever rule. The closer the star is to one
# end, the more of that phase. Heat the sample and the star moves up out of the
# lens into LIQUID; cool it and it moves down into SOLID. That is what you found at
# 1600 K in section 4.
#
# The loop and the closed form agree to about 1e-11, so the numerical route is
# right.
#
# ### Your turn: read the diagram
#
# Find the liquidus composition x_L at 1600 K, either with `closed_form(1600.0)`
# or from the table: `lens[lens[:, 0] == 1600]` keeps the rows whose first column
# (T) equals 1600. Is the SOLID that coexists with this liquid richer or poorer in
# B? Answer `"richer"` or `"poorer"`.

# %%
x_liquidus_1600 = None   # B atom fraction
solid_is = None          # "richer" or "poorer" in B than the liquid
check(x_liquidus_1600, "f4b_x_liquidus_1600")
check(solid_is, "f4b_solid_richer")

# %% [markdown]
# ## 7. The same problem in pycalphad
#
# So far we wrote three things ourselves: the **model** (g0, g_phase), the
# **search** (grid, linear programme, equation solver) and the **diagram** (the
# loop over T). In a CALPHAD program the model lives in a **database file** (TDB
# format) and the program does the search and the diagram.
#
# Here is our model as a TDB. Each line ends with `!`:
#
# - `ELEMENT A BLANK 1.0 0.0 0.0` declares a component. The extra fields
#   (reference phase, mass and two reference enthalpy/entropy values) are not used
#   here, so they are placeholders.
# - `TYPE_DEFINITION % SEQ *` is a standard line that most TDB files carry. It
#   defines the type code `%`, which the `PHASE` lines below refer to; it says
#   the phases use no special options.
# - `PHASE SOLID % 1 1` declares a phase with one sublattice holding 1 site per
#   formula unit (one atom per "mole of formula units", so per mole of atoms).
# - `CONSTITUENT SOLID :A,B:` says A and B can both occupy that sublattice. The
#   site fraction of B is then simply x.
# - `PARAMETER G(SOLID,A;0) 300 1000-10*T; 3000 N` is $g^\circ$ of pure A in
#   SOLID: h − T s with our numbers, valid from 300 K to 3000 K (`N` ends the list
#   of temperature ranges).
#
# What is **not** in the file: the ideal mixing term RT[x ln x + (1−x) ln(1−x)].
# pycalphad adds it automatically for every sublattice that holds more than one
# constituent (weighted by the sublattice's number of sites; here one sublattice
# with 1 site, so exactly our term).
# An interaction term (as in f4 part B's regular solution) would be one more line,
# `PARAMETER L(SOLID,A,B;0) ...`; leaving it out makes the solution ideal.

# %%
from pycalphad import Database, binplot, equilibrium, variables as v

LENS_TDB = """
ELEMENT A BLANK 1.0 0.0 0.0 !
ELEMENT B BLANK 1.0 0.0 0.0 !
TYPE_DEFINITION % SEQ * !
PHASE SOLID % 1 1 !
CONSTITUENT SOLID :A,B: !
PARAMETER G(SOLID,A;0) 300 1000-10*T; 3000 N !
PARAMETER G(SOLID,B;0) 300 2000-10*T; 3000 N !
PHASE LIQUID % 1 1 !
CONSTITUENT LIQUID :A,B: !
PARAMETER G(LIQUID,A;0) 300 7000-16*T; 3000 N !
PARAMETER G(LIQUID,B;0) 300 20000-20*T; 3000 N !
"""
db = Database(LENS_TDB)        # Database() reads a file name or, as here, the TDB text itself
print("phases in the database:", sorted(db.phases))

# %% [markdown]
# **Asking for the equilibrium.** `equilibrium(db, components, phases, conditions)`
# does sections 3–5 for us. The conditions fix the state: temperature `v.T`,
# pressure `v.P` (Pa), total amount `v.N` (1 mol of atoms) and overall composition
# `v.X("B")` (our z). Like us, pycalphad first samples every phase on a grid and
# then refines the best candidates by solving the equilibrium equations.
#
# The result is an *xarray Dataset*: a set of named arrays with labelled axes. For
# one set of conditions the interesting ones are, after `.squeeze()` (which drops
# the axes of length 1, here N, P, T and X_B):
#
# - `Phase`: the names of the phases present, one per **vertex** (a vertex is one
#   region of the split; unused vertices are empty strings);
# - `NP`: the amount of each region (our f_L, f_S; NaN for unused vertices);
# - `X`: the composition of each region, with an axis `component` (A, B);
#   `.sel(component="B")` picks the B column, our x_S and x_L;
# - `GM`: the Gibbs energy of the whole sample per mole of atoms (our G);
# - `MU`: the chemical potentials μ_A and μ_B, the same in every region.

# %%
eq = equilibrium(db, ["A", "B"], ["SOLID", "LIQUID"],
                 {v.T: 1400, v.P: 100000, v.N: 1, v.X("B"): 0.40})
phases = eq.Phase.values.squeeze()                        # e.g. ['LIQUID' 'SOLID' '']
amounts = eq.NP.values.squeeze()                          # amount of each region
x_B = eq.X.sel(component="B").values.squeeze()            # B atom fraction of each region
print("pycalphad at 1400 K, z = 0.40")
for name, amount, xb in zip(phases, amounts, x_B):              # zip walks through the three arrays side by side
    if name:                                              # skip unused (empty) vertices
        print(f"  {name:6s} amount {amount:.6f}  x_B {xb:.6f}")
print(f"  GM = {float(eq.GM.values.squeeze()):.4f} J/mol, MU (A, B) = {eq.MU.values.squeeze()} J/mol")

# %% [markdown]
# **Side by side.** The table puts our from-scratch numbers next to pycalphad's.
# We look the phases up by name, because pycalphad does not promise any order of
# the vertices.

# %%
pyc = {name: (amount, xb) for name, amount, xb in zip(phases, amounts, x_B) if name}   # {phase name: (amount, x_B)}, used vertices only
G_pycalphad = float(eq.GM.values.squeeze())
mu_ours = mu_phase("SOLID", x_S, T)
rows = [("x_S (SOLID composition)", x_S, pyc["SOLID"][1]),
        ("x_L (LIQUID composition)", x_L, pyc["LIQUID"][1]),
        ("f_L (LIQUID amount)", f_L, pyc["LIQUID"][0]),
        ("G (J/mol)", G_best, G_pycalphad),
        ("mu_A (J/mol)", mu_ours[0], float(eq.MU.sel(component="A").values.squeeze())),
        ("mu_B (J/mol)", mu_ours[1], float(eq.MU.sel(component="B").values.squeeze()))]
print(f"{'quantity':26s} {'from scratch':>16s} {'pycalphad':>16s} {'difference':>11s}")
for label, ours, theirs in rows:
    print(f"{label:26s} {ours:16.6f} {theirs:16.6f} {ours - theirs:11.1e}")

# %% [markdown]
# The two routes agree to a few 1e-8 or better (energies in J/mol): the same model and the same
# conditions give the same equilibrium, whoever solves it.
#
# ### Your turn: pycalphad at another temperature
#
# Copy the `equilibrium` call into the cell below, change the temperature to
# 1200 K, and read off which phase(s) pycalphad reports for z = 0.40. Does it
# agree with what our lever rule says at 1200 K? Answer with the phase name, or
# `"both"`.

# %%
# Your equilibrium call; use a new name so the 1400 K result `eq` stays, e.g.
# eq_1200 = equilibrium(db, ["A", "B"], ["SOLID", "LIQUID"], {...})
pycalphad_phase_1200 = None   # "SOLID", "LIQUID" or "both"
check(pycalphad_phase_1200, "f4b_phase_1200")

# %% [markdown]
# **The phase diagram in one call.** `binplot` finds points on the phase
# boundaries and then follows each boundary step by step in temperature, each step
# starting from the previous answer: the continuation idea of section 6. The
# conditions now give ranges as `(start, stop, step)`. pycalphad draws each phase
# boundary in its own colour (its legend names the phases) and some tie lines in
# the two-phase region. `binplot` returns a matplotlib axis, so we can draw our own
# lens on top of it as symbols.

# %%
ax = binplot(db, ["A", "B"], ["SOLID", "LIQUID"],
             {v.X("B"): (0, 1, 0.02), v.T: (950, 1850, 10), v.P: 100000, v.N: 1})
# lens[::4, 2]: every 4th row, column 2 (x_L); mfc="none" draws open symbols
ax.plot(lens[::4, 2], lens[::4, 0], "o", mfc="none", color="k", label="our liquidus")
ax.plot(lens[::4, 1], lens[::4, 0], "s", mfc="none", color="k", label="our solidus")
ax.set(title="pycalphad (lines) and our from-scratch lens (symbols)", xlabel="B atom fraction")
phase_legend = ax.get_legend()                                  # the legend binplot made: one colour per phase
handles = list(phase_legend.legend_handles) + ax.get_lines()[-2:]   # its entries plus our two symbol series
labels = [t.get_text() for t in phase_legend.get_texts()] + ["our liquidus", "our solidus"]
ax.legend(handles, labels, fontsize=8, loc="lower right")       # one legend for both
plt.show()

# %% cellView="form"
#@title After your attempt: check the key numbers against the course values
confirm(x_S, 0.440517, "Solidus composition at 1400 K", tol=1e-5)
confirm(x_L, 0.312410, "Liquidus composition at 1400 K", tol=1e-5)
confirm(pyc["SOLID"][1], x_S, "SOLID composition from pycalphad (our value)", tol=1e-8)
confirm(pyc["LIQUID"][1], x_L, "LIQUID composition from pycalphad (our value)", tol=1e-8)
confirm(G_pycalphad, G_best, "G from pycalphad (our value)", tol=1e-6)
confirm(np.abs(lens[:, 1:] - exact).max(), 0.0, "Largest loop-minus-closed-form difference (zero)", tol=1e-9)

# %% [markdown]
# ## 8. What pycalphad did for us
#
# | Step | From scratch (this notebook) | In pycalphad |
# |---|---|---|
# | Pure components | `g0`: h − T s by hand | `PARAMETER G(...)` lines in the TDB |
# | Phase model | `g_phase`: weighted average + ideal mixing | phase and constituent lines; mixing added automatically |
# | Global search | grid + `linprog` (section 5) | sampling of every phase, then the best combination |
# | Exact answer | equal μ_A, μ_B with `fsolve` (section 4) | the equilibrium solver refines the candidates |
# | Amounts | lever rule | `NP` in the result |
# | Phase diagram | loop over T (section 6) | `binplot` |
#
# For two ideal phases everything fits on a page. Real alloys add what makes a
# program worthwhile: many phases, interaction terms, magnetic contributions,
# several sublattices, ordering and more components. The steps stay the same:
# a model for g of every phase, a global search over phases and compositions, and
# equal chemical potentials at the end.
#
# **Limits.** A and B are invented, and both phases are ideal, so the lens is the
# simplest possible two-phase diagram. Each calculation is a closed bulk sample at
# fixed T and p, with no interfaces, strain or kinetics: the diagram says which
# state has the lowest Gibbs energy, not how fast it forms.
#
# Next: [f5 · a binary in pycalphad](f5_binary_pycalphad.ipynb), which reads a
# database with an interaction term and more of what `equilibrium` returns.
