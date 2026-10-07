# Lesson 14 worksheet — compare compatible branches

Use the [reading](lesson_14_competing_states.md) and [two-state contract](boundary_two_state_contract.md). Keep the [instructor answers](../instructor/lesson_14_guide.md) closed during independent tasks. The two states are invented uniform alternatives. Paper calculations use supplied minimized values; code is optional.

## Meeting 32 — two states, one closed inventory

**A1 — reference card, guided.** Record $T,p,N_b,K,S,A$, total sites and the initial $\theta_0$. At $x_0=0.10$, find fixed total A/B for each state. Write both boundary-site functions, state preferences and baselines. Which facts must match before their energies can be compared?

**A2 — worked low-B comparison.** Use the reading's minimized $\theta$, final $x_b$ and total molar energies at $x_0=0.10$. Check B balance separately for each state, find $D=\bar g_{II}^*-\bar g_I^*$, and choose the lower branch. Convert State II's +2000 J/mol-boundary-site baseline to J/mol **all** sites. If it is omitted, what sign would $D$ have?

**A3 — guided high-B comparison.** At $x_0=0.25$, confirm total B=2050 and subtract the supplied minimized energies. A colleague evaluates both states at the starting $\theta=0.25$ instead. The baseline/preference difference at that *unminimized* occupancy is $200[2000-5000(0.25)]/8200$ J/mol all sites; calculate its sign and explain why it does not select the stable candidate after within-state relaxation.

**A4 — independent fresh inventory.** At $x_0=0.50$, both alternatives have total B=4050. Supplied minimized values are: State I $\theta_I=0.63706496$, $x_{b,I}=0.49032338$, $\bar g_I^*=-8904.79653$ J/mol all sites; State II $\theta_{II}=0.75982577$, $x_{b,II}=0.48725436$, $\bar g_{II}^*=-8941.48054$ J/mol all sites. Check each B balance to rounding, calculate $D$, identify the lower branch and explain why the final bulk fractions differ.

## Meeting 33 — crossing and sensitivity

**B1 — bracket and uniqueness.** Use $D(0.10)$ and $D(0.25)$ from A2/A3 to bracket a crossing. At the reported $x_0\approx0.21618678$, use $\theta_I\approx0.332074$ and $\theta_{II}\approx0.470497$: must the occupancies become equal? Prove the direction of $D'(x_0)$ from the preference ordering, fixed B balance and increasing ideal bulk exchange slope. What does a 17-point scan contribute, and what can it not prove alone?

**B2 — baseline sensitivity, guided.** At fixed $x_0$, changing only $\eta_{II}$ by $+100$ J/mol boundary sites shifts $D$ by what amount in J/mol all sites? Does either state optimum occupancy change? Predict the crossing direction. Repeat for $-100$. Compare with the reported roots 0.20187111, 0.21618678 and 0.23094775.

**B3 — failed comparison cards.** Assess each claim: (i) “State II always wins because its B preference is more negative”; (ii) “We can subtract State I's closed total $G$ from State II's open grand potential”; (iii) “At the crossing the two final bulk fractions and boundary occupancies must match”; (iv) “The crossing proves a Ni–Cu grain-boundary phase transition.” Name the missing term, incompatible basis or missing evidence.

**B4 — independent exit.** At a fresh $x_0=0.20$, supplied separately minimized values are State I $\theta_I=0.31119788$, $x_{b,I}=0.19847005$, $\bar g_I^*=-10790.91356$ J/mol all sites; State II $\theta_{II}=0.44656066$, $x_{b,II}=0.19508598$, $\bar g_{II}^*=-10788.15021$ J/mol all sites. Calculate total B, check both balances, find $D$ and the lower branch. Would increasing $\eta_{II}$ by 100 change the state chosen at this *same* $x_0$? What would be required before calling any corresponding real-interface feature a phase transition?
