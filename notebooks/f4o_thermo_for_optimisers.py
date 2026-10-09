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
# # f4o · Thermodynamics for optimisers (advanced steps 08–09)
#
# **In plain words.** At fixed temperature and pressure, a closed sample's
# equilibrium is its allowed state of lowest Gibbs energy $G$. Each phase model
# gives a cost curve per mole of atoms: a straight line between the pure ends
# plus a term that comes from counting arrangements. In this notebook you build
# those curves yourself, read prices off them, and see when a curve stops
# being convex.
#
# **Learning goals.** After this notebook you can
#
# 1. show with numbers that "total entropy up" and "$G$ of the sample down" are
#    the same statement for a sample in a heat bath;
# 2. count arrangements and see where $x\ln x$ comes from;
# 3. build $g(x)$ for the melting lens and read a chemical potential both as a
#    small addition and as a formula;
# 4. show that adding a straight line to every curve changes no split, only the
#    prices;
# 5. use the sign of $g''$ to tell stable, metastable and unstable states apart;
# 6. (dive deeper, operations research) derive the closed-form pricing step of step 13.
#
# **What you need.** Steps 08 and 09 of the course, or at least their
# cards: why a closed system at fixed T and p minimises G, H and S, z, x and f,
# building g(x), what Ω does.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Sample and heat bath: the second law in numbers | main | 10 min |
# | 2 | Counting arrangements | main | 15 min |
# | 3 | Building g(x) | main | 15 min |
# | 4 | Chemical potentials: a small addition, and a formula | main | 15 min |
# | 5 | The affine shift: only differences matter | main | 10 min |
# | 6 | Bending: Ω against 2RT, metastable and unstable | main | 15 min |
# | 7 | Exercises | both | 20 min |
#
# **Coming from materials.** Everything here is in steps 00–04 already. Use
# the notebook as a numerical check of what you know, and skim the operations-research remarks.
#
# **Coming from operations research.** This is the objective function of the menu LP: where the
# cost coefficients come from, why they are per mole of atoms, and why the
# mixing term makes some curves convex and others not. No thermodynamics is
# assumed.
#
# **How to work.** Run the cells from top to bottom. In each "Your turn" cell,
# replace `None` with your value and run it: `check` says whether you match,
# without showing the answer. Cells marked *After your attempt* hold worked
# solutions.

# %%
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.2.1"
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
# ## 0. Numbers you may change, and the tools
#
# Leave these as they are for the first run: the "Your turn" checks expect
# them. Later, change one number at a time and rerun everything below it.
#
# - `T_BATH`: the heat bath's temperature for section 1, in K;
# - `T_LENS`: the temperature of the melting lens (step 03 part C), in K;
# - `T_REG`: the temperature of the regular solution (step 03 part B), in K.

# %%
T_BATH = 1100.0   # K, section 1
T_LENS = 1400.0   # K, sections 3-5
T_REG = 800.0     # K, section 6

# %% [markdown]
# Three libraries and two course modules. `day3_core` holds the phase models of
# the advanced steps and produced every number on the website; `binary_family` is the
# course's model library of steps 01–04. Colours follow the website.

# %%
import math
import numpy as np
import matplotlib.pyplot as plt
from course.self_study import day3_core as d
from course.foundations import binary_family as bf

SOLID_C, LIQUID_C, LINE_C = "#2445c4", "#cf4418", "#8f6400"   # the website's colours
R = d.R                                                        # 8.3145 J/(mol K), the course value

# %% [markdown]
# ## 1. Sample and heat bath: the second law in numbers (main track, 10 min)
#
# Pure A from step 01: as a solid $g=1000-10T$, as a liquid $g=7000-16T$
# (J/mol). Melting one mole takes $\Delta H=7000-1000=6000$ J from the bath and
# raises the sample's entropy by $\Delta S=16-10=6$ J/(mol K). The bath loses
# the heat, so its entropy falls by $\Delta H/T$.
#
# The second law: the total entropy of sample plus bath cannot fall. The next
# cell computes the three entropy changes and the sample's $\Delta G$.

# %%
dH, dS = 7000.0 - 1000.0, 16.0 - 10.0        # liquid minus solid, J/mol and J/(mol K)
dS_bath = -dH / T_BATH                        # the bath gives up the heat dH
dS_total = dS + dS_bath
dG = dH - T_BATH * dS                         # change of the sample's G
print(f"T = {T_BATH:.0f} K: dS_sample = {dS:.3f}, dS_bath = {dS_bath:.3f}, total = {dS_total:.4f} J/(mol K)")
print(f"dG of the sample = {dG:.1f} J/mol")

