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
# # f4f · Three components: a triangle, a plane and a landscape (advanced step 18, optional)
#
# **In plain words.** Everything from the binary steps carries over to three
# components. The dots now sit on a triangle, the line under the dots becomes a
# tilted plane with three corner heights, and the gap curve becomes a landscape
# over the triangle. The cheapest mixture, the prices, column generation and
# the floor work exactly as before; only the pictures gain a dimension.
#
# **Learning goals.** After this notebook you can
#
# 1. read a composition on a triangle and plot it;
# 2. solve the menu with three rows (amounts, B atoms, C atoms) and explain why
#    three positive amounts are not three phases;
# 3. turn the three multipliers into the plane's corner heights $\mu_A$,
#    $\mu_B$, $\mu_C$ and check that no menu dot lies below it;
# 4. run column generation with closed-form pricing and check it against an
#    independent control, the Rachford–Rice equation;
# 5. (dive deeper) see why a non-ideal liquid makes the landscape harder, and
#    how the number of cells grows with the dimension.
#
# **What you need.** Steps 10–14 of the course, or notebooks f4c and
# f4d. Cards: the lever rule, reading a line, floor and ceiling, reduced cost,
# column generation, twin dots, the phase rule and a tie line.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Points on a triangle | main | 10 min |
# | 2 | The menu has three rows | main | 15 min |
# | 3 | The line becomes a plane | main | 10 min |
# | 4 | The gap becomes a landscape | main | 10 min |
# | 5 | Column generation and the Rachford–Rice control | main | 15 min |
# | 6 | What gets harder | dive deeper | 15 min |
# | 7 | Exercises | both | 20 min |
#
# **The model.** The melting lens of step 03 part C (A melts at 1000 K, B at
# 1800 K) plus an invented third component C that melts at 1250 K. C is
# synthetic: its numbers were chosen for teaching. Both SOLID and LIQUID stay
# ideal solutions of A, B and C. The sample has overall composition
# $z=(0.50, 0.30, 0.20)$ for (A, B, C) at 1400 K.
#
# **Coming from materials.** You know the ternary isothermal section with its
# tie lines. Here you read it as "which dots are used". A tie line joins the
# two coexisting compositions; the sample lies on it, and the lever rule is
# read along it. Tie lines cannot be drawn with a ruler from $z$: they point
# neither to a corner nor parallel to an edge.
#
# **Coming from operations research.** A three-row LP over candidate columns. A basic solution
# uses at most three columns (support size). Gibbs' phase rule at fixed $T$ and
# $p$ generically allows up to three coexisting phases too, but this model has
# only two phase models and no miscibility gap, so a third positive amount is a
# twin dot, not a third phase. Pricing an ideal phase has a closed form.
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
# Leave these as they are for the first run: the "Your turn" checks expect
# them. Later, change one number at a time and rerun everything below it.
#
# - `T`: the temperature in K;
# - `z`: the sample's overall composition (A, B, C), adding to 1;
# - `MENU_N`: the menu is every point $(i, j, k)/n$ of the triangle with
#   $n$ = `MENU_N`; with 12 the sample is not on the menu.

# %%
T = 1400.0                 # K
z = (0.50, 0.30, 0.20)     # overall (A, B, C) atom fractions
MENU_N = 12                # 91 menu points per phase model

# %% [markdown]
# `day3_ternary` is the small course module that also produced the numbers of
# step 18. It holds the two ideal phase models (`g`), the menu solver with
# three rows (`solve_master`), the closed-form pricing (`price`) and the
# Rachford–Rice control (`rachford_rice`). Colours follow the website.

# %%
import math
import numpy as np
import matplotlib.pyplot as plt
from course.self_study import day3_ternary as t3

SOLID_C, LIQUID_C, LINE_C = "#2445c4", "#cf4418", "#8f6400"   # the website's colours
R = t3.R                                                         # 8.3145 J/(mol K)

# %% [markdown]
# ## 1. Points on a triangle (main track, 10 min)
#
# A composition has three fractions that add to 1, so two numbers fix it. A
# triangle shows all of them at once: pure A at the corner $(0, 0)$, pure B at
# $(1, 0)$, pure C at $(1/2, \sqrt3/2)$. A composition $(x_A, x_B, x_C)$ sits at
#
# $$X = x_B + x_C/2,\qquad Y = x_C\,\sqrt3/2 .$$
#
# The further a point is from an edge, the more of the opposite corner's
# component it holds. The helper below does the conversion for a whole array.

