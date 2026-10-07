# Synthetic foundations

These original lessons teach verification of a declared thermodynamic model.
All energy parameters are invented for instruction and have **no Ni-X or other
material interpretation**.


**Notebooks.** Each computational lesson has a course notebook (local Jupyter or
Colab): Lesson 0 → f0, Lesson 1 → f1, Lesson 2 → f2, Lessons 3, 4 and 6 → f3,
Lessons 5 and 7 → f4, Lesson 8 → f5, Lesson 9 → f6, Lessons 11–13 → f7,
Lesson 14 → f8. See the [notebook crosswalk](../../notebooks/README.md).

Start with [Lesson 0](lesson_00.md). The first lessons move slowly and reuse one
invented solid/liquid example so each new tool has a familiar physical meaning.
The opening lessons take six 90-minute meetings plus a practice
clinic. A lesson page is a reading unit, not one lecture's content.
Meetings 01–03 have a [Lesson-0 worksheet](lesson_00_worksheet.md) and
[instructor guide with answers](../instructor/lesson_00_guide.md).
Meetings 04–05 have a [manual-unary worksheet](lesson_01_worksheet.md) and
[instructor guide](../instructor/lesson_01_guide.md) with a supported paper route.
Meeting 06 has a [same-model tool worksheet](lesson_02_worksheet.md),
[supplied outputs](lesson_02_offline_output.md) for offline work and an
[instructor guide](../instructor/lesson_02_guide.md).
[Clinic A](clinic_a_thermo_unary.md) supplies the scheduled meeting 07
paper synthesis and unfamiliar-phase transfer, with an
[instructor key](../instructor/clinic_a_guide.md).
For a short introduction, see the
[one-day primer](../primer/README.md). The full [assembled course route](../assembled_route.md)
indexes Lessons 0–15 and all four clinics.

| Order | One main step | Status |
|---|---|---|
| 0 | Internal energy, enthalpy, entropy, Helmholtz/Gibbs energy and constraints | [Read the refresher](lesson_00.md); no code required |
| 1 | Compare the same two phase-energy lines by hand and plain NumPy; then expose the SciPy optimization | [Plain-code worked example](lesson_01_one_component.md) |
| 2 | Encode those exact lines in a tiny original TDB and repeat with pycalphad | [Repeat the same model](lesson_02_same_model_pycalphad.md) |
| 3–9 | Composition, ideal/nonideal binary equilibrium, common tangents, tools and a synthetic fit | [Assembled course route](../assembled_route.md) |
| 10–15 | Source audit, synthetic boundary sequence and case judgment | [Assembled course route](../assembled_route.md) |

Every early section uses explain → calculate one step → pause → answer. Optional
stretch questions add depth without accelerating the shared core. Optimizing
equilibrium and fitting model parameters will be taught as different tasks.

## Running the examples

Lesson 0 needs no software. For Lessons 1–2, use this repository checkout with
CPython 3.12 and Poetry (the recorded environment used Poetry 2.1.2). Install
Poetry by its [official instructions](https://python-poetry.org/docs/#installation)
if it is not available. Open a terminal in the repository root, where
`pyproject.toml` and `poetry.lock` live, then run:

```bash
poetry env use python3.12
poetry install
poetry run python -c "import numpy, scipy, pycalphad; print('ready')"
```

The success check prints `ready`. The optional atomistic dependency group is
not needed. The full main environment is shared with later CALPHAD work; the
plain example itself uses NumPy/SciPy, with Matplotlib only for its figure.
Use `poetry run python` for a Python session. Paste one complete Python block
at a time, in order, preserving the blank lines inside it. After the paste,
press Enter if needed to submit the last line. If Python still shows `...`,
press Enter on an empty line to finish the block. Wait for `>>>` before pasting
the next block. If an error appears, stop and check it; later output does not
establish that the block succeeded. Commands marked `bash` belong in the
terminal, not inside Python.
Return to the terminal with `exit()` when finished.

Run the complete examples and their checks from that same repository root:

```bash
poetry run python -m course.foundations.one_component_manual
poetry run python -m course.foundations.one_component_tools
poetry run python -m unittest discover -s tests -p test_one_component_course.py -v
```

The first command prints the five-temperature table and a 1000 K crossing.
The second prints a comparison record. [The checked-in result](one_component_result.json)
and [model contract](one_component_contract.md) identify the versions, inputs,
units and checks. Some test runs expose
an upstream NumPy shape-deprecation warning in pycalphad; all comparison checks
still pass. A traceback or failed test is a different result and needs attention.

## Earlier binary exercise

The earlier [binary exercise](lesson_01.md) is kept as supplementary material
for a later lesson. Despite its filename, it is **not the opening Lesson 1 in
this sequence**. It still needs numerical and teaching revisions before
standalone use. Run its existing checks from the repository root:

```bash
poetry run python -m unittest discover -s tests -p test_course_foundations.py -v
```

These checks establish only the stated synthetic equations and implementation.
