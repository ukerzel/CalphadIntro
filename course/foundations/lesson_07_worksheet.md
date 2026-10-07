# Lesson 7 worksheet — interactions and stability

Use [reading](lesson_07_regular_solution.md). Model R1 is ALPHA only, Ω=20000 J/mol,
T600–1800 K, pressure 100000 Pa, closed moles of A/B atoms. Calculator/paper suffice;
round hand energies to 1 J/mol, fractions to 0.001. Software tolerances are unchanged.

## Meeting 17

**A1 — retrieval/worked.** At x=0.5 calculate the interaction contribution for Ω=0
and Ω=20000. With Δsmix=5.763172 J/(mol K), calculate Δgmix at 600 and 1300 K.
Which quantity represents the interaction parameter, and which the composition?
Which quantity changes in a temperature scan with fixed Ω?

**A2 — guided second composition.** At 600 K, x=0.05, use q=−0.1985152433.
Calculate Δh,Δs,Δg and total h. Explain why zero ideal Δh was not a claim of zero
total enthalpy, and why the interaction term introduces no new entropy here.

**A3 — balanced perturbation.** Split a homogeneous z=0.5 sample into equal amounts
at 0.49/0.51. Verify both balances. Given g″(0.5)=−20045.2 J/mol at 600 K, estimate
the energy change using 0.5g″ε². Does the nonzero full g′ invalidate this argument?

**A4 — independent exit.** At x=0.2 the interaction term is what value? Its total
reference enthalpy is 3400 J/mol: find total h. At 600 K the ideal mixing contribution
to G is −2496.357570 J/mol; compute regular Δgmix. Does its sign alone determine
coexistence compositions or a real material's decomposition rate? Explain.

## Meeting 18

**B1 — worked classification.** Draw the four 600 K boundaries from the reading.
Place z=0.01,0.05,0.5,0.95,0.99. Label the corresponding homogeneous states
stable/metastable/unstable using both local and global reasoning.

**B2 — guided equilibrium.** At 600 K use xL=0.021032752, xR=0.978967248 and z=0.05.
Calculate fR,fL, both component balances and equilibriumg from
ℓ(z)=−5097.197721+12000z. Compare with homogeneous −4440.332994 J/mol.
Why can positive curvature coexist with a lower distant split?

**B3 — diagnose false roots and ranges.** A root finder gives xL=xR=0.5 at 600 K
with zero residual. Name two independent checks that reject it. Is full g′(0.5)
zero? A second run at Tc(1−0.5×10⁻⁶) raises an error; does that prove no physical
gap? Can homogeneous properties still be evaluated there?

**B4 — independent fresh example.** At 900 K supplied binodals 0.111251338/0.888748662
and spinodals 0.249153932/0.750846068 apply. Classify homogeneous z=0.05, 0.2, 0.5.
For z=0.2 derive fR from the supplied binodals and verify B balance. With tangent
ℓ(z)=−8635.019724+12000z J/mol, compute equilibrium G for 3 mol of atoms. State
which phase labels should appear, and why BETA is absent.
