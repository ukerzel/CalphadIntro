# One-day CALPHAD primer

A supported introduction for materials researchers with little thermodynamics
and no CALPHAD experience. Bring arithmetic and curiosity; no laptop, programming
experience or preparatory reading is required.

For a two-day supported introduction, continue on the next day with the
[second primer: binary bulk to grain-boundary states](../primer_day2/README.md).
It starts from W9's missing-input map and contains its own paper reading,
exercises, answers and reference card; no detour into the detailed lessons is
required during the two days.

By the end, **with the reference sheet and supplied outputs**, aim to name U, H,
S, F and G; choose G for our fixed-temperature, fixed-pressure bulk question;
compare two molar Gibbs energies; identify the equilibrium objective and amount
constraint; and recognize the same model in arithmetic, plain code and pycalphad.
Explain what is still missing for a real alloy or grain-boundary calculation.
These supported outcomes are narrower than independent mastery of Lessons 0–2.

Print the [worksheet](worksheet.md) for everyone and keep its last reference
section available throughout. Give each person scratch paper and a pen; a basic
calculator is optional. Print the [answer/hint sheet](answers.md) separately for
staged use. The [instructor run sheet](instructor.md) includes board prompts,
recovery choices and the paper alternative for every demonstration. Use the
worksheet's labelled numerical tables even if the optional plot cannot be printed
legibly. Colour, internet access and a screen are not needed for the paper route.
After the day, every worksheet calculation can be repeated in the course
notebooks ([crosswalk](../../notebooks/README.md)): f0 for W1–W3, f1 for W4–W6
and W8, f2 for W7. They are optional and never replace the paper route.

| Time | Minutes | Activity / worksheet task |
|---|---:|---|
| 09:00–09:15 | 15 | Welcome and ungraded system-boundary diagnostic (W0) |
| 09:15–10:00 | 45 | Internal energy and enthalpy (W1) |
| 10:00–10:30 | 30 | Entropy and units (W2) |
| 10:30–10:45 | 15 | Break |
| 10:45–11:30 | 45 | Helmholtz/Gibbs map and conditions (W3) |
| 11:30–12:15 | 45 | Two Gibbs lines by hand (W4) |
| 12:15–13:15 | 60 | Lunch |
| 13:15–14:00 | 45 | Recognize the arithmetic in plain code (W5) |
| 14:00–14:30 | 30 | Objective, fractions and constraints (W6) |
| 14:30–14:45 | 15 | Break |
| 14:45–15:30 | 45 | The same model in TDB/pycalphad (W7) |
| 15:30–16:00 | 30 | Fresh-temperature and error clinic (W8) |
| 16:00–16:30 | 30 | Qualitative Ni–X research map (W9) |
| 16:30–17:00 | 30 | Supported exit, feedback and next steps (W10) |

480 elapsed minutes = 390 contact + 60 lunch + 30 breaks. The optional
detailed opening lessons (six 90-minute meetings plus a clinic) give more practice.
If behind, shorten W9 to ten minutes and transfer twenty to core practice;
then replace optional live code with the printed outputs. Keep breaks and exit.
If core outcomes still cannot fit, record them as incomplete and redesign the
next offering. Do not rush through new equations to preserve the timetable.

Everything quantitative today concerns invented component A, one mole of atoms,
800–1200 K, p=100000 Pa, and only SOLID/LIQUID. There is no measured Ni property,
binary equilibrium, chemical-potential calculation, fitting or defect prediction.
W9 introduces questions and missing inputs without claiming to answer them.

## Next: the six worked examples

After the primers, continue with the worked examples, Tasks 00–05
([course index](../README.md); instructors: [overview](../instructor_overview.md)).
Each task is independent and runs on a laptop. Use the exit explanations to
choose where to start, without a universal score:

- Today's unary model and the tools: Task 00 runs the same model in pycalphad.
- Binary alloys and grain boundaries: take [Day 2](../primer_day2/README.md)
  first; its README maps each step to Task 01, 03 or 04. Task 02 (fitting
  Cu–Ni interactions) and Task 05 (Ni–Nb ordered phases) suit learners whose
  own work needs them.
- Potentials or units still need work: the optional
  [lesson library](../assembled_route.md) has more practice (Lessons 0–2 and
  Clinic A); use it alongside the tasks, not as an entry test.
