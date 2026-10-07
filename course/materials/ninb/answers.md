# Task 05 — answers and observed comparison

The hand calculation from the unchanged local source gives δ NB:NB:NB at
1000 K: **−122000.0201618562 J/mol formula**. pycalphad gives
−122000.02016185605, a difference of $1.46\times10^{-10}$ J/mol formula.
This is a single arithmetic check of a nonmagnetic endmember, not a full test
of the evaluator.
No source coefficients were copied into the course. Learners follow the
endmember's unary reference in their own local TDB for the calculator exercise.

Division by four gives **−30500.005040464013 J/mol atoms** for δ. The all-Ni
μ endmember has **−368073.0553770607 J/mol formula**, divided by thirteen to
**−28313.311952081593 J/mol atoms**. These are hypothetical endmembers;
stability is not implied by having an evaluated energy.

The closest grid point to the requested sample is **1200 K, bulk x(Nb)=0.3416**,
not exactly 0.35. It contains approximately 0.370599 atom-mole fraction μ
with x(Nb)=0.480382, and 0.629401 δ with x(Nb)=0.259883. The amount-weighted
Nb fractions sum to 0.3416; the Ni fractions sum to 0.6584. Dividing these
atom-mole phase amounts by the site divisors would corrupt the balance.
Maximum whole-grid amount error is $5.87\times10^{-9}$, and maximum component
error is $6.60\times10^{-9}$, within the declared $10^{-6}$ tolerance.
Pure liquid Nb/Ni endmember energies are finite; they are not stable-phase claims.

## Comparison actually inspected

Compare [our sampled plot](phase_diagram.png) beside Sun's manuscript Fig. 8(a),
printed p.42 / PDF p.44. Both show a liquid region above the solid regions,
Ni-rich FCC, δ around x(Nb)=0.25, μ around 0.5, low-temperature NbNi₈ and Nb-rich
BCC. The rising Nb-rich liquidus and the lower liquid region around x(Nb)=0.4
have similar broad shapes. This supports a qualitative topology comparison.

Our points fill single-phase fields and mark sampled equilibrium phase
compositions; the paper draws smooth boundaries and superimposes observations.
The 45 K temperature spacing does not establish exact invariant temperatures or
sharp boundaries. NbNi₈ disappears between sampled temperatures near 750–800 K,
consistent at this visual resolution with the paper's low-temperature region.
The μ width varies with temperature in both images, but no quantitative boundary
residual was extracted. The paper's experimental markers and uncertainty evidence
were not recalculated. Temperatures below 300 K and exact pure endpoints are
absent from our grid. Different plotting styles and grid resolution limit visual
agreement; this is not an assertion of exact reproduction of Fig. 8(a).

HCP_A3 and BCC_B2 were enabled and are not present with visible positive amounts
on this grid. That does not prove their physical metastability or rule out a
narrow stable range missed by sampling. No parameter or phase list was adjusted
to produce agreement. Source-header/publication differences remain unresolved.

For magnetism, name the three phases carrying terms and distinguish a complete
model evaluation from adding an extra correction. Further derivation is optional
reading; no magnetic branch derivation or atomistic assessment is needed.
