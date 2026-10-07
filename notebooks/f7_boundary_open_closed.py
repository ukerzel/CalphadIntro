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
# # f7 · A grain boundary in an open or closed cell
#
# **Learning question:** an invented boundary prefers B atoms. How much B does it
# take up, where do those atoms come from, and does the answer change when the
# cell can exchange atoms with a large reservoir or is closed?
#
# Used in: Day 2 D4–D6 and D9, Lessons 11–13, self-study step 04.
# Work each "your turn" on paper first, then type your value.
#
# **Background.** A grain boundary is the thin region where two crystals of
# different orientation meet. Atoms there sit in a less regular environment than
# in the bulk crystal, so some kinds of atoms are more comfortable there. When the
# boundary takes up more B than the bulk has, B is said to **segregate** to the
# boundary. Segregation changes boundary properties, and it is one of the uses of
# CALPHAD-type bulk descriptions beyond phase diagrams.
#
# **The route through the notebook.**
#
# 1. Counting: sites, atoms and the boundary **excess** (how much extra B the
#    boundary holds), before any energy appears.
# 2. **Open cell:** the bulk is connected to a very large reservoir, so its
#    composition stays fixed. A closed formula gives the boundary occupancy.
# 3. **Closed cell:** the total number of B atoms is fixed, so B that goes to the
#    boundary is missing from the bulk. The answer is found step by step.
# 4. Practice with fresh numbers, then the course code and pictures for both cells.
#
# Run the setup cell first; it makes the helpers `check` and `confirm` available.

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
# ## 1. Count the boundary before giving it an energy (D4, Lesson 11)
#
# An invented A/B model at T = 1000 K and p = 100000 Pa. The periodic cell has a
# bulk region and **two equivalent planar boundaries**. Every site holds exactly
# one A or one B atom.
#
# | Quantity | Value | Unit |
# |---|---:|---|
# | bulk sites $N_b$ | 8000 | sites |
# | boundaries $K$ | 2 | — |
# | sites per boundary $S$ | 100 | sites |
# | area per boundary $A$ | 20 | nm² |
# | bulk B fraction $x_b$ | 0…1 | B per bulk site |
# | boundary occupancy $\theta$ | 0…1 | B per boundary site |
#
# So the cell has 8000 + 200 = 8200 sites and 40 nm² of boundary. Counts such as
# $8000\,x_b$ are expected (average) counts and need not be whole numbers.
#
# "Periodic" means the cell repeats itself in every direction, as in a computer
# simulation; that is why a slab of bulk between two boundaries gives exactly two
# equivalent boundaries. The occupancy $\theta$ (Greek "theta") is the fraction of
# boundary sites that hold B; $x_b$ is the same for the bulk sites.
#
# Occupancy $\theta$ is a fraction; it has no area in it. The **equal-site excess**
# compares the cell with bulk material of fraction $x_b$ filling the same 8200
# sites:
#
# $$\Gamma_B=\frac{8000x_b+200\theta-8200x_b}{40\ \mathrm{nm^2}}
# =\frac{S(\theta-x_b)}{A}=5(\theta-x_b)\ \mathrm{atom/nm^2}.$$
#
# For mol/m²: $1\ \mathrm{nm^2}=10^{-18}\ \mathrm{m^2}$ and one mole is
# $N_{\rm Av}=6.02214076\times10^{23}$ atoms.
#
# Reading the formula term by term: the numerator is (B atoms actually in the
# cell) minus (B atoms the same 8200 sites would hold if they all had the bulk
# fraction). That difference is the extra B that exists *because* of the
# boundaries. Dividing by the boundary area makes it a property of the boundary
# per unit area, so it does not depend on how large the cell is. The simplification
# to $5(\theta-x_b)$ uses $200=2\cdot100$ boundary sites and $40=2\cdot20$ nm²; the
# 5 is the site density of a boundary, 100 sites per 20 nm².
#
# The code turns this into two small functions. `K, S = 2, 100` assigns two names in
# one line. Python writes $6.02214076\times10^{23}$ as `6.02214076e23`.

# %%
N_BULK = 8000          # bulk sites
K, S = 2, 100          # boundaries; sites per boundary
AREA_NM2 = 20.0        # nm² per boundary
N_AV = 6.02214076e23   # atoms per mol
N_SITES = N_BULK + K * S        # all cell sites
AREA_TOTAL_NM2 = K * AREA_NM2   # nm² of boundary in the cell

def excess_atoms_per_nm2(theta, x_b):
    cell_B = N_BULK * x_b + K * S * theta   # expected B atoms in the cell
    reference_B = N_SITES * x_b             # same sites, all at bulk fraction
    return (cell_B - reference_B) / AREA_TOTAL_NM2   # extra B per nm² of boundary

def atoms_per_nm2_to_mol_per_m2(value):
    return value * 1e18 / N_AV   # 1 m² = 1e18 nm²; N_AV atoms per mol

