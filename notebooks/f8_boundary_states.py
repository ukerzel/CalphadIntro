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
# # f8 · Two candidate boundary states
#
# **Learning question:** the same invented boundary could take one of two
# structures. Which one has the lower energy, and what must be held the same
# before two energies may be compared at all?
#
# Used in: Day 2 D7, Lesson 14, Clinic D, self-study step 04 extension.
# It continues [f7](f7_boundary_open_closed.ipynb): same cell, same bulk, closed
# inventory. Work each "your turn" on paper first, then type your value; four
# significant figures are enough unless a question asks for more.

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
# ## 1. Two states on one basis (D7, Lesson 14A)
#
# The cell is the one from f7: T = 1000 K, p = 100000 Pa, 8000 bulk sites and two
# equivalent boundaries of 100 sites and 20 nm² each, every site holding one A
# or one B atom. The bulk is the invented ideal ALPHA curve (J/mol of sites,
# $RT=8314.5$ J/mol):
#
# $$g_b(x)=-9000+12000\,x+RT\,[x\ln x+(1-x)\ln(1-x)].$$
#
# Both boundaries take **one** of two invented structures. Each structure has its
# own baseline $\eta_i$ and B preference $\delta_i$:
#
# $$g_{s,i}(\theta)=g_b(\theta)+\eta_i+\delta_i\,\theta .$$
#
# | State | baseline $\eta_i$ (J/mol boundary sites) | preference $\delta_i$ (J/mol boundary sites) |
# |---|---:|---:|
# | I | 0 | −5000 |
# | II | +2000 | −10000 |
#
# State II pays a baseline but likes B more. Neither number is measured.
#
# **What is held the same.** For a chosen start $x_0$, both states start with
# $\theta_0=0.25$ on both boundaries, so they share one closed inventory
# $B_{\rm tot}=8000x_0+200(0.25)=8000x_0+50$. Each state then settles on its own
# $\theta$ and its own final bulk fraction $x_b=(B_{\rm tot}-200\theta)/8000$.
# The energy compared is the closed-cell energy per mole of **all 8200 cell
# sites** (f7, section 3), now with the baseline included:
#
# $$\bar g_i(\theta)=\frac{8000\,g_b[x_b(\theta)]+200\,g_{s,i}(\theta)}{8200}.$$
#
# The baseline does not depend on $\theta$, so it does not move the selected
# occupancy; it only shifts the energy, by $200\,\eta_i/8200$ J/mol all cell sites.

# %%
import numpy as np

RT = 8.3145 * 1000.0                     # J/mol at T = 1000 K
N_BULK, N_BOUNDARY = 8000, 200           # bulk sites; sites on both boundaries
N_SITES = N_BULK + N_BOUNDARY            # 8200 cell sites
THETA_0 = 0.25                           # starting boundary occupancy
STATES = {"I": (-5000.0, 0.0),           # (δ, η) in J/mol boundary sites
          "II": (-10000.0, 2000.0)}

def g_bulk(x):
    return -9000.0 + 12000.0 * x + RT * (x * np.log(x) + (1 - x) * np.log(1 - x))   # J/mol sites

def g_site(theta, delta, eta):
    return g_bulk(theta) + eta + delta * theta                                        # J/mol boundary sites

def B_total(x0):
    return N_BULK * x0 + N_BOUNDARY * THETA_0                                         # B atoms in the cell

def x_bulk(theta, B_tot):
    return (B_tot - N_BOUNDARY * theta) / N_BULK                                      # B per bulk site

def g_bar(theta, B_tot, delta, eta):
    xb = x_bulk(theta, B_tot)
    return (N_BULK * g_bulk(xb) + N_BOUNDARY * g_site(theta, delta, eta)) / N_SITES  # J/mol all cell sites

for name, (delta, eta) in STATES.items():
    print(f"State {name}: δ = {delta:7.0f}, η = {eta:5.0f} J/mol boundary sites")
