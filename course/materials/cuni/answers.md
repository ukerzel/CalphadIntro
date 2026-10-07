# Task 01 — answers and observed results

Independent arithmetic of the fetched pure liquid Cu branch at **1500 K** gives
**−83457.60262034053 J/mol atoms**, equal to the saved evaluator result at printed
precision. FCC's fixed VA site adds no real atoms: its `Model.G`/`GM` ratio is
one, not two. Magnetic-on minus magnetic-off agrees with the separately assembled
magnetic contribution within $8.85\times10^{-12}$ J/mol at the checked states.

At **600 K**, bulk **x(Ni)=0.5**, the magnetic-on state has two FCC compositions:
approximately **0.398259** and **0.796767**, with atom-mole fractions **0.744695**
and **0.255305**. Their amount-weighted Ni fraction is 0.5. These are two
compositions of the same phase model, rather than two distinct crystal structures.
Magnetic-off still has two FCC compositions, approximately **0.406223** and
**0.764343**, with fractions **0.738142** and **0.261858**. Thus the chemical
model already demixes; magnetism changes the result rather than causing the gap.
Use the saved JSON's unrounded numbers for exact balance reconstruction.

The saved `FCC_liquid_example` is the first sampled temperature at x(Ni)=0.5
with both phases present: **1540 K** in each mode. With magnetism on, it is
approximately **0.0978183 liquid** at x(Ni)=**0.368010** and **0.902182 FCC**
at x(Ni)=**0.514311**. Those atom-mole fractions reconstruct x(Ni)=0.5.
Use the JSON's unrounded values for the balance calculation. At **1500 K**,
the x(Ni)=0.5 state is all FCC. At **1600 K, x(Ni)=0.5**, the saved
state is all liquid in both modes. At a fixed alloy composition, equilibrium
minimizes total energy subject to component conservation. It cannot simply choose
the lowest point anywhere along a Gibbs curve and change the alloy composition.

Maximum saved whole-grid component error is below $4.25\times10^{-9}$,
and amount error below $7.85\times10^{-10}$, within the declared $10^{-6}$.
The JSON includes all selected samples from the same unchanged grid.
Tiny last-digit numerical variation
does not change the declared tolerances or teach a physical uncertainty.

## Actual visual comparison

The magnetic-on [sampled diagram](phase_diagram.png) shows the upward-sloping
liquid/FCC coexistence lens seen in Mey Fig. 1, printed p.256. Endpoints near the
Cu and Ni melting regions and the broader central coexistence range have similar
visual shape. The 20 K grid and absent exact pure endpoints do not establish
numerical agreement with every measured marker or boundary temperature.

At low temperature, two FCC branches enclose a miscibility gap, broadly matching
Fig. 7, printed p.259. The plotted gap reaches the vicinity of 640 K on the
magnetic-on grid. The paper also draws a Curie-temperature line; our phase plot
does not reproduce that composition-dependent line. The separate pure-Ni energy
panel marks its source transition temperature and illustrates an extra magnetic
energy contribution, without assigning it a separate structural phase field.

The highest sampled two-FCC temperatures are **640 K on** and **620 K off**.
These are grid observations, **not an exact critical-temperature shift of 20 K**.
The temperature steps are 20 K, compositions are sampled and narrow fields may
be missed. Both modes retain a gap at 600 K, which is enough for the introductory
question. Refining the critical temperature further (for example by bisection) is not needed here.
BCC_A2 and HCP_A3 remain enabled but have no visible positive amounts on this
grid; absence here does not certify physical metastability everywhere.

The [four-row CSV](mey1992_binary_parameters.csv) contains the printed paper's
fitted chemical coefficients. These are calibration/model inputs, not held-out
experimental observations. Liquid $b_0$ differs from the adapted TDB, and the
binary magnetic-moment coefficients also differ. Source-header dates and unary
adaptations further prevent an identity claim. Neither dataset is altered to
force agreement; no new physical assessment is inferred from this visual check.
