# Day 2 instructor route — paper first

Use the [learner sheet](worksheet.md), its keep-beside-you reference card,
and the separate [staged hints and answers](answers.md). Bring Day 1's
W9 research-map question onto the board; no prior reading is needed. This
is a proposed 390-minute route; its pacing has not been observed.
Write “invented A/B at 1000 K” above every numeric board calculation and
leave it visible beside the missing source (no matched real Ni–Cu
boundary dataset is supplied). Day 1's Ni–X becomes Ni–Cu (X = Cu) today.

## Preparation and access

Print both primer worksheets and this day's answer sheet separately. Have
scratch paper and calculators available; calculators are recommended for
Day 2. The required logarithms and exponential factor are already printed,
so a missing calculator does not block conceptual participation. Check math
glyphs, tables and small units
in the actual print renderer before teaching; no such room/print test has
yet been recorded. The whole day works without internet, colour, a screen
or a Python environment. Optional live code should only reproduce the
already checked synthetic results; a failed demo is replaced by the printed
cards immediately and is not learner time for environment repair.
For optional demonstrations use the course notebooks from a kernel started
before the session: [f3](../../notebooks/f3_binary_mixing_potentials.ipynb) for D1–D3,
[f7](../../notebooks/f7_boundary_open_closed.ipynb) for D4–D6 and D9, [f8](../../notebooks/f8_boundary_states.ipynb)
for D7. Their checks reproduce the printed cards. Day 2 has no separate
demonstration minutes: take a demonstration from a block's explanation or
check minutes, or show it after the day.

Symbols: the worksheet writes the synthetic boundary contract's per-boundary sites, area and
boundary count as $N_s$, $a_{\rm gb}$ and $n_{\rm gb}$, so that $S$, $A$
and $K$ keep their Day 1 meanings (entropy, Helmholtz energy or component A,
kelvin). If asked about D4's reference: the equal-site excess is a chosen
convention, not automatically the Gibbsian excess of a real boundary with
another atom density or dividing-surface position. In D8, “one common
reference (including the same stress state)” stands for one mechanical
reference.

## Timed board, practice and listening plan

Minute allocations inside each row sum to that row's length. Give a short
explanation, then let learners calculate or classify before revealing
the printed answer. Keep lunch, both breaks and the exit intact.

| Time / task | Minute allocation | Board and learner action | Listen for |
|---|---|---|---|
| 09:00 D0, 15 | 5 bridge; 5 chain; 5 discuss | Day 1 unary $G$ → B fraction → boundary sites → state functions | Treating the unary crossing as a Ni–Cu defect result. |
| 09:15 D1, 45 | 12 explain; 13 worked balance; 15 pairs; 5 check | Moles of A/B, $x$ versus phase amount, both balances | Substituting image area for atom or phase amount fraction. |
| 10:00 D2, 30 | 10 explain; 10 guided arithmetic; 10 check | Reference plus ideal-mixing term at 0.10 and 0.20 | “Zero enthalpy of mixing” mistaken for zero total energy. |
| 10:30, 15 | 15 break | Stop instruction | Preserve break. |
| 10:45 D3, 45 | 15 exchange derivation; 15 pair calculation; 15 interpretation | One B enters as one A leaves; $\mu_B-\mu_A$ | Using $\mu_B$ alone or calling a slope sign a phase change. |
| 11:30 D4, 45 | 12 geometry; 13 worked count; 15 new excess; 5 check | Two boundaries, **40** nm² total area, equal-site subtraction | Counting only one area, confusing occupancy and excess. |
| 12:15, 60 | 60 lunch | Stop instruction | Preserve lunch. |
| 13:15 D5, 45 | 12 open ensemble; 13 odds; 15 pairs; 5 check | Reservoir fixes both $\mu$; supplied factor; selected $\theta$ | Pretending the open cell conserves B or $\phi$ is absolute. |
| 14:00 D6, 30 | 8 closed contrast; 12 trial; 10 supplied-output balance | Fixed 850 B, variable $x_b(\theta)$, total-cell $G$ | Importing the open reservoir subtraction into closed $G$. |
| 14:30, 15 | 15 break | Stop instruction | Preserve break. |
| 14:45 D7, 45 | 12 common basis; 13 row comparison; 15 pairs; 5 caveat | Baseline conversion, separate minima, $D$ within one inventory | Comparing different B totals or calling the toy crossing real. |
| 15:30 D8, 30 | 8 evidence steps; 12 card sort; 10 discussion | Case and source → bulk model → boundary model → calculation and comparison | Treating a usable source, a solver output or one state as a complete real case. |
| 16:00 D9, 30 | 5 set up; 15 pairs; 10 check | Fresh $x_b=0.20$ open versus 1640-B closed | Reusing a fixed reservoir fraction in the closed trial. |
| 16:30 D10, 30 | 15 independent supported exit; 10 feedback; 5 handback | Name aid used and the next task (00–05) to try | Mistaking supported recall for independent mastery. |

