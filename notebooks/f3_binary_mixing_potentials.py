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
#
# **The plan.** f1 and f2 had one kind of atom, so the only question was *which
# phase*. With two kinds of atoms, A and B, a phase can also have any
# *composition*, and the Gibbs energy becomes a curve against composition instead
# of a single number. The notebook builds that curve in three steps:
#
# 1. **Counting** (section 1): how to describe composition, and how amounts are
#    kept when a sample is divided into regions.
# 2. **Ideal mixing** (section 2): the Gibbs energy of one phase as a function of
#    its composition.
# 3. **Chemical potentials** (section 3): what the slope of that curve means, and
#    how the tangent to the curve gives μ_A and μ_B.
#
# These three ideas are what f4 needs to compare two phases.

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
#
# **Why the balances look like this.** Take one mole of atoms in total. Region 1
# holds f_1 mol of atoms, and a fraction x_1 of those are B, so it holds f_1 x_1 mol
# of B. Region 2 likewise holds f_2 x_2 mol of B. No atom is created or lost, so the
# two B amounts must add up to the z mol of B in the whole sample. The same
# reasoning with the A fractions 1 − x gives the A balance. Adding the two balances
# gives back f_1 + f_2 = 1, so the second one is a useful check rather than new
# information.
#
# The cell below first computes x_B, x_A and the ratio n_B/n_A for 3 mol A and 1 mol
# B, then checks both balances for a worked split. In the printout, compare x_B
# with the ratio: they are different numbers for the same sample.

# %%
n_A, n_B = 3.0, 1.0                 # mol of atoms
x_B = n_B / (n_A + n_B)             # B atom fraction
print(f"x_B = {x_B:.2f}, x_A = {1 - x_B:.2f}, ratio n_B/n_A = {n_B / n_A:.4f}")   # :.2f = 2 decimals

# D1 worked count: two regions, half the atoms in each
f1, f2 = 0.5, 0.5                   # phase amount fractions
x1, x2 = 0.10, 0.50                 # B fraction inside each region
z = f1 * x1 + f2 * x2               # overall B fraction
a_balance = f1 * (1 - x1) + f2 * (1 - x2)   # overall A fraction; must equal 1 − z
print(f"z = {z:.2f}, A balance = {a_balance:.2f}, sum = {z + a_balance:.2f}")   # sum must be 1

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
#
# For item 3, replace f1 by 1 − f2 in the B balance; that leaves one equation with
# one unknown.

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
#
# The B mass fraction is $w_B = m_B/(m_A + m_B)$. Because a B atom here is four
# times as heavy as an A atom, the same sample has a much larger mass fraction of B
# than atom fraction of B. Thermodynamic models in this course always use atom
# (mole) fractions; alloy specifications often use mass fractions (wt%), so the
# conversion matters in practice.

# %%
M_A, M_B = 20.0, 80.0               # g/mol, invented
m_A, m_B = n_A * M_A, n_B * M_B     # g  (mol × g/mol)
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
#
# The route is always the same: convert every amount to the quantity you are asked
# about (grams to moles with n = m/M, or moles to grams with m = nM), and only
# then divide.

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
#
# Reminder: 1 kJ = 1000 J. A value rounded to 0.01 kJ/mol can be off by up to half
# of that step. "J/mol atoms" means "per mole of atoms"; a molar quantity times an
# amount in mol gives a total in J.

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
#
# **Where each term comes from.** Here x is the B atom fraction of the phase and
# g_b its molar Gibbs energy (J per mole of atoms).
#
# - *Reference line.* If A and B atoms did not notice each other, a mole of the
#   phase would just be (1 − x) mol of pure A plus x mol of pure B:
#   $(1-x)g_A + x\,g_B = -9000 + (3000 - (-9000))\,x = -9000 + 12000x$. This is a
#   straight line from g_A at x = 0 to g_B at x = 1.
# - *Mixing term.* Mixing A and B atoms at random on the sites creates many more
#   possible arrangements than keeping them apart. Counting those arrangements
#   (Boltzmann's $S = k_B \ln W$) gives the ideal entropy of mixing
#   $\Delta s_{mix} = -R\,q(x)$. In an *ideal* solution there is no energy change
#   on mixing, so the mixing Gibbs energy is only the entropy part:
#   $\Delta g_{mix} = -T\Delta s_{mix} = RT\,q(x)$.
# - *Sign.* For 0 < x < 1 both logarithms are of numbers below 1, so they are
#   negative; q(x) < 0, and mixing lowers g.
# - *R* is the gas constant, 8.3145 J/(mol K), and RT = 8314.5 J/mol at 1000 K.
#
# **The Python.** `from scipy.special import xlogy` imports one function from SciPy.
# `xlogy(a, b)` computes a·ln(b), but returns exactly 0 when a = 0, which is the
# correct limit for 0 ln 0. The four small functions build g_b piece by piece, so
# each piece can be printed and checked separately. The `with np.errstate(...)`
# block only silences NumPy's warning while the cell deliberately shows what the
# naive 0 · ln 0 gives.

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