# Lesson 11 worked inventory: supplied trial occupancies, not an equilibrium.
x_b, theta = 0.10, 0.25
print(f"bulk B = {N_BULK * x_b:.0f}, boundary B = {K * S * theta:.0f}, "
      f"reference B = {N_SITES * x_b:.0f}")
gamma = excess_atoms_per_nm2(theta, x_b)   # atom/nm²
print(f"excess = {gamma:.2f} atom/nm² (site-density route: {S / AREA_NM2 * (theta - x_b):.2f})")
print(f"       = {atoms_per_nm2_to_mol_per_m2(gamma):.4e} mol/m²")   # .4e: scientific notation, 4 decimals

# %% [markdown]
# The printout follows the formula: 800 B in the bulk, 50 on the boundaries,
# 820 in the reference, so 30 extra B over 40 nm², and the short route
# $5(\theta-x_b)$ gives the same number. In mol/m² the excess is a very small
# number, because one mole is about $6\times10^{23}$ atoms.
#
# ### Your turn
#
# The worksheet trial is $x_b=0.10$, $\theta=0.15$: 800 B in bulk, 30 B on both
# boundaries, an excess of ten B over 40 nm², so 0.25 atom/nm² (not 30/20).
#
# 1. Total A atoms in the cell for this trial (check that A + B = 8200).
# 2. The excess when $\theta=x_b$.
# 3. The excess at $\theta=0.08$, $x_b=0.10$. Does a negative excess mean a
#    negative number of B atoms?
# 4. Units drill: convert 0.25 atom/nm² to mol/m².
#
# Every site holds exactly one atom, so on any group of sites the number of A atoms
# is the number of sites minus the number of B atoms. You may call the two
# functions above, e.g. `excess_atoms_per_nm2(0.08, 0.10)`, to check your hand
# result.

# %%
total_A_trial = None       # A atoms in the whole cell
excess_theta_eq_x = None   # atom/nm²
excess_theta_008 = None    # atom/nm²
excess_025_mol_m2 = None   # mol/m²
check(total_A_trial, "f7_d4_total_A")
check(excess_theta_eq_x, "f7_d4_excess_equal")
check(excess_theta_008, "f7_d4_excess_008")
check(excess_025_mol_m2, "f7_d4_mol_m2_025")

# %% [markdown]
# Counting is done; now the boundary gets an energy, which decides how much B it
# actually takes up. The first case is the simpler one: the bulk is so large that
# the boundary cannot change its composition.
#
# ## 2. Open cell: a large reservoir sets the bulk (D5, Lesson 12)
#
# A very large ALPHA bulk reservoir fixes $x_b$ and both chemical potentials
# $\mu_A$, $\mu_B$. When a B arrives at a boundary site it replaces an A, which
# goes back to the reservoir; the cell alone does not keep a fixed B count.
#
# The bulk Gibbs energy is the ideal ALPHA curve from Day 2 (J/mol of sites,
# $RT = 8.3145\times1000 = 8314.5$ J/mol):
#
# $$g_b(x)=-9000+12000\,x+RT\,[x\ln x+(1-x)\ln(1-x)].$$
#
# The invented boundary-site function adds a B preference $\delta$:
# $g_s(\theta)=g_b(\theta)+\delta\theta$ with $\delta=-5000$ J/mol of boundary
# sites. The open boundary minimises the grand potential per mole of boundary
# sites, subtracting **both** reservoirs:
#
# $$\phi(\theta)=g_s(\theta)-(1-\theta)\mu_A-\theta\mu_B .$$
#
# **What the symbols mean.** $g_b(x)$ is the ALPHA curve of f3–f5 at 1000 K:
# $-9000+12000\,x$ are the weighted pure-element energies ($(1-x)(-9000)+x(3000)$),
# and the $RT[\dots]$ term is the ideal mixing. The **chemical potential** $\mu_B$
# is the Gibbs energy change when one mole of B is added to the reservoir (in
# J/mol); likewise $\mu_A$. For this curve they are
#
# $$\mu_A=-9000+RT\ln(1-x_b),\qquad \mu_B=-9000+12000+RT\ln x_b ,$$
#
# the two ends (at x = 0 and x = 1) of the tangent line to $g_b$ at $x_b$, as in f3.
#
# The sign of $\delta$: a **negative** $\delta$ lowers the boundary energy more the
# more B it holds, so the boundary prefers B. $\delta=0$ would make a boundary site
# exactly like a bulk site.
#
# **Why $\phi$ and not $g_s$.** The boundary does not create its atoms; it takes
# them from the reservoir. Filling the boundary sites with $(1-\theta)$ mol A and
# $\theta$ mol B removes atoms whose Gibbs energy in the reservoir is
# $(1-\theta)\mu_A+\theta\mu_B$. $\phi$ is the energy of the boundary sites minus
# what those atoms would have had in the reservoir, so it is the net change for the
# whole system. With the reservoir fixed, the stable $\theta$ is the one with the
# lowest $\phi$.
#
# **Where the odds formula comes from.** At the minimum, moving one more B onto a
# boundary site (and one A off it) gains nothing against the reservoir:
# $d\phi/d\theta = g_s'(\theta)-(\mu_B-\mu_A)=0$. With
# $g_s'(\theta)=12000+RT\ln\frac{\theta}{1-\theta}+\delta$ and
# $\mu_B-\mu_A=g_b'(x_b)=12000+RT\ln\frac{x_b}{1-x_b}$, the 12000 cancels:
#
# $$\frac{\theta}{1-\theta}=\frac{x_b}{1-x_b}\,\exp(-\delta/RT),
# \qquad \exp(5000/8314.5)=1.82459687 .$$
#
# If the odds are $r$, then $\theta=r/(1+r)$.
#
# The steps in between: the derivative of the mixing term is
# $\frac{d}{dx}[x\ln x+(1-x)\ln(1-x)]=\ln x-\ln(1-x)=\ln\frac{x}{1-x}$. Setting the
# two derivatives equal and cancelling 12000 leaves
# $RT\ln\frac{\theta}{1-\theta}+\delta=RT\ln\frac{x_b}{1-x_b}$; divide by RT and
# take the exponential of both sides. The ratio $\theta/(1-\theta)$ is called the
# **odds** (B against A on a site). Solving $\theta/(1-\theta)=r$ for $\theta$ gives
# $\theta=r(1-\theta)$, so $\theta=r/(1+r)$.
#
# In the code, `np.log` is the natural logarithm ln and `np.exp` the exponential.
# A function argument written `delta=DELTA` has a default value: `phi(0.15, 0.10)`
# uses δ = −5000 J/mol, and `phi(0.15, 0.10, delta=0.0)` overrides it.

