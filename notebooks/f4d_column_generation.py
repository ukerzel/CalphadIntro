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
# # f4d · Find the missing state: column generation (advanced steps 13–14)
#
# **In plain words.** The menu of step 10 was too coarse: the curves dip below
# its line between the dots. Instead of listing every possible state, ask one
# question again and again: is anything below my line? Add the deepest state,
# solve the menu again, and repeat. Each round also gives a ceiling and a floor,
# so you always know how far from the truth you can still be.
#
# **Learning goals.** After this notebook you can
#
# 1. start the search from a menu, from the two pure ends, and recognise a
#    start that cannot work;
# 2. do one round by hand: add a state, solve, draw the new line;
# 3. write the whole loop in a few lines and compare it with the course helper;
# 4. report a ceiling, a floor (raw and best so far) and the remaining
#    uncertainty after every round, also for a run you stop early;
# 5. (dive deeper) say what pycalphad does in the same three stages, and why
#    its sampled grid gets sparse when the number of elements grows.
#
# **What you need.** Steps 10–14 of the course, or notebook f4c, or at
# least these cards: reading a line, floor and ceiling, reduced cost, column
# generation, how ceiling, floor and remaining uncertainty fit together.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Where the search starts | main | 10 min |
# | 2 | One round by hand | main | 15 min |
# | 3 | The deepest dip has a formula | main | 10 min |
# | 4 | The loop | main | 15 min |
# | 5 | Ceiling and floor in every round | main | 10 min |
# | 6 | A run stopped early | main | 5 min |
# | 7 | What a CALPHAD program does | dive deeper | 15 min |
# | 8 | Exercises | both | 25 min |
#
# **Coming from materials.** Every round asks "which composition, at the current
# prices, would lower the energy most?": the largest driving force, asked for
# every composition at once. The answer moves the line towards the common
# tangent of step 03.
#
# **Coming from operations research.** This is column generation with a restricted master (the
# menu LP), exact pricing (the ideal phase models have a closed form) and the
# Lagrangian bound with one convexity row. New is the physical meaning of each
# piece.
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
# - `T`: the temperature in K (the melting lens of step 03 part C);
# - `z`: the overall B atom fraction of the sample;
# - `MENU_X`: the dots of the starting menu, the same for both phase models;
# - `TOL`: stop when the remaining uncertainty is at most this, J/mol atoms.

# %%
T = 1400.0                          # K
z = 0.40                            # overall B atom fraction of the sample
MENU_X = [0.1, 0.3, 0.5, 0.7, 0.9]  # the step 10 menu
TOL = 1e-6                          # J/mol atoms
DEFAULTS = (T, z, MENU_X) == (1400.0, 0.40, [0.1, 0.3, 0.5, 0.7, 0.9])   # are these the page's numbers?

# %% [markdown]
# `day3_core` is the small library behind every number on the advanced steps of the website.
# Here we use its two lens phase models (`lens_models`), its menu solver
# (`solve_master`, the linear programme of notebook f4c) and its pricing step.
# Colours follow the website: SOLID blue, LIQUID orange.

# %%
import math
import numpy as np
import matplotlib.pyplot as plt
from course.self_study import day3_core as d

SOLID_C, LIQUID_C, LINE_C = "#2445c4", "#cf4418", "#8f6400"   # the website's colours
COLOUR = {"SOLID": SOLID_C, "LIQUID": LIQUID_C}
models = d.lens_models(T)            # {'SOLID': model, 'LIQUID': model}; each has .g(x)

# %% [markdown]
# A picture we redraw after every stage: the **gap curve**, each phase model's
# energy minus the current line, with the menu's states as dots. A state below
# zero would lower the energy if it were added. The function only draws; give
# it the line and the states.

# %%
def draw_gap(mu_A, d_mu, states, title, window=(0.2, 0.6), ylim=None):
    xs = np.linspace(window[0], window[1], 801)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for phase, model in models.items():
        ax.plot(xs, model.g(xs) - (mu_A + d_mu * xs), color=COLOUR[phase], label=phase)
    for s in states:
        ax.plot(s.x, s.g - (mu_A + d_mu * s.x), "o", color=COLOUR[s.phase])
    ax.axhline(0, color="black", lw=0.8)
    ax.set(xlim=window, ylim=ylim, xlabel="B atom fraction x", ylabel="gap (J/mol atoms)", title=title)
    ax.legend(); plt.show()

