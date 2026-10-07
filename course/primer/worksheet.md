# Learner worksheet — one model through the day

Keep the reference sheet at the end beside your work. Use extra paper for your
answers. Predict first, then uncover supplied results. In W5 and W7 circle your
route: **paper / watched demonstration / ran code**. A supplied output is a
recorded author calculation, not evidence that you personally ran anything.

## W0 · Draw a boundary (09:00)

Draw a sealed specimen inside a furnace. Circle the specimen as the system and
label the surroundings. Can atoms cross its boundary? Can heat? Is it closed or
isolated? Write one question you hope CALPHAD might help answer. No grading.

## W1 · U and H (09:15)

Internal energy U is a property of the sample's state. Heat q and work are energy
transfers along a process. Take work **on** the sample as positive:
$\Delta U=q+w_{\mathrm{on}}$. A sample receiving 100 J and doing 30 J of work
has $\Delta U=100-30=70$ J. Heat is not another stored state variable. [1]

Enthalpy is $H=U+pV$. Pressure times volume has energy units:
$1\ \mathrm{Pa\,m^3}=1\ \mathrm{J}$. At constant pressure, for a closed sample
with only pressure-volume work in mechanical equilibrium with that pressure,
$\Delta H=q_p$. This limited relation does not define H as stored heat. [1]

Worked state: U=999 J, p=100000 Pa, V=0.00001 m³. Thus pV=1 J and H=1000 J.
This is an invented definition exercise, **not volume data for the A model**.

Pair task: (a) receive 80 J and do 10 J of work: find ΔU; (b) for a different
invented state, U=1498 J, p=100000 Pa, V=0.00002 m³: find pV and H.
(c) Must two processes with the same ΔU have the same heat transfer? Explain.

## W2 · Entropy (10:00)

Entropy S has units J/K. For a reversible heat transfer at constant absolute
T, $\Delta S=q_{\mathrm{rev}}/T$. A reversible 600 J input at 300 K gives
ΔS=2 J/K. Do not use actual irreversible heat divided by T as a general formula
for entropy change. Entropy is a state property, not a synonym for heat. [2]

Try a reversible 900 J input at 300 K. What is ΔS? What are the units of TS?
Discuss: when a sample loses entropy, must the second law be violated? Consider
the entropy change of sample plus surroundings, with that whole isolated.

## W3 · Choose the potential (10:45)

For simple bulk systems with component amounts fixed and no additional surface,
elastic, electrical or magnetic work constraints, equilibrium minimizes F at
fixed T,V and G at fixed T,p. An isolated whole at fixed U,V and component amounts
maximizes S. $F=U-TS$, $G=H-TS=F+pV$. Conditions choose the comparison. [3]

Worked state: W1's U=999 J, H=1000 J, now T=300 K, S=10 J/K.
TS=3000 J; F=−2001 J; G=−2000 J. Check G−F=pV=1 J.
Negative energy is allowed; compare consistent references and the same amounts.

Fill this map for W1(b)'s U=1498 J, pV=2 J at T=300 K, S=4 J/K:

| Step | Your value and unit |
|---|---|
| U + pV → H | ____________________ |
| T × S | ____________________ |
| U − TS → F | ____________________ |
| H − TS → G | ____________________ |
| G − F, compared with pV | ____________________ |

Choose a criterion and justify it: (a) closed bulk sample at fixed T,p;
(b) closed bulk sample at fixed T,V. Why does choosing the smallest H alone
miss something? If g=−8000 J/mol, find total G for 2 mol; explain why comparing
that directly with a one-mole total would be misleading.

## W4 · Two lines, one invented component (11:30)

Our entire phase model is here. A is invented, not Ni. Closed bulk, one mole of
A atoms, p=100000 Pa, 800–1200 K, only SOLID and LIQUID. Constant within-phase
h and s imply zero heat capacity there; pressure dependence and interfaces are
absent. There is no kinetics or real-material prediction. [4]

| Phase | h, J/mol | s, J/(mol K) | g=h−Ts, J/mol |
|---|---:|---:|---|
| SOLID | 1000 | 10 | 1000−10T |
| LIQUID | 7000 | 16 | 7000−16T |

Worked at 900 K: gS=1000−9000=−8000 J/mol;
gL=7000−14400=−7400 J/mol. Solid is lower by 600 J/mol.
Fill the remaining rows **before** reading answers. The saved tables in W5
and W7 repeat these values: keep those pages folded or covered until W4 is done.

| T, K | gS, J/mol | gL, J/mol | Lower phase or tie |
|---:|---:|---:|---|
| 900 | −8000 | −7400 | SOLID |
| 1000 | __________ | __________ | __________ |
| 1100 | __________ | __________ | __________ |

Sketch both lines from this table; label axes and units. Solve
1000−10T=7000−16T for their crossing. Why does the higher-entropy phase's line
fall faster? Why is comparing both branches a better model check than seeing
only the chosen minimum? Does equilibrium tell you a melting time?

Optional full-size source plot (the table/your sketch supplies the paper route):
[full labelled vector plot](../foundations/figures/one_component_gibbs.svg).

