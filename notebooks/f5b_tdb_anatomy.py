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
# # f5b · How a TDB file is built
#
# **Learning question:** what do the lines of a thermodynamic database (TDB)
# file mean, and can you evaluate them by hand to the same number that
# pycalphad gets?
#
# Used in: self-study step 05 (optional, before Task 01) and step 06.
#
# **In plain words.** A published CALPHAD assessment ends as a text file: a few
# dozen lines with Gibbs energy expressions for every phase. This notebook
# writes a small file of that kind, reads it line by line, evaluates its
# numbers by hand and lets pycalphad confirm them. The same line types appear in
# the published databases of the tasks and in the textbooks (Lukas, Fries and
# Sundman, *Computational Thermodynamics*, 2007; Saunders and Miodownik,
# *CALPHAD*, 1998).
#
# **Learning goals.** After this notebook you can
#
# 1. say what the keywords ELEMENT, FUNCTION, TYPE_DEFINITION, PHASE,
#    CONSTITUENT and PARAMETER do, and read temperature ranges with their Y/N
#    flags;
# 2. evaluate a pure-element Gibbs energy in the right temperature range;
# 3. evaluate a Redlich–Kister excess term and the whole molar Gibbs energy of a
#    solution;
# 4. tell site fractions from mole fractions, and moles of formula units from
#    moles of atoms;
# 5. connect the Ω of the course's regular solution to the parameter L0;
# 6. (optional) list the kinds of lines in a published database.
#
# | Section | What | Track | Time |
# |---|---|---|---|
# | 1 | Read the file line by line | main | 20 min |
# | 2 | A pure element by hand | main | 15 min |
# | 3 | The Redlich–Kister excess | main | 15 min |
# | 4 | Site fractions and the amount basis | main | 15 min |
# | 5 | Ω is L0; what L1 adds | main | 10 min |
# | 6 | The magnetic pair TC and BMAGN | dive deeper | 15 min |
# | 7 | A published database | optional | 10 min |
# | 8 | Limits | both | 3 min |
#
# **Invented and published.** Sections 1–6 use an **invented** database for
# two invented elements called A and B. Every number in it is made up for
# teaching; it describes no real system. pycalphad does not look element names
# up in the periodic table, so B here is not boron. Section 7 reads the
# published Cu–Ni database of Task 01, if you have it; the rest of the notebook
# runs without it.
#
# **Coming from materials.** You know the regular solution
# $g=(1-x)g_A+xg_B+RT[x\ln x+(1-x)\ln(1-x)]+\Omega x(1-x)$. A TDB file is the
# same idea written down for a program, with more terms.
#
# **Coming from operations research.** A TDB file is the data file of the
# objective function: it defines $g(T,y)$ for every phase. The equilibrium
# solver of the later steps only minimises what these lines define.
#
# **How to work.** Run the cells from top to bottom. In each "Your turn" cell,
# replace `None` with your value and run it: `check(value, key)` says whether
# you match, without showing the answer. Cells marked *After your attempt* hold
# worked solutions; `confirm(value, expected, "what", tol=...)` there stops
# with an error if a calculation does not reproduce the lesson value.

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
# ## 1. Read the file line by line (main track, 20 min)
#
# Here is the whole invented database, as a Python string. A real file looks
# the same, only longer. Read it once before the explanations below.

# %%
TDB = """
$ Invented teaching database: elements A and B. All numbers are invented.
$ Lines starting with $ are comments.

ELEMENT /-   ELECTRON_GAS   0.0       0.0      0.0 !
ELEMENT VA   VACUUM         0.0       0.0      0.0 !
ELEMENT A    FCC_A1        50.0    5000.0     30.0 !
ELEMENT B    FCC_A1        60.0    5500.0     32.0 !

FUNCTION GHSERA  298.15  -7000+118*T-24*T*LN(T)-0.0035*T**2+60000*T**(-1);  900  Y
                         -10331.667+166.24269*T-31*T*LN(T);                3000  N !
FUNCTION GHSERB  298.15  -8000+130*T-26*T*LN(T)-0.002*T**2;                3000  N !

TYPE_DEFINITION % SEQ * !

PHASE LIQUID  %  1  1.0 !
CONSTITUENT LIQUID  :A,B : !
PARAMETER G(LIQUID,A;0)     298.15  GHSERA+12000-10*T;  3000  N !
PARAMETER G(LIQUID,B;0)     298.15  GHSERB+15000-10*T;  3000  N !
PARAMETER L(LIQUID,A,B;0)   298.15  -5000;              3000  N !

PHASE FCC_A1  %  2  1  1 !
CONSTITUENT FCC_A1  :A,B : VA : !
PARAMETER G(FCC_A1,A:VA;0)    298.15  GHSERA;        3000  N !
PARAMETER G(FCC_A1,B:VA;0)    298.15  GHSERB;        3000  N !
PARAMETER L(FCC_A1,A,B:VA;0)  298.15  15000-5*T;     3000  N !
PARAMETER L(FCC_A1,A,B:VA;1)  298.15  -4000+2*T;     3000  N !

PHASE BCC_A2  %  2  1  3 !
CONSTITUENT BCC_A2  :A,B : VA : !
PARAMETER G(BCC_A2,A:VA;0)    298.15  GHSERA+4000-1.5*T;  3000  N !
PARAMETER G(BCC_A2,B:VA;0)    298.15  GHSERB+3000-1*T;    3000  N !

PHASE A3B  %  2  3  1 !
CONSTITUENT A3B  :A : B : !
PARAMETER G(A3B,A:B;0)  298.15  3*GHSERA+GHSERB-30000+6*T;  3000  N !
"""

