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
# # Task 03 · A Ni twin boundary from published readings
#
# **Learning question:** a paper gives the energy of one Ni grain boundary in
# J/m². How do we fit it, and how do we turn it into an energy per mole of
# boundary sites inside one mole of Ni without counting any atom twice?
#
# Used in: Task 03 ([packet](../course/materials/boundaries/ni_twin.md)).
# Work each "your turn" on paper first, then type your value.
#
# **How this notebook works.** Run the cells from top to bottom (Shift + Enter).
# In each "Your turn" cell, replace `None` with your value and run the cell:
# `check(your_value, key)` (key: the name of the stored answer, in quotes) prints "✓ matches", "close" or "not yet" without
# showing the stored answer. The "After your attempt" cells use
# `confirm(value, expected, "what", tol=...)`, which prints a ✓ line when a
# calculation reproduces the lesson value within `tol` and stops with an error
# otherwise.
#
# The steps: read the published curve (1), fit a straight line to it (2), count
# the boundary area and boundary sites in one mole of Ni (3), and convert the
# energy per area into an energy per mole of sites and back (4).

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
# ## 1. The readings and their units
#
# **Source:** F. Fischer, G. Schmitz and S. M. Eich, "A systematic study of grain
# boundary segregation and grain boundary formation energy using a new
# copper–nickel embedded-atom potential," *Acta Materialia* **176** (2019)
# 220–231, [doi:10.1016/j.actamat.2019.06.027](https://doi.org/10.1016/j.actamat.2019.06.027).
# Open Figure 3 (printed page 224).
#
# The course ships eight readings of one curve in that figure: the **blue band
# for pure Ni, coherent Σ3 {111} twin**, read at its middle every 100 K. The
# curve is a grain-boundary formation energy from an atomistic (EAM) simulation,
# integrated from a reference at 500 K. The green dashed curve (internal excess
# energy), the Cu branch and the brown markers are other quantities and are not
# used here.
#
# **Some words.** A *grain boundary* is the interface between two crystals
# (grains) of the same phase with different orientations. Its atoms sit less
# comfortably than in the perfect crystal, so the boundary carries extra energy;
# $\gamma$ is that extra energy per unit area of boundary, in J/m². A *twin
# boundary* is a special boundary where one grain is the mirror image of the
# other across a crystal plane, here a {111} plane of the FCC lattice. "Σ3" says
# that one in three lattice sites of the two grains coincide. A *coherent* twin
# fits so well across the plane that its energy is very low. *EAM* (embedded-atom
# method) is a model of the forces between metal atoms used in atomistic
# simulations.
#
# | Column | Meaning | Unit |
# |---|---|---|
# | `temperature_K` | temperature | K |
# | `gamma_J_per_m2` | formation energy per boundary area | J/m² |
# | `reading_precision_J_per_m2` | how precisely the plot can be read | J/m² |
#
# The ±0.001 J/m² is how well a plot can be read, not an error bar of the
# simulation.
#
# **The code.** `ROOT / "course" / ...` joins folder names into a path. The file
# is read with `csv.DictReader` (each row a dictionary keyed by the column
# names, values as text) and the two columns are turned into numpy arrays.

# %%
import csv
import numpy as np

CURVE = ROOT / "course" / "materials" / "boundaries" / "ni_twin_curve.csv"
with CURVE.open() as handle:  # the file is closed again at the end of the with-block
    rows = list(csv.DictReader(handle))
T = np.array([float(r["temperature_K"]) for r in rows])          # K
gamma = np.array([float(r["gamma_J_per_m2"]) for r in rows])     # J/m²
precision = float(rows[0]["reading_precision_J_per_m2"])         # J/m²
print(" T (K)   γ (J/m²)")
for t, g in zip(T, gamma):
    print(f" {t:5.0f}   {g:.4f}")
print(f"reading precision ±{precision} J/m²")

# %% [markdown]
# ### Your turn
#
# The eight readings come from one integrated simulation curve. Are they eight
# independent measurements?

# %%
independent_measurements = None   # True or False
check(independent_measurements, "task03_independent")

