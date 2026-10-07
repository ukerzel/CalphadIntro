# Instructor guide — Clinic D synthetic boundary synthesis

Use the [Clinic D sheet](../foundations/clinic_d_synthetic_boundary.md) after
Lesson 14, meeting 34. Timings are planned; they have not been observed with learners. Keep the paper
route complete and show the answer cards only after the independent attempt.
The clinic does not substitute for the missing real inputs discussed in Lesson 15.

| Minutes | Activity | Detecting question |
|---|---|---|
| 00–10 | Retrieve the synthetic boundary geometry, balances and potential choice | Which area goes with a whole-cell excess? |
| 10–22 | Work D1 count and reference | Is 2450/8200 a bulk fraction? |
| 22–40 | Guide D2 open exchange and excess | What replaces each incoming B? |
| 40–45 | Break | — |
| 45–58 | Guide D3 finite inventory and planted fixed-bulk error | Which B total changed in the wrong trial? |
| 58–70 | D4 state comparison and baseline/ensemble errors | Were both states separately relaxed in one cell? |
| 70–85 | D5 independent transfer, then feedback | Does a model result imply a Ni–Cu result? |
| 85–90 | D6 exit and support record | Which potential matches each constraint? |

The 90 minutes include a five-minute break.
Let learners explain D5 orally with an inventory sketch if arithmetic takes
longer, but preserve the independent constraint and claim decision.

## Worked answers and rejection controls

**D1.** Bulk A=$8000(0.70)=5600$; boundary A=$200(0.75)=150$;
total A=5750. Total sites=8200, B=2450 and average B fraction
$2450/8200\approx0.29878049$. The two boundary areas sum to 40 nm².
Using 20 nm² with a whole-cell excess doubles the answer.

**D2.** $-\delta/(RT)=5000/8314.5\approx0.60136$, so the odds multiplier
is about 1.8246; the open optimum $\theta=0.43882335$ exceeds 0.30.
Boundary B grows from 50 to $200(0.43882335)\approx87.76467$:
about 37.76467 B atoms enter from the reservoir and the same number of A
atoms leave to it. The chosen-reference excess is
$5(0.43882335-0.30)\approx0.69411676$ atom/nm², or
$1.15261\times10^{-6}$ mol/m². Subtract both
$(1-\theta)\mu_A$ and $\theta\mu_B$ from $g_{\rm site}$.
$\phi=-1837.87532$ J/mol boundary sites is an excess grand potential under
that fixed reservoir, not an absolute grain-boundary free energy.

**D3.** With fixed B=2450,
$8000(0.29541426)+200(0.43342952)\approx2450$;
using printed fractions leaves at most a few $10^{-5}$ atom of rounding.
The whole-cell reference excess is
$200(0.43342952-0.29541426)\approx27.60305$ B atoms over **40 nm²**:
$0.6900763$ atom/nm² or $1.14590\times10^{-6}$ mol/m².
The open result holds an external $x_b=0.30$ and lets cell B change; it is
not the constrained minimum at fixed 2450 B. Holding 0.30 with the closed
State I occupancy instead gives $2400+86.685904=2486.685904$ B atoms,
an error of 36.685904. It is a trial in an open cell, not the declared
closed experiment.

**D4.** State II's printed balance is
$8000(0.29179117)+200(0.57835338)\approx2450$ to rounding.
The baseline adds $200(2000)/8200=48.7804878$ J/mol all sites.
$D=-10542.40484-(-10529.48099)=-12.92385$ J/mol all sites, so State II
is lower among the two separately relaxed uniform model states at this
fixed inventory. Omitting its baseline would give approximately
$-61.70434$ J/mol all sites, still selecting II **here**; omission is
nevertheless a wrong comparison and reverses the low-B result in Lesson 14.
An open excess grand potential in J/mol boundary sites cannot be subtracted
from a closed Gibbs energy in J/mol all sites: ensemble, subtraction terms and
normalization differ. A branch ordering or crossing alone supplies no
mixed-domain, junction or material coexistence evidence.

**D5.** At $x_0=0.40$, total B=$8000(0.40)+50=3250$, A=4950.
State I: $8000(0.39271824)+200(0.54127054)\approx3250$.
State II: $8000(0.38925808)+200(0.67967666)\approx3250$.
The printed values can leave about $4\times10^{-5}$ atom residual.
$D=-9910.05801-(-9884.21053)=-25.84748$ J/mol all sites;
State II is lower among the two declared uniform alternatives.
Its chosen-reference excess is
$5(0.67967666-0.38925808)=1.4520929$ atom/nm².
The strongest statement is a conditional result for invented A/B functions
and this fixed cell. The real case lacks an eligible complete Ni–Cu bulk
model and matched boundary geometry/state/excess energies with references,
uncertainty and independent evidence. Either exact missing field is acceptable
if the material and transition claims are withheld.

**D6.** D2 fixes the *external* reservoir composition and chemical
potentials; D3–D5 fix total cell A/B. Their minimized quantities have
different reference subtractions and amount bases, so direct subtraction is
undefined.

## Follow-up after an actual attempt

If the excess has a factor of two error, redraw two boundary areas. If the
closed balance fails, solve $x_b=(B_{\rm tot}-200\theta)/8000$ before any
energy comparison. If a learner uses $\phi$ for D4, make them name the
held-fixed variables and the J/mol basis. If the claim answer promotes
Ni–Cu, return to [Clinic C](lesson_10_guide.md) and the source GAP.
Record learner support, timing and revised work from the attempt.