# %% [markdown]
# The two statements are one: $\Delta S_{\text{total}}=-\Delta G/T$. When the total
# entropy rises, $G$ falls, and the other way round. The check below tests
# this at a range of temperatures.

# %%
for T in (800.0, 900.0, 1000.0, 1100.0, 1400.0):
    total, dG_T = dS - dH / T, dH - T * dS
    assert abs(total + dG_T / T) < 1e-12, f"at {T} K the two statements disagree"
    print(f"{T:6.0f} K: total entropy change {total:+.4f}, dG {dG_T:+8.1f} -> {'melts' if dG_T < 0 else 'stays solid' if dG_T > 0 else 'melting point'}")

# %% [markdown]
# So at equilibrium the sample sits in its allowed state of lowest $G$. The
# second law does not say how long it takes to get there; that is kinetics.
# A function that cannot rise does not by itself reach its global minimum.
#
# ### Your turn: the total entropy change at 1100 K
#
# For one mole melting at 1100 K, what is the total entropy change of sample
# plus bath, in J/(mol K)?

# %%
ds_total_1100 = None   # J/(mol K)
check(ds_total_1100, "f4o_ds_total_1100")

# %% [markdown]
# ## 2. Counting arrangements (main track, 15 min)
#
# Put $k$ B atoms on $N$ sites. The number of arrangements is the binomial
# coefficient $W=N!/(k!\,(N-k)!)$, and the entropy is $k_B\ln W$. Factorials
# get huge, so we work with logarithms: `math.lgamma(n + 1)` is $\ln n!$.

# %%
def ln_W(N, k):
    """ln of the number of ways to put k B atoms on N sites."""
    return math.lgamma(N + 1) - math.lgamma(k + 1) - math.lgamma(N - k + 1)

print(f"N = 100, k = 40: W is about 10^{ln_W(100, 40) / math.log(10):.1f}")

# %% [markdown]
# Per site, $\ln W/N$ approaches a simple limit for large $N$ (Stirling's
# approximation $\ln n!\approx n\ln n-n$):
#
# $$\frac{\ln W}{N}\;\to\;-\big[x\ln x+(1-x)\ln(1-x)\big],\qquad x=k/N.$$
#
# `d.q(x)` is the bracket $x\ln x+(1-x)\ln(1-x)$, with the value 0 at the pure
# ends. **Predict first:** is the counted value above or below the limit, and
# does the difference shrink as $N$ grows?

# %%
for N in (10, 100, 1000, 10000):
    k = round(0.4 * N)
    print(f"N = {N:5d}: ln W / N = {ln_W(N, k) / N:.5f}   limit {-float(d.q(k / N)):.5f}")

# %% [markdown]
# Per mole of atoms the mixing entropy is $R$ times the limit, a positive
# number; $-T$ times it is the mixing term of $g(x)$. In optimisation words: an entropy
# regulariser, with the temperature as its weight.
#
# ### Your turn: one count
#
# Give $\ln W/N$ for $N=100$ and $k=40$ (three or four digits).

# %%
lnw_per_n = None
check(lnw_per_n, "f4o_lnw_per_n_100_40")

# %% [markdown]
# ## 3. Building g(x) (main track, 15 min)
#
# The melting lens has two ideal phase models. For each, the pure-end values
# $g^\circ_A$ and $g^\circ_B$ are straight lines in $T$. Its cost curve is the
# straight line between the pure ends plus the mixing term:
#
# $$g(x)=(1-x)\,g^\circ_A+x\,g^\circ_B+RT\big[x\ln x+(1-x)\ln(1-x)\big].$$
#
# In `day3_core` each model stores the end line as `a + b*x` ($a=g^\circ_A$,
# $b=g^\circ_B-g^\circ_A$).

# %%
lens = d.lens_models(T_LENS)
for phase, m in lens.items():
    print(f"{phase:6s}: g°A = {m.a:9.1f}   g°B = {m.a + m.b:9.1f}   (J/mol at {T_LENS:.0f} K)")
RT = R * T_LENS
print(f"RT = {RT:.1f} J/mol")

# %% [markdown]
# Build LIQUID at $x=0.3$ from its two pieces and compare with the model's own
# value. The `confirm` line checks the lesson value from step 08.