# Demonstration: ln(0) is −infinity, and 0 × (−infinity) is undefined (nan, "not a number").
with np.errstate(divide="ignore", invalid="ignore"):   # hide the warning for this one deliberate case
    print("naive 0 * ln(0) =", np.float64(0.0) * np.log(np.float64(0.0)), " ← not a number")
print("xlogy(0, 0)     =", xlogy(0.0, 0.0))

x_demo = 0.10   # D2 worked example
print(f"x = {x_demo}: q = {q_mix(x_demo):.8f}, reference = {g_reference(x_demo):.3f}, "
      f"mixing = {g_mixing(x_demo):.3f}, g_b = {g_b(x_demo):.3f} J/mol atoms")

# %% [markdown]
# **What to look at.** At x = 0.10 the mixing term is negative and pulls g_b below
# the reference line. Check by hand that reference + mixing = g_b in the printout.
#
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
#
# **What the cell adds.** It splits g into enthalpy and entropy, g = h − Ts. The
# pure endmembers here have h_A = 1000 J/mol, h_B = 13000 J/mol and the same entropy
# s = 10 J/(mol K), so the reference enthalpy is the straight line
# h = 1000 + 12000x and g_ref = h − 10T. Ideal mixing adds nothing to h, but adds
# Δs_mix = −Rq to the entropy, so the total entropy is 10 + Δs_mix and the mixing
# Gibbs energy is −TΔs_mix.
#
# **The Python.** `zip(x, gref, gmix, ...)` walks through the six arrays together
# and gives one row (a tuple of six numbers) at a time. In
# `' '.join(f'{v:.6f}' for v in row)` each number is formatted with six decimals
# and the pieces are joined with spaces into one line. `[central]` picks one
# element of an array by its position (Python counts from 0, so position 1 is the
# second row, x = 0.5).

# %%
from scipy.special import xlogy

T = 1000.0                   # K
R = 8.3145                   # J/(mol K)
x = np.array([0.0, 0.5, 1.0])   # B atom fraction of three separate samples
h = 1000.0 + 12000.0*x       # J/mol, enthalpy (no enthalpy of mixing in an ideal solution)
gref = h - 10.0*T            # J/mol, reference Gibbs energy; both endmembers have s = 10 J/(mol K)
q = xlogy(x, x) + xlogy(1-x, 1-x)   # dimensionless, ≤ 0
smix = -R*q                  # J/(mol K), ideal entropy of mixing, ≥ 0
gmix = -T*smix               # J/mol, mixing Gibbs energy, ≤ 0
for row in zip(x, gref, gmix, gref+gmix, h, 10+smix):   # columns: x, g_ref, Δg_mix, g, h, s
    print(' '.join(f'{v:.6f}' for v in row))

