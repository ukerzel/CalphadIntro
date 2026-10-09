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
# # f4p · Linear programmes from scratch (optional LP primer)
#
# **In plain words.** A linear programme (LP) chooses some amounts, keeps a few
# rules and makes a total as small as possible. In this notebook you solve one
# by hand, then let SciPy solve it, read every number it returns, and check
# those numbers yourself. At the end you rename two columns and the same code
# solves the menu of advanced step 10.
#
# **Learning goals.** After this notebook you can
#
# 1. name the variables, the objective and the rules of a small LP, and write
#    it for `scipy.optimize.linprog`;
# 2. read `linprog`'s answer: status, amounts, best total and prices, with
#    their signs;
# 3. check an answer yourself: the rules hold, no amount is negative, and a
#    straight line under all candidates proves that nothing is cheaper;
# 4. check a price by solving again with a nudged rule, and see where the
#    check stops working;
# 5. (dive deeper) solve the companion problem about prices, and meet an
#    unbounded problem and prices that are not unique.
#
# **What you need.** The LP primer page of the course, or at least its
# problem. The lever rule. No derivatives and no matrix algebra beyond
# "multiply and add".
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Every pair, by hand | main | 10 min |
# | 2 | The same problem in `linprog` | main | 15 min |
# | 3 | The search, one swap at a time | main | 10 min |
# | 4 | Prices, and a line under every lot | main | 15 min |
# | 5 | The textbook picture | main | 15 min |
# | 6 | Same problem, new names: step 10's menu | main | 5 min |
# | 7 | The companion problem about prices | dive deeper | 10 min |
# | 8 | Unbounded, and prices that are not unique | dive deeper | 10 min |
# | 9 | Exercises | both | 20 min |
#
# **Coming from materials.** You have done the hand part before: the lever
# rule of step 03 and the chord rule. The new parts are the solver's view and
# the idea that a line under all candidates is a proof.
#
# **Coming from operations research.** You can skip this notebook. Its
# conventions: amounts are `f` (in this course `x` is a composition), masters
# (the course's LPs over a list of phase states) are minimisations with equality rows, and SciPy's marginals are the change of
# the optimum per unit increase of a right-hand side.
#
# **The numbers are invented** for the exercise (prices, contents, caps); they
# are not market data.
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
# A melt shop must make 1 kg of a copper–nickel alloy with exactly 0.40 kg of
# nickel, as cheaply as possible. Each lot of scrap has a nickel content `w`
# (kg Ni per kg of lot) and a price (€ per kg). Leave the numbers as they are
# for the first run: the "Your turn" checks expect them. Later, change one
# number at a time and rerun everything below it.

# %%
NAMES  = ["Cu", "CuNi10", "CuNi30", "CuNi45", "Monel", "Ni"]   # short names of the six lots
W      = [0.00, 0.10, 0.30, 0.45, 0.65, 1.00]                   # Ni content, kg Ni per kg of lot
PRICE  = [7.40, 7.90, 8.40, 10.00, 10.20, 15.50]                 # € per kg of lot
TARGET = 0.40                                                    # kg Ni per kg of charge

# %% [markdown]
# Three libraries. `numpy` for lists of numbers, `matplotlib` for pictures and
# `linprog` from SciPy, the LP solver. Colours follow the website.

# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

LOT_C, LINE_C, MIN_C, BAD_C = "#2445c4", "#8f6400", "#b58900", "#cf4418"   # the website's colours
W, PRICE = np.array(W), np.array(PRICE)
for name, w, price in zip(NAMES, W, PRICE):
    print(f"{name:7s} w = {w:.2f} kg Ni per kg   price = {price:5.2f} € per kg")

# %% [markdown]
# ## 1. Every pair, by hand (main track, 10 min)
#
# Two lots, one below the target and one above, make 1 kg at the target. The
# lever rule fixes the amounts:
#
# $$f_{\text{rich}}=\frac{\text{target}-w_{\text{poor}}}{w_{\text{rich}}-w_{\text{poor}}},\qquad f_{\text{poor}}=1-f_{\text{rich}},$$
#
# and the charge costs $f_{\text{poor}}\,c_{\text{poor}}+f_{\text{rich}}\,c_{\text{rich}}$.
# Two lots on the same side of the target would need a negative amount, which
# cannot be bought.
#
# ### Your turn: one charge
#
# What does 1 kg at 0.40 cost when it is made of copper scrap (Cu) and Monel
# offcuts? Use the lever rule and the printed prices.

