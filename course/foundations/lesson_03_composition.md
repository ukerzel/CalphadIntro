# Lesson 3 — what does alloy composition count?

Two 90-minute meetings, 08–09 in the full course. Before starting, explain the
one-component model's amount balance and the distinction between total G and
molar g. Bring arithmetic, paper and optionally a calculator. No code or calculus
is required. Use the [worksheet](lesson_03_worksheet.md); hints, answers and
meeting timing are in the [instructor guide](../instructor/lesson_03_guide.md).
We now add **counting a second component**, not a new energy model.

## 3.1 Count before introducing symbols

Imagine 20 tokens: 15 labelled A and five labelled B. Each token represents one
atom in this little counting picture. B accounts for 5/20=0.25 of the atoms;
A accounts for 15/20=0.75. The fractions sum to one. A label identifies an atom
species; moving it between boxes does not turn A into B.

An actual macroscopic sample contains far more atoms. The amount n in moles
counts specified entities: here always **atoms**, not molecules, lattice cells
or kilograms. One mole contains exactly $N_A=6.02214076\times10^{23}$ entities;
$N=nN_A$, where N is an atom count. [1] Twenty tokens are not literally one mole.
We can scale their **ratio** to a one-mole model: nA=0.75 mol and nB=0.25 mol.

**Pause:** double the token counts. Which changes: total amount, B fraction,
or both? Answer: total doubles; B fraction remains 0.25.

## 3.2 Give a fraction its numerator and denominator

For this binary A–B system define

$$x_B=\frac{n_B}{n_A+n_B},\qquad x_A=1-x_B.$$

The ratio is dimensionless. It is the **mole fraction** or amount fraction [2].
Because all entities here are atoms, it also equals the atomic number fraction.
“25 at.% B” means xB=0.25, not xB=25; always state what the percentage counts.
A binary composition can be described by one of these fractions because their
sum is fixed, but both component inventories must still be conserved.

Worked: nA=3 mol and nB=1 mol. Total n=4 mol; xB=1/4=0.25.
In contrast, nB/nA=1/3 is an amount **ratio**, not the fraction of the total.

**Pause:** for nA=0.6 mol and nB=0.4 mol, calculate xA, xB and nB/nA.
Answer: 0.6, 0.4 and 2/3. The denominator matters.

## 3.3 Equal atom fractions need not mean equal mass fractions

Mass m and amount n are connected by molar mass M: $m=nM$. Use grams with g/mol,
or kilograms with kg/mol; do not mix them. [3] For this exercise only, assign
**invented** molar masses MA=20 g/mol and MB=80 g/mol. These are supplied arithmetic
inputs, not elemental data and not the unary TDB's placeholder masses.

In the 3 mol A + 1 mol B example, mA=60 g and mB=80 g. Total mass=140 g, so
$w_B=m_B/(m_A+m_B)=80/140=4/7\approx0.571429$. The mass fraction [4] differs
from xB=0.25 because B's molar mass is larger. The definitions give

$$w_B=\frac{x_BM_B}{(1-x_B)M_A+x_BM_B}.$$

Work this from masses, rather than memorize the equation. For an inverse example,
40 g A and 40 g B correspond to 2 mol A and 0.5 mol B: wB=0.5 but xB=0.2.
No density is given. We cannot convert these data into volume or image-area
fractions by relabelling x or w. Do not infer densities from the token drawing.

**Pause:** can “50% B” be interpreted without its amount/mass/volume basis?
Answer: no. For these invented masses, 50 at.% and 50 mass% describe different
numbers of A and B atoms.

## 3.4 Put the same atoms in two boxes

A **phase** is a thermodynamic state of material with its own composition and
properties. A component is a conserved constituent, here A or B. Both components
can occur in either phase; “A” is not the name of one box and “B” the other.
Use α (alpha) and β (beta) for the two candidate phases. We supply their atom
inventories for bookkeeping; we have not established that they are equilibrium.

| Box | A tokens | B tokens | Total tokens | Fraction of all tokens in box | B fraction inside box |
|---|---:|---:|---:|---:|---:|
| α | 9 | 1 | 10 | 0.5 | 0.1 |
| β | 6 | 4 | 10 | 0.5 | 0.4 |
| Whole | 15 | 5 | 20 | 1 | 0.25 |

