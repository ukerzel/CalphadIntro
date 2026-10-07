# Instructor guide — Ni–Cu source audit and Clinic C

[Reading](../foundations/lesson_10_source_audit.md), [worksheet](../foundations/lesson_10_worksheet.md), meetings 23–25. This is an audit-only route that stops at GAP. No real Ni–Cu reservoir result is available. Timings are planned; they have not been observed with learners. Display the source-role and blank-card columns; reveal this answer key only after attempts. Do not fill gaps with an invented TDB, geometry or chemical potential.

| Minutes | Meeting 23 | Meeting 24 | Meeting 25 |
|---|---|---|---|
| 00–10 | Retrieve what Lesson 9's synthetic recovery proved | Retrieve $g$, $G$ and component amounts | Retrieve recovery, verification, material validation |
| 10–22 | Read the four source roles | Work B1 amount derivative | Explain claim/data matrix and source-card fields |
| 22–40 | A1 worked, A2 card start | B2 chain and evidence circles | C1–C4 individually, then compare |
| 40–45 | Break | Break | Break |
| 45–70 | A2 finish, A3 planted mismatch | B3 mismatch and B4 setup | C5 claim challenge, C6 independent card |
| 70–85 | A4 independent, feedback | B4 independent, feedback | C6 feedback and support record |
| 85–90 | Exit: name the first GAP | Exit: state the blocked result | Exit: strongest defensible claim |

Each meeting is 85 contact/practice minutes plus 5 break. Preserve the independent attempt even if the audit vocabulary needs support. A paper card is the complete route. Optional browsing of linked public pages must respect access/rights and is not needed for a learner to complete the supplied exercise. Record actual learner time and reasoning only from real attempts.

## Staged hints

| Task | First hint | Second hint |
|---|---|---|
| A1/A2 | Separate research aim, thermodynamic model and atomistic model. | An article citation does not give executable model bytes or rights. |
| A3 | List the nouns: EAM, TDB, $\Sigma5$, [111]. | NIST marks `ipr1` superseded; compare geometry before using a value. |
| A4 | Name one missing bulk and one missing boundary artifact. | No accepted Ni–Cu case selection or bulk material input exists; choose GAP. |
| B1 | $\mu_A=g-xg'$, $\mu_B=g+(1-x)g'$. | Reconstruct $g$ with the mole fractions. |
| B2/B3 | A homogeneous phase derivative is conditional on that state. | Check stable phases, both balances, actual compositions and references. |
| B4 | Phase regions can exchange both components at fixed $T,p$. | Match both $\mu$ values; sum region amounts and each component inventory. |
| C1–C4 | Ask which exact model/data generated the observations. | Same-generator held-out values are still synthetic. |
| C5/C6 | Trace each arrow from source to claimed observable. | A matched independent material observation needs geometry, state, $T$, bulk composition/reference, excess definition and uncertainty. |

## Answers and rejection controls

**A1.** SFB B06 motivates the Ni–X research question; it does not provide a complete Ni–Cu bulk/boundary case. Mey is a bibliographic thermodynamic assessment lead; no eligible complete TDB is supplied. SGTE supplies restricted-use pure-element descriptions, not permission to combine and redistribute a course model. Fischer/NIST supplies an atomistic Cu–Ni boundary/potential lead; its $\Sigma5$/$\Sigma3$ geometries and semi-grandcanonical study do not identify the proposed [111] Ni boundary. The NIST entry is the page with those two labels.

**A2.** Mey: source ID “Mey 1992 Cu–Ni assessment”, role bulk literature; paper DOI known, exact runnable TDB/version/hash/rights and complete model/independent checks GAP. NIST/Fischer: source ID “Fischer et al. 2019”, role atomistic boundary lead; NIST names `ipr1` implementation, marks files superseded, lists $\Sigma5$/$\Sigma3$, and says files were posted with contributor permission. A selected current implementation hash/licence, matched [111] geometry/excess data and bulk CALPHAD model remain GAP. Neither record alone gives an accepted bulk input or a matched boundary input.

**A3.** Reject EAM→CALPHAD TDB (different representation/quantity), NIST access→repository redistribution licence, $\Sigma5$→[111] Ni boundary equivalence, and published study→validation of this distinct case. Check exact rights text and artifact hash; audit bulk endmembers/interactions/references/magnetism/domain; fix the exact boundary geometry/state/area/inventories and excess definition; obtain an independent matched observation with uncertainty and declared calibration/validation role. No numerical repair can fix a missing source identity.

