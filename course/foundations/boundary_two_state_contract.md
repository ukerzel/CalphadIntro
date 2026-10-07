# Two-state closed-cell boundary contract

This extends the [closed-cell contract](boundary_closed_contract.md) to two compatible synthetic boundary states in one closed cell. That contract is itself based on the [boundary geometry](synthetic_boundary_contract.md) and the [binary-family I1 ALPHA bulk](binary_family_contract.md). All inputs and structural labels are invented. A branch crossing in this model is not evidence of a real interface phase transition.

## Same ensemble and aligned reference

Keep $T=1000$ K, hydrostatic $p=100000$ Pa, $N_b=8000$ bulk sites, $K=2$ equivalent boundaries of $S=100$ occupied sites and $A=20$ nm² each. Both boundaries occupy the *same selected structural state* in a trial; mixed-state domains and junction energies are outside this model. Let $M=KS=200$, $\theta_0=0.25$, starting bulk fraction $x_0\in[0.10,0.90]$, and fixed total $B_{\rm tot}=N_bx_0+M\theta_0=8000x_0+50$. Each $x_0$ specifies a **different closed cell inventory**; compare State I and II only at the same $x_0$, $B_{\rm tot}$, geometry and reference. For either state's trial occupancy, $x_b=(B_{\rm tot}-M\theta)/N_b$; all $0\le\theta\le1$ are feasible and bulk interior in this declared range.

Use the same ideal $q(y)=(1-y)\ln(1-y)+y\ln y$ and the binary-family I1 $g_b(y)=C+\Delta y+RTq(y)$, with continuous pure limits, $C=1000-10T$, $\Delta=12000$ J/mol, $R=8.3145$ J/(mol K). Define *two* boundary-site functions with the **same** pure-A/bulk reference, entropy, site count, and amount basis:

$$g_{s,i}(\theta)=g_b(\theta)+\eta_i+\delta_i\theta\quad\mathrm{J/mol\ boundary\ sites}.$$

| State | Invented baseline $\eta_i$ | Invented B preference $\delta_i$ |
|---|---:|---:|
| I | 0 J/mol boundary sites | −5000 J/mol boundary sites |
| II | +2000 J/mol boundary sites | −10000 J/mol boundary sites |

The baseline represents a hypothetical structure's occupancy-independent energy difference relative to the same reference, **not** a measured grain-boundary energy. The allowed sensitivity probes change only $\eta_{II}$ to 1900 or 2100 J/mol boundary sites; $\eta_I$, both preferences and all other conditions stay fixed. No re-fitting is done.

For state $i$, minimize its own constrained total energy

$$\bar g_i(\theta;x_0)={N_b g_b[x_b(\theta)]+M g_{s,i}(\theta)\over N_b+M}
=\bar g_{\rm closed}(\theta;x_0,\delta_i)+{M\eta_i\over N_b+M}$$

in J/mol of **all cell sites**. Here $\bar g_{\rm closed}(\theta;x_0,\delta)$ is the scaled objective $\bar g$ of the [closed-cell contract](boundary_closed_contract.md) for $N_b=8000$, $B_{\rm tot}=8000x_0+50$ and one-state preference $\delta$, so that its boundary-site energy is $g_b(\theta)+\delta\theta$. Its finite-cell energy in J is $G_{\rm cell,i}=(N_b+M)\bar g_i/N_{\rm Av}$. The constant baseline does not move that state's occupancy minimum. Use the closed-cell contract's direct bounded total-energy minimization and independently derived exchange root for each state; do not compare unminimized trials or an open-reservoir grand potential with this closed total energy. Return both state minima even at a crossing; an equal energy does not imply equal occupancy.

## Crossing, uniqueness and sensitivity

