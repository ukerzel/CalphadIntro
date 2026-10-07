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
# # f4 · Two phases: common tangent, lever rule and phase diagrams
#
# **Learning question:** when does a sample split into two regions, which
# compositions do they take, how much of each forms, and how do these answers
# at many temperatures draw a phase diagram?
#
# Used in: Lessons 5, 7; self-study step 03 (parts A, B, C).
# Work each "your turn" on paper first, then type your value.
#
# **The plan.** f3 built the Gibbs-energy curve of *one* phase and read chemical
# potentials from its tangent. Here a sample may divide into two regions, and we
# ask whether that lowers the total Gibbs energy.
#
# - **Part A** (sections 1 and 2): two different phases, ALPHA and BETA. The lever
#   rule counts the atoms, the common tangent picks the compositions, and a
#   linear programme shows how a computer finds them.
# - **Part B** (section 3): one phase whose curve has a hump, so it splits into two
#   regions of the *same* phase (a miscibility gap). Repeating the calculation at
#   many temperatures draws a phase diagram.
# - **Part C** (section 4): a SOLID and a LIQUID, which together give the melting
#   "lens" diagram.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.4"
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
# ## 1. Part A: two phases, one sample
#
# Closed bulk sample, one mole of atoms, overall B fraction z, p = 100000 Pa,
# T = 1000 K. Two invented phases, ALPHA and BETA, can each hold A and B; x is
# the B atom fraction inside a phase. Energies are J/mol of atoms, with
# R = 8.3145 J/(mol K) and q(x) = (1 − x) ln(1 − x) + x ln x:
#
# $$g_\alpha(x) = -9000 + 12000\,x + RT\,q(x),\qquad g_\beta(x) = 3000 - 12000\,x + RT\,q(x).$$
#
# The two curves are mirror images: g_β(0.8) = g_α(0.2).
#
# **Reading the formulas.** g_α is exactly the ideal ALPHA curve of f3: a straight
# reference line plus the ideal mixing term RT q(x). ALPHA is cheap (low g) near
# pure A and expensive near pure B. BETA has the same mixing term but the opposite
# reference line, so it is cheap near pure B. Replacing x by 1 − x turns one
# formula into the other: −9000 + 12000(1 − x) = 3000 − 12000x, and q is symmetric.
# That is why the curves are mirror images about x = 0.5.
#
# Note the two different composition symbols: **z** is the overall B fraction of
# the whole sample (fixed, because the sample is closed), **x** is the B fraction
# inside one phase region (free to choose, as long as the atoms add up).
#
# **The Python.** `def g_alpha(x, T=T_A):` gives the argument T a *default value*:
# `g_alpha(0.3)` uses T = 1000 K, while `g_alpha(0.3, 600.0)` would use 600 K.

# %%
import numpy as np
from scipy.special import xlogy   # xlogy(x, x) is x ln x, and 0 at x = 0

R = 8.3145   # J/(mol K)
T_A = 1000.0  # K

def q(x):
    return xlogy(1 - x, 1 - x) + xlogy(x, x)   # dimensionless

def g_alpha(x, T=T_A):
    return -9000.0 + 12000.0 * x + R * T * q(x)   # J/mol atoms (at 1000 K)

def g_beta(x, T=T_A):
    return 3000.0 - 12000.0 * x + R * T * q(x)    # J/mol atoms (at 1000 K)

print(f"g_alpha(0.3) = {g_alpha(0.3):.3f} J/mol, g_beta(0.3) = {g_beta(0.3):.3f} J/mol")   # same x, two phases

# %% [markdown]
# ### The lever rule is a balance
#
# A split into an ALPHA region at x_α and a BETA region at x_β must keep the
# amounts of A and B:
# f_α + f_β = 1 and f_α x_α + f_β x_β = z, with 0 ≤ f ≤ 1. Solving gives
#
# $$f_\beta = \frac{z - x_\alpha}{x_\beta - x_\alpha},\qquad f_\alpha = 1 - f_\beta.$$
#
# The split's energy per mole of atoms is f_α g_α(x_α) + f_β g_β(x_β). The lever
# rule fixes the amounts for given endpoints; it does not say which endpoints
# the sample chooses.
#
# **Solving step by step.** Put f_α = 1 − f_β into the B balance:
# (1 − f_β) x_α + f_β x_β = z, so x_α + f_β (x_β − x_α) = z, so
# f_β = (z − x_α)/(x_β − x_α). The picture behind the name: on the composition
# axis, z sits between x_α and x_β like the pivot of a lever. The fraction of BETA
# is the length of the arm from x_α to z, divided by the whole length. The closer z
# lies to x_β, the more BETA forms.
#
# The two functions below turn these formulas into code. `f_beta` is the lever
# rule; `g_split` uses it to weight the two Gibbs energies. The printed example
# uses endpoints 0.1 and 0.9 at z = 0.6.

# %%
def f_beta(z, x_alpha, x_beta):
    return (z - x_alpha) / (x_beta - x_alpha)   # mol BETA atoms per mol atoms

def g_split(z, x_alpha, x_beta):
    fb = f_beta(z, x_alpha, x_beta)
    return (1 - fb) * g_alpha(x_alpha) + fb * g_beta(x_beta)   # J/mol atoms

