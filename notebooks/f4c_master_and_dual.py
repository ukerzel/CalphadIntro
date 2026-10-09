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
# # f4c · The menu, its line and its prices (advanced steps 10–12)
#
# **In plain words.** A computer that "calculates an equilibrium" chooses
# amounts of a list of candidate states so that every atom is kept and the
# energy is as low as possible. It also returns two extra numbers. In this
# notebook you find out that they are the chemical potentials, and that they
# draw a line under the states: a floor that holds for the list, but not for
# the states the list left out.
#
# **Learning goals.** After this notebook you can
#
# 1. write the menu of step 10 as a linear programme and solve it;
# 2. turn the solver's two multipliers into the line $\mu_A+\Delta\mu\,x$ and
#    check that it is a floor for the menu;
# 3. show with a gap curve that the same line is *not* a floor for the
#    continuous curves, and how far to lower it so that it is;
# 4. (dive deeper) read off the range of $z$ over which the line stays put, and
#    see a line that can rotate.
#
# **What you need.** Steps 10–12 of the course, or at least their cards:
# the lever rule, reading a line, floor and ceiling, dual or shadow price,
# reduced cost. No derivatives are needed.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | The menu by hand | main | 15 min |
# | 2 | The menu as a linear programme | main | 15 min |
# | 3 | The line and its prices | main | 15 min |
# | 4 | The gap curve: a floor for the menu only | main | 15 min |
# | 5 | Moving z: ranging | dive deeper | 10 min |
# | 6 | A line that can rotate | dive deeper | 10 min |
# | 7 | Exercises | both | 20 min |
#
# **Coming from materials.** You have done every step of this by hand on
# steps 00–04: the lever rule, the chord rule, the tangent and its end heights.
# The new part is the computer's view of it, and the idea of a *floor*.
#
# **Coming from operations research.** This is a two-row LP over candidate columns, its dual and
# complementary slackness. The new part is what each dual means physically, and
# that the column set is a sample of a continuum.
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
RELEASE = "v0.2.0"
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
# The cell below holds every number this notebook starts from. Leave them as
# they are for the first run: the "Your turn" checks expect these values. Later,
# change one number at a time and rerun everything below it.
#
# - `T`: the temperature in K (the melting lens of step 03 part C at 1400 K);
# - `z`: the overall B atom fraction of the sample;
# - `MENU_X`: the compositions of the menu's dots, the same for both phase models.

# %%
T = 1400.0                         # K
z = 0.40                           # overall B atom fraction of the sample
MENU_X = [0.1, 0.3, 0.5, 0.7, 0.9]  # the step 10 menu; z is not on it

# %% [markdown]
# Three libraries and one course module. `day3_core` is the small library that
# also produced every number on the advanced steps of the website, so your results here and
# the pages agree digit for digit. It contains the two phase models of the lens
# (`lens_models`), the menu solver and the pricing step; this notebook opens
# each of them up.
#
# Colours follow the website: SOLID blue, LIQUID orange.

# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from course.self_study import day3_core as d

SOLID_C, LIQUID_C, LINE_C = "#2445c4", "#cf4418", "#8f6400"   # the website's colours
models = d.lens_models(T)          # {'SOLID': model, 'LIQUID': model}; each has .g(x)

# %% [markdown]
# ## 1. The menu by hand (main track, 15 min)
#
# A *state* is one phase model at one composition: a dot on the $g$–$x$ plot.
# The menu has five SOLID dots and five LIQUID dots. `models[p].g(x)` returns
# the molar Gibbs energy in J per mole of atoms.

# %%
dots = []                                   # (phase, x, g) for every dot of the menu
for phase in ("SOLID", "LIQUID"):
    for x in MENU_X:
        dots.append((phase, x, float(models[phase].g(x))))
for phase, x, g in dots:
    print(f"{phase:6s} x = {x:.1f}   g = {g:10.2f} J/mol atoms")