# %% [markdown]
# ## 2. A straight line through the readings
#
# The readings fall almost on a line, so a two-number description $\gamma(T)$
# is enough to give the boundary energy at any temperature in the range.
#
# Fit $\gamma(T)=A+B\,T$ by ordinary (unweighted) least squares. For a straight
# line the solution has a closed form:
#
# $$B=\frac{\sum_k (T_k-\bar T)(\gamma_k-\bar\gamma)}{\sum_k (T_k-\bar T)^2},
# \qquad A=\bar\gamma-B\,\bar T .$$
#
# Residuals are **fit minus reading**, in J/m². The line describes the readings
# between 100 and 800 K only. For this fixed-area teaching line, $-B$ (in
# J/(m² K)) behaves like an entropy per area; the paper determines the boundary
# entropy in its own way, so the slope of a read-off curve is not that quantity.
#
# **Symbols.** $\bar T$ and $\bar\gamma$ are the averages of the eight
# temperatures and eight readings; $k$ counts the readings. "Least squares"
# chooses $A$ and $B$ so that the sum of the squared residuals is as small as
# possible; setting the derivatives of that sum with respect to $A$ and $B$ to
# zero gives the two formulas. $B$ is the slope (J/(m² K)), $A$ the value of the
# line at $T=0$ (J/m²); the line always passes through the point
# $(\bar T,\bar\gamma)$.
#
# **Why $-B$ looks like an entropy.** For a free energy, $\partial G/\partial T=-S$.
# Applied per area, $-d\gamma/dT$ is an entropy per area, and for a straight
# line $d\gamma/dT=B$.
#
# **The code.** `T.mean()` is the average; `np.sum(...)` adds up all elements;
# operations such as `T - T_mean` act on every element of the array at once.
# `def gamma_fit(temperature):` defines a small function that returns the line's
# value; it works for one temperature or a whole array.

# %%
T_mean, gamma_mean = T.mean(), gamma.mean()   # K, J/m²
slope = np.sum((T - T_mean) * (gamma - gamma_mean)) / np.sum((T - T_mean) ** 2)   # J/(m² K)
intercept = gamma_mean - slope * T_mean                                            # J/m²

def gamma_fit(temperature):
    return intercept + slope * temperature   # J/m²

residuals = gamma_fit(T) - gamma                                                   # J/m², fit minus reading
print(f"T̄ = {T_mean:.1f} K, γ̄ = {gamma_mean:.6f} J/m²; the fit is in `intercept`, `slope` and `residuals`.")

# %% [markdown]
# ### Your turn
#
# Work out A (J/m²) and B (J/(m² K)) with the formulas (or print `intercept` and
# `slope`), find the largest absolute residual (J/m²), and convert $-B$ to
# mJ/(m² K). Four significant figures are enough for every answer.
#
# Useful in a scratch cell: `print(intercept, slope)`, `np.abs(residuals)` (the
# absolute values) and `.max()` (the largest element). 1 J = 1000 mJ.

# %%
fit_A = None             # J/m²
fit_B = None             # J/(m² K)
max_abs_residual = None  # J/m²
minus_B_mJ = None        # mJ/(m² K)
check(fit_A, "task03_fit_A")
check(fit_B, "task03_fit_B")
check(max_abs_residual, "task03_max_residual")
check(minus_B_mJ, "task03_minus_B_mJ")