print(f"endpoints 0.1/0.9 at z = 0.6: f_beta = {f_beta(0.6, 0.1, 0.9):.3f}")   # arm 0.5 over length 0.8

# %% [markdown]
# ### Your turn: split or stay homogeneous? (z = 0.5)
#
# 1. Homogeneous ALPHA at x = 0.5: use q(0.5) = −0.69314718 and RT = 8314.5 J/mol.
# 2. A split with x_α = 0.2 and x_β = 0.8: find f_β from the balance, then the
#    split energy using g_α(0.2) = g_β(0.8) = −10760.596 J/mol.
# 3. How much lower is the split than the homogeneous state (a positive number)?
#
# "Homogeneous" means the whole sample stays one ALPHA region at x = z.

# %%
g_alpha_half = None    # J/mol atoms, homogeneous ALPHA at x = 0.5
f_beta_half = None     # mol BETA atoms per mol atoms, 0.2/0.8 split at z = 0.5
g_split_half = None    # J/mol atoms, to 0.01 J/mol (the difference to μ_A below is only about 2 J/mol)
split_lower_by = None  # J/mol atoms, homogeneous minus split
check(g_alpha_half, "f4_g_alpha_half")
check(f_beta_half, "f4_f_beta_half")
check(g_split_half, "f4_g_split_half")
check(split_lower_by, "f4_split_lower_by")

# %% [markdown]
# ### Your turn: the lever with other overall compositions
#
# Same endpoints 0.2 and 0.8. Draw the composition axis, mark both endpoints and
# z, then find f_α and f_β at z = 0.35. What does the balance give for f_β at
# z = 0.1 (a fraction typed as a division, or three decimals), and can these
# endpoints make that sample?
#
# For `z01_possible` type the Python word `True` or `False`. You can use the
# `f_beta` function above to check your hand calculation.

# %%
f_alpha_035 = None   # mol ALPHA atoms per mol atoms at z = 0.35
f_beta_035 = None    # mol BETA atoms per mol atoms at z = 0.35
f_beta_01 = None     # what the formula gives at z = 0.1
z01_possible = None  # True or False
check(f_alpha_035, "f4_f_alpha_035")
check(f_beta_035, "f4_f_beta_035")
check(f_beta_01, "f4_f_beta_01")
check(z01_possible, "f4_z01_possible")

# %% [markdown]
# ### The common tangent
#
# A split's energy lies on the straight line between its two points
# (x_α, g_α) and (x_β, g_β), read at x = z. The lowest such line touches both
# curves: a **common tangent**. Being one line for both phases, it meets x = 0
# and x = 1 at the same values, μ_A and μ_B, so each chemical potential is the
# same in both phases and atoms gain nothing by moving between them.
#
# The best split here uses x_α ≈ 0.19104 and x_β ≈ 0.80896, with energy
# −10762.730 J/mol. Every z between those two compositions splits into the same
# two compositions; only the amounts change, by the lever rule.
#
# **Why a straight line?** Put the lever rule into the split energy:
# f_α g_α + f_β g_β with f_β = (z − x_α)/(x_β − x_α) is a weighted average of the
# two end values, with weights that change linearly with z. That is exactly the
# straight line (the *chord*) joining the two points, evaluated at z. Finding the
# best split therefore means finding the lowest chord that can be drawn from a point
# on the ALPHA curve to a point on the BETA curve. You can lower a chord until it
# just touches both curves; then it is tangent to both.
#
# Recall from f3 that a tangent's ends at x = 0 and x = 1 are μ_A and μ_B of the
# phase it touches. A *common* tangent has the same two ends for both phases, so
# μ_A(ALPHA) = μ_A(BETA) and μ_B(ALPHA) = μ_B(BETA): this equality of chemical
# potentials is the equilibrium condition between phases.
#
# ### Your turn: the tangent's ends
#
# The curves are mirror images, so the common tangent is horizontal. What is
# μ_A at the best split (J/mol)?

# %%
mu_A_best = None   # J/mol of A, to 0.01 J/mol
check(mu_A_best, "f4_mu_a_best")

# %% [markdown]
# ## 2. How a computer finds the split (Lesson 5)
#
# A computer does not know the touching points in advance. It picks a grid of
# trial compositions for each phase. Every phase/grid point is a possible region
# with a known energy; the unknowns are the amount fractions f ≥ 0. Minimising
# Σ f g subject to Σ f = 1 and Σ f x = z is a **linear programme**. Its result is
# a feasible split, so its energy is an **upper bound** on the true minimum. A
# finer grid that contains the old points cannot do worse.
#
# Here is the whole idea on a 5-point grid, with SciPy's `linprog`:
#
# **Setting up the problem.** With 5 grid points per phase there are 10 candidate
# regions: ALPHA at x = 0, 0.25, 0.5, 0.75, 1 and BETA at the same five
# compositions. Each candidate i has a known composition x_i and energy g_i; the
# unknown is its amount f_i. `linprog` then solves:
#
# - minimise $\sum_i f_i\,g_i$ (argument 1, `energies`: the cost of each unknown);
# - subject to the equations in `A_eq` and `b_eq`, read row by row as
#   "row · f = value": the row of ones gives Σ f_i = 1 (one mole in total), the
#   row `x_all` gives Σ f_i x_i = z (B balance);
# - with `bounds=(0, None)`: every f_i ≥ 0 and no upper limit (the total of 1
#   already caps them);
# - `method="highs"` chooses SciPy's standard solver for linear programmes.
#
# `result.x` holds the best amounts f, `result.fun` the minimum Σ f g, and
# `result.success` says whether the solver finished properly.
#
# **Other Python here.** `np.concatenate([a, b])` joins two arrays end to end;
# `f @ x_all` is the *dot product* Σ f_i x_i; `np.flatnonzero(f > 0)` lists the
# positions where f is not zero; `'ALPHA' if i < points else 'BETA'` picks a word
# depending on a condition (the first `points` entries are ALPHA).

