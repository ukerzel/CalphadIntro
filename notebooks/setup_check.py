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
# # Setup check
#
# Run this notebook **before the course** (and instructors: the day before). It
# checks that Python, the course code, pycalphad and plotting work, and tells you
# which parts of the course you are ready for. Nothing here is graded.
#
# - **On your own computer:** from the course folder run `poetry install --with dev`,
#   then `poetry run jupyter lab`, and open `notebooks/setup_check.ipynb`.
# - **In Colab:** use the "Open in Colab" link; the first cell installs what it needs
#   (a few minutes the first time) and then restarts the session, which Colab reports
#   as a crash. That is expected: run the first cell again, then the rest.
#
# Run the cells from top to bottom (in Jupyter: *Run → Run All Cells*).

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
# ## 1. The course code
#
# The first steps use an invented component A with two phases. The course code
# gives each phase's molar Gibbs energy in J/mol; at 900 K the solid has
# g = 1000 − 10·900 = −8000 J/mol (Day 1, W4).

# %%
from course.foundations import one_component_manual as unary

g_solid, g_liquid = unary.gibbs(900.0)
print(f"g_SOLID(900 K) = {g_solid:.0f} J/mol, g_LIQUID(900 K) = {g_liquid:.0f} J/mol")
confirm(g_solid, -8000.0, "Solid Gibbs energy at 900 K", tol=1e-9)
ready = {"course code": True}

# %% [markdown]
# ## 2. pycalphad with the course's own invented database
#
# The same model is stored as a small database file in the course folder.
# pycalphad finds the equilibrium at 1100 K: all liquid, with g = −10600 J/mol.
# The first pycalphad call takes a few seconds.

# %%
from course.foundations import one_component_tools as unary_pycalphad

result = unary_pycalphad.equilibrium_at(1100.0)
print(f"At 1100 K pycalphad finds {result['fractions']} with GM = {result['GM']:.1f} J/mol")
confirm(result["GM"], -10600.0, "Equilibrium Gibbs energy at 1100 K", tol=1e-6)
ready["pycalphad"] = True

# %% [markdown]
# ## 3. A plot
#
# You should see two straight lines crossing at 1000 K (solid: full line,
# liquid: dashed). If no figure appears, plots are not working yet.

# %%
import matplotlib.pyplot as plt
import numpy as np

temperatures = np.linspace(800, 1200, 41)
energies = unary.gibbs(temperatures)
fig, ax = plt.subplots(figsize=(5, 3.2))
ax.plot(temperatures, energies[:, 0] / 1000, "-", label="SOLID")
ax.plot(temperatures, energies[:, 1] / 1000, "--", label="LIQUID")
ax.set_xlabel("T (K)")
ax.set_ylabel("g (kJ/mol)")
ax.legend()
plt.show()
ready["plots"] = True

# %% [markdown]
# ## 4. Published databases (for the full Task 01–05 calculations)
#
# The real-alloy tasks use two published databases. Tasks 01–04 use the Cu–Ni
# database when it is present (Task 01 for its whole calculation, Tasks 02–04 for
# optional parts); Task 05 uses the Ni–Nb database in the same way. Without them
# every task still runs in no-database mode from saved results. You fetch the
# databases yourself; they are kept outside the course folder and checked by size
# and SHA-256.
#
# | Database | Source |
# |---|---|
# | Cu–Ni, `CuNi-92Mey-LB.tdb` | [phasediagrams.org](https://phasediagrams.org/phase-diagram/CuNi-92Mey-LB.tdb); S. an Mey, *Calphad* 16 (1992) 255–260; B. Hallstedt, *Calphad* 89 (2025) 102833 |
# | Ni–Nb, `calpha_102563_Nb-Ni_new_mmc1.tdb` | [supplement of Sun et al.](https://doi.org/10.1016/j.calphad.2023.102563), *Calphad* 82 (2023) 102563 |
#
# Change `DOWNLOAD` to `True` to fetch them now. If a download is refused,
# the message says how to get the file in your browser instead.

# %%
DOWNLOAD = False
ready["Cu–Ni database"] = database("cuni", download=DOWNLOAD) is not None
ready["Ni–Nb database"] = database("ninb", download=DOWNLOAD) is not None

# %% [markdown]
# ## 5. What you are ready for

# %%
basics = ["course code", "pycalphad", "plots"]
missing = [item for item in basics if not ready.get(item)]
print(f"{'ready' if not missing else 'not yet'}: Day 1 and Day 2 notebooks, Task 00"
      + (f"  (missing: {', '.join(missing)})" if missing else ""))
for name, tasks in (("Cu–Ni database", "Tasks 01–04 (Cu–Ni)"), ("Ni–Nb database", "Task 05 (Ni–Nb)")):
    if missing:
        print(f"not yet: {tasks}  (missing: {', '.join(missing)})")
    elif ready[name]:
        print(f"ready (full calculation): {tasks}")
    else:
        print(f"ready (saved results; download the {name} for the full calculation): {tasks}")
