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
# # f4e · A valley the search can miss, and a check that none is left (advanced steps 15–17)
#
# **In plain words.** With one phase model whose curve has a hump, a search
# that only walks downhill from the sample's own composition can report "single
# phase" while a much deeper valley sits far away. In this notebook you watch
# that happen, keep looking until the true split appears, and then check, piece
# by piece of the composition range, that no deeper valley is left.
#
# **Learning goals.** After this notebook you can
#
# 1. show that a local search on the gap curve from $z=0.15$ misses the valley
#    near $x=0.958$, and that a full scan finds it;
# 2. keep pricing until the used states reach the coexisting compositions 0.070
#    and 0.930, and say why one added state was not enough;
# 3. compute a chord floor on one interval and say why it is a guaranteed floor;
# 4. run a small branch-and-bound that closes every interval of $[0,1]$, and read
#    its floor, its remaining uncertainty and an unresolved run;
# 5. (dive deeper) check the answer with a short verifier of your own.
#
# **What you need.** Steps 15–17 of the course, or their cards: which model
# am I in?, local and global minimum, metastable or unstable, relaxation and
# underestimator, intervals and halving, prune and incumbent, tolerance,
# checkable answer. Notebook f4d (column generation) helps but is not required.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Local search misses a valley | main | 15 min |
# | 2 | Keep pricing | main | 15 min |
# | 3 | A floor for one interval | main | 15 min |
# | 4 | Branch-and-bound: check that no valley is left | main | 20 min |
# | 5 | How short is short enough, and stopping early | dive deeper | 10 min |
# | 6 | A checkable answer and your own verifier | dive deeper | 15 min |
# | 7 | Exercises | both | 25 min |
#
# **Coming from materials.** The sample at $z=0.15$ is a supersaturated solid
# solution: metastable. A real alloy may stay like that for a long time. An
# equilibrium calculation must still find the lower split, and this notebook
# shows how a computer can miss it and how it can make sure it did not.
#
# **Coming from operations research.** The pricing problem of column generation is now
# nonconvex. A local pricer can stop the method too early; a spatial
# branch-and-bound with a secant underestimator turns "no negative reduced cost
# found" into "none below $-\varepsilon$ exists", in floating point.
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
# Leave these numbers as they are for the first run: the "Your turn" checks
# expect them. Later, change one at a time and rerun everything below it.
#
# - `T`: the temperature in K (the regular solution of step 03 part B at 800 K);
# - `z`: the overall B atom fraction of the sample;
# - `EPS`: the tolerance $\varepsilon$ of branch-and-bound, in J/mol atoms;
# - `STARTS`: where the local searches of section 1 begin.

# %%
T = 800.0                                 # K
z = 0.15                                  # overall B atom fraction of the sample
EPS = 1.0                                 # J/mol atoms: dips shallower than this are not chased
STARTS = [0.05, 0.15, 0.3, 0.5, 0.7, 0.9]  # starts of the local searches

# %% [markdown]
# Two course modules: `day3_core`, the small library that produced every number
# on the advanced steps of the website, and `binary_family`, which holds the regular solution
# itself and its exact coexisting compositions. `alpha.g(x)` is the molar Gibbs
# energy of the one phase model, ALPHA, in J per mole of atoms; `alpha.slope(x)`
# is its slope and `alpha.curvature(x)` how strongly it bends.

# %%
import numpy as np
import matplotlib.pyplot as plt
from course.self_study import day3_core as d
from course.foundations import binary_family as bf

ALPHA_C, LINE_C, DIP_C = "#2445c4", "#8f6400", "#cf4418"   # the website's colours
models = d.regular_models(T)       # {'ALPHA': model}: step 02's ALPHA plus Omega x(1 - x)
alpha = models["ALPHA"]

