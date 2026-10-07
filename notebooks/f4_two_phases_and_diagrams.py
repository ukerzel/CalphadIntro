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

print(f"g_alpha(0.3) = {g_alpha(0.3):.3f} J/mol, g_beta(0.3) = {g_beta(0.3):.3f} J/mol")

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

# %%
def f_beta(z, x_alpha, x_beta):
    return (z - x_alpha) / (x_beta - x_alpha)   # mol BETA atoms per mol atoms

def g_split(z, x_alpha, x_beta):
    fb = f_beta(z, x_alpha, x_beta)
    return (1 - fb) * g_alpha(x_alpha) + fb * g_beta(x_beta)   # J/mol atoms

print(f"endpoints 0.1/0.9 at z = 0.6: f_beta = {f_beta(0.6, 0.1, 0.9):.3f}")

# %% [markdown]
# ### Your turn: split or stay homogeneous? (z = 0.5)
#
# 1. Homogeneous ALPHA at x = 0.5: use q(0.5) = −0.69314718 and RT = 8314.5 J/mol.
# 2. A split with x_α = 0.2 and x_β = 0.8: find f_β from the balance, then the
#    split energy using g_α(0.2) = g_β(0.8) = −10760.596 J/mol.
# 3. How much lower is the split than the homogeneous state (a positive number)?

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

# %%
from scipy.optimize import linprog

points = 5
grid = np.linspace(0.0, 1.0, points)
x_all = np.concatenate([grid, grid])                        # ALPHA points, then BETA points
energies = np.concatenate([g_alpha(grid), g_beta(grid)])    # J/mol atoms
z = 0.5
result = linprog(energies, A_eq=[np.ones_like(x_all), x_all], b_eq=[1.0, z],
                 bounds=(0, None), method="highs")
f = result.x
print("success:", result.success, "| total:", f.sum(), "| B:", f @ x_all, "| A:", f @ (1 - x_all))
for i in np.flatnonzero(f > 0):
    print(f"  {'ALPHA' if i < points else 'BETA'} at x = {x_all[i]:.2f}: f = {f[i]:.3f}")
print(f"grid energy: {result.fun:.3f} J/mol")

# %% [markdown]
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

# %% cellView="form"
#@title After your attempt: the Lesson 5 refinement, 21 → 101 → 501 points
from course.foundations.binary_family import ideal_grid, ideal_equilibrium
T, z = 1000.0, 0.5
reference = ideal_equilibrium(T, z)['GM']
for points in (21, 101, 501):
    state = ideal_grid(T, z, points)
    regions = state['regions']
    total = sum(r['f'] for r in regions)
    B = sum(r['f']*r['x'] for r in regions)
    A = sum(r['f']*(1-r['x']) for r in regions)
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

# %%
OMEGA = 20000.0   # J/mol

def g_mix_regular(x, T):
    return OMEGA * x * (1 - x) + R * T * q(x)   # J/mol atoms

for T in (600.0, 1500.0):
    print(f"{T:.0f} K: mixing part at x = 0.3, 0.4, 0.5:",
          [round(float(g_mix_regular(x, T)), 1) for x in (0.3, 0.4, 0.5)], "J/mol")

# %% [markdown]
# ### Your turn: predict, then compute T_c
#
# As T rises towards T_c, do the two compositions move closer together or
# further apart? Answer with one word, `"together"` or `"apart"`. Then compute
# T_c in kelvin (four significant figures).

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

# %%
from course.foundations.binary_family import regular_binodal
import matplotlib.pyplot as plt

gap_temperatures = []   # K, e.g. 600, 650, ...; your choice
gap_T, gap_left, gap_right = [], [], []
for T in gap_temperatures:
    ends = regular_binodal(T)["compositions"]
    if ends:
        gap_T.append(T)
        gap_left.append(ends[0])
        gap_right.append(ends[1])
if gap_T:
    plt.plot(gap_left, gap_T, "o-", label="B-poor region")
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

# %%
H = {"A": {"SOLID": 1000.0, "LIQUID": 7000.0}, "B": {"SOLID": 2000.0, "LIQUID": 20000.0}}   # J/mol
S = {"A": {"SOLID": 10.0, "LIQUID": 16.0}, "B": {"SOLID": 10.0, "LIQUID": 20.0}}           # J/(mol K)

