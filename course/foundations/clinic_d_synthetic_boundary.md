# Clinic D — one cell, three thermodynamic questions

Meeting 34, after [Lesson 14](lesson_14_competing_states.md). Use this sheet
with the [instructor answer key](../instructor/clinic_d_guide.md) closed until
the independent task. The complete paper route needs a calculator, not Python.
All species, structures, preferences and energies are invented. Lessons
[11](lesson_11_geometry.md), [12](lesson_12_reservoir.md),
[13](lesson_13_finite_reservoir.md) and [14](lesson_14_competing_states.md)
define the conventions. The [Lesson 10 source audit](lesson_10_source_audit.md)
still records a real Ni–Cu input GAP.

**Exit goal:** count both components and boundary areas, choose the potential
that matches what is held fixed, compare two separately relaxed states on one
energy basis, and say which evidence is missing for a real-material conclusion.

## Shared card — read before calculating

At 1000 K and 100000 Pa, the cell has 8000 bulk sites and two equivalent
boundaries. **Each** boundary has 100 substitutional sites and area 20 nm².
Every site contains one A or B atom. Initially the boundary B fraction is
$\theta_0=0.25$ and the bulk B fraction is $x_0=0.30$. The bulk uses the [binary-family
ideal ALPHA](binary_family_contract.md) model, with $R=8.3145$ J/(mol K). For a boundary occupancy $\theta$,
State I adds $\delta_I\theta$ to the same ideal site energy, with
$\delta_I=-5000$ J/mol boundary sites. State II adds
$\eta_{II}+\delta_{II}\theta$, with $\eta_{II}=+2000$ and
$\delta_{II}=-10000$ J/mol boundary sites. State I's baseline is zero.
For the chosen equal-site reference, excess per boundary area is

$$\Gamma_B=\frac{S(\theta-x_b)}{A N_{\rm Av}},\qquad
N_{\rm Av}=6.02214076\times10^{23}\ \mathrm{mol}^{-1}.$$

The closed cell fixes total A and B; the open experiment fixes the composition
and chemical potentials of a large external bulk reservoir. A boundary B atom
always replaces an A atom. The two experiments have different constraints.

## 00–40 minutes — count, then select the ensemble

**D1 — worked count (12 minutes).** Initially bulk B is
$8000(0.30)=2400$ atoms and boundary B is $2(100)(0.25)=50$ atoms. The cell
therefore has **2450 B and 5750 A on 8200 sites**. Check the A count by adding
bulk and boundary A separately. Its cell-average B fraction is $2450/8200$;
it is neither $x_0$ nor $\theta_0$. The area for a whole-cell excess count is
$2(20)=40$ nm², whereas $S/A=5$ sites/nm² is the per-boundary density.

**D2 — guided open route (18 minutes).** Keep a large external ALPHA reservoir
at $x_b=0.30$ and use State I only. The Lesson 12 odds relation gives the supplied
open result $\theta_{I,\mathrm{open}}=0.43882335$ and minimized excess grand
potential $\phi_I=-1837.87532$ J/mol **boundary sites**. Reconstruct the odds
multiplier $e^{-\delta_I/(RT)}$ and check the direction of enrichment. Starting
from the shared card's $\theta_0$, how many B atoms enter the 200 boundary
sites, and what happens to the same number of A atoms? Calculate $\Gamma_B$
in atoms/nm² and mol/m² using the fixed reservoir $x_b$. Name the two chemical
potentials subtracted from the site energy; is $\phi_I$ an absolute grain-boundary
energy?

**Break: 40–45 minutes.**

## 45–70 minutes — close the cell, then compare states

**D3 — guided closed route.** Return to **2450 fixed B atoms**. State I's
separately minimized card is

| State I, closed | $\theta_I$ | final $x_{b,I}$ | $\bar g_I^*$ |
|---|---:|---:|---:|
| $x_0=0.30$ | 0.43342952 | 0.29541426 | −10529.48099 J/mol all cell sites |

Use $8000x_b+200\theta=2450$ to check it to printed rounding. Calculate the
whole-cell equal-site B excess using both boundary areas. Why is the open
$\theta$ from D2 a wrong answer to this closed problem? A colleague holds
$x_b=0.30$ while changing $\theta$ to 0.43342952 and still claims total
B=2450: calculate the actual total and identify the broken constraint.

**D4 — two compatible states.** State II is separately minimized with the
same closed inventory, area, sites, binary-family reference, temperature and pressure:

| State II, closed | $\theta_{II}$ | final $x_{b,II}$ | $\bar g_{II}^*$ |
|---|---:|---:|---:|
| $x_0=0.30$ | 0.57835338 | 0.29179117 | −10542.40484 J/mol all cell sites |

Check its B balance. Convert State II's baseline of +2000 J/mol **boundary
sites** to J/mol **all 8200 cell sites**, then calculate
$D=\bar g_{II}^*-\bar g_I^*$. Which of these **two uniform model branches** is
lower? If someone omits the baseline, which branch would the numerical card
select? Explain why subtracting D2's open $\phi_I$ from D4's closed
$\bar g_{II}^*$ has no meaning. Neither subtraction proves that two physical
boundary phases coexist.

## 70–90 minutes — independent transfer and claim check

**D5 — fresh closed cell (15 minutes; complete unaided first).** Repeat the
same model at $x_0=0.40$, with the same initial $\theta_0=0.25$. These are
separately minimized, **supplied** values; solving again is optional.

| State | $\theta^*$ | final $x_b$ | $\bar g^*$, J/mol all cell sites |
|---|---:|---:|---:|
| I | 0.54127054 | 0.39271824 | −9884.21053 |
| II | 0.67967666 | 0.38925808 | −9910.05801 |

Find total A and B; verify B for each state to rounding. Find $D$ and the
lower branch. Convert State II's **chosen-reference** excess to atoms/nm².
One presenter calls this a measured Ni–Cu segregation result and the synthetic
branch switch a confirmed interface phase transition. Write two sentences:
the strongest supported synthetic conclusion and one exact missing bulk or
boundary evidence field that stops the real claim. Preserve the source GAP.

**D6 — exit (5 minutes).** Circle the quantity fixed in each route:
external reservoir $x_b$ or closed total B. On one line, state why the two
potentials cannot be subtracted. Mark which of D2–D5 you completed unaided,
with hints or not yet.

### Hints to reveal only after an attempt

1. For D2, $RT=8314.5$ J/mol and $\theta/(1-\theta)
   =[x_b/(1-x_b)]e^{-\delta/(RT)}$. Boundary B changes by
   $200(\theta-0.25)$; $S/A=5$ sites/nm².
2. For D3 and D5, first calculate $B_{\rm tot}=8000x_0+50$.
   The final bulk fraction is a result, not a second fixed input.
3. For D4, the baseline contribution is $200\eta_{II}/8200$ J/mol
   all sites. Compare only the two separately minimized **closed** energies.
4. For the claim check, a synthetic source card cannot specify an eligible
   Ni–Cu TDB, boundary geometry/state, excess reference or held-out observation.

### Optional code check after the paper answer

In the project's Poetry environment, compare the supplied cards with the
existing small functions; do not read a successful run as material validation.

```python
from course.foundations.boundary_one_state import open_equilibrium
from course.foundations.boundary_two_state import compare_states

print(open_equilibrium(0.30, -5000))
for x_initial in (0.30, 0.40):
    print(compare_states(x_initial))
```