# %% [markdown]
# **The grammar.** Every statement ends with `!`; it may run over several
# lines. Lines starting with `$` are comments. Upper and lower case mean the
# same.
#
# **ELEMENT** `name  reference-phase  mass  H298−H0  S298`. The reference
# phase is the element's stable state at 298.15 K and 1 bar; the next three
# fields are the molar mass (g/mol), the enthalpy difference $H_{298}-H_0$
# (J/mol) and the entropy $S_{298}$ (J/(mol K)). The last three are
# information only: pycalphad does not use them to compute Gibbs energies. `VA`
# (vacancy, an empty site) and `/-` (the electron, for charged species) appear
# in almost every file.
#
# **FUNCTION** `name  T_low  expression;  T_high  Y  expression;  T_high  N !`
# gives a name to an expression in temperature. Each range is a lower limit,
# an expression ending in `;`, and an upper limit. `Y` means "another range
# follows, starting where this one ends"; `N` means "this was the last range"
# (a reference code may follow the `N`). So `GHSERA` is the first expression
# for 298.15 K ≤ T < 900 K and the second for 900 K ≤ T ≤ 3000 K. In the
# expressions `*` multiplies, `**` is a power (`T**(-1)` is 1/T) and `LN` is
# the natural logarithm. Each range has the form
# $a+bT+cT\ln T+dT^2+eT^{-1}$: the Gibbs energy that belongs to a simple heat
# capacity $C_p=-c-2dT-2eT^{-2}$.
#
# The name GHSER means "G relative to the stable element reference" (SER): the
# enthalpy of every element in its reference phase at 298.15 K and 1 bar is set
# to zero. Only differences of Gibbs energy can be measured, so every database
# fixes such a zero; all numbers below are $G-\sum_i b_i H_i^{\rm SER}$ in J,
# with $b_i$ the moles of element $i$.
#
# **TYPE_DEFINITION** defines a one-character label that PHASE lines can
# carry. `% SEQ *` is the plain label most files give every phase; it adds
# nothing to the model. Other type definitions attach extra model parts, such
# as the magnetic term of section 6.
#
# **PHASE** `name  type-labels  number-of-sublattices  site-ratios !`.
# `PHASE FCC_A1 % 2 1 1` has two sublattices with one site each per formula
# unit. FCC_A1 holds the metal atoms on the first sublattice and the
# interstitial sites (octahedral holes) on the second. In this file the second
# holds only vacancies; real databases keep it so that C or N can be added
# later. BCC_A2 is written with three interstitial sites per metal site, as in
# most published databases.
#
# **CONSTITUENT** lists what may sit on each sublattice, sublattices separated
# by `:`. `:A,B : VA :` means A or B on the first, only vacancies on the second.
#
# **PARAMETER** `type(phase, constituent-array; degree)  T_low  expression;  T_high  N !`
#
# - `G(FCC_A1,A:VA;0)` is the Gibbs energy of the *endmember* A:VA, the
#   compound with A on every first-sublattice site and a vacancy on every
#   second-sublattice site. A colon separates sublattices.
# - `L(FCC_A1,A,B:VA;0)` is an *interaction parameter*: a comma joins
#   constituents that mix on one sublattice. The number after `;` is the
#   Redlich–Kister degree (0, 1, 2, ...).
# - The expressions may use the FUNCTION names, here `GHSERA` and `GHSERB`.
#
# **The amount basis.** Every G and L value is in **J per mole of formula
# units**, as set by the site ratios of the PHASE line, measured from SER. A
# formula unit of FCC_A1 here is $(A,B)_1(\mathrm{Va})_1$, which holds one atom;
# a formula unit of A3B is $A_3B_1$, which holds four. Section 4 turns this into
# J/mol of atoms.
#
# The next cell lets pycalphad read the string and prints what it found.
# `Database(TDB)` reads the text; `db.phases[name].sublattices` holds the site
# ratios and `db.search(...)` lists the parameters (a query on the stored
# fields; `Q.phase_name.exists()` matches all of them).