# %% [markdown]
# ## 1. Local search misses a valley (main track, 15 min)
#
# Start where a careful program would: with the single uniform state at
# $z=0.15$ and the tangent there. The tangent's slope is the curve's slope at
# 0.15; it touches the curve at $g(0.15)$.

# %%
d_mu_t = float(alpha.slope(z))            # slope of the tangent at z
g_z = float(alpha.g(z))                   # the uniform state's energy
mu_A_t = g_z - d_mu_t * z                 # the tangent's height at x = 0
confirm(d_mu_t, 14462.127620, "Tangent slope at 0.15", tol=1e-4)
print(f"g(0.15) = {g_z:.1f}   mu_A = {mu_A_t:.1f}   d_mu = {d_mu_t:.1f}   (J/mol)")

# %% [markdown]
# Is the uniform state at 0.15 stable against small changes? The curvature
# says how the curve bends: positive means it bends up.

# %%
print(f"curvature at 0.15: {float(alpha.curvature(z)):.0f} J/mol atoms")
print("binodal and spinodal:", bf.regular_binodal(T))

# %% [markdown]
# The gap curve is $g(x)$ minus the tangent. At 0.15 it is zero and it rises on
# both sides. Now let the computer search for states below the line by walking
# downhill on the gap curve, from several starts. `d.local_descent` returns the
# compositions it visits; it is the computer's search, not what atoms do.
#
# **Predict first:** where does the search from 0.15 end? And from 0.5?

# %%
for start in STARTS:
    path = d.local_descent(alpha, mu_A_t, d_mu_t, start)
    end = path[-1]
    print(f"start {start:.2f}: ends at {end:.4f}, gap {float(alpha.g(end)) - mu_A_t - d_mu_t * end:9.1f}")

# %% [markdown]
# Starts at or near 0.15 never leave it: the gap curve is flat there and rises
# on both sides, so "no state below the line" looks true. Starts further right
# roll into a deep valley. The picture shows why.

# %%
xs = np.linspace(0.0, 1.0, 1001)
gap_t = alpha.g(xs) - (mu_A_t + d_mu_t * xs)
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(xs, gap_t, color=ALPHA_C, label="gap against the tangent at 0.15")
ax.axhline(0, color="black", lw=0.8); ax.axvline(z, color="grey", ls=":")
ax.set(xlabel="B atom fraction x", ylabel="gap (J/mol atoms)", title="The valley a local search from 0.15 cannot see")
ax.legend(); plt.show()

# %% [markdown]
# A full scan looks everywhere: `d.price_scan` evaluates the gap on 20001 points
# of $[0,1]$ and refines the best one.

# %%
dip = d.price_scan(alpha, mu_A_t, d_mu_t)
print(f"full scan: deepest dip {dip.depth:.1f} J/mol atoms at x = {dip.x:.4f}")
assert dip.depth < -EPS, "expected a valley below the tangent"

# %% [markdown]
# ### Your turn: the valley by hand
#
# At $x=0.958$ the curve has $g = 4141.7$ J/mol atoms (printed below). Use the
# tangent from the first cell of this section to find the gap there.
# Second: is the uniform sample at 0.15 *stable*, *metastable* or *unstable*?

# %%
print(f"g(0.958) = {float(alpha.g(0.958)):.1f} J/mol atoms")
gap_0958 = None     # J/mol atoms, negative
state_015 = None    # one word
check(gap_0958, "f4e_gap_0958")
check(state_015, "f4e_state_015")

# %% [markdown]
# ## 2. Keep pricing (main track, 15 min)
#
# Add the state at the dip and solve the menu again, as in column generation.
# Here is the surprise: after adding the state near 0.958, the menu has no state
# left of 0.15, so the only mixture that makes $z=0.15$ is the 0.15 state itself.
# Many lines pass through that one dot and stay under the 0.958 dot: every one
# of them is optimal, and the solver returns one of them (here a flat one). Keep
# pricing anyway.
#
# `d.column_generation` runs the loop; its `line` argument lets round 0 use the
# tangent we chose by hand (a one-state menu leaves the slope free).