print(f"Shared inventory: x0 = 0.10 gives B_tot = {B_total(0.10):.0f}; x0 = 0.25 gives {B_total(0.25):.0f}")
print("\nUnrelaxed trials at B_tot = 850 (not yet minima):")
for trial in (0.15, 0.20, 0.30, 0.35):
    print(f"  θ = {trial:.2f}: ḡ_I = {g_bar(trial, 850, *STATES['I']):.4f}, "
          f"ḡ_II = {g_bar(trial, 850, *STATES['II']):.4f} J/mol all cell sites")

# %% [markdown]
# ## 2. Let each state settle, then compare (D7)
#
# Each state is minimised **separately** at the shared inventory. As in f7, the
# minimum satisfies the exchange condition $g_{s,i}'(\theta)=g_b'(x_b)$, which
# gives the odds formula with that state's own preference:
#
# $$\frac{\theta}{1-\theta}=\frac{x_b}{1-x_b}\,\exp(-\delta_i/RT),
# \qquad x_b=\frac{B_{\rm tot}-200\theta}{8000}.$$
#
# The hand method from f7 repeats: odds formula at the current $x_b$, then update
# $x_b$ from the fixed inventory. The cell below runs that loop for both states.
# Compare the two settled energies with
#
# $$D=\bar g_{II}^*-\bar g_I^*\quad\text{at one } x_0 .$$
#
# Positive $D$: State I is lower. Negative $D$: State II is lower.

# %%
def settle(x0, delta, eta, rounds=60):
    """Hand iteration at fixed inventory: odds formula, then update x_b."""
    B_tot = B_total(x0)
    xb = x0
    for _ in range(rounds):
        odds = xb / (1 - xb) * np.exp(-delta / RT)
        theta = odds / (1 + odds)
        xb = x_bulk(theta, B_tot)
    return theta, xb, g_bar(theta, B_tot, delta, eta)

print("x0     B_tot   state  θ*           ḡ* (J/mol all cell sites)")
for x0 in (0.10, 0.25):
    for name, (delta, eta) in STATES.items():
        theta, xb, g = settle(x0, delta, eta)
        print(f"{x0:.2f}   {B_total(x0):5.0f}   {name:<5}  {theta:.8f}   {g:.5f}")

# %% [markdown]
# ### Your turn
#
# Use the settled values printed above (they are the D7 table).
#
# 1. $D$ at $x_0=0.10$ and at $x_0=0.25$; name the lower state in each row
#    (`"I"` or `"II"`). Is "State II at $x_0=0.25$ minus State I at $x_0=0.10$" a
#    meaningful comparison?
# 2. Row $x_0=0.10$: State II's boundary B count, its bulk B count and its final
#    $x_b$; State I's bulk B count. Could both states keep the same final $x_b$
#    and still hold 850 B each?
# 3. A report drops $\eta_{II}$. What is State II's energy at $x_0=0.10$ without
#    the baseline, and which state would that report call lower?
# 4. Someone compares both states at the unrelaxed start $\theta=0.25$ in the
#    $x_0=0.25$ cell. What $D$ do they get, and which state would they pick?

# %%
D_010 = None                  # J/mol all cell sites
lower_010 = None              # "I" or "II"
D_025 = None                  # J/mol all cell sites
lower_025 = None              # "I" or "II"
cross_row_meaningful = None   # True or False
check(D_010, "f8_d7_D_010")
check(lower_010, "f8_d7_lower_010")
check(D_025, "f8_d7_D_025")
check(lower_025, "f8_d7_lower_025")
check(cross_row_meaningful, "f8_d7_cross_row")

# %%
boundary_B_II = None          # B atoms on both boundaries, State II, 850 B
bulk_B_II = None              # B atoms in the bulk, State II
x_b_II = None                 # B per bulk site, State II
bulk_B_I = None               # B atoms in the bulk, State I
same_x_b_possible = None      # True or False
check(boundary_B_II, "f8_d7_boundary_B_II")
check(bulk_B_II, "f8_d7_bulk_B_II")
check(x_b_II, "f8_d7_x_b_II")
check(bulk_B_I, "f8_d7_bulk_B_I")
check(same_x_b_possible, "f8_d7_same_x_b")

