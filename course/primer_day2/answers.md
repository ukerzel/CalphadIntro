# Day 2 staged hints and answers — facilitator copy

Offer a first hint, then a second hint before showing the worked answer.
Equivalent reasoning with correct conditions, units and amount basis is fine.
The numbers are invented model outputs, not learner measurements or real
Ni–Cu values. Keep this sheet separate from independent attempts.

## D0 · Bridge

**Hint 1:** Day 1 had only A and two bulk phases. Name the new composition
variable before naming an interface.

**Hint 2:** Ask what must be known at a boundary besides the surrounding bulk.

**Answer:** the new links need a binary bulk composition/model, then boundary
site geometry, exchange or inventory rule, and candidate state energies.
Only (a), the invented unary line crossing, was supported by Day 1. It
neither supplies Ni–Cu parameters nor a boundary model.

## D1 · Composition and balance

**Hint 1:** $n_B=z(n_A+n_B)$; the remaining amount is A.

**Hint 2:** Put $f_1=1-f_2$ into $z=f_1x_1+f_2x_2$.

**Answer:** (1) $n_B=0.40$ mol and $n_A=1.60$ mol.
(2) $0.20=(1-f_2)0.10+f_2(0.50)$ gives $f_2=0.25$ and $f_1=0.75$.
B balance is $0.75(0.10)+0.25(0.50)=0.20$; A balance is
$0.75(0.90)+0.25(0.50)=0.80$. These fractions sum to one.
(3) $x=0.20$ is B atom fraction **within ALPHA**. Area occupied by a phase
requires geometry or an area measurement, and the phase amount fraction
requires a phase-equilibrium/amount calculation. Neither is $x$.

## D2 · Ideal bulk

**Hint 1:** Evaluate the reference as $-9000+12000x$ first.

**Hint 2:** The supplied $q(0.20)$ is dimensionless; multiply by $RT$ with
units J/mol.

**Answer:** (1) at $x=0.20$, reference $=-6600$ J/mol atoms; the ideal
mixing term is $8314.5q\approx-4160.596$ J/mol atoms, so
$g_b\approx-10760.596$ J/mol atoms. The endmember weighted value omits the
mixing contribution. (2) $-10.50$ kJ/mol is $-10500$ J/mol; it differs
from $-10502.902$ J/mol by about 2.902 J/mol, consistent with rounding
to $0.01$ kJ/mol. The printed values do not show a distinct model.

## D3 · Exchange

**Hint 1:** A fixed occupied site trades one A away for one B in.

**Hint 2:** Use $\ln(0.1/0.9)=-2.19722458$ and
$\ln(0.2/0.8)=-1.38629436$.

**Answer:** (1) $-16144.844-(-9876.020)=-6268.824$ J/mol atoms;
$12000+8314.5(-2.19722458)\approx-6268.824$. Subtracting only
$\mu_B$ would fail to account for the A atom replaced at a filled site.
(2) at 0.20, $\mu_B-\mu_A\approx+473.656$ J/mol atoms. A sign of an
exchange slope is not an equality of two phase Gibbs energies or a
two-phase global minimum. We allowed only ALPHA here.

## D4 · Geometry and excess

**Hint 1:** Compute A separately in 8000 bulk and 200 boundary sites.

**Hint 2:** For atom/nm², use excess B count divided by **40** nm².

**Answer:** (1) bulk A $=8000(0.90)=7200$; boundary A
$=200(0.85)=170$. With 800+30=830 B, A is 7370 and the total is 8200.
(2) at $\theta=x_b$, reference and cell B counts agree and excess is
zero. At $\theta=0.08$, the boundary has 16 B, the bulk 800 B and the
reference 820 B: excess $=-4$ B over 40 nm², or $-0.10$ atom/nm².
There are still 816 B atoms in the cell; a negative **excess** means
depletion relative to the chosen equal-site bulk reference.

Optional conversion: the worked $0.25$ atom/nm² equals
$0.25\times10^{18}/N_{\rm Av}\approx4.15135\times10^{-7}$ mol/m².
The count/area route and $5(0.15-0.10)$ route agree. Using one boundary's
area with both boundaries' count would double the reported value.

## D5 · Open one-state selection

**Hint 1:** Multiply bulk odds $0.1/0.9$ by 1.82459687.

**Hint 2:** If the resulting odds are $r$, solve $\theta=r/(1+r)$.

**Answer:** (1) selected odds $\approx0.20273299$, so
$\theta_*\approx0.16856026$. Since $\delta<0$, B lowers boundary-site
energy; the selected occupancy exceeds 0.10. At $\delta=0$ the factor is
one, $\theta_*=x_b=0.10$, and this convention's excess vanishes.
(2) $\theta$ is a **fraction of 200 sites**; expected boundary B count is
about 33.7121 atoms, or $33.7121/N_{\rm Av}$ mol, not 0.16856 mol.
$\phi$ is a reservoir-subtracted excess grand potential per mole of
boundary sites under a chosen reference, not absolute boundary free energy.

The excess is $5(0.16856026-0.10)=0.3428013$ atom/nm². Converting with
$10^{18}/N_{\rm Av}$ gives $5.69235\times10^{-7}$ mol/m². For both
boundaries, excess B count $\approx13.7121$ over 40 nm².

## D6 · Closed inventory

**Hint 1:** Total B stays 850. Boundary B is $200\theta$.

**Hint 2:** Divide the remaining B count by 8000 to obtain bulk $x_b$.