**A4.** Proposed $\Gamma_{\mathrm{Cu}}$ is mol/m² for one fixed Ni boundary against an FCC Ni–Cu reservoir. Literature and the SFB project page motivate Ni–Cu study, and Fischer gives a Cu–Ni atomistic lead. The first bulk blocker is an eligible full Ni–Cu TDB with references/rights and a semantic/reference audit; the boundary blocker is matched [111] geometry/state/excess data. Executable status is **GAP**. Specific equivalent wording is acceptable if it preserves these limits.

**B1.** $\mu_A=-9000-0.2(3000)=-9600$ J/mol; $\mu_B=-9000+0.8(3000)=-6600$ J/mol. Reconstruction: $0.8(-9600)+0.2(-6600)=-9000$ J/mol. $g'=\mu_B-\mu_A=3000$ J/mol is the fixed-total exchange slope. The supplied numbers are a separate synthetic arithmetic example.

**B2.** The Ni–Cu route stops before the first exact eligible bulk artifact: the case selection is a GAP, and no accepted bulk model/result exists. A literature lead, a pure-element file or an EAM potential is not circled as a complete TDB. At the chemical-potential arrow use $G$ in J, $n_i$ in mol of atoms, $g$ and $\mu_i$ in J/mol of component, and composition as mole fraction on the same amount basis. Independent checks and held-out material evidence remain unfilled.

**B3.** Confirm allowed phases and stable equilibrium at fixed $T,p,z$, including both component balances and support, then evaluate the reservoir's common $\mu_i$ with the accepted model/reference. A homogeneous metastable derivative is only that conditional branch result. $g'=\mu_{\mathrm{Cu}}-\mu_{\mathrm{Ni}}$ if B=Cu; $\mu_{\mathrm{Cu}}=g+(1-x)g'$, not $g'$ alone.

**B4.** At equilibrium with exchange of both components, coexisting regions share $\mu_A$ and $\mu_B$ at the same $T,p$ in a compatible reference. Fractions satisfy $\sum f_r=1$ and $\sum f_rx_r=z$; equivalently $\sum f_r(1-x_r)=1-z$. The case selection remains GAP and no eligible bulk input exists, so do not report real Ni–Cu $\mu_i$ or $\Gamma$. An exact source with rights, a semantic audit and independent bulk checks are needed before any calculation, followed by matched boundary evidence.

**C1.** Synthetic recovery: the known coefficient returns from its own noiseless generating equation; the four held-out points check same-generator prediction and are not material observations. **C2.** Same-model verification: two implementations agree within recorded synthetic checks, not a real-alloy validation. **C3.** Bibliographic/source lead plus executable material GAP: a cited assessment is not an accepted exact TDB. **C4.** Atomistic source lead plus geometry/rights GAP: $\Sigma5$/$\Sigma3$ and superseded `ipr1` do not test [111] Ni.

**C5.** The invalid chain promotes synthetic Ω to Ni–Cu, treats implementation parity as experimental confirmation, treats a paper as model bytes, and substitutes different boundary geometry. The narrow conclusion is that synthetic bulk concepts and implementations have been checked for their declared model, while Ni–Cu source and geometry remain GAP. A future held-out material observation must state measured observable and excess convention, exact boundary geometry/state, $T$, bulk composition/reservoir reference, uncertainty/provenance and separation from calibration/model selection.

**C6.** Accept cards/matrices that preserve exact role, rights and missing-field labels, and distinguish these three claims without real numbers. For the material row, the targeted next check is exact eligible bulk artifact/rights and semantic/reference audit; boundary evidence is a separate later check. Mark learner support as an observation only after a real attended attempt. A polished card alone cannot support a teaching-effectiveness claim.

## Readiness and stop record

Collect A4, B4 and C6 with the learner's evidence labels. If the learner conflates EAM/TDB, geometry or synthetic/material validation, revisit that specific card before Lessons 11–12. Lesson 11's boundary geometry contract uses invented inputs and does not promote Ni–Cu inputs. Material computation remains stopped at GAP; no result from this audit should be graphed as a measured or predicted segregation curve.