# %%
import numpy as np
import matplotlib.pyplot as plt
from pycalphad import Database, calculate, variables as v
from tinydb import Query

db = Database(TDB)
Q = Query()
COMPS = ["A", "B", "VA"]
LINE_C, ALT_C, REF_C, BAD_C = "#2445c4", "#cf4418", "#8f6400", "#b58900"   # the website's colours


def name_of(p):
    """A parameter as it would be written in a TDB file, e.g. L(FCC_A1,A,B:VA;1)."""
    array = ":".join(",".join(s.name for s in subl) for subl in p["constituent_array"])
    return f"{p['parameter_type']}({p['phase_name']},{array};{p['parameter_order']})"


print("elements:", sorted(db.elements))
print("functions:", sorted(k for k in db.symbols if k.startswith("GHSER")))
for name, phase in db.phases.items():
    constituents = " : ".join(",".join(sorted(s.name for s in subl)) for subl in phase.constituents)
    print(f"{name:7s} site ratios {phase.sublattices}   constituents {constituents}")
print()
for p in db.search(Q.phase_name.exists()):
    print(name_of(p))

# %% [markdown]
# ### Your turn: read a melting point
#
# Pure A melts where the liquid and the FCC phase of pure A have the same Gibbs
# energy. Subtract `G(FCC_A1,A:VA;0)` from `G(LIQUID,A;0)`: the function
# `GHSERA` cancels. At which temperature (K) is the difference zero?

# %%
T_melt_A = None   # K
check(T_melt_A, "f5b_t_melt_a")

# %% [markdown]
# *After your attempt.* $G^{\rm liq}_A-G^{\rm fcc}_A=12000-10T$ J/mol, zero at
# 12000/10 K. pycalphad confirms it. `calculate(db, components, phase, T=..., P=...,
# points=...)` evaluates one phase at the site fractions you give in `points`
# (one entry per constituent, sublattice by sublattice, in alphabetical order:
# for FCC_A1 that is $y_A, y_B, y_{\rm Va}$). It returns the molar Gibbs
# energy `GM`, in J per mole of atoms.

# %%
def gm(phase, y, T, output="GM"):
    """pycalphad's molar Gibbs energy of one phase at site fractions y and T (K), P = 101325 Pa."""
    r = calculate(db, COMPS, phase, T=T, P=101325, N=1, points=np.array([y]), output=output)
    return float(r[output].values.squeeze())


T_m = 12000 / 10
d_melt = gm("LIQUID", [1, 0], T_m) - gm("FCC_A1", [1, 0, 1], T_m)
print(f"melting point of A: {T_m:.0f} K;  G(liquid A) - G(fcc A) there: {d_melt:.6f} J/mol")
confirm(d_melt, 0.0, "Liquid and FCC A equal at the melting point", tol=1e-6)

# %% [markdown]
# ## 2. A pure element by hand (main track, 15 min)
#
# All energies below are at T = 1000 K and P = 101325 Pa (the invented file
# has no pressure terms, so P does not matter here).
#
# ### Your turn: G of pure FCC A at 1000 K
#
# Evaluate `G(FCC_A1,A:VA;0)` at 1000 K, in J/mol, to 0.05 J/mol. Pick the
# range of `GHSERA` whose limits enclose 1000 K. In a scratch cell:
# `import math`, `T = 1000.0`, then type the expression with `math.log(T)` for
# `LN(T)`.

# %%
T = 1000.0        # K
R = 8.3145        # J/(mol K), the value pycalphad uses
g_fcc_A = None    # J/mol (per formula unit of (A)1(Va)1, which is one mole of atoms)
check(g_fcc_A, "f5b_g_fcc_a_1000")

# %% [markdown]
# *After your attempt.* 1000 K lies in the second range (900 K ≤ T ≤ 3000 K).
# The cell writes both ranges as Python functions and compares with pycalphad.
# It also shows how little the first range would differ: the two ranges were
# joined so that G and its slope $-S$ agree at 900 K, so the wrong range gives
# a close but wrong number. That is why the check above asks for 0.05 J/mol.

# %%
def ghsera_low(T):   # 298.15 K <= T < 900 K
    return -7000 + 118*T - 24*T*np.log(T) - 0.0035*T**2 + 60000/T

def ghsera_high(T):  # 900 K <= T <= 3000 K
    return -10331.667 + 166.24269*T - 31*T*np.log(T)

def ghsera(T):
    return ghsera_low(T) if T < 900 else ghsera_high(T)

def ghserb(T):       # 298.15 K <= T <= 3000 K
    return -8000 + 130*T - 26*T*np.log(T) - 0.002*T**2


