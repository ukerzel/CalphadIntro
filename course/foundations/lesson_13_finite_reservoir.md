# Lesson 13 — one boundary state in a finite closed cell

Meetings 30–31. Continue [Lesson 11's two-boundary geometry](lesson_11_geometry.md) and [Lesson 12's one-state energy](lesson_12_reservoir.md), using the [closed-cell contract](boundary_closed_contract.md), [worksheet](lesson_13_worksheet.md) and [instructor guide](../instructor/lesson_13_guide.md). This is the same invented A/B model at 1000 K and 100000 Pa.

**Exit goal:** conserve both atom inventories while occupancy varies, minimize total cell energy, test the answer with an independently derived exchange root, and recover the open-reservoir limit as the bulk grows. One structural state cannot establish an interface transition.

## 13A — moving B changes the finite bulk

Keep two equivalent 100-site boundaries ($M=200$ boundary sites total, $A=20$ nm² each) and $N_b=8000$ bulk sites. Initially, $x_0=0.10$ in the bulk and $\theta_0=0.25$ at the boundary, so the **closed** cell contains $8000(0.10)+200(0.25)=850$ B atoms and 7350 A atoms. “Atoms” in this continuum site-fraction model are expected counts; a physical microstate would require integer occupations.

If the boundary has trial occupancy $\theta$, the bulk must have

$$x_b(\theta)=\frac{850-200\theta}{8000}.$$

For example, $\theta=0.35$ puts 70 B atoms on the boundaries and 780 B in bulk, so $x_b=0.0975$. Holding bulk $x_b=0.10$ at that occupancy would give 870 B atoms and violate the fixed inventory. A moves the opposite way at every substitution. In this 850-B cell, every $0\le\theta\le1$ leaves a feasible bulk fraction. A very B-poor cell could restrict that interval: with only 30 B atoms in the same 200-boundary-site geometry, $\theta$ cannot exceed $30/200=0.15$.

The [binary-family I1 ALPHA](binary_family_contract.md) bulk molar Gibbs function is $g_b(x)$. The boundary function is the same [one-state](boundary_one_state_contract.md) ideal site function $g_s(\theta)=g_b(\theta)+\delta\theta$, with an invented preference $\delta$. For a fixed cell, compare the **total** Gibbs energy

$$G_{\rm cell}(\theta)=\frac{N_b g_b[x_b(\theta)]+200g_s(\theta)}{N_{\rm Av}}\quad\mathrm{J}.$$

Each atom count divided by $N_{\rm Av}$ is mol of occupied sites. A convenient numerical equivalent is $\bar g=G_{\rm cell}N_{\rm Av}/8200$ in J/mol of all cell sites. It has the same minimum because 8200 is fixed. The open-reservoir $-\mu_A,-\mu_B$ subtraction from Lesson 12 is **not** part of this fixed-inventory energy. These two functions answer different physical questions.

### Worked trial comparison

Use $\delta=-5000$ J/mol boundary sites and fixed B=850. At $\theta=0.10,0.15,0.20,0.25$, the bulk B fractions are $0.10375,0.10250,0.10125,0.10000$. The corresponding $\bar g$ values are about $-10537.4054,-10541.3690,-10541.1526,-10537.6008$ J/mol all sites. The lowest **supplied trial** is 0.15. These are energy comparisons of the *same* closed cell; they cannot be replaced by fixed-$x_b$ Lesson 12 potentials.

## 13B — independent exchange check

Because $dx_b/d\theta=-200/N_b$, differentiating the total energy gives

$$\frac{d\bar g}{d\theta}=\frac{200}{N_b+200}\left[g_s'(\theta)-g_b'(x_b)\right]
=\frac{200}{N_b+200}\left[\delta+RT\ln\frac{\theta}{1-\theta}-RT\ln\frac{x_b}{1-x_b}\right].$$

Both $x_b$ and $\theta$ change while total B stays fixed. The bracket increases strictly with $\theta$: its derivative is $RT[1/(\theta(1-\theta))+(200/N_b)/(x_b(1-x_b))]>0$. It runs from $-\infty$ at the lower end of the feasible $\theta$ interval to $+\infty$ at the upper end, so it crosses zero once and the root is the unique global minimum. The [small solver](boundary_closed.py) evaluates total energy directly with a bounded minimizer and separately solves this exchange root. It rejects invalid output and checks that the two answers agree.

For the worked cell, the exchange root is $\theta_*\approx0.17160752$, the direct minimum is about 0.17160753, and $x_b(\theta_*)\approx0.10195981$. The boundary holds about 34.3215 B and the bulk 815.6785 B; together they still hold 850. The chosen equal-site excess is $\Gamma_B=S(\theta_*-x_b)/(A N_{\rm Av})\approx5.78264\times10^{-7}$ mol/m², or $0.348239$ atom/nm². Independently, both boundaries have $200(\theta_*-x_b)\approx13.92954$ excess B atoms over $2A=40$ nm². The excess uses the **new** bulk $x_b$, not the starting $x_0$.

The negative preference enriches the boundary relative to its final bulk composition, although the supplied initial occupancy 0.25 happens to be *above* the selected 0.1716. Preference sign compares **equilibrium regions**, not necessarily the direction of motion from an arbitrary initial trial. At $\delta=0$, the unique equilibrium equalizes all site fractions: $\theta_*=x_b=B_{\rm tot}/(N_b+200)=850/8200\approx0.10365854$, rather than the starting $x_0=0.10$. The chosen excess then vanishes.

## Make the bulk large without changing the boundary

Hold 200 boundary sites and the initial $x_0=0.10,\theta_0=0.25,\delta=-5000$ while increasing $N_b$ to 80000 and 800000. Each cell has its **own** conserved total B, $N_bx_0+50$. The closed exchange roots are about 0.17160752, 0.16887603 and 0.16859195. Their distances to [Lesson 12's open result](lesson_12_reservoir.md), $0.16856026$ at fixed reservoir $x_b=0.10$, are about 0.00304726, 0.00031577 and 0.00003169. The bulk shift also shrinks: about 0.10195981, 0.10020281 and 0.10002035. As the bulk grows, the closed cell approaches the open reservoir.

## Paper route and optional code check

On paper, start with total B, compute $x_b(\theta)$ for each trial, evaluate both regions' energies in one basis, then solve the exchange equation with a calculator or bracketed guesses. Check B and A totals and divide whole-cell excess by **both** areas. For the optional exact code route in this project's Poetry environment:

```python
from course.foundations.boundary_closed import closed_trial, closed_equilibrium

for theta in (0.10, 0.15, 0.20, 0.25):
    print(theta, closed_trial(theta, 850, -5000, 8000))
print(closed_equilibrium(0.10, -5000, 8000))
```

The paper route is sufficient. The model and its preference are invented, so these numbers describe no real Ni–Cu boundary, and a transition would need a second, compatible structural state, which [Lesson 14](lesson_14_competing_states.md) adds.
