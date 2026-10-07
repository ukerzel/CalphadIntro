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
# # f3 · Binary mixtures: composition, ideal mixing and chemical potentials
#
# **Learning question:** when a second invented component B joins A in one phase,
# how do we count the atoms, what does mixing add to the Gibbs energy, and what do
# the chemical potentials μ_A and μ_B tell us?
#
# Used in: Day 2 D1–D3, Lessons 3, 4 and 6, self-study step 02.
# Work each "your turn" on paper first, then type your value. Give numbers to at
# least four significant figures, or type the arithmetic itself and let Python
# evaluate it.

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
# ## 1. Composition and conserved amounts (D1, Lesson 3)
#
# Two invented atom species A and B. All amounts are moles of **atoms**. The B atom
# fraction is $x_B = n_B/(n_A + n_B)$ and $x_A = 1 - x_B$; both are dimensionless.
# A ratio such as $n_B/n_A$ is something else: its denominator is not the total.
#
# A **phase amount fraction** f says how much of the sample is in a region; a
# **phase composition** x says how B-rich that region is; the **overall composition**
# z counts B in the whole sample. For two regions,
# $f_1 + f_2 = 1$ and $z = f_1 x_1 + f_2 x_2$ (B balance); the A balance is
# $f_1(1 - x_1) + f_2(1 - x_2) = 1 - z$. A balanced split only checks the amounts;
# it does not show that the two regions are in equilibrium.

# %%
n_A, n_B = 3.0, 1.0                 # mol of atoms
x_B = n_B / (n_A + n_B)             # B atom fraction
print(f"x_B = {x_B:.2f}, x_A = {1 - x_B:.2f}, ratio n_B/n_A = {n_B / n_A:.4f}")

# D1 worked count: two regions, half the atoms in each
f1, f2 = 0.5, 0.5                   # phase amount fractions
x1, x2 = 0.10, 0.50                 # B fraction inside each region
z = f1 * x1 + f2 * x2               # overall B fraction
a_balance = f1 * (1 - x1) + f2 * (1 - x2)
print(f"z = {z:.2f}, A balance = {a_balance:.2f}, sum = {z + a_balance:.2f}")

# %% [markdown]
# ### Your turn (D1, step 02)
#
# 1. For nA = 0.6 mol and nB = 0.4 mol, give the amount ratio nB/nA (as a fraction
#    typed as a division, or to four significant figures).
# 2. For 2 mol of atoms at z = 0.20, find n_B and n_A.
# 3. With x1 = 0.10, x2 = 0.50 and z = 0.20, find f2 from the B balance, then check
#    the A balance: f1(1 − x1) + f2(1 − x2).
#
# "The ALPHA composition x = 0.20 means 20 % of the sample's area is ALPHA."
# What information is missing to talk about area?

# %%
ratio_nB_nA = None   # dimensionless
n_B_2mol = None      # mol
n_A_2mol = None      # mol
f2_trial = None      # phase amount fraction of region 2
A_balance = None     # A fraction of the whole sample
check(ratio_nB_nA, "f3_ratio_nb_na")
check(n_B_2mol, "f3_nb_2mol")
check(n_A_2mol, "f3_na_2mol")
check(f2_trial, "f3_f2_trial")
check(A_balance, "f3_a_balance")

# %% [markdown]
# ### Atom fraction is not mass fraction
#
# Mass and amount are linked by the molar mass: m = nM (grams with g/mol). For this
# exercise only, take **invented** molar masses M_A = 20 g/mol and M_B = 80 g/mol.
# For 3 mol A + 1 mol B:

# %%
M_A, M_B = 20.0, 80.0               # g/mol, invented
m_A, m_B = n_A * M_A, n_B * M_B     # g
w_B = m_B / (m_A + m_B)             # B mass fraction
print(f"m_A = {m_A:.0f} g, m_B = {m_B:.0f} g, w_B = {w_B:.6f}, but x_B = {x_B:.2f}")