# %%
seed = [d.State("ALPHA", z, g_z)]
rounds = d.column_generation(models, seed, z, tol=1e-9, max_iter=12,
                             line=lambda master, k: (mu_A_t, d_mu_t) if k == 0 else (master.mu_A, master.d_mu))
for it in rounds:
    used = ", ".join(f"{s.x:.4f} ({f:.3f})" for s, f in it.master.used())
    label = "chosen by hand" if it.k == 0 else "returned by the solver"
    print(f"round {it.k}: d_mu {it.master.d_mu:9.1f} ({label:22s}) uses {used:30s} deepest dip {it.best.depth:10.4f} at {it.best.x:.4f}")

# %% [markdown]
# Round 1 shows the flat line: its gap curve dips about 1594 below near
# $x\approx0.009$. A line through both the 0.15 and the 0.958 dots would still
# dip below near 0.068. Neither is wrong; the menu is just too small to fix the
# line. After four more rounds the used states settle where the regular
# solution's two phases really are.

# %%
two = rounds[1].master.states[1]                  # the state added after round 0 (near 0.958)
slope_two = (two.g - g_z) / (two.x - z)          # the line through both dots
print(f"two-dot line: slope {slope_two:.1f}; its deepest dip:", d.price_scan(alpha, g_z - slope_two * z, slope_two))
final = rounds[-1].master
xs_used = sorted(s.x for s, _ in final.used())
exact = bf.regular_binodal(T)["compositions"]
print(f"used states {xs_used[0]:.4f} and {xs_used[1]:.4f}; exact coexistence {exact[0]:.4f} and {exact[1]:.4f}")
assert all(abs(a - b) < 1e-5 for a, b in zip(xs_used, exact)), "column generation did not reach the binodal"

# %% [markdown]
# ### Your turn: the B-rich phase
#
# What is the composition of the B-rich phase at equilibrium? Is it the same as
# the composition of the first dip, 0.958?

# %%
x_rich = None   # B atom fraction
check(x_rich, "f4e_x_rich")

# %% [markdown]
# ## 3. A floor for one interval (main track, 15 min)
#
# Column generation stopped because its last scan found nothing deeper than
# about 0.0001. A scan is a list of points: it cannot prove that no valley hides
# between them. A *floor* for a whole interval can.
#
# The regular solution's curve is a straight line, plus the ideal mixing term
# (which bends up), plus the hump $\Omega x(1-x)$ (which bends down). On an
# interval $[l,u]$, replace the hump by its chord, the straight line through its
# values at $l$ and $u$. An arch lies above its chord, so the new curve lies on
# or below the gap curve on the whole interval. And the new curve bends up
# everywhere, so its lowest point has a formula:
#
# $$s=b-\Delta\mu+\Omega(1-l-u),\qquad x^*=\frac{1}{1+e^{\,s/RT}}\ \text{(clipped to }[l,u]),$$
#
# where $b=12000$ J/mol is the rise of the straight end line. The floor is the
# new curve's value at $x^*$.

# %%
mu_A, d_mu = final.mu_A, final.d_mu               # the converged line
lo, hi = 0.0625, 0.078125                         # one interval near the touching point 0.070
RT = d.R * T
s = alpha.b - d_mu + alpha.w * (1 - lo - hi)
x_star = min(max(1 / (1 + np.exp(s / RT)), lo), hi)
print(f"s = {s:.1f} J/mol,  x* = {x_star:.5f}")

# %% [markdown]
# The new curve at $x^*$: the straight part, the mixing part, the chord of the
# hump, minus the line. The cell then compares your by-hand floor with the
# library's `d.chord_floor`.