**Answer:** (1) at $\theta=0.35$, boundary B=70, bulk B=780 and
$x_b=780/8000=0.0975$. Keeping 0.10 in bulk would give 800+70=870 B,
contradicting the fixed 850. A remains 7350 because every B movement
replaces an A movement in the opposite direction.
(2) at the supplied minimum, boundary B $\approx34.3215$ and bulk B
$\approx815.6785$; their sum is 850 within display rounding. State
comparisons at different total B compare different systems, so an energy
ordering for one closed inventory cannot be inferred from another.
The closed $\theta_*$ need not equal the open $0.16856026$ because the
finite bulk fraction adjusts.

## D7 · Candidate boundary states

**Hint 1:** Calculate $D=$ II minus I **within each table row**.

**Hint 2:** In row one, State II boundary B count is
$200(0.2689826)$; subtract it from the shared 850.

**Answer:** (1) at $x_0=0.10$, $D=+22.21984$ J/mol all cell sites and I
is lower. At $x_0=0.25$, $D=-5.47887$ J/mol all sites and II is lower.
Different rows have different B totals (850 versus 2050) and are not a
same-inventory comparison. The sign change brackets a crossing for the
declared continuous uniform-state model; it does not by itself establish
coexisting real boundary phases.
(2) State II has boundary B $\approx53.796516$, bulk B
$\approx796.203484$, and $x_{b,II}\approx0.0995254$. State I has
boundary B $\approx34.3215$, bulk B $\approx815.6785$, and
$x_{b,I}\approx0.10195981$. Each sums to 850. Since the two selected
occupancies differ, forcing a shared final $x_b$ would change at least one
state's total B.
(3) omitting $\eta_{II}$ defines a different model, so the printed
energy would no longer follow from the stated function. The missing term
is $200(2000)/8200=48.78049$ J/mol **all cell sites** at either row;
the baseline is not 2000 J/mol all sites. It shifts State II's energy
without changing its selected occupancy at fixed inventory.

## D8 · What would make this a material case?

**Hint 1:** Ask whether a sentence describes invented arithmetic, a needed
input, or an asserted observation/prediction about Ni–Cu.

**Hint 2:** Separate one-state segregation from a two-state transition.

**Answer:** (a) toy-model result; (b) missing evidence, bulk model;
(c) unsupported real claim; (d) missing evidence, boundary model,
including compatible states under one reference. If a real single state were validated along
with the exact case and bulk, a **conditional segregation** question could
then be calculated, with its own checks. A structural
transition additionally needs at least two matched real state functions,
physical interface coexistence conditions and independent evidence. A toy
energy crossing or solver return is not such evidence. A crossing compares
only *uniform* states: at fixed inventory, a boundary partly in I and partly
in II can have lower total energy than either uniform state near the
crossing, so the change may happen over a range of compositions rather than
as a sharp switch. Only a coexistence analysis decides this.

## D9 · Fresh integrated card

**Hint 1:** Open odds start at $0.20/0.80=0.25$; closed B starts from
$8000x_0+200\theta_0$.

**Hint 2:** For excess use $5(\theta_*-x_b)$ atom/nm². For the closed
trial, subtract boundary B from fixed total B.

**Answer:** (1) open odds $=0.25(1.82459687)=0.45614922$ and
$\theta_*\approx0.31325719$. Excess $=5(0.31325719-0.20)
\approx0.566286$ atom/nm². Across 40 nm², excess B count is
$0.566286(40)\approx22.6514$ atoms, also
$200(0.31325719-0.20)\approx22.6514$.
(2) closed total B $=8000(0.20)+200(0.20)=1640$.
At $\theta=0.40$, boundary B=80, bulk B=1560 and $x_b=0.195$.
Keeping 0.20 would give 1680 B, violating the 1640-B inventory.
(3) Example: “The invented uniform-state model orders I below II at
850 B and II below I at 2050 B.” “It supplies no validated Ni–Cu bulk
and matched boundary-state energies or physical interface coexistence
analysis, so neither a measured transition nor a strengthening effect
follows.” Other precise supported/gap pairs are acceptable.

## D10 · Supported exit

**Hint 1:** Day 1 gives the potential choice; D5 and D6 give different
matter-exchange boundaries.

**Hint 2:** Reuse D5's zero-preference limit and D7's first row.

**Answer:** (1) minimize total $G$ for the closed cell at fixed $T,p$ and
fixed A/B counts. In the open boundary experiment the combined
cell+reservoir conserves atoms while the cell exchanges B for A at fixed
occupied boundary sites and fixed reservoir $\mu_A,\mu_B$. In the finite
closed cell, both cell A and B totals are fixed and bulk $x_b$ changes.
(2) $\theta_*=0.10$ and $\Gamma_B=0$ by the chosen equal-site convention.
The zero follows from an invented zero-preference model, not observed
segregation data. (3) $D=+22.21984$ J/mol all sites; I is lower among
the two uniform candidates. Examples of missing conditions: compatible
real state free energies and geometry, physical interface coexistence,
uncertainty/held-out evidence, or demonstrated stability against other
candidates. (4) The named next task or lesson should match the learner's
question (for example D1–D3 → Task 01, D4–D6 → Task 04, D7 → Task 03 or
04); neither primer validates a Ni–Cu prediction.

## Facilitator interpretation

Do not turn this answer sheet into a pass/fail threshold. Record whether
the learner needed the printed factor, partner help or supplied state
energies, and which *concept* needs more practice: binary balance, energy
basis, exchange, area/excess, ensemble or real-claim evidence. Point that need
to the matching worked example (Tasks 00–05) or optional detailed lesson,
not automatically to the entire lesson library.
