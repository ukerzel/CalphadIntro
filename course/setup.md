# Set up and run the introductory examples

Start in the root of your checkout, beside `pyproject.toml` and `poetry.lock`.
The two [primers](README.md) also work on paper. For computations you need
**CPython 3.12**, **Poetry 2.x**, and internet access for packages and two
external databases. The examples were run with Python 3.12.14 and Poetry
2.5.1 on Linux. Obtain Python and Poetry through their normal installation
instructions; the examples do not install system software for you.
[Poetry installation instructions](https://python-poetry.org/docs/#installation).

## Install the locked environment

Use a terminal without another virtual environment activated. If one is active,
leave it first (`deactivate` for a standard venv). This prevents Poetry from
selecting an unrelated environment. Then, from the repository root:

```bash
export POETRY_VIRTUALENVS_IN_PROJECT=true
poetry env use python3.12
poetry install --without atomistic
.venv/bin/python -c "import sys, pycalphad; print(sys.executable); print(sys.version); print(pycalphad.__version__)"
```

Expect this checkout's `.venv/bin/python`, Python **3.12.x**, and pycalphad
**0.11.2**. Use the committed `poetry.lock` without regenerating it. The optional atomistic
group is unnecessary; no OpenCalphad, LAMMPS job or Equilipy exercise is required.
If package access fails, stop setup and retain the error. Do not change package
versions to turn a failed installation into a passing one.

No commercial software or licence file is needed. The [source guide](sources/README.md)
documents licensed/included material, all paper access routes and the Cu–Ni ZIP fallback.

## Optional: run the course notebooks

`poetry install --with dev` adds Jupyter and jupytext. Then, from the
repository root, `poetry run jupyter lab` and open `notebooks/setup_check.ipynb`:
it checks the versions, the course code, pycalphad, plotting and your database
copies, and says which tasks you are ready for. The
[notebook crosswalk](../notebooks/README.md) lists one notebook per task and
lesson; each also opens in Colab.

## Obtain the two external inputs

Only Tasks 01–05 need these inputs. Code and the small cited teaching data are
included; complete TDBs and paper figures remain external. Keep downloaded
files outside the checkout. For example:

```bash
export CALPHAD_INPUT_DIR="$HOME/calphad-inputs"
mkdir -p "$CALPHAD_INPUT_DIR"
```

Download [CuNi-92Mey-LB.tdb](https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb)
there. Download [Sun's Ni–Nb supplement ZIP](https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip)
and extract **`calpha_102563_Nb-Ni_new_mmc1.tdb`** into the same directory.
You can use a browser, or this Python block in the terminal:

```bash
.venv/bin/python - <<'PY'
import io, os, urllib.request, zipfile
from pathlib import Path
folder = Path(os.environ['CALPHAD_INPUT_DIR'])
with urllib.request.urlopen('https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb', timeout=30) as response:
    (folder / 'CuNi-92Mey-LB.tdb').write_bytes(response.read())
with urllib.request.urlopen('https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip', timeout=30) as response:
    archive = response.read()
member = 'calpha_102563_Nb-Ni_new_mmc1.tdb'
with zipfile.ZipFile(io.BytesIO(archive)) as supplement:
    (folder / member).write_bytes(supplement.read(member))
PY
```

Check the files before running a material example:

```bash
.venv/bin/python - <<'PY'
import hashlib, os
from pathlib import Path
folder = Path(os.environ['CALPHAD_INPUT_DIR'])
expected = {
    'CuNi-92Mey-LB.tdb': (6789, '7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1'),
    'calpha_102563_Nb-Ni_new_mmc1.tdb': (13087, 'ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a'),
}
for name, identity in expected.items():
    data = (folder / name).read_bytes()
    actual = (len(data), hashlib.sha256(data).hexdigest())
    if actual != identity:
        raise SystemExit(f'Input mismatch: {name}: {actual}')
    print(f'OK: {name}')
PY
```

If a download fails, use the same published supplement/browser route described
in the [Cu–Ni](materials/cuni/README.md) or [Ni–Nb](materials/ninb/README.md)
source note. If the member or hash differs, stop that example and report the
mismatch; do not edit the input. Task 00 and the paper primers remain usable.
The course notebooks find the databases in this `$CALPHAD_INPUT_DIR` folder
(or `~/calphad-inputs`); they can also download them themselves.

## Task 00: check the tools

For the following Linux commands, prepare a temporary output directory and
limit numerical libraries to one thread:

```bash
export CALPHAD_OUTPUT_DIR="$(mktemp -d /tmp/calphad-examples-XXXXXX)"
export MPLCONFIGDIR="$CALPHAD_OUTPUT_DIR/mpl" MPLBACKEND=Agg
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$MPLCONFIGDIR"
poetry run python -m course.foundations.one_component_manual
poetry run python -m course.foundations.one_component_tools
```

The first prints a five-temperature table and **1000 K** crossing for the
included invented unary model. The second prints the pycalphad comparison as
JSON. No external TDB is needed. The [opening explanations](foundations/README.md)
provide hand calculations and exercises.

## Run Tasks 01–05

Use the input and output variables set above. Each command is independent;
select one using the [ordered course entry](README.md), then read its lesson
and inspect the resulting plot and JSON. The parentheses apply Linux address
space limits only to that command: 4 GiB/600 s for diagrams, 2 GiB/120 s for
fitting and boundary examples. On other systems use the same Python commands
with an equivalent local resource limit.

```bash
# Task 01 — Cu–Ni diagram, energies and magnetism on/off
(ulimit -v 4194304; timeout 600 .venv/bin/python course/materials/cuni/worked_example.py --tdb "$CALPHAD_INPUT_DIR/CuNi-92Mey-LB.tdb" --output "$CALPHAD_OUTPUT_DIR/task01")
# Task 02 — fit two FCC interactions at 1000 K
(ulimit -v 2097152; timeout 120 poetry run python -m course.materials.cuni.fit_activity --tdb "$CALPHAD_INPUT_DIR/CuNi-92Mey-LB.tdb" --output "$CALPHAD_OUTPUT_DIR/task02")
# Task 03 — Ni twin curve and area/site accounting
(ulimit -v 2097152; timeout 120 poetry run python -m course.materials.boundaries.ni_twin --tdb "$CALPHAD_INPUT_DIR/CuNi-92Mey-LB.tdb" --output "$CALPHAD_OUTPUT_DIR/task03")
# Task 04 — illustrative open/finite Cu–Ni segregation
(ulimit -v 2097152; timeout 120 poetry run python -m course.materials.boundaries.segregation --tdb "$CALPHAD_INPUT_DIR/CuNi-92Mey-LB.tdb" --output "$CALPHAD_OUTPUT_DIR/task04")
# Task 05 — Ni–Nb diagram, ordered phases and amount conversions
(ulimit -v 4194304; timeout 600 .venv/bin/python course/materials/ninb/worked_example.py --tdb "$CALPHAD_INPUT_DIR/calpha_102563_Nb-Ni_new_mmc1.tdb" --output "$CALPHAD_OUTPUT_DIR/task05")
```

| Output directory | JSON | Plot(s) |
|---|---|---|
| `task01` | `results.json` | `phase_diagram.png`, `energy_magnetism.png` |
| `task02` | `activity_fit_results.json` | `activity_fit.png` |
| `task03` | `ni_twin_results.json` | `ni_twin.png` |
| `task04` | `segregation_results.json` | `segregation.png` |
| `task05` | `results.json` | `phase_diagram.png` |

The material lessons name the published comparison figures, checks and limits.
Task 02 is an isothermal calibration; Task 03 combines a cited simulated curve
with stated teaching geometry; Task 04's boundary preference is invented.
These executions demonstrate the declared models. They do not validate their
physics.