# %%
chord = alpha.w * (lo * (1 - lo) + (1 - lo - hi) * (x_star - lo))   # the hump's chord at x*
mixing = RT * (x_star * np.log(x_star) + (1 - x_star) * np.log(1 - x_star))
floor_hand = alpha.a + alpha.b * x_star + mixing + chord - (mu_A + d_mu * x_star)
floor_lib, _ = d.chord_floor(alpha, mu_A, d_mu, lo, hi)
print(f"floor by hand {floor_hand:.4f}, library {floor_lib:.4f} J/mol atoms")
assert abs(floor_hand - floor_lib) < 1e-9, "the by-hand floor differs from the library"

# %% [markdown]
# How loose can the chord be? The hump lies above its chord by at most
# $\Omega(u-l)^2/4$, at the midpoint. Halving an interval quarters that: the
# reason branch-and-bound works. The picture shows the gap curve and the floor
# curve on this interval.

# %%
xi = np.linspace(lo, hi, 201)
gap_i = alpha.g(xi) - (mu_A + d_mu * xi)
under = gap_i - alpha.w * xi * (1 - xi) + alpha.w * (lo * (1 - lo) + (1 - lo - hi) * (xi - lo))
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(xi, gap_i, color=ALPHA_C, label="gap curve"); ax.plot(xi, under, color=LINE_C, ls="--", label="hump replaced by its chord")
ax.axhline(-EPS, color=DIP_C, lw=0.8, label="−ε"); ax.axhline(0, color="black", lw=0.8)
ax.set(xlabel="B atom fraction x", ylabel="J/mol atoms", title=f"One interval [{lo}, {hi}]"); ax.legend(); plt.show()

# %% [markdown]
# ### Your turn: one interval
#
# 1. Give the floor of $[0.0625, 0.078125]$ to three decimals.
# 2. Give the largest looseness $\Omega(u-l)^2/4$ on this interval.
# 3. With $\varepsilon=1$: prune or split?

# %%
floor_interval = None   # J/mol atoms
looseness = None        # J/mol atoms
decision = None         # "prune" or "split"
check(floor_interval, "f4e_floor_interval")
check(looseness, "f4e_looseness")
check(decision, "f4e_decision")

# %% [markdown]
# ## 4. Branch-and-bound: check that no valley is left (main track, 20 min)
#
# Start with $[0,1]$. For each interval compute its floor. If the floor is at
# least $-\varepsilon$, nothing in it lies more than $\varepsilon$ below the line:
# prune it. Otherwise cut it in half and look at both halves. When every
# interval is pruned, the line lowered by the lowest floor $m$ is a floor for
# every state:
#
# $$G_{\text{low}}=\mu_A+\Delta\mu\,z+\min(0,m).$$
#
# **Predict first:** where will the intervals have to be short?

# %%
proof = d.branch_and_bound(alpha, mu_A, d_mu, eps=EPS)
print(" node  interval                floor      gap at x*   action")
for n in proof.nodes:
    print(f"{n.n:5d}  [{n.lo:.5f}, {n.hi:.5f}]  {n.floor:10.3f}  {n.gap_at_x:10.3f}   {n.action}")

# %% [markdown]
# The short intervals collect near 0.070 and 0.930, where the line touches the
# curve: there the gap is close to zero and any looseness of the chord pushes
# the floor below $-\varepsilon$. Near the middle the curve lies hundreds of
# J/mol above the line, and long intervals are pruned at once.

# %%
G_up = final.G_up                                   # the best mixture: the ceiling
G_low = mu_A + d_mu * z + min(0.0, proof.m)         # the line lowered by the lowest leaf floor
print(f"{len(proof.nodes)} intervals, {len(proof.leaves)} leaves, status {proof.status}")
print(f"lowest floor m = {proof.m:.3f};  ceiling {G_up:.2f},  floor {G_low:.2f},  remaining {G_up - G_low:.2f} J/mol atoms")
assert proof.status == "proved" and G_up - G_low <= EPS, "branch-and-bound did not close [0, 1] within the tolerance"

