# Task 02 — answers and observed fit

1. Pure FCC Ni at the same temperature fixes the activity reference. Its Gibbs
   energy already includes the magnetic contribution; subtract it once.
   FCC has one real metal atom per formula unit and fixed VA is bookkeeping,
   so `GM` is J/mol metal atoms, with divisor one. An equilibrium mixture may
   have different phase compositions and chemical potentials; it is not the
   measured homogeneous FCC response at each supplied composition.
2. At $x=0.5$, $\delta g=\delta L_0/4$ and
   $d\delta g/dx=-\delta L_1/2$. Therefore
   $\delta\mu_{Ni}=(\delta L_0-\delta L_1)/4$.
   The [actual run](activity_fit_results.json) returns corrections
   **519.991892** and **39.460350 J/mol**, giving **120.132886 J/mol**.
   The homogeneous model's pure-Ni activity is unity to arithmetic precision.
3. The isothermal interactions at 1000 K change as follows (J/mol atoms):

   | Value | Pinned input | Fit |
   |---|---:|---:|
   | $L_0(1000)$ | 11469.89 | 11989.881892 |
   | $L_1(1000)$ | −1044.16 | −1004.699650 |

   The residual sum falls from **627804.870690** to **202937.165894 (J/mol)²**.
   At $x=0.3$, the reported activity is **0.5985**: the input predicts
   **0.598163**, the fit **0.616491**. That point gets worse. At $x=0.5$, the
   fit predicts **0.740367**, versus input **0.729746** and observation
   **0.7506**; it improves but is not exact. Minimizing a sum does not promise
   that every residual shrinks. These digits permit arithmetic reproduction;
   they are not experimental precision or a scientific agreement criterion.
4. $(A_k+1000c)+(B_k-c)1000=A_k+1000B_k$. Distinct A/B pairs therefore produce
   the same isothermal interaction. Other-temperature activity/entropy-sensitive
   information would help distinguish them; simply adding more compositions
   at the same temperature cannot. No such extension is assigned here.
   Calibration to observations used in or predating an assessment is not
   independent validation. All nine rows enter this demonstration's fit; no
   held-out physical validation group or confidence interval is claimed.

The pinned source TDB is unchanged. Only its FCC chemical isotherm receives an
in-memory correction; no new reusable temperature-dependent database is issued.
The fit ran in about **0.63 s internally**, excluding Python imports, with nine
observations and a 201-point plot. Hand and normal-equation checks pass the
declared $10^{-7}$ J/mol tolerance. Visual inspection confirms that residuals
remain across composition. The selected Table 1 rows were checked visually
against the source table. If you write your own version, also check that the
pure-Ni activity is one, that a fit to activities generated from known
interaction values recovers them, that repeated or pure-endpoint compositions
and zero or missing activities are rejected, and that one temperature
cannot separate $A_k$ from $B_k$.
