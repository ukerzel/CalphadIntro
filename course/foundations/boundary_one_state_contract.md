# One-state open-reservoir boundary contract

This contract specializes the [boundary geometry contract](synthetic_boundary_contract.md) to one original, noninteracting A/B boundary-site energy for meetings 28–29. All quantities are synthetic. This contract covers only the declared fixed-temperature domain and does not define a Ni–X boundary, a structural transition, an experimental fit or a real grain-boundary energy.

## Physical and reference choices

Keep the boundary geometry contract's two equivalent boundaries: $K=2$, area $A=20$ nm² and $S=100$ sites **per** boundary, $N_b=8000$ bulk sites, one atom per site, fixed hydrostatic $T=1000$ K and $p=100000$ Pa. The bulk is the [binary-family](binary_family_contract.md) **I1 ALPHA only** model, with $R=8.3145$ J/(mol K), pure endmember difference $\Delta=12000$ J/mol and $C(T)=1000-10T$ J/mol. For this lesson's numerical route, the supported domain is $x_b\in[0.01,0.99]$ and a single preference $\delta\in[-10000,10000]$ J/mol of boundary sites; the geometry contract's wider physical statement $0<x_b<1$ is unchanged. $\delta$ is an **invented** change to the boundary B-for-A site-energy difference relative to the binary-family $\Delta$. Negative $\delta$ favors B; no fitted or measured parameter is implied.

For one mole of occupied boundary sites at B fraction $\theta\in[0,1]$, define the same ideal mixing function $q(y)=(1-y)\ln(1-y)+y\ln y$ with the continuous $0\ln0=0$ limits. The **one-state** site Gibbs function is

$$g_{\rm site}(\theta)=C(T)+(\Delta+\delta)\theta+RTq(\theta)
=g_{\rm I1,ALPHA}(\theta)+\delta\theta\quad\mathrm{J/mol\ sites}.$$

This aligns the pure-A/reference and ideal term with the bulk model and varies exactly one boundary preference. It has no structural baseline grain-boundary energy. The open reservoir fixes the binary-family I1 pair

$$\mu_A=C(T)+RT\ln(1-x_b),\qquad
\mu_B=C(T)+\Delta+RT\ln x_b.$$

The cell exchanges B for A at fixed site count, so the boundary-site **excess grand potential relative to equal-site bulk** is

$$\phi(\theta)=g_{\rm site}(\theta)-(1-\theta)\mu_A-\theta\mu_B
=RT\left[(1-\theta)\ln\frac{1-\theta}{1-x_b}
+\theta\ln\frac{\theta}{x_b}\right]+\delta\theta\quad\mathrm{J/mol\ sites}.$$

Endpoint terms use continuous limits. Multiplying $\phi$ by $KS/N_{\rm Av}$ would give a **cell excess potential in J** for these chosen equal sites, and dividing by $KA$ would give a **reference-dependent excess potential per area**. Neither is an absolute physical grain-boundary free energy; no such value is reported here. Using $\mu_B$ alone omits the A-for-B exchange and changes the model's minimizer.

## Independent analytical solution and limits

For $0<\theta<1$,

$$\phi'(\theta)=\delta+RT\ln\frac{\theta}{1-\theta}
-RT\ln\frac{x_b}{1-x_b},\qquad
\phi''(\theta)=\frac{RT}{\theta(1-\theta)}>0.$$

Strict convexity and the endpoint derivative limits give one global minimum. The exchange-equilibrium condition is $g'_{\rm site}(\theta)=\mu_B-\mu_A$, yielding

$$\frac{\theta_*}{1-\theta_*}=
\frac{x_b}{1-x_b}\exp\!\left(-\frac{\delta}{RT}\right),\qquad
\theta_*={x_b e^{-\delta/(RT)}\over 1-x_b+x_b e^{-\delta/(RT)}}.$$