# %%
def to_xy(x):
    """Triangle coordinates of (A, B, C) fractions (one row per point)."""
    x = np.atleast_2d(x)
    return x[:, 1] + x[:, 2] / 2, x[:, 2] * np.sqrt(3) / 2

def frame(ax):
    """Draw the triangle and label its corners."""
    ax.plot([0, 1, 0.5, 0], [0, 0, np.sqrt(3) / 2, 0], color="black", lw=0.8)
    for label, (px, py) in (("A", (-0.04, -0.04)), ("B", (1.01, -0.04)), ("C", (0.48, 0.89))):
        ax.text(px, py, label)
    ax.set_aspect("equal"); ax.axis("off")

# %% [markdown]
# ### Your turn: where is the sample?
#
# Give the horizontal coordinate $X$ of $z=(0.50, 0.30, 0.20)$.

# %%
X_z = None
check(X_z, "f4f_x_of_z")

# %% [markdown]
# ## 2. The menu has three rows (main track, 15 min)
#
# The menu is every grid point of the triangle, as a SOLID dot and as a
# LIQUID dot. The constraints now have three rows: amounts add to 1, B atoms
# add to $z_B$, C atoms add to $z_C$ (the A row follows from these).
#
# **Predict first:** how many dots will the cheapest mixture use?

# %%
menu = t3.grid(MENU_N)                                  # (A, B, C) for every grid point
phases = ["SOLID"] * len(menu) + ["LIQUID"] * len(menu)
states = np.vstack([menu, menu])
assert not any(np.allclose(p, z) for p in menu), "the sample is on the menu: choose another MENU_N"
master = t3.solve_master(phases, states, z, T)
print(f"{len(states)} dots; cheapest mixture G_up = {master.G_up:.2f} J/mol atoms")

# %%
for p, x, f in zip(master.phases, master.x, master.f):
    if f > 0:
        print(f"uses {p:6s} at (A, B, C) = ({x[0]:.3f}, {x[1]:.3f}, {x[2]:.3f}): f = {f:.3f}")
f, x = master.f, master.x
assert abs(f.sum() - 1) < 1e-9, f"amounts sum to {f.sum():.6f}, not 1"
assert np.allclose(f @ x, z, atol=1e-9), f"the atoms add to {f @ x}, not z = {z}"

# %% [markdown]
# Three dots carry an amount: two neighbouring LIQUID dots and one SOLID dot.
# That is a small *tie triangle*: the true liquid composition lies between the
# two liquid dots, and the solver mixes them to get close. Three positive
# amounts here are not three phases: two of them are twin dots of one phase.
#
# ### Your turn: count
#
# How many dots does the cheapest mixture use?

# %%
n_used = None
check(n_used, "f4f_menu_used")

# %% [markdown]
# ## 3. The line becomes a plane (main track, 10 min)
#
# With three rows the solver returns three multipliers $\pi_0, \pi_B, \pi_C$.
# They describe a plane over the triangle, $\pi_0 + \pi_B x_B + \pi_C x_C$.
# Its heights at the three corners are the chemical potentials:
#
# $$\mu_A = \pi_0,\qquad \mu_B = \pi_0+\pi_B,\qquad \mu_C = \pi_0+\pi_C .$$
#
# `master.mu` already holds the three corner heights. A dot's gap is its
# energy minus the plane's height there, $g(x)-\sum_i x_i\mu_i$.

# %%
mu = master.mu
print(f"mu_A = {mu[0]:.1f}   mu_B = {mu[1]:.1f}   mu_C = {mu[2]:.1f}   (J/mol)")
for p in ("SOLID", "LIQUID"):
    gaps = t3.g(p, menu, T) - menu @ mu
    print(f"{p:6s}: lowest gap of the menu dots {gaps.min():.2e}")
    assert gaps.min() > -1e-8, f"a {p} dot lies {gaps.min():.3g} J/mol below the plane"