# %% [markdown]
# ## 3. Count the boundary in one mole of Ni
#
# A CALPHAD calculation counts in moles, a boundary energy in square metres.
# To combine the two, we need to know how much boundary area, and how many
# boundary atoms, one mole of Ni contains.
#
# To use an energy per area in a molar calculation we need an area and a number
# of boundary sites. Choose a **fixed teaching geometry** (not the paper's
# simulation box):
#
# | Input | Value | Unit |
# |---|---:|---|
# | FCC Ni lattice parameter $a$ | 0.352 | nm |
# | cubic grains of edge $d$ | 100 | nm |
# | total Ni | 1 | mol |
# | atoms per FCC unit cell | 4 | — |
#
# Molar volume, and boundary area per mole: each cube has six faces, and each
# face is **shared by two grains**, so a grain owns three faces' worth of
# boundary, $3d^2$ per volume $d^3$:
#
# $$V_m=\frac{N_{\rm Av}a^3}{4},\qquad A_{GB}=\frac{3V_m}{d}.$$
#
# Step by step: the cubic FCC unit cell has volume $a^3$ and holds 4 atoms
# (8 corners × 1/8 + 6 face centres × 1/2), so one atom takes $a^3/4$ and one
# mole of atoms ($N_{\rm Av}$ atoms) takes $V_m$. The boundary area per volume is
# $3d^2/d^3=3/d$; multiplied by the volume $V_m$ of one mole, it gives $A_{GB}$
# in m² per mole of Ni.
#
# Site convention: the boundary is two occupied {111} planes, one from each
# grain. A {111} plane has $4/(\sqrt3a^2)$ atoms per area, so
#
# $$\rho=\frac{2}{N_{\rm Av}}\cdot\frac{4}{\sqrt3\,a^2}\ \ \mathrm{mol\ sites/m^2},
# \qquad n_s=\rho A_{GB},\qquad n_b=1-n_s .$$
#
# Where $4/(\sqrt3a^2)$ comes from: the {111} plane cuts the unit cube in an
# equilateral triangle with side $\sqrt2\,a$ and area $\frac{\sqrt3}{2}a^2$. It
# holds 3 atoms at its corners × 1/6 and 3 atoms at the middles of its sides
# × 1/2 (these are face centres of the cube), i.e. 2 atoms, so
# $2\big/\big(\tfrac{\sqrt3}{2}a^2\big)=4/(\sqrt3a^2)$ atoms per m². The factor 2
# in $\rho$ counts the two planes; dividing by $N_{\rm Av}$ turns atoms into
# moles. $n_s$ is the amount of Ni (mol) on boundary sites and $n_b$ the amount
# in the grain interiors (bulk).
#
# Each site holds one real Ni atom. The boundary atoms are part of the one mole;
# they are taken from it, not added to it.
#
# The cell sets up these formulas in SI units (m, m², m³) but does not print
# the values, so that you can work them out first.

# %%
N_AV = 6.02214076e23   # atoms per mol
a = 0.352e-9           # m
d = 100e-9             # m

V_m = N_AV * a**3 / 4                              # m³/mol
A_GB = 3 * V_m / d                                 # m² of boundary per mol Ni
rho = 2 / N_AV * 4 / (np.sqrt(3) * a**2)           # mol boundary sites per m²
n_s = rho * A_GB                                   # mol Ni on boundary sites
n_b = 1 - n_s                                      # mol Ni in the bulk
print("Formulas are set up; fill in the values below, then compare with these variables.")

# %% [markdown]
# ### Your turn
#
# 1. Calculate $V_m$, $A_{GB}$, $\rho$, $n_s$ and $n_b$ on paper (SI units), to at
#    least 4 significant figures (for example `1.234e-05`); round only the final
#    value, not the intermediate steps.
# 2. Someone counts all six cube faces without sharing. What area do they get?
# 3. Someone keeps one mole in the bulk and adds the boundary atoms on top. How
#    many moles of Ni does their cell hold?
#
# In Python, `1.234e-05` means $1.234\times10^{-5}$.

# %%
V_m_answer = None        # m³/mol
A_GB_answer = None       # m²
rho_answer = None        # mol sites/m²
n_s_answer = None        # mol
n_b_answer = None        # mol
A_six_faces = None       # m², the unshared count
total_Ni_wrong = None    # mol, bulk 1 mol plus boundary atoms
check(V_m_answer, "task03_V_m")
check(A_GB_answer, "task03_A_GB")
check(rho_answer, "task03_rho")
check(n_s_answer, "task03_n_s")
check(n_b_answer, "task03_n_b")
check(A_six_faces, "task03_A_six_faces")
check(total_Ni_wrong, "task03_total_wrong")

