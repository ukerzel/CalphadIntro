# Lesson 0 worksheet — energy accounts before software

Meetings 01–03. Bring paper
and a calculator.
No code, derivatives or thermodynamic database is needed. Use the
[reading](lesson_00.md) one section at a time. Answers and two levels of hints
are in the [instructor guide](../instructor/lesson_00_guide.md).

You should be able to multiply, divide, keep units and order negative numbers.
If $-8000<-7400$ is unfamiliar, put both numbers on a number line with the
instructor before comparing energies. All numbers here are invented.

## Meeting 01 — follow energy across a boundary

Read sections 0.1–0.2 only. A **system** is the matter inside your chosen
boundary. **Surroundings** are everything outside. A closed system keeps its
matter; an isolated system exchanges neither matter nor energy.

| Symbol | Meaning | Unit / convention |
|---|---|---|
| $U$ | Internal energy of the whole sample | J |
| $\Delta U$ | Final $U$ minus initial $U$ | J; $\Delta$ means change |
| $q$ | Energy transferred as heat | J; positive into the sample |
| $w_{\mathrm{on}}$ | Energy transferred as work | J; positive work on the sample |

For a closed sample with no change in motion or height of the whole sample,
$\Delta U=q+w_{\mathrm{on}}$. Heat and work describe a transfer, not stored
state quantities. Use this sign convention in every row. [Reading, sources 1–2]

**A1 — worked together.** A sealed sample receives 100 J as heat and does
30 J of work on its surroundings. Draw the boundary and arrows. Label
$q=+100$ J and $w_{\mathrm{on}}=-30$ J. Then $\Delta U=100-30=70$ J.
It is closed, but not isolated.

**A2 — guided practice.** Keep the same type of closed sample at rest.
For each process, sketch the arrows first, then fill all three signed entries.

| Process | $q$, J | $w_{\mathrm{on}}$, J | $\Delta U$, J |
|---|---|---|---|
| (a) Receives 80 J as heat and does 10 J of work | … | … | … |
| (b) Loses 40 J as heat; surroundings do 15 J of work on it | … | … | … |
| (c) No heat crosses; surroundings do 25 J of work on it | … | … | … |

Explain why (c) is not isolated. If A1 and A2(a) connect the same initial and
final states, must their separate heat transfers agree?

**A3 — diagnose.** A colleague writes, “The sample stores 100 J of heat and
30 J of work, so its internal energy increased by 130 J in A1.”
Correct the language and the calculation. State what initial information would
be needed to report its final $U$, rather than just $\Delta U$.

**A4 — independent exit.** A closed sample at rest loses 50 J as heat while
20 J of work is done on it. Give $\Delta U$ with units, explain each sign and
say whether “closed” guarantees constant $U$. Leave your arrows beside the answer.

## Meeting 02 — enthalpy first, entropy second

Read 0.3, pause, then 0.4. These are two separate ideas.

| Symbol | Meaning | Unit |
|---|---|---|
| $p$ | Pressure | Pa |
| $V$, $\Delta V$ | Sample volume, its change | m$^3$ |
| $H=U+pV$ | Enthalpy of the sample | J; Pa m$^3$ = J |
| $T$ | Absolute temperature | K |
| $S$, $\Delta S$ | Sample entropy, its change | J/K |
| $q_{\mathrm{rev}}$ | Heat transferred on a reversible path | J |

A reversible path is an ideal path that can be reversed without a net change
to the system and surroundings. Only for such a heat transfer at constant $T$
do we use $\Delta S=q_{\mathrm{rev}}/T$ here. Actual irreversible heat divided
by temperature need not equal the sample's entropy change.

**B1 — worked in two stages.** First, $U=999$ J, $p=100000$ Pa and
$V=0.00001$ m$^3$ give $pV=1$ J and $H=1000$ J.
Separately, a hypothetical reversible process at constant 300 K transfers
600 J of heat into a system: $\Delta S=600/300=2$ J/K.
These are definition exercises, not states or processes of the later unary
phase model. We do not assume that the two exercises describe the same sample.

**B2 — guided enthalpy account.** For a second invented sample, $U=1998$ J,
$p=100000$ Pa, $V=0.00002$ m$^3$. Find $pV$ and $H$.
In a separate closed-system process, hold $p=100000$ Pa fixed, allow only
pressure–volume work at that same external pressure, and let
$\Delta V=0.00002$ m$^3$ and $q=50$ J. The initial and final sample pressures
equal this pressure. Use $w_{\mathrm{on}}=-p\Delta V$.
Find $w_{\mathrm{on}}$, $\Delta U$, and $\Delta H=\Delta U+p\Delta V$.
Explain why $\Delta H=q$ in this process. Would constant pressure alone be
sufficient if electrical work were also supplied?