# %% [markdown]
# The used dots sit on the plane (gap zero) and no dot lies below it: the plane
# is a floor for the menu, exactly as the line was on step 11.
#
# ### Your turn: one corner height
#
# What is $\mu_C$, the plane's height at the C corner?

# %%
mu_C = None   # J/mol
check(mu_C, "f4f_mu_c_menu")

# %% [markdown]
# ## 4. The gap becomes a landscape (main track, 10 min)
#
# Draw the gap of every composition of a phase model, not only the menu dots,
# as a colour map over the triangle. Blue is above the plane, red below it.
#
# **Predict first:** will the landscape dip below zero somewhere between the
# dots, as the gap curve did on step 12?

# %%
fine = t3.grid(60)
FX, FY = to_xy(fine)

def landscape(mu_plane, title):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, p in zip(axes, ("SOLID", "LIQUID")):
        gap = t3.g(p, fine, T) - fine @ mu_plane
        im = ax.tricontourf(FX, FY, np.clip(gap, -60, 60), levels=24, cmap="RdBu")
        frame(ax); ax.plot(*to_xy(np.array(z)), "k*", ms=10); ax.set_title(f"{p}: gap (J/mol atoms)")
    fig.colorbar(im, ax=axes, shrink=0.8); fig.suptitle(title); plt.show()
    return {p: (t3.g(p, fine, T) - fine @ mu_plane).min() for p in ("SOLID", "LIQUID")}

print(landscape(mu, "Against the menu's plane (values clipped to ±60)"))

# %% [markdown]
# Both landscapes dip below zero between the dots: the menu's plane is a floor
# for the menu, not for every state. Each phase model's deepest point has a
# formula, because both phase models are ideal:
#
# $$x_i \propto e^{-(g^\circ_i-\mu_i)/RT},\qquad \text{depth} = -RT\ln\sum_i e^{-(g^\circ_i-\mu_i)/RT}.$$
#
# `t3.price` applies it.

# %%
for p in ("SOLID", "LIQUID"):
    xd, depth = t3.price(p, mu, T)
    print(f"{p:6s}: deepest point ({xd[0]:.4f}, {xd[1]:.4f}, {xd[2]:.4f}), gap {depth:.2f} J/mol atoms")
    lowest = (t3.g(p, fine, T) - fine @ mu).min()
    assert depth <= lowest + 1e-9, "the formula should be at or below every grid point"

# %% [markdown]
# ## 5. Column generation and the Rachford–Rice control (main track, 15 min)
#
# Add the deepest state, solve again, repeat: column generation, as in step
# 13. The floor is the plane lowered by the deepest dip, read at $z$; as in
# step 14, the helper keeps the best floor so far. One round per row.

# %%
rounds = t3.column_generation(seed_n=MENU_N, z=z, t=T, tol=1e-4, max_iter=60)
print(" round   ceiling       deepest dip   remaining")
for r in rounds:
    print(f"{r['k']:5d}  {r['master'].G_up:11.3f}  {r['dips'][r['best']][1]:11.5f}  {r['remaining']:10.5f}")

# %%
ups = [r["master"].G_up for r in rounds]
assert all(b <= a + 1e-9 for a, b in zip(ups, ups[1:])), "the ceiling rose: the master lost a column"
fig, ax = plt.subplots(figsize=(6, 3))
ax.semilogy([r["k"] for r in rounds], [max(r["remaining"], 1e-12) for r in rounds], "o-", color=LINE_C)
ax.set(xlabel="round", ylabel="remaining uncertainty (J/mol atoms)", title="Column generation on the triangle"); plt.show()

# %% [markdown]
# **An independent control.** For two ideal phases the split follows from the
# partition ratios $K_i = x_{L,i}/x_{S,i} = e^{(g^\circ_{S,i}-g^\circ_{L,i})/RT}$.
# The liquid amount $V$ solves the Rachford–Rice equation
#
# $$\sum_i \frac{z_i (K_i-1)}{1+V(K_i-1)} = 0,\qquad 0<V<1,$$
#
# whose left side decreases with $V$ and has one root on $(0,1)$ when a split
# exists. It uses no grid and no LP at all.

# %%
K = t3.partition(T)
rr = t3.rachford_rice(z, T)
print("K =", K.round(4), "  V =", round(rr["V"], 4))
print("solid  ", rr["x_SOLID"].round(4), "\nliquid ", rr["x_LIQUID"].round(4))
confirm(rr["V"], 0.770823, "The liquid amount from Rachford–Rice", tol=1e-5)

