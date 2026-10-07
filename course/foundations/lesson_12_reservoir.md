# Lesson 12 — one boundary state in an open reservoir

Meetings 28–29. Use the [one-state open-reservoir contract](boundary_one_state_contract.md), [Lesson 11 geometry](lesson_11_geometry.md), [worksheet](lesson_12_worksheet.md) and [instructor answers](../instructor/lesson_12_guide.md). This is an invented A/B system at 1000 K and 100000 Pa.

**Exit goal:** compare trial occupancies on one declared energy basis, derive the A-for-B exchange condition, check it with a bounded minimizer, and convert the selected occupancy to the equal-site excess per area. The result describes one structural state only.

## 12A — hold the reservoir fixed

Retain two equivalent boundaries, each with 100 substitutional sites and area 20 nm², plus 8000 bulk sites. In the **open** experiment, a large ALPHA bulk reservoir fixes its B fraction $x_b$ and both chemical potentials. Changing boundary occupancy exchanges B for A; each site stays filled. We do not conserve B in the 8200-site cell alone. For numerical work in this lesson, $0.01\le x_b\le0.99$ and the invented boundary preference $-10000\le\delta\le10000$ J/mol of boundary sites.

The boundary-site Gibbs energy per mole of occupied sites is the [binary-family ideal ALPHA energy](binary_family_contract.md) plus $\delta\theta$. Thus $\delta<0$ lowers the energy when B occupies a boundary site. For occupancy $\theta$, subtract **both** bulk component reservoirs:

$$\phi(\theta)=g_{\rm site}(\theta)-(1-\theta)\mu_A-\theta\mu_B.$$

This is an *excess grand potential relative to equal-site bulk*, in J/mol of boundary sites. It simplifies to

$$\phi(\theta)=RT\left[(1-\theta)\ln\frac{1-\theta}{1-x_b}+\theta\ln\frac{\theta}{x_b}\right]+\delta\theta,$$

with $0\ln0=0$ at the endpoints. The logarithmic part measures the cost of a boundary occupancy different from the reservoir. The preference competes with that cost. This chosen reference has no structural baseline; $\phi$ can be negative or positive. It is **not** an absolute grain-boundary free energy. A number in J/mol of sites is also not yet J for a finite cell: multiply by $2S/N_{\rm Av}$ mol of sites if that total is needed.

### Worked trial comparison

Take $x_b=0.10$, $\delta=-5000$ J/mol sites and $RT=8314.5$ J/mol. At $\theta=x_b=0.10$, the logarithmic part vanishes, so $\phi=-500$ J/mol sites. At $\theta=0.15$, the full expression gives about $-648.27$ J/mol sites; at $\theta=0.25$, about $-482.31$ J/mol sites. Of these three **trials**, 0.15 is best. The three-way comparison does not establish the continuous minimum.

At fixed sites, the change associated with B entering and A leaving depends on $\mu_B-\mu_A$. Subtracting $\mu_B$ alone would make a different energy and a different minimizer. For this reservoir, $\mu_A\approx-9876.02$ and $\mu_B\approx-16144.84$ J/mol atoms; their difference is $-6268.82$ J/mol atoms. Both components must be accounted for even though the boundary has one independent occupancy.

## 12B — select and check the occupancy

Inside $0<\theta<1$, the derivative is

$$\phi'(\theta)=\delta+RT\ln\frac{\theta}{1-\theta}-RT\ln\frac{x_b}{1-x_b}.$$

It is strictly increasing because $\phi''=RT/[\theta(1-\theta)]>0$. Its zero is therefore the unique global minimum, including the endpoint comparison. Rearranging the A-for-B exchange condition gives the *odds relation*

$$\frac{\theta_*}{1-\theta_*}=\frac{x_b}{1-x_b}\exp[-\delta/(RT)],\qquad
\theta_* = \frac{x_b e^{-\delta/(RT)}}{1-x_b+x_b e^{-\delta/(RT)}}.$$

For the worked case, $\theta_*\approx0.16856026$ and $\phi_*\approx-658.80722$ J/mol sites. Direct bounded minimization of the **full** $g_{\rm site}-(1-\theta)\mu_A-\theta\mu_B$ returns the same $\theta\approx0.16856026$. A solver's success flag alone would not suffice: compare the occupancy and energy with the independent formulas, and reject infeasible or nonfinite output. The [small Python implementation](boundary_one_state.py) performs these checks.

The equal-site excess from Lesson 11 is $\Gamma_B=S(\theta_*-x_b)/(A N_{\rm Av})\approx5.69235\times10^{-7}$ mol/m², or $5(0.16856026-0.10)\approx0.3428013$ atom/nm². Two equivalent boundaries produce $2S(\theta_*-x_b)\approx13.7121$ excess B atoms over $2A=40$ nm²; fractional *expected* atom counts are appropriate for the continuum site fraction. The reservoir supplies the net B and takes the same number of A atoms. In a finite closed cell, $x_b$ would change; that is a later, separate calculation.

At $\delta=0$, $\theta_*=x_b$, $\phi_*=0$ and the chosen excess is zero. Negative $\delta$ enriches B; positive $\delta$ depletes it. As $x_b$ tends to zero, $\theta_*/x_b$ tends to $e^{-\delta/(RT)}$; as $x_b$ tends to one, $(1-\theta_*)/(1-x_b)$ tends to $e^{\delta/(RT)}$. These are analytical limits, not calls to this lesson's numerical API at excluded endpoints.

## Paper route and optional code check

The paper route needs a calculator: compute $RT$, the odds multiplier, $\theta_*$, then compare two trial $\phi$ values and convert $\theta_*-x_b$ through $S/A$. Show the **reservoir exchange** and the area denominator. For an optional exact code check in the project's Poetry environment:

```python
from course.foundations.boundary_one_state import grand_potential, open_equilibrium

x_bulk, preference = 0.10, -5000.0
for theta in (0.10, 0.15, 0.25):
    print(theta, grand_potential(theta, x_bulk, preference))
print(open_equilibrium(x_bulk, preference))
```

The system and its boundary preference are invented, so $\phi_*$ is not a measured energy of any real interface, and one convex state cannot show a transition between boundary structures; that needs a second, compatible state ([Lesson 14](lesson_14_competing_states.md)).