G_A, G_B = ghsera(T), ghserb(T)
print(f"by hand:   G(FCC_A1,A:VA) = {G_A:.4f} J/mol,  G(FCC_A1,B:VA) = {G_B:.4f} J/mol")
print(f"pycalphad: G(FCC_A1,A:VA) = {gm('FCC_A1', [1, 0, 1], T):.4f} J/mol,  "
      f"G(FCC_A1,B:VA) = {gm('FCC_A1', [0, 1, 1], T):.4f} J/mol")
print(f"wrong range (the first one) at 1000 K: {ghsera_low(T):.4f} J/mol, "
      f"off by {ghsera_low(T) - G_A:+.3f} J/mol")
step = ghsera_high(900.0) - ghsera_low(900.0)
slope = (ghsera_high(900.001) - ghsera_high(899.999) - ghsera_low(900.001) + ghsera_low(899.999)) / 0.002
print(f"at 900 K the ranges differ by {step:+.5f} J/mol in G and {slope:+.5f} J/(mol K) in dG/dT")
confirm(float(v.R), R, "pycalphad's gas constant R", tol=1e-12)
confirm(gm("FCC_A1", [1, 0, 1], T), G_A, "pycalphad's G of pure FCC A at 1000 K", tol=1e-6)
confirm(gm("FCC_A1", [0, 1, 1], T), G_B, "pycalphad's G of pure FCC B at 1000 K", tol=1e-6)

# %% [markdown]
# Check the joint yourself: it is the first thing to look at when a database
# behaves oddly near a temperature limit. A jump in G at a range limit is an
# error in the file; a jump in $C_p$ is common and usually harmless.

# %% [markdown]
# ## 3. The Redlich–Kister excess (main track, 15 min)
#
# For one sublattice with A and B mixing (the second holds only vacancies), the
# molar Gibbs energy of FCC_A1 is
#
# $$G_m = y_A\,G_{A:Va} + y_B\,G_{B:Va} + RT\,(y_A\ln y_A + y_B\ln y_B) + G^{\rm ex},$$
#
# $$G^{\rm ex} = y_A\,y_B\,\big[L_0 + L_1\,(y_A-y_B) + L_2\,(y_A-y_B)^2 + \dots\big].$$
#
# The three parts are the reference line (straight in $y$), ideal mixing and
# the excess. Here the vacancy sublattice is full of vacancies, so the site
# fractions on the first sublattice equal the mole fractions: $y_A=x_A$,
# $y_B=x_B$.
#
# **Sign convention.** The factor is $(y_A-y_B)$ with A the *first* constituent
# of the parameter, so the sign of the odd terms ($L_1$, $L_3$) depends on the
# order. pycalphad sorts the constituents of every parameter alphabetically
# when it reads a file (the cell after the next turn shows it). A paper that
# writes the B–A order, with $(x_B-x_A)$, needs the sign of its odd terms
# changed when you type it into a file written A,B.
#
# ### Your turn: the excess and the whole G at x_B = 0.3
#
# At 1000 K, with $x_B=0.3$: first evaluate $L_0$ and $L_1$ from their lines,
# then $G^{\rm ex}$, then $G_m$ (use your $G_A$ and $G_B$ from section 2 and
# R = 8.3145 J/(mol K)).

# %%
x_B = 0.3
G_ex_03 = None   # J/mol of atoms
G_m_03 = None    # J/mol of atoms
check(G_ex_03, "f5b_gex_03")
check(G_m_03, "f5b_gm_03")

# %% [markdown]
# *After your attempt.* By hand, then pycalphad's $G_m$ minus the reference
# line minus ideal mixing: what is left is the excess.

# %%
x_A = 1 - x_B
L0, L1 = 15000 - 5*T, -4000 + 2*T
excess = x_A * x_B * (L0 + L1 * (x_A - x_B))
ideal = R * T * (x_A * np.log(x_A) + x_B * np.log(x_B))
reference = x_A * G_A + x_B * G_B
G_m_hand = reference + ideal + excess
G_m_pyc = gm("FCC_A1", [x_A, x_B, 1], T)
print(f"L0 = {L0:.0f} J/mol, L1 = {L1:.0f} J/mol")
print(f"reference line {reference:.4f}, ideal mixing {ideal:.4f}, excess {excess:.4f} J/mol")
print(f"G_m by hand {G_m_hand:.4f} J/mol,  pycalphad {G_m_pyc:.4f} J/mol")
print(f"pycalphad G_m - reference - ideal = {G_m_pyc - reference - ideal:.4f} J/mol")
confirm(G_m_pyc - reference - ideal, excess, "The excess left in pycalphad's G_m", tol=1e-6)