# %%
import numpy as np

RT = 8.3145 * 1000.0   # J/mol at T = 1000 K
DELTA = -5000.0        # J/mol boundary sites

def g_bulk(x):
    return -9000.0 + 12000.0 * x + RT * (x * np.log(x) + (1 - x) * np.log(1 - x))   # J/mol sites, 0 < x < 1

def mu_A(x_b):
    return -9000.0 + RT * np.log(1 - x_b)             # J/mol

def mu_B(x_b):
    return -9000.0 + 12000.0 + RT * np.log(x_b)       # J/mol

def g_site(theta, delta=DELTA):
    return g_bulk(theta) + delta * theta              # J/mol boundary sites

def phi(theta, x_b, delta=DELTA):
    # grand potential: boundary energy minus the reservoir energy of the same atoms, J/mol boundary sites
    return g_site(theta, delta) - (1 - theta) * mu_A(x_b) - theta * mu_B(x_b)

def theta_open(x_b, delta=DELTA):
    odds = x_b / (1 - x_b) * np.exp(-delta / RT)   # bulk odds times the preference factor
    return odds / (1 + odds)                       # from odds r to occupancy θ = r/(1 + r)

print(f"factor exp(-δ/RT) = {np.exp(-DELTA / RT):.8f}")
print(f"reservoir at x_b = 0.10: μ_A = {mu_A(0.10):.2f}, μ_B = {mu_B(0.10):.2f}, "
      f"μ_B − μ_A = {mu_B(0.10) - mu_A(0.10):.2f} J/mol")
for trial in (0.10, 0.15, 0.25):   # Lesson 12 trials: compare, do not yet minimise
    print(f"  trial θ = {trial:.2f}: φ = {phi(trial, 0.10):8.2f} J/mol boundary sites")

# %% [markdown]
# Of these three trials 0.15 is lowest, but three trials do not locate the
# minimum. φ is in J/mol of **boundary sites** and depends on the chosen
# reference; it is not an absolute grain-boundary free energy.
#
# ### Your turn
#
# At $x_b=0.10$ and $\delta=-5000$ J/mol: the odds, the occupancy, the expected
# number of B atoms on both boundaries, and the excess in both units. Then set
# $\delta=0$: what is $\theta$? Why is $\theta$ above $x_b$ for $\delta<0$?
#
# Also reject, in words: "The boundary has 0.16856 mol B, and $\phi$ is its
# absolute grain-boundary free energy." (Two errors.)
#
# Work from the odds formula with the printed factor. `theta_open(x_b)` and
# `theta_open(x_b, delta=0.0)` let you check your hand values; the functions of
# section 1 convert an occupancy into an excess.

# %%
odds_open = None           # dimensionless
theta_open_010 = None      # B per boundary site
boundary_B_open = None     # expected B atoms on both boundaries
excess_open = None         # atom/nm²
excess_open_mol_m2 = None  # mol/m²
theta_no_preference = None # B per boundary site, δ = 0
check(odds_open, "f7_d5_odds")
check(theta_open_010, "f7_d5_theta")
check(boundary_B_open, "f7_d5_boundary_B")
check(excess_open, "f7_d5_excess")
check(excess_open_mol_m2, "f7_d5_mol_m2")
check(theta_no_preference, "f7_d5_theta_delta0")

