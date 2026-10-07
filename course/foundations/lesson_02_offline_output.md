# Supplied outputs — the same unary model in pycalphad

Use with the [Lesson-2 worksheet](lesson_02_worksheet.md).
**These are supplied outputs from the author's local run, not a record of your
own execution.** Predict each result before uncovering its row. On your worksheet
mark whether you ran code, watched a demonstration or used this sheet.

Model: invented A, one mole of atoms, p=100000 Pa, only SOLID/LIQUID,
800–1200 K. The [contract](one_component_contract.md) fixes the equations,
amount basis and numerical checks. There is no real-material prediction.

## The three actions

1. Loading the TDB defines the model and candidates; it prints no equilibrium.
2. Evaluating each phase returns its properties, including the higher branch.
3. Equilibrium selects minimum energy among the allowed states at the imposed
   temperature, pressure and conserved amount.

The following tables were transcribed programmatically from the comparison
record calculated on 28 September 2026. Energies are shown to one decimal;
checks used unrounded values.

## Evaluate both branches

| T, K | SOLID GM, J/mol | LIQUID GM, J/mol |
|---:|---:|---:|
| 800 | -7000.0 | -5800.0 |
| 900 | -8000.0 | -7400.0 |
| 1000 | -9000.0 | -9000.0 |
| 1100 | -10000.0 | -10600.0 |
| 1200 | -11000.0 | -12200.0 |

## Check enthalpy and entropy

Each row lists both phases, including the higher-energy phase.

| T, K | SOLID HM, J/mol | LIQUID HM, J/mol | SOLID SM, J/(mol K) | LIQUID SM, J/(mol K) |
|---:|---:|---:|---:|---:|
| 800 | 1000.0 | 7000.0 | 10.0 | 16.0 |
| 900 | 1000.0 | 7000.0 | 10.0 | 16.0 |
| 1000 | 1000.0 | 7000.0 | 10.0 | 16.0 |
| 1100 | 1000.0 | 7000.0 | 10.0 | 16.0 |
| 1200 | 1000.0 | 7000.0 | 10.0 | 16.0 |

## Equilibrium with both phases allowed

| T, K | SciPy GM, J/mol | pycalphad GM, J/mol | Used pycalphad phase amounts, mol (N=1) |
|---:|---:|---:|---|
| 800 | -7000.0 | -7000.0 | SOLID 1.0 |
| 900 | -8000.0 | -8000.0 | SOLID 1.0 |
| 1000 | -9000.0 | -9000.0 | LIQUID 1.0 |
| 1100 | -10600.0 | -10600.0 | LIQUID 1.0 |
| 1200 | -12200.0 | -12200.0 | LIQUID 1.0 |

At 1000 K the recorded LIQUID 1.0 output is only one possible minimizer.
Every allowed mixture has the same energy. Compare energy and conservation,
not identical phase lists or fractions at the crossing. At other tabulated
temperatures this model has a unique preferred pure phase.

The SOLID-only counterexample at 1100 K returned SOLID 1.0 and −10000 J/mol.
That restricted result omits the liquid candidate, whose −10600 J/mol is lower.

Environment: numpy 2.5.3, scipy 1.18.1, pycalphad 0.11.2, matplotlib 3.11.2, python 3.12.3.
These are outputs of the declared synthetic model, not learner results.
