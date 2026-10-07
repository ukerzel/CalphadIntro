# Instructor guide — one-parameter homogeneous fitting

[Reading](../foundations/lesson_09_fitting.md),
[worksheet](../foundations/lesson_09_worksheet.md), meetings 21–22.
Timings are planned; they have not been observed with learners. Prepare training/held-out cards and
residual columns. Keep the observable fixed before introducing the optimizer.

| Minutes | Meeting 21 | Meeting 22 |
|---|---|---|
| 00–10 | Retrieve homogeneous/total/mixing enthalpy | Retrieve residual definition and parameter versus state |
| 10–22 | Explain parameter, observation and squared objective | Explain forward-model swap and held-out isolation |
| 22–40 | Worked A1, then quadratic minimum | Worked B1 wrong-observable comparison |
| 40–45 | Break | Break |
| 45–70 | A2 (15), A3 (10) | B2 (12), B3 (13), optional cell if ready |
| 70–85 | A4 independent (8), feedback (7) | B4 independent (8), feedback (7) |
| 85–90 | Exit: what does this fit actually establish? | Exit: one missing-sensitivity or validation limit |

90 minutes each,85 contact/practice plus 5 break. Supply the quadratic sums if
arithmetic stalls, preserve residual units and observable reasoning. Optional
coding does not displace the held-out/identifiability task. Record support and
unresolved concepts before applying these ideas to a real-source audit.

## Staged hints

| Task | Hint 1 | Hint 2 |
|---|---|---|
| A1 | a=x(1−x); residual=prediction−observation. | Opposite errors can cancel in a sum, not in squared sum. |
| A2 | Predictions scale linearly with Ω. | Residuals double relative to 18000; objective quadruples. |
| A3 | State variables and model coefficients play different roles. | Fixed observed x cannot be optimized away. |
| A4 | Divide the two sums. | Ω*=20000 J/mol, inside [0,24000]. |
| B1 | Same-phase pure H reference is 7000. | Homogeneous 5000; wrong split differs by about 2189.314. |
| B2 | Estimation must finish before validation informs a decision. | A revised fit needs a new honest validation split/claim. |
| B3 | At pure ends x(1−x)=0. | B*T contribution cancels in G−T*dG/dT. |
| B4 | At .25, x(1−x)=.1875. | Ω=3750/.1875; predict at .4 with no refit. |

## Answers

A1 predictions 1620, 3780, 4500, 3780, 1620; residuals −180, −420, −500, −420, −180 J/mol;
SSE=667600 (J/mol)². Squared values are 32400, 176400, 250000, 176400, 32400.
A raw residual sum permits cancellation and is not this least-squares objective.
A2 predictions 1440, 3360, 4000, 3360, 1440; residuals −360, −840, −1000, −840, −360;
SSE=2670400 (J/mol)². Ω=18000/22000 each 667600, Ω=20000 zero. Bounds alone allow
many values and do not specify a fit. A3 equilibrium varied region amounts and
compositions at fixed model and overall inventories. The fit varies Ω while the
observation compositions,T,p,reference and data stay fixed. Changing supplied x
changes the observations/model question. A4 Ω*=20000 J/mol, interior bounds,
homogeneous mixing H relative to 1000+12000x. This is noiseless synthetic recovery,
not physical validation or an experimental uncertainty interval.

B1 hmix=12000−7000=5000; equilibrium result undershoots by 2189.313764 J/mol.
The error is substituting a G-minimized mixture property for homogeneous fixed x
`calculate` output. ALPHA-only phase selection does not prevent two compositions.
B2 predicted 3200, 4800, 4800, 3200 J/mol. Investigate errors against fixed data/model/
API; do not silently tune the parameter on the held-out set and retain an untouched
validation claim. B3 all Ω predictzero at pure ends, so sensitivity vanishes and
no unique estimate follows. For (A+BT)x(1−x), H=Ax(1−x); B cancels exactly and cannot
be identified by these enthalpies. A numerical optimizer might still return an
arbitrary B, which would not constitute recovery.
B4 Ω=20000 J/mol; at .4, prediction 4800 J/mol. B remains unidentifiable. Recovery:
retrieve a known synthetic generating coefficient. Same-model verification:
independent representations/algorithms reproduce the same stated observable.
Material validation: independent relevant observations test adequacy for an actual
material/domain, not supplied by this exercise.

## Readiness record

Retain A4/B4 plus B1's observable diagnosis. Label independent/supported/not yet.
A small optimizer objective is not a substitute for naming the model/data/units.