## W5 · Recognize the arithmetic in code (13:15)

The following is a verbatim code cell from Lesson 1. It supplies an array of
kelvin values, evaluates both expressions and prints one row per temperature, including the lower value.
`np` names NumPy; `column_stack` places columns beside one another; `minimum` selects the lower value in each row.
Read and annotate it on paper; writing a program is not an entry requirement.

<!-- excerpt: plain-array -->
```python
import numpy as np

temperatures = np.array([800.0, 900.0, 1000.0, 1100.0, 1200.0])
solid = 1000.0 - 10.0 * temperatures
liquid = 7000.0 - 16.0 * temperatures
lowest = np.minimum(solid, liquid)
print(np.column_stack([temperatures, solid, liquid, lowest]))
```

Before uncovering the table, predict the 1100 K row and circle the constants
that express the **model**, as distinct from the input temperatures. On paper,
change the input to 950 K while keeping the model constants; predict both values.
A facilitator may demonstrate the same substitution. Answers follow in the
separate sheet; the complete supplied output is here for annotation:

**Saved output, columns T/K, gS/(J/mol), gL/(J/mol), minimum/(J/mol); display rounded to integers:**

| T | gS | gL | Minimum |
|---:|---:|---:|---:|
| 800 | -7000 | -5800 | -7000 |
| 900 | -8000 | -7400 | -8000 |
| 1000 | -9000 | -9000 | -9000 |
| 1100 | -10000 | -10600 | -10600 |
| 1200 | -11000 | -12200 | -12200 |

Underline the row agreeing with your hand calculation. Changing h or s would
change the model; changing only T asks another question of the same model.

## W6 · What may an optimizer change? (14:00)

Let fL be the liquid mole fraction and fS=1−fL. Both must lie between 0 and 1.
These are phase amounts divided by the total, not image-area fractions.
The objective to minimize at fixed T,p is
$g_{\mathrm{mix}}=(1-f_L)g_S+f_Lg_L$ subject to $0\le f_L\le1$.
This is two macroscopic phases of **one component**, not an A–B atomic solution;
we neglect their interface. The model parameters stay fixed.

At 900 K, gmix=−8000+600fL J/mol. Complete:

| fL | 0 | 0.25 | 0.5 | 0.75 | 1 |
|---|---:|---:|---:|---:|---:|
| gmix, J/mol | −8000 | ______ | ______ | ______ | −7400 |

Which fraction minimizes energy? At fL=−0.2 the formula gives −8120 J/mol;
why must an optimizer reject it even though it is lower?

Read this **argument card**, not runnable code:
`c=[gS,gL]`; `A_eq=[[1,1]]`; `b_eq=[1]`; `bounds=[(0,1),(0,1)]`.
Match each to objective, amount balance or physical bounds. The variables are
`[fS,fL]`. SciPy's `linprog` solves this linear problem; the complete Lesson 1
implementation checks success before using a returned solution. [5]

**Saved SciPy result at 900 K:** fractions SOLID=1, LIQUID=0;
minimum=−8000 J/mol. (Signed floating-point zero is still zero.)
At 1000 K, try fL=0, 0.5 and 1 by hand. Can two solvers return different valid
fractions there? State the energy and balance checks that still matter.

## W7 · Load, evaluate, minimize (14:45)

The course's tiny TDB file stores the same expressions. These are its exact
energy records, not a complete database file:

```text
PARAMETER G(SOLID,A;0) 800 1000-10*T; 1200 N !
PARAMETER G(LIQUID,A;0) 800 7000-16*T; 1200 N !
```

Underline each h and coefficient of −T. `800` and `1200` bound this declared
interval; `!` ends a record. The file's other lines name the dummy component
and phases. Placeholder element metadata do not provide a real material.

Follow three distinct actions with the full TDB file:

| Action | API name | What it does here |
|---|---|---|
| Load | `Database` | Read the two phase models; no equilibrium yet |
| Evaluate | `calculate` | Compute a phase property, even for the higher branch |
| Minimize | `equilibrium` | Use allowed phases/components and imposed conditions |

Conditions are T in K, p=100000 Pa, N=1 mol; candidates are A, SOLID and LIQUID.
`GM` is molar Gibbs energy in J/mol, `HM` molar enthalpy in J/mol and `SM` molar
entropy in J/(mol K). In this N=1 route phase amounts numerically equal fractions.
Do not assume arbitrary total-N support or general array shapes from this example.

**Saved pycalphad output from the course's own run:**

| T, K | SOLID GM, J/mol | LIQUID GM, J/mol | Minimum GM, J/mol | Returned used phase amount, mol |
|---:|---:|---:|---:|---|
| 900 | -8000 | -7400 | -8000 | SOLID 1 |
| 1000 | -9000 | -9000 | -9000 | LIQUID 1 |
| 1100 | -10000 | -10600 | -10600 | LIQUID 1 |

For both phases at each listed T, HM is [1000,7000] J/mol and SM is [10,16]
J/(mol K), in SOLID/LIQUID order. At 1000 K the returned LIQUID 1 is just one
minimizer; all balanced nonnegative mixtures have the same energy.

