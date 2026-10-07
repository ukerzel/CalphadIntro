# Lesson 2 worksheet — the same equations in a database

Meeting 06. Bring your two phase curves and fraction explanation
from Lesson 1. Use the [reading](lesson_02_same_model_pycalphad.md),
[model contract](one_component_contract.md) and
[instructor guide](../instructor/lesson_02_guide.md).

One invented component A; closed bulk sample with one mole of atoms;
$p=100000$ Pa, $800\le T\le1200$ K. SOLID has $g_S=1000-10T$ and LIQUID
has $g_L=7000-16T$, in J/mol. These are the same models as Lesson 1.
They contain no material assessment, composition dependence, interface or
kinetic model. No symbol or phase name makes A into a real element.

The computer route uses the [existing setup](README.md#running-the-examples);
run the three cells in order in one Python session from the repository root.
The paper route annotates the same cells and uses the
[supplied output sheet](lesson_02_offline_output.md) after predicting values.
Mark your route as **ran / observed demonstration / supplied output**.

## F1 — worked equation-to-record map

TDB means the text database format used here. Read the two records from
the [original file](one_component_model.tdb):

~~~text
PARAMETER G(SOLID,A;0) 800 1000-10*T; 1200 N !
PARAMETER G(LIQUID,A;0) 800 7000-16*T; 1200 N !
~~~

The first says: phase SOLID, the A endmember (all sites occupied by A),
Gibbs-energy expression 1000−10T, over the declared 800–1200 K interval.
The constant 1000 carries J/mol; the coefficient 10 carries J/(mol K).
The ! terminates the record; N says there is no next temperature segment.
The ;0 labels parameter order zero for this unary endmember, not a phase
fraction or temperature. There is no A/B interaction in this one-component file.

Underline the liquid enthalpy term and circle the term containing its entropy.
Fill the liquid values: h=… J/mol, s=… J/(mol K).
Predict both g values at 900 K before loading the file.
The other declarations identify phases and site occupants; the instructor's
full record map is available for reference, with no need to memorize the grammar.

## F2 — loading and evaluating are separate actions

First load the model and name the candidates:

~~~python
from pycalphad import Database, calculate, equilibrium, variables as v

database = Database("course/foundations/one_component_model.tdb")
components = ["A"]
phases = ["SOLID", "LIQUID"]
~~~

This cell produces no equilibrium result. Next evaluate both branches:

~~~python
temperatures = [800., 900., 1000., 1100., 1200.]  # K
solid_result = calculate(database, components, "SOLID",
                         T=temperatures, P=100000., output="GM")
liquid_result = calculate(database, components, "LIQUID",
                          T=temperatures, P=100000., output="GM")
print(solid_result.GM.values.reshape(-1))
print(liquid_result.GM.values.reshape(-1))
~~~

GM is molar Gibbs energy, J/mol. Each result contains named arrays;
.values gives the array and .reshape(-1) displays it in one row for this
tiny unary case. Do not generalize that flattening without inspecting the
dimensions of a larger calculation.

Compare every value with your Lesson-1 hand table. Why is a liquid value
returned at 900 K even though solid is favored? If only the lower branch
agreed, what would remain unchecked?

The supplied sheet also reports HM (molar enthalpy, J/mol) and SM (molar entropy,
J/(mol K)) for both phases. Compare them with the two coefficient pairs.
Here they are constant with T; they are not additional fitted observations.
Their software derivation need not be introduced as calculus in this meeting.

## F3 — equilibrium adds allowed choices and conditions

Predict the preferred phase and energy at 900 K, then run or annotate:

~~~python
conditions = {v.T: 900., v.P: 100000., v.N: 1.}
answer = equilibrium(database, components, phases, conditions)
print(float(answer.GM.values.squeeze()))
for phase, amount in zip(answer.Phase.values.reshape(-1),
                         answer.NP.values.reshape(-1)):
    if phase:
        print(phase, float(amount))
~~~

The condition names specify temperature, pressure and amount. With N=1 mol,
the printed phase amounts numerically equal mole fractions. Empty phase-name
entries are unused result slots and are skipped. The loop pairs each used phase
name with its reported amount; it does not choose the stable phase itself.

Change 900 to 1100 in the conditions and rerun this third cell. What is the
same as Lesson 1's optimizer, and what did the library construct for you?
Then compare the supplied 1000 K result. Name what must agree at the crossing,
and what need not agree between programs.

## F4 — diagnose a restricted calculation

A colleague calculates at 1100 K using only phases=["SOLID"].
It returns SOLID with molar energy −10000 J/mol. They conclude the original
two-phase model favors solid. Use the known liquid branch to reject this
conclusion. Name the input that changed and the physically different question
the calculation answered. A successful call cannot include an omitted candidate.

Someone else runs the raw API at 600 K and gets a number. Explain why this does
not extend the course model's valid domain. The helpers enforce the
800–1200 K contract; raw calls here must stay within it.

## F5 — independent exit

At 850 K and the same pressure/amount, calculate both phase energies by hand.
Predict what SOLID property evaluation returns and what equilibrium with both
phases returns. Identify the TDB terms you used.
State one check besides “the program ran” and explain why replacing the dummy
element label with Ni would not establish a nickel melting prediction.

## Handback before the opening clinic

Explain **load → evaluate each phase → minimize among allowed states**.
Keep F5, your annotated records and your actual execution route.
If hidden prerequisites or setup consumed the practice time, record that for
the instructor and revisit the task at Clinic A.
The [reading's primary sources](lesson_02_same_model_pycalphad.md#sources)
support the interfaces; original model inputs remain fixed by the contract.