# %% [markdown]
# Now the order of the constituents. The next cell writes the $L_1$ line once
# as `L(FCC_A1,B,A:VA;1)` and reads the file again. If the program kept the
# written order, the factor would become $(y_B-y_A)$ and the excess would
# change; pycalphad sorts the names, so it does not.

# %%
db_swapped = Database(TDB.replace("L(FCC_A1,A,B:VA;1)", "L(FCC_A1,B,A:VA;1)"))
r = calculate(db_swapped, COMPS, "FCC_A1", T=T, P=101325, N=1, points=np.array([[x_A, x_B, 1]]))
excess_swapped = float(r.GM.values.squeeze()) - reference - ideal
print(f"written B,A: pycalphad excess {excess_swapped:.4f} J/mol")
print(f"with (y_B - y_A) it would be  {x_A * x_B * (L0 + L1 * (x_B - x_A)):.4f} J/mol")
confirm(excess_swapped, excess, "pycalphad reads B,A as A,B", tol=1e-6)

# %% [markdown]
# So in a file read by pycalphad, `L(...;1)` always multiplies
# $(y_{\rm first}-y_{\rm second})$ with the two names in alphabetical order.
# For Cu–Ni that is $(y_{\rm Cu}-y_{\rm Ni})$. When you copy an odd-order
# parameter from a paper, check which order the paper's formula uses.

# %% [markdown]
# ## 4. Site fractions and the amount basis (main track, 15 min)
#
# A *site fraction* $y$ is the fraction of one sublattice's sites taken by one
# constituent; a *mole fraction* $x$ counts atoms over the whole formula unit.
# Vacancies take sites but are not atoms. The moles of atoms in one formula
# unit are
#
# $$n_{\rm atoms} = \sum_s a_s\,(1 - y_{{\rm Va},s}),$$
#
# with $a_s$ the site ratio of sublattice $s$. pycalphad's `GM` divides the
# energy of one formula unit by $n_{\rm atoms}$, so `GM` is in J per mole of
# atoms. `output="G"` returns the energy per mole of formula units instead.
#
# ### Your turn: atoms per formula unit
#
# BCC_A2 is written `(A,B)1(Va)3`: four sites per formula unit. How many moles
# of atoms are in one mole of its formula units? Then: what is the molar Gibbs
# energy of A3B at 1000 K in **J per mole of atoms**?

# %%
atoms_bcc = None   # mol atoms per mol formula units
G_A3B_atoms = None   # J/mol of atoms, A3B at 1000 K
check(atoms_bcc, "f5b_atoms_bcc")
check(G_A3B_atoms, "f5b_g_a3b_atoms")

# %% [markdown]
# *After your attempt.* The three vacancy sites hold no atoms: one atom per
# formula unit, so for FCC_A1 and BCC_A2 the per-formula-unit and per-atom
# numbers are the same. A3B holds four atoms per formula unit: its parameter
# is per $A_3B_1$, and `GM` is a quarter of it. The cell compares pycalphad's
# `G` (per formula unit) with `GM` (per mole of atoms) for all three.

# %%
cases = [("FCC_A1", [x_A, x_B, 1]), ("BCC_A2", [x_A, x_B, 1]), ("A3B", [1, 1])]
for phase, y in cases:
    G_fu, G_at = gm(phase, y, T, "G"), gm(phase, y, T)
    print(f"{phase:7s} G {G_fu:12.4f} J/mol formula units   GM {G_at:11.4f} J/mol atoms   ratio {G_fu / G_at:.3f}")
G_A3B_hand = (3 * G_A + G_B - 30000 + 6 * T) / 4
G_bcc_hand = (x_A * (G_A + 4000 - 1.5*T) + x_B * (G_B + 3000 - 1*T) + ideal)  # 3 R T (1 ln 1) = 0 on the vacancy sites
print(f"A3B by hand: {G_A3B_hand:.4f} J/mol atoms;  BCC_A2 at x_B = 0.3 by hand: {G_bcc_hand:.4f} J/mol atoms")
confirm(gm("A3B", [1, 1], T), G_A3B_hand, "GM of A3B per mole of atoms", tol=1e-6)
confirm(gm("BCC_A2", [x_A, x_B, 1], T), G_bcc_hand, "GM of BCC_A2 with three vacancy sites", tol=1e-6)
confirm(gm("A3B", [1, 1], T, "G") / gm("A3B", [1, 1], T), 4.0, "Atoms per formula unit of A3B", tol=1e-9)

# %% [markdown]
# This is the amount-basis trap of Task 05 (Ni–Nb) in small: a compound
# parameter is per formula unit, a phase diagram is per mole of atoms. Compare
# two phases only on the same basis.