# %% [markdown]
# ## 1. Where the search starts (main track, 10 min)
#
# Column generation needs a first menu, the *seed*, that can make the sample at
# all: at least one dot left of $z$ and one right of it (or one exactly at $z$).
# Our first seed is the menu of step 10.

# %%
menu = d.menu_states(models, MENU_X)        # list of states: phase, x and g
master = d.solve_master(menu, z)
print(f"ceiling G_up = {master.G_up:.2f}; line mu_A = {master.mu_A:.1f}, d_mu = {master.d_mu:.1f}")
if DEFAULTS:   # lesson values exist only for the page's own numbers
    confirm(master.G_up, -20429.542431, "The step 10 menu's cheapest mixture", tol=1e-5)

# %% [markdown]
# A second seed needs no menu at all: the two pure ends, $x=0$ and $x=1$. At the
# ends the mixing term is zero, so the energies are finite (the helper uses
# $0\ln0=0$). The pure ends can make any $z$ by the lever rule.

# %%
ends = d.menu_states(models, [0.0, 1.0])
for s in ends:
    print(f"{s.phase:6s} x = {s.x:.0f}: g = {s.g:.1f}")
print(f"ceiling from the pure ends: {d.solve_master(ends, z).G_up:.2f}")

# %% [markdown]
# **Predict first:** what happens if every dot of the seed lies right of $z$?
# The solver should refuse: no non-negative amounts can make $z=0.40$ from
# dots at 0.6 and 0.8. The next cell catches the solver's message.

# %%
bad = d.menu_states(models, [0.6, 0.8])
try:
    d.solve_master(bad, z)
except ValueError as message:
    print("the solver says:", message)

# %% [markdown]
# The fix is to add a dot on the other side of $z$; any one will do. Pure A
# ($x=0$) is always available.

# %%
fixed = bad + d.menu_states(models, [0.0])
print(f"with pure A added: ceiling {d.solve_master(fixed, z).G_up:.2f}")

# %% [markdown]
# ## 2. One round by hand (main track, 15 min)
#
# Step 12 found the deepest dip of the step 10 line: SOLID near $x=0.4489$. We
# add that state, printed as $x=0.44887$. Its energy comes from the model,
# rounded to two decimals as on step 13.

# %%
x_new = 0.44887
g_new = round(float(models["SOLID"].g(x_new)), 2)
g_liq = round(float(models["LIQUID"].g(0.3)), 2)       # the LIQUID dot that stays in use
print(f"new SOLID state: x = {x_new}, g = {g_new}; LIQUID x = 0.3, g = {g_liq}")

# %% [markdown]
# **Predict first:** with the new state on the menu, which two states make
# $z=0.40$ cheapest? (Step 13 says: LIQUID 0.3 and the new SOLID.) Work the
# lever rule, the energy and the line yourself before running the next cells.
#
# ### Your turn: round 1 by hand
#
# 1. The amount of the new SOLID state, $f_S=(z-0.3)/(x_{\text{new}}-0.3)$.
# 2. The new ceiling, $f_L\,g_L+f_S\,g_S$.
# 3. The new slope $\Delta\mu$ of the line through the two used states.

# %%
f_S = None          # mol atoms per mol sample
G_up_1 = None       # J/mol atoms
d_mu_1 = None       # J/mol
check(f_S, "f4d_f_solid_round1")
check(G_up_1, "f4d_ceiling_round1")
check(d_mu_1, "f4d_d_mu_round1")

# %% cellView="form"
#@title After your attempt: round 1 by hand
f_S_hand = (z - 0.3) / (x_new - 0.3)
G_hand = (1 - f_S_hand) * g_liq + f_S_hand * g_new
slope = (g_new - g_liq) / (x_new - 0.3)
print(f"f_S = {f_S_hand:.3f}, ceiling = {G_hand:.2f}, d_mu = {slope:.1f}, mu_A = {g_liq - slope * 0.3:.1f}")