The minimum potential is independently $\phi_*=-RT\ln[1-x_b+x_b e^{-\delta/(RT)}]$. These identities provide a different route from bounded direct minimization of the full $g_{\rm site}-\mu$ expression. At $\delta=0$, $\theta_*=x_b$, $\phi_*=0$ and the boundary geometry contract's equal-site excess $\Gamma_B=S(\theta_*-x_b)/(A N_{\rm Av})=0$. Negative preference gives $\theta_*>x_b$ and positive excess; positive preference gives depletion. As $x_b\to0^+$, $\theta_*/x_b\to e^{-\delta/(RT)}$; as $x_b\to1^-$, $(1-\theta_*)/(1-x_b)\to e^{\delta/(RT)}$. These are analytical limits, not API calls at the excluded bulk endpoints. $\theta_*$ always lies strictly between 0 and 1 for the declared finite inputs; direct energy evaluation at $\theta=0,1$ remains finite.

The result is a one-state equilibrium **within this declared synthetic model**. Enrichment does not establish a second structural state, a phase transition, kinetics or a material prediction. The [closed-cell contract](boundary_closed_contract.md) closes the total A/B inventory using this same $g_{\rm site}$ and compares constrained total energy at the changed bulk composition; the [two-state contract](boundary_two_state_contract.md) adds a second compatible state under its own definitions.

## Numerical checks and domain

| Surface | Required criterion |
|---|---|
| Input/domain | Accept finite scalar $x_b\in[0.01,0.99]$, $\delta\in[-10000,10000]$ J/mol sites and $\theta\in[0,1]$ for energy. Reject arrays, NaN/Inf, out-of-range values, clipping and altered T/p/phase. |
| Independent potential | At $x_b=0.01,0.10,0.50,0.90,0.99$, $\delta=-10000,0,+10000$, and $\theta=0,0.10,0.50,0.90,1$, compare the full binary-family energy/chemical-potential route with at least 50-digit independent logarithmic expression to $\le10^{-7}$ J/mol sites. Exact endpoint limits are included. |
| Analytical occupancy | At the 15 $(x_b,\delta)$ pairs, compare stable closed-form implementation to at least 50-digit independent ratio expression to $\le10^{-12}$ absolute occupancy. Verify zero-preference identity and enrichment/depletion signs. |
| Direct minimizer | Bounded scalar minimization of full $g_{\rm site}-\mu$ on $[0,1]$ must return a finite feasible point, success/status and objective; compare direct occupancy with the independent analytic value to $\le2\times10^{-6}$, and objective with the independent minimum expression to $\le10^{-6}$ J/mol sites at all 15 pairs. Check returned objective against fresh evaluation; no success flag alone is acceptance. |
| Excess and balances | Compute $\Gamma_B$ from the boundary geometry contract's $S/A$ site-density formula and independently from whole-cell B counts and $KA$; difference $\le10^{-10}$ mol/m². An open +20 B boundary substitution must exchange −20 A, with opposite reservoir changes. |
| Controls | At $x_b=0.10,\delta=-5000$, reject reversed preference sign and use of $\mu_B$ alone through the analytical occupancy/control comparison; dividing whole-cell excess by only $A$ must double the area result and fail. Reject failed, nonfinite, out-of-bounds or internally inconsistent solver output. A zero-preference result at $\theta\ne x_b$ must fail. |

The direct route uses the pinned SciPy bounded scalar minimizer with an explicit positional tolerance; it is a numerical check, not an independent physical model. Its method and output are those of the installed SciPy version. Tolerances, input cases, state and reference stay as declared here; a failure near a domain boundary is reported as a failure and never hidden by clipping.

## Sources and provenance

[1] R. Jaramillo, “Solution Models — Ideal, Dilute, and Regular,” MIT 3.020, Lecture 17, 2021, [original notes](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l17.pdf). The ideal entropy form is standard; the numerical site preference, references and domain here are original choices. No DOI is listed for these lecture notes.

[2] T. Frolov and Y. Mishin, “Thermodynamics of coherent interfaces under mechanical stresses. I. Theory,” *Phys. Rev. B*, vol. 85, 224106, 2012, doi:10.1103/PhysRevB.85.224106, [author manuscript](https://arxiv.org/abs/1304.0144). Its stressed-interface scope is excluded here.

[3] SciPy developers, “`scipy.optimize.minimize_scalar`,” [official API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html), accessed 29 September 2026. The installed `1.18.1` implementation, not a future documentation page alone, is the runtime authority here. No DOI is listed for this API page.