# %%
cost_cu_monel = None   # € per kg
check(cost_cu_monel, "f4p_cu_monel")

# %% [markdown]
# **Predict first.** Which pair do you expect to be cheapest? The next cell
# tries every pair with a plain double loop.

# %%
best = None
for i in range(len(W)):
    if W[i] == TARGET:                                 # a single lot already at the target
        print(f"{NAMES[i]:7s} alone      amount 1.000 kg           cost {PRICE[i]:6.3f} €")
        if best is None or PRICE[i] < best[0]:
            best = (PRICE[i], i, i, 1.0)
    for j in range(len(W)):
        if W[i] < TARGET < W[j]:                       # one lot below the target, one above
            f_rich = (TARGET - W[i]) / (W[j] - W[i])   # lever rule
            cost = (1 - f_rich) * PRICE[i] + f_rich * PRICE[j]
            print(f"{NAMES[i]:7s} + {NAMES[j]:7s}  amounts {1 - f_rich:.3f} + {f_rich:.3f} kg   cost {cost:6.3f} €")
            if best is None or cost < best[0]:
                best = (cost, i, j, f_rich)
print(f"\ncheapest: {' + '.join(dict.fromkeys([NAMES[best[1]], NAMES[best[2]]]))}, {best[0]:.3f} € per kg")

# %% [markdown]
# A picture of the same thing: lots as dots, price against content. A two-lot
# charge at the target costs the height of the chord between the two dots at
# the target, so the cheapest charge is the chord whose height at 0.40 is lowest.

# %%
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.scatter(W, PRICE, color=LOT_C, zorder=3)
for name, w, price in zip(NAMES, W, PRICE):
    ax.annotate(name, (w, price), textcoords="offset points", xytext=(5, 6), fontsize=9)
i, j = best[1], best[2]
ax.plot([W[i], W[j]], [PRICE[i], PRICE[j]], color=MIN_C, lw=2, label="cheapest chord")
ax.axvline(TARGET, color="0.4", ls="--", lw=1)
ax.plot(TARGET, best[0], "o", color=MIN_C, ms=8, zorder=4)
ax.set_xlabel("Ni content w (kg Ni per kg)"); ax.set_ylabel("price (€ per kg)"); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# ## 2. The same problem in `linprog` (main track, 15 min)
#
# The three parts of the problem, in plain words and then in symbols:
#
# - **choose** the amounts $f_j\ge0$ of every lot $j$, in kg (the variables);
# - **to make** the total cost $\sum_j f_j\,c_j$ as small as possible (the objective);
# - **while keeping** the rules $\sum_j f_j=1$ (1 kg) and $\sum_j f_j\,w_j=0.40$
#   (0.40 kg nickel); these are the constraints.
#
# In one line: minimise $\sum_j f_jc_j$ **subject to** $\sum_j f_j=1$,
# $\sum_j f_jw_j=0.40$, $f_j\ge0$. "Subject to" means "while keeping these
# rules".
#
# `linprog` takes the problem as arrays. `c` holds one cost per lot. Each row
# of `A_eq` is one rule, each column one lot: the rule says "this row times the
# amounts equals the matching entry of `b_eq`". `bounds=(0, None)` says that no
# amount is negative. `method="highs-ds"` asks for the dual simplex method
# (the mirror image of the swap search in section 3: it keeps a line under every
# lot and swaps until the used pair can make the target), which returns a corner answer: at most as many non-zero amounts as rules.

# %%
c = PRICE                                   # objective: cost of 1 kg of each lot
A_eq = np.array([np.ones(len(W)),           # rule 1: the amounts add up ...
                 W])                        # rule 2: the nickel adds up ...
b_eq = np.array([1.0, TARGET])              # ... to 1 kg and to 0.40 kg
print("        " + "".join(f"{n:>8s}" for n in NAMES) + "      b_eq")
for name, row, rhs in zip(["1 kg", "Ni"], A_eq, b_eq):
    print(f"{name:6s}  " + "".join(f"{v:8.2f}" for v in row) + f"   = {rhs:.2f}")
print("cost    " + "".join(f"{v:8.2f}" for v in c))

# %%
res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs-ds")
print("status: ", res.status, "-", res.message)   # 0 means: a best answer was found