# %% [markdown]
# A sample at $z=0.40$ can be made from one dot left of 0.40 and one dot right
# of it. The lever rule fixes the amounts:
#
# $$f_{\text{right}}=\frac{z-x_{\text{left}}}{x_{\text{right}}-x_{\text{left}}},\qquad f_{\text{left}}=1-f_{\text{right}},$$
#
# and the mixture's energy is $f_{\text{left}}\,g_{\text{left}}+f_{\text{right}}\,g_{\text{right}}$
# (the chord rule).
#
# ### Your turn: one mixture
#
# Find the energy of the mixture of LIQUID at 0.3 and SOLID at 0.5 that makes
# $z=0.40$. Use the printed energies.

# %%
g_pair = None   # J/mol atoms
check(g_pair, "f4c_g_menu_pair")

# %% [markdown]
# **Predict first.** Of all pairs that bracket 0.40, which do you expect to be
# the cheapest? The next cell tries every pair. It is a plain double loop: for
# every left dot and every right dot it applies the lever rule.

# %%
best = None
for pl, xl, gl in dots:
    for pr, xr, gr in dots:
        if xl < z < xr:
            f_right = (z - xl) / (xr - xl)
            G = (1 - f_right) * gl + f_right * gr
            if best is None or G < best[0]:
                best = (G, pl, xl, pr, xr, f_right)
print("cheapest pair: %s %.1f and %s %.1f, amounts %.3f and %.3f, G = %.2f" % (best[1], best[2], best[3], best[4], 1 - best[5], best[5], best[0]))

# %% [markdown]
# ## 2. The menu as a linear programme (main track, 15 min)
#
# The loop above tried pairs. A computer states the problem once and lets a
# solver search:
#
# - **variables:** the amounts $f_j\ge0$ of every dot $j$;
# - **objective:** the total energy $\sum_j f_j g_j$, as small as possible;
# - **constraints:** $\sum_j f_j=1$ (all atoms are somewhere) and
#   $\sum_j f_j x_j=z$ (all B atoms are somewhere).
#
# In `linprog` this is `c` (the energies), `A_eq` (two rows: ones and the
# compositions) and `b_eq` (1 and $z$). `method="highs-ds"` asks for the dual
# simplex method, which returns a *basic* answer: at most as many dots with a
# non-zero amount as there are constraint rows, here two.

# %%
c = np.array([g for _, _, g in dots])                      # energy of each dot
A_eq = np.array([[1.0] * len(dots), [x for _, x, _ in dots]])  # row 1: amounts; row 2: B atoms
b_eq = np.array([1.0, z])
result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs-ds")
f = result.x                                               # amounts, mol atoms per mol sample
G_up = result.fun                                          # the cheapest energy of the menu
print(result.message)

# %%
for (phase, x, g), amount in zip(dots, f):
    if amount > 1e-12:
        print(f"uses {phase} at x = {x:.1f}: f = {amount:.4f}")
print(f"G_up = {G_up:.2f} J/mol atoms   (the best mixture of the menu: a ceiling)")

# %% [markdown]
# Two checks every LP answer must pass, whoever solved it: the amounts keep the
# atoms, and no amount is negative. The messages say in words what went wrong
# if a check fails.

# %%
assert abs(f.sum() - 1) < 1e-9, f"amounts sum to {f.sum():.6f}, not 1"
assert abs(f @ A_eq[1] - z) < 1e-9, f"B atoms sum to {f @ A_eq[1]:.6f}, not z = {z}"
assert f.min() > -1e-12, f"a negative amount: {f.min():.3g}"
if (T, z, MENU_X) == (1400.0, 0.40, [0.1, 0.3, 0.5, 0.7, 0.9]):   # only the page's own numbers have a lesson value to compare with
    confirm(G_up, -20429.542431, "The menu's cheapest mixture", tol=1e-5)
else:
    print("You changed the numbers in section 0: no lesson value to compare with.")

# %% [markdown]
# ## 3. The line and its prices (main track, 15 min)
#
# Besides the amounts, the solver returns one *multiplier* per constraint row:
# how much the optimal energy changes when that row's right-hand side changes a
# little, as long as the same dots stay in use (section 6 shows a case where
# they are not unique). `result.eqlin.marginals` holds them. For our rows $(1, z)$ they are
# exactly the intercept and the slope of a straight line:
#
# - $\mu_A$, the line's height at $x=0$ (from the "amounts" row);
# - $\Delta\mu=\mu_B-\mu_A$, its slope (from the "B atoms" row).
#
# The sign convention matters: SciPy reports $\partial G_{\text{up}}/\partial b$,
# which is what we want here (some other solvers report the negative).