# %% [markdown]
# Now let the solver do the same round and compare. The helper's state uses
# the unrounded energy, so agreement to about 0.1 J/mol atoms is what to expect.

# %%
round1 = d.solve_master(menu + [d.State("SOLID", x_new, float(models["SOLID"].g(x_new)))], z)
for state, amount in round1.used():
    print(f"uses {state.phase} at x = {state.x}: f = {amount:.3f}")
print(f"ceiling {round1.G_up:.2f}; mu_A = {round1.mu_A:.1f}, d_mu = {round1.d_mu:.1f}")
if DEFAULTS:   # the hand round uses the page's numbers
    assert abs(round1.G_up - G_hand) < 0.1, "hand and solver disagree by more than 0.1 J/mol atoms"

# %%
draw_gap(round1.mu_A, round1.d_mu, round1.states, "Round 1: gap curve against the new line", ylim=(-10, 40))

# %% [markdown]
# The added state now sits on the line (gap zero). The line has tilted, and the
# deepest dip has moved to the LIQUID side, near 0.312: much shallower than
# before, but still below zero.
#
# ## 3. The deepest dip has a formula (main track, 10 min)
#
# For an ideal phase model the gap curve is
#
# $$\mathrm{gap}(x)=a+b\,x+RT\,[x\ln x+(1-x)\ln(1-x)]-\mu_A-\Delta\mu\,x ,$$
#
# where $a+b\,x$ is the straight line between the model's pure ends. It bends
# up everywhere, so its lowest point is where its slope is zero:
# $b-\Delta\mu+RT\ln\frac{x}{1-x}=0$. Solving for $x$ gives
#
# $$x^*=\frac{1}{1+e^{-(\Delta\mu-b)/RT}} .$$
#
# No search is needed: one line of arithmetic per phase model gives the deepest
# state. (Each model stores its $a$ and $b$.)

# %%
def deepest_state(model, mu_A, d_mu):
    x = 1 / (1 + math.exp(-(d_mu - model.b) / (d.R * model.T)))   # where the gap curve is flattest
    return x, float(model.g(x)) - (mu_A + d_mu * x)                 # the state and its gap

for phase, model in models.items():
    x, gap = deepest_state(model, master.mu_A, master.d_mu)
    print(f"{phase:6s}: deepest at x = {x:.5f}, gap {gap:.3f} J/mol atoms")

# %% [markdown]
# Check the formula against the helper's pricing step and against a fine grid.
# A grid can only confirm it from above; the formula is the guarantee.

# %%
for phase, model in models.items():
    x, gap = deepest_state(model, master.mu_A, master.d_mu)
    dip = d.price_ideal(model, master.mu_A, master.d_mu)
    xs = np.linspace(0.001, 0.999, 9999)
    grid_low = (model.g(xs) - (master.mu_A + master.d_mu * xs)).min()
    assert abs(x - dip.x) < 1e-12 and abs(gap - dip.depth) < 1e-9, f"{phase}: formula and helper differ"
    assert grid_low >= gap - 1e-9, f"{phase}: the grid went below the formula's minimum"
print("formula = helper, and no grid point lies below it")

# %% [markdown]
# ### Your turn: the deepest SOLID state of the step 10 line
#
# Use the formula with the step 10 line ($\Delta\mu=-1389.0$), $b=1000$ for
# SOLID and $RT=11640.3$ J/mol. Give $x^*$ to four decimals.

# %%
x_star = None   # B atom fraction
check(x_star, "f4d_closed_form_x")

# %% [markdown]
# ## 4. The loop (main track, 15 min)
#
# Now the whole method in a few lines: solve the menu, read the line, find the
# deepest state of each phase model, stop if none lies below the line,
# otherwise add the deepest one and go round again.
#
# **Predict first:** how many rounds until the deepest dip is smaller than
# 0.003 J/mol atoms?

# %%
states = list(menu)
for k in range(10):
    m = d.solve_master(states, z)                                 # master: menu -> line
    found = [(deepest_state(mod, m.mu_A, m.d_mu), p) for p, mod in models.items()]
    (x, gap), phase = min(found, key=lambda item: item[0][1])     # pricer: the deepest dip
    print(f"round {k}: ceiling {m.G_up:.4f}, deepest dip {gap:.4f} ({phase} at {x:.4f})")
    if gap > -TOL:
        break                                                     # nothing worth adding
    states.append(d.State(phase, x, float(models[phase].g(x))))   # add it, go round again

