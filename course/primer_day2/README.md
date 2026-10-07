# Day 2 primer — from binary bulk to grain-boundary states

This is the second half of a **supported two-day route**. Start with
[Day 1: thermodynamic fundamentals and one invented unary model](../primer/README.md),
then use this packet the next day. Day 1's W9 map asks what extra bulk and
boundary inputs a defect question needs. Here we answer that question with
an **invented A/B example**, ending at a conditional comparison of two
grain-boundary structural states. The boundary functions are simple
**CALPHAD-style Gibbs models**, not TDB phases or validated real-interface
models. A boundary state is a candidate *interface phase* in this teaching
model; no physical Ni–Cu interface phase, transition, kinetics or material
property is established.

Bring Day 1's understanding of $G$ at fixed $T,p$, molar energy versus total
energy, and constrained minimization. You need no laptop or extra
reading. The [learner sheet](worksheet.md) explains every required new
symbol and supplies all numbers and results needed on paper. Bring a basic
calculator (recommended; logarithms and the exponential factor are printed,
so nobody is blocked without one). Keep its reference
sheet visible. The [answers and staged hints](answers.md) are separate. The
[instructor route](instructor.md) gives timing, recovery and checks, and the
[source map](source_map.md) names the detailed lessons behind each step. Those links
are for later depth: the day does **not** require repeated detours into them.
After the day, the calculations can be repeated in the course notebooks
([crosswalk](../../notebooks/README.md)): f3 for D1–D3, f7 for D4–D6 and D9,
f8 for D7. They are optional and never replace the paper route.

By the end, with the reference sheet and supplied results, a participant
should be able to conserve A and B in a binary sample, interpret ideal
mixing and the A-for-B exchange condition, distinguish boundary occupancy
from equal-site excess, choose an open or closed inventory, compare two
compatible minimized boundary-state energies, and say what additional
evidence a real defect-phase claim needs. This is a supported overview, not
independent mastery.

| Time | Minutes | Local task and question |
|---|---:|---|
| 09:00–09:15 | 15 | D0: Day 1 bridge — what changed when B was added? |
| 09:15–10:00 | 45 | D1: binary composition and conserved amounts |
| 10:00–10:30 | 30 | D2: one ideal bulk Gibbs curve and mixing |
| 10:30–10:45 | 15 | Break |
| 10:45–11:30 | 45 | D3: chemical potentials and exchange |
| 11:30–12:15 | 45 | D4: two boundaries, occupancy and excess |
| 12:15–13:15 | 60 | Lunch |
| 13:15–14:00 | 45 | D5: open reservoir and one boundary state |
| 14:00–14:30 | 30 | D6: finite closed inventory |
| 14:30–14:45 | 15 | Break |
| 14:45–15:30 | 45 | D7: two compatible candidate boundary states |
| 15:30–16:00 | 30 | D8: what a real material case would need |
| 16:00–16:30 | 30 | D9: integrated paper case |
| 16:30–17:00 | 30 | D10: supported exit and continuation |

The day is 480 elapsed minutes: **390 contact**, 60 lunch and two 15-minute
breaks. Together the two primers propose **13 contact hours** over two days.
Neither day is a measured pace or a substitute for the worked examples.
Day 2 is denser than Day 1. If time is short, recover in this order
(the same as the [instructor route](instructor.md)):

1. Shorten D8's discussion from 30 to 15 minutes; give the 15 minutes to
   the weakest core step.
2. Drop D7 question 3, the optional D4 mol/m² conversion and D2 question 2.
3. Replace any optional demonstration with the printed output cards.
4. Keep D9, D10, lunch and both breaks. If core work still does not fit,
   record the unfinished outcomes rather than treating a rushed state
   comparison as understood.

Optional demonstrations take time only from a block's explanation or check
minutes, or happen after the day.

## Next: the six worked examples

After the two days, continue with the worked examples, Tasks 00–05
([course index](../README.md); instructors: [overview](../instructor_overview.md)).
Each task is independent and runs on a laptop:

| Here | Next worked example |
|---|---|
| Day 1 potentials and unary comparison | Task 00: the same unary model in pycalphad |
| D1–D3 composition, mixing and exchange | Task 01: Cu–Ni equilibria from a published database |
| D4–D6 boundary sites, open and closed inventory | Task 04: Cu–Ni segregation with an open reservoir and a finite inventory |
| D7 competing boundary states | Task 03 (Ni twin-boundary energies, area/site accounting) and Task 04 |

Tasks 02 (fitting Cu–Ni interactions) and 05 (Ni–Nb ordered phases) suit
learners whose own work needs them. For more depth on any step, the optional
[lesson library](../assembled_route.md) has detailed lessons and exercises;
the [source map](source_map.md) lists them step by step. The two days are an
introduction to the research question, not a validated real
Ni–Cu case.
