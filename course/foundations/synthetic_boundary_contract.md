# Synthetic boundary geometry contract

This contract fixes **geometry, amounts, ensemble, reference and mechanical conditions** for the one-state/open-reservoir ([Lesson 12](lesson_12_reservoir.md)), finite-inventory ([Lesson 13](lesson_13_finite_reservoir.md)) and two-state ([Lesson 14](lesson_14_competing_states.md)) teaching sequence. It defines no boundary free-energy function or solver. [Lesson 11](lesson_11_geometry.md) teaches its bookkeeping. All species, sites and dimensions are invented; no Ni–Cu or other material value follows.

## System and bulk reference

Use the [binary-family I1](binary_family_contract.md) **ideal, one-phase ALPHA** model for a synthetic A/B bulk. The allowed temperature and pressure for these boundary examples are fixed at $T=1000$ K and $p=100000$ Pa. Bulk composition $x_b$ means B **atom mole fraction** among occupied bulk substitutional sites. Only ALPHA is allowed; no phase split, vacancy, interstitial, adsorption from a gas, chemical reaction or moving boundary is in this teaching model. The binary-family $g_{\rm ALPHA}(T,x)$, R and pure references remain unchanged. The boundary is an additional model object, not a renamed bulk phase.

For open examples, a sufficiently large bulk reservoir is represented by fixed $0<x_b<1$ and the corresponding binary-family pair $\mu_A,\mu_B$ at this $T,p$; the binary-family contract does not define endpoint chemical-potential calls. Each boundary substitution B-for-A sends one A to the reservoir and draws one B from it: the relevant exchange driving force is $\Delta\mu=\mu_B-\mu_A$. Supplying B alone would change the fixed site count and is outside this contract. For closed examples, total A and B atom counts are each conserved and $x_b$ must be determined from the remaining bulk inventory; holding it fixed while B moves to the boundary violates the declared finite-sample model. At a closed-route pure-bulk endpoint, evaluate finite energies by their limiting definitions rather than call an undefined chemical-potential derivative.

## Fixed geometric and mechanical choice

The teaching cell has **two equivalent planar boundaries**, each of area $A=20\ \mathrm{nm}^2=2\times10^{-17}\ \mathrm{m}^2$. Each boundary has $S=100$ fixed, equivalent substitutional sites. A separate bulk region has $N_b=8000$ occupied substitutional sites. Thus $K=2$, $N_{\rm gb}=KS=200$, $N_{\rm cell}=N_b+KS=8200$ occupied sites/atoms and total boundary area $K A=40\ \mathrm{nm}^2=4\times10^{-17}\ \mathrm{m}^2$. The two boundaries share the same mean B-site occupancy $\theta\in[0,1]$ and structural state. $\theta$ is a site fraction (dimensionless); $KS\theta$ is an expected B count in a mean-field description. The worked integer examples also admit literal atom counts.

$A$ is a fixed normalization area, not a variable to minimize. The idealized lattice is hydrostatic at the stated pressure with no imposed shear, coherency strain, area change, elastic work, line defects, free surfaces or mechanical transition. Two-state comparisons must use the **same** $T,p,A,K,S,N_b$, atom reference and mechanical constraints. Changing area, site number, deformation or boundary equivalence requires a new contract and compatible thermodynamic potential; dividing by $2A$ without proving two equivalent interfaces is invalid. This simple model is deliberately narrower than stressed-interface thermodynamics [1].

## Inventories and selected excess convention

Let $C_i$ denote **atom counts**, and let $N_{\rm Av}=6.02214076\times10^{23}\ \mathrm{mol}^{-1}$ be the exact SI Avogadro constant [2]. At bulk fraction $x_b$ and boundary occupancy $\theta$:

$$C_B^{\rm bulk}=N_bx_b,\quad C_B^{\rm gb}=KS\theta,\quad C_B^{\rm cell}=N_bx_b+KS\theta,$$
$$C_A^{\rm bulk}=N_b(1-x_b),\quad C_A^{\rm gb}=KS(1-\theta),\quad C_A^{\rm cell}+C_B^{\rm cell}=N_{\rm cell}.$$

Amounts in mol are $n_i=C_i/N_{\rm Av}$; no energy in J/mol may multiply a raw atom count. For this **equal-site reference**, define B excess relative to a homogeneous bulk fraction filling the same total number of sites:

$$\Gamma_B=\frac{C_B^{\rm cell}-x_bN_{\rm cell}}{K A N_{\rm Av}}=\frac{S(\theta-x_b)}{A N_{\rm Av}}\quad\mathrm{mol/m^2}.$$