# %% [markdown]
# The course helper `column_generation` does the same, and also keeps the
# floors (section 5). The two must agree round by round.

# %%
history = d.column_generation(models, menu, z, tol=1e-9, max_iter=40)
for it in history:
    print(f"round {it.k}: ceiling {it.master.G_up:.4f}, deepest dip {it.best.depth:.4f}")
if DEFAULTS:   # lesson values exist only for the page's own numbers
    confirm(history[3].best.depth, -0.002719896, "The deepest dip in round 3", tol=1e-8)

# %% [markdown]
# After the first added state, two more additions bring the deepest dip to
# 0.0027 J/mol atoms, and a fourth to 0.0015. Redraw the gap curve after each
# round. The dips get too small to see on one scale, so each picture zooms in
# to its own dip.

# %%
for it in history[1:5]:
    w = abs(it.best.depth)
    draw_gap(it.master.mu_A, it.master.d_mu, it.master.states, f"Round {it.k}: deepest dip {it.best.depth:.4f}",
             window=(it.best.x - 0.03 * min(1, w) ** 0.5 - 0.002, it.best.x + 0.03 * min(1, w) ** 0.5 + 0.002), ylim=(-1.5 * w, 3 * w))

# %% [markdown]
# The used states approach the true compositions, liquid 0.312 and solid
# 0.441, and the line approaches the common tangent of step 03. Two states of
# the same phase model can be used together for a while (twin dots): they
# stand for one phase between them.

# %%
last = history[-1].master
for state, amount in last.used():
    print(f"{state.phase:6s} x = {state.x:.5f}: f = {amount:.4f}")
if DEFAULTS:   # lesson values exist only for the page's own numbers
    confirm(last.G_up, -20473.124218, "The converged ceiling (the lens answer of step 03)", tol=1e-5)

# %% [markdown]
# ### Your turn: read the rounds
#
# 1. The remaining uncertainty after round 3 (the deepest dip of round 3,
#    as a positive number).
# 2. How many states are added *after the first one* until the deepest dip is
#    below 0.003 J/mol atoms?

# %%
remaining_3 = None      # J/mol atoms, positive
more_states = None      # a whole number
check(remaining_3, "f4d_remaining_round3")
check(more_states, "f4d_more_states")

# %% [markdown]
# ## 5. Ceiling and floor in every round (main track, 10 min)
#
# Every round gives two numbers that bracket the truth:
#
# - the **ceiling** `G_up`: the menu's cheapest mixture, a real mixture;
# - the **floor** `G_low`: the line at $z$ lowered by the deepest dip of the
#   whole curve, $\mu_A+\Delta\mu\,z+\min(0,\text{dip})$.
#
# The ceiling never rises, because the menu only grows. The raw floor can fall
# from one round to the next, because the line moves; every raw floor is
# valid, so we keep the best (highest) one so far.

# %%
print(" round   ceiling        raw floor      best floor     remaining")
for it in history:
    print(f"{it.k:5d}  {it.master.G_up:12.4f}  {it.G_low_raw:12.4f}  {it.G_low_best:12.4f}  {it.gap:12.6f}")

# %%
ups = [it.master.G_up for it in history]
assert all(b <= a + 1e-9 for a, b in zip(ups, ups[1:])), "the ceiling rose: the menu lost a state?"
truth = history[-1].master.G_up
assert all(it.G_low_best <= truth + 1e-8 for it in history), "a floor lies above the answer"
print("ceilings never rise; every floor lies at or below the answer")

# %% [markdown]
# On a logarithmic axis the remaining uncertainty falls by orders of magnitude
# in a few rounds.

# %%
rows = [it for it in history if it.gap > 0]
fig, ax = plt.subplots(figsize=(6, 3))
ax.semilogy([it.k for it in rows], [it.gap for it in rows], "o-", color=LINE_C)
ax.set(xlabel="round", ylabel="ceiling − best floor (J/mol atoms)", title="Remaining uncertainty per round")
plt.show()

