# Answers and staged hints

Facilitator copy; offer hint 1, then hint 2 before revealing an answer. Learners
may use the reference sheet throughout. Equivalent explanations with correct
conditions, units and amount basis are welcome. Record support used rather than
turning these examples into a universal readiness score.

| Task | Hint 1 | Hint 2 |
|---|---|---|
| W0 | Separate matter from energy. | A sealed wall can still pass heat. |
| W1 | What is the sign of work done by the sample? | Work on it is negative; multiply p by V before adding U. |
| W2 | Divide reversible heat by absolute T. | J/K is entropy; multiply by K for energy. |
| W3 | Build H and TS before subtracting. | Fixed volume and fixed pressure select different potentials. |
| W4 | Substitute the same T in both expressions. | At the crossing, move the −T terms to one side: 6T=6000. |
| W5 | Match the constants to W4. | The input array changes T, not h or s. |
| W6 | Try the endpoint fractions first. | A negative fraction is forbidden even if its objective is lower. |
| W7 | Separate read, evaluate and select. | The solver cannot select a phase excluded from its candidates. |
| W8 | Multiply 1050 by each entropy separately. | Put report A in one energy unit; sum report B's fractions. |
| W9 | Which cards request data, and which assert a prediction? | A is not Ni; the model contains no boundary. |
| W10 | State conditions and basis before calculating. | Compare both branches; at equality check energy and balance, not one fraction. |

## W0–W3 · Energy and conditions

W0: the sample is closed, not isolated. No atoms pass the sealed boundary; heat
can cross from the furnace. Accept any labelled drawing that makes this clear.

W1(a): ΔU=80−10=70 J. It matches the worked example's ΔU but not its q.
W1(b): pV=100000×0.00002=2 J; H=1498+2=1500 J.
W1(c): the same initial/final states fix ΔU; q and work can differ while their
sum stays the same. H=U+pV always; ΔH=q at constant p needs the stated closed,
pressure-volume-work-only and mechanical-equilibrium assumptions.

W2: ΔS=900/300=3 J/K for the stated reversible isothermal transfer.
TS has units K×J/K=J. The sample's entropy can decrease if surroundings gain
sufficient entropy; the second-law constraint is on their isolated whole.
Do not accept “entropy is disorder” alone as a quantitative explanation.

W3: H=1500 J; TS=1200 J; F=298 J; G=300 J; G−F=2 J=pV.
(a) Minimize G at fixed T,p and fixed component amounts; (b) minimize F at
fixed T,V and fixed amounts, with the simple-work assumptions. H omits −TS.
For 2 mol, G=2×(−8000)=−16000 J. Comparing it directly with a one-mole total
changes the amount as well as the state; compare a common amount or molar basis.

## W4–W5 · Branches and plain code

| Task / T, K | gS, J/mol | gL, J/mol | Lower branch |
|---|---:|---:|---|
| W4 / 900 | -8000 | -7400 | SOLID |
| W4 / 1000 | -9000 | -9000 | Tie |
| W4 / 1100 | -10000 | -10600 | LIQUID |
| W5 / 950 | -8500 | -8200 | SOLID |
| W8 / 1050 | -9500 | -9800 | LIQUID |
| W10 / 975 | -8750 | -8600 | SOLID |

For W4: 6T=6000, T=1000 K, within our supported interval. The coefficient of T
is −s, so greater s gives a steeper decrease. A plot has T/K horizontally and
g/(J/mol) vertically; its two lines meet at (1000,−9000). The lower line switches
from solid to liquid. Keeping the higher branch exposes errors hidden by a
minimum-only comparison. No rate, time, diffusion or nucleation model is supplied.

W5: 1000 and 7000 are the h values; 10 and 16 are the s values. NumPy applies
the same hand arithmetic to each T. At 950 K both values are in the table above;
solid is lower by 300 J/mol. The output columns mean T, gS, gL and their minimum, not fractions.
Reading a supplied table is a legitimate paper route but is not personal execution.

## W6 · Minimization under constraints