# %% [markdown]
# In the open cell the reservoir supplied every extra B atom without noticing. A
# real grain usually has no such reservoir: whatever goes to the boundary must
# come out of the bulk next to it.
#
# ## 3. Closed cell: a fixed inventory (D6, Lesson 13)
#
# Now no atoms enter or leave the 8200-site cell. Start with bulk $x_0=0.10$ and
# both boundaries at $\theta_0=0.25$. Total B is $8000x_0+200\theta_0$ and total
# A is $8200-B_{\rm tot}$. B that moves to the boundaries must come from the
# bulk:
#
# $$x_b(\theta)=\frac{B_{\rm tot}-200\theta}{8000}.$$
#
# The closed cell minimises its **total** Gibbs energy, here per mole of all 8200
# cell sites (no reservoir subtraction):
#
# $$\bar g(\theta)=\frac{8000\,g_b[x_b(\theta)]+200\,g_s(\theta)}{8200}.$$
#
# Differentiating with $dx_b/d\theta=-200/8000$ gives the same exchange condition
# as the open cell, $g_s'(\theta)=g_b'(x_b)$, but now $x_b$ moves with $\theta$.
# A hand method: put the current $x_b$ into the odds formula to get $\theta$,
# update $x_b$ from the inventory, and repeat.
#
# The derivative written out (chain rule for the bulk term):
#
# $$\frac{d\bar g}{d\theta}=\frac{8000\,g_b'(x_b)\left(-\frac{200}{8000}\right)+200\,g_s'(\theta)}{8200}
# =\frac{200}{8200}\,\bigl[g_s'(\theta)-g_b'(x_b)\bigr]=0 .$$
#
# The bar in $\bar g$ marks an average over all cell sites. Here there is nothing to
# subtract: no atoms leave the cell, so its total Gibbs energy is the quantity to
# minimise. The two unknowns $\theta$ and $x_b$ are tied together by the B balance,
# so one equation cannot be solved for $\theta$ alone in closed form. The hand
# method solves it by repetition: every round moves a little B between bulk and
# boundary, and because the boundaries have only 200 sites against 8000 in the bulk,
# $x_b$ changes only slightly from round to round, so the rounds settle quickly.
#
# In the code, `hand_round` performs one round and returns two values,
# `(θ, new x_b)`.

# %%
def x_bulk_closed(theta, B_total):
    return (B_total - K * S * theta) / N_BULK   # B per bulk site

def g_bar_closed(theta, B_total, delta=DELTA):
    x_b = x_bulk_closed(theta, B_total)
    return (N_BULK * g_bulk(x_b) + K * S * g_site(theta, delta)) / N_SITES   # J/mol all cell sites

def hand_round(x_b, B_total, delta=DELTA):
    theta = theta_open(x_b, delta)              # odds formula at the current bulk
    return theta, x_bulk_closed(theta, B_total) # new occupancy, updated bulk

B_total = N_BULK * 0.10 + K * S * 0.25   # B atoms in the cell, fixed from now on
for trial in (0.10, 0.15, 0.20, 0.25):   # Lesson 13 trials of the same closed cell
    print(f"  trial θ = {trial:.2f}: x_b = {x_bulk_closed(trial, B_total):.5f}, "
          f"ḡ = {g_bar_closed(trial, B_total):.4f} J/mol all cell sites")

# %% [markdown]
# These ḡ values compare states of the **same** closed cell. They cannot be ranked
# against the open φ values: different energies on different bases.
#
# Note how $x_b$ in the printout falls as the trial $\theta$ rises: B on the
# boundary is B missing from the bulk.
#
# ### Your turn
#
# 1. Total B and total A of the cell.
# 2. Trial $\theta=0.35$: boundary B, bulk B and $x_b$. How many B would the cell
#    hold if you kept $x_b=0.10$ instead?
# 3. Hand iteration, round 1: start with $x_b=x_0=0.10$, get $\theta$ from the odds
#    formula, then the updated $x_b$.
# 4. Keep going (use `hand_round` in a loop) until θ stops changing in the fifth
#    decimal. Give the settled $\theta$, $x_b$ and boundary B count.
#
# A loop for question 4 can look like this (type it into a new cell):
#
# ```python
# x_b = 0.10
# for k in range(8):
#     theta, x_b = hand_round(x_b, B_total)
#     print(k + 1, round(theta, 6), round(x_b, 6))
# ```
#
# `range(8)` repeats the indented lines 8 times; each round starts from the `x_b`
# that the previous round returned.