# %% [markdown]
# **The floor can fall.** Start from the two pure ends instead. Watch the raw
# floor column: it goes down before it goes up. The best-so-far floor does not.

# %%
from_ends = d.column_generation(models, ends, z, tol=1e-9, max_iter=40)
for it in from_ends[:6]:
    print(f"round {it.k}: raw floor {it.G_low_raw:11.2f}   best floor {it.G_low_best:11.2f}   ceiling {it.master.G_up:11.2f}")
print(f"... {len(from_ends)} rounds in all to a remaining uncertainty of 1e-9, ending at {from_ends[-1].master.G_up:.4f}")

# %% [markdown]
# ## 6. A run stopped early (main track, 5 min)
#
# A real program has a work limit. Stop after one round: what can you say? Not
# "this is the answer", but "the answer lies between this floor and this
# ceiling". If the gap between them is larger than you care about, the result
# is **unresolved**.

# %%
short = d.column_generation(models, menu, z, tol=TOL, max_iter=1)
it = short[-1]
status = "converged" if it.gap <= TOL else "unresolved"
print(f"after {it.k} added state(s): {status}; floor {it.G_low_best:.2f} <= answer <= ceiling {it.master.G_up:.2f}")
print(f"remaining uncertainty {it.gap:.2f} J/mol atoms")

# %% [markdown]
# ### Your turn: the stopped run
#
# What is the remaining uncertainty of the run stopped after one added state?

# %%
remaining_stopped = None   # J/mol atoms
check(remaining_stopped, "f4d_unresolved_remaining")

# %% [markdown]
# ## 7. What a CALPHAD program does (dive deeper, 15 min)
#
# pycalphad 0.11.2 finds an equilibrium in three stages, each with a name
# from the advanced steps:
#
# | Stage in pycalphad | What it does | Name in the advanced steps |
# |---|---|---|
# | grid LP | samples states of every phase and solves the menu LP over them | the menu and its line (steps 10–11) |
# | continuous refinement | a Newton-type solver moves the compositions of the phases in use off the grid and returns new chemical potentials | adding a better state (step 13), done continuously |
# | pricing the grid | checks every sampled state against the new line and adds the phase with the largest driving force, up to ten rounds | the pricing step, with the grid as the search set |
#
# The next cell solves our lens with pycalphad from the same model written as a
# small database (the one step 03 part D uses) and compares the energy with the
# column-generation answer. It takes a few seconds.

# %%
from pycalphad import Database, equilibrium, variables as v
from course.self_study.from_scratch_export import TDB      # the lens as a database text
eq = equilibrium(Database(TDB), ["A", "B"], ["SOLID", "LIQUID"], {v.T: T, v.P: 100000, v.N: 1, v.X("B"): z})
G_pycalphad = float(eq.GM.values.squeeze())
print(f"pycalphad {G_pycalphad:.6f}   column generation {truth:.6f}   difference {G_pycalphad - truth:.2e}")
assert abs(G_pycalphad - truth) < max(1e-4, history[-1].gap + 1e-6), "pycalphad and column generation disagree by more than the remaining uncertainty"

# %% [markdown]
# **Where the effort goes with many elements.** pycalphad's default sample for
# an equilibrium is 60 points per degree of freedom. For a phase with one
# sublattice and $C$ elements that is $60(C-1)$ interior points (plus the pure
# ends and lines between them). The space they must cover has $C-1$ dimensions,
# so the points per direction shrink fast.

# %%
from pycalphad.core.utils import point_sample
for C in (2, 3, 5, 10):
    n = point_sample([C], pdof=60).shape[0]
    print(f"{C:2d} elements: {n:4d} interior points, about {n ** (1 / (C - 1)):5.1f} per direction")

