# Lesson 1 — a binary model you can check by hand

**Synthetic teaching model.** The parameters below are invented. No database,
fitted observation or Ni-X property enters this lesson. After this lesson you
should be able to derive the two chemical potentials, distinguish a local
instability from two-phase coexistence, and check a phase-fraction result by
conservation.

Prerequisites: molar Gibbs energy, partial derivatives, logarithms and a little
Python. Let $x$ be the mole fraction of component B among real atoms, $T$ the
temperature in K, $g_A^0$ and $g_B^0$ the pure-state molar Gibbs energies in
J/mol, and $\Omega$ a symmetric interaction energy in J/mol. One mole means
one mole of A+B atoms; there are no vacancies or sublattices. Define

$$
g(x,T)=(1-x)g_A^0+xg_B^0+RT[x\ln x+(1-x)\ln(1-x)]
+\Omega x(1-x).
$$

The $x\ln x$ terms are zero by their continuous limit at $x=0$ or $1$.
The molar gas constant is $R=8.31446261815324$ J/(mol K), consistent with
[NIST's 2022 CODATA value](https://physics.nist.gov/cuu/pdf/JPCRD2022CODATA.pdf)
(DOI: [10.1063/5.0279860](https://doi.org/10.1063/5.0279860)).
Only positive finite $T$, finite energies and $0\le x\le1$ are admitted. The
code returns finite pure-state $g$ at the endpoints, while derivative and
chemical-potential methods require $0<x<1$ because an absent component has a
logarithmically divergent chemical potential in this ideal mixing model.

## Derive the quantities before computing them

For an interior composition, differentiating the declared $g$ gives

$$
g_x=g_B^0-g_A^0+RT\ln\frac{x}{1-x}+\Omega(1-2x),\qquad
g_{xx}=\frac{RT}{x(1-x)}-2\Omega.
$$

For total Gibbs energy $G=n g(n_B/n)$ at fixed $T$, with $n=n_A+n_B$,
differentiate with respect to each amount:

$$
\mu_A=g-xg_x,\qquad \mu_B=g+(1-x)g_x.
$$

Check $(1-x)\mu_A+x\mu_B=g$ before trusting a numerical result. Positive
$g_{xx}$ is a local stability check. Negative $g_{xx}$ marks a spinodal
instability; it is **not** the binodal, which requires a common tangent and a
lower convex envelope. For this symmetric model, $T_c=\Omega/(2R)$ when
$\Omega>0$. At $T\ge T_c$, no two-phase miscibility gap exists in this model.

At $T<T_c$, linear pure-state terms tilt the whole curve but do not change
the coexistence compositions. Write $x_\alpha<1/2$ and
$x_\beta=1-x_\alpha$. Symmetry makes the common-tangent slope
$g_B^0-g_A^0$, so solve the **mixing** derivative

$$
RT\ln\frac{x_\alpha}{1-x_\alpha}
+\Omega(1-2x_\alpha)=0
$$

on the lower-composition branch. $x=1/2$ is also stationary for the symmetric
mixing part, but below $T_c$ it is a central maximum and **not** a coexistence
endpoint. Check the two phases have equal $\mu_A$ and $\mu_B$, and that their
common tangent lies no higher than $g(x)$ throughout the interior. For a bulk
composition $z$ between the endpoints, the beta fraction is
$f_\beta=(z-x_\alpha)/(x_\beta-x_\alpha)$. Check
$(1-f_\beta)x_\alpha+f_\beta x_\beta=z$ and $0\le f_\beta\le1$.

## Run and challenge the model

From the repository root, run this example. It prints only synthetic quantities.

```bash
poetry run python - <<'PY'
from course.foundations.regular_solution import BinaryRegularSolution, lever_fraction

model = BinaryRegularSolution(temperature=600.0, omega=20000.0,
                              g_a0=1000.0, g_b0=1200.0)
left, right = model.binodal()
fraction = lever_fraction(0.4, left, right)
print(f"coexistence x_B = {left:.6f}, {right:.6f}")
print(f"beta fraction at z_B=0.4 = {fraction:.6f}")
print(f"chemical potential gap = {abs(model.chemical_potentials(left)[1] - model.chemical_potentials(right)[1]):.3e} J/mol")
PY
```

Observed in the pinned Poetry environment:

```text
coexistence x_B = 0.021032, 0.978968
beta fraction at z_B=0.4 = 0.395609
chemical potential gap = 3.638e-12 J/mol
```

Exercises: (1) Derive both chemical potentials from $G(n_A,n_B)$ without
looking at the code. (2) Change $g_A^0-g_B^0$ and check that the coexistence
compositions stay fixed while the tangent slope changes. (3) Set $\Omega=0$:
the model must reject a binodal request, even though $x=1/2$ is stationary
for equal pure-state energies. (4) Try a bulk $z$ outside the coexistence
interval: a phase fraction there is inadmissible. (5) Enter $\Omega=20$ as if
20 kJ/mol were 20 J/mol; explain the false no-gap conclusion and use
$\Omega/(RT)$ to expose the unit error. (6) Explain why neither these checks
nor a plotted curve validate Ni-Cu segregation.

The accompanying [implementation](regular_solution.py) uses a bounded
bisection for this one symmetric model; it is not a general CALPHAD equilibrium
solver. The [tests](../../tests/test_course_foundations.py) compare analytic
limits, finite-difference derivatives, branch curvature, common-tangent
conditions and mass conservation. These checks cover only the stated synthetic
equations and implementation.