Pair task: connect each TDB term to W4, compare both GM columns with your table,
and explain why evaluating liquid at 900 K is valid. Can loading a database
alone establish the equilibrium? Predict what happens if LIQUID is excluded at
1100 K, then uncover: **saved SOLID-only result = −10000 J/mol, SOLID 1**.
Why is that not the unrestricted minimum? No database writing is needed today.

## W8 · Consolidate and catch an error (15:30)

At **1050 K**, calculate both Gibbs energies, select the lower phase, write the
allowed fraction range and amount balance, and predict the minimum energy.

Two fictional reports deliberately contain errors. Correct each and explain:

- A: at 900 K, “gS=−8 J/mol, gL=−7.4 kJ/mol, so solid wins.”
- B: at 900 K, “fS=0.8, fL=0.4 satisfies the one-mole balance.”

Does observing a low objective alone establish a valid equilibrium result?

## W9 · A research map, not a new calculation (16:00)

A real Ni–X question adds a second element. We would need an assessed model
for the chosen components, phases, temperature/composition range and conditions.
A grain-boundary question also needs a boundary description, sites/area basis,
exchange or closed-inventory conditions, and a model with supporting evidence.
Comparing competing boundary structures needs compatible thermodynamic references
and validation. Our unary bulk lines supply none of those data. [4]

Sort the cards into **known from today's model**, **model/input needed**, or
**cannot conclude from today's model**, and explain your placement:

1. A's two branches cross at 1000 K.
2. A suitable Ni–X bulk Gibbs model with provenance and validity range.
3. Boundary geometry/site inventory and segregation/structural-state energies.
4. The solute concentration at an actual Ni grain boundary.
5. A real boundary changes structure at 1000 K because the A lines cross there.
6. Whether solute may exchange with a large reservoir or a finite closed sample.

Draw the question sequence: bulk composition → boundary sites/exchange →
competing boundary structures. Add one missing input under each arrow.
No segregation equation, binary equilibrium or real transition is calculated.

## W10 · Supported exit (16:30)

Use the reference sheet and calculator if useful, but first try without the
answer sheet. Mark any hint, partner help or supplied result you use. This is
a conversation about next practice, not a certification score.

1. Choose the equilibrium potential for a closed bulk sample at fixed T,p.
   Distinguish it from H and U; what changes if T,V are fixed instead?
2. At **975 K**, find gS and gL, identify the lower branch and explain the
   crossing at 1000 K. Does the crossing fix a unique phase fraction?
3. State variables, objective and amount constraint. A report labels an energy
   “−8 kJ” for one mole and compares it directly with “−8000 J/mol.”
   State the unit/basis conversion needed. Is the unit mistake evidence of a
   different thermodynamic model?
4. Why can these lines not predict Ni–X grain-boundary enrichment or a structural
   transition? Name at least one missing bulk input and one missing boundary input.

Feedback: which explanation needed help? Which condition or unit will you check
first next time? Agree a continuation using the README routes.

## Keep-beside-you reference sheet

| Symbol / word | Meaning and units |
|---|---|
| System / closed / isolated | Chosen matter / no matter exchange / no matter or energy exchange |
| U | Internal energy of sample, J; ΔU=q+work on sample |
| H | Enthalpy, U+pV, J; not a universal synonym for heat |
| S; T | Entropy, J/K; absolute temperature, K |
| F (also A) | Helmholtz energy, U−TS, J; fixed T,V comparison |
| G | Gibbs energy, H−TS, J; fixed T,p comparison |
| n; g=G/n | Amount, mol of atoms; molar Gibbs energy, J/mol |
| h; s | Molar enthalpy J/mol; molar entropy J/(mol K) |
| fS, fL | Nonnegative mole fractions of phases, summing to one |
| Equilibrium | Minimum appropriate potential among allowed states under constraints; not a rate |
| Model / algorithm / output | Physical expressions and parameters / calculation procedure / numerical result to check |
| CALPHAD | CALculation of PHAse Diagrams; phase models and equilibrium calculations, with model assessment requiring evidence |

The potential criteria assume simple bulk conditions and fixed component amounts
as in W3. Only the synthetic A model W4 is used for numerical phase comparison.
Its 1000 K crossing fixes equal energies, not a unique fraction.

Sources for the condensed explanations:
[1] R. Jaramillo, MIT 3.020, Lecture 3, 2021,
[First Law](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l03.pdf).
[2] R. Jaramillo, MIT 3.020, Lecture 5, 2021,
[Entropy](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l05.pdf).
[3] R. Jaramillo, MIT 3.020, Lecture 6, 2021,
[Thermodynamic potentials](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l06.pdf).
No DOI is listed for these lecture notes; wording/examples here are original.
[4] The course's [synthetic model contract](../foundations/one_component_contract.md)
defines our assumptions.
[5] SciPy developers, [linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).
API roles are also documented by the pycalphad developers:
[phase evaluation](https://pycalphad.org/docs/latest/examples/LegacyEnergySurface.html)
and [equilibrium](https://pycalphad.org/docs/latest/examples/EquilibriumWithOrdering.html).