# %% [markdown]
# Lesson 3's two-box inventory, same invented masses:
#
# | Box | A (mol) | B (mol) |
# |---|---:|---:|
# | α | 0.45 | 0.05 |
# | β | 0.30 | 0.20 |
#
# ### Your turn
#
# 1. A sample has 40 g A and 40 g B, so w_B = 0.5. What is x_B?
# 2. What fraction of the total **mass** is in β? (Its amount fraction is 0.5, its
#    B fraction 0.4; neither is the answer.) Give it as a fraction typed as a
#    division, or to four significant figures.

# %%
x_B_40g = None             # dimensionless
beta_mass_fraction = None  # dimensionless
check(x_B_40g, "f3_xb_40g")
check(beta_mass_fraction, "f3_beta_mass_fraction")

# %% [markdown]
# ### Your turn: units and amount basis
#
# Supplied value: one model gives g_b = −10502.902 J/mol atoms at x = 0.10. Another
# report gives −10.50 **kJ/mol** at the same x.
#
# 1. Convert, then give the size of the difference in J/mol (a positive number).
#    Does the rounding to 0.01 kJ/mol explain it?
# 2. What is the total G, in J, of 2 mol of atoms at x = 0.10? (Multiply J/mol by
#    moles, never by an atom count.)

# %%
kJ_report_gap = None   # J/mol
G_2mol_x010 = None     # J
check(kJ_report_gap, "f3_kj_gap")
check(G_2mol_x010, "f3_g_2mol_x010")

# %% [markdown]
# ## 2. Ideal mixing (D2, Lesson 4)
#
# One invented phase, ALPHA, at T = 1000 K and p = 100000 Pa, per mole of atoms.
# The pure endmembers have $g_A = -9000$ and $g_B = 3000$ J/mol, so the
# **reference line** is $-9000 + 12000x$. Ideal mixing adds $RT\,q(x)$ with
# R = 8.3145 J/(mol K), RT = 8314.5 J/mol and natural logarithms:
#
# $$q(x) = (1-x)\ln(1-x) + x\ln x,\qquad g_b(x) = -9000 + 12000x + 8314.5\,q(x).$$
#
# The ideal enthalpy **of mixing** is zero, yet the mixing Gibbs energy is negative
# for 0 < x < 1. At a pure end use the limit $0\ln 0 = 0$: then q = 0. Never ask a
# computer for ln 0; `scipy.special.xlogy(x, x)` returns the limit 0 at x = 0.

# %%
import numpy as np
from scipy.special import xlogy

RT = 8314.5   # J/mol at 1000 K

def q_mix(x):
    return xlogy(1 - x, 1 - x) + xlogy(x, x)   # dimensionless, 0 at x = 0 and 1

def g_reference(x):
    return -9000.0 + 12000.0 * x               # J/mol atoms

def g_mixing(x):
    return RT * q_mix(x)                       # J/mol atoms

def g_b(x):
    return g_reference(x) + g_mixing(x)        # J/mol atoms

with np.errstate(divide="ignore", invalid="ignore"):
    print("naive 0 * ln(0) =", np.float64(0.0) * np.log(np.float64(0.0)), " ← not a number")
print("xlogy(0, 0)     =", xlogy(0.0, 0.0))

x_demo = 0.10   # D2 worked example
print(f"x = {x_demo}: q = {q_mix(x_demo):.8f}, reference = {g_reference(x_demo):.3f}, "
      f"mixing = {g_mixing(x_demo):.3f}, g_b = {g_b(x_demo):.3f} J/mol atoms")

# %% [markdown]
# ### Your turn (D2, step 02)
#
# At x = 0.20, use q(0.20) = −0.50040242 to find the reference term, the mixing term
# and g_b, in J/mol atoms. Why is g_b not just 0.8 g_A + 0.2 g_B?
# Then: what is g_b at the pure-B end, x = 1?

# %%
reference_020 = None   # J/mol atoms
mixing_020 = None      # J/mol atoms
g_b_020 = None         # J/mol atoms
g_b_pure_B = None      # J/mol atoms
check(reference_020, "f3_ref_020")
check(mixing_020, "f3_mix_020")
check(g_b_020, "f3_gb_020")
check(g_b_pure_B, "f3_gb_pure_b")