# %% [markdown]
# Read `res.status` first: 0 optimal, 2 infeasible (no choice keeps every
# rule), 3 unbounded (the total can fall without limit). Other codes mean the
# solver stopped early or ran into numerical trouble; read `res.message`. Only
# for status 0 are the other numbers an answer.
#
# - `res.x` holds the **amounts**, despite its name. In this course $x$ is a
#   composition, so we copy it into `f` at once;
# - `res.fun` is the best total.

# %%
f = res.x                                   # amounts in kg; "x" is SciPy's name, not a composition
for name, amount in zip(NAMES, f):
    if amount > 1e-12:
        print(f"buy {amount:.4f} kg of {name}")
print(f"best cost: {res.fun:.4f} € per kg")

# %% [markdown]
# Two checks every LP answer must pass, whoever solved it: the rules hold and
# no amount is negative. The messages say in words what went wrong if a check
# fails.

# %%
assert abs(f.sum() - 1) < 1e-9, f"the amounts add to {f.sum():.6f} kg, not 1"
assert abs(f @ W - TARGET) < 1e-9, f"the charge holds {f @ W:.6f} kg Ni, not {TARGET}"   # @: multiply and add
assert f.min() > -1e-12, f"a negative amount: {f.min():.3g}"
if (list(W), list(PRICE), TARGET) == ([0.0, 0.1, 0.3, 0.45, 0.65, 1.0], [7.4, 7.9, 8.4, 10.0, 10.2, 15.5], 0.40):
    confirm(res.fun, 8.914286, "The cheapest charge", tol=1e-5)
else:
    print("You changed the numbers in section 0: no lesson value to compare with.")

# %% [markdown]
# ### Your turn: how many lots?
#
# How many lots does the cheapest charge use? Why can a corner answer of this
# problem never use more?

# %%
lots_used = None   # a whole number
check(lots_used, "f4p_lots_used")

# %% [markdown]
# *After your attempt.* Two lots. A charge of three lots at 0.40 is a mixture of
# two-lot charges, each at 0.40 (pair each lot below 0.40 with one above), and
# the cheaper of those costs no more than the mixture. With two rules a best
# charge never needs more than two lots; a corner answer has at most as many
# non-zero amounts as rules.

# %% [markdown]
# ## 3. The search, one swap at a time (main track, 10 min)
#
# Trying every pair works for six lots, not for thousands. A solver searches:
#
# 1. start from a pair that can make the charge, here Cu and Ni;
# 2. draw the line through the two used lots; for every lot compute its price
#    minus the line's height at its content (its *gap*);
# 3. if no gap is negative, stop. Otherwise the lot with the most negative gap
#    comes in, and the used lot on the same side of the target goes out (only
#    that swap keeps both amounts positive). Go to 2.
#
# This is the (primal) simplex method on a two-rule problem. The cost never rises.

# %%
used = [0, 5]                                          # Cu and Ni: indices into the lists above
for round_ in range(1, 10):
    a, b = used
    slope = (PRICE[b] - PRICE[a]) / (W[b] - W[a])      # the line through the two used lots
    base = PRICE[a] - slope * W[a]                     # its height at w = 0
    gap = PRICE - (base + slope * W)                   # price minus line, for every lot
    f_b = (TARGET - W[a]) / (W[b] - W[a])
    cost = (1 - f_b) * PRICE[a] + f_b * PRICE[b]
    print(f"round {round_}: {NAMES[a]} + {NAMES[b]}, cost {cost:.3f} €; gaps " + ", ".join(f"{n} {g:+.3f}" for n, g in zip(NAMES, gap)))
    enter = int(np.argmin(gap))
    if gap[enter] > -1e-9:
        print("no lot below the line: done")
        break
    leave = a if (W[a] - TARGET) * (W[enter] - TARGET) > 0 else b   # the used lot on the entering lot's side
    print(f"         {NAMES[enter]} comes in, {NAMES[leave]} goes out")
    used = sorted([k for k in used if k != leave] + [enter], key=lambda k: W[k])

# %% [markdown]
# The course module `lp_primer` holds the same search; the website's lab plays
# its rounds. Both agree with `linprog`.

# %%
from course.self_study import lp_primer
my_lots = [lp_primer.Lot(n, n, w, p) for n, w, p in zip(NAMES, W, PRICE)]   # your numbers from section 0
frames = lp_primer.swap_path(my_lots, TARGET, (0, 5))
print([[NAMES[k] for k in frame["used"]] for frame in frames], "final cost", frames[-1]["cost"])
assert abs(frames[-1]["cost"] - res.fun) < 1e-6