# %% [markdown]
# ### Your turn: read the check
#
# 1. What is the floor $G_{\text{low}}$ for the sample?
# 2. What is the remaining uncertainty, ceiling minus floor?

# %%
g_low_answer = None     # J/mol atoms
remaining = None        # J/mol atoms
check(g_low_answer, "f4e_g_low")
check(remaining, "f4e_remaining")

# %% [markdown]
# ## 5. How short is short enough, and stopping early (dive deeper, 10 min)
#
# The chord is loose by at most $\Omega(u-l)^2/4$, so near a touching point an
# interval of width about $2\sqrt{\varepsilon/\Omega}\approx0.014$ has a floor
# near $-\varepsilon$. That width is a scale, not a guarantee. Centre an
# interval of exactly that width on the touching point 0.070: against the exact
# common tangent its floor is $-1.000$; against a line only 0.005 J/mol too high
# it is $-1.005$, so it is split again.

# %%
left = bf.regular_binodal(T)["compositions"][0]
d_mu_x = float(alpha.slope(left)); mu_A_x = float(alpha.g(left)) - d_mu_x * left   # the exact common tangent
h = 2 * np.sqrt(EPS / alpha.w)
for raise_by in (0.0, 0.005):
    fl, _ = d.chord_floor(alpha, mu_A_x + raise_by, d_mu_x, left - h / 2, left + h / 2)
    print(f"width {h:.5f}, line raised by {raise_by}: floor {fl:.4f}")

# %% [markdown]
# If the line's own gap dips to $-\delta$ (here up to 0.005), pruning is
# guaranteed only once $\Omega(u-l)^2/4<\varepsilon-\delta$. The computed floor
# always decides.
#
# Stopping early is allowed, but the answer is then honest about it: after
# nine intervals, the pieces still waiting have never been examined (no floor
# at all), and the result is "unresolved", never "stable".

# %%
early = d.branch_and_bound(alpha, mu_A, d_mu, eps=EPS, max_nodes=9)
print("status:", early.status)
for n in early.leaves:
    floor_text = "not examined" if n.floor is None else f"floor {n.floor:9.2f}"
    print(f"  [{n.lo:.4f}, {n.hi:.4f}]  {floor_text:>15s}  {n.action}")

# %% [markdown]
# ## 6. A checkable answer and your own verifier (dive deeper, 15 min)
#
# The result can be checked without trusting the solver. The answer lists the
# mixture (the ceiling), the final line, every interval and the tolerance.

# %%
answer = {"states": [(s.x, f) for s, f in final.used()], "mu_A": mu_A, "d_mu": d_mu,
          "intervals": [(n.lo, n.hi) for n in proof.leaves], "eps": EPS, "z": z,
          "G_up": G_up, "G_low": G_low}
print(f"{len(answer['intervals'])} intervals; mixture", [(round(x, 4), round(f, 3)) for x, f in answer["states"]])

# %% [markdown]
# Here is a separate verifier, about twenty lines. It uses only the formula of
# section 3, not the library's branch-and-bound. It recomputes the mixture's
# energy, checks the atom balances, checks that the intervals cover $[0,1]$
# without holes, recomputes every interval's floor, and compares ceiling minus
# floor with the tolerance. This is a floating-point teaching check, not a
# rigorous proof: rounding is not controlled.