# %% [markdown]
# ### Lesson 4's table in code
#
# This is the Lesson 4 cell with one change: its x = 0.2 and x = 0.8 rows contain
# your answers above, so they are left out here and printed after your attempt. Each row is x, g_ref, Δg_mix,
# total g (J/mol), total h (J/mol), total s (J/(mol K)). The rows are **different
# samples**, not regions of one sample.

# %%
from scipy.special import xlogy

T = 1000.0
R = 8.3145
x = np.array([0.0, 0.5, 1.0])
h = 1000.0 + 12000.0*x
gref = h - 10.0*T
q = xlogy(x, x) + xlogy(1-x, 1-x)
smix = -R*q
gmix = -T*smix
for row in zip(x, gref, gmix, gref+gmix, h, 10+smix):
    print(' '.join(f'{v:.6f}' for v in row))

central, pure_A = 1, 0
confirm((gref + gmix)[central], -8763.172233, "Total g at x = 0.5", tol=1e-6)
confirm(gmix[central], -5763.172233, "Mixing term at x = 0.5", tol=1e-6)
confirm((10 + smix)[central], 15.763172, "Total s at x = 0.5", tol=1e-6)
confirm((gref + gmix)[pure_A], -9000.0, "Pure-A row: total g", tol=1e-9)
confirm(gmix[pure_A], 0.0, "Pure-A row: no mixing term", tol=1e-12)

# %% [markdown]
# ## 3. Chemical potentials and the tangent (D3, Lesson 6)
#
# The chemical potential μ_B is the change of total G when a little B is **added**
# with n_A fixed (μ_A likewise with n_B fixed). On a filled set of sites, putting in
# one B means taking out one A, so an **exchange** changes G by μ_B − μ_A, the slope
# of the molar curve:
#
# $$g_b' = \mu_B - \mu_A,\qquad \mu_A = g_b - x\,g_b',\qquad \mu_B = g_b + (1-x)\,g_b'.$$
#
# For this ideal ALPHA, inside 0 < x < 1:
#
# $$\mu_A = -9000 + 8314.5\ln(1-x),\qquad \mu_B = 3000 + 8314.5\ln x,\qquad
# g_b' = 12000 + 8314.5\ln\frac{x}{1-x}.$$
#
# The **tangent** at x0 is $\ell(x) = g_b(x_0) + g_b'(x_0)(x - x_0)$. At x = 0 it
# equals μ_A, at x = 1 it equals μ_B: the two ends of one tangent hold both
# chemical potentials. These are ends of a straight line, not g_b(0) or g_b(1).
# Derivatives exist only inside the interval, so x = 0 and x = 1 are excluded.

# %%
def mu_A(x):
    return -9000.0 + RT * np.log(1 - x)        # J/mol atoms, 0 < x < 1

def mu_B(x):
    return 3000.0 + RT * np.log(x)             # J/mol atoms

def slope(x):
    return 12000.0 + RT * np.log(x / (1 - x))  # g_b' = mu_B − mu_A, J/mol atoms

def tangent(x, x0):
    return g_b(x0) + slope(x0) * (x - x0)      # J/mol atoms

for x0 in (0.10, 0.50):
    print(f"x0 = {x0}: mu_A = {mu_A(x0):.3f}, mu_B = {mu_B(x0):.3f}, "
          f"mu_B − mu_A = {mu_B(x0) - mu_A(x0):.3f}, slope = {slope(x0):.3f} J/mol atoms")
    print(f"   tangent at x = 0: {tangent(0.0, x0):.3f}, at x = 1: {tangent(1.0, x0):.3f}; "
          f"(1 − x) mu_A + x mu_B = {(1 - x0) * mu_A(x0) + x0 * mu_B(x0):.3f} = g_b = {g_b(x0):.3f}")