# %%
from scipy.optimize import linprog

points = 5
grid = np.linspace(0.0, 1.0, points)                        # trial compositions 0, 0.25, 0.5, 0.75, 1
x_all = np.concatenate([grid, grid])                        # ALPHA points, then BETA points
energies = np.concatenate([g_alpha(grid), g_beta(grid)])    # J/mol atoms
z = 0.5                                                     # overall B fraction of the sample
# minimise energies · f  with  [1 1 ... 1] · f = 1  and  x_all · f = z,  all f ≥ 0
result = linprog(energies, A_eq=[np.ones_like(x_all), x_all], b_eq=[1.0, z],
                 bounds=(0, None), method="highs")
f = result.x                                                # amount of each candidate region, mol per mol atoms
print("success:", result.success, "| total:", f.sum(), "| B:", f @ x_all, "| A:", f @ (1 - x_all))   # balances: 1, z, 1 − z
for i in np.flatnonzero(f > 0):                             # only the regions that are used
    print(f"  {'ALPHA' if i < points else 'BETA'} at x = {x_all[i]:.2f}: f = {f[i]:.3f}")
print(f"grid energy: {result.fun:.3f} J/mol")               # minimum Σ f g over this grid

# %% [markdown]
# **What to look at.** First check the balance line: total 1, B equal to z, A equal
# to 1 − z. Then see which candidates the solver used: of the ten, only two carry a
# non-zero amount, one of each phase. Finally compare the grid energy with the best
# split, −10762.730 J/mol. The grid result is higher, because the true touching
# points are not on this coarse grid.
#
# ### Your turn: predict the finer grids
#
# The Lesson 5 table uses 21, 101 and 501 uniform points per phase at z = 0.5.
#
# 1. With 21 points (spacing 0.05) the search picks the grid points closest to
#    the touching points. How far above the best split (−10762.730 J/mol) does its
#    energy lie (J/mol, three significant figures are enough)?
# 2. With 101 points (spacing 0.01), which ALPHA composition does it pick?

# %%
grid21_gap = None     # J/mol, 21-point grid energy minus −10762.730
x_alpha_101 = None    # B atom fraction chosen in ALPHA
check(grid21_gap, "f4_grid21_gap")
check(x_alpha_101, "f4_x_alpha_101")

# %% [markdown]
# The next cell repeats the grid search with 21, 101 and 501 points through the
# course function `ideal_grid`, which does the same `linprog` set-up as above.
# Each printed row is: number of points per phase, grid energy (J/mol), its distance
# above the exact minimum (J/mol), and the three balances (total, A, B).
# `state['regions']` is a list of dictionaries, one per region used, each with the
# phase, composition `'x'` and amount `'f'`; `sum(r['f'] for r in regions)` adds up
# the amounts. `lesson5` is a dictionary from the number of points to the
# (energy, ALPHA composition) pair quoted in Lesson 5.

# %% cellView="form"
#@title After your attempt: the Lesson 5 refinement, 21 → 101 → 501 points
from course.foundations.binary_family import ideal_grid, ideal_equilibrium
T, z = 1000.0, 0.5   # K, overall B fraction
reference = ideal_equilibrium(T, z)['GM']   # exact (continuous) minimum, J/mol
for points in (21, 101, 501):
    state = ideal_grid(T, z, points)
    regions = state['regions']               # list of {'phase', 'x', 'f'} for the regions used
    total = sum(r['f'] for r in regions)          # should be 1
    B = sum(r['f']*r['x'] for r in regions)       # should be z
    A = sum(r['f']*(1-r['x']) for r in regions)   # should be 1 − z
    print(points, f"{state['GM']:.6f}", f"{state['GM']-reference:.6f}",
          f'{total:.6f}', f'{A:.6f}', f'{B:.6f}')

lesson5 = {21: (-10760.595951, 0.2), 101: (-10762.700840, 0.19), 501: (-10762.705297, 0.192)}
for points, (energy, x_alpha) in lesson5.items():
    state = ideal_grid(T, z, points)
    confirm(state["GM"], energy, f"{points}-point grid energy", tol=1e-6)
    confirm(state["regions"][0]["x"], x_alpha, f"{points}-point ALPHA composition", tol=1e-12)
confirm(reference, -10762.730017, "Continuous minimum", tol=1e-6)

# %% [markdown]
# Each finer grid gets closer to −10762.730 J/mol from above, and the chosen
# endpoints need not move steadily. pycalphad starts the same way: before it
# refines a result, it samples many trial compositions of every phase, and its
# `pdens` setting is the number of sample points per degree of freedom. f5 shows
# this on a database.