# %% [markdown]
# ## 4. Prices, and a line under every lot (main track, 15 min)
#
# Besides the amounts, `linprog` returns one **price** per rule in
# `res.eqlin.marginals`: how much the best total changes per unit increase of
# that rule's right-hand side (its entry of `b_eq`), for small changes, while the same lots stay in
# use. For our two rules (1 kg, 0.40 kg Ni) they are the height and the slope
# of a straight line, $\text{base}+\text{slope}\times w$.

# %%
base, slope = res.eqlin.marginals     # d(best cost)/d(1 kg) and d(best cost)/d(target)
print(f"base = {base:.4f} €   slope = {slope:.4f} € per unit content")
print(f"line at w = 0: {base:.2f} € (1 kg of Cu is worth this here)")

# %% [markdown]
# **The check that proves it.** Subtract the line's height from every lot's
# price: the gap. If no gap is negative, every lot costs at least the line's
# height at its content, so every charge costs at least the line's height at
# the target. Our charge costs exactly that: nothing can be cheaper.

# %%
gap = PRICE - (base + slope * W)
for name, g in zip(NAMES, gap):
    print(f"{name:7s} gap {g:+.4f} €")
assert gap.min() > -1e-9, "a lot lies below the line: the line is not a floor"
line_at_target = base + slope * TARGET
assert abs(line_at_target - res.fun) < 1e-9, "the line at the target does not meet the cheapest charge"
print(f"line at the target: {line_at_target:.4f} € = cheapest charge {res.fun:.4f} €")

# %% [markdown]
# ### Your turn: what is 1 kg of nickel worth in this charge?
#
# Hint: 1 kg of copper is worth the line's height at $w=0$.

# %%
ni_worth = None   # € per kg
check(ni_worth, "f4p_ni_worth")

# %% [markdown]
# **Check a price by solving again.** Nudge the target from 0.40 to 0.41. The
# slope predicts the change; a new solve measures it.

# %%
def best_cost(target):
    """Cheapest cost of 1 kg at this target; None when no charge can make it."""
    r = linprog(c, A_eq=A_eq, b_eq=[1.0, target], bounds=(0, None), method="highs-ds")
    return r.fun if r.status == 0 else None

for nudge in (0.01, 0.30):
    measured = best_cost(TARGET + nudge) - res.fun
    print(f"target {TARGET:.2f} → {TARGET + nudge:.2f}: predicted {slope * nudge:+.4f} €, measured {measured:+.4f} €")

# %% [markdown]
# The small nudge matches. The large one does not: at 0.70 the target has
# passed Monel (0.65), other lots come into use and the price changes. A price
# holds only while the same lots stay in use, here for targets from 0.30 to
# 0.65. The picture: the cheapest cost for every target is the lowest chord
# under the dots, a bent line whose slope is the price.

# %%
targets = np.linspace(0, 1, 101)
costs = [best_cost(t) for t in targets]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(targets, costs, color=MIN_C, lw=2, label="cheapest cost for every target")
ax.scatter(W, PRICE, color=LOT_C, zorder=3)
ax.plot([0, 1], [base, base + slope], color=LINE_C, ls="--", label="price line at 0.40")
ax.set_xlabel("target Ni content"); ax.set_ylabel("€ per kg"); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# ### Your turn: a new offer
#
# A dealer offers swarf at $w=0.50$ for €9.20 per kg. What is its gap (price
# minus the line's height at 0.50)? Is it worth buying?

# %%
offer_gap = None   # €, with its sign
check(offer_gap, "f4p_offer_gap")

# %% [markdown]
# *After your attempt.* Add the swarf to the lists and solve again. Checking one
# new candidate against the line, without solving again, is called pricing;
# step 13 uses it to find missing states.

# %%
res_offer = linprog(np.append(c, 9.20), A_eq=np.column_stack([A_eq, [1.0, 0.50]]), b_eq=b_eq, bounds=(0, None), method="highs-ds")
print(f"with the swarf: {res_offer.fun:.3f} € per kg, amounts {np.round(res_offer.x, 3) + 0.0}")