# %% [markdown]
# ### Addition is not exchange: Lesson 6's finite differences
#
# Lesson 6's cell, written here with the g_b defined above, builds the total
# G(n_A, n_B) = n g_b(x) and changes the amounts directly at n_A = n_B = 0.5 mol. "Addition" adds B with A fixed (an estimate of
# μ_B); "exchange" swaps A for B at fixed total (an estimate of g_b'). Columns: step
# h (mol), addition (J/mol), exchange (J/mol). Predict both signs first.

# %%
def total_G(nA, nB):
    n = nA + nB                     # mol of atoms
    return n * g_b(nB / n)          # J

for h in (1e-3, 1e-4, 1e-5, 1e-6):
    addition = (total_G(.5, .5+h)-total_G(.5, .5-h))/(2*h)
    exchange = (total_G(.5-h, .5+h)-total_G(.5+h, .5-h))/(2*h)
    print(f'{h:.0e} {addition:.6f} {exchange:.6f}')

# %%
for step in (1e-5, 1e-6):
    addition = (total_G(.5, .5 + step) - total_G(.5, .5 - step)) / (2 * step)
    exchange = (total_G(.5 - step, .5 + step) - total_G(.5 + step, .5 - step)) / (2 * step)
    confirm(addition, -2763.172233, f"Addition estimate of mu_B (h = {step:.0e} mol)", tol=1e-3)
    confirm(exchange, 12000.0, f"Exchange estimate of the slope (h = {step:.0e} mol)", tol=1e-3)

# %% [markdown]
# ### Your turn (D3, step 02)
#
# 1. At x = 0.20, use ln(0.20/0.80) = −1.38629436 to find the exchange slope g_b'.
#    Is it positive or negative? Then compute μ_A and μ_B at x = 0.20.
# 2. Take the tangent at x0 = 0.5. What is its value at x = 0.8?
# 3. Find the slope at x = 0.19. Between which two compositions on a 0.01 grid does
#    the slope change sign? Solve g_b' = 0 for x exactly.
# 4. The slope changes sign somewhere between the pure ends. Does that mean two
#    phases form? Write one sentence before you open the next section.

# %%
slope_020 = None          # J/mol atoms
mu_A_020 = None           # J/mol atoms
mu_B_020 = None           # J/mol atoms
tangent_05_at_08 = None   # J/mol atoms
slope_019 = None          # J/mol atoms
x_zero_slope = None       # dimensionless
check(slope_020, "f3_slope_020")
check(mu_A_020, "f3_mua_020")
check(mu_B_020, "f3_mub_020")
check(tangent_05_at_08, "f3_tangent_05_at_08")
check(slope_019, "f3_slope_019")
check(x_zero_slope, "f3_x_zero_slope")

# %% [markdown]
# ## After your attempt: the course code and the plots
#
# Run these two cells once you have your own answers. The first repeats the step 02
# and lesson numbers with `course.foundations.binary_family` and answers the
# two-phase question; the second draws the curves.

# %% cellView="form"
#@title After your attempt: run to check the numbers with the course code
import math
from course.foundations import binary_family as bf

print("Step 02, worked answer: at x = 0.20 the reference is −6600, the mixing term about −4160.596\n"
      "and g_b about −10760.596 J/mol atoms; the exchange slope is about +473.656 J/mol atoms.\n"
      "Two moles at z = 0.20 hold 0.40 mol B and 1.60 mol A. The slope changes sign between\n"
      "x = 0.19 (about −56) and 0.20 (about +474): that is the lowest point of this one curve.\n"
      "It is not two phases forming. Only ALPHA was allowed, and a closed sample's composition\n"
      "is fixed by its amounts of A and B, so it stays homogeneous at that composition.\n"
      "Comparing two phases needs a second curve and a common tangent: that is f4.\n")
T = 1000.0   # K
props = bf.ideal_properties(T, 0.20)
deriv = bf.ideal_derivatives(T, 0.20)
print(f"x = 0.20: reference {float(props['GM_reference']):.3f}, mixing {float(props['GM_mix']):.3f}, "
      f"g_b {float(props['GM']):.3f}, slope {float(deriv['slope']):.3f}, "
      f"mu_A {float(deriv['mu_A']):.3f}, mu_B {float(deriv['mu_B']):.3f} J/mol atoms")
