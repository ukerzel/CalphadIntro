# Shared model for Lessons 1 and 2

This original synthetic model is the same in hand arithmetic, NumPy/SciPy and
the bundled TDB/pycalphad route. It predicts no real material. One invented
component `A` has two allowed phases named `SOLID` and `LIQUID`.

| Quantity | Contract |
|---|---|
| Basis | One mole of A atoms; energies J/mol, entropy J/(mol K) |
| Conditions | Closed bulk system, fixed T, fixed p=100000 Pa, total n=1 mol |
| Supported temperature | 800 through 1200 K inclusive |
| SOLID | h=1000 J/mol, s=10 J/(mol K), g=1000-10T J/mol |
| LIQUID | h=7000 J/mol, s=16 J/(mol K), g=7000-16T J/mol |
| Degrees of freedom | Solid/liquid mole fractions, nonnegative and summing to one |
| Equilibrium objective | Minimize fS*gS+fL*gL |
| Crossing | 1000 K, both g=-9000 J/mol; fractions are not uniquely determined |

Constant h/s imply zero heat capacity within each phase. The model supplies no
pressure dependence, strain, magnetism, interfaces, nucleation or kinetics.
No inference about volumes or behavior at other pressures is supported.
`A` is a dummy species; its TDB mass/reference metadata are placeholders, not
physical element data. No mass-fraction conversion is performed.

The TDB is independently written original course content with exactly these
two Gibbs expressions. It is not extracted from a school or material database.
The repository license applies. Reading it with another engine is a test of
this declared model, not of that engine's full CALPHAD feature set.

## Numerical checks

At 800, 900, 1000, 1100 and 1200 K, compare **both** branch energies, including
the higher-energy branch, with the equations above. Absolute tolerance:
1e-7 J/mol. Check pycalphad HM/SM recover the tabulated h/s to 1e-7 in their
respective units. Compare equilibrium energy with min(gS,gL) to 1e-6 J/mol.
Check the numerical crossing to 1e-8 K and off-crossing phase fractions/amount
balance to 1e-8. These computational tolerances express no material uncertainty.

At the crossing compare minimum energy and valid balance, not one phase list
or fraction. Test multiple trial mixtures there; the energy is constant.
Reject empty, nonfinite and out-of-range temperatures. Scalar equilibrium calls
reject arrays. Exercise optimizer failure handling and a common-reference shift.
Record actual environment versions, source/code/test/contract hashes and outputs.
No numerical tolerances may change merely to accommodate a failed comparison.

## Reproduction

From the repository root in the pinned Poetry environment:

```bash
poetry run python -m course.foundations.one_component_manual
poetry run python -m course.foundations.one_component_tools > /tmp/one_component_result.json
poetry run python -m unittest discover -s tests -p test_one_component_course.py -v
```

The old binary helper is not used.
