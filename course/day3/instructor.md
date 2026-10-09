# Advanced steps 07–18 — instructor notes (tandem: materials science and operations research)

These notes turn the advanced self-study steps into one in-person day, taught by a
materials instructor and an operations-research instructor together. The day
is the main track of steps 10–17; dive-deeper boxes, notebooks and step 18 stay
self-study. Timings are a draft until a pilot has been run.

## Before the day

- Learners do their preparation step at home: step 07 (from materials science)
  or steps 08 and 09 (from operations research). Ask them to bring the entry-check answers.
- Learners new to linear programmes can do the optional LP primer at home
  (website or the [LP primer sheet](../print/lp_primer_sheet.pdf)).
- Print, per pair: the [picture sheet](../print/day3_picture_sheet.pdf), the
  [card deck](../print/day3_card_deck.pdf) and the
  [column-generation game](../print/day3_game_kit.pdf), plus a transparent
  ruler.
- The labs run from the website without a login; check one step on the
  projector before the session.

## Entry clinic (about 30 minutes, two rooms)

- **Room 1, operations-research learners, led by the materials instructor:** the lowest-G rule
  in a heat bath, a cost curve as a straight line plus a mixing term, the
  common tangent and its end heights, and the Ω bump. Use the Ω-bump lab of
  step 08 on the website.
- **Room 2, materials learners, led by the operations-research instructor:** objective,
  variables and constraints; a menu solved by the lever rule; what a dual is.
  Use the menu builder of step 10.

## Draft running order and leads (no times)

| Block | Steps | Lead | Handover cue |
|---|---|---|---|
| Morning 1 | 10: the hook and the menu | materials | "the computer only knows the dots: what else does it return?" |
| | 11: the line, floor and ceiling | operations research, with a shared moment on μ | the multiplier becomes μA: materials names it, operations research proves it is a floor |
| | 12: the gap curve | duet | driving force (materials), then complementary slackness (operations research) |
| Morning 2 | 13: column generation | operations research | "the curve dips below the line: which state would you add?" |
| | 14: ceiling and floor | operations research, with a materials comment on scale | "is 0.003 J/mol good? compared with what?" |
| Afternoon 1 | 15: local search misses a valley | materials, with operations research on local and global | metastable alloy (materials), nonconvex pricing (operations research) |
| | 16: prune or split, in pairs | operations research | learners decide the eight open rows of the table |
| Afternoon 2 | 17: the joint case, the game, the two questions | materials closes | "did we solve the model?" against "is the model good enough?" |

**Shared duets** (materials voice first, then operations research): the moment the multiplier
becomes μ (step 11), driving force and complementary slackness (step 12), the lever rule
and ranging (step 12), metastability and local against global (step 15).

## Lab protocol

One instructor drives the lab on the projector while the other narrates. Every
reveal starts with a prediction: ask the room to vote (which dot will the line
touch? prune or split?), then show it. The labs read only prepared numbers and
work offline once a step is loaded.

## Deep-dive parking lot

Keep a visible list of questions that belong to dive-deeper boxes. Choose at
most two to answer live; good candidates are the line that can rotate (step
11) and why the chord floor works (step 16). Point everything else to the
dive-deeper boxes and notebooks f4p, f4c–f4e and f4g.

## The column-generation game (about 20 minutes)

Pairs: the master holds the dots, the pricer the full curves. The master
announces a line; the pricer offers a state below it or says "none". Swap
roles after the first answer. Debrief with one question: how did you know
when to stop?

## Where learners get stuck

- **The floor holds only for the menu.** Learners from operations research read the menu's line
  as a bound for the continuous problem. Step 12's gap curve is the fix: show
  the curve dipping below it.
- **Metastable means wrong.** Materials learners object that real alloys are
  metastable. Separate the two: the alloy may be; the calculation that claims
  equilibrium must not return it, unless the restriction is declared.
- **Twin dots are two phases.** Two neighbouring dots of one phase model often
  stand for one phase between them; inside a miscibility gap they can be two
  real compositions. The curve between them decides (card twin dots).
- **Remaining uncertainty is model uncertainty.** It measures how well the
  declared model was solved, nothing more.

## Further reading for instructors

- A. Mitsos and P. I. Barton (2007), a dual extremum principle in
  thermodynamics, AIChE Journal.
- F. E. Pereira, G. Jackson, A. Galindo and C. S. Adjiman (2010), a
  duality-based approach to phase equilibrium, Fluid Phase Equilibria.
- S. R. Tessier, J. F. Brennecke and M. A. Stadtherr (2000), reliable phase
  stability analysis for excess Gibbs energy models, Chemical Engineering
  Science.
- C. M. McDonald and C. A. Floudas (1995), global optimisation for the phase
  and chemical equilibrium problem, Computers and Chemical Engineering.
- C. C. R. S. Rossi, L. Cardozo-Filho and R. Guirardello (2009), Gibbs energy
  minimisation by linear programming, Fluid Phase Equilibria.
- C. Barnhart, E. L. Johnson, G. L. Nemhauser, M. W. P. Savelsbergh and P. H.
  Vance (1998), branch-and-price, Operations Research.
- M. E. Lübbecke and J. Desrosiers (2005), selected topics in column
  generation, Operations Research.
- M. L. Michelsen (1982), the isothermal flash problem, part I: stability,
  Fluid Phase Equilibria (the tangent-plane test).
- R. J. Vanderbei, Linear Programming: Foundations and Extensions, Springer.

Pacing and timetable claims wait for a pilot with learners.