# %%
mu_A, d_mu = result.eqlin.marginals   # d(G_up)/d(1) and d(G_up)/dz: the line's intercept and slope
mu_B = mu_A + d_mu                    # the line's height at x = 1
print(f"mu_A = {mu_A:.1f}   d_mu = {d_mu:.1f}   mu_B = {mu_B:.1f}   (J/mol)")

# %% [markdown]
# **Check 1: the line passes through the used dots**, so its height at $z$ is
# the ceiling. This is strong duality for the menu: the best floor equals the
# best mixture.

# %%
line_at_z = mu_A + d_mu * z
assert abs(line_at_z - G_up) < 1e-8, f"line at z is {line_at_z:.4f}, the ceiling {G_up:.4f}"
print(f"line at z = {line_at_z:.2f} = ceiling {G_up:.2f}")

# %% [markdown]
# **Check 2: no dot lies below the line.** Subtract the line's height from
# every dot's energy. This difference is the dot's *gap* (its reduced cost).
# Used dots have gap zero; every other dot must have gap zero or more, or the
# line would not be a floor for the menu.

# %%
gaps = [g - (mu_A + d_mu * x) for _, x, g in dots]
for (phase, x, _), gap in zip(dots, gaps):
    print(f"{phase:6s} x = {x:.1f}: gap = {gap:8.1f}")
assert min(gaps) > -1e-8, f"a dot lies {min(gaps):.3g} J/mol below the line"

# %% [markdown]
# **Check 3: the slope is the price of B.** Move $z$ a little, solve again and
# compare the change of the cheapest energy with $\Delta\mu\times$ the change.

# %%
dz = 0.001
moved = linprog(c, A_eq=A_eq, b_eq=[1.0, z + dz], bounds=(0, None), method="highs-ds")
print(f"energy change {moved.fun - G_up:.4f}  against  d_mu * dz = {d_mu * dz:.4f}")
assert abs((moved.fun - G_up) - d_mu * dz) < 1e-6, "the slope is not the price of B"

# %% [markdown]
# ### Your turn: read the line
#
# 1. What is $\mu_B$, the line's height at $x=1$?
# 2. Nudge $z$ by $+0.01$. By how much does the cheapest energy change?

# %%
mu_B_answer = None   # J/mol
nudge = None         # J/mol atoms, with its sign
check(mu_B_answer, "f4c_mu_b_menu")
check(nudge, "f4c_nudge")

# %% [markdown]
# ## 4. The gap curve: a floor for the menu only (main track, 15 min)
#
# The line lies under every dot of the menu. Does it lie under the whole curves?
# Draw the gap for every composition of each phase model: $g(x)$ minus the line.
#
# **Predict first:** will the curves stay at or above zero between the dots?

# %%
xs = np.linspace(0.001, 0.999, 999)
fig, ax = plt.subplots(figsize=(7, 3.6))
for phase, colour in (("SOLID", SOLID_C), ("LIQUID", LIQUID_C)):
    ax.plot(xs, models[phase].g(xs) - (mu_A + d_mu * xs), color=colour, label=phase)
    ax.plot(MENU_X, [g for p, _, g in dots if p == phase] - (mu_A + d_mu * np.array(MENU_X)), "o", color=colour)
ax.axhline(0, color="black", lw=0.8)
ax.set(xlim=(0.2, 0.6), ylim=(-100, 600), xlabel="B atom fraction x", ylabel="gap (J/mol atoms)", title="Gap curve against the menu's line")
ax.legend(); plt.show()

# %% [markdown]
# Between the dots the SOLID curve dips below zero. The menu's line is a floor
# for mixtures of the menu, not for every state. How deep does the curve go?
# For these ideal phase models the deepest point of the gap curve has a
# formula; `d.deepest` applies it to both phase models and returns the deepest
# dip overall and each phase model's own dip.

