# Task 03 — answers and observed results

1. Use the blue band labelled Σ3 Ni, in the lower part of Figure 3. It is
   formation energy from Gibbs–Helmholtz integration with a shared 500 K
   reference. Sampling the same curve does not create independent observations.
   The green dashed curve is internal excess energy per area; brown values
   come from switching-Hamiltonian calculations. Neither is the selected input.
   The readings were taken for this course from the published Figure 3.
2. The [actual fit](ni_twin_results.json) gives

   $$A=0.067525\ \mathrm{J/m^2},\qquad
   B=-2.025\times10^{-5}\ \mathrm{J/(m^2\,K)}.$$

   Largest absolute residual is **0.000175 J/m²**, at 600 and 800 K, and
   the residual sum of squares is **$1.025\times10^{-7}$ J²/m⁴**. These are
   residuals of approximate curve readings; their size below the stated
   ±0.001 J/m² graphical allowance is not a statistical test of the fit.
   The teaching coefficient −B is **0.02025 mJ/(m² K)**. Interpreting it as
   the source's exact physical excess entropy would omit the source's
   internal-energy/mechanical treatment and the limitations of graphical data.
3. On the one-mole Ni basis,

   | Quantity | Value |
   |---|---:|
   | $V_m$ | $6.566272493\times10^{-6}$ m³/mol |
   | $A_{GB}$ | 196.9881748 m² |
   | Two-plane $\rho$ | $6.190035366\times10^{-5}$ mol sites/m² |
   | Boundary Ni $n_s$ | 0.01219363769 mol |
   | Bulk Ni $n_b$ | 0.98780636231 mol |

   Counting six unshared faces doubles the boundary area. Adding $n_s$ to
   one mole of bulk Ni creates atoms: the boundary allocation already belongs
   to the total one mole. The chosen two-plane count is a site convention,
   not a measured boundary thickness.
4. At 500 K, fitted γ is **0.0574 J/m²**, ε is **927.2968022 J/mol sites**,
   and $A_{GB}\gamma$ is **11.30712123 J**. The saved total-cell calculation
   reproduces that excess. At 300 and 800 K it likewise gives about
   **12.10492334** and **10.11041807 J**. With zero offset, reallocating Ni
   between identical bulk/site functions leaves the one-mole energy unchanged.
   Recovery is accounting of the inserted offset, not independent validation
   of the source potential, magnetic copying or a physical boundary phase.

The run took about **0.77 s internally**, excluding imports. If you write
your own version, check that it recovers a known straight line exactly,
accounts residuals correctly when readings deviate from the line, reproduces
the shared-face geometry and two-plane site amounts above, keeps the one-mole
Ni balance with a total excess of $A_{GB}\gamma$, and rejects invalid inputs
such as repeated temperatures or a zero lattice parameter. No physical
boundary assessment is made.