The **phase mole fraction** fβ=10/20=0.5 tells how much of the sample is in β.
The **phase composition** xBβ=4/10=0.4 tells how B-rich β is. The **overall
composition** zB=5/20=0.25 counts B in the whole. These answer different questions.
A superscript α or β labels a phase; it is not an exponent in this notation.

On a one-mole total basis: nα=nβ=0.5 mol; α contains 0.45 mol A and 0.05 mol B;
β contains 0.30 mol A and 0.20 mol B. A totals 0.75 mol and B 0.25 mol.
Using our invented masses, the phase masses are 13 g and 22 g, so β's phase
**mass** fraction is 22/35, not its mole fraction 0.5 or its B composition 0.4.

**Pause:** if β contains 40 at.% B, does β occupy 40% of the whole sample?
Answer: no; xBβ alone supplies no phase amount.

## 3.5 Write two balances before selecting a phase split

Let total amount be n, with nα and nβ in the phases, and fα=nα/n, fβ=nβ/n.
For a closed system with no component reactions or losses:

$$n_\alpha+n_\beta=n,$$
$$n_\alpha x_B^\alpha+n_\beta x_B^\beta=nz_B,$$
$$n_\alpha(1-x_B^\alpha)+n_\beta(1-x_B^\beta)=n(1-z_B).$$

Every amount is nonnegative and every composition is between zero and one.
Dividing by n gives fα+fβ=1 and
$z_B=f_\alpha x_B^\alpha+f_\beta x_B^\beta$.
For this binary, total and B balance algebraically imply A balance, but writing
both helps expose a mistaken denominator. Counting conserves each species, not
only the total number of atoms. This accounting says nothing about which split
has the lowest Gibbs energy.

Worked: n=2 mol, zB=0.3, nα=nβ=1 mol, xBα=0.1, xBβ=0.5.
B: 1×0.1+1×0.5=0.6 mol=2×0.3. A: 0.9+0.5=1.4 mol=2×0.7.
A trial with the same amounts but xBβ=0.4 preserves n=2 mol and loses 0.1 mol B.
It is invalid for the stated closed sample even if someone reports a low energy.

## 3.6 Infer a missing amount, without an equilibrium solver

Suppose zB=0.25 and the **supplied** phase compositions are 0.1 and 0.4.
Substitute fα=1−fβ into balance:

$$0.25=(1-f_\beta)0.1+f_\beta0.4=0.1+0.3f_\beta.$$

Thus fβ=0.5 and fα=0.5. We inferred the amount for these proposed compositions;
we did not derive the compositions themselves. Later an energy model will do
that extra work. If zB=0.5 with the same phase compositions, balance would demand
fβ=4/3 and fα=−1/3: these two compositions cannot represent that sample.
Never clip the fractions to [0,1] and call the changed inventory a solution.

For coincident supplied compositions xBα=xBβ=zB, any phase fraction obeys this
component balance; balance alone cannot select an amount. If both supplied
compositions are equal to a different value from zB, none is feasible.

## 3.7 What we can now ask

Before equilibrium, define the total inventories, allowed components/phases,
amount basis and constraints. A candidate must first preserve both components.
Then a Gibbs model can compare its energy with other candidates. The next lesson
will build an ideal-solution energy for the same binary counting variables.
Today supplies no phase diagram, tie-line prediction, chemical potential, real
Ni–X parameters or kinetics. The [binary-family contract](binary_family_contract.md)
declares the later invented model before its code is introduced.

## Sources

[1] BIPM, [SI base unit: mole](https://www.bipm.org/en/si-base-units/mole), current SI definition; no DOI listed.
[2] IUPAC, “Amount fraction,” *Gold Book*, doi:
[10.1351/goldbook.A00296](https://doi.org/10.1351/goldbook.A00296),
[definition](https://goldbook.iupac.org/terms/view/A00296).
[3] IUPAC, “Molar mass,” *Gold Book*, doi:
[10.1351/goldbook.12214](https://doi.org/10.1351/goldbook.12214),
[definition](https://goldbook.iupac.org/terms/view/12214).
[4] IUPAC, “Mass fraction,” *Gold Book*, doi:
[10.1351/goldbook.M03722](https://doi.org/10.1351/goldbook.M03722),
[definition](https://goldbook.iupac.org/terms/view/M03722).
The equations for box inventories follow directly from these amount definitions;
all token counts and example masses are original synthetic teaching choices.