# %% [markdown]
# ## 3. Part B: one phase, two compositions (Lesson 7)
#
# Now only ALPHA is allowed, with one extra mixing term that penalises unlike
# neighbours (a **regular solution**), Ω = 20000 J/mol:
#
# $$g(x) = 1000 + 12000\,x - 10T + RT\,q(x) + \Omega\,x(1-x).$$
#
# The straight part 1000 + 12000x − 10T does not change which split is lowest,
# so we look at the **mixing part** Δg_mix = Ω x(1 − x) + RT q(x). At low T it
# has a hump in the middle; a tangent then touches it twice, and the sample
# separates into two ALPHA regions of different composition: a **miscibility
# gap**. The touching compositions solve RT ln(x/(1 − x)) + Ω(1 − 2x) = 0 away
# from the middle root x = 0.5. The hump disappears at the critical temperature
# T_c = Ω/(2R).
#
# **Where the new term comes from.** In a random mixture, the chance that a given
# pair of neighbouring sites holds one A and one B is proportional to x(1 − x).
# If an A–B bond costs more energy than the average of A–A and B–B bonds, each
# unlike pair adds a little energy; Ω (in J/mol) collects that cost. Ω > 0 means
# the atoms "prefer" like neighbours. Two effects now compete: the Ω term favours
# separating A and B, the entropy term RT q(x) favours mixing, and its weight grows
# with T.
#
# **Why the straight part can be ignored.** Adding any straight line a + bx to a
# curve adds the same a + bz to *every* balanced split at overall composition z, so
# it does not change which split is lowest. Only the curved mixing part matters.
#
# **Where the two formulas come from.** Δg_mix is symmetric about x = 0.5, so the
# tangent touching it twice is horizontal: it touches where the slope is zero. The
# slope is d/dx[Ω x(1 − x)] + d/dx[RT q(x)] = Ω(1 − 2x) + RT ln(x/(1 − x)). For T_c:
# the hump exists while the curve bends downwards at x = 0.5. The curvature (second
# derivative) is −2Ω + RT/(x(1 − x)), which at x = 0.5 is −2Ω + 4RT. It changes sign
# when 4RT = 2Ω, that is at T = Ω/(2R).
#
# The cell prints the mixing part at three compositions for one low and one high
# temperature. **What to look at:** does it rise or fall towards x = 0.5?

# %%
OMEGA = 20000.0   # J/mol

def g_mix_regular(x, T):
    return OMEGA * x * (1 - x) + R * T * q(x)   # J/mol atoms

for T in (600.0, 1500.0):   # K, one temperature below and one above T_c
    # round(float(...), 1): one decimal place; the list comprehension evaluates three compositions
    print(f"{T:.0f} K: mixing part at x = 0.3, 0.4, 0.5:",
          [round(float(g_mix_regular(x, T)), 1) for x in (0.3, 0.4, 0.5)], "J/mol")

# %% [markdown]
# ### Your turn: predict, then compute T_c
#
# As T rises towards T_c, do the two compositions move closer together or
# further apart? Answer with one word, `"together"` or `"apart"`. Then compute
# T_c in kelvin (four significant figures).
#
# The quotation marks matter: in Python, `"together"` is a piece of text (a
# *string*), while `together` without quotes would be an unknown variable name.

# %%
gap_direction = None   # "together" or "apart"
T_c = None             # K
check(gap_direction, "f4_gap_direction")
check(T_c, "f4_tc")

# %% [markdown]
# ### Your turn: build the gap diagram
#
# `regular_binodal(T)` returns the two touching compositions at T (an empty list
# at or above T_c). Fill the list of temperatures (K, between 600 and 1200), run
# the cell and plot both compositions against T. That plot is a phase diagram:
# outside the curve one ALPHA is stable, inside the sample splits. Then enter
# the left composition at 900 K (four significant figures).
#
# **How the cell works.** `regular_binodal(T)` solves the touching condition above
# numerically and returns a dictionary; its entry `"compositions"` is the list
# [x_left, x_right]. The loop collects the results in three lists with `.append`,
# which adds one item to the end of a list. `if ends:` is True only for a non-empty
# list, so temperatures without a gap are skipped. `if gap_T:` draws the plot only
# when there is something to draw, which is why the cell runs without error while
# your list is still empty.
#
# A phase diagram puts composition on the horizontal axis and temperature on the
# vertical axis, so the plot uses `plt.plot(compositions, temperatures)`.
#
# Typing the list: either by hand, `[600, 700, 800]`, or with
# `list(range(600, 1201, 50))`, which gives 600, 650, …, 1200 (`range` stops just
# before its second number). Include 900 so you can read the answer, and use
# enough temperatures to see the shape. The course function accepts temperatures
# from 600 to 1800 K.

# %%
from course.foundations.binary_family import regular_binodal
import matplotlib.pyplot as plt

gap_temperatures = []   # K, e.g. 600, 650, ...; your choice
gap_T, gap_left, gap_right = [], [], []   # three empty lists, filled by the loop
for T in gap_temperatures:
    ends = regular_binodal(T)["compositions"]   # [x_left, x_right], or [] at or above T_c
    if ends:                                    # skip temperatures without a gap
        gap_T.append(T)
        gap_left.append(ends[0])
        gap_right.append(ends[1])