# %% [markdown]
# ## 4. From J/m² to J/mol of sites, and back
#
# With the area and the number of sites known, the boundary energy can be
# written in the units a CALPHAD model uses: J per mole of sites.
#
# Turn the fitted curve into an energy offset per mole of boundary sites, give
# each boundary site the bulk energy plus this offset, and add up the cell:
#
# $$\varepsilon(T)=\frac{\gamma(T)}{\rho},\qquad g_s=g^{\rm Ni}_{\rm FCC}+\varepsilon,
# \qquad G_{\rm cell}=n_b\,g^{\rm Ni}_{\rm FCC}+n_s\,g_s .$$
#
# Because $n_b+n_s=1$, $G_{\rm cell}-g^{\rm Ni}_{\rm FCC}=n_s\varepsilon=A_{GB}\,\gamma$:
# the boundary adds exactly its area times its energy per area.
#
# **Units and steps.** $\gamma/\rho$ has units (J/m²)/(mol/m²) = J/mol: the
# energy per area divided by the moles of sites per area. Then
# $G_{\rm cell}=n_b\,g+n_s\,(g+\varepsilon)=(n_b+n_s)\,g+n_s\varepsilon=g+n_s\varepsilon$,
# and $n_s\varepsilon=\rho A_{GB}\cdot\gamma/\rho=A_{GB}\gamma$. $G_{\rm cell}$ is
# in J for the whole cell of one mole of Ni.
#
# The bulk $g^{\rm Ni}_{\rm FCC}$ (J/mol) is pure FCC Ni from the published
# Cu–Ni database used in Task 01, at 101325 Pa, evaluated only at 300, 500 and
# 800 K (the database's Ni description starts at 298.15 K). To fetch the
# database, set `DOWNLOAD = True` in the next cell. Without it, the notebook uses
# the values saved by the course run;
# the accounting is the same. Combining a simulated boundary curve with a
# CALPHAD bulk energy in this way is a teaching construction.
#
# **The code.** `database("cuni", download=DOWNLOAD)` returns the path of a
# checked copy of the file, or `None`. With the file, `Model(db, COMPONENTS,
# "FCC_A1")` builds pycalphad's symbolic Gibbs energy of FCC; `fcc.GM` is the
# energy per mole of atoms as a formula, and `evaluate(fcc, fcc.GM, T, 1.0)`
# puts in the numbers (temperature, 101325 Pa, x(Ni) = 1 for pure Ni) and
# returns a float. `g_bulk` is a dictionary {temperature in K: g in J/mol}.
# `{... for t in (...)}` builds such a dictionary in one line. The loop prints a
# table and skips 500 K with `continue`, because that row is your exercise.

# %%
import json

SAVED = json.loads((ROOT / "course" / "materials" / "boundaries" / "ni_twin_results.json").read_text())  # course run
DOWNLOAD = False   # True: fetch CuNi-92Mey-LB.tdb into your session (6,789 bytes, checked)
tdb = database("cuni", download=DOWNLOAD)  # path to the checked file, or None
if tdb is not None:
    from pycalphad import Model
    from course.materials.cuni.worked_example import COMPONENTS, evaluate, load_source
    fcc = Model(load_source(tdb), COMPONENTS, "FCC_A1")  # symbolic FCC Gibbs energy
    g_bulk = {t: evaluate(fcc, fcc.GM, t, 1.0) for t in (300.0, 500.0, 800.0)}   # pure Ni: x_Ni = 1
    print("Bulk g from the database (pycalphad).")
else:
    g_bulk = {row["T_K"]: row["bulk_g_J_per_mol_NI"] for row in SAVED["energy_checks"]}  # {K: J/mol}
    print("No-database mode: bulk g from the saved course run.")

print(" T (K)   g_FCC (J/mol)   γ fit (J/m²)   ε (J/mol sites)   G_cell (J)       G_cell − g (J)")
for t, g in g_bulk.items():
    if t == 500.0:
        continue   # 500 K is your turn below
    epsilon = gamma_fit(t) / rho                # J/mol boundary sites
    G_cell = n_b * g + n_s * (g + epsilon)      # J, whole cell of one mole of Ni
    print(f" {t:5.0f}   {g:12.4f}    {gamma_fit(t):.6f}       {epsilon:9.4f}       {G_cell:12.4f}    {G_cell - g:8.5f}")

# %% [markdown]
# ### Your turn
#
# The table leaves out 500 K. At 500 K: the fitted γ, the offset ε in J/mol sites
# and the boundary's total
# contribution $A_{GB}\gamma$ in J (one mole of Ni). Then set γ to zero: by how
# much does $G_{\rm cell}$ differ from $g^{\rm Ni}_{\rm FCC}$? Give the numbers to
# 4 significant figures. Finally: does the
# exact recovery of $A_{GB}\gamma$ show that the simulation or this construction
# is right?