# %%
closed_total_B = None        # B atoms in the cell
closed_total_A = None        # A atoms in the cell
boundary_B_035 = None        # B atoms on both boundaries at θ = 0.35
bulk_B_035 = None            # B atoms in the bulk at θ = 0.35
x_b_035 = None               # B per bulk site at θ = 0.35
wrong_B_035 = None           # B atoms if x_b stayed 0.10
theta_round1 = None          # B per boundary site after round 1
x_b_round1 = None            # B per bulk site after round 1
theta_closed = None          # settled occupancy
x_b_closed = None            # settled bulk fraction
boundary_B_closed = None     # settled B atoms on both boundaries
check(closed_total_B, "f7_d6_total_B")
check(closed_total_A, "f7_d6_total_A")
check(boundary_B_035, "f7_d6_boundary_B_035")
check(bulk_B_035, "f7_d6_bulk_B_035")
check(x_b_035, "f7_d6_x_b_035")
check(wrong_B_035, "f7_d6_wrong_B_035")
check(theta_round1, "f7_d6_theta_round1")
check(x_b_round1, "f7_d6_x_b_round1")
check(theta_closed, "f7_d6_theta_final")
check(x_b_closed, "f7_d6_x_b_final")
check(boundary_B_closed, "f7_d6_boundary_B_final")

# %% [markdown]
# ## 4. A fresh card (D9) and more practice (self-study step 04)
#
# Same invented parameters, factor 1.82459687. These are two different
# experiments, even though both start with the number 0.20.
#
# - **Open**: reservoir $x_b=0.20$. Find the odds, $\theta$, the excess in
#   atom/nm², and the excess B count across the 40 nm² of both boundaries.
# - **Closed**: a new 8200-site cell with $x_0=0.20$, $\theta_0=0.20$ and trial
#   $\theta=0.40$. Find total B, boundary B, bulk B and $x_b$; how many B would
#   "keep $x_b=0.20$ because the open reservoir did" give?
# - **Baseline**: a different boundary state could carry an extra baseline
#   $\eta=2000$ J/mol of boundary sites. How much does that add per mole of all
#   8200 cell sites?
#
# Then write two sentences about a colleague who calls a model energy crossing
# a measured Ni–Cu boundary transition that strengthens the alloy: one statement
# this invented model does support, and one exact reason the claim does not follow.
#
# A **baseline** $\eta$ (Greek "eta") is a constant added to the boundary-site energy,
# $g_s(\theta)+\eta$, the same for every occupancy. For the baseline question, look
# again at how $\bar g$ in section 3 weights the boundary sites against all cell
# sites.

# %%
odds_020 = None            # dimensionless
theta_020 = None           # B per boundary site
excess_020 = None          # atom/nm²
excess_count_020 = None    # excess B atoms over both boundaries
card_total_B = None        # B atoms in the closed cell
card_boundary_B = None     # B atoms on both boundaries at θ = 0.40
card_bulk_B = None         # B atoms in the bulk at θ = 0.40
card_x_b = None            # B per bulk site at θ = 0.40
card_wrong_B = None        # B atoms if x_b stayed 0.20
baseline_per_cell_site = None   # J/mol all cell sites
check(odds_020, "f7_d9_odds")
check(theta_020, "f7_d9_theta")
check(excess_020, "f7_d9_excess")
check(excess_count_020, "f7_d9_excess_count")
check(card_total_B, "f7_d9_total_B")
check(card_boundary_B, "f7_d9_boundary_B")
check(card_bulk_B, "f7_d9_bulk_B")
check(card_x_b, "f7_d9_x_b")
check(card_wrong_B, "f7_d9_wrong_B")
check(baseline_per_cell_site, "f7_baseline_eta")

# %% [markdown]
# ## 5. After your attempt: the course code and the pictures
#
# The course modules `boundary_one_state` and `boundary_closed` solve the same
# model independently: a bounded minimiser on the full energy, checked against
# the odds formula (open) or the exchange root (closed).
#
# A **bounded minimiser** (here `scipy.optimize.minimize_scalar` with
# `method="bounded"`) searches for the lowest value of a function of one variable
# between two limits, here $0\le\theta\le1$, without using any formula for the
# answer. That makes it an independent check on the odds formula.
#
# **The first cell (open cell)** confirms your D4 and D5 values and then draws two
# panels.
#
# - **Left, the tangent picture.** The dotted line is the tangent to the bulk curve
#   $g_b$ at the reservoir composition $x_b=0.10$; its height at any x is
#   $(1-x)\mu_A+x\mu_B$. The boundary curve $g_s$ (dashed) lies below $g_b$ because
#   of $\delta$. The selected $\theta$ is where a line **parallel** to the reservoir
#   tangent just touches $g_s$: there the slope of $g_s$ equals $\mu_B-\mu_A$, which
#   is the exchange condition. The arrow is $\phi$, the vertical distance between
#   $g_s$ and the reservoir tangent at $\theta$.
# - **Right:** $\phi(\theta)$ itself, with the three Lesson 12 trials and the
#   minimum.
#
# `lambda z: ...` defines a small unnamed function in one line; here it is the
# reservoir tangent line.

