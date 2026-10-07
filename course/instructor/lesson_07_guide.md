# Instructor guide — regular solution and stability

[Reading](../foundations/lesson_07_regular_solution.md),
[worksheet](../foundations/lesson_07_worksheet.md), meetings 17–18.
Timings are planned; they have not been observed with learners. Prepare reference/mixing cards, composition axes and separate
hint/answer cards. Model names and amounts must be explicit before curves.

| Minutes | Meeting 17 | Meeting 18 |
|---|---|---|
| 00–10 | Retrieve ideal/reference terms and fixed inventory | Retrieve curvature versus full slope |
| 10–22 | Add one constant interaction term, ALPHA only | Distinguish spinodal from binodal |
| 22–40 | Worked A1, then A2 setup | Worked B1 boundary diagram and B2 line |
| 40–45 | Break | Break |
| 45–70 | A2 (12), A3 (13) | B2 (12), B3/root controls (13) |
| 70–85 | A4 independent (8), feedback (7) | B4 independent (8), feedback (7) |
| 85–90 | Exit: changed term and unchanged reference | Exit: local/global evidence and numerical limit |

90 minutes each, 85 contact/practice plus 5 break. If algebra is slow, supply q and
curvatures, preserve balance and classification reasoning. Defer optional root
finder code and extra plotted temperatures; do not remove the independent attempt.
Record support needs.

## Staged hints

| Task | Hint 1 | Hint 2 |
|---|---|---|
| A1 | At 0.5, x(1−x)=1/4. | Δg=5000−T×5.763172. |
| A2 | Total h includes its weighted endmembers. | Δh=20000×0.05×0.95; total h uses href=1600. |
| A3 | Linear terms cancel between equal/opposite changes. | ε=.01; multiply curvature by ε²/2. |
| A4 | Interaction is not total g. | Δh=3200; total h=3400+3200. |
| B1 | Mark binodal and spinodal separately. | Between binodal/spinodal is positive-curvature metastability. |
| B2 | Lever rule still applies to same-structure regions. | fR≈0.030239278; line at z=.05 is −4497.197721. |
| B3 | Zero residual does not determine the gap. | Compare with high-precision noncentral reference endpoints and support/curvature. |
| B4 | New T changes both pairs of boundaries. | fR=(.2−.111251338)/(.888748662−.111251338). |

## Answers

A1 interaction 0 or 5000 J/mol. For R1, Δg=1542.096660 at 600 K and −2492.123903 J/mol
at 1300 K. Ω is a parameter,x the composition; aT scan changes the entropy-weighted
G contribution, not the fixed Ω term. A2 Δh=950 J/mol, Δs=1.650555 J/(mol K),
Δg=−40.332994 J/mol, total h=2550 J/mol. Constant Ω has no T derivative, so no excess
entropy; the ideal mixing entropy remains. A3 both overall fractions 0.5;
Δg≈−1.00226 J/mol. Linear slopes cancel by balance; full g′ need not vanish.
A4 Δh=3200, total h=6600 J/mol, Δgmix=703.642430 J/mol. Its sign is relative to the
unmixed reference, not a coexistence calculation or kinetic rate.

B1 z=.01/.99 stable; .05/.95 metastable; .5 unstable. The equilibrium two-region
mixtures inside the gap are globally stable states even where the homogeneous
state is unstable. At exact binodal/spinodal boundaries use equality/limit labels.
B2 fR≈0.030239278, fL≈0.969760722, overall B=.05, A=.95; equilibrium g=−4497.197721,
homogeneous excess 56.864727 J/mol. Positive local curvature says small fluctuations
raise G; it cannot rule out a finite composition separation that lowers G.
B3 central gapzero disagrees with actual 0.957934495, central curvature negative
and its affine-subtracted tangent sits above lower states. Full g′(.5)=12000 J/mol,
not zero. The near-critical error is an explicit numerical scope limit, not absence
of a physical gap; properties remain supported. Tiny residual alone is inadequate.
B4 z=.05 stable, .2 metastable, .5 unstable. fR≈0.114146582, fL≈0.885853418;
B=.2, A=.8. Equilibrium g=−6235.019724 J/mol and G≈−18705.059172 J for 3 mol.
Both region labels are ALPHA with different compositions; BETA is not allowed by R1.

## Readiness

Retain A4 and B4 explanations plus B3 rejection. Require the comparison's fixed
inventory and amount basis to be stated. Numerical output alone does not distinguish
metastability from instability. Preserve assistance labels and revisit Clinic B
if phase amounts or exchange meaning remain unclear before binary tool parity.
