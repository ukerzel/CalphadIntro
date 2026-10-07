# Instructor guide — Clinic A opening synthesis

Use the [Clinic A sheet](../foundations/clinic_a_thermo_unary.md) after
Lesson 2, meeting 07. Keep this answer key hidden until A4 has been
attempted independently. The paper route is complete; the
[supplied unary output](../foundations/lesson_02_offline_output.md) may be
shown only after learners predict A2; its temperature list does not include
A2's 950/1050 K cases. The P/Q card is a **new transfer
model**, not part of the fixed A/SOLID/LIQUID TDB. Timings are planned; they have not been observed with learners.

| Minutes | Activity | Detecting question |
|---|---|---|
| 00–10 | Retrieve closed/isolated, state versus transfer, fixed variables | What crosses the sample boundary? |
| 10–22 | Work A1 volume, $pV$, $TS$, four energies | Are $F$ and $G$ in J for this state? |
| 22–40 | Guide A2 two-branch table and crossing | Was the higher branch actually evaluated? |
| 40–45 | Break | — |
| 45–70 | Diagnose A3, introduce the P/Q table format without its answers | Is every compared candidate on one basis? |
| 70–85 | A4 independent transfer, then feedback | Are both P/Q branches and the mixture checked? |
| 85–90 | A5 exit and support record | What did the tool really minimize? |

This is 85 contact/practice minutes plus a five-minute break. Give extra
time in a later meeting if the unit or constraint decision remains unclear.
Keep the separate A1 state card from being attached to the unary phase
lines: their references and amount basis are not identified as the same.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1 | Draw heat/work arrows and convert cm³ to m³. | $pV=2$ J and $TS=7200$ J; then add/subtract. |
| A2 | Write both functions at each temperature before deciding. | $g_L-g_S=6000-6T$; at equality every $f_L$ has the same mixture energy. |
| A3 | Name the fixed conditions and candidate set before reading output. | One phase list excludes a lower allowed phase; an optimizer at a flat crossing cannot fix kinetics or unique fractions. |
| A4 | Compare P and Q on the same one-mole basis. | Their difference is $g_Q-g_P=5200-5T$; test 900, 1040 and 1100 K. |
| A5 | Match potential to constraints. | $T,p$ uses $G$; $T,V$ uses $F$ for the declared simple closed system. |

## Answers and rejection controls

**A1.** $q=+120$ J, $w_{\rm on}=-40$ J, so $\Delta U=+80$ J.
The state card has $20$ cm³ $=20\times10^{-6}$ m³;
$pV=(100000)(20\times10^{-6})=2$ J; $TS=(900)(8)=7200$ J.
Thus $H=12002$ J, $F=4800$ J and $G=4802$ J, with $G-F=2$ J.
The first-law transfer and the separate state card need not be the same
process. Heat/work cannot be substituted for $H$ or $S$. $F<G$ for this
single state does not rank two other phases or change the fixed-variable
rule. The A1 state model/reference are not linked to the unary lines.

**A2.** At 950 K, $g_S=1000-9500=-8500$ and
$g_L=7000-15200=-8200$ J/mol: SOLID is lower by 300 J/mol.
At 1050 K, $g_S=1000-10500=-9500$ and
$g_L=7000-16800=-9800$ J/mol: LIQUID is lower by 300 J/mol.
Solving $6000-6T=0$ gives 1000 K and common energy −9000 J/mol.
At this equality $g_{\rm mix}=(1-f_L)(-9000)+f_L(-9000)=-9000$
J/mol for every $0\le f_L\le1$; the fraction is not unique in this
no-interface model. A higher branch still checks the complete allowed
model and exposes a wrong parameter or omitted phase.

**A3.** (1) A1's $F$ and $G$ differ by $pV$ for one unrelated state;
lower $F$ than its own $G$ cannot choose the separate A/SOLID/LIQUID
candidate. At the declared fixed $T,p$ compare compatible $g_S$ and
$g_L$. (2) A single-phase LIQUID call only answers a restricted problem;
SOLID is lower at 950 K. (3) At 1000 K the idealized mixture energy is
flat in $f_L$, and neither energy line supplies a transformation rate.
(4) Convert both candidates to the same total amount, or compare molar
energies for the same conserved amount, and first require common model and
reference. A two-mole total from an unrelated model is not an allowed
competitor.

**A4.** At 900 K, $g_P=1500-8100=-6600$ and
$g_Q=6700-12600=-5900$ J/mol; P is lower. At 1100 K,
$g_P=1500-9900=-8400$ and $g_Q=6700-15400=-8700$ J/mol;
Q is lower. $g_Q-g_P=5200-5T=0$ at **1040 K**;
$g_P=g_Q=-7860$ J/mol. Mixtures with $f_Q=0.25$ and $0.75$
both have −7860 J/mol; no unique fraction is determined at equality.
At 900 K, the quarter-Q trial has
$0.75(-6600)+0.25(-5900)=-6425$ J/mol, above all-P's
−6600 J/mol. These functions use a different dummy component Z and
new parameters with no representation in the A-only TDB. Neither set
has fitted/validated real-material inputs or kinetic information.

**A5.** For this simple closed system, fixed $T,p$ and conserved amounts
select the compatible Gibbs-energy comparison; fixed $T,V$ and conserved
amounts select Helmholtz. Restricting a solver to one phase can make it
converge successfully to the best state **within that reduced candidate
set**, while a lower allowed phase in the declared model goes unchecked.
Judge independent reasoning from the attempt itself, not from the
worksheet self-mark.

## Handback into Lesson 3

Retain A4 and A5 with one concept to revisit. [Lesson 3](../foundations/lesson_03_composition.md)
adds a second atom species and distinguishes overall composition, region
composition and phase amount; it does not change the principle that
candidate energies and both component balances need common conditions.
If the learner still compares totals from unequal amounts or equates
heat with stored enthalpy, offer another supported arithmetic attempt
before introducing composition.