def g0(element, phase, T):
    return H[element][phase] - T * S[element][phase]   # J/mol of the pure element

def lens_ends(T):
    """(x_SOLID, x_LIQUID) at T in K, or None outside the two-phase range."""
    a = np.exp((g0("A", "SOLID", T) - g0("A", "LIQUID", T)) / (R * T))
    b = np.exp((g0("B", "SOLID", T) - g0("B", "LIQUID", T)) / (R * T))
    if not a > 1 > b:
        return None
    x_solid = (1 - a) / (b - a)
    return x_solid, b * x_solid

print("950 K:", lens_ends(950.0), "| 1850 K:", lens_ends(1850.0))

# %% [markdown]
# ### Your turn: build the lens
#
# Fill the temperatures (K, between 1000 and 1800), run and plot both edges.
# Then give x_S and x_L at 1400 K (four significant figures), and say which
# component the solid is richer in: `"A"` or `"B"`.

# %%
lens_temperatures = []   # K, your choice
lens_T, lens_solid, lens_liquid = [], [], []
for T in lens_temperatures:
    ends = lens_ends(T)
    if ends:
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

best = bf.ideal_equilibrium(1000.0, 0.5)
xa, xb = best["regions"][0]["x"], best["regions"][1]["x"]
mu = bf.ideal_derivatives(1000.0, xa, "ALPHA")
mu_beta = bf.ideal_derivatives(1000.0, xb, "BETA")
confirm(xa, 0.19104, "Best ALPHA composition", tol=1e-5)
confirm(xb, 0.80896, "Best BETA composition", tol=1e-5)
confirm(best["GM"], -10762.730, "Best split energy", tol=1e-3)
confirm(float(mu["mu_A"]), -10762.730, "mu_A in ALPHA", tol=1e-3)
confirm(float(mu_beta["mu_A"]), float(mu["mu_A"]), "mu_A equal in BETA", tol=1e-6)
confirm(float(mu_beta["mu_B"]), float(mu["mu_B"]), "mu_B equal in both phases", tol=1e-6)

x = np.linspace(0.0, 1.0, 201)
tangent = float(mu["mu_A"]) + (float(mu["mu_B"]) - float(mu["mu_A"])) * x
z_show = 0.35
fb = bf.lever_fraction(z_show, xa, xb)
g_at_z = float(mu["mu_A"]) + (float(mu["mu_B"]) - float(mu["mu_A"])) * z_show
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(x, g_alpha(x) / 1000, "-", label="ALPHA")
ax.plot(x, g_beta(x) / 1000, "--", label="BETA")
ax.plot(x, tangent / 1000, ":", color="k", label="common tangent")
ax.plot([xa, xb], [g_alpha(xa) / 1000, g_beta(xb) / 1000], "ko", label="touching points")
ax.plot([xa, z_show], [g_at_z / 1000 - 0.4] * 2, "-|", lw=2, label=f"arm z − x_α → f_β = {fb:.3f}")
ax.plot([z_show, xb], [g_at_z / 1000 - 0.8] * 2, "--|", lw=2, label=f"arm x_β − z → f_α = {1 - fb:.3f}")
ax.axvline(z_show, color="grey", lw=0.8)
ax.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="1000 K: ALPHA, BETA and the common tangent",
       ylim=(-12.5, -2))
ax.legend(fontsize=10, loc="upper center")
plt.show()
print(" x      g_ALPHA (J/mol)  g_BETA (J/mol)")
for xi in (0.1, 0.19104, 0.5, 0.80896, 0.9):
    print(f"{xi:.5f}  {g_alpha(xi):12.3f}  {g_beta(xi):12.3f}")
print(f"z = {z_show} with the best endpoints: f_alpha = {1 - fb:.4f}, f_beta = {fb:.4f}; the vertical line marks z")

# %% cellView="form"
#@title After your attempt: part B, the hump and the gap diagram
confirm(bf.TC_R1, 1202.718143, "T_c = Omega/(2R)", tol=1e-6)
confirm(OMEGA / (2 * R), bf.TC_R1, "T_c from the formula above", tol=1e-9)
ends_600 = bf.regular_binodal(600.0)["compositions"]
confirm(ends_600[0], 0.021032752, "Left composition at 600 K", tol=1e-9)
confirm(ends_600[1], 0.978967248, "Right composition at 600 K", tol=1e-9)
confirm(float(bf.regular_properties(600.0, 0.5)["GM_mix"]), 1542.096660, "Mixing part at x = 0.5, 600 K", tol=1e-6)
confirm(float(g_mix_regular(0.5, 600.0)), 1542.096660, "Same value from the formula above", tol=1e-6)

