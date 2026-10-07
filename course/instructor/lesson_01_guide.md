# Instructor guide — manual unary comparison and equilibrium

Meetings 04–05. Use the [worksheet](../foundations/lesson_01_worksheet.md)
with the [original reading](../foundations/lesson_01_one_component.md).

## Preparation and access

Check the Lesson-0 explanation tasks before teaching. Keep the worksheet model
card visible throughout. Supply calculator, graph paper, worksheet and this
guide's answer tables separately. The paper route completes the same predictions,
tables and annotations without installing software. Label any printed/computer
demonstration result as supplied; do not claim a learner executed it.

For the live route use the [pinned setup](../foundations/README.md#running-the-examples)
and run the three worksheet Python cells in order. Run Python blocks inside
Python, not in the terminal; the README explains the prompt and blank line
needed after an indented block. Show assignment, multiplication, arrays,
function input/return and comments as each first appears. No learner needs to
write a solver or understand linear-algebra notation to label its physical roles.

Before class, the existing full calculation/check commands are:

~~~bash
poetry run python -m course.foundations.one_component_manual
poetry run python -m unittest discover -s tests -p test_one_component_course.py -v
~~~

The model and test tolerances are in the
[contract](../foundations/one_component_contract.md). Success alone is
insufficient: compare both phase branches, bounds, balance and minimum energy.
Never treat an arbitrary crossing fraction as a unique prediction.

## Timing and board plan

| Minutes | Meeting 04 | Meeting 05 |
|---|---|---|
| 00–10 | Retrieve C5: conditions, same amount, lower g | Retrieve D4; sketch the two branches |
| 10–22 | Model card, signs and short Python notation introduction | Introduce fS,fL; objective, variables and constraints |
| 22–40 | D1 then first two D2 rows by hand; show array cell | E1 by hand; annotate E3 call before running |
| 40–45 | Break | Break |
| 45–70 | Complete D2 table/plot (15); D3 hand crossing then root (10) | E2 table (12); E3 changed temperature/crossing (8); E4 (5) |
| 70–85 | D4 independently (8), feedback (7) | E5 independently (8), feedback (7) |
| 85–90 | Collect D4; state one model limit | Collect E5; explain crossing nonuniqueness |

Keep guided practice and breaks if syntax discussion overruns; use the supplied
output route and arrange setup help outside the core meeting. Record unfinished
conceptual work and schedule another attempt. Timings are planned; they have not been observed with learners.
Do not turn optional discussion about reference shifts into an entry requirement.

## Hints and answers: meeting 04

| Task | Hint 1 | Hint 2 |
|---|---|---|
| D2 | Compute the two phases separately. | Subtract solid from liquid; positive gap means solid is lower. |
| D3 | A root makes the difference zero. | Solve 6T=6000; then check opposite bracket signs. |
| D4 | Change T, keeping h and s fixed. | Compute 1000−10×950 and 7000−16×950. |

D1: the gap decreases by 6 J/mol for each kelvin increase.
D2 answer table and supplied output values:

| T, K | gS, J/mol | gL, J/mol | Δg, J/mol | Selection |
|---:|---:|---:|---:|---|
| 800 | −7000 | −5800 | 1200 | SOLID |
| 900 | −8000 | −7400 | 600 | SOLID |
| 1000 | −9000 | −9000 | 0 | Tie |
| 1100 | −10000 | −10600 | −600 | LIQUID |
| 1200 | −11000 | −12200 | −1200 | LIQUID |

The first cell prints these first four columns as floating-point numbers.
Both branches are needed to locate the crossing and check the higher branch.
Ask learners to describe the liquid's larger downward slope in terms of entropy.

D3: the bracket endpoints give +1200 and −1200 J/mol; the hand root and printed
root are 1000 K. The 800–900 K bracket has no sign change and contains no root
of these two lines; this brentq call raises ValueError. This is a useful
diagnostic, not a reason to change the model. Root finding varies T to make
Δg zero. Parameter fitting would vary h/s using data, which this task lacks.

D4: at 950 K, gS=−8500 and gL=−8200 J/mol; Δg=300 J/mol.
SOLID is favored at the stated pressure on the same molar basis.
Liquid has the more negative −Ts slope. There is no rate information.

## Hints and answers: meeting 05

| Task | Hint 1 | Hint 2 |
|---|---|---|
| E2 | Each row splits the same one mole. | At 900 K use −8000+600fL; at 1100 K use −10000−600fL. |
| E3 | Identify which input contains the two energies. | Change c with T; keep sum=1 and 0–1 bounds; inspect success first. |
| E4 | A valid state must have physical amounts. | fL=−0.2 forces fS=1.2; at the crossing compare energy and balance, not identical fractions. |
| E5 | Compute branch energies before mixing. | At 1050 K use gmix=−9500−300fL. |

E1: −7850 J/mol; 0.75 mol solid and 0.25 mol liquid at one mole total.
E2:

| fL | 900 K, J/mol | 1000 K, J/mol | 1100 K, J/mol |
|---:|---:|---:|---:|
| 0 | −8000 | −9000 | −10000 |
| 0.25 | −7850 | −9000 | −10150 |
| 0.5 | −7700 | −9000 | −10300 |
| 0.75 | −7550 | −9000 | −10450 |
| 1 | −7400 | −9000 | −10600 |

At 900 K the unique minimum is all solid; at 1100 K all liquid.
At 1000 K every allowed fraction has gmix=−9000 J/mol, including endpoints.

E3: c holds the two energies; A_eq and b_eq express fS+fL=1; bounds require
each fraction in [0,1]. Printed 900 K values are [1,0] and −8000 J/mol
(a signed −0 is zero). The changed coefficients at 1100 K are
[−10000,−10600]; output is [0,1] and −10600 J/mol.
At 1000 K [1,0], [0,1] or any valid mixture is acceptable if balance and
energy agree. The variables are fractions; energies are fixed coefficients
within each equilibrium call.

E4: the arithmetic −8000+600(−0.2)=−8120 J/mol is correct; negative liquid
amount is inadmissible. Check nonnegative amounts, total balance, energy,
model and conditions before declaring solver disagreement at the crossing.

E5: gS=−9500, gL=−9800 J/mol; at fL=0.4, gmix=−9620 J/mol.
The minimum is all liquid at −9800 J/mol. Minimize fS gS+fL gL over the two
fractions, subject to fS+fL=1 and 0≤fS,fL≤1.
Changing fractions at fixed coefficients is equilibrium; fitting changes
parameters to explain observations.

## Readiness handback

Assess D4, E5 and the explanation of the flat 1000 K mixture energy.
If the result was obtained with hints, record supported work and offer a fresh
attempt rather than independent readiness. Annotating a supplied call is valid
on the paper route; record actual execution separately.
No numerical score stands in for explaining conditions, units and constraints.
