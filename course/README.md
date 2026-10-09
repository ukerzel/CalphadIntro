# Open CALPHAD course — primers and six worked examples

Two one-day primers, six worked examples and an optional lesson library; not
a semester programme.
Begin with [primer day 1](primer/README.md) and [primer day 2](primer_day2/README.md).
Both have a paper route. For the runnable examples, use the
[fresh-checkout setup and input guide](setup.md), then select a task below.
The examples are independently usable; the detailed lesson library is optional.
The [source/retrieval guide](sources/README.md) lists included excerpts, exact
downloads and comparison pages. **Only open-source software and published
inputs are needed.** The one-page [course map](course_map.md) shows the
goals, the junctions and a short path per part; the optional
[advanced steps 07–18](day3/README.md) read the equilibrium calculation as an
optimisation problem.

**Instructors:** the one-page [instructor overview](instructor_overview.md) lists what to
print, run and hand out for each day and task; the [pilot protocol](primer/pilot.md)
records a first run.

**Notebooks.** Every task and the computational lessons have a runnable
notebook (local Jupyter or Colab); start with `notebooks/setup_check.ipynb`.
The [notebook crosswalk](../notebooks/README.md) maps notebooks to primer tasks,
lessons and self-study steps.

| Task | Start here | Input |
|---|---|---|
| 00 — tooling and unary energies | [Run the unary examples](setup.md#task-00-check-the-tools) · [opening explanations](foundations/README.md) | Invented unary model included in the repository |
| 01 — Cu–Ni equilibria | [Phase diagram, energies and magnetism on/off](materials/cuni/README.md) | Learner-fetched Cu–Ni TDB |
| 02 — Cu–Ni fitting | [Fit two isothermal interactions](materials/cuni/fitting.md) | Same TDB; cited activity observations included |
| 03 — Ni twin boundary | [Twin-energy curve and area/site accounting](materials/boundaries/ni_twin.md) | Same TDB; cited simulated curve readings included |
| 04 — Cu–Ni segregation | [Open reservoir and finite inventory](materials/boundaries/segregation.md) | Same TDB; explicitly invented boundary preference |
| 05 — Ni–Nb ordered phases | [Diagram, sublattices and formula/atom conversion](materials/ninb/README.md) | Learner-fetched Sun TDB |

## Lesson library

The optional [lesson library](assembled_route.md) and its notebooks f0–f8 give
more depth; nothing in it is required before a task. To see what a CALPHAD
program does inside an equilibrium calculation, work through
[f4b](../notebooks/f4b_lens_from_scratch.ipynb): one phase diagram from scratch
in numpy/SciPy, then the same in pycalphad.