# %% [markdown]
# Compare: the states column generation ended with sit at the Rachford–Rice
# compositions (twin columns of one phase have nearly the same composition).

# %%
last = rounds[-1]["master"]
for p, x, f in zip(last.phases, last.x, last.f):
    if f > 1e-9:
        target = rr["x_SOLID"] if p == "SOLID" else rr["x_LIQUID"]
        print(f"{p:6s} f = {f:.4f}  at {x.round(4)}  (Rachford–Rice {target.round(4)})")
        assert np.allclose(x, target, atol=2e-3), f"a {p} state is far from the Rachford–Rice composition"
liquid = sum(f for p, f in zip(last.phases, last.f) if p == "LIQUID")
print(f"total liquid amount {liquid:.4f}  against V = {rr['V']:.4f}")

# %% [markdown]
# The edges of the triangle are binaries. On the A–B edge the lens of step 03
# returns (liquid 0.312, solid 0.441 in B); on the C–B edge the band is
# narrower; the A–C edge is all liquid at 1400 K.

# %%
for pair in (("A", "B"), ("C", "B"), ("A", "C")):
    tie = t3.edge_tie(pair, T)
    print(f"{pair[0]}–{pair[1]} edge:", "all one phase" if tie is None else f"solid {tie[0]:.3f}, liquid {tie[1]:.3f} in {pair[1]}")

# %% [markdown]
# ### Your turn: the control
#
# 1. What fraction of the sample is liquid?
# 2. What is $x_B$ of the coexisting liquid?
# 3. On the C–B edge, what is the B fraction of the liquid?

# %%
V_answer = None
xB_liquid = None
cb_liquid = None
check(V_answer, "f4f_V")
check(xB_liquid, "f4f_xb_liquid")
check(cb_liquid, "f4f_cb_liquid")

# %% [markdown]
# ## 6. What gets harder (dive deeper, 15 min)
#
# Give the liquid an energy cost for A–C neighbours, $\Omega\,x_Ax_C$ with
# $\Omega = 30000$ J/mol. On the A–C edge that is more than $2RT$, so the liquid
# can split into an A-rich and a C-rich liquid: its landscape is no longer
# convex and the closed-form pricing no longer applies.
#
# Take the tangent plane of this liquid at the A-rich point (0.75, 0.05, 0.20)
# and look at the landscape against it.

# %%
at = np.array(t3.HARDER_AT)
mu_at = t3.mu_with_ac(at, T)
gap_at = float(t3.g_with_ac("LIQUID", at, T) - at @ mu_at)
print(f"tangent plane at {at}: corner heights {mu_at.round(1)}; gap there {gap_at:.2e}")
near = fine[np.linalg.norm(fine - at, axis=1) < 0.06]
print(f"lowest gap within 0.06 of the tangent point: {(t3.g_with_ac('LIQUID', near, T) - near @ mu_at).min():.3f}")

# %% [markdown]
# Near the tangent point nothing lies below the plane: a local search started
# there stops at once. A full scan of the triangle tells a different story.

# %%
scan = t3.grid(160)
gap_scan = t3.g_with_ac("LIQUID", scan, T) - scan @ mu_at
k = int(np.argmin(gap_scan))
print(f"full scan: deepest point {scan[k].round(3)}, gap {gap_scan[k]:.1f} J/mol atoms")
fig, ax = plt.subplots(figsize=(4.8, 4.2))
sx, sy = to_xy(scan)
im = ax.tricontourf(sx, sy, np.clip(gap_scan, -800, 800), levels=24, cmap="RdBu")
frame(ax); ax.plot(*to_xy(at), "k^", ms=8); ax.plot(*to_xy(scan[k]), "k*", ms=11)
fig.colorbar(im, ax=ax, shrink=0.8); ax.set_title("A–C liquid against its tangent plane"); plt.show()

# %% [markdown]
# The valley sits far away, on the C-rich side: the triangle version of step
# 15. On a triangle, a proof that no valley is left needs floors on small
# triangles instead of intervals, and the number of cells grows fast with the
# dimension $d$: cutting every direction into pieces of width $h$ gives about
# $(1/h)^d$ cells of a cube, about $(1/h)^d/d!$ on the composition simplex. That is the uniform worst case; branch-and-bound refines only
# near the touching points, but each split still makes several smaller cells.