# %%
def verify_answer(ans, model, slack=1e-9):
    """Return a list of problems; an empty list means the answer passes."""
    problems, x = [], np.array([s[0] for s in ans["states"]])
    f = np.array([s[1] for s in ans["states"]])
    if f.min() < 0 or abs(f.sum() - 1) > slack or abs(f @ x - ans["z"]) > slack:
        problems.append("the mixture does not keep the atoms")
    if abs(sum(fi * float(model.g(xi)) for xi, fi in zip(x, f)) - ans["G_up"]) > 1e-6:
        problems.append("the ceiling is not the mixture's energy")
    iv = sorted(ans["intervals"])
    if iv[0][0] != 0.0 or iv[-1][1] != 1.0 or any(a[1] != b[0] for a, b in zip(iv, iv[1:])):
        problems.append("the intervals leave a hole in [0, 1]")
    RT_, floors = d.R * model.T, []
    for l, u in iv:
        s_ = model.b - ans["d_mu"] + model.w * (1 - l - u)
        xs_ = min(max(1 / (1 + np.exp(s_ / RT_)), l), u)
        mix = RT_ * float(d.q(xs_))
        floors.append(model.a + model.b * xs_ + mix + model.w * (l * (1 - l) + (1 - l - u) * (xs_ - l)) - ans["mu_A"] - ans["d_mu"] * xs_)
    if min(floors) < -ans["eps"]:
        problems.append("an interval's floor is below −ε")
    g_low = ans["mu_A"] + ans["d_mu"] * ans["z"] + min(0.0, min(floors))
    if abs(g_low - ans["G_low"]) > 1e-6 or ans["G_up"] - g_low > ans["eps"] + slack:
        problems.append("the floor or the remaining uncertainty does not hold")
    return problems

# %% [markdown]
# The verifier accepts the answer, and rejects it when an interval is removed or
# the line is raised by 2 J/mol.

# %%
print("as computed:", verify_answer(answer, alpha) or "passes")
print("one interval removed:", verify_answer({**answer, "intervals": answer["intervals"][1:]}, alpha))
print("line raised by 2 J/mol:", verify_answer({**answer, "mu_A": mu_A + 2.0}, alpha))
assert not verify_answer(answer, alpha), "the verifier rejects the computed answer"
assert verify_answer({**answer, "mu_A": mu_A + 2.0}, alpha), "the verifier accepts a raised line"

# %% [markdown]
# The library has its own verifier, `d.verify`, written the same way; both agree.

# %%
lib_answer = d.Answer([("ALPHA", x, f) for x, f in answer["states"]], mu_A, d_mu, answer["intervals"],
                      EPS, z, EPS, G_up, G_low)
print("library verifier:", d.verify(lib_answer, alpha))

# %% [markdown]
# ## 7. Exercises
#
# **Materials flavour: run, change one number, explain.**
#
# - Raise the temperature above $T_c=\Omega/2R\approx1203$ K, for example to
#   1250 K. The hump is gone; how many intervals does branch-and-bound need
#   against the tangent at $z$? The cell below runs it. Explain the difference.
# - Confine the local searches of section 1 to a window around $z$, as a program
#   that "starts near the answer" would, for example starts between 0.10 and
#   0.20. Widen the window until a search finds the valley. Which start is the
#   first one that does?

# %%
hot = d.regular_models(1250.0)["ALPHA"]
slope_hot = float(hot.slope(z)); mu_hot = float(hot.g(z)) - slope_hot * z
tree = d.branch_and_bound(hot, mu_hot, slope_hot, eps=EPS)
print(f"1250 K: {tree.status} with {len(tree.nodes)} intervals (800 K needed {len(proof.nodes)} against the converged line)")

# %%
for window in (0.05, 0.10, 0.15, 0.20):
    starts = np.clip(np.linspace(z - window, z + window, 5), 0.01, 0.99)   # stay inside (0, 1)
    ends = [d.local_descent(alpha, mu_A_t, d_mu_t, float(start))[-1] for start in starts]
    finders = [round(float(st), 3) for st, end in zip(starts, ends) if end > 0.9]   # starts that reach the valley near 0.958
    print(f"starts within ±{window:.2f} of z: furthest end {max(ends):.3f};  starts that find the valley: {finders or 'none'}")

# %% [markdown]
# **Optimisation flavour: complete a function, then one deeper exercise.**
#
# Complete `covers`: given a list of `(l, u)` intervals, return `True` if, once
# sorted, they start at 0, end at 1 and leave no hole. Test it on the leaves of
# section 4.

