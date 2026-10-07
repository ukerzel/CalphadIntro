# Instructor guide — balanced search and lever rule

[Reading](../foundations/lesson_05_two_phase.md),
[worksheet](../foundations/lesson_05_worksheet.md), meetings 12–13.
Timings are planned; they have not been observed with learners. Prepare blank composition axes,
energy cards and separate hints/answers. Preserve the paper route before code.

| Minutes | Meeting 12 | Meeting 13 |
|---|---|---|
| 00–10 | Retrieve A/B inventory; A1 setup | Retrieve feasible versus lowest candidate |
| 10–22 | Explain second branch and weighted energy | Derive lever rule from two balances |
| 22–40 | Worked A1 with two boxes | Worked B1 diagram and amount scaling |
| 40–45 | Break | Break |
| 45–70 | A2 (12), A3 (13) | B2 (10), B3/table or optional code (15) |
| 70–85 | A4 independent (8), feedback (7) | B4 independent (8), feedback (7) |
| 85–90 | Exit: feasible does not mean best | Exit: endpoints, amounts and grid limitation |

90 minutes each,85 contact/practice plus 5 break. If weighted averages stall,
return to boxes and one inventory; use supplied G values rather than recalculate
logs. Defer optional solver inspection, preserve the independent balance attempt.
Record support/incomplete concepts before chemical potential; no fictitious data.

## Staged hints

| Task | Hint 1 | Hint 2 |
|---|---|---|
| A1 | Compare the same total A/B. | Multiply each phase's energy and composition by its amount. |
| A2 | Reflection gives equal region energies. | A lower candidate is still not an exhaustive search. |
| A3 | The solver's word is not a component balance. | Final B is 0.2 mol, required B0.5. |
| A4 | Percent means fraction ×100; label denominator. | B=0.75×0.2+0.25×0.8. |
| B1 | fα=1−fβ. | z=0.2+0.6fβ; then multiply by 4 mol. |
| B2 | A weighted average lies between endpoints. | With fβ=0, overall x is 0.2, not 0.1. |
| B3 | More candidates can only help the mathematical minimum. | Endpoint error can change sign even if energy decreases. |
| B4 | Subtract left endpoint before dividing by the gap. | fβ≈0.095416; N times f is the phase amount. |

## Answers

A1: initial A=B=0.5 mol. Homogeneous branches each −8763.172233 J/mol;
split has Aα=0.4, Bα=0.1, Aβ=0.1, Bβ=0.4 mol and g=−10760.595951 J/mol.
Its reduction is 1997.423718 J/mol. A2: split g=−10502.902382 J/mol;
0.2/0.8 is lower by 257.693568 J/mol. Only these candidates were compared.
A3: total passes 1 mol, but A=0.8 and B=0.2 fail their required 0.5 each.
A4: A=0.75×0.8+0.25×0.2=0.65, B=0.35 mol; g=−10760.595951 J/mol.
These are phase mole/atom-amount percentages, not compositions or mass fractions.
Need a search or analytical proof of the minimum over all allowed balanced states.

B1: fβ=0.25, fα=0.75; nα=3, nβ=1 mol. In ALPHA:A2.4, B0.6; in BETA:A0.2, B0.8.
Totals A2.6, B1.4 mol. B2: fβ=−1/6, fα=7/6 invalid. Clipping to 0/1 gives overall 0.2.
Coincident endpoints at z admit every fraction; balance alone does not determine it.
B3: B=0.5(xα+xβ)=0.5 each row; gaps 2.134067, 0.029178, 0.024721 J/mol.
ALPHA endpoint goes 0.2→0.19→0.192, crossing the reference 0.191040753.
Energy decreases without monotone endpoints; sampling alone is not global proof.

B4: fβ≈0.095415897, fα≈0.904584103; nβ≈0.190831794, nα≈1.809168206 mol.
Bβ≈0.154375144, Bα≈0.345624856 mol (sum 0.5); A totals 1.5 mol.
G≈−21525.460035 J. Coarse 0.2/0.8 amounts fβ=1/12, fα=11/12 preserve z=0.25;
g=−10760.595951 J/mol. Supplied continuous result is lower by 2.134067 J/mol.
Endpoints/region energies were supplied; balances and amounts were derived.
The next lesson verifies that the supporting line lies below every allowed branch.

## Readiness evidence

Retain A4 and B4 with labelled units and the A3 error diagnosis. Separate an
independent answer from one produced after revealing hints. A correct lever-rule
calculation does not show why the selected endpoints are equilibrium. Do not
introduce the common-tangent formula before the addition/exchange lesson.