# %%
gamma_500 = None          # J/m²
epsilon_500 = None        # J/mol boundary sites
excess_500 = None         # J for one mole of Ni
excess_zero_offset = None # J
recovery_validates = None # True or False
check(gamma_500, "task03_gamma_500")
check(epsilon_500, "task03_epsilon_500")
check(excess_500, "task03_excess_500")
check(excess_zero_offset, "task03_excess_zero")
check(recovery_validates, "task03_validates")

# %% [markdown]
# ## 5. After your attempt: the course code and the pictures
#
# The course module `ni_twin` does the same fit (with `numpy.linalg.lstsq`), the
# same geometry and the same accounting. Its saved results are checked here at
# the packet's tolerances: 1e-8 J/m² for energies per area, 1e-7 J (or J/mol
# sites) for energies, 1e-10 mol for amounts.
#
# The cell first checks that the readings file is the one the course run used
# (by its SHA-256 fingerprint), then compares the fit, the geometry and the
# energies with the module and the saved run, and finally draws the readings
# with the fitted line (left) and the residuals in mJ/m² (right). In the right
# panel, the dotted lines mark the ±1 mJ/m² reading precision: residuals inside
# that band are as small as the readings allow.

# %% cellView="form"
#@title After your attempt: compare with the course module and the saved run
import hashlib
from course.materials.boundaries import ni_twin
import matplotlib.pyplot as plt

# SHA-256 fingerprint of the readings file must equal the one stored with the course run
if hashlib.sha256(CURVE.read_bytes()).hexdigest() != SAVED["curve_csv_sha256"]:
    raise AssertionError("The readings file differs from the one used by the saved course run.")
print("✓ The shipped readings are the ones used by the saved course run (SHA-256 match).")
module_T, module_gamma = ni_twin.read_curve()
fit = ni_twin.fit_curve(module_T, module_gamma)  # dict with A, B, residuals, sum of squares
confirm(fit["A_J_per_m2"], SAVED["fit"]["A_J_per_m2"], "A (module)", tol=1e-8)
confirm(intercept, SAVED["fit"]["A_J_per_m2"], "A (closed form above)", tol=1e-8)
confirm(slope * 800, SAVED["fit"]["B_J_per_m2_K"] * 800, "B × 800 K (closed form above)", tol=1e-8)
confirm(fit["max_absolute_residual_J_per_m2"], SAVED["fit"]["max_absolute_residual_J_per_m2"], "Largest residual", tol=1e-8)
confirm(fit["sse_J2_per_m4"], 1.025e-7, "Residual sum of squares (packet answer)", tol=1e-12)
confirm(intercept, 0.067525, "A (packet answer)", tol=1e-8)
confirm(-slope * 1000, 0.02025, "−B in mJ/(m² K) (packet answer)", tol=1e-8)
print(" T (K)   reading    fit        fit − reading (mJ/m²)")
for t, g, r, saved in zip(T, gamma, residuals, SAVED["fit"]["residual_J_per_m2"]):
    print(f" {t:5.0f}   {g:.4f}     {gamma_fit(t):.6f}   {1000 * r:+.3f}")
    confirm(r, saved, f"Residual at {t:.0f} K", tol=1e-8)

geom = ni_twin.geometry(ni_twin.LATTICE_PARAMETER_M, ni_twin.GRAIN_SIZE_M)  # the module's V_m, A_GB, ρ, n_s, n_b
saved_geom = SAVED["geometry"]
# relative tolerances: 1e-12 times the value itself
confirm(V_m, saved_geom["molar_volume_m3_per_mol"], "V_m (12 significant digits)", tol=1e-12 * V_m)
confirm(A_GB, saved_geom["area_m2_for_one_mol_NI"], "A_GB (12 significant digits)", tol=1e-12 * A_GB)
confirm(rho, saved_geom["site_density_mol_per_m2"], "ρ (12 significant digits)", tol=1e-12 * rho)
confirm(n_s, saved_geom["boundary_NI_mol"], "Boundary Ni n_s", tol=1e-10)
confirm(geom["bulk_NI_mol"], saved_geom["bulk_NI_mol"], "Bulk Ni n_b (module)", tol=1e-10)
confirm(n_s + n_b, 1.0, "Ni balance n_s + n_b", tol=1e-10)
confirm(n_s, 2 * np.sqrt(3) * a / d, "n_s = 2√3 a/d (short form)", tol=1e-10)  # N_Av cancels in ρ·A_GB