The first expression audits the whole-cell subtraction; the second audits the boundary-only count. They must agree. $\Gamma_B=0$ when $\theta=x_b$ and can be negative for depletion. It is a **chosen synthetic excess convention**: fixed equal site capacities and a bulk reference at the actual $x_b$. It is not automatically the Gibbsian excess of an arbitrary real grain boundary with different atomic density or a unique dividing surface. Boundary site occupancy $\theta$ and excess $\Gamma_B$ are different observables.

## Open and closed constraints

| Route | Fixed quantities | Allowed change and test |
|---|---|---|
| Open reservoir (one state) | $T,p,A,K,S,N_b,x_b,\mu_A,\mu_B$ and one boundary structural state | A/B substitution at fixed $KS$ changes the cell's $C_B$ by $+q$ and $C_A$ by $-q$; the reservoir changes B by $-q$ and A by $+q$. The combined inventory is conserved. |
| Closed sample | $T,p,A,K,S,N_b,C_A^{\rm total},C_B^{\rm total}$ and one structural state | Boundary and bulk exchange internally: $C_B^{\rm total}=N_bx_b+KS\theta$ and $C_A^{\rm total}=N_b(1-x_b)+KS(1-\theta)$ at every trial. $x_b$ changes with $\theta$. |
| Two synthetic states | First declare open or closed route; use same geometry, atom/reference and mechanical conditions for both states | Compare only compatible state potentials **after** minimizing occupancy within each state. A crossing is a model equilibrium candidate, not observed material transition or kinetic accessibility. |

In the closed route, write $z=C_B^{\rm total}/N_{\rm cell}$. Feasible occupancy obeys

$$\max\!\left(0,\frac{zN_{\rm cell}-N_b}{KS}\right)\le\theta\le\min\!\left(1,\frac{zN_{\rm cell}}{KS}\right),\qquad x_b=\frac{zN_{\rm cell}-KS\theta}{N_b}.$$

These bounds come only from $0\le x_b,\theta\le1$ and exact inventories; they do not determine an energy minimum. The [one-state open-reservoir](boundary_one_state_contract.md), [closed-cell](boundary_closed_contract.md) and [two-state](boundary_two_state_contract.md) contracts declare their own boundary free-energy functions, parameter values, analytical limits, comparison checks and numerical tolerances **before** solving. An open chemical-potential result and a closed total-energy result are different ensembles and cannot be compared as bare scalar values.

## Fixed conversion example and failure controls

At $x_b=0.10$ and $\theta=0.25$, bulk has 800 B and 7200 A atoms; both boundaries together have 50 B and 150 A. The cell has 850 B and 7350 A, totaling 8200. A homogeneous 8200-site bulk reference at $x_b=0.10$ has 820 B. The B excess is 30 atoms over $40\ \mathrm{nm}^2$: $0.75\ \mathrm{atoms/nm}^2=7.5\times10^{17}\ \mathrm{atoms/m}^2\approx1.2454\times10^{-6}\ \mathrm{mol/m}^2$. The independent site-density route gives $(100/20)(0.25-0.10)=0.75$ atoms/nm². Using $A$ rather than $2A$ with the **whole-cell** excess doubles the answer incorrectly.

If the open boundary occupancy rises to $0.35$ with bulk fraction fixed, boundary B rises by 20 and A falls by 20; the reservoir must lose 20 B and gain 20 A. If the same 8200-site cell is **closed** with total B fixed at 850, boundary B=70 and bulk B=780, so $x_b=0.0975$; A remains 7350 overall. These inventories are bookkeeping controls, not predictions of occupancy. No value of $\theta$ is energetically selected in this contract.

## Reference and scope notes

[1] T. Frolov and Y. Mishin, “Thermodynamics of coherent interfaces under mechanical stresses. I. Theory,” *Phys. Rev. B* 85, 224106 (2012), [author manuscript](https://arxiv.org/abs/1304.0144), DOI [10.1103/PhysRevB.85.224106](https://doi.org/10.1103/PhysRevB.85.224106). It distinguishes substitutional diffusion potentials and generalized excesses under nonhydrostatic stress; this synthetic model excludes that setting. [Interface-phase theory](https://arxiv.org/abs/1506.08890) likewise motivates keeping a two-state model separate from one-state enrichment.

[2] BIPM, [SI defining constants](https://www.bipm.org/en/measurement-units/si-defining-constants), exact $N_{\rm Av}$ value, checked 29 September 2026. The site/area numbers and excess convention above are original teaching choices, not sourced material measurements.