# %% [markdown]
# ## 5. Ω is L0; what L1 adds (main track, 10 min)
#
# The regular solution of steps 03, 07 and 15 has the excess $\Omega\,x(1-x)$
# with Ω = 20000 J/mol. In TDB terms that is a single
# `L(PHASE,A,B;0)` = Ω and no higher terms. $L_1$ adds the factor
# $(x_A-x_B)=1-2x_B$, which is positive on the A-rich side and negative on the
# B-rich side: it tilts the bump.
#
# **Predict first.** In this file $L_1$ = −2000 J/mol at 1000 K. Is the top of
# the excess bump at $x_B$ below or above 0.5?

# %%
from course.self_study import day3_core
OMEGA = day3_core.OMEGA     # J/mol, the regular solution of step 03 part B
x = np.linspace(0, 1, 401)
ex_L0 = x * (1 - x) * L0
ex_L01 = x * (1 - x) * (L0 + L1 * (1 - 2 * x))
ex_omega = OMEGA * x * (1 - x)
pyc = calculate(db, COMPS, "FCC_A1", T=T, P=101325, N=1, points=np.column_stack([1 - x, x, np.ones_like(x)]))
with np.errstate(divide="ignore", invalid="ignore"):   # 0 ln 0 = 0 at the two ends
    mixing = R * T * np.nan_to_num(x * np.log(x) + (1 - x) * np.log(1 - x))
ex_pyc = pyc.GM.values.squeeze() - ((1 - x) * G_A + x * G_B) - mixing
print(f"Ω of step 03 part B: {OMEGA:.0f} J/mol")
print(f"top of the bump: L0 only at x_B = {x[np.argmax(ex_L0)]:.3f}; L0 + L1 at x_B = {x[np.argmax(ex_L01)]:.3f}")
print(f"largest difference between the L0 + L1 curve and pycalphad: {np.max(np.abs(ex_pyc - ex_L01)):.2e} J/mol")
confirm(OMEGA, 20000.0, "Ω of step 03 part B", tol=1e-9)
confirm(float(np.max(np.abs(ex_pyc - ex_L01))), 0.0, "The excess curve agrees with pycalphad", tol=1e-6)

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(x, ex_omega, color=REF_C, ls="--", lw=1.5, label="step 03: Ω x(1−x), Ω = 20000 J/mol")
ax.plot(x, ex_L0, color=LINE_C, lw=2, label=f"L0 only (L0 = {L0:.0f} J/mol)")
ax.plot(x, ex_L01, color=ALT_C, lw=2, label=f"L0 and L1 (L1 = {L1:.0f} J/mol)")
ax.axvline(0.5, color="0.6", lw=0.8)
ax.set_xlabel("x_B (mole fraction)"); ax.set_ylabel("G_ex (J/mol of atoms)")
ax.set_title("FCC_A1 excess at 1000 K"); ax.legend(frameon=False, fontsize=8)
plt.show()

# %% [markdown]
# ### Your turn: flip the sign of L1
#
# Keep $L_0$ = 10000 J/mol and set $L_1$ = +2000 J/mol. Compute the asymmetry
# $G^{\rm ex}(x_B=0.25)-G^{\rm ex}(x_B=0.75)$ by hand. From its sign, which sign
# of $L_1$ ("positive" or "negative") puts the top of the bump on the A-rich
# side ($x_B<0.5$)?

# %%
asymmetry_flip = None   # J/mol of atoms, G_ex(0.25) - G_ex(0.75) with L1 = +2000 J/mol
sign_L1_A_rich = None   # "positive" or "negative"
check(asymmetry_flip, "f5b_asym_flip")
check(sign_L1_A_rich, "f5b_l1_sign")

# %% [markdown]
# *After your attempt.* At $x_B=0.25$ the factor $(x_A-x_B)$ is +0.5, at
# $x_B=0.75$ it is −0.5, and $x_Ax_B$ = 0.1875 at both. So the asymmetry is
# $0.1875\,L_1$: positive for $L_1>0$, and the bump is higher on the A-rich side.

# %%
L1_flip = 2000.0
ex_flip = lambda xb: xb * (1 - xb) * (L0 + L1_flip * (1 - 2 * xb))
asym = ex_flip(0.25) - ex_flip(0.75)
x_top = x[np.argmax(ex_flip(x))]
print(f"L1 = +2000 J/mol: asymmetry {asym:.1f} J/mol, top of the bump at x_B = {x_top:.3f}")
confirm(asym, 0.1875 * L1_flip, "Asymmetry 0.1875 L1", tol=1e-9)
confirm(float(x_top < 0.5), 1.0, "The top lies on the A-rich side", tol=0)

# %% [markdown]
# In general the factor $L_0+L_1(1-2x_B)$ is larger on the side where
# $L_1(1-2x_B)>0$: a positive $L_1$ tilts the bump towards A, a negative one
# (as in this file) towards B. In real assessments $L_1$ carries the asymmetry
# of measured mixing enthalpies or of a miscibility gap; $L_2$ and higher terms
# appear less often.

