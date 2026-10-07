# Original synthetic binary-family contract

This specification underlies Lessons 4–9. It is an instructor/developer contract,
not required pre-reading for Lesson 3. Later lessons introduce each term slowly.
Nothing here is a Ni–X assessment.

## Physical question, amounts and exclusions

Closed macroscopic bulk at fixed T and p=100000 Pa, conserving A and B atoms
separately. T is 600–1800 K inclusive; composition x=nB/(nA+nB) and overall z
are in [0,1]. Normalize total n to one mole of atoms for equilibrium calculations.
Learner balance examples may scale n explicitly; pycalphad comparisons use N=1.
Fractions f count moles of atoms in phase regions, not mass, volume, pixel area
or grain-boundary sites. Phase compositions and phase amounts both vary in a
binary equilibrium calculation. For any candidate regions r:

$$f_r\ge0,\quad\sum_r f_r=1,\quad\sum_r f_rx_r=z,
\quad\sum_r f_r(1-x_r)=1-z,$$
$$g_{\rm total}=\sum_r f_rg_r(x_r,T),\qquad G=n g_{\rm total}.$$

A/B are invented atom species, no reactions or losses. Macroscopic regions may
exchange both components. We omit interfaces, strain/coherency, magnetism,
pressure dependence, kinetics and nucleation barriers. No volume, boundary excess
or real-material inference follows. Lesson 3's MA=20, MB=80 g/mol are independent
counting exercises, not required by or imported into this Gibbs model.

This binary family is **new**, not a claim that the earlier unary LIQUID/SOLID
models gained physical B parameters. ALPHA/BETA are invented distinct phase
models with the references below; their names imply no FCC/BCC identification.
The ALPHA_A expression happens to reuse the unary solid line, but BETA_A is a
different declared expression. The earlier unary contract/domain is unchanged.

## Complete models and constants

Use the natural logarithm ln. Define q(x)=(1−x)ln(1−x)+x ln x by continuous
extension with 0 ln 0=0. This is a limiting value, never an instruction to evaluate
ln(0). R=**8.3145 J/(mol K)** is a declared rounded constant matching the installed
pycalphad 0.11.2 `variables.R`; do not silently substitute a different precision.
This numerical choice carries no material-accuracy claim.

Let C(T)=1000−10T J/mol and Δ=12000 J/mol. The four endmember references are:

| Phase | pure A gA, J/mol | pure B gB, J/mol |
|---|---|---|
| ALPHA | C(T) | C(T)+Δ |
| BETA | C(T)+Δ | C(T) |

For phase φ, write the complete function

$$g_\phi=(1-x)g_A^\phi+xg_B^\phi+RTq(x)+\Omega_\phi x(1-x).$$

| Variant | Allowed phase models | Interaction / intended use |
|---|---|---|
| I1: ideal one phase | ALPHA only | Ω=0; Lesson 4 separates reference and ideal entropy terms. |
| I2: ideal two phases | ALPHA and BETA | Ω=0 in both; Lessons 5–6 conserve both components across distinct phase models. |
| R1: regular one phase | ALPHA only, may separate into two compositions of this same structure | Ω=20000 J/mol; Lessons 7–8 distinguish local and global stability. BETA is excluded. |

R1's two composition regions must not be relabelled as ALPHA/BETA structures.
A negative-Ω illustration may be described algebraically but is outside the
fixed R1 coexistence dataset. For Lesson 9 fitting only, evaluate the same
ALPHA function with trial Ω in [0,24000] J/mol; parameters varied in fitting
are separate from phase amounts/compositions varied in equilibrium. The R1 coexistence
criteria below apply to Ω=20000, not every fit trial or arbitrary Ω,T.

These regular/ideal-solution forms are standard [1]; all reference functions,
parameters and domains above are original pedagogical choices. Mixing quantities
are relative to the **same phase's** unmixed endmembers at the same T,p:
Δgmix=RTq+Ωx(1−x), Δhmix=Ωx(1−x), Δsmix=−Rq. Total h includes endmember h;
“ideal mixing has zero enthalpy of mixing” does not mean total h=0. Within each
phase at fixed x, the model has constant h/s and zero heat capacity.

## Required analytical controls, before algorithms

For 0<x<1, with dφ=gBφ−gAφ (±Δ here):

$$g'_\phi=d_\phi+RT\ln\!\frac{x}{1-x}+\Omega_\phi(1-2x),$$
$$g''_\phi=RT\left(\frac1x+\frac1{1-x}\right)-2\Omega_\phi.$$

An addition derivative of total G at fixed T,p and the other component's amount
gives μA=g−xg′ and μB=g+(1−x)g′. Changing x at fixed total n exchanges A for B:
g′=μB−μA. It is not μB alone. Derive this from G=(nA+nB)g(nB/(nA+nB)) before
teaching the tangent construction. Coexisting regions require both μ values
matched and a tangent that supports **every allowed** phase branch [2].
A stationary tangent may be unsupported; a small residual is not an error bound.