This allocates 390 contact minutes, including 186 minutes explicitly for
worked, guided, pair or independent arithmetic/classification in D1–D9.
That is a planned allocation, not measured learner engagement. A fast group
may inspect a derivation from the optional lesson library (for example D3's
chemical-potential results, which the sheet shows without derivation); do
not turn an optional branch into required completion. A slower group should finish constraint and unit
checks before expanding the state-crossing discussion.

## Recovery without hidden prerequisite jumps

If D1's two balances fail, keep one-mole A/B counts visible through D7;
let pairs check B then A independently. If D2's logarithm is the obstacle,
use the printed $q$ values and ask for the reference/mixing distinction.
If D3's $\mu$ notation stalls, physically move a labelled B token into a
filled site while an A token leaves, then return to the difference. If D4's
area denominator fails, draw two separate 20-nm² boundary rectangles and
sum their areas before dividing. For D5–D7, the supplied values keep the
task on ensemble choice, conservation and comparable energy basis rather
than numerical optimization.

Day 2 is denser than Day 1. Recover in this order (the same as the
[README](README.md)):

1. Shorten D8 discussion from 30 to 15 minutes and transfer 15 to the
   weakest core step.
2. Drop D7 question 3, the optional D4 mol/m² conversion and D2 question 2.
3. Replace any optional demonstration with the printed cards.
4. Keep D9 and D10 as the check of transfer, and keep lunch and both
   breaks. If core work still does not fit, record which outcomes remained
   incomplete and revise a later offering rather than declaring the two-day
   sequence finished by the clock.

## Operations-research asides (optional, at most 5 minutes each)

For groups with operations-research learners, or when teaching with an operations-research
colleague. Each aside connects the step to the advanced steps 07–18 of the website; none is needed
for the day's outcomes.

- **D1:** two balances, two unknown amounts: solving that two-by-two system is
  the lever rule.
- **D3:** the tangent's end heights are prices: what one more A or B atom costs
  at this composition. In the advanced steps they reappear as the multipliers of a linear
  programme.
- **D5 and D6, the strongest joint moment:** the open cell is the closed problem
  with its B balance removed and a fixed price ($\mu$) charged for B instead, a
  Lagrangian relaxation; the closed cell is the constrained problem itself.
  Iterating by hand (guess $x_b$, read $\theta$ from the odds, update $x_b$ from
  the B balance) is price coordination. From $\theta_0=0.25$ it gives 0.16856,
  0.17173, 0.17160: each round shrinks the error by a factor of about 0.04 and
  flips its sign, because the 200 boundary sites are small next to the 8000
  bulk sites. Such iterations are not guaranteed to converge in general.
- **D7:** a discrete choice made after continuous minimization: each state is
  minimized first, then the lower one is chosen. "Partly one state, partly the
  other" would be a mixture whose energy, ignoring the walls between domains,
  lies on the straight line between the two states: the chord argument the advanced steps
  builds on.

## What the instructor may and may not infer

The synthetic outputs were checked under the binary and boundary contracts
named in the [source map](source_map.md). Day 2 has not been piloted.
A correct subtraction of two supplied minima checks
interpretation; it does **not** demonstrate that a learner can derive,
implement or validate the solver. Record paper/observed/demo route and
hint use separately. Do not describe model agreement as a human pilot,
Ni–Cu parameter validation, interface coexistence or property
prediction. Next steps for learners are the worked examples, Tasks 00–05
(see the [README](README.md) and the [instructor overview](../instructor_overview.md)).
The [source map](source_map.md) points to deeper work and exact scientific
limits.