# %% [markdown]
# ## 6. The magnetic pair TC and BMAGN (dive deeper, 15 min)
#
# Ferromagnetic elements (Fe, Co, Ni) carry a magnetic contribution. Databases
# give it as two parameters per phase: `TC`, the Curie temperature (K), and
# `BMAGN`, the mean magnetic moment per atom (in Bohr magnetons). The model of
# Inden, Hillert and Jarl adds
#
# $$G^{\rm mag} = RT\ln(\beta+1)\,g(\tau),\qquad \tau = T/T_C,$$
#
# with, for $\tau\le1$,
# $$g(\tau)=1-\frac1A\Big[\frac{79\,\tau^{-1}}{140\,p}+\frac{474}{497}\Big(\frac1p-1\Big)\Big(\frac{\tau^3}{6}+\frac{\tau^9}{135}+\frac{\tau^{15}}{600}\Big)\Big],$$
# for $\tau>1$,
# $$g(\tau)=-\frac1A\Big(\frac{\tau^{-5}}{10}+\frac{\tau^{-15}}{315}+\frac{\tau^{-25}}{1500}\Big),$$
# and $A=\frac{518}{1125}+\frac{11692}{15975}\big(\frac1p-1\big)$. The
# structure factor $p$ is 0.28 for FCC and HCP and 0.4 for BCC. A
# TYPE_DEFINITION line switches the model on and sets $p$; the phase then
# carries its label:
#
# `TYPE_DEFINITION & GES A_P_D FCC_A1 MAGNETIC -3.0 0.28 !` and
# `PHASE FCC_A1 %& 2 1 1 !`
#
# (−3.0 is the antiferromagnetic factor: a negative TC or BMAGN is divided by
# it.)
# The cell adds these lines and an invented magnetic pure A: TC = 800 K,
# BMAGN = 0.6.

# %%
TDB_MAG = TDB.replace("PHASE FCC_A1  %  2  1  1 !",
                      "TYPE_DEFINITION & GES A_P_D FCC_A1 MAGNETIC -3.0 0.28 !\n"
                      "PHASE FCC_A1  %&  2  1  1 !") + """
PARAMETER TC(FCC_A1,A:VA;0)     298.15  800;  3000  N !
PARAMETER BMAGN(FCC_A1,A:VA;0)  298.15  0.6;  3000  N !
"""
db_mag = Database(TDB_MAG)
print({k: v_ for k, v_ in db_mag.phases["FCC_A1"].model_hints.items()})

# %% [markdown]
# ### Your turn: the magnetic term at 600 K
#
# Evaluate $G^{\rm mag}$ of pure FCC A at 600 K with $p=0.28$ (J/mol). First
# $\tau$, then $A$, then $g(\tau)$ from the right branch.

# %%
G_mag_600 = None   # J/mol of atoms
check(G_mag_600, "f5b_gmag_600")

# %% [markdown]
# *After your attempt.* The formula in Python, and pycalphad's G of pure A with
# the magnetic lines minus without them, at four temperatures on both sides of
# TC.

# %%
def g_mag(T, Tc, beta, p=0.28):
    """Inden-Hillert-Jarl magnetic Gibbs energy, J per mole of formula units (here the same as per mole of atoms)."""
    tau, A = T / Tc, 518 / 1125 + 11692 / 15975 * (1 / p - 1)
    if tau <= 1:
        g = 1 - (79 / (140 * p * tau) + 474 / 497 * (1 / p - 1) * (tau**3 / 6 + tau**9 / 135 + tau**15 / 600)) / A
    else:
        g = -(tau**-5 / 10 + tau**-15 / 315 + tau**-25 / 1500) / A
    return R * T * np.log(beta + 1) * g


for Tk in (400.0, 600.0, 1000.0, 1200.0):
    pts = np.array([[1, 0, 1]])
    with_mag = float(calculate(db_mag, COMPS, "FCC_A1", T=Tk, P=101325, N=1, points=pts).GM.values.squeeze())
    print(f"T = {Tk:6.0f} K  tau = {Tk / 800:.3f}   by hand {g_mag(Tk, 800, 0.6):10.4f}   "
          f"pycalphad {with_mag - gm('FCC_A1', [1, 0, 1], Tk):10.4f} J/mol")
mag_600 = float(calculate(db_mag, COMPS, "FCC_A1", T=600, P=101325, N=1, points=np.array([[1, 0, 1]])).GM.values.squeeze()) \
          - gm("FCC_A1", [1, 0, 1], 600)
confirm(mag_600, g_mag(600, 800, 0.6), "The magnetic term of pure A at 600 K", tol=1e-6)

