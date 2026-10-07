# Instructor guide — boundary inventory and amount basis

[Reading](../foundations/lesson_11_geometry.md), [worksheet](../foundations/lesson_11_worksheet.md), [boundary geometry contract](../foundations/synthetic_boundary_contract.md), meetings 26–27. Work with cards labelled “per boundary,” “bulk,” “cell” and “external reservoir”; hold numerical answers back until the independent attempts. There is no real alloy, boundary free-energy function, solver result or observed learner timing here.

| Minutes | Meeting 26 | Meeting 27 |
|---|---|---|
| 00–10 | Retrieve mole fraction and component balance | Retrieve two-interface area and excess reference |
| 10–22 | Draw geometry and label all counts/units | Explain open versus closed system boundary |
| 22–40 | A1 worked, start A2 | B1 worked exchange, start B2 |
| 40–45 | Break | Break |
| 45–70 | Finish A2, diagnose A3 | Finish B2, diagnose B3 |
| 70–85 | A4 independent, feedback | B4 independent, feedback |
| 85–90 | Exit: occupancy versus excess | Exit: what changes when B moves? |

Each meeting has 85 contact/practice minutes plus a 5-minute break. If conversions overrun, provide the exact SI constant and unit ladder; retain the independent A4/B4 reasoning. Record support and time from the attempts.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1 | Calculate B in bulk and in **both** boundaries separately. | A=total sites minus B in each region. |
| A2 | Compare actual B with $x_b$ times **all** sites. | Divide 30 atoms by $2A=40$ nm², then use $N_{\rm Av}$. |
| A3 | J/mol must multiply mol. | 20 atoms are $20/N_{\rm Av}$ mol; swap A for B. |
| A4 | Two boundaries contribute $2S=80$ sites. | Check excess by count and by $(S/A)(\theta-x_b)$. |
| B1 | Fixed sites mean $\Delta C_A=-\Delta C_B$ in the boundary. | Add cell and reservoir change columns. |
| B2 | Keep total B=850. | New boundary B=70, so bulk B=780. |
| B3 | Label each area and occupancy separately. | Excess count is $S_1(\theta_1-x_b)+S_2(\theta_2-x_b)$. |
| B4 | Total B is bulk B plus 80$\theta$. | For the 30-B control, boundary B cannot exceed all 30. |

## Answers and detecting failures

**A1.** Bulk (A,B,total)=(7200,800,8000); both boundaries together=(150,50,200); cell=(7350,850,8200). The cell-average B fraction is $850/8200\approx0.1036585$; $x_b=0.10$ uses bulk sites only and $\theta=0.25$ uses boundary sites only. A fraction of cell atoms is not automatically an excess per area.

**A2.** Homogeneous reference B=820; actual B=850; excess=30 atoms. Both boundary areas total 40 nm², so $30/40=0.75$ atoms/nm² $\approx1.2454\times10^{-6}$ mol/m². Independent site density $S/A=5$ sites/nm² times $(0.25-0.10)=0.15$ B/site gives 0.75 atom/nm². Dividing 30 by only 20 nm² gives the wrong 1.5 atoms/nm². $50/(2A)=1.25$ B atoms/nm² is raw boundary B areal content, not bulk-subtracted excess.

**A3.** $20/N_{\rm Av}\approx3.3211\times10^{-23}$ mol of each exchanged component. A $\mu$ in J/mol times 20 raw atoms is dimensionally wrong; multiply by the mol amount. At fixed sites, the exchange's reservoir/energy accounting involves B entering and A leaving, so its chemical-potential difference is $\mu_B-\mu_A$ rather than a B-only chemical potential. No numerical energy is requested.

**A4.** Bulk (A,B,total)=(690,230,920); boundaries together=(40,40,80); cell=(730,270,1000). Reference B=$0.25(1000)=250$; excess=20 B atoms over 20 nm², giving 1 atom/nm² $\approx1.6605\times10^{-6}$ mol/m². Independent route: $(S/A)(\theta-x_b)=(40/10)(0.50-0.25)=1$ atom/nm². Equivalent boundaries need the same area, site count, structural state and occupancy under identical imposed conditions; matching area alone does not establish equivalence for a real specimen.

**B1.** Boundary/cell $\Delta B=+20$, $\Delta A=-20$; external reservoir $\Delta B=-20$, $\Delta A=+20$. Both combined changes are zero. Bulk region in the modeled cell retains $x_b=0.10$ in this ideal large-reservoir route. Adding B without removing A would make 8220 atoms occupy 8200 sites.

**B2.** New boundaries (A,B)=(130,70); bulk (A,B)=(7220,780), so $x_b=780/8000=0.0975$. Cell remains (A,B)=(7350,850). Holding bulk B=800 would give a false B total=870. This is a feasible trial; no boundary energy has selected it.

**B3.** The boundaries differ in area, sites and occupancy, so the equivalent-boundary $2A$ and one-$\theta$ formula cannot be reused. Excess count is $40(0.50-0.25)+60(0.40-0.25)=10+9=19$ B atoms. Actual total area is $10+15=25$ nm²; whole-cell mean excess density is $19/25=0.76$ atom/nm². A state free-energy comparison also needs the same bulk atom/reference basis, compatible mechanical/temperature/pressure conditions and an appropriate potential for the declared ensemble; this sketch alone does not supply one.

**B4.** New boundary B=$80(0.625)=50$, A=30; bulk B=$270-50=220$, A=700; cell remains B=270, A=730. Bulk fraction is $220/920=11/46\approx0.2391304$. For total B=270, the physical bounds allow all $0\le\theta\le1$, because bulk B stays between 190 and 270. In the separate 30-B control, $\theta\le30/80=0.375$, so 0.625 is infeasible. Zero chosen excess states equal occupancy to bulk fraction; it supplies no boundary energy minimum, and one structural state cannot establish a transition between states.

## Readiness record

Retain A4 and B4 explanations, especially both count routes and the failed 30-B control. Mark independent/supported/not-yet, with one concept to revisit. Lesson 12 is the next **separate** step; it declares an explicit boundary free-energy function, parameters, analytical limits and numerical checks before solving. The real-material case selection, bulk model and matched boundary inputs remain missing.