# %% [markdown]
# ## 5. The textbook picture (main track, 15 min)
#
# Books draw LPs with the amounts on the axes. Take two lots, CuNi30 (amount
# $f_P$) and Monel (amount $f_Q$), and four rules of the kind melt shops have:
#
# | Rule | In symbols |
# |---|---|
# | the charge weighs at least 1 kg | $f_P+f_Q\ge1$ |
# | it holds at least 0.40 kg nickel | $0.30f_P+0.65f_Q\ge0.40$ |
# | it holds at most 0.012 kg iron (CuNi30 0.6 %, Monel 2.0 % Fe) | $0.006f_P+0.020f_Q\le0.012$ |
# | the furnace holds at most 1.5 kg | $f_P+f_Q\le1.5$ |
#
# `linprog` wants "at most" rules (`A_ub @ f <= b_ub`), so an "at least" rule
# is multiplied by $-1$. Remember which rows you flipped: their prices flip
# sign too.

# %%
P_PRICE, Q_PRICE = 8.40, 10.20
A_ub = np.array([[-1.0, -1.0],      # weight at least 1 kg, times -1
                 [-0.30, -0.65],    # nickel at least 0.40 kg, times -1
                 [0.006, 0.020],    # iron at most 0.012 kg
                 [1.0, 1.0]])       # furnace at most 1.5 kg
b_ub = np.array([-1.0, -0.40, 0.012, 1.5])
FLIPPED = np.array([-1, -1, 1, 1])  # -1 marks a rule multiplied by -1
RULE_NAMES = ["weight", "nickel", "iron", "furnace"]
poly = linprog([P_PRICE, Q_PRICE], A_ub=A_ub, b_ub=b_ub, bounds=(0, None), method="highs-ds")
print(poly.message)
print(f"buy {poly.x[0]:.3f} kg CuNi30 and {poly.x[1]:.3f} kg Monel, cost {poly.fun:.3f} €")

# %% [markdown]
# **Corners by hand.** Every corner of the allowed region is where two
# boundary lines meet and every rule holds. Try every pair of lines (the four
# rules and the two axes), keep the allowed points, and price them.

# %%
lines = [(row * s, rhs * s, name) for row, rhs, s, name in zip(A_ub, b_ub, FLIPPED, RULE_NAMES)]
lines += [(np.array([1.0, 0.0]), 0.0, "no CuNi30"), (np.array([0.0, 1.0]), 0.0, "no Monel")]
corners = []
for k in range(len(lines)):
    for m in range(k + 1, len(lines)):
        M = np.array([lines[k][0], lines[m][0]])
        if abs(np.linalg.det(M)) < 1e-12:
            continue                                         # parallel lines never meet
        point = np.linalg.solve(M, [lines[k][1], lines[m][1]])
        if point.min() > -1e-9 and np.all(A_ub @ point <= b_ub + 1e-9):
            corners.append((point, lines[k][2], lines[m][2]))
for point, r1, r2 in corners:
    print(f"({point[0]:.3f}, {point[1]:.3f})  {r1} and {r2} tight   cost {P_PRICE * point[0] + Q_PRICE * point[1]:.3f} €")

# %% [markdown]
# ### Your turn: one corner
#
# What does the corner where the weight and iron rules are tight cost?

# %%
corner_cost = None   # €
check(corner_cost, "f4p_corner_cost")

# %% [markdown]
# The picture: the allowed region, the four rule lines and the cheapest cost
# line. Slide a cost line $8.40f_P+10.20f_Q=C$ towards lower $C$ until it is
# about to leave the region: it last touches a corner.

# %%
centre = np.mean([p for p, _, _ in corners], axis=0)                       # the polygon's middle
order = np.argsort([np.arctan2(p[1] - centre[1], p[0] - centre[0]) for p, _, _ in corners])
region = np.array([corners[k][0] for k in order])
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.fill(region[:, 0], region[:, 1], color="#2a9d8f", alpha=0.25, label="allowed charges")
fp = np.linspace(0, 1.7, 2)
for (row, rhs, name) in lines[:4]:
    ax.plot(fp, (rhs - row[0] * fp) / row[1], lw=1.2, label=name)
ax.plot(fp, (poly.fun - P_PRICE * fp) / Q_PRICE, color=MIN_C, lw=2.4, ls="--", label=f"cost {poly.fun:.2f} €")
ax.plot(*poly.x, "o", color=MIN_C, ms=9)
ax.set_xlim(0, 1.7); ax.set_ylim(0, 0.8)
ax.set_xlabel("f_P: kg of CuNi30"); ax.set_ylabel("f_Q: kg of Monel"); ax.legend(frameon=False, fontsize=8, ncol=2)
plt.show()

