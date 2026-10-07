# Detailed lesson library — the 36-meeting resource map

The 36-meeting sequence below is an optional resource map, not a required
schedule. If you use the library as a full course, follow the rows in order; each reading is
paired with a learner worksheet and a separate instructor answer guide.
The [one-day primer](primer/README.md) is a separate shorter route, not a
replacement for these 36 meetings. Each meeting is 90 minutes.

| Meetings | Unit and paper route | Learner worksheet | Instructor answers |
|---|---|---|---|
| 01–03 | [0 — U, H, S, F, G](foundations/lesson_00.md) | [0 tasks](foundations/lesson_00_worksheet.md) | [0 guide](instructor/lesson_00_guide.md) |
| 04–05 | [1 — unary by hand/plain code](foundations/lesson_01_one_component.md) | [1 tasks](foundations/lesson_01_worksheet.md) | [1 guide](instructor/lesson_01_guide.md) |
| 06 | [2 — same model in pycalphad](foundations/lesson_02_same_model_pycalphad.md), [offline output](foundations/lesson_02_offline_output.md) | [2 tasks](foundations/lesson_02_worksheet.md) | [2 guide](instructor/lesson_02_guide.md) |
| 07 | [Clinic A — energy/constraint synthesis](foundations/clinic_a_thermo_unary.md) | In clinic sheet | [A guide](instructor/clinic_a_guide.md) |
| 08–09 | [3 — composition/counting](foundations/lesson_03_composition.md) | [3 tasks](foundations/lesson_03_worksheet.md) | [3 guide](instructor/lesson_03_guide.md) |
| 10–11 | [4 — ideal mixing](foundations/lesson_04_ideal_mixing.md) | [4 tasks](foundations/lesson_04_worksheet.md) | [4 guide](instructor/lesson_04_guide.md) |
| 12–13 | [5 — balanced coexistence](foundations/lesson_05_two_phase.md) | [5 tasks](foundations/lesson_05_worksheet.md) | [5 guide](instructor/lesson_05_guide.md) |
| 14–15 | [6 — chemical potentials/common tangent](foundations/lesson_06_chemical_potential.md) | [6 tasks](foundations/lesson_06_worksheet.md) | [6 guide](instructor/lesson_06_guide.md) |
| 16 | Clinic B — integrated task in [Lesson 6 worksheet](foundations/lesson_06_worksheet.md) | Meeting 16 section | [6 guide](instructor/lesson_06_guide.md) |
| 17–18 | [7 — nonideal stability](foundations/lesson_07_regular_solution.md) | [7 tasks](foundations/lesson_07_worksheet.md) | [7 guide](instructor/lesson_07_guide.md) |
| 19–20 | [8 — original binary tools](foundations/lesson_08_binary_tools.md) | [8 tasks](foundations/lesson_08_worksheet.md) | [8 guide](instructor/lesson_08_guide.md) |
| 21–22 | [9 — one-parameter fitting](foundations/lesson_09_fitting.md) | [9 tasks](foundations/lesson_09_worksheet.md) | [9 guide](instructor/lesson_09_guide.md) |
| 23–24 | [10 — Ni–Cu source audit at GAP](foundations/lesson_10_source_audit.md) | [10 tasks](foundations/lesson_10_worksheet.md) | [10 guide](instructor/lesson_10_guide.md) |
| 25 | Clinic C — claim/data matrix in [Lesson 10 worksheet](foundations/lesson_10_worksheet.md) | Meeting 25 section | [10 guide](instructor/lesson_10_guide.md) |
| 26–27 | [11 — boundary geometry/basis](foundations/lesson_11_geometry.md) | [11 tasks](foundations/lesson_11_worksheet.md) | [11 guide](instructor/lesson_11_guide.md) |
| 28–29 | [12 — one-state open reservoir](foundations/lesson_12_reservoir.md) | [12 tasks](foundations/lesson_12_worksheet.md) | [12 guide](instructor/lesson_12_guide.md) |
| 30–31 | [13 — finite closed inventory](foundations/lesson_13_finite_reservoir.md) | [13 tasks](foundations/lesson_13_worksheet.md) | [13 guide](instructor/lesson_13_guide.md) |
| 32–33 | [14 — two uniform synthetic states](foundations/lesson_14_competing_states.md) | [14 tasks](foundations/lesson_14_worksheet.md) | [14 guide](instructor/lesson_14_guide.md) |
| 34 | [Clinic D — ensemble/branch synthesis](foundations/clinic_d_synthetic_boundary.md) | In clinic sheet | [D guide](instructor/clinic_d_guide.md) |
| 35–36 | [15 — case judgment at source GAP](foundations/lesson_15_case_judgment.md) | [15 tasks](foundations/lesson_15_worksheet.md) | [15 guide](instructor/lesson_15_guide.md) |

The row intervals cover meetings **01 through 36 exactly once**. Clinic A
and D have standalone learner sheets; Clinics B and C are complete meeting
sections in their neighboring worksheets. Keep all answer guides separate
from independent attempts. Supplied output is a paper fallback only for
the unchanged Lesson 2 unary model; it is not a new material result.

## Dependency and stop map

The synthetic method path is 0–2 → Clinic A → 3–6 → Clinic B → 7–9 →
10/Clinic C **as a source audit**; Lesson 11 can use its synthetic
geometry without a Ni–Cu model; Lessons 12–14 and Clinic D stay invented.
Lesson 15 makes a research judgment from the documented source GAP.
At every boundary exercise, keep geometry, amount basis, reference,
ensemble and candidate state set explicit. A program run is a model check,
not a material prediction.

The real capstone remains a separate path: an exact case/source choice, a
checked bulk model and a matched defect input must be accepted, then a bounded
real calculation with its own physical/resource/run controls and an
independent check of its result are required. One evidenced state can
support only its conditional segregation question; two compatible evidenced
state functions plus physical coexistence analysis are needed for a
transition question. No Ni–Cu $\mu_i$, $\Gamma$, transition, kinetic or
mechanical-property result is included here.