# %%
baseline_all_sites = None     # J/mol all cell sites, η_II = 2000
g_II_no_baseline = None       # J/mol all cell sites, x0 = 0.10
lower_no_baseline = None      # "I" or "II"
D_unrelaxed_025 = None        # J/mol all cell sites, both at θ = 0.25, x0 = 0.25
lower_unrelaxed_025 = None    # "I" or "II"
check(baseline_all_sites, "f8_d7_baseline")
check(g_II_no_baseline, "f8_d7_g_II_no_baseline")
check(lower_no_baseline, "f8_d7_lower_no_baseline")
check(D_unrelaxed_025, "f8_l14_D_unrelaxed")
check(lower_unrelaxed_025, "f8_l14_lower_unrelaxed")

# %% [markdown]
# ## 3. Where does the order switch? (Lesson 14B)
#
# $D$ is positive at $x_0=0.10$ and negative at $x_0=0.25$, so it changes sign
# somewhere in between. Each $x_0$ is a **different** closed cell; the scan below
# simply repeats the same-inventory comparison for several cells from 0.10 to 0.35.

# %%
starts = np.round(np.arange(0.10, 0.351, 0.05), 2)   # 6 starting bulk fractions, 0.10 to 0.35

def D_at(x0, eta_II=2000.0):
    g_I = settle(x0, -5000.0, 0.0)[2]
    g_II = settle(x0, -10000.0, eta_II)[2]
    return g_II - g_I                                   # J/mol all cell sites

print("x0     B_tot   D = ḡ_II* − ḡ_I* (J/mol all cell sites)")
for x0 in starts:
    print(f"{x0:.2f}   {B_total(x0):5.0f}   {D_at(x0):9.4f}")

# %% [markdown]
# ### Your turn
#
# 1. Find the crossing $x_0$ (where $D=0$) to four decimals. Halve the interval
#    by hand with `D_at`, or write a short loop.
# 2. Change **only** $\eta_{II}$ from 2000 to 2100 J/mol boundary sites. By how
#    much does $D$ shift at any fixed $x_0$? Does State II's selected $\theta$
#    change? Where does the crossing move (four decimals)?

# %%
x0_crossing = None            # starting bulk B fraction where D = 0
D_shift_2100 = None           # J/mol all cell sites
theta_II_changes = None       # True or False
x0_crossing_2100 = None       # starting bulk B fraction, η_II = 2100
check(x0_crossing, "f8_l14_crossing")
check(D_shift_2100, "f8_l14_shift_2100")
check(theta_II_changes, "f8_l14_theta_changes")
check(x0_crossing_2100, "f8_l14_crossing_2100")

# %% [markdown]
# ## 4. A fresh card from Clinic D
#
# Same model, a new closed cell started at $x_0=0.40$, $\theta_0=0.25$. The
# separately settled values are supplied:
#
# | State | $\theta^*$ | final $x_b$ | $\bar g^*$ (J/mol all cell sites) |
# |---|---:|---:|---:|
# | I | 0.54127054 | 0.39271824 | −9884.21053 |
# | II | 0.67967666 | 0.38925808 | −9910.05801 |
#
# Find total B and total A, check the B balance of each state, then $D$ and the
# lower state. Give State II's equal-site excess $5(\theta-x_b)$ in atom/nm²
# (f7, section 1). Finally write two sentences for a presenter who calls this a
# measured Ni–Cu result and the switch a confirmed boundary transition: one thing
# this invented model does show, and one missing piece of evidence.