for row in SAVED["energy_checks"]:  # 300, 500 and 800 K
    t = row["T_K"]
    energy = ni_twin.cell_energy(g_bulk[t], gamma_fit(t), geom)  # ε, g_s, G_cell and the excess
    if tdb is not None:
        confirm(g_bulk[t], row["bulk_g_J_per_mol_NI"], f"Bulk g from the database at {t:.0f} K", tol=1e-7)
    confirm(energy["epsilon_J_per_mol_sites"], row["epsilon_J_per_mol_sites"], f"ε at {t:.0f} K", tol=1e-7)
    confirm(energy["epsilon_J_per_mol_sites"] * rho, gamma_fit(t), f"ε·ρ back to γ at {t:.0f} K", tol=1e-8)
    confirm(energy["excess_total_J"], A_GB * gamma_fit(t), f"G_cell − g = A_GB γ at {t:.0f} K", tol=1e-7)
    confirm(energy["excess_total_J"], row["excess_total_J"], f"Saved excess at {t:.0f} K", tol=1e-7)
    confirm(ni_twin.cell_energy(g_bulk[t], 0.0, geom)["cell_G_J"], g_bulk[t], f"Zero offset at {t:.0f} K", tol=1e-7)

grid = np.linspace(100, 800, 101)  # K, 101 temperatures for drawing the line
fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2))
# error bars of ±precision show the reading precision, not a simulation uncertainty
left.errorbar(T, gamma, yerr=precision, fmt="o", capsize=3, label="readings (±0.001 J/m² reading precision)")
left.plot(grid, gamma_fit(grid), "-", label=f"fit: {intercept:.6f} {slope:+.3e}·T")
left.set(xlabel="temperature T (K)", ylabel="formation energy γ (J/m²)",
         title="Ni coherent Σ3 {111} twin, Fischer et al. 2019 Fig. 3")
left.legend(fontsize=9)
right.axhline(0, color="grey", lw=0.8)
for edge in (-1, 1):
    right.axhline(edge * precision * 1000, color="grey", ls=":", lw=1)  # ±1 mJ/m²
right.plot(T, (gamma_fit(T) - gamma) * 1000, "s-", label="fit − reading")  # J/m² → mJ/m²
right.set(xlabel="temperature T (K)", ylabel="residual (mJ/m²)",
          title="Residuals; dotted: ±1 mJ/m² reading precision")
right.legend(fontsize=9)
fig.tight_layout()
plt.show()
print(f"V_m = {V_m:.9e} m³/mol, A_GB = {A_GB:.7f} m², ρ = {rho:.9e} mol/m², n_s = {n_s:.11f}, n_b = {n_b:.11f} mol")
print(f"Wrong counts: six unshared faces → {2 * A_GB:.7f} m²; bulk 1 mol plus boundary → {1 + n_s:.11f} mol Ni")
print(" T (K)   γ fit (J/m²)   ε (J/mol sites)   A_GB γ (J per mol Ni)")
for t in (300.0, 500.0, 800.0):
    print(f" {t:5.0f}   {gamma_fit(t):.6f}       {gamma_fit(t) / rho:.7f}       {A_GB * gamma_fit(t):.8f}")

# %% [markdown]
# Full answers: [Task 03 answers](../course/materials/boundaries/ni_twin_answers.md).
# For a simpler counting exercise see Day 2 D4 ([worksheet](../course/primer_day2/worksheet.md)).
#
# ## 6. Limits
#
# The readings are taken by eye from a plotted simulation curve, so they are
# approximate and not independent; the fit only describes them between 100 and
# 800 K. The lattice parameter, grain shape and two-plane site count are chosen
# for teaching, not taken from the paper. Giving the boundary sites the bulk
# CALPHAD energy plus an offset is a construction: the exact recovery of
# $A_{GB}\gamma$ checks the bookkeeping, not the simulation, the bulk database or
# any physical boundary model. The boundary area is fixed by the chosen
# geometry, so nothing here decides whether boundaries grow or shrink.
# Next: [Task 04 · Cu–Ni segregation to an invented boundary](task04_cuni_segregation.ipynb).