x_in = np.linspace(0.001, 0.999, 400)
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))
for T, style in ((600.0, "-"), (900.0, "--"), (1100.0, "-."), (1300.0, ":")):
    left.plot(x_in, g_mix_regular(x_in, T) / 1000, style, label=f"{T:.0f} K")
    ends = bf.regular_binodal(T)["compositions"]
    if ends:
        level = float(g_mix_regular(ends[0], T)) / 1000
        left.plot(ends, [level, level], "ko-", ms=4)
left.set(xlabel="B atom fraction x", ylabel="mixing part Δg_mix (kJ/mol atoms)",
         title="Hump and horizontal tangent (black)")
left.legend(fontsize=10)

temps = np.concatenate([np.arange(600.0, 1200.0, 25.0), [1200.0]])
rows = [(T, *bf.regular_binodal(T)["compositions"], *bf.regular_binodal(T)["spinodal"]) for T in temps]
table = np.array(rows)
right.plot(table[:, 1], table[:, 0], "o-", ms=3, label="B-poor region")
right.plot(table[:, 2], table[:, 0], "s--", ms=3, label="B-rich region")
right.plot([0.5], [bf.TC_R1], "k*", ms=10, label=f"T_c ≈ {bf.TC_R1:.0f} K")
right.set(xlabel="B atom fraction x", ylabel="T (K)", title="Miscibility gap (one ALPHA phase)", xlim=(0, 1))
right.legend(fontsize=10)
plt.show()
print("T (K)   x_left    x_right")
for T, xl, xr, *_ in rows[::4]:
    print(f"{T:6.0f}  {xl:.5f}  {xr:.5f}")
print(f"{bf.TC_R1:6.1f}  0.5 (the two compositions meet)")

# %% cellView="form"
#@title After your attempt: part C, the melting lens
from course.self_study import two_phase_export as tp

x_s, x_l = tp.lens_coexistence(1400.0)
confirm(lens_ends(1400.0)[0], x_s, "Solidus at 1400 K (formula vs course function)", tol=1e-12)
confirm(lens_ends(1400.0)[1], x_l, "Liquidus at 1400 K (formula vs course function)", tol=1e-12)
mu_s, mu_l = tp.lens_mu("SOLID", x_s, 1400.0), tp.lens_mu("LIQUID", x_l, 1400.0)
confirm(mu_s[0], mu_l[0], "mu_A equal in SOLID and LIQUID", tol=1e-6)
confirm(mu_s[1], mu_l[1], "mu_B equal in SOLID and LIQUID", tol=1e-6)
confirm(g0("A", "SOLID", 1000.0), g0("A", "LIQUID", 1000.0), "A melts at 1000 K", tol=1e-9)
confirm(g0("B", "SOLID", 1800.0), g0("B", "LIQUID", 1800.0), "B melts at 1800 K", tol=1e-9)

temps = np.arange(1010.0, 1800.0, 10.0)
lens = np.array([(T, *tp.lens_coexistence(T)) for T in temps])
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.plot(lens[:, 2], lens[:, 0], "-", lw=2, label="liquidus (LIQUID composition)")
ax.plot(lens[:, 1], lens[:, 0], "--", lw=2, label="solidus (SOLID composition)")
ax.plot([0, 1], [1000, 1800], "ko", label="pure A and pure B melt")
ax.plot([x_l, x_s], [1400, 1400], "k:|", label="tie line at 1400 K")
ax.text(0.65, 1150, "SOLID", ha="center")
ax.text(0.3, 1650, "LIQUID", ha="center")
ax.set(xlabel="B atom fraction x", ylabel="T (K)", title="Ideal SOLID/LIQUID lens", xlim=(0, 1))
ax.legend(fontsize=10, loc="upper left")
plt.show()
print("T (K)   x_LIQUID  x_SOLID")
for T, xs, xl in lens[::10]:
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
# Next: [f5 · binary equilibrium in pycalphad](f5_binary_pycalphad.ipynb).