central, pure_A = 1, 0       # row positions: 1 is x = 0.5, 0 is x = 0
confirm((gref + gmix)[central], -8763.172233, "Total g at x = 0.5", tol=1e-6)
confirm(gmix[central], -5763.172233, "Mixing term at x = 0.5", tol=1e-6)
confirm((10 + smix)[central], 15.763172, "Total s at x = 0.5", tol=1e-6)
confirm((gref + gmix)[pure_A], -9000.0, "Pure-A row: total g", tol=1e-9)
confirm(gmix[pure_A], 0.0, "Pure-A row: no mixing term", tol=1e-12)

# %% [markdown]
# **What to look at.** At both pure ends the mixing column is 0 and the entropy
# column is 10: a pure substance has nothing to mix. At x = 0.5 the mixing term is
# largest in size, because a 50:50 mixture has the most possible arrangements.
#
# So far g_b tells us the Gibbs energy of a whole mole of the phase at a given
# composition. The next question is how g changes when atoms are added or swapped:
# that is what chemical potentials measure.

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
#
# **Step by step.** Write the total Gibbs energy of the sample as
# $G(n_A, n_B) = n\,g_b(x)$ with $n = n_A + n_B$ and $x = n_B/n$. In symbols,
# $\mu_B = \partial G/\partial n_B$ at fixed $n_A$: the extra G per extra mole of B.
#
# 1. Adding $dn_B$ of B changes both n and x: $dn = dn_B$ and
#    $dx = (1-x)\,dn_B/n$.
# 2. So $dG = g_b\,dn + n\,g_b'\,dx = [g_b + (1-x)\,g_b']\,dn_B$, which gives the
#    formula for μ_B. The same steps with A (where $dx = -x\,dn_A/n$) give
#    $\mu_A = g_b - x\,g_b'$.
# 3. Subtracting the two: $\mu_B - \mu_A = g_b'$. Multiplying μ_A by (1 − x), μ_B
#    by x and adding: $(1-x)\mu_A + x\mu_B = g_b$.
#
# For the ideal ALPHA the derivative of q is
# $q'(x) = -\ln(1-x) - 1 + \ln x + 1 = \ln\frac{x}{1-x}$, which gives the slope
# above. Putting it into $\mu_A = g_b - x\,g_b'$, the 12000x terms cancel and the
# logarithms combine to RT ln(1 − x). Each μ is "pure-element g plus RT ln(own
# atom fraction)", and it falls steeply as that atom fraction goes to 0.
#
# **Why the tangent ends are μ_A and μ_B.** Put x = 0 into ℓ(x): ℓ(0) = g_b − x_0 g_b'
# = μ_A. Put x = 1: ℓ(1) = g_b + (1 − x_0) g_b' = μ_B. This picture (draw the tangent
# and read its two ends) is how chemical potentials are read off a Gibbs curve.

# %%
def mu_A(x):
    return -9000.0 + RT * np.log(1 - x)        # J/mol atoms, 0 < x < 1

def mu_B(x):
    return 3000.0 + RT * np.log(x)             # J/mol atoms

def slope(x):
    return 12000.0 + RT * np.log(x / (1 - x))  # g_b' = mu_B − mu_A, J/mol atoms

def tangent(x, x0):
    return g_b(x0) + slope(x0) * (x - x0)      # J/mol atoms

for x0 in (0.10, 0.50):   # two touching points
    # line 1: both potentials, their difference and the slope (these two must agree)
    print(f"x0 = {x0}: mu_A = {mu_A(x0):.3f}, mu_B = {mu_B(x0):.3f}, "
          f"mu_B − mu_A = {mu_B(x0) - mu_A(x0):.3f}, slope = {slope(x0):.3f} J/mol atoms")
    # line 2: tangent ends (must equal mu_A and mu_B) and the weighted average (must equal g_b)
    print(f"   tangent at x = 0: {tangent(0.0, x0):.3f}, at x = 1: {tangent(1.0, x0):.3f}; "
          f"(1 − x) mu_A + x mu_B = {(1 - x0) * mu_A(x0) + x0 * mu_B(x0):.3f} = g_b = {g_b(x0):.3f}")