# %% cellView="form"
#@title After your attempt: open cell, numbers and the tangent picture
from course.foundations import boundary_one_state as one_state
import matplotlib.pyplot as plt

# D4: A atoms = 8000(1 − 0.10) in the bulk + 200(1 − 0.15) on the boundaries.
print("D4:", f"A = {8000 * 0.90 + 200 * 0.85:.0f};",
      f"excess at θ = 0.08: {excess_atoms_per_nm2(0.08, 0.10):.2f} atom/nm²;",
      f"0.25 atom/nm² = {atoms_per_nm2_to_mol_per_m2(0.25):.5e} mol/m²")
confirm(8000 * 0.90 + 200 * 0.85 + 830, 8200, "A + B for the D4 trial", tol=1e-9)
confirm(excess_atoms_per_nm2(0.08, 0.10), -0.10, "Excess at θ = 0.08", tol=1e-9)
confirm(atoms_per_nm2_to_mol_per_m2(0.25), 4.15135e-7, "0.25 atom/nm² in mol/m²", tol=1e-11)

# D5: the course minimiser against the odds formula.
result = one_state.open_equilibrium(0.10, DELTA)   # dict with θ (minimiser), θ (formula), φ and the excess in mol/m²
print("\nOpen cell at x_b = 0.10:", {k: result[k] for k in ("theta", "theta_analytic", "phi_J_per_mol_sites", "gamma_B_mol_per_m2")})
odds = 0.10 / 0.90 * 1.82459687   # bulk odds times the preference factor
print(f"odds = {odds:.8f}, θ = {odds / (1 + odds):.8f}, boundary B = {200 * odds / (1 + odds):.4f}, "
      f"excess = {5 * (odds / (1 + odds) - 0.10):.7f} atom/nm²")
confirm(odds, 0.20273299, "Open odds", tol=1e-8)
confirm(result["theta"], 0.16856026, "Open occupancy (minimiser)", tol=1e-6)
confirm(theta_open(0.10), 0.16856026, "Open occupancy (odds formula)", tol=1e-8)
confirm(5 * (theta_open(0.10) - 0.10), 0.3428013, "Open excess in atom/nm²", tol=1e-7)
confirm(result["gamma_B_mol_per_m2"], 5.69235e-7, "Open excess in mol/m²", tol=1e-11)
confirm(result["phi_J_per_mol_sites"], -658.80722, "φ at the open minimum", tol=1e-4)
confirm(theta_open(0.10, delta=0.0), 0.10, "θ at zero preference", tol=1e-12)

# Tangent picture at x_b = 0.10: the boundary settles where a line parallel to
# the reservoir tangent touches g_s; φ is the vertical gap between the two lines.
x = np.linspace(0.005, 0.40, 200)   # composition grid; avoids x = 0, where ln x is undefined
xb, th = 0.10, theta_open(0.10)
reservoir_line = lambda z: (1 - z) * mu_A(xb) + z * mu_B(xb)   # tangent to g_b at x_b, J/mol
slope = mu_B(xb) - mu_A(xb)                                    # slope of that tangent, J/mol
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 5))
left.plot(x, g_bulk(x) / 1000, "-", label="bulk g_b")
left.plot(x, g_site(x) / 1000, "--", label="boundary g_s (δ = −5000)")
left.plot(x, reservoir_line(x) / 1000, ":", lw=2, label="reservoir tangent at x_b = 0.10")
left.plot(x, (g_site(th) + slope * (x - th)) / 1000, "-.", label="parallel line touching g_s")   # same slope, through (θ, g_s(θ))
left.plot([xb], [g_bulk(xb) / 1000], "o", label="reservoir x_b")
left.plot([th], [g_site(th) / 1000], "s", label="selected θ")
# Double-headed arrow from the tangent down to g_s at θ: its length is φ.
left.annotate("", xy=(th, g_site(th) / 1000), xytext=(th, reservoir_line(th) / 1000),
              arrowprops=dict(arrowstyle="<->"))
left.text(th + 0.012, (g_site(th) + 2 * reservoir_line(th)) / 3000, f"φ = {phi(th, xb):.0f} J/mol",
          bbox=dict(facecolor="white", edgecolor="none"))   # label placed one third of the way down the arrow
