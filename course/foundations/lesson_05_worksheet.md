# Lesson 5 worksheet — feasible first, lower energy second

Use [reading](lesson_05_two_phase.md). All energies below are synthetic at 1000 K;
amount basis is moles of atoms. Calculator/paper suffice. Round hand energies to
1 J/mol and amounts to 0.001; this is not a software tolerance change.

## Meeting 12

**A1 — retrieve and work.** For n=1, z=0.5 write initial A/B inventories. Compare
homogeneous ALPHA x=0.5, homogeneous BETA x=0.5 and half ALPHA x=0.2/half BETA x=0.8.
Use the supplied energies, compute both balances and rank the feasible candidates.

**A2 — guided second comparison.** Use half ALPHA x=0.1 and half BETA x=0.9;
each region has g=−10502.902382 J/mol. Compute sample g and compare with A1's
0.2/0.8 split. Which endpoint pair has lower energy? Have we searched every pair?

**A3 — planted error.** A solver reports all atoms as ALPHA x=0.2 for z=0.5.
It says “success, low energy.” List three checks (total,A,B), then diagnose the
failure. Would only checking the sum of phase fractions detect it?

**A4 — independent exit.** At z=0.35 try 75% of atoms in ALPHA x=0.2 and 25% in
BETA x=0.8. Calculate A/B inventories and sample g. Are these percentages phase
amounts, phase compositions, or mass percentages? State what extra evidence is
needed before calling the candidate the continuous equilibrium.

## Meeting 13

**B1 — worked lever rule.** Draw xα=0.2, xβ=0.8, z=0.35 and derive fβ from balance.
On n=4 mol find both phase amounts and both constituent amounts in each phase.

**B2 — guided failure.** Repeat the fraction calculation for z=0.1. Show why
clipping the answer changes overall composition. What if both endpoints equal 0.35?

**B3 — guided grid table.** For each row in the reading's21/101/501 table, use
fβ=0.5 to check B balance and its positive energy gap. Do the selected endpoints
move monotonically? Can a dense plot replace a global support proof? Explain.

**B4 — independent fresh example.** Supplied continuous endpoints at 1000 K are
xα=0.191040753, xβ=0.808959247. Let z=0.25, n=2 mol. Find fα,fβ, both phase amounts
and total B from the two regions. Their energies equal −10762.730017 J/mol;
compute total G. Compare with a coarse candidate using 0.2/0.8 at this same z.
Which has lower energy and by how much per mole? State what is given, derived,
and still requires the next lesson's global-support argument.
