# Instructor overview — what to print, run and hand out

One page for running the in-class course.
Details live in the linked run sheets and packets.
Nothing here has been timed with learners yet; durations are planned allocations.

## Before the course

| When | You | Participants |
|---|---|---|
| A week before | Send the [setup notes](setup.md) and ask everyone with a laptop to run [`setup_check`](../notebooks/setup_check.ipynb) (local Jupyter or Colab). Laptops are optional for the primers. | Run `setup_check`; it reports which parts they are ready for. |
| The day before | Run `setup_check` yourself; start a local kernel you will keep open (`poetry run jupyter lab` from the repository root). Print the sheets below and check them on paper: formulas, tables and small units. | — |
| On the day | Keep the [executed notebook copies](../notebooks/instructor_exports/) open offline as a projector fallback. Never install software during class. | — |

## The two primer days (paper first)

| Day | Print for everyone | Keep back, hand out staged | Run sheet | Optional demonstration (≤ 15 min, pre-started kernel) |
|---|---|---|---|---|
| 1 | [Worksheet](print/day1_worksheet.pdf), [reference card](print/day1_reference_card.pdf) | [Answers and hints](print/day1_answers.pdf) | [Day 1 instructor](primer/instructor.md) | W5: [f1](../notebooks/f1_unary_by_hand_and_code.ipynb) section 2; W7: [f2](../notebooks/f2_unary_pycalphad.ipynb) sections 1–3 |
| 2 | [Worksheet](print/day2_worksheet.pdf), [reference card](print/day2_reference_card.pdf) | [Answers and hints](print/day2_answers.pdf) | [Day 2 instructor](primer_day2/instructor.md) | D1–D3: [f3](../notebooks/f3_binary_mixing_potentials.ipynb); D4–D6, D9: [f7](../notebooks/f7_boundary_open_closed.ipynb); D7: [f8](../notebooks/f8_boundary_states.ipynb) |

The PDFs are built from the Markdown sheets (`course/print/build_print.py`);
rebuild them after any change to a worksheet or answer sheet.

## The six worked examples (laptops, after the primers)

Each task is independent; learners can pick the one closest to their work.
Each packet has its own answers; each notebook lets learners try first and
then check.

| Task | Packet | Answers | Notebook | Needs |
|---|---|---|---|---|
| 00 Tools | [Setup, Task 00](setup.md#task-00-check-the-tools) | in the setup notes | [setup_check](../notebooks/setup_check.ipynb), [f2](../notebooks/f2_unary_pycalphad.ipynb) | course environment only |
| 01 Cu–Ni equilibria | [README](materials/cuni/README.md) | [answers](materials/cuni/answers.md) | [task01](../notebooks/task01_cuni_equilibria.ipynb) (the full grid takes up to about a minute) | Cu–Ni database, fetched by each learner (optional: saved values work) |
| 02 Cu–Ni fitting | [fitting](materials/cuni/fitting.md) | [answers](materials/cuni/fitting_answers.md) | [f6](../notebooks/f6_fitting_synthetic.ipynb) then [task02](../notebooks/task02_cuni_activity_fit.ipynb) | Cu–Ni database (optional: saved values work) |
| 03 Ni twin boundary | [ni_twin](materials/boundaries/ni_twin.md) | [answers](materials/boundaries/ni_twin_answers.md) | [task03](../notebooks/task03_ni_twin.ipynb) | Cu–Ni database (optional: saved values work); curve readings included |
| 04 Cu–Ni segregation | [segregation](materials/boundaries/segregation.md) | [answers](materials/boundaries/segregation_answers.md) | [f7](../notebooks/f7_boundary_open_closed.ipynb) then [task04](../notebooks/task04_cuni_segregation.ipynb) | Cu–Ni database (optional: saved values work) |
| 05 Ni–Nb ordered phases | [README](materials/ninb/README.md) | [answers](materials/ninb/answers.md) | [task05](../notebooks/task05_ninb_sublattices.ipynb) | Ni–Nb database, fetched by each learner (optional: saved values work) |

Databases are never handed out: each learner downloads them (the notebooks
check size and SHA-256; sources and citations in [sources/README.md](sources/README.md)).
Without them every task notebook still runs from the saved results.

## Beyond the classroom

- Detailed lessons for learners who need more depth: [lesson library](assembled_route.md)
  and the matching notebooks f0–f8 ([crosswalk](../notebooks/README.md)).
- Learners working alone: the self-study site (steps 00–06, not yet hosted;
  build it locally from `site/`) uses the same notebooks through its
  "Open in Colab" buttons.

## Status

Nothing has been piloted with learners yet.
