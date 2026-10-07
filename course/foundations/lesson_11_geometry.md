# Lesson 11 — count the boundary before assigning it energy

Meetings 26–27. Start from the [boundary geometry contract](synthetic_boundary_contract.md), [Lesson 6 chemical potentials](lesson_06_chemical_potential.md) and [Lesson 10's source audit](lesson_10_source_audit.md). Use the [worksheet](lesson_11_worksheet.md) and [instructor guide](../instructor/lesson_11_guide.md). Everything here is an invented A/B site model. The proposed Ni–Cu case still lacks eligible bulk and boundary inputs.

**Exit goal:** draw the whole system, distinguish a site fraction from an excess per area, convert an atom count through moles and two-interface area, and state which inventories are fixed for open and closed experiments. No boundary energy or equilibrium occupancy is calculated in this lesson.

## 11A — draw one consistent system

Imagine a periodic cell with a bulk region and two **equivalent** planar boundary regions. Each boundary has area $A=20$ nm² and $S=100$ substitutional sites. The bulk region has $N_b=8000$ sites. Every site is filled by exactly one invented A or B atom. Hence the cell has $8000+2(100)=8200$ sites and atoms. No vacancy or extra adsorption plane is counted. $A$ in an area equation means area; A in “A atom” names the first component. Write units to avoid confusing them.

| Quantity | Meaning | Unit in this lesson |
|---|---|---|
| $K=2$ | count of equivalent boundaries | dimensionless |
| $A=20$ | area **per** boundary | nm² or m² |
| $S=100$ | sites **per** boundary | sites |
| $N_b=8000$ | bulk sites | sites |
| $x_b$ | B fraction on bulk sites | dimensionless |
| $\theta$ | B fraction on boundary sites | dimensionless |
| $KS/(KA)=S/A$ | boundary-site density | sites/area of one boundary |

The cancellation in $KS/(KA)=S/A$ is a useful geometry check. Calling $\theta=0.25$ an excess is wrong: a fraction has no area denominator. The area is fixed for this exercise; orientation, plane, atomic state and stress are **not** imported from a real grain boundary.

## 11A worked inventory

Set $x_b=0.10$ and $\theta=0.25$ as **supplied trial occupancies**, not equilibrium results. Bulk B count is $8000(0.10)=800$, so bulk A count is 7200. Two boundaries contain $2(100)(0.25)=50$ B and 150 A. Thus cell B=850 and A=7350. Both component counts sum to 8200; their cell-average B fraction is $850/8200\approx0.10366$, which is distinct from bulk $x_b=0.10$ and boundary $\theta=0.25$.

For the chosen equal-site reference, put the *same* $x_b$ on all 8200 sites: the reference has 820 B. Actual minus reference gives 30 excess B atoms. Divide by **both** boundary areas, $2A=40$ nm², to get $0.75$ atom/nm². The site-density route checks it independently: $S/A=100/20=5$ sites/nm²; $5(0.25-0.10)=0.75$ atom/nm².

To convert to mol/m², $1\ \mathrm{nm}^2=10^{-18}\ \mathrm{m}^2$ and one mole has exactly $N_{\rm Av}=6.02214076\times10^{23}$ specified entities [SI definition](https://www.bipm.org/en/measurement-units/si-defining-constants). Therefore

$$0.75\ \frac{\mathrm{atoms}}{\mathrm{nm}^2}
\times\frac{10^{18}\ \mathrm{nm}^2}{1\ \mathrm{m}^2}
\times\frac{1\ \mathrm{mol}}{6.02214076\times10^{23}\ \mathrm{atoms}}
\approx1.2454\times10^{-6}\ \mathrm{mol/m}^2.$$

The full-count route is $30/N_{\rm Av}$ mol divided by $40\times10^{-18}$ m², the same answer. Dividing the *whole-cell* 30-atom excess by only $A$ gives a false factor of two. Dividing the 50 B atoms by area gives boundary B areal content, **not excess relative to bulk**. The general chosen convention is

$$\Gamma_B=\frac{C_B^{\rm cell}-x_bN_{\rm cell}}{KA N_{\rm Av}}
=\frac{S(\theta-x_b)}{A N_{\rm Av}}.$$

This site-reference excess is zero at $\theta=x_b$. A real interface with different site density or stress needs its own excess definition and mechanical contract. The present formula is a transparent model choice.

## 11B — decide what can cross the system boundary

**Open reservoir:** the boundary cell is in contact with a much larger bulk A/B reservoir represented by fixed $T=1000$ K, $p=100000$ Pa and the [binary-family I1](binary_family_contract.md) stable ALPHA bulk chemical potentials at fixed $x_b$. Its $\mu_B-\mu_A$ drives substitution of B for A at a boundary site. At fixed capacity, replacing 20 A sites by B raises cell B by 20 and lowers cell A by 20. The reservoir loses 20 B and gains 20 A. Combined cell+reservoir inventories balance. One cannot simply add 20 B and leave all A sites occupied.

**Closed sample:** the cell itself has fixed A=7350 and B=850 atoms in the worked starting example. If boundary occupancy rises from 0.25 to 0.35, its B count rises from 50 to 70. Bulk B must fall from 800 to 780, so its new fraction is $780/8000=0.0975$. Bulk A rises from 7200 to 7220 while boundary A falls from 150 to 130. This is an **allowed trial**, not a prediction that the change lowers energy. Holding $x_b=0.10$ as well as B=850 would instead create 20 B atoms.

| Question | Open route | Closed route |
|---|---|---|
| What is fixed? | Reservoir $x_b$ and $\mu_A,\mu_B$; geometry/sites; $T,p$ | Total A/B, geometry/sites; $T,p$ |
| Where does exchanged B come from? | External reservoir, with opposite A transfer | The finite bulk region |
| What changes when $\theta$ changes? | Cell component counts; reservoir has opposite changes | Bulk composition $x_b$ and boundary count; total cell counts stay fixed |
| Which energy will be compared later? | A boundary excess potential at fixed reservoir variables | A constrained **total** energy at fixed inventories |

The later energy model must use one ensemble at a time and the same area, site count, atom reference and mechanical conditions when comparing structural states. [Lesson 12](lesson_12_reservoir.md) defines a one-state boundary free energy and checks; [Lesson 13](lesson_13_finite_reservoir.md) closes the inventory; [Lesson 14](lesson_14_competing_states.md) adds a second synthetic state. A crossing of two model branches would require compatible potentials and independent scientific evidence before any real interface-phase claim.

## Quick self-check

At $\theta=x_b$, which quantity is zero: boundary B count or chosen excess? If there is only one boundary or two inequivalent boundaries, can the worked $2A$ and one $\theta$ be reused? If a value is in J/mol, which conversion is needed before multiplying by 20 atoms? Use the [worksheet](lesson_11_worksheet.md) for a fresh geometry and an unsupported-claim challenge.