# %%
deepest, dips = d.deepest(models, mu_A, d_mu)
for phase, dip in dips.items():
    print(f"{phase:6s}: deepest point at x = {dip.x:.4f}, gap {dip.depth:.2f} J/mol atoms")
assert deepest.depth < 0, "expected the curves to dip below the menu's line"

# %% [markdown]
# Lower the line, keeping its slope, by the deepest dip. Now no state of either
# phase model lies below it: check it on a fine grid. (A grid can only test
# this; the formula for the deepest point is what guarantees it.)

# %%
lowered = mu_A + deepest.depth            # the same slope, moved down by the deepest dip
for phase in ("SOLID", "LIQUID"):
    lowest = (models[phase].g(xs) - (lowered + d_mu * xs)).min()
    assert lowest > -1e-6, f"{phase} still dips {lowest:.3g} below the lowered line"
G_low = lowered + d_mu * z                # a floor for every state: step 14's floor
print(f"floor {G_low:.2f} <= truth <= ceiling {G_up:.2f}; remaining uncertainty {G_up - G_low:.1f} J/mol atoms")

# %% [markdown]
# ### Your turn: read the gap curve
#
# 1. What is the gap of the SOLID dot at $x=0.3$?
# 2. How deep is the deepest dip of the whole curve (a negative number)?

# %%
gap_solid_03 = None   # J/mol atoms
deepest_dip = None    # J/mol atoms, negative
check(gap_solid_03, "f4c_gap_solid_03")
check(deepest_dip, "f4c_deepest_dip")

# %% [markdown]
# ## 5. Moving z: ranging (dive deeper, 10 min)
#
# Keep the menu and move $z$. Inside the range where the same two dots stay in
# use, the line does not move: the prices stay the same across the two-phase
# region. Outside it the used dots, and the line, change.

# %%
for zz in (0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55):
    r = linprog(c, A_eq=A_eq, b_eq=[1.0, zz], bounds=(0, None), method="highs-ds")
    used = [f"{p} {x:.1f}" for (p, x, _), a in zip(dots, r.x) if a > 1e-12]
    print(f"z = {zz:.2f}: uses {', '.join(used):24s} d_mu = {r.eqlin.marginals[1]:9.1f}")

# %% [markdown]
# For $0.3<z<0.5$ the line is the same. At exactly 0.3 or 0.5 the sample sits
# on a used dot and the solver may return a different line (section 6). The true
# two-phase region of the continuous curves, 0.312 to 0.441, is narrower: the
# coarse menu blurs it.
#
# ## 6. A line that can rotate (dive deeper, 10 min)
#
# Step 03 part D's coarse grid has dots at 0.2, 0.4, 0.6 and 0.8, so the sample
# at 0.40 sits exactly on a dot, and the solver uses that one SOLID dot alone.
# Which line do the multipliers give now? Ask two solver methods.

# %%
coarse = d.menu_states(models, [0.2, 0.4, 0.6, 0.8])
c2 = np.array([s.g for s in coarse])
A2 = np.array([[1.0] * len(coarse), [s.x for s in coarse]])
for method in ("highs-ds", "highs-ipm"):
    r = linprog(c2, A_eq=A2, b_eq=[1.0, z], bounds=(0, None), method=method)
    print(f"{method:9s}: G = {r.fun:.4f}   mu_A = {r.eqlin.marginals[0]:9.2f}   d_mu = {r.eqlin.marginals[1]:9.2f}")

# %% [markdown]
# The energy is the same; the line may not be. Any line through the used dot
# that stays under its neighbours is optimal: its slope can be anything
# between the slopes of the chords to the neighbouring dots on the lower
# envelope. The next cell computes that range from the dots.

# %%
on_grid = [s for s in coarse if abs(s.x - z) < 1e-12]                       # dots exactly at z
if on_grid:
    used = min(on_grid, key=lambda s: s.g)                                  # the cheaper dot at z
    left = max((s.g - used.g) / (s.x - used.x) for s in coarse if s.x < z)  # steepest chord to the left
    right = min((s.g - used.g) / (s.x - used.x) for s in coarse if s.x > z) # shallowest chord to the right
    print(f"every slope between {left:.1f} and {right:.1f} gives an optimal line")