confirm(float(props["GM_reference"]), -6600.0, "Step 02: reference at x = 0.20", tol=1e-6)
confirm(float(props["GM_mix"]), -4160.596, "Step 02: mixing term at x = 0.20", tol=1e-3)
confirm(float(props["GM"]), -10760.596, "Step 02: g_b at x = 0.20", tol=1e-3)
confirm(float(deriv["slope"]), 473.656, "Step 02: exchange slope at x = 0.20", tol=1e-3)
confirm(2 * 0.20, 0.40, "Step 02: mol B in 2 mol at z = 0.20", tol=1e-12)
confirm(bf.lever_fraction(0.20, 0.10, 0.50), 0.25, "D1: f2 for the balanced trial", tol=1e-12)

grid = np.round(np.arange(1, 100) / 100, 2)
grid_slope = bf.ideal_derivatives(T, grid)["slope"]
first_positive = int(np.argmax(grid_slope > 0))
print(f"sign change between x = {grid[first_positive - 1]:.2f} ({grid_slope[first_positive - 1]:.1f}) "
      f"and x = {grid[first_positive]:.2f} ({grid_slope[first_positive]:.1f}) J/mol atoms")
confirm(grid[first_positive - 1], 0.19, "Step 02: last negative slope on the 0.01 grid", tol=1e-12)
confirm(float(grid_slope[first_positive - 1]), -56.0, "Step 02: slope at x = 0.19 (about −56)", tol=0.5)
confirm(1 / (1 + math.exp(12000 / RT)), 0.191040753, "Lesson 6: zero of the ALPHA slope", tol=1e-9)

for x0 in (0.10, 0.20, 0.50):
    d = bf.ideal_derivatives(T, x0)
    confirm(float(d["mu_A"]), mu_A(x0), f"mu_A formula at x = {x0}", tol=1e-6)
    confirm(float(d["mu_B"]), mu_B(x0), f"mu_B formula at x = {x0}", tol=1e-6)
    confirm(tangent(0.0, x0), float(d["mu_A"]), f"Tangent at x = 0 is mu_A (x0 = {x0})", tol=1e-6)
    confirm(tangent(1.0, x0), float(d["mu_B"]), f"Tangent at x = 1 is mu_B (x0 = {x0})", tol=1e-6)

d10 = bf.ideal_derivatives(T, 0.10)
confirm(float(bf.ideal_properties(T, 0.10)["GM"]), -10502.902, "D2: g_b at x = 0.10", tol=1e-3)
confirm(float(d10["mu_A"]), -9876.020, "D3: mu_A at x = 0.10", tol=1e-3)
confirm(float(d10["mu_B"]), -16144.844, "D3: mu_B at x = 0.10", tol=1e-3)
confirm(float(d10["slope"]), -6268.824, "D3: mu_B − mu_A at x = 0.10", tol=1e-3)
d50 = bf.ideal_derivatives(T, 0.50)
confirm(float(d50["mu_A"]), -14763.172233, "Lesson 6: mu_A at x = 0.5", tol=1e-6)
confirm(float(d50["mu_B"]), -2763.172233, "Lesson 6: mu_B at x = 0.5", tol=1e-6)
confirm(float(d50["slope"]), 12000.0, "Lesson 6: slope at x = 0.5", tol=1e-9)
confirm(tangent(0.8, 0.5), -5163.172233, "Lesson 6: tangent at x0 = 0.5, read at x = 0.8", tol=1e-6)

print("\nLesson 4's full cell, now with its x = 0.2 row (x, g_ref, Δg_mix, g, h, s):")
full = bf.ideal_properties(T, np.array([0.0, 0.2, 0.5, 0.8, 1.0]))
for row in zip([0.0, 0.2, 0.5, 0.8, 1.0], full["GM_reference"], full["GM_mix"], full["GM"], full["HM"], full["SM"]):
    print(' '.join(f'{v:.6f}' for v in row))