if gap_T:                                       # plot only if at least one temperature has a gap
    plt.plot(gap_left, gap_T, "o-", label="B-poor region")     # x on the horizontal axis, T vertical
    plt.plot(gap_right, gap_T, "s--", label="B-rich region")
    plt.xlabel("B atom fraction x")
    plt.ylabel("T (K)")
    plt.legend(fontsize=10)
    plt.show()
    print("T (K)   x_left    x_right")
    for T, xl, xr in zip(gap_T, gap_left, gap_right):
        print(f"{T:6.0f}  {xl:.5f}  {xr:.5f}")

x_left_900 = None   # B atom fraction of the B-poor region at 900 K
check(x_left_900, "f4_x_left_900")

# %% [markdown]
# **Reading the diagram.** Each temperature contributes one horizontal *tie line*
# from x_left to x_right. A sample whose overall composition z lies between them
# splits into a B-poor and a B-rich ALPHA region with those compositions, in amounts
# given by the lever rule; a sample outside stays one homogeneous ALPHA.
#
# Parts A and B used one phase curve or two mirror-image ones. Part C applies the
# same common-tangent idea to a solid and a liquid, which gives the most common
# diagram for two metals that mix completely.

# %% [markdown]
# ## 4. Part C: melting and the lens
#
# Now a SOLID and a LIQUID, each an ideal solution of A and B. Component A is the
# one from f1 (SOLID h = 1000, s = 10; LIQUID h = 7000, s = 16), so it melts at
# 1000 K. Component B is invented: SOLID h = 2000, s = 10; LIQUID h = 20000,
# s = 20 (J/mol and J/(mol K)), so it melts at 1800 K. Between those two
# temperatures a common tangent touches both curves. Step 01 used A's straight
# lines only over 800–1200 K; this example simply uses the same invented lines,
# and B's, over 950–1850 K.
#
# For ideal solutions, equal μ_A and μ_B in both phases give two short equations.
# With $a = e^{(g^\circ_{A,S}-g^\circ_{A,L})/RT}$ and $b = e^{(g^\circ_{B,S}-g^\circ_{B,L})/RT}$:
#
# $$1 - x_L = a\,(1 - x_S),\qquad x_L = b\,x_S\quad\Rightarrow\quad x_S = \frac{1-a}{b-a},\; x_L = b\,x_S.$$
#
# x_S is the **solidus** composition and x_L the **liquidus** composition.
#
# **Symbols.** $g^\circ_{A,S}$ is the molar Gibbs energy of *pure* A as a SOLID,
# h − Ts from the numbers above (likewise for L = LIQUID and for B). The melting
# points follow from $g^\circ_S = g^\circ_L$: for A, 1000 − 10T = 7000 − 16T gives
# T = 1000 K; for B, 2000 − 10T = 20000 − 20T gives T = 1800 K.
#
# **Deriving the two equations.** In an ideal solution (f3, section 3) the chemical
# potential of A is $\mu_A = g^\circ_A + RT\ln(1-x)$, and of B is
# $\mu_B = g^\circ_B + RT\ln x$. Equal μ_A in SOLID and LIQUID means
#
# $$g^\circ_{A,S} + RT\ln(1-x_S) = g^\circ_{A,L} + RT\ln(1-x_L)
# \;\Rightarrow\; \ln\frac{1-x_L}{1-x_S} = \frac{g^\circ_{A,S}-g^\circ_{A,L}}{RT}
# \;\Rightarrow\; 1-x_L = a\,(1-x_S).$$
#
# The same steps for B give x_L = b x_S. Putting the second equation into the first,
# 1 − b x_S = a − a x_S, and solving for x_S gives the formula above.
#
# **When is there a solution?** a > 1 means pure A's LIQUID is below its SOLID
# (A is above its melting point); b < 1 means pure B's SOLID is below its LIQUID
# (B is below its melting point). Both hold only between the two melting points;
# outside that range the formula would give compositions outside 0…1, so the
# function returns `None` ("no answer"). Python allows the chained comparison
# `a > 1 > b`, which means `a > 1 and 1 > b`.
#
# **The Python.** `H` and `S` are *nested dictionaries*: `H["B"]["LIQUID"]` first
# looks up B, then LIQUID inside it, giving 20000.0. The text in triple quotes
# under `def lens_ends` is a *docstring*, a short description of the function.
# `np.exp` is the exponential function.

# %%
H = {"A": {"SOLID": 1000.0, "LIQUID": 7000.0}, "B": {"SOLID": 2000.0, "LIQUID": 20000.0}}   # J/mol
S = {"A": {"SOLID": 10.0, "LIQUID": 16.0}, "B": {"SOLID": 10.0, "LIQUID": 20.0}}           # J/(mol K)

def g0(element, phase, T):
    return H[element][phase] - T * S[element][phase]   # J/mol of the pure element

def lens_ends(T):
    """(x_SOLID, x_LIQUID) at T in K, or None outside the two-phase range."""
    a = np.exp((g0("A", "SOLID", T) - g0("A", "LIQUID", T)) / (R * T))   # dimensionless
    b = np.exp((g0("B", "SOLID", T) - g0("B", "LIQUID", T)) / (R * T))   # dimensionless
    if not a > 1 > b:          # only between the two melting points
        return None
    x_solid = (1 - a) / (b - a)        # solidus: B fraction of the SOLID
    return x_solid, b * x_solid        # (solidus, liquidus)