# %%
card_total_B = None           # B atoms in the cell
card_total_A = None           # A atoms in the cell
card_D = None                 # J/mol all cell sites
card_lower = None             # "I" or "II"
card_excess_II = None         # atom/nm²
check(card_total_B, "f8_clinic_total_B")
check(card_total_A, "f8_clinic_total_A")
check(card_D, "f8_clinic_D")
check(card_lower, "f8_clinic_lower")
check(card_excess_II, "f8_clinic_excess_II")

# %% [markdown]
# ## 5. After your attempt: the course code and the pictures
#
# The course module `boundary_two_state` minimises each state's full closed-cell
# energy with a bounded minimiser (not the hand iteration above) and brackets
# the crossing with a root finder.

# %% cellView="form"
#@title After your attempt: the D7 table, the baseline and the crossing
from course.foundations.boundary_two_state import compare_states, crossing
import matplotlib.pyplot as plt

lesson = {0.10: (0.17160753, -10541.72679, 0.26898258, -10519.50695, 22.21984),
          0.25: (0.37428128, -10713.32958, 0.51703766, -10718.80845, -5.47887)}
for x0, (th_I, g_I, th_II, g_II, D) in lesson.items():
    pair = compare_states(x0)
    print(f"x0 = {x0:.2f}: θ_I = {pair['I']['theta']:.8f}, ḡ_I = {pair['I']['G_molar_J_per_mol_sites']:.5f}; "
          f"θ_II = {pair['II']['theta']:.8f}, ḡ_II = {pair['II']['G_molar_J_per_mol_sites']:.5f}; "
          f"D = {pair['difference_J_per_mol_sites']:+.5f} J/mol all cell sites")
    confirm(pair["I"]["theta"], th_I, f"θ_I at x0 = {x0:.2f}", tol=1e-7)
    confirm(pair["II"]["theta"], th_II, f"θ_II at x0 = {x0:.2f}", tol=1e-7)
    confirm(pair["I"]["G_molar_J_per_mol_sites"], g_I, f"ḡ_I at x0 = {x0:.2f}", tol=1e-5)
    confirm(pair["II"]["G_molar_J_per_mol_sites"], g_II, f"ḡ_II at x0 = {x0:.2f}", tol=1e-5)
    confirm(pair["difference_J_per_mol_sites"], D, f"D at x0 = {x0:.2f}", tol=1e-5)
    confirm(settle(x0, -10000.0, 2000.0)[2] - settle(x0, -5000.0, 0.0)[2], D,
            f"D at x0 = {x0:.2f} from the hand iteration above", tol=1e-5)

row = compare_states(0.10)
for name in ("I", "II"):
    s = row[name]
    print(f"State {name} at 850 B: boundary B = {200 * s['theta']:.6f}, bulk B = {8000 * s['x_bulk']:.6f}, x_b = {s['x_bulk']:.8f}")
    confirm(200 * s["theta"] + 8000 * s["x_bulk"], 850, f"B balance of State {name}", tol=1e-9)
confirm(200 * row["II"]["theta"], 53.796516, "State II boundary B", tol=1e-5)
confirm(8000 * row["II"]["x_bulk"], 796.203484, "State II bulk B", tol=1e-5)
confirm(8000 * row["I"]["x_bulk"], 815.678494, "State I bulk B", tol=1e-5)
confirm(200 * 2000 / 8200, 48.78049, "Baseline per mole of all cell sites", tol=1e-5)
print(f"Without the baseline, State II at x0 = 0.10 would read {-10519.50695 - 200 * 2000 / 8200:.5f} J/mol, "
      "below State I: the report would pick the wrong state.")
print(f"Unrelaxed comparison at θ = 0.25, x0 = 0.25: D = {g_bar(0.25, 2050, -10000, 2000) - g_bar(0.25, 2050, -5000, 0):+.5f} "
      "J/mol (= 200(2000 − 5000·0.25)/8200), the opposite sign to the settled D.")

cross = {}
for eta, expected in ((1900, 0.20187111), (2000, 0.21618678), (2100, 0.23094775)):
    cross[eta] = crossing(eta)
    confirm(cross[eta]["x_initial"], expected, f"Crossing for η_II = {eta}", tol=1e-8)
