# Instructor guide — finite inventory and total energy

[Reading](../foundations/lesson_13_finite_reservoir.md), [worksheet](../foundations/lesson_13_worksheet.md), [closed-cell contract](../foundations/boundary_closed_contract.md), meetings 30–31. Timings are planned; they have not been observed with learners.

| Minutes | Meeting 30 | Meeting 31 |
|---|---|---|
| 00–10 | Retrieve Lesson 11 closed inventory | Retrieve total-energy basis and best trial |
| 10–25 | Draw system, fix A/B, derive $x_b(\theta)$ | Derive exchange residual and convexity |
| 25–40 | Work A1, begin A2 | Work B1, then B2 counts and excess |
| 40–45 | Break | Break |
| 45–70 | Finish A2, A3 trial energy | Finish B2, B3 large-reservoir comparison |
| 70–85 | A4 independent, feedback | B4 independent, failed-claim diagnosis |
| 85–90 | Exit: what changes in the finite bulk? | Exit: what does one-state convergence prove? |

Each meeting has 85 contact/practice minutes and a five-minute break. If energy arithmetic absorbs time, provide $q(y)$ and a calculator, then preserve the independent balance, sign and ensemble checks. Record supported versus independent work from the attempts.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1 | Initial B is bulk B plus B in both boundaries. | New bulk B is $850-200\theta$; A is capacity minus B. |
| A2 | Require both $0\le\theta\le1$ and $0\le B_{\rm tot}-200\theta\le N_b$. | For 30 B, 200$\theta\le30$. Counts divided by $N_{\rm Av}$ are mol. |
| A3 | Recompute $x_b$ at every trial before evaluating $g_b$. | Compare one fixed-cell $\bar g$ basis, not four fixed-$x_b$ grand potentials. |
| A4 | Total B is $8000(0.50)+200(0.25)$. | Positive preference means $\theta_*<x_b(\theta_*)$, not necessarily $\theta_*<0.25$. |
| B1 | $dx_b/d\theta=-200/N_b$. | Set $\delta+RT[\ln\frac{\theta}{1-\theta}-\ln\frac{x_b(\theta)}{1-x_b(\theta)}]=0$. |
| B2 | Keep total B=850 while using the new $x_b$. | Whole excess $=200(\theta-x_b)$ over $2A=40$ nm². |
| B3 | At zero preference all sites have the same B fraction. | Each size has $B_{\rm tot}=N_b(0.10)+50$; compare occupancy errors. |
| B4 | Root and direct minimization agree near 0.35171022. | Check final region fractions, not direction from an arbitrary initial state. |

## Answers and detecting failures

**A1.** Initial bulk B=800, boundary B=50, total B=850; total A=7350. $x_b=(850-200\theta)/8000$. At $\theta=0.35$, boundaries (A,B)=(130,70), bulk (A,B)=(7220,780), so the cell remains (A,B)=(7350,850). Holding bulk $x_b=0.10$ would create 20 B atoms.

**A2.** $\max[0,(B_{\rm tot}-N_b)/200]\le\theta\le\min(1,B_{\rm tot}/200)$. For B=30, $\theta=0.15$ uses all 30 B at boundaries and leaves bulk B=0, feasible at the endpoint; $\theta=0.625$ would require 125 boundary B and is impossible. In $N_b g_b+200g_s$, each count divided by $N_{\rm Av}$ is mol of sites, giving J. Dividing this numerator by $N_b+200$ gives the numerically scaled J/mol-all-sites energy; dividing by both would be a double normalization.

**A3.** For $\theta=(0.10,0.15,0.20,0.25)$, $x_b=(0.10375,0.10250,0.10125,0.10000)$ and $\bar g\approx(-10537.4054,-10541.3690,-10541.1526,-10537.6008)$ J/mol all sites. Each row has $8000x_b+200\theta=850$. The lowest supplied trial is 0.15; the continuous minimum lies near 0.17160752. The closed energy includes bulk and boundary Gibbs terms at changing compositions. It does not subtract fixed reservoir chemical potentials.

**A4.** $B_{\rm tot}=4050$. At $\theta=(0.25,0.35,0.50)$, $x_b=(0.50000,0.49750,0.49375)$ and $\bar g\approx(-8779.3274,-8784.2909,-8774.7336)$ J/mol all sites. The best supplied trial is 0.35. Positive $\delta$ depletes boundary B relative to its final bulk; the selected occupancy can exceed the supplied initial 0.25, as it does here.

**B1.** $dx_b/d\theta=-200/8000=-0.025$ for the main cell. The ideal ALPHA pure-endmember difference $\Delta$ occurs in both $g_s'$ and $g_b'$ and cancels. $\bar g'=200/8200\{\delta+RT[\ln\frac{\theta}{1-\theta}-\ln\frac{x_b}{1-x_b}]\}$. Its bracket derivative is $RT[1/(\theta(1-\theta))+(200/8000)/(x_b(1-x_b))]>0$, with opposite endpoint signs. Root $\theta\approx0.171607524$; a direct total-energy minimum is about 0.171607533. The first evaluates a separately derived exchange condition; the second minimizes the full constrained energy. Agreement is numerical evidence within the model, not an independent experimental validation.

**B2.** At the direct result, $x_b\approx0.101959812$, bulk B$\approx815.67849$, boundary B$\approx34.32151$, total B=850. Bulk A$\approx7184.32151$, boundary A$\approx165.67849$, total A=7350. $\theta-x_b\approx0.06964772$. Site density $S/A=5$ sites/nm² gives $\Gamma_B\approx0.348239$ atom/nm² $\approx5.78264\times10^{-7}$ mol/m². Whole-cell excess $200(\theta-x_b)\approx13.92954$ atoms over 40 nm² gives the same value. Dividing by only one 20 nm² boundary doubles it; using starting $x_0=0.10$ uses the wrong final bulk reference and biases the excess.

**B3.** Zero preference gives $\theta_*=x_b=z=850/8200\approx0.103658537$, distinct from initial bulk 0.10. In the open zero-preference case the reservoir keeps $x_b=0.10$ and selects $\theta=0.10$. The three closed cells have B totals 850, 8050 and 80050 respectively. At $\delta=-5000$, closed exchange roots are about 0.17160752, 0.16887603 and 0.16859195. Their absolute errors against open $0.16856026$ are about 0.00304726, 0.00031577 and 0.00003169, strictly decreasing, with final error below the fixed $5\times10^{-5}$ limit. This only checks a mathematical reservoir-size limit of the synthetic model.

**B4.** In the 4050-B cell with $\delta=+5000$, $\theta_*\approx0.35171022$, $x_b\approx0.49745724$, $\bar g\approx-8784.29224$ J/mol all sites. Bulk B$\approx3979.65795$, boundary B$\approx70.34205$, total B=4050; total A=4150. The final excess is $5(\theta-x_b)\approx-0.728735$ atom/nm² $\approx-1.21009\times10^{-6}$ mol/m²; whole-cell excess $\approx-29.1494$ atoms over 40 nm² agrees. The first statement confuses sign relative to the final bulk with movement from a supplied trial; compare $\theta_*$ to $x_b$, and note $0.3517>0.25$. The second breaks B conservation; recalculate $x_b$ and the 4050-B sum. The third lacks a second compatible structural branch and real interface evidence; optimizer convergence is only a numerical status for one declared function.

## Readiness record

Preserve independent A4/B4 reasoning and the failed-claim checks. The code tests check the closed synthetic model only. The second state has its own contract (Lesson 14). No real-material inputs are involved.