# %%
x = 0.3
m = lens["LIQUID"]
end_line = m.a + m.b * x                       # the straight line between the pure ends
mixing = RT * float(d.q(x))                    # -T times the mixing entropy
g_built = end_line + mixing
print(f"end line {end_line:.1f} + mixing {mixing:.1f} = {g_built:.2f}")
confirm(g_built, float(m.g(x)), "g_LIQUID(0.3) built by hand equals the model", tol=1e-9)

# %% [markdown]
# Draw both curves. Where they cross, the cheaper phase changes; between their
# common tangent's touching points a split beats both (step 09).

# %%
xs = np.linspace(0.0, 1.0, 401)
fig, ax = plt.subplots(figsize=(7, 3.6))
for phase, colour in (("SOLID", SOLID_C), ("LIQUID", LIQUID_C)):
    ax.plot(xs, lens[phase].g(xs), color=colour, label=phase)
    ax.plot([0, 1], [lens[phase].a, lens[phase].a + lens[phase].b], "--", color=colour, lw=1)
ax.set(xlabel="B atom fraction x", ylabel="g (J/mol atoms)", title=f"The melting lens at {T_LENS:.0f} K: curves and end lines")
ax.legend(); plt.show()

# %% [markdown]
# ### Your turn: build one value
#
# 1. The mixing term at $x=0.4$ and 1400 K (negative, J/mol atoms).
# 2. $g_{\text{LIQUID}}(0.3)$ in J/mol atoms.

# %%
mixing_04 = None   # J/mol atoms
g_liquid_03 = None # J/mol atoms
check(mixing_04, "f4o_mixing_04")
check(g_liquid_03, "f4o_g_liquid_03")

# %% [markdown]
# ## 4. Chemical potentials: a small addition, and a formula (main track, 15 min)
#
# $\mu_B$ is the change of the total Gibbs energy per mole of B added, for a
# small addition at fixed $T$, $p$ and amount of A. Take a sample with
# $n_A=0.7$ and $n_B=0.3$ mol of LIQUID. Its total energy is
# $G=(n_A+n_B)\,g\big(n_B/(n_A+n_B)\big)$. Add a little B and divide.

# %%
def G_total(nA, nB):
    """Total Gibbs energy of nA + nB moles of LIQUID, in J."""
    return (nA + nB) * float(lens["LIQUID"].g(nB / (nA + nB)))

nA, nB, small = 0.7, 0.3, 1e-6
mu_B_added = (G_total(nA, nB + small) - G_total(nA, nB)) / small
print(f"mu_B by a small addition: {mu_B_added:.2f} J/mol")

# %% [markdown]
# For an ideal phase there is a formula: $\mu_B=g^\circ_B+RT\ln x$ (and
# $\mu_A=g^\circ_A+RT\ln(1-x)$). The same numbers are the end heights of the
# tangent at $x$: the tangent's slope is $\mu_B-\mu_A$, and it touches the curve
# at $x$. All three routes must agree.

# %%
mu_B_formula = m.a + m.b + RT * math.log(x)
mu_A_formula = m.a + RT * math.log(1 - x)
slope = float(m.slope(x))                      # dg/dx at x, from the model
mu_A_tangent = float(m.g(x)) - slope * x       # the tangent's height at x = 0
print(f"formula: mu_A = {mu_A_formula:.2f}, mu_B = {mu_B_formula:.2f}")
print(f"tangent: mu_A = {mu_A_tangent:.2f}, mu_B = {mu_A_tangent + slope:.2f}")
assert abs(mu_B_added - mu_B_formula) < 0.05, "the small addition and the formula disagree"
assert abs(mu_A_tangent - mu_A_formula) < 1e-6, "the tangent's end height is not mu_A"

# %% [markdown]
# In optimisation words: these are the prices of A and B atoms at this state. On step 09
# the common tangent of two coexisting phases gives one pair of prices that
# both phases share; in the menu LP they are the duals of the two rows.
#
# ### Your turn: one price
#
# What is $\mu_B$ of LIQUID at $x=0.3$ and 1400 K, in J/mol?

# %%
mu_b_liquid_03 = None   # J/mol
check(mu_b_liquid_03, "f4o_mu_b_liquid_03")