print("950 K:", lens_ends(950.0), "| 1850 K:", lens_ends(1850.0))   # both outside 1000–1800 K

# %% [markdown]
# **What to look at.** Both test temperatures lie outside the range between the two
# melting points, so both calls return `None`: at 950 K everything is solid, at
# 1850 K everything is liquid, whatever the composition.
#
# ### Your turn: build the lens
#
# Fill the temperatures (K, between 1000 and 1800), run and plot both edges.
# Then give x_S and x_L at 1400 K (four significant figures), and say which
# component the solid is richer in: `"A"` or `"B"`.
#
# The cell works like the gap cell above: list your temperatures, for example with
# `list(range(1050, 1800, 50))`, and include 1400. To answer the last question,
# compare x_S and x_L at the same temperature (x is the B fraction).

# %%
lens_temperatures = []   # K, your choice
lens_T, lens_solid, lens_liquid = [], [], []
for T in lens_temperatures:
    ends = lens_ends(T)                 # (x_SOLID, x_LIQUID), or None
    if ends:                            # None counts as False: skip temperatures outside the lens
        lens_T.append(T)
        lens_solid.append(ends[0])
        lens_liquid.append(ends[1])
if lens_T:
    plt.plot(lens_liquid, lens_T, "o-", label="liquidus (LIQUID composition)")
    plt.plot(lens_solid, lens_T, "s--", label="solidus (SOLID composition)")
    plt.xlabel("B atom fraction x")
    plt.ylabel("T (K)")
    plt.legend(fontsize=10)
    plt.show()
    print("T (K)   x_LIQUID  x_SOLID")
    for T, xs, xl in zip(lens_T, lens_solid, lens_liquid):
        print(f"{T:6.0f}  {xl:.5f}   {xs:.5f}")

x_solid_1400 = None    # B atom fraction
x_liquid_1400 = None   # B atom fraction
solid_richer_in = None   # "A" or "B"
check(x_solid_1400, "f4_lens_xs_1400")
check(x_liquid_1400, "f4_lens_xl_1400")
check(solid_richer_in, "f4_lens_richer")

# %% [markdown]
# ## 5. After your attempt: check with the course code and plot
#
# The cells below reproduce the step 03 and Lesson 7 numbers with the course
# functions, then draw the four pictures. Each plot has a small table beside it.
#
# **Part A cell.** The `confirm` lines check your part A numbers against the course
# module `binary_family` (`bf`). `bf.ideal_equilibrium(1000.0, 0.5)` returns the
# exact best split: a dictionary with `"GM"` and a list of `"regions"`, here an ALPHA
# and a BETA region with their compositions `"x"`. `bf.ideal_derivatives` gives μ_A
# and μ_B in each phase at its touching point; they must be equal in both phases.
#
# The plot draws both curves, the common tangent and, below it, the two lever
# arms for z = 0.35. The tangent is the straight line from μ_A at x = 0 to μ_B at
# x = 1: ℓ(x) = μ_A + (μ_B − μ_A) x. The arm from x_α to z sets the amount of BETA,
# the arm from z to x_β sets the amount of ALPHA: each phase's amount is given by
# the arm on the *opposite* side. The marker style `"-|"` draws a line with short
# vertical end marks; `ylim` fixes the vertical range of the plot.

# %% cellView="form"
#@title After your attempt: part A numbers and the common tangent
from course.foundations import binary_family as bf

confirm(float(bf.ideal_properties(1000.0, 0.5, "ALPHA")["GM"]), -8763.172, "Homogeneous ALPHA at x = 0.5", tol=1e-3)
confirm(float(g_alpha(0.5)), -8763.172, "Same value from the formula above", tol=1e-3)
confirm(float(bf.ideal_properties(1000.0, 0.2, "ALPHA")["GM"]), -10760.596, "g_alpha(0.2)", tol=1e-3)
confirm(float(bf.ideal_properties(1000.0, 0.8, "BETA")["GM"]), -10760.596, "g_beta(0.8)", tol=1e-3)
confirm(bf.lever_fraction(0.5, 0.2, 0.8), 0.5, "f_beta for 0.2/0.8 at z = 0.5", tol=1e-12)
confirm(float(g_split(0.5, 0.2, 0.8)), -10760.596, "0.2/0.8 split energy", tol=1e-3)
confirm(bf.lever_fraction(0.35, 0.2, 0.8), 0.25, "f_beta at z = 0.35", tol=1e-12)
confirm(f_beta(0.1, 0.2, 0.8), -1 / 6, "Balance at z = 0.1 (negative, so impossible)", tol=1e-12)