# %%
def covers(intervals):
    """True when the sorted intervals cover [0, 1] without a hole."""
    return None   # replace with True or False

check(covers([(n.lo, n.hi) for n in proof.leaves]), "f4e_covers")

# %% cellView="form"
#@title After your attempt: a solution of covers
def covers_solution(intervals):
    iv = sorted(intervals)
    return iv[0][0] == 0.0 and iv[-1][1] == 1.0 and all(a[1] == b[0] for a, b in zip(iv, iv[1:]))

print(covers_solution([(n.lo, n.hi) for n in proof.leaves]), covers_solution([(0.0, 0.5), (0.6, 1.0)]))

# %% [markdown]
# **Deeper exercise (operations research).**
#
# 1. Count the intervals of the proof for $\varepsilon$ = 10, 1, 0.1 and 0.01.
#    How does the count grow, and why mostly near the touching points?
# 2. Write your own loop that takes intervals from a stack (depth-first)
#    instead of a queue (first in, first out). Does the number of intervals
#    change? Does the answer?
# 3. Replace the full scan in column generation by `d.bb_deepest`, a
#    branch-and-bound that searches for the deepest dip, and run column
#    generation from the 0.15 state. Do the used states reach the compositions
#    of `bf.regular_binodal`?

# %% cellView="form"
#@title After your attempt: tolerance, depth-first, and branch-and-bound pricing
from collections import deque
for eps in (10.0, 1.0, 0.1, 0.01):
    print(f"eps {eps:5}: {len(d.branch_and_bound(alpha, mu_A, d_mu, eps=eps, max_nodes=5000).nodes)} intervals")

def count(eps, depth_first):
    todo, seen = deque([(0.0, 1.0)]), 0
    while todo:
        l, u = todo.pop() if depth_first else todo.popleft()
        seen += 1
        if d.chord_floor(alpha, mu_A, d_mu, l, u)[0] < -eps:
            todo.extend([(l, (l + u) / 2), ((l + u) / 2, u)])
    return seen
print("queue:", count(EPS, False), " stack:", count(EPS, True), "intervals (same tree, different order)")

states = list(seed)
for k in range(15):
    master = d.solve_master(states, z)
    line_k = (mu_A_t, d_mu_t) if k == 0 else (master.mu_A, master.d_mu)
    found = d.bb_deepest(alpha, *line_k, tol=0.01, max_nodes=3000).found
    if found.gap_at_x > -1e-4:
        break
    states.append(d.State("ALPHA", found.x_floor, float(alpha.g(found.x_floor))))
print("used states", sorted(round(s.x, 4) for s, _ in master.used()), " binodal", [round(v, 4) for v in exact])

# %% [markdown]
# ## Recap
#
# - Against the tangent at 0.15 the gap curve is flat and rises on both sides:
#   a local search there reports "single phase", while a valley 2082 J/mol atoms
#   deep sits near 0.958. The sample is metastable; the calculation must still
#   find the split.
# - One added state was not enough: the menu could not fix the line. Pricing on,
#   the used states reach the coexisting compositions 0.070 and 0.930.
# - A chord replaces the hump on an interval and gives a guaranteed floor;
#   branch-and-bound prunes intervals whose floor is at least $-\varepsilon$ and
#   splits the rest. When all of $[0,1]$ is pruned, the floor and the ceiling
#   lie within $\varepsilon$: a check for the declared model, in floating point (a teaching check, not a rigorous proof).
# - Stopped early, the honest answer is "unresolved".
#
# **On the website:** steps 15 (local search can miss a valley), 16 (check that
# no valley is left) and 17 (two questions and the joint case). Cards: local and global
# minimum, metastable or unstable, relaxation and underestimator, prune and
# incumbent, checkable answer.
#
# **If a cell fails:** rerun the setup cell first; then check that section 0
# still has its original numbers.