- I1: g″>0 throughout the interior, so a homogeneous phase at x=z is the global
  equilibrium. Pure endpoints use exact limiting g and s, not derivative calls.
- I2: strict convexity of each branch and reflection symmetry give
  xα=1/(1+exp(Δ/(RT))), xβ=1−xα. Both slopes are zero. The horizontal line at
  C−RT ln(1+exp(−Δ/(RT))) touches their minima and lies below both entire curves.
  Between xα and xβ, fβ=(z−xα)/(xβ−xα); outside, select homogeneous ALPHA on
  the A-rich side or BETA on the B-rich side. Equality at a boundary is the same
  state with a zero amount of the other phase; an absent phase's composition
  is not an independently determined output. The pointwise lower envelope of
  the two curves is not the equilibrium convex envelope between their minima.
- R1: affine C+Δx changes chemical-potential reference/tilt but not coexistence
  compositions. Tc=Ω/(2R). Below Tc, the spinodal compositions are
  (1±sqrt(1−2RT/Ω))/2. The binodal endpoints xL and 1−xL solve
  RT ln(xL/(1−xL))+Ω(1−2xL)=0 for the noncentral root 0<xL<0.5.
  Do not accept the always-present x=0.5 root as the subcritical binodal.
  The supporting tangent has slope Δ, not zero. At/above Tc the homogeneous
  ALPHA state is stable; the critical point does not give a finite two-phase gap.
  Positive curvature inside the binodal but outside the spinodal is metastable
  relative to the lower split, not the global equilibrium. Negative curvature
  denotes instability to infinitesimal composition fluctuations in this model.
- Add the same a(T)+b(T)x to **every allowed branch**: all balanced candidates
  shift by a(T)+b(T)z, so equilibrium compositions/amounts are unchanged. μA
  shifts by a and μB by a+b. Shifting only one phase changes the model's ordering.

## Numerical domain and endpoint policy

Energy/H/S evaluation supports the closed composition interval and temperature
domain above, rejecting nonfinite, empty or out-of-domain inputs. Derivatives
and chemical potentials require strictly interior composition, reject exact
endpoints and report nonfinite output rather than pretending the dilute
logarithm is finite. Check both 1−x and x are representable when returning pairs.
No input clipping, extrapolation or replacement of zero with epsilon may silently
change the caller's model/conditions. Any tool-imposed small endpoint offset must
be reported with its actual composition and checked there, separately from exact
pure-limit verification of the model expression.

The plain R1 coexistence routine supports T≤Tc(1−10⁻⁶) within
600–1800 K. For Tc(1−10⁻⁶)<T<Tc return an explicit near-critical numerical-domain
error, not a zero-width two-phase success. At/above Tc return a documented
single-phase status. Energies remain supported in the near-critical interval;
only automatic coexistence endpoints are restricted. This deliberate contract
boundary addresses conditioning, not a change to the regular-solution equation.

The older `regular_solution.py` helper is not an implementation of this
contract. A distinctly named binary-family module satisfies this narrower,
explicit contract; it is not a repair of the old helper.

## Numerical checks and tolerances

All tolerances below are **absolute unless explicitly relative**. They bound
numerical comparisons for this synthetic model, not experimental uncertainty.
A failed check is reported as a failure; its tolerance is not loosened to make it pass.

| Surface | Required check / threshold |
|---|---|
| Phase energies/H/S | At T=600,1000,1800 K and x=0,0.05,0.2,0.5,0.8,0.95,1: compare full reference/mixing branches with independent high-precision expressions; g/h error ≤10⁻⁷ J/mol, s ≤10⁻⁷ J/(mol K). Exact pure limits checked separately if tool samples shifted endpoints. |
| Derivatives/μ | Compare analytic identities and independent finite differences of total G at x=0.2,0.5,0.8, T=1000 K; separately vary nB at fixed nA and exchange at fixed n. Use step refinement; error ≤10⁻³ J/mol on a resolved central-difference plateau. No endpoint derivative claim. |
| I2 continuous equilibrium | T=600,1000,1800; z=0.05,0.25,0.5,0.75,0.95; compare analytic endpoints to ≤10⁻⁸, active phase fractions to ≤10⁻⁸, both balances to ≤10⁻¹⁰, total minimum to ≤10⁻⁶ J/mol. Zero-amount phases need not have a unique reported composition. |
| Grid teaching search | Show nested 21,101,501-point composition grids, both endpoints included. Candidate balance ≤10⁻¹⁰; minimum is an upper bound on the continuous minimum, and must not increase on nested refinement beyond 10⁻⁷ J/mol roundoff. Label finite-grid error; no universal exact equilibrium claim from a grid or spacing alone. |
| R1 coexistence, plain | T=600,900,1100 K and Tc(1−10⁻⁴), Tc(1−2×10⁻⁶): both endpoints within 10⁻⁹ of ≥60-digit reference; gap relative error ≤10⁻⁵. Both μ residuals ≤10⁻⁶ J/mol plus global support and balance. Central-root and unsupported near-critical controls must fail. |
| Global support | Combine analytic convexity/derivative-sign arguments with independent minimum checks of g minus tangent on every allowed branch and endpoints. Maximum downward violation ≤10⁻⁶ J/mol. A sampled-grid check alone is not proof of support. |
| Same-model pycalphad | Phase-property criteria above at actual recorded x. Equilibrium at I2 points and R1 T=600,900,1100,1300,1800 with z=0.05,0.25,0.5,0.75,0.95: energy ≤10⁻⁵ J/mol, active compositions ≤10⁻⁶, active fractions ≤10⁻⁶, both balances ≤10⁻⁸. Near-critical tool equilibria are not compared. |
| Failure/reference controls | Invalid x/T, NaN/Inf, empty arrays, unsupported coexistence range, solver failure, exact endpoints for μ, central root, clipping/conservation error, common affine reference shift and phase omission. Retain rejected-result evidence. |

