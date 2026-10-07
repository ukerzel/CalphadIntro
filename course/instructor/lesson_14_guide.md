# Instructor guide — two synthetic closed-state branches

[Reading](../foundations/lesson_14_competing_states.md), [worksheet](../foundations/lesson_14_worksheet.md), [two-state contract](../foundations/boundary_two_state_contract.md), meetings 32–33. Timings are planned; they have not been observed with learners. Keep the State I/II energy cards on one amount basis and at one total B before asking for a winner.

| Minutes | Meeting 32 | Meeting 33 |
|---|---|---|
| 00–10 | Retrieve Lesson 13 closed inventory | Retrieve state-energy difference and sign |
| 10–25 | Align geometry, references, baselines | Bracket crossing and derive monotonicity |
| 25–40 | Work A1, A2 | Work B1, start B2 sensitivity |
| 40–45 | Break | Break |
| 45–70 | A3 unminimized trap | Finish B2, diagnose B3 claims |
| 70–85 | A4 independent, feedback | B4 independent, feedback |
| 85–90 | Exit: same inventory? | Exit: what is not proven? |

Each meeting allocates 85 contact/practice minutes plus a five-minute break. Use supplied minimized values for the paper route; numerical minimization is optional. Preserve independent A4/B4 balance and interpretation. Record support and time from the attempts.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1 | A state changes boundary energy, not cell capacity or inventory. | Total B=$8000x_0+50$; both use the ideal ALPHA model I1 and the same $q(\theta)$. |
| A2 | Sum 8000$x_b+200\theta$ separately for I and II. | Baseline contribution is $200(2000)/8200$ J/mol all sites. |
| A3 | Compute the positive unminimized difference first. | Then compare two *separately minimized* full energies: their difference is negative. |
| A4 | Both totals should round to 4050 B. | Subtract State II minus State I in the same J/mol-all-sites basis. |
| B1 | More negative State II preference means its $\theta$ is greater. | Fixed B then gives $x_{b,II}<x_{b,I}$ and a lower envelope slope. |
| B2 | A constant baseline does not move a within-state minimizer. | Shift $D$ by $200(\Delta\eta)/8200$; positive shift needs more B to cross. |
| B3 | Ask whether the two numbers are the same thermodynamic potential. | Distinguish invented branch ordering from material interface coexistence. |
| B4 | Total B=$8000(0.20)+50$. | At $+100$, add $2.43902$ J/mol all sites to the original $D$. |

## Answers and detecting failures

**A1.** $T=1000$ K, $p=100000$ Pa, $N_b=8000$, $K=2$, $S=100$ sites and $A=20$ nm² each, total sites=8200, $\theta_0=0.25$. At $x_0=0.10$ both states have B=850 and A=7350. Both use $g_b(\theta)$ plus $\eta_i+\delta_i\theta$, with $(\eta_I,\delta_I)=(0,-5000)$ and $(\eta_{II},\delta_{II})=(2000,-10000)$ J/mol boundary sites. Same cell inventory, geometry, T/p, ideal ALPHA reference, amount unit and minimized closed potential are needed; a shared final $x_b$ is *not* required.

**A2.** State I: $8000(0.10195981)+200(0.17160752)\approx850$. State II: $8000(0.09952543)+200(0.26898261)\approx850$; discrepancies at these printed precisions are rounding. $D=-10519.50695-(-10541.72679)\approx+22.21984$ J/mol all sites, so I is lower. The baseline adds $200(2000)/8200\approx48.78049$ J/mol all sites. Omitting it makes the difference about $-26.56064$ J/mol all sites and falsely selects II at low B.

**A3.** Total B=$8000(0.25)+50=2050$. Minimized $D=-10718.80845-(-10713.32958)\approx-5.47887$ J/mol all sites, favoring II. At the unminimized common $\theta=0.25$, the difference is $200(750)/8200\approx+18.29268$ J/mol all sites, favoring I *among those two trials*. Separate relaxation changes each state's $\theta$ and bulk $x_b$, so the trial comparison cannot choose the lower minimum.

**A4.** Total B=4050. State I balance $8000(0.49032338)+200(0.63706496)\approx4050$; State II $8000(0.48725436)+200(0.75982577)\approx4050$. $D=-8941.48054-(-8904.79653)\approx-36.68401$ J/mol all sites, favoring II. State II traps more B at the boundary; the finite bulk gives up B and ends at a smaller fraction while the total is identical.

**B1.** Positive $D(0.10)$ and negative $D(0.25)$ bracket a root near $x_0=0.21618678$. At that root, $\theta_I\approx0.332074$ and $\theta_{II}\approx0.470497$, not equal. State II's more negative preference selects larger boundary occupancy; fixed B makes its bulk fraction lower. The ideal bulk $g_b'$ rises with $x_b$, so the envelope slope of State II is lower; $D'(x_0)<0$ throughout the checked range. The 17-point scan detects an implementation mistake in ordering; it alone cannot exclude extra crossings between grid points. The analytical slope argument does so within the declared model.

**B2.** $\Delta D=200(\pm100)/8200=\pm2.43902439$ J/mol all sites at fixed $x_0$. Neither occupancy changes because the baseline is constant in $\theta$. Raising $\eta_{II}$ delays the root to a larger $x_0$; lowering it advances the root. The three roots are about 0.20187111 (1900), 0.21618678 (2000), 0.23094775 (2100). This sensitivity is to invented inputs, not a real-material uncertainty interval.

**B3.** (i) Omits State II's positive structural baseline; low-B $D>0$ selects I. (ii) Open grand potential and closed total Gibbs energy use different ensembles and reference terms; no subtraction is defined. (iii) Only total B and branch energies match at the crossing; state-specific minimizers and final bulk fractions can differ. (iv) No real material's structural identity, defect geometry, measured/free-energy inputs, mixed-domain/junction equilibrium or independent evidence is present.

**B4.** Total B=1650. State I $8000(0.19847005)+200(0.31119788)\approx1650$; II $8000(0.19508598)+200(0.44656066)\approx1650$. $D=-10788.15021-(-10790.91356)\approx+2.76335$ J/mol all sites, selecting I. Raising $\eta_{II}$ by 100 adds $2.43902$, leaving $D\approx+5.20237$, still I at the same inventory. A real-interface transition claim needs eligible structural/source evidence, compatible physical interface excess/potential and coexistence conditions, plus independent scientific and material validation. This exercise supplies none.

## Readiness record

Preserve the paper balance, baseline and unminimized-trial diagnostics, and mark actual independent learner completion only from real attempts. No real-material, mixed-state or learner inference follows from the code tests.
