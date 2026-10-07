# Lesson 8 worksheet — represent, evaluate, minimize, verify

Use [reading](lesson_08_binary_tools.md), printed tables and original TDB. All data
are synthetic, fixed pressure 100000 Pa, atom mole basis. Optional code uses the
existing environment; no new installation is a hidden prerequisite.

## Meeting 19

**A1 — worked mapping.** For ALPHA at 1000 K, x=0.2, mark the two G parameters,
the generated ideal entropy term and LZERO. Write the complete equation with Ω=0,
then with Ω=20000. Which part should not be typed a second time into the TDB?

**A2 — guided second branch.** At 1000 K, x=0.8 compare ideal BETA with ideal
ALPHA at x=0.2. Use the table to check G,H,S. Why do they match? What would happen
if the BETA pure references were copied in the ALPHA order?

**A3 — planted mismatch.** An edited file has G(ALPHA,B)=12000−10T instead of
13000−10T. At x=0.5 estimate the change in G and H; does ideal entropy change?
Would loading the file successfully prove it represents the intended model?

**A4 — independent exit.** At 1000 K, x=0.5 the tool returns homogeneous R1
G=−3763.172233, H=12000, S=15.763172. Check G=H−TS to displayed precision, subtract
the declared enthalpy reference and label the mixing observable. State why
`calculate` with explicit points is appropriate and which actual coordinate to save.

## Meeting 20

**B1 — worked interpretation.** For each I2/R1 equilibrium row at z=0.5, compute
the amount of B and A in its region. Sum them. Why must the two ALPHA rows in R1
remain separate? Is the repeated equilibrium-g table column a region's energy?

**B2 — guided wrong observable.** The R1 equilibrium mixing enthalpy is 2810.686236
J/mol, versus homogeneous 5000. Compute the discrepancy. Does ALPHA-only phase
selection prevent separation? Which thermodynamic potential chose the split?

**B3 — guided diagnosis.** A run with only ALPHA and Ω=0 reports G=−8763.172233 at
z=0.5 and passes both balances. The intended variant was I2. Is it accepted? Name
a check that catches this and a check that cannot by itself.

**B4 — independent fresh example.** A tool result at 1000 K, z=0.25 reports I2
ALPHA x=0.191040753, f=0.904584103 and BETA x=0.808959247, f=0.095415897.
Check B and A balances. On 4 mol, compute both region amounts and total G using
sample g=−10762.730017 J/mol. List three provenance/model fields needed to make
this a reviewable calculation. Does parity with the plain model validate an alloy?
