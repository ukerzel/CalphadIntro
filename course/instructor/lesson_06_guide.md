# Instructor guide — chemical potentials, support and Clinic B

[Reading](../foundations/lesson_06_chemical_potential.md) and
[worksheet/clinic](../foundations/lesson_06_worksheet.md).
Timings are planned; they have not been observed with learners. Prepare total-versus-molar cards, blank tangent
axes, fixed-variable labels and separate hints/answers. Calculus identities are
derived on the board; finite steps provide the numerical foothold. Code optional.

| Minutes | Meeting 14 | Meeting 15 | Meeting 16 Clinic B |
|---|---|---|---|
| 00–10 | Retrieve n,x,total G; A1 starts | Retrieve μA,μB versus g′ | Retrieve composition and amount vocabulary |
| 10–22 | Explain finite difference and held variables | Explain tangent slope/intercepts | Re-explain one flagged balance/path confusion |
| 22–40 | Work A1, derive A2 identities slowly | Work B1 line, then B2 counterexample | Work one analogous balance/path example |
| 40–45 | Break | Break | Break |
| 45–70 | A2 (12), A3/cell (13) | B2 finish (10), B3 support proof (15) | C1 (9), C2 (8), C3 (8), with recorded hints |
| 70–85 | A4 independent (8), feedback (7) | B4 independent (8), feedback (7) | C4 independent (8), feedback (7) |
| 85–90 | Exit: what remains fixed? | Exit: a tangent versus global support | Exit: identify prerequisite support for Lesson 7 |

Three 90-minute meetings, each 85 contact/practice plus 5 break. If chain-rule algebra
stalls, keep explicit addition/exchange amounts and numerical identities; record
the unresolved derivation rather than claim mastery. In meeting 15 prioritize the
support/balance proof over optional code or extra derivative manipulations.
Clinic examples address the uncertainties learners actually show. Preserve independent attempts and the break.

## Staged hints

| Task | Hint 1 | Hint 2 |
|---|---|---|
| A1 | Adding B also changes total amount. | x after addition is 0.51/1.01, not 0.51. |
| A2 | μB includes g as well as slope. | μA=g−xg′; μB=g+(1−x)g′. |
| A3 | Differentiate G=ng, not g alone. | Resolve convergence over multiple h values. |
| A4 | x and 1−x weight different terms. | μA≈−10855.327; μB≈−10381.672. |
| B1 | c=g−xg′, m=g′. | Evaluate the line, not the phase curve, at 0 and 1. |
| B2 | Support means phase minus line is nonnegative. | BETA lies 5597.424 J/mol below the line. |
| B3 | Use nonnegative f to preserve inequality. | Sum f=1 and sum fx=z. |
| B4 | Common a+bx changes intercept and slope. | μA gains 432; μB gains 432−765. |
| C1 | Derive f from overall composition. | fβ=(0.4−0.2)/0.6=1/3. |
| C2 | Keep the separate supplied model values. | μA=−10500; μB=−8500. |
| C3 | Only one violating state is needed. | At 0.8 the line is −9400. |
| C4 | A solver state is not a scientific material validation. | Name allowed phases, constraints and independent evidence. |

## Answers

A1 addition:(nA,nB,n,x)=(0.5,0.51,1.01,0.504950495); exchange:
(0.49,0.51,1,0.51). μB is addition at fixed A,T,p; g′ is exchange at fixedtotal,T,p.
A2 μA=−14763.172233, μB=−2763.172233 J/mol. First-order ΔGaddition≈−2.763172 J,
ΔGexchange≈12 J. These are approximations for finite steps, not exact integrated
changes; distinct constraints explain different signs.
A3 the missing term is g plus the factor (1−x) on g′ for B addition. Step refinement
must show a resolved plateau before subtraction roundoff dominates.
A4 μA=−10855.327058, μB=−10381.671523 J/mol. Weighted sum≈−10760.595951 J/mol;
μB−μA≈473.655535 J/mol. Hold nB fixed for μA, nA for μB, nA+nB for exchange.

B1 ℓ=−14763.172233+12000x J/mol; ℓ(0)=−14763.172233, ℓ(1)=−2763.172233,
ℓ(0.8)=−5163.172233. Pure ALPHA values are −9000 and 3000; line intercepts are
partial molar quantities of the mixed state, not pure endmember values.
B2 gBETA−ℓ≈−5597.423718 J/mol, so support fails. B3 nonnegative amounts preserve
the inequality; total and B balance give ∑f(c+mx)=c+mz. A touching feasible split
attains that lower bound. A plot omits unsampled states and cannot prove the
inequality everywhere; analytical convexity plus extrema/endpoints checks do.
B4 new μA=−10330.730017, μB=−11095.730017 J/mol, slope −765 J/mol.
At z=0.25 all candidates shift by 240.75 J/mol. Endpoints/amounts unchanged if the
same shift affects all branches; shifting BETA alone changes the competition.

C1 fβ=1/3, fα=2/3; nβ=2/3, nα=4/3 mol. ALPHA:A16/15, B4/15 mol;
BETA:A2/15, B8/15 mol; totals A6/5=1.2, B4/5=0.8 mol.0.8 is BETA's internal
B fraction, not its share of the sample. C2 μA=−10500, μB=−8500 J/mol;
first-order addition ΔG=−17 J, exchange ΔG=4 J. C3 ℓ(0.8)=−9400 and g−ℓ=−1360.595951
J/mol: unsupported. No need to show tangency failure as well.
C4 feasible: nonnegative amounts plus both inventories. Lower among candidates:
energies compared for the same constraints. Global: support across every allowed
branch/composition plus a feasible state attaining the bound. Real-material
validation: eligible assessed model, domain/uncertainty and independent relevant
observations, none supplied by synthetic exercises. A finite grid can miss optimal
compositions while exactly balancing its selected regions.

## Readiness evidence

Retain A4, B4 and C4 explanations, C1 inventories and error diagnoses; distinguish
assistance before/during/after attempts. No universal numerical score
certifies readiness. If inventories/held variables/global support remain
unclear, arrange another supported attempt before nonideality; record the delivery
change.