**B3 — guided entropy account.** A different reversible process removes
900 J of heat from a sample at a constant 300 K. Find $\Delta S$.
For another process, the sample's entropy change is supplied as $-2$ J/K and
its surroundings' change as $+3$ J/K. Treat their combination as isolated.
Find the total entropy change. Is the negative sample change alone grounds
for rejecting the process under the second law?

**B4 — diagnose.** Someone uses 27 in $\Delta S=600/T$ because a thermometer
reads 27 °C. Name the temperature scale needed; do not use that calculation
as a physical answer. Then explain the additional missing condition if the
600 J was actual heat from an irreversible process.

**B5 — independent exit.** Compute $H$ for $U=1497$ J, $p=100000$ Pa,
$V=0.00003$ m$^3$. Separately, compute $\Delta S$ for 800 J of reversible heat
input at constant 400 K. Attach the correct units to both results and name one
reason why $H$ is not “heat stored in a sample.”

## Meeting 03 — choose a potential, then compare equal amounts

Read 0.5–0.8. Section 0.9 supplies only the final bridge to Lesson 1.

| Symbol | Meaning | Unit / relation |
|---|---|---|
| $F$ (also $A$) | Helmholtz energy | J; $F=U-TS$ |
| $G$ | Gibbs energy | J; $G=H-TS=F+pV$ |
| $n$ | Amount of atoms | mol |
| $g$, $h$, $s$ | Gibbs energy, enthalpy, entropy per mole of atoms | J/mol, J/mol, J/(mol K) |

Here the sample is simple bulk matter, with fixed amounts of each component.
We leave out extra electrical, magnetic, elastic and interface work effects.
An **allowed state** must satisfy the imposed conditions and amount constraints.
Among those states, equilibrium uses:

| Imposed conditions | Criterion |
|---|---|
| Isolated; fixed $U,V$ and component amounts | Maximum $S$ |
| Fixed $T,V$ and component amounts | Minimum $F$ |
| Fixed $T,p$ and component amounts | Minimum $G$ |

**C1 — worked potential map.** With $U=999$ J, $pV=1$ J,
$T=300$ K and $S=10$ J/K, calculate $H=1000$ J and $TS=3000$ J.
Then $F=-2001$ J and $G=-2000$ J. Check $G-F=1$ J.
Explain why $F$ and $G$ are different quantities even for the same state.

**C2 — guided second map.** Use $U=1998$ J, $pV=2$ J,
$T=400$ K, $S=6$ J/K. Find $H,TS,F,G,G-F$.
For each separate situation, choose the row of the condition table:
(a) a sealed rigid vessel held at a fixed temperature;
(b) a closed sample at fixed temperature and pressure;
(c) an isolated sample with fixed volume.
State both what is fixed and whether to minimize or maximize.
No assertion is made that the illustrative 400 K state describes our phase model.

**C3 — amount and error diagnosis.** At the same $T,p$ and with a common
reference, phase X has $g_X=-8000$ J/mol; phase Y has $g_Y=-7400$ J/mol.
These labels stand for candidate homogeneous phases of the same component.
(a) Compute $G_X$ for 2 mol and $G_Y$ for 3 mol.
(b) A colleague chooses Y because its total is more negative. Correct the
comparison by calculating both totals for 2 mol.
(c) Another colleague chooses the smaller $G$ for a problem imposing fixed
$T,V$. Explain what information that problem needs instead.

**C4 — bridge, with guidance available.** Our next model is one invented
component A, one mole of atoms, fixed $p=100000$ Pa and only 800–1200 K.
Its candidate phases are SOLID ($h=1000$, $s=10$) and LIQUID
($h=7000$, $s=16$), in J/mol and J/(mol K).
Use $g=h-Ts$ at 900 K to compare them. Explain why choosing the smaller
enthalpy alone would omit part of the comparison. Predict qualitatively how
the larger liquid entropy affects its Gibbs energy as temperature rises.
We will calculate and graph the full temperature dependence in Lesson 1.
These constant $h,s$ imply zero heat capacity within each modeled phase;
they are a teaching simplification and do not describe a real element.

**C5 — independent exit.** For the same two phase expressions at 1100 K,
calculate each $g$ and choose the lower one. State conditions, amount basis and
units. Explain why this calculation cannot give a transformation time.
If the bridge still needs hints, retain this as supported practice and revisit
it at the start of Lesson 1; do not record independent readiness.

## Before Lesson 1

Keep your three exit tasks. Explain heat versus $U$, $H=U+pV$, the temperature
and reversible-path assumptions in the entropy exercise, the potential chosen
by each constraint, and why comparisons need the same amount basis.
Ask for another changed-number attempt on any unclear part; speed is not the
criterion. No optional derivation is a prerequisite.

The [source lesson](lesson_00.md#sources-and-further-reading) supplies the
primary definitions and references. The [unary contract](one_component_contract.md)
governs C4–C5 only. All other numerical states/processes are independent
definition exercises; they do not extend the unary model outside 800–1200 K.