left.set(xlabel="B fraction x or θ", ylabel="g (kJ/mol sites)", title="Open cell: tangent picture")
left.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)   # legend below the panel
grid = np.linspace(0.01, 0.40, 200)
right.plot(grid, phi(grid, xb), "-", label="φ(θ), x_b = 0.10")
right.plot([0.10, 0.15, 0.25], [phi(t, xb) for t in (0.10, 0.15, 0.25)], "^", label="Lesson 12 trials")
right.plot([th], [phi(th, xb)], "s", label="minimum")
right.set(xlabel="boundary occupancy θ", ylabel="φ (J/mol boundary sites)", title="Open cell: grand potential per site")
right.legend()
fig.tight_layout()
plt.show()
print(" θ      φ (J/mol boundary sites)")
for t in (0.10, 0.15, round(th, 5), 0.25):
    print(f" {t:.5f}  {phi(t, xb):9.2f}")

# %% [markdown]
# **The second cell (closed cell)** confirms your D6 values, prints the hand
# iteration round by round, and compares the open and closed cells.
#
# - `closed.closed_trial(θ, B_tot, δ, 8000)` evaluates one trial occupancy of a
#   closed cell with 8000 bulk sites; `closed.closed_equilibrium(x0, δ, n_bulk)`
#   finds its minimum (starting from $\theta_0=0.25$).
# - The loop over 80000 and 800000 bulk sites makes the bulk 10 and 100 times
#   larger. The closed occupancy then moves towards the open result: a very large
#   closed bulk behaves like a reservoir.
# - **Left panel:** the selected occupancy against $x_b$ (open) or $x_0$ (closed).
#   The dotted line $\theta=x$ is "no preference"; both curves lie above it because
#   $\delta<0$. The closed cell starts with $\theta_0=0.25$ (dash-dotted line).
#   Where the selected $\theta$ is above 0.25, the boundary has to take extra B out
#   of the finite bulk, which lowers $x_b$, so the closed $\theta$ ends a little below
#   the open one. Where it is below 0.25 (at 0.10), the boundary gives B back to
#   the bulk and the closed $\theta$ ends a little above the open one.
# - **Right panel:** $\theta$ after each round of the hand iteration, approaching
#   the closed minimum (dashed), not the open result (dotted).

# %% cellView="form"
#@title After your attempt: closed cell, the hand iteration and both cells side by side
from course.foundations import boundary_closed as closed
from course.self_study.boundary_export import hand_iteration

trial = closed.closed_trial(0.35, 850, DELTA, 8000)   # θ = 0.35 in the 850-B cell with 8000 bulk sites
print(f"Closed trial θ = 0.35: boundary B = {200 * 0.35:.0f}, bulk B = {850 - 200 * 0.35:.0f}, x_b = {trial['x_bulk']:.4f}")
confirm(trial["x_bulk"], 0.0975, "Bulk fraction at θ = 0.35", tol=1e-12)
# ḡ at the four Lesson 13 trials, from the course module and from g_bar_closed above.
for t, expected in ((0.10, -10537.4054), (0.15, -10541.3690), (0.20, -10541.1526), (0.25, -10537.6008)):
    confirm(closed.closed_trial(t, 850, DELTA, 8000)["G_molar_J_per_mol_sites"], expected, f"ḡ at θ = {t:.2f}", tol=1e-4)
    confirm(g_bar_closed(t, 850), expected, f"ḡ at θ = {t:.2f} from the formula above", tol=1e-4)

steps = hand_iteration()["steps"]   # list of rounds; each round is a dict with k, x_b_used, theta, boundary_B, bulk_B
print("\nround  x_b used    θ           boundary B  bulk B")
for s in steps:
    print(f"{s['k']:>5}  {s['x_b_used']:.8f}  {s['theta']:.8f}  {s['boundary_B']:.4f}     {s['bulk_B']:.4f}")
confirm(steps[0]["theta"], 0.16856026, "Round 1 occupancy", tol=1e-8)
confirm((850 - steps[0]["boundary_B"]) / 8000, 0.10203599, "Round 1 bulk fraction", tol=1e-8)

final = closed.closed_equilibrium(0.10, DELTA, 8000)   # minimiser and exchange root for x0 = 0.10, θ0 = 0.25
print("\nClosed cell from x0 = 0.10, θ0 = 0.25:", {k: final[k] for k in ("theta", "theta_root", "x_bulk", "G_molar_J_per_mol_sites")})
confirm(final["theta"], 0.17160753, "Closed occupancy (minimiser)", tol=1e-7)
confirm(final["theta_root"], 0.17160752, "Closed occupancy (exchange root)", tol=1e-7)
confirm(final["x_bulk"], 0.10195981, "Closed bulk fraction", tol=1e-7)
confirm(200 * final["theta_root"], 34.3215, "Boundary B at the closed minimum", tol=1e-4)
confirm(200 * final["theta_root"] + 8000 * x_bulk_closed(final["theta_root"], 850), 850, "B inventory", tol=1e-9)
for nb, expected in ((80000, 0.16887598), (800000, 0.16859187)):   # bigger bulk → open result
    confirm(closed.closed_equilibrium(0.10, DELTA, nb)["theta"], expected, f"Closed occupancy with {nb} bulk sites", tol=1e-7)

