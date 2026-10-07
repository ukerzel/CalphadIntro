# Lesson 10 — audit a real source before calculating a reservoir

Meetings 23–24 and [Clinic C](lesson_10_worksheet.md). First complete [Lesson 9](lesson_09_fitting.md): a fitted number, a checked implementation and a checked material claim are different results. Use the [worksheet](lesson_10_worksheet.md) and [instructor guide](../instructor/lesson_10_guide.md). Paper and pencil suffice. This packet teaches an audit where required inputs are missing (**GAP**); it contains no Ni–Cu bulk calculation or material prediction.

**Exit goal:** build a source/model card, identify which evidence can support each claim, state the missing inputs for a Ni–Cu bulk reservoir, and explain how one would calculate chemical potentials after an eligible model and result packet were accepted.

## 10A — fix the question and the source roles

Our proposed later question is Cu Gibbsian excess $\Gamma_{\mathrm{Cu}}$ (mol/m²) at one specified Ni grain boundary, against a verified FCC Ni–Cu bulk reservoir. Ni–Cu is chosen provisionally for teaching; its source and geometry inputs are a **GAP**. The case proposes a [111] tilt boundary but does not provide its plane, misorientation, area, site/atom inventory, state or matched excess data. A grain-boundary potential alone cannot supply a bulk CALPHAD $g(T,p,x)$.

Read each row as evidence for a *particular role*, not as an interchangeable file. The SFB, NIST and SGTE pages were checked on 29 September 2026; the Mey row uses its bibliographic record because the DOI landing page did not load in this check. A later material use must recheck its exact artifact and terms.

| Record | What it supports here | What is still missing for this case |
|---|---|---|
| [SFB B06 project page](https://www.sfb1394.rwth-aachen.de/index.php?L=0&id=399) | Motivation: Ni–X with X=Cu, Au or Nb; [111] tilt work described for pure Ni | A published, matched Ni–Cu [111] boundary data packet and its geometry |
| [Mey Cu–Ni reassessment](https://doi.org/10.1016/0364-5916(92)90022-P) | A bibliographic lead for a bulk thermodynamic assessment | An eligible complete, exact-version bulk TDB with unaries, references, phase/magnetic terms, domain, rights and independent checks |
| [SGTE unary page](https://www.sgte.net/en/free-pure-elements-database) | Pure-element descriptions exist | Its stated use is limited to assessment extraction or pure-element tables/plots; a free download does not clear combined-model redistribution or this course case |
| [Fischer Cu–Ni entry at NIST](https://www.ctcms.nist.gov/potentials/entry/2019--Fischer-F-Schmitz-G-Eich-S-M--Cu-Ni/2019--Fischer-F--Cu-Ni--LAMMPS--ipr1.html) | Atomistic Cu–Ni grain-boundary study and potential implementation lead | It studies $\Sigma5$ and $\Sigma3$ boundaries, not the proposed [111] Ni geometry; the displayed `ipr1` files are superseded, and an EAM file is not a bulk Gibbs-energy TDB |

For any artifact, a DOI establishes identity, a download route establishes access, and neither alone supplies reuse permission or scientific fitness. The NIST page says its potential files were posted with the contributor's permission; that is not a repository redistribution licence. No file is downloaded or copied for this lesson.

### Fill the model card

| Field needed before a real Ni–Cu calculation | Current card |
|---|---|
| Observable and amount basis | Proposed $\Gamma_{\mathrm{Cu}}$ in mol/m²; requires an explicit Gibbsian excess/reference convention |
| Bulk model bytes, version/hash and rights | **GAP** — no eligible Ni–Cu TDB selected |
| Pure Ni/Cu reference functions, phase topology and magnetic terms | **GAP** — inspect the selected model, not the paper title |
| Temperature, pressure, composition and phase domain | **GAP** — must be fixed with the selected model and case |
| Independent bulk verification and held-out material observations | **GAP** — no checked bulk input/result packet |
| Boundary plane, misorientation, state, area and site/atom amounts | **GAP** — no matched [111] Ni–Cu packet |
| Defect free-energy/excess evidence and its use rights | **GAP** — no checked defect input packet |

The card can be complete as an **audit** while these input fields remain GAP. Do not replace a blank with an invented value. A model for Cu–Ni bulk, an atomistic boundary potential and an experimental excess curve would each need separate provenance and an explicit compatibility argument.

## 10B — trace the reservoir calculation that is currently blocked

In the synthetic [binary-family contract](binary_family_contract.md), at fixed $T,p$ and homogeneous $x_B$, $g$ is Gibbs energy per mole of atoms and $g'=\partial g/\partial x_B$. For one differentiable phase,

$$\mu_A=g-x_Bg',\qquad \mu_B=g+(1-x_B)g'.$$

Both chemical potentials are in J/mol of their respective atom component. They are derivatives of **total** $G$ with respect to component amount while the other component's amount is fixed. The slope $g'=\mu_B-\mu_A$ instead describes an A-for-B exchange at fixed total amount. An equilibrium multiphase reservoir needs its accepted phase set and supporting equilibrium before a homogeneous derivative can be treated as the reservoir state; reporting a metastable FCC derivative as the stable reservoir would answer another question.

**Worked arithmetic, explicitly synthetic:** at $x_B=0.2$, suppose $g=-9000$ J/mol and $g'=3000$ J/mol. Then $\mu_A=-9600$ J/mol and $\mu_B=-6600$ J/mol. Check $(1-x_B)\mu_A+x_B\mu_B=-9000$ J/mol. The arithmetic checks the amount/reference convention only. These supplied values are not a Ni–Cu model, calculation or validation.

A future **eligible** real packet would have to fix the exact model bytes and reference states; $T,p,z$ and allowed phases; the stable bulk state and actual phase compositions/amounts; the chemical-potential convention and units; numerical checks against an independent route; and genuinely held-out material evidence in the claimed domain. If the reservoir is multiphase, common component chemical potentials and both balances must be checked. Bulk $\mu_i$ can then condition a separate boundary model under compatible mechanical and reference conditions. It does not calculate $\Gamma_{\mathrm{Cu}}$ by itself.

Here the exact case selection is a **GAP** and no checked Ni–Cu bulk input/result packet exists, so Lesson 10B traces the prerequisite audit instead of a real calculation. No real $\mu_{\mathrm{Ni}}$, $\mu_{\mathrm{Cu}}$, phase diagram or segregation value is reported. Selecting the exact case and checking the bulk model must come before such a result.

## Clinic C — choose the strongest justified claim

Use the fresh [claim/data matrix](lesson_10_worksheet.md) after the two meetings. A noiseless recovery of the known synthetic $\Omega$ establishes recovery for that generating equation. Plain/tool agreement on the declared synthetic model establishes same-model implementation agreement at the checked points. A paper or potential about the right alloy is a source lead until the exact model, geometry, observables, rights and independent material comparison align.

## Vocabulary and source boundary

**Source card:** exact artifact, rights, physical role, domain, reference, and checks. **Reservoir:** bulk state fixing the component chemical potentials for an open boundary model. **Recovery:** return of a known generating parameter. **Verification:** check that a stated model is represented/evaluated as intended. **Material validation:** comparison of that model's predictions with relevant independent observations in a declared domain. **GAP:** a required input or independent check is absent; it is a recorded decision, not a numerical result.