# %%
for h in (0.1, 0.01):
    print(f"h = {h}: " + ",  ".join(f"d = {d}: {math.comb(round(1 / h) + d, d):.0e} grid points on the simplex" for d in (1, 2, 9)))

# %% [markdown]
# ### Your turn: the hidden valley
#
# How deep is the hidden valley found by the full scan (a negative number, J/mol atoms)?

# %%
hidden_depth = None
check(hidden_depth, "f4f_hidden_depth")

# %% [markdown]
# ## 7. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Set `z = (0.40, 0.40, 0.20)` in section 0 and rerun. Does the sample still
#   split? Read the new tie line: does it point to a corner?
# - Set `MENU_N = 24` and rerun. How many dots are used now, and how far is the
#   ceiling above the Rachford–Rice energy?
#
# **Optimisation flavour: complete a function, then one deeper exercise.**
#
# Complete `plane_heights`: given the three multipliers $(\pi_0, \pi_B, \pi_C)$,
# return the corner heights $(\mu_A, \mu_B, \mu_C)$.

# %%
def plane_heights(pi0, piB, piC):
    """Corner heights of the plane pi0 + piB xB + piC xC."""
    return None   # replace with (mu_A, mu_B, mu_C)

guess = plane_heights(master.mu[0], master.mu[1] - master.mu[0], master.mu[2] - master.mu[0])
check(None if guess is None else guess[2], "f4f_mu_c_menu")

# %% cellView="form"
#@title After your attempt: a solution of plane_heights
def plane_heights_solution(pi0, piB, piC):
    return pi0, pi0 + piB, pi0 + piC     # the plane's height at (1,0,0), (0,1,0) and (0,0,1)

print(plane_heights_solution(master.mu[0], master.mu[1] - master.mu[0], master.mu[2] - master.mu[0]))

# %% [markdown]
# **Deeper exercise (operations research).** Write your own Rachford–Rice solver: first the
# existence test (a split exists only if $\sum_i z_iK_i>1$ and
# $\sum_i z_i/K_i>1$), then bisection on $(0, 1)$, where the function is
# monotone. Compare $V$ and the compositions with `t3.rachford_rice`.

# %% cellView="form"
#@title After your attempt: a bracketed Rachford–Rice solver
def my_rachford_rice(z, K, tol=1e-14):
    z, K = np.asarray(z, float), np.asarray(K, float)
    if (z * K).sum() <= 1 or (z / K).sum() <= 1:
        return None                                   # one phase only: no root in (0, 1)
    f = lambda v: (z * (K - 1) / (1 + v * (K - 1))).sum()
    lo, hi = 0.0, 1.0                                 # f(0) > 0 > f(1) when a split exists
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    v = 0.5 * (lo + hi)
    xs = z / (1 + v * (K - 1))
    return v, xs, K * xs

v, xs, xl = my_rachford_rice(z, K)
print(round(v, 6), xs.round(4), xl.round(4))
assert abs(v - rr["V"]) < 1e-9 and np.allclose(xs, rr["x_SOLID"]) and np.allclose(xl, rr["x_LIQUID"])

# %% [markdown]
# ## Recap
#
# - A ternary composition is a point on a triangle; the menu is a grid of
#   points, as SOLID and as LIQUID dots.
# - The menu LP has three rows; its cheapest mixture uses at most three dots.
#   Here two of them are twin LIQUID dots: a tie triangle, not three phases.
# - The three multipliers give a plane whose corner heights are $\mu_A$,
#   $\mu_B$, $\mu_C$; it is a floor for the menu only.
# - Closed-form pricing and column generation reach the split that the
#   Rachford–Rice equation gives without any grid.
# - A non-ideal liquid hides valleys, and checks on a uniform grid grow like $(1/h)^d$
#   (branch-and-bound needs fewer pieces, but still many more in more dimensions).
#
# **Next:** back to the website; step 18 shows these pictures in the
# triangle lab. Cards: the phase rule and a tie line, twin dots, column
# generation, local and global minimum.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers.
