# Lesson 4 worksheet — separate, add, conserve

Use the [reading](lesson_04_ideal_mixing.md) and its log card. Calculator optional;
rounded hand answers to 1 J/mol and 0.001 J/(mol K) are sufficient for learning,
not changes to the software's tighter verification tolerances. Keep answers
hidden until the attempt. All models/amounts are synthetic as declared in the [binary-family contract](binary_family_contract.md).

## Meeting 10: A tasks

**A1 — retrieval/worked start.** One mole has xB=0.2. Write its moles of A and B.
At 1000 K, use gA=−9000 and gB=3000 J/mol. Find the unmixed weighted reference.
Does a uniform state with xB=0.5 contain the same inventory?

**A2 — guided logarithms and arrangements.** List the six arrangements of two A
and two B on four labelled sites. Does counting six directly give the macroscopic
molar entropy used in this lesson? From the log card calculate q at x=0.5 and 0.2;
find Δsmix and Δgmix at 1000 K. Explain the signs. What is Δhmix in this model?

**A3 — endpoint diagnostic.** A program prints NaN for x=0 because it used
`0*log(0)`. Explain the intended limit and give g, h and s for pure A at 1000 K.
Would replacing zero by 0.01 preserve the requested sample?

**A4 — independent exit.** At x=0.5 compare the mixing terms at 600 and 1800 K.
Give Δh, Δs and Δg with units. Does “ideal enthalpy of mixing is zero” justify
setting the total enthalpy to zero? Explain using the pure-reference contribution.

## Meeting 11: B tasks

**B1 — worked decomposition.** At 1000 K complete rows x=0,0.2,0.5,0.8,1 with
columns gref, Δgmix, g, h, s. Plot gref and Δgmix separately before adding them.
Use the supplied figure or five labelled points; use a different line style for
each energy column. If using code, predict both endpoints before running the cell.

**B2 — guided change.** Keep x=0.5 but lower T to 600 K. Calculate h, s, gref,
Δgmix and g. Then scale the sample to 2 mol and state total G,H,S with units.
Which quantities change with total amount? Which mixing term changes with T?

**B3 — diagnose an invalid comparison.** A learner with closed z=0.5 sees that
g(0.2) is lower than g(0.5), and reports homogeneous x=0.2 as equilibrium.
Count the initial/final A and B amounts and explain the mistake. Does comparing
curves across x alone implement conservation?

**B4 — independent fresh example.** At 1000 K, x=0.25, use ln(0.25)=−1.38629436,
ln(0.75)=−0.28768207. Find q, Δs, Δg, gref, total g and total h. Scale G to 3 mol.
Then compare x=0.75: which mixing contributions match, and why does total g
not match? Supply one sentence distinguishing symmetry of mixing from symmetry
of the complete phase reference.
