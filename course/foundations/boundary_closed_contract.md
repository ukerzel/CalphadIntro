# One-state closed-cell boundary contract

This closes the *same* [boundary geometry](synthetic_boundary_contract.md) and [one-state boundary-site energy](boundary_one_state_contract.md), without changing their functions or open-reservoir result. Everything remains an invented A/B substitutional model at hydrostatic $T=1000$ K and $p=100000$ Pa, not a Ni–X calculation or physical grain-boundary energy.

## Cell, inventory and energy basis

There are $K=2$ equivalent boundaries, $S=100$ sites and $A=20$ nm² **per** boundary. Write $M=KS=200$ boundary sites and $N_b$ bulk sites. The main cell has $N_b=8000$, starting bulk B fraction $x_0=0.10$ and starting boundary occupancy $\theta_0=0.25$, hence fixed $B_{\rm tot}=N_bx_0+M\theta_0=850$ expected B atoms and fixed $A_{\rm tot}=N_b+M-B_{\rm tot}=7350$. Trial boundary occupancy $\theta$ forces

$$x_b(\theta)={B_{\rm tot}-M\theta\over N_b}.$$

No external reservoir supplies B or accepts A. A trial is feasible only if $0\le\theta\le1$ and $0\le x_b(\theta)\le1$. For a general fixed $B_{\rm tot}$, its exact feasible interval is $\max(0,(B_{\rm tot}-N_b)/M)\le\theta\le\min(1,B_{\rm tot}/M)$. This also catches the 30-B, 80-boundary-site feasibility control of [Lesson 11 worksheet task B4](lesson_11_worksheet.md) in that task's own geometry; for the main 850-B cell, all $0\le\theta\le1$ are feasible. The numerical solution subset uses $N_b\in\{8000,80000,800000\}$, $x_0\in[0.10,0.90]$, fixed $\theta_0=0.25$ and $\delta\in[-10000,10000]$ J/mol sites. These ranges ensure all $\theta\in[0,1]$ are feasible with interior bulk composition. The detecting grid is $x_0=0.10,0.50,0.90$ and $\delta=-5000,0,+5000$ at each $N_b$.

At each trial use the binary-family I1 ALPHA ideal $g_b(x)=C+\Delta x+RTq(x)$ and the one-state $g_s(\theta)=C+(\Delta+\delta)\theta+RTq(\theta)$, both J/mol occupied sites, with $C=1000-10T$, $\Delta=12000$ J/mol, $R=8.3145$ J/(mol K), $q(y)=(1-y)\ln(1-y)+y\ln y$ and continuous $0\ln0=0$. The constrained **total cell** energy is

$$G_{\rm cell}(\theta)={N_b g_b[x_b(\theta)]+M g_s(\theta)\over N_{\rm Av}}\quad\mathrm{J}.$$

Here site counts divided by $N_{\rm Av}$ convert atoms to moles. The numerically scaled objective is $\bar g=G_{\rm cell}N_{\rm Av}/(N_b+M)$ in J/mol of *all cell sites*. The scaling is a positive constant within one fixed cell, so it selects the same minimum and avoids optimizing numbers near $10^{-16}$ J. Do not subtract an open-reservoir $\mu$ term, hold $x_b=x_0$ when $\theta$ changes, or compare total energies across different $N_b$ as if they were the same system.

## Independent exchange condition and limits

The fixed-inventory derivative is

$$\frac{d\bar g}{d\theta}={M\over N_b+M}\left[\delta+RT\ln{\theta\over1-\theta}-RT\ln{x_b(\theta)\over1-x_b(\theta)}\right].$$

The $\Delta$ terms cancel because exactly one bulk A/B exchange accompanies each boundary substitution. The bracket is $g_s'(\theta)-g_b'[x_b(\theta)]$, and its derivative is

$$RT\left[{1\over\theta(1-\theta)}+{M/N_b\over x_b(\theta)[1-x_b(\theta)]}\right]>0.$$

For the declared grid, endpoint limits are $-\infty,+\infty$, so a unique interior root is the global minimum. The root method uses this exchange residual directly; the separate bounded optimizer evaluates the original total $\bar g$. Their agreement detects an ensemble/reference error. At $\delta=0$, all sites have the same ideal energy and the minimum is $\theta=x_b=z=B_{\rm tot}/(N_b+M)$, which for the main cell is $850/8200\approx0.1036585366$, **not** the starting $x_0=0.10$. At nonzero preference, the equal-site excess per area is $\Gamma_B=S(\theta-x_b)/(A N_{\rm Av})$, using the *new* bulk composition and both equivalent boundaries. Whole-cell count route: $M(\theta-x_b)/(KA N_{\rm Av})$.

For a size sequence $N_b=8000,80000,800000$ with the same $x_0=0.10$, $\theta_0=0.25$, $M=200$ and $\delta=-5000$, $B_{\rm tot}=N_bx_0+50$. As $N_b\to\infty$, the bulk composition tends to $x_0$, so the closed root tends to the [open equilibrium](boundary_one_state.py) at fixed $x_b=x_0$. The three computed occupancy errors against that open value must decrease strictly; the last error must be at most $5\times10^{-5}$. This is a limit check, not a claim that an 8000-site bulk is already an infinite reservoir.

## Numerical checks and scope

| Surface | Requirement |
|---|---|
| Independent energy | At the 27 $(N_b,x_0,\delta)$ cases and trial $\theta=0,0.10,0.25,0.50,1$, compare the binary-family energy route with 65-digit independent $q$ calculation to $\le10^{-7}$ J/mol all sites. Check pure endpoint limits. |
| Balance | For every trial and equilibrium, bulk B+boundary B equals $B_{\rm tot}$ and A totals the complement within $10^{-9}$ atoms; verify changing $\theta$ changes $x_b$ by $-M\Delta\theta/N_b$. Reject nonfinite, out-of-range or infeasible input; do not clip. |
| Independent root | Bracket the strict-convexity exchange residual on the declared interior domain. Residual magnitude $\le10^{-6}$ J/mol sites; root and direct bounded minimum differ by $\le2\times10^{-6}$ occupancy and $\le10^{-6}$ J/mol all sites. Compare each returned solver value to fresh evaluation; reject failed, nonfinite, out-of-bounds or inconsistent results. |
| Limits/reference | At $\delta=0$, $\theta=x_b=z$ within $2\times10^{-6}$; at $x_0=0.10,\delta=-5000$ size sequence, errors decrease and final error $\le5\times10^{-5}$. Negative preference enriches boundary relative to its *new* bulk; positive depletes. |
| Excess/negative controls | Count and site-density routes for $\Gamma_B$ agree within $10^{-10}$ mol/m². Dividing whole-cell excess by only $A$ must fail by factor two. Holding $x_b=x_0$ while changing $\theta$ must fail fixed B balance. Wrong preference sign must fail occupancy/sign. |

No second structural branch, crossing, phase transition, finite-size physical scaling, measured parameter, or real interface is established. General ideal-solution source: R. Jaramillo, “Solution Models — Ideal, Dilute, and Regular,” MIT 3.020 Lecture 17, 2021, [original notes](https://ocw.mit.edu/courses/3-020-thermodynamics-of-materials-spring-2021/mit3_020s21_l17.pdf), no DOI listed. The closed ensemble, numbers and checks here are original; the [binary-family](binary_family_contract.md), [boundary geometry](synthetic_boundary_contract.md) and [one-state open-reservoir](boundary_one_state_contract.md) contracts are the local scientific references. Numerical method API: SciPy developers, [`minimize_scalar`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html) and [`brentq`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html), installed version 1.18.1.