Define $D(x_0;\eta_{II})=\min_\theta\bar g_{II}-\min_\theta\bar g_I$, with *both* minima evaluated at the same $B_{\rm tot}$. $D>0$ selects State I; $D<0$ selects State II. For the base $\eta_{II}=2000$, require $D(0.10)>5$ and $D(0.25)<-5$ J/mol all sites. A bracketed root in $(0.10,0.25)$ is the one model ordering switch; the crossing residual must be $\le10^{-6}$ J/mol all sites.

There is an analytical uniqueness check. At fixed $x_0$, State II's preference is more negative, so its strictly convex exchange residual reaches zero at a larger $\theta$ than State I. With the same total B, $x_{b,II}<x_{b,I}$. The binary-family ideal bulk exchange slope $g_b'(x)$ increases strictly with $x$, and the envelope derivative is $d\min\bar g_i/dB_{\rm tot}=g_b'(x_{b,i})/(N_b+M)$. Since $dB_{\rm tot}/dx_0=N_b>0$, $D'(x_0)<0$ throughout the declared domain. A 17-point uniform $x_0$ scan is a detecting check, while this argument establishes at most one crossing within the declared model. The crossing is a switch between **constrained uniform-state branches**; no mixed-domain equilibrium, interfacial junction cost, kinetic path or real transition is solved.

Increasing $\eta_{II}$ by 100 adds exactly $M(100)/(N_b+M)\approx2.43902439$ J/mol all sites to $D$ at every $x_0$, without moving either within-state optimum. It must shift the crossing to larger $x_0$; decreasing by 100 shifts it to smaller $x_0$. Both perturbed roots must remain in $(0.10,0.25)$ and move by at least $10^{-3}$ in $x_0$. This is *parameter sensitivity* for invented energies, not material uncertainty.

## Numerical checks

| Surface | Requirement |
|---|---|
| State energies | At $x_0=0.10,0.25,0.50,0.90$ and each state, compare closed-cell full-energy minima plus baseline with a separate 65-digit Decimal bulk+boundary root/energy route: $|\Delta\theta|\le2\times10^{-6}$, $|\Delta\bar g|\le10^{-6}$ J/mol all sites. Both branches conserve B/A within $10^{-9}$ atoms. |
| Base crossing | $D(0.10)>5$, $D(0.25)<-5$ J/mol all sites; bracketed crossing residual $\le10^{-6}$ J/mol all sites and location error vs independent Decimal crossing $\le10^{-7}$ in $x_0$. Exactly one ordering change on the 17-point scan; analytical monotonicity as above. |
| Sensitivity | Repeat bracketed crossing for $\eta_{II}=1900,2100$; both roots remain inside the base bracket, ordered $x_{1900}<x_{2000}<x_{2100}$ with each movement $\ge10^{-3}$. Check exact constant-baseline effect on $D$ at $x_0=0.10,0.25,0.50$ to $\le10^{-9}$ J/mol all sites and unchanged occupancies to $\le10^{-9}$. |
| Negative controls | Reject invalid/nonfinite $x_0$, baseline outside the three declared values, crossed ensemble/reference, infeasible or unbalanced state outputs, failed/nonfinite/misbracketed crossing root or inconsistent returned residual. Deliberately omitting the State II baseline or comparing before within-state minimization must fail base ordering/crossing controls. |

Source context: T. Frolov and Y. Mishin, “Thermodynamics of coherent interfaces under mechanical stresses. I. Theory,” *Phys. Rev. B* 85, 224106 (2012), doi:10.1103/PhysRevB.85.224106, [author manuscript](https://arxiv.org/abs/1304.0144), and T. Frolov and Y. Mishin, “Phases, phase equilibria and phase rules in low-dimensional systems,” *J. Chem. Phys.* 143, 044706 (2015), doi:10.1063/1.4927414, [author manuscript](https://arxiv.org/abs/1506.08890). Their real-interface theory does not validate these invented branches. For numerical methods, use installed SciPy 1.18.1 `brentq` and the [official API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html); no new dependency.