# %% [markdown]
# ## 5. The affine shift: only differences matter (main track, 10 min)
#
# Every element's zero is a chosen reference. Adding the same straight line
# $a+bx$ to every phase model's curve must therefore change no split. It should
# only move the prices: $\mu_A$ by $a$ and $\Delta\mu=\mu_B-\mu_A$ by $b$.
#
# Test it on the step 10 menu with the menu solver `d.solve_master`. It
# returns the amounts `f`, the cheapest energy `G_up` and the line `mu_A`,
# `d_mu`.
#
# **Predict first:** do the amounts change?

# %%
menu = d.menu_states(lens, [0.1, 0.3, 0.5, 0.7, 0.9])
z = 0.40
before = d.solve_master(menu, z)
a, b = 1000.0, -500.0                                      # the line added to every curve, J/mol
shifted_menu = [d.State(s.phase, s.x, s.g + a + b * s.x) for s in menu]
after = d.solve_master(shifted_menu, z)

# %%
print("same amounts:", np.allclose(before.f, after.f))
print(f"mu_A moved by {after.mu_A - before.mu_A:.6f}   d_mu moved by {after.d_mu - before.d_mu:.6f}")
assert np.allclose(before.f, after.f), "the shift changed the amounts"
assert abs(after.mu_A - before.mu_A - a) < 1e-6 and abs(after.d_mu - before.d_mu - b) < 1e-6, "the prices moved wrongly"

# %% [markdown]
# In LP terms: adding the same affine function of the constraint rows to every
# cost moves the optimal value and the duals, not the optimal amounts. That is
# why the energies in the advanced steps are large negative numbers, and why only
# differences carry meaning.
#
# ### Your turn: the shift of the exchange price
#
# Somebody adds $a+bx$ with $a=300$ and $b=2000$ J/mol to every curve. By how
# much does $\Delta\mu$ change?

# %%
d_mu_shift = None   # J/mol
check(d_mu_shift, "f4o_d_mu_shift")

# %% [markdown]
# ## 6. Bending: Ω against 2RT, metastable and unstable (main track, 15 min)
#
# The regular solution of step 03 part B is step 02's ALPHA plus $\Omega x(1-x)$,
# with $\Omega=20000$ J/mol. Its second derivative is
#
# $$g''(x)=RT\Big(\frac1x+\frac1{1-x}\Big)-2\Omega .$$
#
# The first part is smallest at $x=0.5$, where it is $4RT$. So the curve bends
# down somewhere exactly when $\Omega>2RT$.

# %%
reg = d.regular_models(T_REG)["ALPHA"]
print(f"Omega = {reg.w:.0f} J/mol, 2RT = {2 * R * T_REG:.1f} J/mol, Omega/RT = {reg.w / (R * T_REG):.3f}")
for xx in (0.15, 0.5):
    print(f"g''({xx}) = {float(reg.curvature(xx)) / 1000:+.1f} kJ/mol atoms")

# %% [markdown]
# **Predict first:** a uniform sample at $z=0.15$, and one at $z=0.50$: stable,
# metastable or unstable? The binodal (where one tangent touches the curve
# twice) and the spinodal (where the bending changes sign) decide it.

# %%
gap = bf.regular_binodal(T_REG)
binodal, spinodal = gap["compositions"], gap["spinodal"]
print("binodal", [round(v, 3) for v in binodal], "  spinodal", [round(v, 3) for v in spinodal])

def classify(zz):
    """Stable, metastable or unstable for a uniform sample at zz."""
    if gap["status"] == "single_phase":
        return "stable"            # above the critical temperature: no gap, the curve bends up everywhere
    if spinodal[0] < zz < spinodal[1]:
        return "unstable"          # bends down: any small change lowers g
    if binodal[0] < zz < binodal[1]:
        return "metastable"        # bends up, but a split is lower
    return "stable"

# %%
for zz in (0.05, 0.15, 0.5):
    print(f"z = {zz}: {classify(zz)}   (g'' = {float(reg.curvature(zz)) / 1000:+.1f} kJ/mol atoms)")
if T_REG == 800.0:   # the checks hold for the page's 800 K; at other temperatures, read the printout instead
    assert classify(0.15) == "metastable" and float(reg.curvature(0.15)) > 0, "0.15 should bend up but be metastable"
    assert classify(0.5) == "unstable" and float(reg.curvature(0.5)) < 0, "0.50 should bend down"

# %% [markdown]
# The bulk model has no barrier: a metastable sample stays because forming a
# small region of the new composition costs interface energy, which the model
# leaves out, and because atoms must move. A calculation that promises
# equilibrium must still find the split (step 15).
#
# ### Your turn: bending
#
# 1. What is $2RT$ at 800 K, in J/mol?
# 2. Classify the uniform sample at $z=0.50$: type "stable", "metastable" or
#    "unstable".