# %% [markdown]
# **Prices and slack.** `res.slack` is the room left in each rule (zero when
# the rule is tight). `res.ineqlin.marginals` holds the prices; for the rows
# you multiplied by $-1$, flip the sign back.

# %%
for name, room, price, s in zip(RULE_NAMES, poly.slack, poly.ineqlin.marginals, FLIPPED):
    print(f"{name:8s} room left {room:.4f}   price {s * price + 0.0:+.4f} €")   # + 0.0 turns a printed -0.0 into 0.0

# %% [markdown]
# The weight rule costs €6.86 per kg and the nickel rule €5.14 per kg of
# nickel: the same numbers as the line under the dots in section 4. (More
# nickel in the same weight swaps copper, worth €6.86, for nickel, worth
# €12.00: 12.00 − 6.86 = 5.14.) Above 0.45 kg of nickel the iron cap takes over
# from the weight rule and the nickel price jumps; try it in `b_ub`. Rules with
# room to spare cost nothing. Make the iron cap strict (0.005 kg) and no
# charge keeps every rule: `linprog` reports status 2.

# %%
strict = linprog([P_PRICE, Q_PRICE], A_ub=A_ub, b_ub=[-1.0, -0.40, 0.005, 1.5], bounds=(0, None), method="highs-ds")
print("strict iron cap: status", strict.status, "-", strict.message)

# %% [markdown]
# ## 6. Same problem, new names: step 10's menu (main track, 5 min)
#
# Rename two columns: Ni content becomes the B atom fraction $x$, price becomes
# the molar Gibbs energy $g$ in J/mol atoms, and amounts are moles of atoms
# instead of kilograms (atom fractions instead of mass fractions). Lots become states: one phase model
# at one composition, the ten dots of step 10's menu. The same `linprog` call
# then solves step 10, and its two prices are $\mu_A$, the line's height at
# $x=0$, and $\Delta\mu=\mu_B-\mu_A$, its slope.
#
# One difference matters. Costs add because lots are bought and melted
# separately. A mixture of menu dots adds energies the same way, as a real sample
# of separate regions (boundary energy ignored), so the true equilibrium is at or
# below it: the menu's cheapest mixture is a ceiling. It need not be the truth,
# because states between the dots are missing: if the atoms of two dots of one
# phase model form one phase at the average composition, its energy lies on that
# phase's curve, which can lie below the chord.

# %%
from course.self_study import day3_core
models = day3_core.lens_models(1400.0)                     # step 03 part C's melting lens
X = np.array([0.1, 0.3, 0.5, 0.7, 0.9] * 2)                # the menu's compositions, both phases
G = np.array([float(models[p].g(x)) for p in ("SOLID", "LIQUID") for x in X[:5]])   # J/mol atoms
menu = linprog(G, A_eq=np.array([np.ones(10), X]), b_eq=[1.0, 0.40], bounds=(0, None), method="highs-ds")
mu_A, d_mu = menu.eqlin.marginals
print(f"cheapest mixture {menu.fun:.2f} J/mol atoms; mu_A = {mu_A:.1f}, d_mu = {d_mu:.1f} J/mol")
confirm(menu.fun, -20429.542431, "Step 10's cheapest mixture", tol=1e-5)

# %% [markdown]
# ## 7. The companion problem about prices (dive deeper, 10 min)
#
# Every LP has a companion problem, its *dual*. Here it asks: of all straight
# lines $\text{base}+\text{slope}\times w$ that stay on or below every lot, which
# is highest at the target? In symbols: maximise $\text{base}+0.40\,\text{slope}$
# subject to $\text{base}+\text{slope}\times w_j\le c_j$ for every lot. The two
# prices are now the variables, and they may be negative (`bounds=(None, None)`).
# `linprog` only minimises, so minimise the negative and negate the answer.

# %%
dual = linprog([-1.0, -TARGET], A_ub=np.column_stack([np.ones(len(W)), W]), b_ub=PRICE,
               bounds=(None, None), method="highs-ds")
print(f"highest line at the target: {-dual.fun:.4f} € (base {dual.x[0]:.4f}, slope {dual.x[1]:.4f})")
print(f"cheapest charge:            {res.fun:.4f} €")

