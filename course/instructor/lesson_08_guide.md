# Instructor guide — binary TDB/tool parity

[Reading](../foundations/lesson_08_binary_tools.md),
[worksheet](../foundations/lesson_08_worksheet.md), meetings 19–20.
Timings are planned; they have not been observed with learners. Prepare printed model/parameter cards, full TDB,
comparison tables and separate answers. Keep tools optional after predictions.

| Minutes | Meeting 19 | Meeting 20 |
|---|---|---|
| 00–10 | Retrieve homogeneous/mixture and R1 phase set | Retrieve evaluate versus minimize |
| 10–22 | Explain one sublattice and parameter mapping | Explain region arrays, amounts and actual compositions |
| 22–40 | Worked A1 and pointwise output | Worked B1 both inventory sums |
| 40–45 | Break | Break |
| 45–70 | A2 (12), A3 (13) | B2 (12), B3 (13), optional cell if ready |
| 70–85 | A4 independent (8), feedback (7) | B4 independent (8), feedback (7) |
| 85–90 | Exit: one term and its model meaning | Exit: one detecting check beyond solver success |

Each meeting 90 minutes,85 contact/practice plus 5 break. If syntax dominates, use
highlighted printed entries and supplied outputs; preserve model/observable
reasoning. Defer extra coding, not the independent diagnostic. Record support
needed before fitting. No claim that learners already completed these meetings.

## Staged hints

| Task | Hint 1 | Hint 2 |
|---|---|---|
| A1 | Pure terms are weighted by 1−x and x. | RTq is generated; Ω term changes by 3200 J/mol at x=.2. |
| A2 | Reflect both composition and phase references. | BETA at .8 has the same weights on low/high pure references. |
| A3 | Only B reference changed by −1000. | Its weight at .5 is 1/2; no change in T coefficient. |
| A4 | Total H minus weighted same-phase pure H is mixing H. | Pure reference 7000; actual_x must be.5. |
| B1 | Multiply f by x for B and f(1−x) for A. | Repeated name does not imply identical composition. |
| B2 | Property evaluation and minimization answer different questions. | Difference≈2189.314 J/mol; minimum G, not minimum H. |
| B3 | A valid result can solve the wrong phase problem. | Check allowed phases and independent expected G. |
| B4 | f sums to 1; fx sums to z. | Multiply phase fractions and g by 4 mol for amounts and G. |

## Answers

A1 g=−9000+12000x+8314.5q+Ωx(1−x); at x=.2, Ω=0 gives −10760.595951,
Ω=20000 gives −7560.595951 J/mol. Do not duplicate ideal entropy in the TDB.
A2 both G=−10760.595951, H=3400 J/mol, S=14.160596 J/(mol K). Copying ALPHA's
pure-reference order into BETA would make another ALPHA-like branch, changing I2.
A3 ΔG=ΔH=−500 J/mol at .5; ideal entropy unchanged. Parser success is syntax,
not intended-model verification. A4 H−TS≈−3763.172 J/mol within display rounding;
Δhmix=12000−7000=5000 J/mol. Explicit point evaluation retains the homogeneous
state even if unstable; save actual_x, not only the requested number.

B1 I2 regions: B≈0.0955203765/0.4044796235, A≈0.4044796235/0.0955203765 mol.
R1 regions: B≈0.0845720035/0.4154279965, A reversed. Totals A=B=0.5 in both.
A dictionary keyed only by ALPHA would discard one R1 composition/amount. The g
column is the whole sample's equilibrium energy, not energy to sum for each row.
B2 difference 5000−2810.686236≈2189.313764 J/mol. Restricting ALPHA still permits
two ALPHA regions; G minimization selected them. Replacing the observable is wrong.
B3 reject as an I2 result: omitted BETA changes scope and expected G differs by about
1999.558 J/mol. Both balances passing does not certify the model or minimum.
B4 fα+fβ=1, B≈0.25, A≈0.75. At 4 mol: nα≈3.618336412, nβ≈0.381663588 mol;
G≈−43050.920068 J. Retain T,p,overall composition/amount basis, allowed phases,
parameter overrides, TDB/source/environment revision and actual outputs (any
three relevant fields with explanations). Same-model parity is implementation
verification, not an experimental or real-alloy validation.

## Readiness evidence

Retain A4/B4 and one planted-error explanation. Separate a valid state under the
wrong phase set from a broken mass/amount balance. Correct tool output alone does
not show that the learner understands the requested observable.
