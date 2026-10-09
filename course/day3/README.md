# Advanced steps 07–18 — from materials science to operations research and back

Steps 00–06 find equilibria by hand and then read real alloys: a sample at
fixed temperature and pressure lowers its Gibbs energy, splits by the lever
rule, and its chemical potentials are the end heights of a tangent. The
advanced steps ask how a program finds that answer when it can only try a
list of candidate states, and how it can know that nothing lower is left.
The calculation is read twice: once as thermodynamics, once as an
optimisation problem (a linear programme, its prices, column generation and
branch-and-bound).

The advanced steps are optional. There are two starting points:

- **Know CALPHAD from materials science, or followed steps 00–06?** Start at
  step 07. First-semester calculus is enough.
- **Know methods from operations research** (linear programming, duality,
  branch-and-bound), but no thermodynamics? Start at step 08.

Both lead into the same steps 10–18. Never met a linear programme? The
optional **LP primer**, after step 07 and before step 10, starts from scratch: a
melt-shop charge as dots and chords, how a solver searches, its prices, and
the textbook picture (about an hour, with a lab, notebook
[f4p](../../notebooks/f4p_lp_primer.ipynb) and a [paper sheet](lp_primer_sheet.md)). Instructors teaching them in person as
one day, with a materials and an operations-research instructor: see the
[instructor notes](instructor.md).

## Steps

| Step | Content | Who |
|---|---|---|
| 07 | From materials science: two phases, one phase model with two phases, metastability, and a menu by hand | from materials science |
| 08 | From operations research: energy, phases and cost curves | from operations research |
| 09 | Prices and metastability: temperature, chemical potential and CALPHAD; self-check | from operations research |
| LP | Optional LP primer: the cheapest mix, and how to prove it | anyone new to linear programmes |
| 10 | Menu: equilibrium as the cheapest mixture of listed states | everyone |
| 11 | Price line: floor, ceiling and chemical potentials | everyone |
| 12 | Gap curve: how far each state lies above or below the line; moving the composition | everyone |
| 13 | Column generation: find a missing state | everyone |
| 14 | Bounds: ceiling, floor and the remaining uncertainty | everyone |
| 15 | Global search: a local search can miss a valley; keep pricing | everyone |
| 16 | Branch-and-bound: check that no valley is left | everyone |
| 17 | Solved and good enough: the solver versus the model | everyone |
| 18 | Three components | optional |

Steps 10–14 use **the melting lens** of step 03 part C (1400 K, overall B
fraction 0.40). Steps 15–17 use **the regular solution** of step 03 part B
(800 K, overall B fraction 0.15). Both models are invented; their two B
components are different elements.

## What "finished" means

- *Prepare:* step 07, or steps 08–09, or pass that step's entry check.
- *Do:* the main track of steps 10–17.
- *Show:* the check questions of the six outcomes below.
- *Not needed to finish:* dive-deeper boxes, boxes marked for one
  background, notebooks, step 18.

The six outcomes:

1. Set up a small menu of states and find the cheapest mixture with the
   lever rule.
2. Read μA and Δμ from a line, and say why the line is a floor for its menu.
3. Read a gap curve: decide which states are used and which should be added.
4. State a ceiling, a floor and the remaining uncertainty, and why the line
   from a grid is not a floor for the whole curve.
5. Tell a local answer from a global one in the regular solution, and say
   what a floating-point teaching check of "no valley left" shows and does
   not show.
6. Separate "Did we solve the model?" from "Is the model good enough?".

## Time (estimates, not yet measured with learners)

| | From materials science | From operations research |
|---|---|---|
| Preparation | step 07, about 100 minutes | steps 08 and 09, about 150 minutes |
| Steps 10–17 | about 30–40 minutes each | a summary of steps 10–12 after the self-check in step 09, then steps 12–17 |
| Notebooks | optional | recommended |

Work over several sittings. Every step says what you can skip.

## To print

- [LP primer sheet](lp_primer_sheet.md) ([PDF](../print/lp_primer_sheet.pdf)):
  the optional primer on paper, with answers; invented prices.
- [Picture sheet](picture_sheet.md) ([PDF](../print/day3_picture_sheet.pdf)):
  the menu and its line, the gap curve, ceiling and floor, and the interval
  bars on one page.
- [Card deck](card_deck.md) ([PDF](../print/day3_card_deck.pdf)): every side
  card, to cut out.
- [Column-generation game](game_kit.md) ([PDF](../print/day3_game_kit.pdf)):
  a master's sheet of dots and a pricer's sheet of curves, for two players.

## What the advanced steps do not tell you

The models are invented and validated for nothing. A small remaining
uncertainty says the declared model was solved well, not that the model
describes a material. No unknown phase is found by any of these methods,
a small energy difference does not guarantee the compositions, and
interfaces and kinetics need their own descriptions.
