# Task 04 — answers and observed calculation

1. Positive $\delta$ penalizes Ni on boundary sites relative to Cu. With the
   increasing exchange derivative on this example's branch, the stationary
   $y$ lies below bulk $x$. Cu occupancy $1-y$ rises. Each added Ni replaces
   Cu at a filled site, so the driving potential is $\mu_{Ni}-\mu_{Cu}$.
   Omitting the Cu reservoir is not that occupied-site exchange.
2. At overall/open-reservoir Ni fraction 0.5, the [actual run](segregation_results.json)
   gives open $y=0.1775730682$, closed bulk $x=0.5065438265$ and closed
   $y=0.1793525022$. On the closed one-mole basis,

   $$n_{Ni}=0.98x+0.02y=0.5000000000\ \mathrm{mol},$$
   $$n_{Cu}=0.98(1-x)+0.02(1-y)=0.5000000000\ \mathrm{mol}.$$

   Relative to initially uniform $x=y=z$, Cu moves from bulk into the
   boundary and Ni returns to the bulk. Boundary Cu is 0.8206474978 in the
   closed cell, versus 0.8224269318 for the open reservoir. Finite Cu supply
   reduces the boundary Cu occupancy; the final bulk Ni fraction rises.
3. Closed Cu excess is $10(0.5065438265-0.1793525022)$, or
   **3.271913243 atoms/nm²**, **$5.433139764\times10^{-6}$ mol/m²**.
   Open excess is **3.224269318 atoms/nm²**. The closed bulk reference has
   itself become Cu-depleted, so a smaller boundary Cu occupancy can still
   have a greater excess relative to that changed reference. Excess is not
   simply the boundary occupancy, nor does its direction of change have a
   universal relation to the open/closed occupancy change.
4. Trial excess is $10(0.5-0.3)=2$ atoms/nm², or
   $2\times10^{18}/N_A=3.321078134\times10^{-6}$ mol/m². For zero preference
   the identical bulk/site functions give $y=x$ in the open case and
   $x=y=z$ in the closed cell; both excesses vanish.
   A physical calibration needs a stated boundary character, compatible
   observed composition/excess and site/area convention, conditions and an
   evidenced boundary model. None is supplied by choosing the invented
   preference or copying bulk magnetic terms. That further work is not assigned.

The run takes about **1.49 s internally**, excluding imports. Maximum exchange
residual is $2.17\times10^{-9}$ J/mol sites and maximum zero-preference fraction
error $4.44\times10^{-16}$; both are within the stated tolerances. Minimum
**sampled** bulk curvature is about 10024 J/mol, a screen rather than a global
proof. If you write your own version, check the sign of the preference, the
ideal odds relation, both finite-cell balances, the closed-energy derivative,
the zero-preference case and the excess unit conversion, and check that a
very dilute inventory still gives a feasible bulk/boundary split.

These occupancies come
from the stated illustrative boundary function, not measured Cu–Ni segregation
or a validated physical boundary state.
