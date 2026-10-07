# Instructor guide — one-state open boundary

[Reading](../foundations/lesson_12_reservoir.md), [worksheet](../foundations/lesson_12_worksheet.md), [one-state open-reservoir contract](../foundations/boundary_one_state_contract.md), meetings 28–29. Show the physical system and reference before showing an optimizer. Timings are planned; they have not been observed with learners.

| Minutes | Meeting 28 | Meeting 29 |
|---|---|---|
| 00–10 | Retrieve site and area basis from Lesson 11 | Retrieve A-for-B exchange and trial minimum |
| 10–25 | Define open reservoir and $g_{\rm site}$ | Derive $\phi'$ and strict convexity |
| 25–40 | Work A1, begin A2 | Work B1, compare analytical/direct routes |
| 40–45 | Break | Break |
| 45–70 | Finish A2; diagnose A3 | B2 amount/area routes; B3 limits |
| 70–85 | A4 independent, feedback | B4 independent, failure analysis |
| 85–90 | Exit: what chemical-potential difference acts? | Exit: what is and is not established? |

Each meeting allocates 85 contact/practice minutes plus a five-minute break. Give the exact constants and logarithmic formula when arithmetic is the obstacle; retain the independent preference/sign and excess checks. Record support and time from the attempts.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1 | At $\theta=x_b$, both logarithmic ratios equal one. | The remaining term is $\delta x_b$; the zero is equal-site bulk only when $\delta=0$. |
| A2 | Compare all three values in the **same** J/mol-site basis. | A smaller untested $\theta$ interval may contain the continuous minimum. |
| A3 | There are 200 boundary sites in the cell. | A $+20$ B replacement requires $-20$ A in the cell and the opposite reservoir transfers. |
| A4 | Positive $\delta$ penalizes boundary B. | At $\theta=x_b$, $\phi=\delta x_b=1000$ J/mol sites. |
| B1 | Set $\delta+RT[\ln\frac{\theta}{1-\theta}-\ln\frac{x_b}{1-x_b}]=0$. | Exponentiate the odds, then solve for $\theta$. |
| B2 | First find $\theta_*-x_b$ and multiply by $S/A=5$ sites/nm². | For whole-cell counts use $2S$ and divide by $2A=40$ nm². |
| B3 | Set the odds multiplier to one. | Divide the odds equation by $x_b$ near zero and by $1-x_b$ near one. |
| B4 | Compute $\exp[-4000/(8314.5)]$ first. | Compare count and site-density excess, then test sign and potential consistency. |

## Answers and detecting failures

**A1.** $RT=8314.5$ J/mol. The two displayed formulas in the reading are equal because the ideal ALPHA (model I1) pure endmember terms cancel against $(1-\theta)\mu_A+\theta\mu_B$. At $\theta=x_b=0.1$ the logarithmic term is zero, so $\phi=-500$ J/mol sites. The reference is the same number of bulk-like occupied sites at the reservoir composition, with no structural boundary baseline. A negative excess does not mean an absolute interface energy is negative.

**A2.** $\phi(0.10)=-500.0000$, $\phi(0.15)\approx-648.2711$, $\phi(0.25)\approx-482.3096$ J/mol sites. The lowest supplied trial is 0.15. The function is continuous, and 0.15 was only one of three sampled values; the actual minimum is near 0.16856. The full potential subtracts both $\mu_A$ and $\mu_B$ weighted by their site fractions.

**A3.** Cell boundary changes are $\Delta B=+20$, $\Delta A=-20$ expected atoms; reservoir changes are $\Delta B=-20$, $\Delta A=+20$. The fixed-site differential reservoir term is $-(\mu_B-\mu_A)d\theta$, not $-\mu_Bd\theta$. An optimizer can converge exactly for a wrongly specified objective; analytical exchange and zero-preference controls detect the reference error.

**A4.** $\phi(0.15)\approx847.4797$, $\phi(0.20)\approx858.2190$, $\phi(0.25)=1000.0000$ J/mol sites, so 0.15 is the best supplied trial. Positive preference gives $\theta_*<0.25$. The reference-dependent potential is zero for equal-site bulk at $\delta=0$; at $\delta=+4000$, even its minimum is positive relative to that chosen reference. This is not an absolute grain-boundary energy.

**B1.** $\phi'=\delta+RT\ln\frac{\theta}{1-\theta}-RT\ln\frac{x_b}{1-x_b}$ and $\phi''=RT/[\theta(1-\theta)]>0$. The endpoint derivative limits are $-\infty$ and $+\infty$, so the interior root is the unique global minimum. For $x_b=0.10,\delta=-5000$, the odds multiplier is $e^{5000/8314.5}\approx1.8246$, giving $\theta_*\approx0.16856026$. With $Z=1-x_b+x_be^{-\delta/(RT)}$, substitute $\theta_*=x_be^{-\delta/(RT)}/Z$ and $1-\theta_*=(1-x_b)/Z$ into $\phi$: $\phi_*=RT[-(1-\theta_*)\ln Z+\theta_*(-\delta/(RT)-\ln Z)]+\delta\theta_*=-RT\ln Z$. Here $Z\approx1.082460$ and $\phi_*\approx-658.80722$ J/mol sites. It is lower than the best supplied trial. A bounded minimizer checks the original $g-\mu$ objective while the ratio and $\phi_*$ expression come from separate algebra; agreement tests the implementation, within the stated domain and tolerance.

**B2.** $\theta_*-x_b\approx0.06856026$. Since $S/A=5$ sites/nm², $\Gamma_B\approx0.3428013$ atom/nm² $\approx5.69235\times10^{-7}$ mol/m². The two boundaries carry $200(0.06856026)\approx13.71205$ excess B atoms; divide by 40 nm² for the same density. Dividing that whole-cell count by only 20 nm² gives about $0.6856026$ atom/nm², twice the correct value. A-for-B replacement removes the same expected A count from the cell and sends it to the reservoir.

**B3.** If $\delta=0$, the odds ratio is one, so $\theta_*=x_b$, $\phi_*=0$ and this chosen $\Gamma_B=0$. As $x_b\to0^+$, $\theta_*/x_b\to e^{-\delta/(RT)}$; as $x_b\to1^-$, $(1-\theta_*)/(1-x_b)\to e^{\delta/(RT)}$. The numerically checked domain is only $x_b\in[0.01,0.99]$. Zero excess is a reference condition, not evidence for a real structural state or transition.

**B4.** For $x_b=0.25,\delta=+4000$, $\theta_*\approx0.17083804$, $\phi_*\approx834.29605$ J/mol sites and $\theta_*-x_b\approx-0.07916196$. Thus $\Gamma_B\approx-0.3958098$ atom/nm² $\approx-6.57258\times10^{-7}$ mol/m². Whole-cell excess is $200(-0.07916196)\approx-15.83239$ B atoms over 40 nm². (i) Nonzero preference requires changed odds; 0.25 fails the analytic occupancy. (ii) Positive preference must deplete B, so enrichment fails the sign check. (iii) Compare the solver's returned objective with a fresh full-objective evaluation and the independent $\phi_*$ formula; success alone is insufficient. No real Ni–Cu segregation, competing structural state or phase transition can be inferred.

## Readiness record

Keep A4/B4 independent reasoning and note supported versus independent completion. The code checks cover this synthetic contract only. The finite-inventory and two-state comparisons have their own contracts (Lessons 13–14).