A tool's phase-selection or starting-point limitation is reported as a
limitation; it is not a reason to change the model or to drop the difficult
case from the comparison. Any change of the numerical domain is stated explicitly.
Finite-difference step sizes should be selected from a recorded refinement
sequence before interpreting agreement, not tuned to one misleading residual.

## Fitting slice boundary (Lesson 9)

Use synthetic **mixing enthalpy** at T=1000 K from R1, Ωtrue=20000 J/mol.
Training x={0.1,0.3,0.5,0.7,0.9}; held-out x={0.2,0.4,0.6,0.8}; no noise for
the recovery control. Fit only Ω with [0,24000] bounds and unweighted residuals
in J/mol; objective is their squared sum in (J/mol)². Require Ω error ≤10⁻⁵ J/mol
and all held-out hmix residuals ≤10⁻⁶ J/mol using plain and tool forward models.
Both forward models must evaluate the **homogeneous ALPHA phase at the supplied
composition**, whether stable, metastable or unstable. For the tool route use
`calculate` (or the equivalent fixed-site-fraction `Model` property evaluation),
record the actual homogeneous composition, and evaluate HM at the specified T,p.
Do **not** substitute `equilibrium` or an equilibrium mixture/convex-envelope
property into the fitting residual. Restricting the phase name to ALPHA alone
does not prevent that same phase model from separating into two compositions.

For each sample subtract the same phase's unmixed pure-endmember enthalpies at
the same T,p and supplied x:

$$\Delta h_{\rm mix}=h_{\rm ALPHA}(x,T)
-[(1-x)h_A^{\rm ALPHA}(T)+xh_B^{\rm ALPHA}(T)].$$

Here hAALPHA=1000 and hBALPHA=13000 J/mol, so the subtracted reference is
1000+12000x J/mol and the intended result remains Ωx(1−x). This subtraction is
part of the observable definition, identical for plain/tool routes and every
trial Ω; no equilibrium selection of alternative references is permitted.

Required wrong-observable control at T=1000 K, Ω=20000, x=z=0.5: homogeneous
Δhmix=5000 J/mol (check with the existing 10⁻⁶ J/mol forward-residual criterion),
whereas the Gibbs-equilibrium split has Δhmix≈2810.68623619 J/mol after the same
overall-reference subtraction. Deliberately supplying that equilibrium result
must fail the homogeneous-observable comparison by more than 2000 J/mol; do
not fit away the mismatch or move the temperature. The exact split is computed
from the noncentral binodal in this contract, not from minimizing enthalpy.
This is an additional detecting control, not a relaxed numerical threshold.

Keep held-out values out of estimation. An optional entropy-interaction parameter
would be unidentifiable from hmix alone: show the missing sensitivity, not a
spurious two-parameter recovery. This is not an assessed material dataset.

## Representation

Lessons 4–8 use one source of model definitions for plain calculations and independently authored
original TDB representations, with every reference/interaction term mapped and
both branches evaluated before comparing equilibria. Use the existing pinned
Poetry environment; declare any unsupported parser/tool feature without changing
dependencies. Keep calculation output, independent checks and display rounding
separate.

## Primary scientific references

[1] R. Jaramillo, “Solution Models — Ideal, Dilute, and Regular,” MIT 3.020,
Lecture 17, 2021, [original notes](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l17.pdf).
[2] R. Jaramillo, “Phase Coexistence and Separation,” MIT 3.020, Lecture 21,
2021, [original notes](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l21.pdf).
[3] R. Jaramillo, “Regular Solution Models and Stability,” MIT 3.020,
Lecture 19, 2021, [original notes](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l19.pdf).
These lecture notes list no DOI. Our analytic controls follow from the declared
functions; they are not measurements reproduced from those sources. The local
rounded R is independently checked against pinned pycalphad variables.py, with
[official implementation](https://pycalphad.org/docs/latest/_modules/pycalphad/variables.html)
as an external reference whose current version may differ from the installed one.
