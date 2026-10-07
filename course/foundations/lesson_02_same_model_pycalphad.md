# Lesson 2 — the same calculation in pycalphad

Complete [Lesson 1](lesson_01_one_component.md) first. The material model stays
the same: one invented component, two phases, the same h and s, 800–1200 K and
100000 Pa. Only the software representation changes.

Our goals are modest: find the two familiar equations in a database file,
calculate their values, and read one equilibrium result. Work through those
three steps separately. Use the [setup route](README.md#running-the-examples)
and run the Python blocks in order in one session from the repository root.

## 2.1 A database can be very small

Open [one_component_model.tdb](one_component_model.tdb). TDB is a text format
for thermodynamic model information. This file was written specifically for
these lessons; it contains no real material data. Its two energy records are:

```text
PARAMETER G(SOLID,A;0) 800 1000-10*T; 1200 N !
PARAMETER G(LIQUID,A;0) 800 7000-16*T; 1200 N !
```

Read the first one slowly:

| Text | Meaning in this example |
|---|---|
| `PARAMETER G` | Specify a Gibbs-energy model parameter |
| `SOLID,A;0` | The unary A endmember of the SOLID phase; no composition interaction here |
| `800` | Start of the declared temperature interval, K |
| `1000-10*T` | Our solid molar Gibbs expression, J/mol |
| `1200 N` | End of this interval; no following interval in this record |
| `!` | End of the record |

The other lines name the dummy element and phases. `PHASE SOLID % 1 1` and
`CONSTITUENT SOLID :A:` describe a single occupied site with only A available.
The type-definition line declares the `%` code used by these phase records.
The placeholder elemental mass and reference metadata are not measurements.
We perform no mass conversion. You do not need general sublattice modeling yet.

The [shared contract](one_component_contract.md) is the place to check units and
physical limits. Software may permit extrapolation beyond a file's interval;
that does not establish validity. The course helpers explicitly reject inputs
outside our 800–1200 K interval. Stay inside it in the raw API examples below.

**Pause:** where is the solid entropy of 10 J/(mol K) visible?

<details><summary>Answer</summary>

In the `-10*T` term. Since this example uses $g=h-Ts$ with constant h and s,
the coefficient of −T is s. It is not a separate fitted number in this file.

</details>

## 2.2 Load the model without calculating equilibrium

```python
from pycalphad import Database, calculate, equilibrium, variables as v

database = Database("course/foundations/one_component_model.tdb")
components = ["A"]
phases = ["SOLID", "LIQUID"]
```

`Database` reads the model descriptions. `components` selects the atoms we allow;
`phases` lists the modeled phases we allow. Loading a file does not by itself
calculate which phase is stable. A phase also cannot appear in a calculation
if it was never included among the candidates.

**Pause:** has this step introduced a measured melting temperature?

<details><summary>Answer</summary>

No. It loaded the same invented expressions. Any crossing still follows from
those expressions, not from an experimental dataset.

</details>

## 2.3 Calculate one phase's energy first

```python
temperatures = [800.0, 900.0, 1000.0, 1100.0, 1200.0]
solid_result = calculate(database, components, "SOLID",
                         T=temperatures, P=100000, output="GM")
print(solid_result.GM.values.reshape(-1))
```

Output: `[-7000. -8000. -9000. -10000. -11000.]`. Compare each entry with
Lesson 1 before continuing. `GM` means molar Gibbs energy. The result object
contains named arrays; `.values` accesses an array and `.reshape(-1)` displays
its entries as a single list. This flattening is convenient for this tiny
unary example; inspect dimensions before doing it for a multicomponent result.

Now change only the phase name:

```python
liquid_result = calculate(database, components, "LIQUID",
                          T=temperatures, P=100000, output="GM")
print(liquid_result.GM.values.reshape(-1))
```

Output: `[-5800. -7400. -9000. -10600. -12200.]`.
`calculate` evaluates phase properties, including a higher-energy phase; the
call does not choose the globally stable phase assemblage. These official API
examples illustrate the distinction between property calculation and
equilibrium. [1,2]

**Pause:** at 900 K, why can pycalphad return a liquid Gibbs energy even though
the solid is favored?

<details><summary>Answer</summary>

We asked it to evaluate the liquid model. A valid model value and the selection
of an equilibrium phase are different questions. Comparing both curves is part
of checking that the database represents the intended model.

</details>

## 2.4 Ask for equilibrium at one temperature

We now specify the surroundings and total amount explicitly:

```python
conditions = {v.T: 900.0, v.P: 100000.0, v.N: 1.0}
answer = equilibrium(database, components, phases, conditions)
print(float(answer.GM.values.squeeze()))
for phase, amount in zip(answer.Phase.values.reshape(-1),
                         answer.NP.values.reshape(-1)):
    if phase:
        print(phase, float(amount))
```

The output is −8000 J/mol and `SOLID 1.0`. Entries with an empty phase name are
unused output slots, so the small loop skips them. `v.T`, `v.P` and `v.N` are
pycalphad names for temperature, pressure and total amount. Here N=1 mol,
so the reported phase amounts numerically equal mole fractions.

Compare the roles with the calculation we already understand:

| Plain/SciPy route | pycalphad route |
|---|---|
| We type the two Gibbs expressions | `Database` reads them from the original TDB |
| We evaluate each expression | `calculate` evaluates each phase's model |
| We supply fractions, bounds and amount balance to `linprog` | `equilibrium` constructs the thermodynamic problem from models, components and conditions |
| We inspect success, energy and fractions | We inspect energy, phase names, amounts and balance against our known answer |

For this one-component example, the allowable compositions are fixed. Later,
binary equilibrium will also need to determine each phase's composition while
conserving the amount of each element. That is an additional lesson.

**Pause:** if we omit LIQUID from `phases`, can the result tell us whether liquid
would be more stable at 1100 K?

<details><summary>Answer</summary>

No. The equilibrium search is restricted to the allowed phase set. A solver
answer must be read together with the model and constraints that produced it.

</details>

## 2.5 Repeat the known checks

At 1100 K the result should be all liquid with −10600 J/mol. At 1000 K the
minimum energy is −9000 J/mol. A program's chosen phase fraction at the crossing
is not unique; the current run returns liquid, which is one of many minimizers.
The explanation from Lesson 1 still applies.

```python
for T in [1000.0, 1100.0]:
    result = equilibrium(database, components, phases,
                         {v.T: T, v.P: 100000.0, v.N: 1.0})
    print(T, float(result.GM.values.squeeze()))
```

Output: `1000.0 -9000.0` and `1100.0 -10600.0`.

The full [comparison program](one_component_tools.py) also requests `HM` and
`SM`, recovering the original h and s. The [saved result](one_component_result.json)
records both routes and their versions at all five temperatures. Run it yourself:

```bash
poetry run python -m course.foundations.one_component_tools
```

You can read the physics in this compact comparison:

| T, K | Plain/SciPy minimum g | pycalphad minimum g | Interpretation |
|---:|---:|---:|---|
| 800 | −7000 | −7000 | Solid |
| 900 | −8000 | −8000 | Solid |
| 1000 | −9000 | −9000 | Equal phase energies; fraction undetermined |
| 1100 | −10600 | −10600 | Liquid |
| 1200 | −12200 | −12200 | Liquid |

Energies are J/mol. Agreement checks this synthetic model's implementation; it
cannot turn invented parameters into a prediction for an actual element.

## 2.6 Stop and explain the complete route

In your own words, distinguish these four objects: a physical question, a model
with parameters, an equilibrium algorithm, and its numerical output. Then say
which part would have to change to answer a question about a real Ni-X alloy.

<details><summary>Expected explanation</summary>

The question supplied conditions and allowed phases. The model supplied the
two Gibbs functions. SciPy and pycalphad computed equilibrium from them. Their
output must be checked against energy and conservation. A real Ni-X question
needs a suitable assessed model and evidence for its domain; a defect question
also needs a defect description and the appropriate constraints. Merely changing
the label A to Ni does not provide any of that information.

</details>

**Optional stretch:** suppose only the liquid's constant term changes from
7000 to 7600 J/mol. Predict the new crossing before running anything: it would
be 1100 K. That edit changes a parameter. Estimating such a parameter from data
is a later fitting task; our equilibrium calls leave parameters fixed.

Next, we will introduce composition and mixing gradually, then chemical
potentials and binary coexistence. The historical binary exercise is development
material awaiting revision; it is not required reading before this lesson.

## Sources

[1] pycalphad developers, [Calculating Energy Surfaces](https://pycalphad.org/docs/latest/examples/LegacyEnergySurface.html).
This documented `calculate` interface is used explicitly for the pinned 0.11.2
teaching environment; newer recommended interfaces can be introduced later.

[2] pycalphad developers, [Equilibrium Properties](https://pycalphad.org/docs/latest/examples/EquilibriumWithOrdering.html).
Those official examples use other models; the model here is our own TDB.

[3] R. Otis and Z.-K. Liu, “pycalphad: CALPHAD-based Computational Thermodynamics
in Python,” *J. Open Research Software*, vol. 5, art. 1, 2017, doi:
[10.5334/jors.140](https://doi.org/10.5334/jors.140).
[Official project/citation](https://pycalphad.org/docs/latest/).