# %% [markdown]
# **What to look at.** For each x0, three pairs of numbers must agree: μ_B − μ_A and
# the slope; the tangent at x = 0 and μ_A; the tangent at x = 1 and μ_B. The last
# check, (1 − x)μ_A + xμ_B = g_b, says the molar Gibbs energy is the
# composition-weighted average of the two chemical potentials.

# %% [markdown]
# ### Addition is not exchange: Lesson 6's finite differences
#
# Lesson 6's cell, written here with the g_b defined above, builds the total
# G(n_A, n_B) = n g_b(x) and changes the amounts directly at n_A = n_B = 0.5 mol. "Addition" adds B with A fixed (an estimate of
# μ_B); "exchange" swaps A for B at fixed total (an estimate of g_b'). Columns: step
# h (mol), addition (J/mol), exchange (J/mol). Predict both signs first.
#
# **The numerical method.** A derivative can be estimated without any algebra by a
# *central difference*: change the input by +h and by −h, and divide the change of
# the output by the total step 2h:
#
# $$\frac{dG}{dn} \approx \frac{G(n + h) - G(n - h)}{2h}.$$
#
# The smaller h, the closer the estimate, until rounding errors of the computer
# start to matter at very small h. For the exchange, n_B goes up by h while n_A goes
# down by h, so the total n stays at 1 mol. In this cell `h` is the step in mol; it
# reuses the name of the enthalpy array above, which is not needed any more.
# `1e-3` is Python's way of writing 1 × 10⁻³, and the format `{h:.0e}` prints a
# number in that style.

# %%
def total_G(nA, nB):
    n = nA + nB                     # mol of atoms
    return n * g_b(nB / n)          # J

for h in (1e-3, 1e-4, 1e-5, 1e-6):   # step size in mol
    addition = (total_G(.5, .5+h)-total_G(.5, .5-h))/(2*h)            # n_A fixed: estimate of mu_B, J/mol
    exchange = (total_G(.5-h, .5+h)-total_G(.5+h, .5-h))/(2*h)        # n_A + n_B fixed: estimate of g_b', J/mol
    print(f'{h:.0e} {addition:.6f} {exchange:.6f}')

# %% [markdown]
# **What to look at.** Read down each column: the estimates settle to fixed values
# as h shrinks. Compare the settled values with μ_B and the slope at x0 = 0.5 printed
# two cells above. Addition and exchange give clearly different numbers, because
# they are different questions. The next cell confirms both settled values.

# %%
for step in (1e-5, 1e-6):   # the two smallest steps, in mol
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
#
# You may use the functions defined above (`slope`, `mu_A`, `mu_B`, `tangent`) to
# check your hand calculation, for example in a new line of the cell below.
# For item 3, set the slope formula equal to 0 and solve for x step by step: first
# isolate the logarithm, then undo it with the exponential function.

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
#
# **About the first cell.** The course module `binary_family` (imported as `bf`)
# contains the same model written independently of this notebook:
#
# - `bf.ideal_properties(T, x)` returns a dictionary with `"GM_reference"`,
#   `"GM_mix"` and `"GM"` (all J/mol atoms), and also `"HM"` and `"SM"`.
# - `bf.ideal_derivatives(T, x)` returns `"slope"`, `"mu_A"` and `"mu_B"`.
# - `bf.lever_fraction(z, x1, x2)` solves the B balance for the fraction of the
#   second region (f4 uses it again).
#
# The values come back as NumPy arrays, so `float(...)` turns a single value into
# an ordinary number for printing and comparing.
#
# **Finding the sign change on a grid.** `np.arange(1, 100) / 100` gives
# 0.01, 0.02, …, 0.99 and `np.round(..., 2)` removes tiny rounding leftovers.
# `grid_slope > 0` is an array of True/False; `np.argmax` of it returns the position
# of the first True, which is the first composition with a positive slope. The one
# before it is the last negative one. The exact zero follows from
# 12000 + RT ln(x/(1 − x)) = 0: x/(1 − x) = e^(−12000/RT), so x = 1/(1 + e^(12000/RT));
# `math.exp` is the exponential function for a single number.

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
props = bf.ideal_properties(T, 0.20)    # dictionary: GM_reference, GM_mix, GM, ... (J/mol atoms)
deriv = bf.ideal_derivatives(T, 0.20)   # dictionary: slope, mu_A, mu_B (J/mol atoms)
print(f"x = 0.20: reference {float(props['GM_reference']):.3f}, mixing {float(props['GM_mix']):.3f}, "
      f"g_b {float(props['GM']):.3f}, slope {float(deriv['slope']):.3f}, "
      f"mu_A {float(deriv['mu_A']):.3f}, mu_B {float(deriv['mu_B']):.3f} J/mol atoms")