# %% [markdown]
# In a solution, TC and BMAGN mix like G: a linear average of the endmember
# values plus their own Redlich–Kister terms, `TC(FCC_A1,A,B:VA;0)` and so on.
# Section 7 shows such lines in the Cu–Ni database.

# %% [markdown]
# ## 7. A published database (optional, 10 min)
#
# The Cu–Ni database of Task 01 (S. an Mey, *Calphad* 16 (1992) 255–260, as
# adapted in B. Hallstedt, *Calphad* 89 (2025) 102833) uses the same line types.
# Set `DOWNLOAD = True` to fetch it into your session (outside the course
# folder; size and SHA-256 are checked), or skip this section. The cell reads
# your copy and lists what kinds of lines it contains; it does not copy the file
# anywhere.

# %%
DOWNLOAD = False
CUNI = database("cuni", download=DOWNLOAD)
if CUNI is None:
    print("No database: section 7 is skipped. Sections 1-6 did not need it.")
else:
    from collections import Counter
    text = "\n".join(line for line in CUNI.read_text().splitlines() if not line.lstrip().startswith("$"))
    statements = [" ".join(s.split()) for s in text.split("!") if s.strip()]
    print("statements by keyword:", dict(Counter(s.split()[0].upper() for s in statements)))
    cuni = Database(CUNI)
    print("FUNCTION names:", ", ".join(sorted(k for k in cuni.symbols)))
    for name, phase in cuni.phases.items():
        print(f"{name:7s} site ratios {phase.sublattices}")
    params = cuni.search(Q.phase_name.exists())
    print("parameters by type:", dict(Counter(p["parameter_type"] for p in params)))
    print("FCC_A1 interaction and magnetic parameters:")
    for p in params:
        if p["phase_name"] == "FCC_A1" and p["parameter_type"] in ("L", "TC", "BMAGN"):
            print("  ", name_of(p))

# %% [markdown]
# What to look for:
#
# - Keywords may be shortened and written with `-` for `_`: `PAR` is
#   PARAMETER, `CONST` is CONSTITUENT, `TYPE-DEF` is TYPE_DEFINITION.
# - FUNCTION lines hold the pure-element functions (GHSERCU, GHSERNI and the
#   liquid and BCC forms) and a few helpers such as R or ZERO.
# - BCC_A2 has three interstitial sites per metal site and HCP_A3 half a site:
#   still one atom per formula unit, as in section 4.
# - Per phase, G lines for the endmembers and L lines of degree 0 and 1; for
#   the magnetic FCC phase, TC and BMAGN of Ni (BMAGN is written BM in that file)
#   plus their own interaction terms.
# - `TEMP-LIM`, `DEFINE-SYSTEM-DEFAULT`, `DEFAULT-COM`, `ASSESSED_SYSTEM` and
#   the reference list set defaults and notes for other programs; pycalphad reads
#   past them, and they do not change the expressions.
#
# In Task 01 you evaluate one of the G lines by hand, as in section 2.

# %% [markdown]
# ## 8. Limits
#
# - The database of sections 1–6 is invented. It shows the format and the
#   arithmetic, not any real alloy.
# - Only substitutional solutions with Redlich–Kister terms, a fixed-composition
#   compound and the magnetic model appear. Ordered phases with mixing on two
#   sublattices, reciprocal parameters, ionic liquids and pressure terms use the
#   same file format with more lines.
# - Outside the temperature limits of a line, pycalphad 0.11.2 carries the
#   lowest range on below its lower limit and the highest range on above its
#   upper limit, without a warning (the cell below shows pure A at 200 K and
#   3500 K). The data were fitted only inside the limits; look at them before
#   you trust a number.
# - In the TDB convention the written order sets the sign of odd-order terms:
#   L(…,B,A;1) means $(y_B-y_A)$, so it equals −L(…,A,B;1). pycalphad 0.11.2
#   sorts the names first and does not flip the sign, so a file with a
#   non-alphabetical odd-order line gives a different model in pycalphad.
#   Write odd-order parameters in alphabetical order and every program agrees.
# - Evaluating lines by hand checks that you read the file as the program
#   does; it says nothing about whether the assessment is right.

# %%
for Tk, expression, where in ((200.0, ghsera_low, "below 298.15 K, first range"), (3500.0, ghsera_high, "above 3000 K, last range")):
    print(f"pure FCC A at {Tk:.0f} K ({where}): pycalphad {gm('FCC_A1', [1, 0, 1], Tk):.1f} J/mol, "
          f"that range's expression {expression(Tk):.1f} J/mol")
    confirm(gm("FCC_A1", [1, 0, 1], Tk), expression(Tk), f"pycalphad extends the range to {Tk:.0f} K", tol=1e-6)