confirm(cross[2000]["I"]["theta"], 0.332074, "θ_I at the crossing", tol=1e-6)
confirm(cross[2000]["II"]["theta"], 0.470497, "θ_II at the crossing", tol=1e-6)
shift = compare_states(0.10, 2100)["difference_J_per_mol_sites"] - compare_states(0.10)["difference_J_per_mol_sites"]
confirm(shift, 2.43902, "D shift for η_II = 2100", tol=1e-5)

for x0, expected in ((0.30, -12.92385), (0.40, -25.84748)):   # Clinic D cards
    confirm(compare_states(x0)["difference_J_per_mol_sites"], expected, f"Clinic D: D at x0 = {x0:.2f}", tol=1e-5)
card = compare_states(0.40)["II"]
confirm(5 * (card["theta"] - card["x_bulk"]), 1.4520929, "Clinic D: State II excess at x0 = 0.40", tol=1e-6)

# Pictures: both settled energies against the inventory, and their difference.
grid = np.round(np.arange(0.10, 0.901, 0.05), 2)
pairs = [compare_states(x0) for x0 in grid]
g_I = np.array([p["I"]["G_molar_J_per_mol_sites"] for p in pairs])
g_II = np.array([p["II"]["G_molar_J_per_mol_sites"] for p in pairs])
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2))
left.plot(grid, g_I / 1000, "o-", label="State I (η = 0, δ = −5000)")
left.plot(grid, g_II / 1000, "s--", label="State II (η = 2000, δ = −10000)")
left.set(xlabel="starting bulk B fraction x0 (sets B_tot = 8000 x0 + 50)",
         ylabel="settled ḡ* (kJ/mol all cell sites)", title="Each point is its own closed cell")
left.legend(fontsize=10)
right.axhline(0, color="grey", lw=0.8)
for eta, style in ((1900, "^:"), (2000, "o-"), (2100, "v--")):
    D = [compare_states(x0, eta)["difference_J_per_mol_sites"] for x0 in grid]
    right.plot(grid, D, style, label=f"η_II = {eta}")
    right.plot([cross[eta]["x_initial"]], [0], "kx", ms=9)
right.set(xlabel="starting bulk B fraction x0", ylabel="D = ḡ_II* − ḡ_I* (J/mol all cell sites)",
          title="Above 0: I lower · below 0: II lower (× = crossing)")
right.legend(fontsize=10)
fig.tight_layout()
plt.show()
print(" x0    B_tot    ḡ_I*          ḡ_II*          D")
for x0, a, b in zip(grid, g_I, g_II):
    print(f" {x0:.2f}  {8000 * x0 + 50:5.0f}  {a:12.5f}  {b:12.5f}  {b - a:+9.5f}")

# %% [markdown]
# Full worked answers: [Day 2 answers](../course/primer_day2/answers.md) (D7),
# [Lesson 14](../course/foundations/lesson_14_competing_states.md) and
# [Clinic D](../course/foundations/clinic_d_synthetic_boundary.md).
#
# ## 6. Limits
#
# Both structures are invented: their baselines and preferences are chosen
# numbers, and the bulk is the invented ideal ALPHA curve. Each state is one
# uniform structure for both boundaries; the model has no boundary made of
# patches of I and II, no path between them and no atomistic structure. An
# energy crossing between two invented candidates is therefore not a real
# boundary transition, and it says nothing about Ni–Cu or about strength.
# Energies are compared only within one inventory; values from different $x_0$
# belong to different cells.
# Next, in the classroom route: [Task 03 · a Ni twin boundary from published
# readings](task03_ni_twin.ipynb). In the self-study route this notebook is the
# step 04 extension: go back to the site and continue with step 05 and its
# notebook, [task01 · Cu–Ni equilibria](task01_cuni_equilibria.ipynb).