else:
    print(f"z = {z} is not on the coarse grid: the line cannot rotate there")

# %% [markdown]
# Different solvers may pick different members of that range; both are right.
# The card "What if the answer is not unique?" separates this case (a line that
# can rotate) from the other one (several optimal amounts).
#
# ## 7. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Set `z = 0.45` in section 0 and rerun. Which dots are used, and does the
#   line change? Explain with the lever rule.
# - Add 0.44 to `MENU_X` and rerun. By how much does the ceiling drop, and why
#   does one extra dot near the true solid composition help so much?
#
# **Optimisation flavour: complete a function, then one deeper exercise.**
#
# Complete `line_from_basis`: given the two used dots (as `(x, g)` pairs), return
# `(mu_A, d_mu)` by making the line pass through both. Do not call `linprog`.

# %%
def line_from_basis(dot1, dot2):
    """The line through two used dots: two equations, two unknowns."""
    return None   # replace with (mu_A, d_mu)

guess = line_from_basis((0.3, float(models["LIQUID"].g(0.3))), (0.5, float(models["SOLID"].g(0.5))))
check(None if guess is None else guess[1], "f4c_line_from_basis")

# %% cellView="form"
#@title After your attempt: a solution of line_from_basis
def line_from_basis_solution(dot1, dot2):
    (x1, g1), (x2, g2) = dot1, dot2
    slope = (g2 - g1) / (x2 - x1)          # the line rises by g2 - g1 over x2 - x1
    return g1 - slope * x1, slope          # the intercept puts the line through dot1

print(line_from_basis_solution((0.3, float(models["LIQUID"].g(0.3))), (0.5, float(models["SOLID"].g(0.5)))))

# %% [markdown]
# **Deeper exercise (operations research).** Write the dual LP explicitly: maximise
# $\mu_A+\Delta\mu\,z$ subject to $\mu_A+\Delta\mu\,x_j\le g_j$ for every dot,
# with both variables free. Solve it with `linprog` (which minimises, so negate
# the objective) and compare with the marginals. Then test the affine shift: add
# $a+bx$ to every dot's energy, solve the menu again, and show that the amounts
# stay the same while $\mu_A$ moves by $a$ and $\Delta\mu$ by $b$.

# %% cellView="form"
#@title After your attempt: the dual LP and the affine shift
dual = linprog([-1.0, -z], A_ub=np.column_stack([np.ones(len(dots)), [x for _, x, _ in dots]]), b_ub=c,
               bounds=[(None, None), (None, None)], method="highs-ds")
print(f"dual: mu_A = {dual.x[0]:.4f}, d_mu = {dual.x[1]:.4f}, value {-dual.fun:.4f}")
assert np.allclose(dual.x, [mu_A, d_mu]) and abs(-dual.fun - G_up) < 1e-8, "dual and primal disagree"
a, b = 1000.0, -500.0
shifted = linprog(c + a + b * A_eq[1], A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs-ds")
print("same amounts:", np.allclose(shifted.x, f), "  mu_A moved by", round(shifted.eqlin.marginals[0] - mu_A, 6),
      "  d_mu moved by", round(shifted.eqlin.marginals[1] - d_mu, 6))

# %% [markdown]
# ## Recap
#
# - The menu is a two-row linear programme: amounts are the variables, the
#   atom balances the constraints, the energy the objective.
# - Its two multipliers are the line $\mu_A+\Delta\mu\,x$: the chemical
#   potential of A and the exchange price $\mu_B-\mu_A$.
# - The line is a floor for the menu (every dot on or above it) and meets the
#   ceiling there. It is not a floor for the continuous curves: they dip 61.2
#   J/mol atoms below it near SOLID 0.4489.
# - Lowered by the deepest dip, the line is a floor for every state: step 14.
#
# **Next:** notebook f4d adds the missing states one by one (column
# generation). On the website: steps 10 (the menu), 11 (the line) and 12 (the gap
# curve). Cards: the lever rule, reading a line, floor and ceiling, dual or
# shadow price, reduced cost.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers.
