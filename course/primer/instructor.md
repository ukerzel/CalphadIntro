# Instructor run sheet

Use with the [learner worksheet](worksheet.md) and [staged hints/answers](answers.md).
This is a planned 390-minute introduction; its pacing has not been measured.
Preserve the assumptions when paraphrasing. Ask for a prediction before showing
an answer; use paired discussion without requiring anyone to disclose experience.

## Preparation and access

Print the worksheet, separate hints/answers, and scratch paper. Check that minus
signs, subscripts, tables and formulas remain readable in your actual print
renderer. Tables plus hand sketches replace the optional SVG; do not depend on
colour or tiny projection labels. Supply the reference sheet throughout. The
packet contains all required paper activities and selected outputs locally.
The saved W5 and W7 tables show W4's answers: ask learners to fold or cover
those pages until W4 is done, or print those tables as separate output cards.
Reading online sources is optional instructor preparation, not learner homework.
Print rendering and room visibility have not been tested.

If demonstrating, use the course Poetry environment from the repository
root; follow the [foundations setup](../foundations/README.md#running-the-examples).
Do not spend learner time installing software. If it is unavailable, use the
paper route immediately. Known pycalphad/NumPy deprecation warnings can
appear; a traceback or unexpected result stops the demonstration, not the class.

## Timed board and activity plan

Minutes in each row sum to that block. Worked arithmetic, learner practice and
annotated output interpretation dominate each core block. Never silently borrow
break, lunch or exit time. The diagnostic and exit have no required coding.

| Time / task | Minute allocation | Board / action | Listen for and respond |
|---|---|---|---|
| 09:00 W0, 15 | 5 welcome; 5 sketch; 5 discussion | Specimen box inside furnace; arrows for heat | Closed is not isolated; distinguish matter from energy. |
| 09:15 W1, 45 | 15 explain; 15 worked; 15 pairs | ΔU=q+w on; H=U+pV; show Pa·m³=J | Correct work sign and “stored heat”; keep pV example separate from A. |
| 10:00 W2, 30 | 10 explain; 10 guided; 10 discussion | 600 J / 300 K; label reversible/isothermal | Sample S alone is not the isolated whole's S. |
| 10:30, 15 | 15 break | Stop instruction | Keep break. |
| 10:45 W3, 45 | 15 map; 15 worked; 15 choice/explanation | U→H add pV; U→F subtract TS; H→G subtract TS | Ask what is held fixed before accepting “minimize G.” |
| 11:30 W4, 45 | 10 explain; 15 worked; 20 prediction/sketch | Two lines, common basis, 6T=6000 | Larger negative magnitude means lower; equilibrium is not a time. |
| 12:15, 60 | 60 lunch | Stop instruction | Keep lunch. |
| 13:15 W5, 45 | 10 annotate; 15 facilitator walk-through; 20 supported change | Match code constants to hand equations, then 950 K | Paper: annotate the printed code and compute 950 K. Demo is optional. |
| 14:00 W6, 30 | 10 objective; 10 trial fractions; 10 interpret result | Rising mixture line at 900 K; flat at 1000 K | Reject a negative amount; crossing does not fix fraction. |
| 14:30, 15 | 15 break | Stop instruction | Keep break. |
| 14:45 W7, 45 | 10 term map; 15 demonstration/walk-through; 20 paired interpretation | Same h−Ts in TDB; load→evaluate→minimize | Paper: read three-action table and selected output, including restricted phase set. |
| 15:30 W8, 30 | 5 frame; 15 individual/pairs; 10 feedback | 1050 K, unit and amount error cards | Ask for a rejected output's reason, not only corrected number. |
| 16:00 W9, 30 | 5 frame; 15 card sort; 10 discuss | Composition→sites/exchange→structures | A crossing supplies no real Ni–X/defect data. |
| 16:30 W10, 30 | 15 exit; 10 feedback; 5 next steps | Four exit actions with reference sheet | Record support and unfinished reasoning; choose the next task (00–05). |

Core blocks W1–W8 budget 200/315 minutes for worked/guided/practice/interpretation,
excluding explanation/map time and both optional 15-minute demonstrations.
This is allocation, not evidence of actual learner engagement or fit.

## Demonstration route and saved alternative

W5 has one executable cell, copied exactly from Lesson 1. In a fresh
Python session from the repository root, paste the complete cell and compare its
four columns with the printed table. For the supported change, replace the input
array with `[950.0]`, leaving h/s untouched. It should print 950, −8500, −8200, −8500.
The normal primer does not ask learners to type control blocks into an interpreter.
The same cell is section 2 of the notebook
[f1_unary_by_hand_and_code](../../notebooks/f1_unary_by_hand_and_code.ipynb); for W7, sections 1–3 of
[f2_unary_pycalphad](../../notebooks/f2_unary_pycalphad.ipynb) show the TDB text, `calculate`,
`equilibrium` and the SOLID-only result at 1100 K. Open them in a kernel started
before the session (`poetry run jupyter lab`); never install during class.

For W6, inspect `equilibrium_at` in
[the plain module](../foundations/one_component_manual.py), especially coefficients,
nonnegative bounds, conservation and failure check. Use its saved 900 K output
on the worksheet. Linear-programming derivations are not needed today.

For W7, show the full [TDB](../foundations/one_component_model.tdb) and
the [Lesson 2 cells](../foundations/lesson_02_same_model_pycalphad.md).
Follow load, evaluate both branches, then equilibrium in that order. The complete
course module can reproduce the selected table without typing new model code:

```bash
poetry run python -m course.foundations.one_component_manual
poetry run python -m course.foundations.one_component_tools
```

The worksheet's TDB records are excerpts, not a runnable replacement database;
its argument card is an annotation exercise, not executable Python. Demo only
inside 800–1200 K at p=100000 Pa, N=1. Follow the lesson's cell instructions,
including blank lines and stop-on-error guidance. If software fails or time is
short, walk through printed results and label the route “paper” or “watched.”
No installation, hosted service or independent learner coding is assumed.

## Operations-research asides (optional, at most 5 minutes each)

For groups with operations-research learners, or when teaching with an operations-research
colleague. Each aside connects the step to the advanced steps 07–18 of the website; none is needed
for the day's outcomes.

- **W6:** a linear objective on the segment $0\le f_L\le1$ is smallest at an
  end; at 1000 K the objective is flat and every point of the segment ties.
  Feasibility (bounds and the amount balance) comes before the objective, and a
  solver's "success" still needs the balance and energy checks.
- **W7:** leaving LIQUID out at 1100 K shrinks the candidate list, so the
  minimum can only rise (−10000 instead of −10600 J/mol). The advanced steps call the best
  mixture of a restricted list a *ceiling*.
- **W8, report B:** it fails feasibility (the fractions sum to 1.2) before any
  energy is looked at. Check the constraints first, then the objective.

## Recovery and incomplete outcomes

First reduce W9 from 30 to 10 minutes: two minutes framing, five sorting cards
1–6, three discussing why real predictions need more inputs. Transfer the freed
twenty minutes to the core block needing practice; preserve the 17:00 finish.
Next switch live code to the supplied-output route. It preserves the interpretation
activity and avoids setup/debugging time; it does not prove execution competence.
If core work still does not fit, keep W10 and record which supported outcomes
remain incomplete. Do not introduce binary mathematics as an “extension” or cut
breaks to force completion. Redesign timing from actual observations later.

## Source-to-excerpt and assessment map

| Primer | Where it comes from | Checkable learner evidence |
|---|---|---|
| W0–W3 | Lesson 0 §§0.1–0.8, condensed; guided numbers written for the primer | Signs, pV, units, condition choice; W10 action 1 |
| W4 | Lesson 0 §0.9, Lesson 1 §§1.1–1.4; same synthetic model | Both branches/crossing; W10 action 2 |
| W5 | Lesson 1 first NumPy array cell, copied unchanged; Lesson 1's saved branch results | Match constants, fresh 950 K substitution |
| W6 | Lesson 1 §§1.5–1.7; argument card summarizes the lesson's solver call | Trial fractions/bounds/balance; W10 action 3 |
| W7 | Lesson 2 §§2.1–2.5; TDB records copied unchanged; selected saved rows | Load/evaluate/minimize; amount/energy comparison |
| W8 | Arithmetic/error exercises written for the primer; same model and conditions | Fresh 1050 K, inconsistent units/amounts |
| W9 | Lesson 2 §2.6 and the course's bulk-to-boundary progression | Missing-input card reasons; W10 action 4 |
| W10 | 975 K and conversion task written for the primer; same model and conditions | Four supported outcomes; named assistance and gaps |

The primer has not been piloted with learners; record a first run on the
[pilot form](pilot.md).
