# Clinic A — choose the energy, then compare the states

Meeting 07, after [Lesson 0](lesson_00.md),
[Lesson 1](lesson_01_one_component.md) and
[Lesson 2](lesson_02_same_model_pycalphad.md). Keep the
[instructor answers](../instructor/clinic_a_guide.md) closed until the
independent task. A calculator and this sheet are sufficient. The existing
[Lesson 2 supplied output](lesson_02_offline_output.md) is an optional check
of the same fixed functions at its **own** listed temperatures after the
paper answer; it does not give A2's 950/1050 K results. No installation or
new TDB is needed in this clinic.
All quantities are invented. No phase name or symbol here refers to Ni or
another real material.

**Exit goal:** separate state from transfer, keep units and amount bases,
choose the potential that matches fixed conditions, compare both allowed
unary phase energies, and transfer the method to an unfamiliar pair of lines.

## Shared reminder

For a closed sample, work **on** the sample is positive and
$\Delta U=q+w_{\rm on}$. At one state,
$H=U+pV$, $F=U-TS$ and $G=H-TS=F+pV$.
Heat $q$ and work $w$ describe a path, not stored state values. At fixed
$T,V$ and amounts compare appropriate Helmholtz energies; at fixed $T,p$
and amounts compare appropriate Gibbs energies. The first check is always:
**same system, conditions, conserved amount and reference?**

## 00–40 minutes — units and the fixed unary model

**A1 — worked state and transfer card (12 minutes).** A sealed sample
receives 120 J of heat and performs 40 J of work on its surroundings. With
the stated sign convention, $w_{\rm on}=-40$ J and
$\Delta U=120-40=80$ J. It is closed to matter but not isolated.
Separately, an invented **single state** has $U=12000$ J,
$p=100000$ Pa, $V=20$ cm³, $T=900$ K and $S=8$ J/K. Convert the volume
to m³, calculate $pV$, $TS$, $H$, $F$ and $G$, and check $G-F=pV$.
Do **not** compare this state's $F$ or $G$ with the phase energies below:
its amount/reference and physical model have not been tied to them.

**A2 — guided fixed-$T,p$ comparison (18 minutes).** Return to the
[fixed Lessons 1–2 contract](one_component_contract.md): one mole of
invented A atoms, $p=100000$ Pa, $800\le T\le1200$ K, with
$g_S=1000-10T$ and $g_L=7000-16T$ in J/mol. Evaluate **both** branches
at 950 K and 1050 K. Choose the lower Gibbs energy at each temperature.
Explain why the higher branch is still worth checking and find the exact
temperature where both are equal. At that crossing, is the liquid fraction
fixed by these two energy lines alone? Keep a one-mole total and
$f_S+f_L=1$.

**Break: 40–45 minutes.**

## 45–70 minutes — diagnose tempting wrong routes

**A3 — guided rejection cards.** For each proposal, name the broken
constraint, amount basis, reference or physical inference, then repair the
claim without rerunning a solver.

1. “The A1 sample has $F<G$, so the SOLID phase at 950 K must win.”
2. “At 950 K I evaluated only LIQUID. My program succeeded, so LIQUID is
   the stable phase of the **two-phase** model.”
3. “At 1000 K an optimizer printed 50% liquid, so the model uniquely
   predicts that fraction and how fast melting occurs.”
4. “A2 uses J/mol, so I can compare its $g_S$ for one mole directly with
   an unrelated total $G$ for two moles.”

Before the independent task, the instructor may show how to make a two-row
table with one column per candidate and a common unit. Do not put the new
functions below into the Lesson 2 TDB: they are a separate transfer card.

## 70–90 minutes — independent unfamiliar pair and exit

**A4 — fresh transfer (15 minutes; try unaided first).** A different,
completely invented one-component system Z has two allowed macroscopic
phases P and Q. At $p=100000$ Pa, one mole of Z and
$850\le T\le1150$ K, its *new* molar Gibbs functions are

$$g_P(T)=1500-9T,\qquad g_Q(T)=6700-14T\quad\mathrm{J/mol}.$$

Calculate **both** values at 900 K and 1100 K and select the lower phase.
Solve their exact crossing temperature and common energy. At that crossing,
calculate $g_{\rm mix}=(1-f_Q)g_P+f_Qg_Q$ for $f_Q=0.25$ and $0.75$,
with $0\le f_Q\le1$ and $f_P=1-f_Q$. Does this idealized model select a
unique fraction there? At 900 K, calculate $g_{\rm mix}$ for $f_Q=0.25$
and compare it with the all-P state. State two reasons these P/Q values
cannot be presented as a prediction from the A-only TDB or a real material.

**A5 — exit (5 minutes).** Circle $F$ or $G$ for a closed sample at fixed
$T,p$ and at fixed $T,V$. Explain in one sentence why an executable
calculation with the wrong phase list is not an equilibrium check of the
declared model. Mark A2–A4 unaided, with a hint, or not yet.

### Hints, only after an attempt

1. A1: $1\ \mathrm{cm}^3=10^{-6}\ \mathrm{m}^3$ and
   $1\ \mathrm{Pa\,m}^3=1\ \mathrm{J}$. Multiply $T$ by $S$ only after
   checking J/K.
2. A2: subtract $g_L-g_S=6000-6T$. Equal energy does not fix phase
   fractions when the full mixture energy is flat in $f_L$.
3. A3: a successful calculation only optimizes over the candidates it was
   given. Totals for different conserved amounts are not direct competitors.
4. A4: set $1500-9T=6700-14T$; at equality any allowed phase fraction
   has the same weighted Gibbs energy in this simplified no-interface model.