# %%
two_rt_800 = None   # J/mol
class_050 = None    # a word
check(two_rt_800, "f4o_two_rt_800")
check(class_050, "f4o_class_050")

# %% [markdown]
# ## 7. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Set `T_BATH = 950.0` in section 0 and rerun section 1. Does the sample
#   melt? Explain with the sign of $\Delta G$ and of the total entropy change.
# - Set `T_REG = 1250.0` and rerun section 6. What happened to the binodal and
#   the spinodal, and why? (Hint: compare $\Omega$ with $2RT$.)
#
# **Optimisation flavour: complete a function, then one deeper exercise.**
#
# Complete `mu_pair`: for an ideal phase model `m` (with `m.a`, `m.b`) at
# composition `x` and temperature `T`, return `(mu_A, mu_B)` from the formulas
# of section 4.

# %%
def mu_pair(m, x, T):
    """The two chemical potentials of an ideal phase model at x."""
    return None   # replace with (mu_A, mu_B)

answer = mu_pair(lens["SOLID"], 0.5, T_LENS)
check(None if answer is None else answer[1], "f4o_mu_pair")

# %% cellView="form"
#@title After your attempt: a solution of mu_pair
def mu_pair_solution(m, x, T):
    RT_ = R * T
    return m.a + RT_ * math.log(1 - x), m.a + m.b + RT_ * math.log(x)   # g°A + RT ln(1-x), g°B + RT ln x

print(mu_pair_solution(lens["SOLID"], 0.5, T_LENS))

# %% [markdown]
# **Deeper exercise (operations research): closed-form pricing.** On step 13 the pricing step
# asks: given a line $\mu_A+\Delta\mu\,x$, which state of an ideal phase model
# lies deepest below it? Write the gap
# $g(x)-\mu_A-\Delta\mu\,x=a+bx+RT[x\ln x+(1-x)\ln(1-x)]-\mu_A-\Delta\mu\,x$,
# set its slope $b-\Delta\mu+RT\ln\frac{x}{1-x}$ to zero, and solve for $x$:
#
# $$x^*=\frac{1}{1+e^{-(\Delta\mu-b)/RT}} .$$
#
# The gap is convex (its second derivative is $RT/(x(1-x))>0$), so this
# stationary point is the global minimum. Apply it to SOLID at the step 10
# line (`before.mu_A`, `before.d_mu` from section 5) and compare with
# `d.price_ideal`. Give $x^*$.

# %%
x_star = None
check(x_star, "f4o_x_star")

# %% cellView="form"
#@title After your attempt: closed-form pricing against the course helper
solid = lens["SOLID"]
x_s = 1 / (1 + math.exp(-(before.d_mu - solid.b) / RT))
depth = float(solid.g(x_s)) - before.mu_A - before.d_mu * x_s
helper = d.price_ideal(solid, before.mu_A, before.d_mu)
print(f"by hand: x* = {x_s:.5f}, depth {depth:.2f}   helper: x* = {helper.x:.5f}, depth {helper.depth:.2f}")
assert abs(x_s - helper.x) < 1e-12 and abs(depth - helper.depth) < 1e-9, "hand formula and helper disagree"

# %% [markdown]
# ## Recap
#
# - For a closed sample in a heat bath, total entropy up and $G$ of the sample
#   down are the same statement; equilibrium is the allowed state of lowest $G$,
#   and kinetics decides whether it is reached.
# - Counting arrangements gives the mixing term: $\ln W/N\to-[x\ln x+(1-x)\ln(1-x)]$.
# - A cost curve is the end line plus $RT[x\ln x+(1-x)\ln(1-x)]$ (plus
#   $\Omega x(1-x)$ for a regular solution).
# - Chemical potentials are prices: a small addition, a formula, and the end
#   heights of the tangent all give the same numbers.
# - Adding $a+bx$ to every curve changes no split, only the prices.
# - $\Omega>2RT$ makes the curve bend down: between binodal and spinodal a
#   uniform state is metastable, inside the spinodal unstable.
#
# **Next:** notebook f4c turns the menu into a linear programme and reads its
# prices. On the website: steps 08 (energy, phases and cost curves) and
# 09 (temperature, prices, metastability and CALPHAD). Cards: why minimise G, H and
# S, where x ln x comes from, building g(x), what Ω does, metastable or unstable.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers.