best = bf.ideal_equilibrium(1000.0, 0.5)                 # exact best split at z = 0.5
xa, xb = best["regions"][0]["x"], best["regions"][1]["x"]   # touching compositions in ALPHA and BETA
mu = bf.ideal_derivatives(1000.0, xa, "ALPHA")           # mu_A, mu_B of ALPHA at its touching point
mu_beta = bf.ideal_derivatives(1000.0, xb, "BETA")       # the same for BETA
confirm(xa, 0.19104, "Best ALPHA composition", tol=1e-5)
confirm(xb, 0.80896, "Best BETA composition", tol=1e-5)
confirm(best["GM"], -10762.730, "Best split energy", tol=1e-3)
confirm(float(mu["mu_A"]), -10762.730, "mu_A in ALPHA", tol=1e-3)
confirm(float(mu_beta["mu_A"]), float(mu["mu_A"]), "mu_A equal in BETA", tol=1e-6)
confirm(float(mu_beta["mu_B"]), float(mu["mu_B"]), "mu_B equal in both phases", tol=1e-6)

x = np.linspace(0.0, 1.0, 201)
tangent = float(mu["mu_A"]) + (float(mu["mu_B"]) - float(mu["mu_A"])) * x   # common tangent, J/mol
z_show = 0.35                                              # overall composition used for the lever arms
fb = bf.lever_fraction(z_show, xa, xb)                     # f_beta at z_show
g_at_z = float(mu["mu_A"]) + (float(mu["mu_B"]) - float(mu["mu_A"])) * z_show   # tangent height at z_show
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(x, g_alpha(x) / 1000, "-", label="ALPHA")
ax.plot(x, g_beta(x) / 1000, "--", label="BETA")
ax.plot(x, tangent / 1000, ":", color="k", label="common tangent")
ax.plot([xa, xb], [g_alpha(xa) / 1000, g_beta(xb) / 1000], "ko", label="touching points")
# the two lever arms, drawn 0.4 and 0.8 kJ/mol below the tangent so they do not hide it
ax.plot([xa, z_show], [g_at_z / 1000 - 0.4] * 2, "-|", lw=2, label=f"arm z − x_α → f_β = {fb:.3f}")
ax.plot([z_show, xb], [g_at_z / 1000 - 0.8] * 2, "--|", lw=2, label=f"arm x_β − z → f_α = {1 - fb:.3f}")
ax.axvline(z_show, color="grey", lw=0.8)                  # vertical line at z
ax.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="1000 K: ALPHA, BETA and the common tangent",
       ylim=(-12.5, -2))
ax.legend(fontsize=10, loc="upper center")
plt.show()
print(" x      g_ALPHA (J/mol)  g_BETA (J/mol)")
for xi in (0.1, 0.19104, 0.5, 0.80896, 0.9):
    print(f"{xi:.5f}  {g_alpha(xi):12.3f}  {g_beta(xi):12.3f}")
print(f"z = {z_show} with the best endpoints: f_alpha = {1 - fb:.4f}, f_beta = {fb:.4f}; the vertical line marks z")

# %% [markdown]
# **Part B cell.** After checking T_c and the 600 K compositions, it draws two
# panels. *Left:* the mixing part at four temperatures; where a gap exists, the
# horizontal tangent is drawn in black between its two touching points. *Right:* the
# gap diagram from 600 K up to 1200 K in steps of 25 K, with T_c marked by a star.
#
# Python details: `np.arange(600.0, 1200.0, 25.0)` gives 600, 625, …, 1175 (it stops
# before 1200), so 1200 is added with `np.concatenate`. In
# `(T, *bf.regular_binodal(T)["compositions"], ...)` the `*` unpacks a list into
# separate entries, so each row becomes (T, x_left, x_right, spinodal_left,
# spinodal_right). The *spinodal* compositions are where the curve's curvature
# changes sign; they are stored but not plotted here. `table[:, 1]` takes column 1
# of every row; `rows[::4]` takes every fourth row; and `for T, xl, xr, *_ in ...`
# keeps the first three entries and ignores the rest.

# %% cellView="form"
#@title After your attempt: part B, the hump and the gap diagram
confirm(bf.TC_R1, 1202.718143, "T_c = Omega/(2R)", tol=1e-6)
confirm(OMEGA / (2 * R), bf.TC_R1, "T_c from the formula above", tol=1e-9)
ends_600 = bf.regular_binodal(600.0)["compositions"]
confirm(ends_600[0], 0.021032752, "Left composition at 600 K", tol=1e-9)
confirm(ends_600[1], 0.978967248, "Right composition at 600 K", tol=1e-9)
confirm(float(bf.regular_properties(600.0, 0.5)["GM_mix"]), 1542.096660, "Mixing part at x = 0.5, 600 K", tol=1e-6)
confirm(float(g_mix_regular(0.5, 600.0)), 1542.096660, "Same value from the formula above", tol=1e-6)

x_in = np.linspace(0.001, 0.999, 400)   # avoid the pure ends
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))
for T, style in ((600.0, "-"), (900.0, "--"), (1100.0, "-."), (1300.0, ":")):   # K, line style
    left.plot(x_in, g_mix_regular(x_in, T) / 1000, style, label=f"{T:.0f} K")
    ends = bf.regular_binodal(T)["compositions"]
    if ends:                                         # a gap exists at this T
        level = float(g_mix_regular(ends[0], T)) / 1000   # height of the horizontal tangent, kJ/mol
        left.plot(ends, [level, level], "ko-", ms=4)
left.set(xlabel="B atom fraction x", ylabel="mixing part Δg_mix (kJ/mol atoms)",
         title="Hump and horizontal tangent (black)")
left.legend(fontsize=10)

