# Task 05 — Ni–Nb: ordered phases in a published database

**Notebook:** [task05_ninb_sublattices](../../../notebooks/task05_ninb_sublattices.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ukerzel/CalphadIntro/blob/v0.1.0/notebooks/task05_ninb_sublattices.ipynb): the same steps with try-first checks; locally `poetry run jupyter lab`.

For detailed download/member/hash and paper-access steps, use the
[source guide](../../sources/README.md). Only open-source software and the
published database are needed.

This compact example introduces sublattices, amounts and reference states by
running Sun's published input in pycalphad **0.11.2**, Python **3.12.14**.
Use the [setup guide](../../setup.md), the [primers](../../primer/README.md) and the
[two-phase lesson](../../foundations/lesson_05_two_phase.md)
for extra explanation.

## Inputs and run

Read H. Sun et al., [“Thermodynamic modeling of the Nb-Ni system with uncertainty
quantification using PyCalphad and ESPEI,” *Calphad* 82, 102563 (2023)](https://doi.org/10.1016/j.calphad.2023.102563).
The [institutional manuscript](https://www.osti.gov/servlets/purl/2205728)
contains the comparison: **Fig. 8(a), printed page 42 / PDF page 44**, present
assessment. Fig. 8(b) uses a previous assessment. Open the paper beside our plot;
the course does not redistribute its figure.

Download the TDB supplement yourself from the paper's publisher page:
[original ZIP](https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip).
Extract `calpha_102563_Nb-Ni_new_mmc1.tdb` to a local path outside the repository.
The expected member is 13,087 bytes, SHA-256
`ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a`.
Use your lawful source access; this course ships
original code and instructions, without the TDB or its coefficient expressions.
The source header predates publication; its identity with the final plotted
assessment is not established simply by its filename. Compare rather than assume.

From the repository root with the locked `.venv` created by the setup guide:

```bash
mkdir -p /tmp/ninb-mpl
export MPLCONFIGDIR=/tmp/ninb-mpl MPLBACKEND=Agg
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
(ulimit -v 4194304; timeout 600 .venv/bin/python course/materials/ninb/worked_example.py --tdb /absolute/path/to/calpha_102563_Nb-Ni_new_mmc1.tdb --output /tmp/ninb-output)
```

This Linux command bounds address space to 4 GiB and elapsed time to 10 minutes.
No network access occurs in the script. Expected files are `phase_diagram.png`
and `results.json`; inspect both. They should remain below 20 MiB total.
The shipped [plot](phase_diagram.png) and [results](results.json) record the actual
run, rather than a promised exact copy of a literature diagram.

The fixed calculation uses 61 temperatures from **300 to 3000 K**, 51 bulk
Nb mole fractions from **0.005 to 0.995**, **101325 Pa**, **one mole of real
atoms**, and sampling density `pdens=60`. Pressure is a lesson convention;
the inspected figure caption does not specify it. The domain stays within the
unary function ranges for this computation; it is not a physical-validity claim.
All eight source phases are enabled: LIQUID, FCC_A1, BCC_A2, HCP_A3, DELTA,
MU_PHASE, NBNI8 and BCC_B2. No phase is removed to make the picture agree.

## Read the calculation

The plot shows the compositions of equilibrium phases at sampled temperatures,
including points inside single-phase regions. It is not a tracing of exact
phase boundaries. Two phases at different compositions can serve one bulk
composition; their atom-mole amounts satisfy a lever rule. `NP` is the phase
fraction on that atom-mole basis, and `X(NB)` is the Nb fraction among real atoms.
Vacancies on fixed vacancy sites do not add real atoms.

δ has three anonymous sublattices in ratio **1:1:2**, giving four atoms per
formula. μ has five in ratio **2:2:2:6:1**, giving thirteen. These labels introduce
CEF bookkeeping, without assigning physical Wyckoff positions.
The named δ-NbNi₃ and μ-Nb₇Ni₆ compositions are useful labels; variable site
occupation allows composition ranges. A hypothetical all-Nb δ endmember or
all-Ni μ endmember is a model building block, not necessarily a stable material.

`Model.G` is the formula-basis model expression in this check;
`Model.GM` is already in J/mol real atoms. Thus $G_m=G_{formula}/4$ for δ,
and $G_m=G_{formula}/13$ for μ. Do not divide `GM` again.
This use of `Model.G` is distinct from the public property-framework `G`, an
extensive energy in joules. SER references organize energies relative to the
standard element reference states; Gibbs energy is not required to be zero
at 298.15 K. Do not add the element metadata's enthalpy/entropy a second time.

Magnetic ordering contributes to Gibbs energy through the transition temperature
and magnetic moment. This source carries magnetic parameters in FCC_A1, BCC_A2
and HCP_A3; FCC_A1 also has binary composition-dependent terms. The total model
already includes them. No separate magnetic term is added here. The
[Task 01 Cu–Ni on/off comparison](../cuni/README.md) is available as the
lightweight magnetic demonstration. Copying bulk magnetic parameters to a
boundary model would be an explicit assumption. Sun's assessment combines
DFT-based information, experimental data and uncertainty analysis. Energies
from a nonmagnetic machine-learned interatomic potential (MLIP), such as a
participant may use in their own research, have a different energy basis and
origin. We do not refit.

## Short exercise

1. Open local `G(DELTA,NB:NB:NB;0)` and follow its named unary function to the
   branch containing 1000 K. Evaluate that branch with a calculator, then the
   endmember expression, on the formula basis. The source is read locally; no
   expression is reproduced here. Compare with `energy_checks` in the JSON.
2. Convert that δ energy and the all-Ni μ energy to J/mol atoms. Explain why
   dividing the reported `atom_J_per_mol` by four or thirteen would be wrong.
3. At the JSON sample's actual temperature/composition, reconstruct the bulk
   Nb fraction from the reported phase amounts and compositions. Repeat for Ni.
4. Compare our plot with Fig. 8(a). Locate the liquid region, δ near 0.25 Nb,
   μ near 0.5 Nb, NbNi₈ at lower temperatures and Nb-rich BCC. Which details
   can a 45 K temperature spacing resolve? Does an enabled but unseen phase
   prove physical metastability?

See [answers and observed comparison](answers.md). Numeric checks use a
hand/conversion absolute tolerance **1e-8 J/mol** and relative
**1e-12**; component and amount balances absolute **1e-6**. Both pure liquid
endmember evaluations must be finite. Near-pure grid results are inspected;
they do not substitute for an exact endpoint equilibrium or melting-point fit.

Evaluator conventions at $T=T_C$, regularization, gas-constant choices,
extrapolation and support of zero-weight terms can differ. This lesson uses the
pinned evaluator, without investigating those edge cases or claiming literal-source
or cross-engine equivalence. See the pinned installed `pycalphad/model.py`,
[Hillert–Jarl](https://doi.org/10.1016/0364-5916(78)90011-1) and
[Dinsdale](https://doi.org/10.1016/0364-5916(91)90030-N) for further reading.
The arithmetic, balances and visual comparison demonstrate evaluator output;
they do not validate the physics or the uncertainty model.