confirm(float(props["GM_reference"]), -6600.0, "Step 02: reference at x = 0.20", tol=1e-6)
confirm(float(props["GM_mix"]), -4160.596, "Step 02: mixing term at x = 0.20", tol=1e-3)
confirm(float(props["GM"]), -10760.596, "Step 02: g_b at x = 0.20", tol=1e-3)
confirm(float(deriv["slope"]), 473.656, "Step 02: exchange slope at x = 0.20", tol=1e-3)
confirm(2 * 0.20, 0.40, "Step 02: mol B in 2 mol at z = 0.20", tol=1e-12)
confirm(bf.lever_fraction(0.20, 0.10, 0.50), 0.25, "D1: f2 for the balanced trial", tol=1e-12)

grid = np.round(np.arange(1, 100) / 100, 2)               # 0.01, 0.02, ..., 0.99
grid_slope = bf.ideal_derivatives(T, grid)["slope"]       # slope at every grid point, J/mol atoms
first_positive = int(np.argmax(grid_slope > 0))           # position of the first positive slope
print(f"sign change between x = {grid[first_positive - 1]:.2f} ({grid_slope[first_positive - 1]:.1f}) "
      f"and x = {grid[first_positive]:.2f} ({grid_slope[first_positive]:.1f}) J/mol atoms")
confirm(grid[first_positive - 1], 0.19, "Step 02: last negative slope on the 0.01 grid", tol=1e-12)
confirm(float(grid_slope[first_positive - 1]), -56.0, "Step 02: slope at x = 0.19 (about −56)", tol=0.5)
confirm(1 / (1 + math.exp(12000 / RT)), 0.191040753, "Lesson 6: zero of the ALPHA slope", tol=1e-9)   # exact zero of g_b'

# The course module and the formulas of section 3 must give the same mu_A, mu_B and tangent ends.
for x0 in (0.10, 0.20, 0.50):
    d = bf.ideal_derivatives(T, x0)
    confirm(float(d["mu_A"]), mu_A(x0), f"mu_A formula at x = {x0}", tol=1e-6)
    confirm(float(d["mu_B"]), mu_B(x0), f"mu_B formula at x = {x0}", tol=1e-6)
    confirm(tangent(0.0, x0), float(d["mu_A"]), f"Tangent at x = 0 is mu_A (x0 = {x0})", tol=1e-6)
    confirm(tangent(1.0, x0), float(d["mu_B"]), f"Tangent at x = 1 is mu_B (x0 = {x0})", tol=1e-6)

# The worked values quoted in the Day 2 primer and in Lesson 6
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

print("\nLesson 4's full cell, now with its x = 0.2 and x = 0.8 rows (x, g_ref, Δg_mix, g, h, s):")
full = bf.ideal_properties(T, np.array([0.0, 0.2, 0.5, 0.8, 1.0]))
for row in zip([0.0, 0.2, 0.5, 0.8, 1.0], full["GM_reference"], full["GM_mix"], full["GM"], full["HM"], full["SM"]):
    print(' '.join(f'{v:.6f}' for v in row))
confirm(float(full["GM"][2]), -8763.172233, "Lesson 4: central row with the course module", tol=1e-6)
confirm(float(full["GM"][1]), -10760.596, "Lesson 4: total g at x = 0.2", tol=1e-3)