temps = np.concatenate([np.arange(600.0, 1200.0, 25.0), [1200.0]])   # K
# each row: T, x_left, x_right, spinodal_left, spinodal_right
rows = [(T, *bf.regular_binodal(T)["compositions"], *bf.regular_binodal(T)["spinodal"]) for T in temps]
table = np.array(rows)
right.plot(table[:, 1], table[:, 0], "o-", ms=3, label="B-poor region")
right.plot(table[:, 2], table[:, 0], "s--", ms=3, label="B-rich region")
right.plot([0.5], [bf.TC_R1], "k*", ms=10, label=f"T_c ≈ {bf.TC_R1:.0f} K")
right.set(xlabel="B atom fraction x", ylabel="T (K)", title="Miscibility gap (one ALPHA phase)", xlim=(0, 1))
right.legend(fontsize=10)
plt.show()
print("T (K)   x_left    x_right")
for T, xl, xr, *_ in rows[::4]:          # every fourth row (every 100 K); spinodal columns ignored
    print(f"{T:6.0f}  {xl:.5f}  {xr:.5f}")
print(f"{bf.TC_R1:6.1f}  0.5 (the two compositions meet)")

# %% [markdown]
# **Part C cell.** It checks the formula in `lens_ends` against the course function
# `tp.lens_coexistence` at 1400 K, checks that μ_A and μ_B are equal in SOLID and
# LIQUID there (`tp.lens_mu` returns the pair (μ_A, μ_B) of one phase), and checks the
# two melting points. It then draws the lens from 1010 K to 1790 K in 10 K steps:
# above the liquidus everything is LIQUID, below the solidus everything is SOLID,
# and in between a sample splits into a SOLID and a LIQUID whose compositions are
# read off the two edges at the same temperature (the dotted tie line at 1400 K).

# %% cellView="form"
#@title After your attempt: part C, the melting lens
from course.self_study import two_phase_export as tp

x_s, x_l = tp.lens_coexistence(1400.0)   # (solidus, liquidus) at 1400 K
confirm(lens_ends(1400.0)[0], x_s, "Solidus at 1400 K (formula vs course function)", tol=1e-12)
confirm(lens_ends(1400.0)[1], x_l, "Liquidus at 1400 K (formula vs course function)", tol=1e-12)
mu_s, mu_l = tp.lens_mu("SOLID", x_s, 1400.0), tp.lens_mu("LIQUID", x_l, 1400.0)   # (mu_A, mu_B) in each phase
confirm(mu_s[0], mu_l[0], "mu_A equal in SOLID and LIQUID", tol=1e-6)
confirm(mu_s[1], mu_l[1], "mu_B equal in SOLID and LIQUID", tol=1e-6)
confirm(g0("A", "SOLID", 1000.0), g0("A", "LIQUID", 1000.0), "A melts at 1000 K", tol=1e-9)
confirm(g0("B", "SOLID", 1800.0), g0("B", "LIQUID", 1800.0), "B melts at 1800 K", tol=1e-9)

temps = np.arange(1010.0, 1800.0, 10.0)   # K, 1010 … 1790
lens = np.array([(T, *tp.lens_coexistence(T)) for T in temps])   # columns: T, x_SOLID, x_LIQUID
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.plot(lens[:, 2], lens[:, 0], "-", lw=2, label="liquidus (LIQUID composition)")
ax.plot(lens[:, 1], lens[:, 0], "--", lw=2, label="solidus (SOLID composition)")
ax.plot([0, 1], [1000, 1800], "ko", label="pure A and pure B melt")
ax.plot([x_l, x_s], [1400, 1400], "k:|", label="tie line at 1400 K")
ax.text(0.65, 1150, "SOLID", ha="center")     # label placed inside the single-phase SOLID region
ax.text(0.3, 1650, "LIQUID", ha="center")     # label placed inside the single-phase LIQUID region
ax.set(xlabel="B atom fraction x", ylabel="T (K)", title="Ideal SOLID/LIQUID lens", xlim=(0, 1))
ax.legend(fontsize=10, loc="upper left")
plt.show()
print("T (K)   x_LIQUID  x_SOLID")
for T, xs, xl in lens[::10]:              # every tenth row, i.e. every 100 K
    print(f"{T:6.0f}  {xl:.5f}   {xs:.5f}")

# %% [markdown]
# **Limits.** All three models are invented and describe no real alloy. Each is a
# closed bulk sample at fixed T and p with no interfaces, strain or kinetics;
# whether a split actually forms, and how fast, is a different question. A grid
# search gives an upper bound that depends on the grid. Close below T_c the
# course function refuses to report the two compositions rather than guess, and
# the lens uses ideal solutions only. Real diagrams combine several such regions;
# step 05 shows a gap and a lens in Cu–Ni.
#
# Worked answers, after your attempt: the worked answer of self-study step 03
# and Lessons [5](../course/foundations/lesson_05_two_phase.md) and
# [7](../course/foundations/lesson_07_regular_solution.md).
#
# Next: [f4b · one phase diagram from scratch, then with pycalphad](f4b_lens_from_scratch.ipynb)
# (optional: the lens of part C built step by step and handed to pycalphad), or
# straight on to [f5 · binary equilibrium in pycalphad](f5_binary_pycalphad.ipynb).