# Open and closed occupancy for bulk fractions 0.10, 0.15, …, 0.90.
starts = np.round(np.arange(0.10, 0.901, 0.05), 2)   # rounded to 2 decimals to avoid values like 0.15000000000000002
open_theta = [one_state.open_equilibrium(z, DELTA)["theta"] for z in starts]
closed_theta = [closed.closed_equilibrium(z, DELTA, 8000)["theta"] for z in starts]
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))
left.plot(starts, open_theta, "o-", label="open: reservoir x_b")
left.plot(starts, closed_theta, "x--", label="closed: start x0, θ0 = 0.25")
left.plot(starts, starts, ":", label="no preference (θ = x)")
left.axhline(0.25, color="grey", lw=0.8, ls="-.", label="θ0 = 0.25")
left.set(xlabel="reservoir x_b (open) or start x0 (closed)", ylabel="selected occupancy θ",
         title="Occupancy at δ = −5000 J/mol")
left.legend(fontsize=8)
rounds = [s["k"] for s in steps]   # round numbers 1, 2, …
right.plot(rounds, [s["theta"] for s in steps], "o-", label="θ after each round")
right.axhline(final["theta_root"], ls="--", color="grey", label="closed minimum")
right.axhline(theta_open(0.10), ls=":", color="black", label="open result at 0.10")
right.set(xlabel="round", ylabel="boundary occupancy θ", title="Closed cell by hand")
right.legend()
fig.tight_layout()
plt.show()
print(" x      θ open      θ closed")
for z, a, b in zip(starts, open_theta, closed_theta):
    print(f" {z:.2f}   {a:.6f}   {b:.6f}")

# %% [markdown]
# **The third cell** confirms the D9 card. Note in the closed card how much B the
# "keep $x_b=0.20$" reasoning would need compared with the fixed total: the
# difference is B that the closed cell does not have. The baseline line shows the
# weighting $200\,\eta/8200$: only the 200 boundary sites carry $\eta$, but the
# energy is expressed per mole of all 8200 cell sites.

# %% cellView="form"
#@title After your attempt: the D9 card and the step 04 practice
# Open card: reservoir x_b = 0.20.
odds = 0.20 / 0.80 * 1.82459687
print(f"Open x_b = 0.20: odds = {odds:.8f}, θ = {theta_open(0.20):.8f}, "
      f"excess = {5 * (theta_open(0.20) - 0.20):.6f} atom/nm² = {200 * (theta_open(0.20) - 0.20):.4f} B over 40 nm²")
confirm(odds, 0.45614922, "Open odds at 0.20", tol=1e-8)
confirm(one_state.open_equilibrium(0.20, DELTA)["theta"], 0.31325719, "Open occupancy at 0.20 (minimiser)", tol=1e-6)
confirm(5 * (theta_open(0.20) - 0.20), 0.566286, "Open excess at 0.20", tol=1e-6)
confirm(excess_atoms_per_nm2(theta_open(0.20), 0.20) * 40, 22.6514, "Excess B count over 40 nm²", tol=1e-4)

# Closed card: x0 = 0.20, θ0 = 0.20, trial θ = 0.40.
card_B = 8000 * 0.20 + 200 * 0.20   # fixed total B of this cell
card = closed.closed_trial(0.40, card_B, DELTA, 8000)
print(f"Closed x0 = 0.20, θ0 = 0.20: B_tot = {card_B:.0f}; trial θ = 0.40: boundary B = {200 * 0.40:.0f}, "
      f"bulk B = {card_B - 200 * 0.40:.0f}, x_b = {card['x_bulk']:.3f}; keeping x_b = 0.20 would need {8000 * 0.20 + 200 * 0.40:.0f} B")
confirm(card_B, 1640, "Closed total B", tol=1e-9)
confirm(card["x_bulk"], 0.195, "Closed trial bulk fraction", tol=1e-12)
# Baseline: 2000 J/mol on 200 boundary sites, expressed per mole of all 8200 cell sites.
confirm(200 * 2000 / 8200, 48.78049, "Baseline per mole of all cell sites", tol=1e-5)

# %% [markdown]
# Full worked answers and discussion: [Day 2 answers](../course/primer_day2/answers.md)
# (D4–D6, D9) and Lessons [11](../course/foundations/lesson_11_geometry.md),
# [12](../course/foundations/lesson_12_reservoir.md) and
# [13](../course/foundations/lesson_13_finite_reservoir.md).
#
# ## 6. Limits
#
# The boundary is invented: its preference δ, sites and area are chosen numbers,
# not measured properties of any real grain boundary, and the bulk is the
# invented ideal ALPHA curve. The excess uses one chosen equal-site reference;
# a real interface with another site density would need its own definition.
# One boundary state cannot show a boundary transition. The open and closed
# cells minimise different energies, so their values are never ranked against
# each other.
# Next: [f8 · two candidate boundary states](f8_boundary_states.ipynb).