confirm(float(full["GM"][2]), -8763.172233, "Lesson 4: central row with the course module", tol=1e-6)
confirm(float(full["GM"][1]), -10760.596, "Lesson 4: total g at x = 0.2", tol=1e-3)

# %% cellView="form"
#@title After your attempt: plot the curve, a tangent and the chemical potentials
import matplotlib.pyplot as plt

x0 = 0.20   # composition of the tangent; change it (0 < x0 < 1) and run again
plt.rcParams.update({"font.size": 12})
x_all = np.linspace(0.0, 1.0, 201)       # pure ends included: 0 ln 0 = 0
x_in = np.linspace(0.01, 0.99, 99)       # derivatives: interior only
fig, (left, middle, right) = plt.subplots(1, 3, figsize=(15, 4.4))

left.plot(x_all, g_b(x_all) / 1000, "-", lw=2, label="g_b (total)")
left.plot(x_all, g_reference(x_all) / 1000, "--", label="reference −9000 + 12000x")
left.plot(x_all, g_mixing(x_all) / 1000, ":", lw=2.5, label="mixing term RT q(x)")
left.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="ALPHA at 1000 K")
left.legend(fontsize=10)

middle.plot(x_all, g_b(x_all) / 1000, "-", lw=2, label="g_b")
middle.plot([0, 1], [tangent(0.0, x0) / 1000, tangent(1.0, x0) / 1000], "--", label=f"tangent at x0 = {x0}")
middle.plot([x0], [g_b(x0) / 1000], "o", ms=8, label="touching point")
middle.plot([0], [mu_A(x0) / 1000], "s", ms=9, label="x = 0: μ_A")
middle.plot([1], [mu_B(x0) / 1000], "^", ms=9, label="x = 1: μ_B")
middle.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="Tangent ends are μ_A and μ_B")
middle.legend(fontsize=10)

right.plot(x_in, mu_A(x_in) / 1000, "-", label="μ_A")
right.plot(x_in, mu_B(x_in) / 1000, "--", label="μ_B")
right.plot(x_in, slope(x_in) / 1000, "-.", marker="o", markevery=10, label="slope μ_B − μ_A")
right.axhline(0, color="grey", lw=0.8)
right.set(xlabel="B atom fraction x", ylabel="kJ/mol atoms", title="Chemical potentials and slope")
right.legend(fontsize=10)
fig.tight_layout()
plt.show()

print(f"tangent at x0 = {x0}: mu_A = {mu_A(x0):.3f}, mu_B = {mu_B(x0):.3f}, slope = {slope(x0):.3f} J/mol atoms")
print(f"{'x':>5} {'reference':>10} {'mixing':>10} {'g_b':>11} {'mu_A':>11} {'mu_B':>11} {'slope':>10}   (J/mol atoms)")
for xv in (0.01, 0.10, 0.19, 0.20, 0.50, 0.80, 0.99):
    print(f"{xv:5.2f} {g_reference(xv):10.1f} {g_mixing(xv):10.1f} {g_b(xv):11.1f} "
          f"{mu_A(xv):11.1f} {mu_B(xv):11.1f} {slope(xv):10.1f}")

# %% [markdown]
# **Limits.** A and B and the ALPHA phase are invented, with ideal mixing only; the
# numbers say nothing about a real alloy. Only one phase is allowed, so nothing here
# compares phases or finds an equilibrium between them: the lowest point of g_b is
# not the composition a closed sample takes, and a sign change of the slope is not a
# phase transition. Chemical potentials and slopes exist only for 0 < x < 1.
#
# Worked answers, after your attempt: [Day 2 answers](../course/primer_day2/answers.md)
# (D1–D3), the worked answer of self-study step 02, and Lessons
# [3](../course/foundations/lesson_03_composition.md),
# [4](../course/foundations/lesson_04_ideal_mixing.md) and
# [6](../course/foundations/lesson_06_chemical_potential.md).
#
# Next: [f4 · two phases and phase diagrams](f4_two_phases_and_diagrams.ipynb).