# %% [markdown]
# **About the plotting cell.** It draws three panels side by side
# (`plt.subplots(1, 3)` returns the figure and three sets of axes):
#
# - *Left:* g_b split into the reference line and the mixing term. The total is
#   their sum.
# - *Middle:* g_b with the tangent at x0, the touching point, and the two tangent
#   ends marked as μ_A (square at x = 0) and μ_B (triangle at x = 1). Change `x0` in
#   the first line and run again to see the tangent ends move.
# - *Right:* μ_A, μ_B and their difference, the slope, against composition. The grey
#   horizontal line marks zero, so you can see where the slope changes sign.
#
# Two composition grids are used: `x_all` includes the pure ends (the curve is
# defined there, thanks to `xlogy`), `x_in` stays strictly inside, because ln 0 in μ_A
# or μ_B would be −∞. Energies are divided by 1000 to plot kJ/mol. Other plotting
# details: `plt.rcParams.update({"font.size": 12})` sets a larger default font,
# `markevery=10` puts a marker on every tenth point only, `fig.tight_layout()` stops
# the panels from overlapping. In the final table, a format like `{'x':>5}` prints
# the text right-aligned in a column 5 characters wide.

# %% cellView="form"
#@title After your attempt: plot the curve, a tangent and the chemical potentials
import matplotlib.pyplot as plt

x0 = 0.20   # composition of the tangent; change it (0 < x0 < 1) and run again
plt.rcParams.update({"font.size": 12})
x_all = np.linspace(0.0, 1.0, 201)       # pure ends included: 0 ln 0 = 0
x_in = np.linspace(0.01, 0.99, 99)       # derivatives: interior only
fig, (left, middle, right) = plt.subplots(1, 3, figsize=(15, 4.4))

# Left panel: the curve and its two parts (kJ/mol atoms)
left.plot(x_all, g_b(x_all) / 1000, "-", lw=2, label="g_b (total)")
left.plot(x_all, g_reference(x_all) / 1000, "--", label="reference −9000 + 12000x")
left.plot(x_all, g_mixing(x_all) / 1000, ":", lw=2.5, label="mixing term RT q(x)")
left.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="ALPHA at 1000 K")
left.legend(fontsize=10)

# Middle panel: the tangent at x0 is a straight line, so two points (x = 0 and x = 1) draw it
middle.plot(x_all, g_b(x_all) / 1000, "-", lw=2, label="g_b")
middle.plot([0, 1], [tangent(0.0, x0) / 1000, tangent(1.0, x0) / 1000], "--", label=f"tangent at x0 = {x0}")
middle.plot([x0], [g_b(x0) / 1000], "o", ms=8, label="touching point")   # ms: marker size
middle.plot([0], [mu_A(x0) / 1000], "s", ms=9, label="x = 0: μ_A")
middle.plot([1], [mu_B(x0) / 1000], "^", ms=9, label="x = 1: μ_B")
middle.set(xlabel="B atom fraction x", ylabel="g (kJ/mol atoms)", title="Tangent ends are μ_A and μ_B")
middle.legend(fontsize=10)

# Right panel: chemical potentials and slope, interior compositions only
right.plot(x_in, mu_A(x_in) / 1000, "-", label="μ_A")
right.plot(x_in, mu_B(x_in) / 1000, "--", label="μ_B")
right.plot(x_in, slope(x_in) / 1000, "-.", marker="o", markevery=10, label="slope μ_B − μ_A")
right.axhline(0, color="grey", lw=0.8)   # horizontal line at zero
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
# **What to look at.** Left: the mixing term is zero at both ends and pulls the
# total below the reference line everywhere in between. Middle: the tangent touches
# the curve at x0 and its two ends sit at μ_A and μ_B, not at the curve's own end
# values. Right: μ_A drops steeply as x → 1 and μ_B as x → 0; the slope crosses zero
# where the curve has its lowest point.
#
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