The five energies at fL=0,0.25,0.5,0.75,1 are respectively
−8000, −7850, −7700, −7550, −7400 J/mol. All solid minimizes energy at 900 K.
fL=−0.2 implies a negative liquid amount, and fS=1.2; it is infeasible.

`c` holds objective coefficients; `A_eq` and `b_eq` require fS+fL=1;
`bounds` keep each fraction in [0,1]. These explicit bounds aid the physical
reading; SciPy's default bounds are already nonnegative, so omitting this
argument is not evidence that negative fractions are allowed.

At 1000 K the three trial fractions all give −9000 J/mol. Every fraction from
0 to 1 gives that value. Different solver fractions can both be valid: check
finite energy at the common minimum, nonnegative amounts and a total of one.
A solver's successful termination still needs physical and numerical checks.

## W7 · Same model, different representation

SOLID's constant term is 1000 J/mol and coefficient of −T is 10 J/(mol K);
LIQUID's are 7000 and 16. Loading only reads the model. `calculate` evaluates a
specified phase, including a higher-energy liquid at 900 K. `equilibrium` finds
the minimum for its model, allowed phases and imposed conditions. The branch
and minimum columns reproduce W4 and the saved SciPy result.

At 1000 K, LIQUID 1 is one allowed minimizer, not a unique prediction of amount.
HM/SM recover the same constants in W4. At 1100 K, excluding liquid gives solid
at −10000 J/mol, although allowing liquid gives −10600 J/mol. The restricted
answer cannot establish the unrestricted equilibrium. Database existence and
engine agreement do not validate a real material model.

## W8 · New temperature and planted errors

At 1050 K, gS=1000−10500=−9500 and gL=7000−16800=−9800 J/mol.
Minimum=−9800 J/mol, all liquid; fS,fL≥0 and fS+fL=1.

A: solid should be −8000 J/mol = −8 kJ/mol. Written literally, −8 J/mol is
higher than −7.4 kJ/mol=−7400 J/mol, contradicting the claimed winner and the
model. Correct the unit/value, then compare. B: 0.8+0.4=1.2, not 1. Renormalizing
silently changes the reported state; reject it and check the calculation's basis.
A low objective is insufficient if units, amount balance or candidates are wrong.

## W9 · Missing model inputs

Known today: card 1 only, and only for synthetic A. Needed inputs: cards 2, 3
and 6. Cannot conclude from today's model: cards 4 and 5. Accept an alternative
placement only if the learner explicitly distinguishes a question to investigate
from an asserted result; never accept the real 1000 K transition inference.

Example map: bulk composition → **assessed composition-dependent phase models**
→ boundary sites/exchange → **geometry, site capacity, exchange conditions and
boundary-state model/data** → competing structures. Each comparison needs a
consistent amount/area basis and reference. Do not infer enrichment magnitude,
direction or a transition from the two unary bulk lines.

## W10 · Exit reasoning and next practice

1. G=H−TS=U+pV−TS, fixed T,p with fixed component amounts and the simple bulk
   assumptions. U and H omit terms needed for those constraints. Fixed T,V
   instead selects F=U−TS.
2. At 975 K the table above gives solid lower by 150 J/mol. At 1000 K the
   energies meet at −9000 J/mol; the fraction is not fixed uniquely.
3. Variables fS,fL; minimize fSgS+fLgL; nonnegative fractions sum to one.
   −8 kJ for one mole is total −8000 J; dividing by 1 mol gives −8000 J/mol.
   They then agree. Correct the unit/basis before proposing a changed model.
4. Need a validated composition-dependent Ni–X bulk model plus boundary geometry,
   site/area basis, exchange/inventory conditions and a supported boundary model.
   One clearly explained missing input from each category meets this supported
   exit action; it does not establish independent defect-model competence.

Record each action as explained independently / explained with named support /
not yet explained. These descriptions guide follow-up; there is no validated
pass threshold. Discuss the README's next steps (Tasks 00–05), and point
unresolved condition, unit or conservation errors to Task 00 or the optional
opening lessons/Clinic A.
