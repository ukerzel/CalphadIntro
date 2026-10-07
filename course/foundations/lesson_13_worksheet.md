# Lesson 13 worksheet — conserve a finite cell

Use the [reading](lesson_13_finite_reservoir.md) and [closed-cell contract](boundary_closed_contract.md). Keep the [answers](../instructor/lesson_13_guide.md) closed for the independent tasks. Show which site count and energy basis each number uses. A calculator and paper suffice; code is optional.

## Meeting 30 — total energy with fixed A/B

**A1 — guided inventory.** Draw the $N_b=8000$, two-boundary cell with 100 sites and 20 nm² per boundary. At initial $x_0=0.10,\theta_0=0.25$, find total A and B. Write $x_b(\theta)$ when total B is fixed. At $\theta=0.35$, find bulk and boundary A/B counts and show both total balances.

**A2 — feasibility and basis.** Write the feasible $\theta$ interval for a general total B with $N_b$ bulk and $M=200$ boundary sites. For this same geometry with only 30 B atoms total, test $\theta=0.15$ and $0.625$. Explain why $N_b g_b+Mg_s$ has to be divided by $N_{\rm Av}$ to give joules, and why dividing by $N_b+M$ instead gives J/mol of all sites.

**A3 — supplied closed trials.** With B=850 and $\delta=-5000$ J/mol boundary sites, fill a table for $\theta=0.10,0.15,0.20,0.25$: final $x_b$, $\bar g$ in J/mol all sites, and total B check. Select the lowest supplied trial and state why it is not yet the continuous minimum. Compare the *kind* of energy used here with Lesson 12's open potential.

**A4 — independent fresh trial.** Start with $x_0=0.50,\theta_0=0.25$ and the same 8000+200 sites, but $\delta=+5000$ J/mol. Find fixed B total. Evaluate $x_b$ and $\bar g$ for trial $\theta=0.25,0.35,0.50$. Which trial is best? Predict whether the equilibrium boundary fraction is above or below the **final bulk** fraction. Can its value nonetheless be above the *starting* 0.25?

## Meeting 31 — root, excess and reservoir limit

**B1 — derive the exchange root.** Differentiate $x_b(\theta)$ and the total molar energy. Show why the binary-family $\Delta$ tilt cancels and why the residual is strictly increasing. For A3, bracket the root between 0.15 and 0.20 and compare with the continuous result near 0.17160752. State why a direct bounded minimum and the exchange root are separate checks.

**B2 — final inventory and excess.** Using $\theta_*=0.17160752$ for A3, find final $x_b$, boundary and bulk B counts, and total A/B. Compute $\Gamma_B$ by the site-density route and by whole-cell excess over 40 nm². What happens if someone divides the whole-cell excess by only 20 nm² or uses initial $x_0$ as the final bulk reference?

**B3 — zero preference and limit.** At $\delta=0$, determine the closed equilibrium fraction for B=850 and compare it with initial $x_0=0.10$ and Lesson 12's open zero-preference result. For $N_b=8000,80000,800000$ with the same $x_0,\theta_0,\delta=-5000$, explain which total B is fixed in each cell. Compare the three closed occupancies with the open occupancy 0.16856026; do the errors decrease?

**B4 — independent exit and failed claims.** For A4's 4050-B cell, find the continuous $\theta_*$, final $x_b$, $\bar g$, and $\Gamma_B$ in atom/nm² and mol/m². Check both component totals. Assess three statements: “positive preference means occupancy must decrease from its starting trial,” “one can keep $x_b=0.50$ while changing $\theta$ in a closed cell,” and “a converged energy minimizer proves a boundary phase transition.” Give a detecting check or missing scientific requirement for each.