# %% [markdown]
# They meet. Any line under the lots is a floor for every charge (weak
# duality); the highest one meets the cheapest charge (strong duality). A lot
# strictly above the best line is never used (complementary slackness).

# %% [markdown]
# ## 8. Unbounded, and prices that are not unique (dive deeper, 10 min)
#
# **Unbounded.** Drop "no amount is negative": a negative amount means selling
# a lot you do not have. Then the cost can fall without limit.

# %%
free = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(None, None), method="highs-ds")
print("amounts may be negative: status", free.status, "-", free.message)

# %% [markdown]
# **Prices that are not unique.** Put the target exactly on a used lot, 0.30
# (CuNi30). The best charge is clear, 1 kg of CuNi30. But many lines touch the
# dots there: the price to the left differs from the price to the right, and
# two solver methods may return different ones.

# %%
for method in ("highs-ds", "highs-ipm"):
    r = linprog(c, A_eq=A_eq, b_eq=[1.0, 0.30], bounds=(0, None), method=method)
    print(f"{method:9s} cost {r.fun:.4f} €  amounts {np.round(r.x, 3) + 0.0}  prices {np.round(r.eqlin.marginals, 4)}")

# %% [markdown]
# Here: same cost, same amounts, two different slopes (which method returns
# which can depend on the solver version). Each is a valid line under all lots.
#
# This matters when the list is short. Keep only Cu and Monel and put the target
# on Monel, 0.65. The best charge is 1 kg Monel; the line through Cu and Monel
# is one valid answer for the prices. CuNi30 lies below that line, yet 1 kg
# Monel is already the cheapest charge of all six lots. So with a target on a
# used lot, a lot below the returned line does not prove that the charge can be
# improved; step 15 meets this again.

# %%
cu, monel, cuni30 = 0, 4, 2                                   # indices into the lists of section 0
slope_cm = (PRICE[monel] - PRICE[cu]) / (W[monel] - W[cu])    # the line through Cu and Monel
gap_cuni30 = PRICE[cuni30] - (PRICE[cu] + slope_cm * W[cuni30])
print(f"short list: 1 kg Monel, {PRICE[monel]:.2f} €; CuNi30 lies {-gap_cuni30:.2f} € below the Cu-Monel line")
print(f"all six lots at 0.65: {best_cost(0.65):.2f} € (still 1 kg Monel)")

# %% [markdown]
# ## 9. Exercises (both tracks, 20 min)
#
# **Exercise 1 (main).** Make 2 kg of solder with at least 1.2 kg of tin, from
# alloy A (0.5 tin, €20 per kg) and alloy B (0.7 tin, €26 per kg), as cheaply as
# possible. Write it for `linprog` and give the best cost.

# %%
solder_cost = None   # €
check(solder_cost, "f4p_solder_cost")

# %% [markdown]
# **Exercise 2 (main).** In the textbook picture, Monel costs €8.00 instead of
# €10.20. What does the cheapest charge cost now? Which rules are tight?

# %%
monel8_cost = None   # €
check(monel8_cost, "f4p_monel8_cost")

# %% [markdown]
# *After your attempt.*

# %%
solder = linprog([20.0, 26.0], A_eq=[[1.0, 1.0]], b_eq=[2.0], A_ub=[[-0.5, -0.7]], b_ub=[-1.2],
                 bounds=(0, None), method="highs-ds")
print(f"solder: {solder.x.round(3)} kg, {solder.fun:.2f} €")
cheap = linprog([P_PRICE, 8.00], A_ub=A_ub, b_ub=b_ub, bounds=(0, None), method="highs-ds")
print(f"Monel at €8.00: {cheap.x.round(3)} kg, {cheap.fun:.3f} €; tight: "
      + ", ".join(n for n, room in zip(RULE_NAMES, cheap.slack) if room < 1e-9))

# %% [markdown]
# ## What you have done
#
# - You wrote a linear programme in plain words and in `linprog`'s arrays.
# - You read its status, amounts, best total and prices, and checked them: the
#   rules hold, nothing is negative, and a line under every lot proves that
#   nothing is cheaper.
# - You saw that a price holds only while the same lots stay in use, and that
#   it can be non-unique when the target sits on a used lot.
# - With two columns renamed, the same call solved step 10's menu. Continue
#   with step 10 on the website, or notebook f4c for its code.