# %% [markdown]
# The binary edges stay well covered; the inside of a many-element phase does
# not. A valley between sparse points can be missed (step 10's coarse-grid
# miss in more dimensions), and a denser grid costs energy evaluations at every
# temperature. Searching for the deepest state by a formula or a branch-and-bound check, as in
# steps 13–16, is the other way out. No speed comparison is made here.
#
# ## 8. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Set `T = 1500.0` in section 0 and rerun. How do the final compositions and
#   the number of rounds change? Compare with the lens of step 03 part C.
# - Set `MENU_X = [0.3, 0.5]` and rerun. Does a smaller seed need more rounds?
#
# **Optimisation flavour: complete a function.** Complete `one_round`: given the current
# list of states, solve the master, price both phase models with
# `deepest_state`, and return the new list of states (unchanged if nothing lies
# below the line by more than `TOL`).

# %%
def one_round(states):
    """Master, pricer, add: one round of column generation."""
    return None   # replace with the new list of states

after = one_round(list(menu))
check(None if after is None else d.solve_master(after, z).G_up, "f4d_ceiling_round1")

# %% cellView="form"
#@title After your attempt: a solution of one_round
def one_round_solution(states):
    m = d.solve_master(states, z)
    found = [(deepest_state(mod, m.mu_A, m.d_mu), p) for p, mod in models.items()]
    (x, gap), phase = min(found, key=lambda item: item[0][1])
    return states if gap > -TOL else states + [d.State(phase, x, float(models[phase].g(x)))]

print(f"ceiling after one round: {d.solve_master(one_round_solution(list(menu)), z).G_up:.2f}")

# %% [markdown]
# **Deeper exercises (operations research).**
#
# 1. Derive the closed-form pricing of section 3 yourself: differentiate the
#    gap, set it to zero, and show that the stationary point is the global
#    minimum on $(0,1)$.
# 2. *One column per phase.* Change the loop so that every round adds the
#    deepest state of *each* phase model that lies below the line, not only the
#    deepest overall. Count the rounds until the remaining uncertainty is at
#    most `TOL`, and compare with one column per round.
# 3. *Best so far.* Explain why every raw floor is a valid lower bound, so that
#    the highest one seen so far is valid too, although the raw floor itself
#    can fall from one round to the next (section 5, start from the pure ends).

# %% cellView="form"
#@title After your attempt: the derivation, one column per phase, best so far
# 1. d(gap)/dx = b - d_mu + RT ln(x/(1-x)); the second derivative RT/(x(1-x)) > 0,
#    so the gap curve is convex and its single stationary point is the global minimum.
def rounds_until(states, per_phase):
    for k in range(50):
        m = d.solve_master(states, z)
        found = [(deepest_state(mod, m.mu_A, m.d_mu), p) for p, mod in models.items()]
        low = m.G_up - floor_of(m, min(g for (_, g), _ in found))
        if low <= TOL:
            return k
        new = [f for f in found if f[0][1] < -TOL] if per_phase else [min(found, key=lambda f: f[0][1])]
        states = states + [d.State(p, x, float(models[p].g(x))) for (x, _), p in new]
    return None

floor_of = lambda m, dip: d.floor(m.mu_A + m.d_mu * z, dip)
print("rounds, one column per round:", rounds_until(list(menu), False), "  one per phase:", rounds_until(list(menu), True))
# 3. Each raw floor is the line slid below every state of both phase models, read at z:
#    no mixture can lie below it. A valid bound stays valid after the line moves on,
#    so the maximum over all rounds is a valid floor too.

# %% [markdown]
# ## Recap
#
# - Column generation starts from a seed that can make the sample (a menu, or
#   the pure ends) and repeats: master → line → deepest dip → add the state.
# - For ideal phase models the deepest dip has a formula, so pricing is exact.
# - After the first added state, two more bring the deepest dip to 0.0027
#   J/mol atoms; the answer converges to the common tangent of step 03.
# - Every round has a ceiling (never rises) and a floor (keep the best so far);
#   a run stopped early is reported as an interval, "unresolved".
# - pycalphad works in the same three stages, with a sampled grid as its search
#   set; with many elements that grid gets sparse.
#
# **Next:** notebook f4e changes the model to the regular solution, where the
# deepest dip has no formula and a local search can miss it. On the website:
# steps 13 (find a missing state) and 14 (ceiling, floor and the remaining
# uncertainty). Cards: column generation, what a grid can miss, twin dots, does
# my CALPHAD code do this too?, how ceiling, floor and remaining uncertainty fit
# together.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers.
