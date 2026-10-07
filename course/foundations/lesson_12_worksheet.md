# Lesson 12 worksheet — trial sites and open equilibrium

Use the [reading](lesson_12_reservoir.md) and [contract](boundary_one_state_contract.md). Keep the [answer guide](../instructor/lesson_12_guide.md) closed until the independent tasks. State units and the fixed reservoir for every calculation. A calculator and paper suffice; the Python module is optional.

## Meeting 28 — energy and exchange

**A1 — reference check, guided.** At $T=1000$ K, $x_b=0.10$ and $\delta=-5000$ J/mol boundary sites, calculate $RT$. Write $\phi(\theta)$ both as $g_{\rm site}-(1-\theta)\mu_A-\theta\mu_B$ and as the logarithmic expression. Why does $\phi(x_b)=\delta x_b$? State what reference makes this an *excess* potential and why it is not an absolute physical grain-boundary energy.

**A2 — three supplied trials.** Calculate $\phi$ at $\theta=0.10,0.15,0.25$. Choose the lowest *of these trials*. Is that yet a continuous equilibrium? Sketch how an untested occupancy could be lower. Include both component chemical potentials in the reservoir expression.

**A3 — exchange diagnostic.** For the two-boundary cell, occupancy rises from 0.10 to 0.20 at fixed bulk reservoir $x_b$. Give cell and reservoir changes in A and B expected atom counts. A colleague uses $g_{\rm site}-\theta\mu_B$ and finds a minimizer. Identify the missing transfer and explain why a converged optimizer cannot repair it.

**A4 — independent fresh preference.** At $x_b=0.25$ and $\delta=+4000$ J/mol sites, calculate $\phi$ at $\theta=0.15,0.20,0.25$ and select the lowest trial. Predict whether the continuous optimum is above or below $x_b$ before calculating it. A positive $\phi_*$ may still be the minimum: explain what zero means for this reference.

## Meeting 29 — derivation, excess and limits

**B1 — derive the one-state minimum.** Differentiate the logarithmic $\phi$, show $\phi''>0$ for interior occupancy, and derive the odds relation. Calculate $\theta_*$ for A1 and compare it with A2's best supplied trial. Calculate $\phi_*$ using $-RT\ln[1-x_b+x_b e^{-\delta/(RT)}]$. Why is it legitimate to compare a direct bounded minimizer with this different analytical route?

**B2 — convert and balance.** For B1, calculate $\Gamma_B$ in atom/nm² and mol/m² using $S=100$ sites and $A=20$ nm² **per boundary**. Check independently from $2S(\theta_*-x_b)$ excess B atoms and $2A$ total area. Say what wrong value results if the whole-cell excess is divided by one boundary area. State the simultaneous A transfer.

**B3 — zero preference and analytical limits.** Repeat the odds relation for $\delta=0$. Take the analytical limits $x_b\to0^+$ and $x_b\to1^-$ for the two occupancy ratios in the reading. Do not feed $x_b=0$ or 1 to the numerical solver. Explain whether $\Gamma_B=0$ alone identifies a real boundary phase.

**B4 — independent exit and failure analysis.** For A4's $x_b=0.25$, $\delta=+4000$, calculate $\theta_*$, $\phi_*$ and $\Gamma_B$ in both units. Use the whole-cell count route as a check. Then assess three purported results: (i) $\theta_*=0.25$ with this nonzero preference, (ii) $\theta_*>x_b$ for positive preference, (iii) an objective returned by a solver without checking it against the formula. Identify a detecting check for each. State one question this one-state exercise cannot answer about a real interface.
