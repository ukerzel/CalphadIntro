# Instructor guide — one meeting to repeat the unary model

Meeting 06. [Worksheet](../foundations/lesson_02_worksheet.md) and
[supplied output sheet](../foundations/lesson_02_offline_output.md).

## Preparation, entry and access

Learners should explain D4/E5 and the flat crossing energy before proceeding.
Supply the original TDB, worksheet, output sheet and prior phase tables locally
or on paper. Only the live route needs the existing Poetry setup. If it fails,
record the failure and use the supplied-output route for conceptual practice;
do not report a successful learner installation or execution.

Use the same model throughout. The output sheet covers GM for both branches,
HM and SM, equilibrium energy and one admissible crossing output. The core
lesson requires interpretation of these properties, not derivation by calculus.
Do not require new Python syntax beyond recognizing the short calls and the
name/amount loop. Explain imports, lists and condition names when first seen.

## 90-minute plan

| Minutes | Activity and board/output use |
|---|---|
| 00–10 | Retrieve equal-energy fraction explanation; same-model card |
| 10–22 | F1 record map; learner marks each h and −sT term |
| 22–40 | Work the 900 K prediction; show F2 load and both property calls separately; define GM/HM/SM and read one output row |
| 40–45 | Break |
| 45–70 | F2 compare all five rows/properties (8 min); F3 equilibrium and changes (10); F4 missing-phase/domain diagnosis (7) |
| 70–85 | F5 independently (8 min); feedback (7) |
| 85–90 | Collect F5 and execution-route labels; record topics for Clinic A |

Protect the break and guided practice. Use printed output if setup discussion
overruns. If concepts still need more time, record unfinished work and continue
in the clinic rather than declaring readiness. Timings are planned; they have not been observed with learners.

## Full TDB record map for reference

Map every non-comment line of the unchanged
[TDB](../foundations/one_component_model.tdb):

| Record / tokens | Meaning in this file; teaching limit |
|---|---|
| Lines beginning with $ | Comments: original synthetic model, dummy metadata, stated domain; comments do not enforce the domain |
| ELEMENT A BLANK 1.0 0.0 0.0 ! | Declare dummy A; BLANK reference-phase label; placeholder mass 1.0 and reference-state H298/S298 values 0.0/0.0. None is measured material evidence or a phase h/s parameter. No mass conversion is taught. |
| TYPE_DEFINITION % SEQ * ! | Declare the % type marker used below. This default record adds no extra Gibbs-energy term in the pinned parser. |
| PHASE SOLID % 1 1 ! | Name SOLID; use %; one sublattice (one kind of site) with site ratio 1 per formula unit |
| CONSTITUENT SOLID :A: ! | Only A occupies that sublattice; no composition variable |
| PARAMETER G(SOLID,A;0) 800 1000-10*T; 1200 N ! | Unary order-zero endmember: gS=1000−10T J/mol. Start/end interval 800/1200 K; N means no next interval; ! ends the record. |
| PHASE LIQUID % 1 1 ! | The same site-count convention for LIQUID |
| CONSTITUENT LIQUID :A: ! | Only A in LIQUID |
| PARAMETER G(LIQUID,A;0) 800 7000-16*T; 1200 N ! | gL=7000−16T J/mol with the same interval and termination syntax |

The parameters' constants are h=1000/7000 J/mol; coefficients of −T are
s=10/16 J/(mol K). No interaction, pressure, interface or magnetic term is
encoded here. The physical pressure is fixed by the contract/calls, not by the
comment or a pressure-dependent TDB term. Extrapolation permitted by a reader
is not additional physical validity. General sublattice theory is later work.

The metadata interpretation above follows the pycalphad 0.11.2 TDB reader and
its documentation.
Only the two parameter lines are required for the learner's core annotation.

## Staged hints and worked answers

| Task | Hint 1 | Hint 2 |
|---|---|---|
| F1 | Match each expression with h−Ts. | The constant is h; the negative T coefficient is s, not −s. |
| F2 | A property call is asked about one candidate. | Evaluate both even when one is higher; loading does not compare them. |
| F3 | Identify T, p and N before reading output. | At 1100 K compare −10000 with −10600; at 1000 K both branches are −9000. |
| F4 | Which states was the software allowed to consider? | Omitted LIQUID cannot appear; a numeric result outside the contract is not validated physics. |
| F5 | Reuse both equations with T=850. | Compute 1000−10×850 and 7000−16×850; distinguish phase evaluation from minimum selection. |

F1: liquid h=7000 J/mol, s=16 J/(mol K); 900 K predictions are
gS=−8000 and gL=−7400 J/mol. Loading the file supplies neither measurements
nor a stability determination.

F2: solid outputs −7000, −8000, −9000, −10000, −11000 J/mol;
liquid outputs −5800, −7400, −9000, −10600, −12200 J/mol.
Evaluating the higher liquid at 900 K is legitimate. It checks that branch's
expression without declaring it the equilibrium selection.
HM is 1000/7000 J/mol for solid/liquid at every tabulated temperature;
SM is 10/16 J/(mol K). The reference-state placeholder zeros do not override
the phase energy coefficients.

F3: 900 K equilibrium is SOLID, amount 1 mol, g=−8000 J/mol.
At 1100 K it is LIQUID, 1 mol, g=−10600 J/mol. The same Gibbs minimization and
conserved amount as Lesson 1 are now constructed from candidate phases and
conditions. At 1000 K, compare g=−9000 J/mol, nonnegative valid amounts and
total one mole; a unique phase fraction is not imposed.
Do not infer a discrepancy merely from a different admissible crossing output.

F4: SOLID-only at 1100 K gives −10000 J/mol within that restricted phase set,
but LIQUID gives −10600 J/mol and lowers the complete model's energy by
600 J/mol. The phase list changed the feasible states.
600 K lies outside the 800–1200 K teaching/verification domain. A raw API may
evaluate there, but that does not make the model valid there.

F5: at 850 K, gS=−7500 and gL=−6600 J/mol.
SOLID property evaluation gives −7500 J/mol; equilibrium with both allowed
phases gives all SOLID with the same molar energy. The terms are exactly the
two original parameter expressions, at p=100000 Pa and N=1 mol.
Accept energy comparison and amount balance as explicit checks.
A real-element calculation needs an appropriate assessed model and supporting
evidence; editing the species name supplies neither.

## Continuation record

Retain the route label, independent versus hinted F5 explanation, unresolved
units/constraint confusion, setup issues and unfinished tasks.
