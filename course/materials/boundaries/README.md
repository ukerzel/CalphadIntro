# Tasks 03/04 — boundary energy and segregation

**Notebooks:** [task03_ni_twin](../../../notebooks/task03_ni_twin.ipynb), [task04_cuni_segregation](../../../notebooks/task04_cuni_segregation.ipynb), and for the invented A/B exercises [f7_boundary_open_closed](../../../notebooks/f7_boundary_open_closed.ipynb) and [f8_boundary_states](../../../notebooks/f8_boundary_states.ipynb) ([crosswalk with Colab links](../../../notebooks/README.md)).

Use this compact route after the primers, or select the exercises you need.
It offers the published Ni twin curve, a public Cu–Ni bulk/invented-boundary
example, and the simpler **invented A/B** paper exercises of the Day 2 primer. Each input
role is explicit; no synthetic parameter is relabelled as measured material data.
The detailed lessons are optional; physical Cu–Ni boundary calibration is not
part of these examples.

## Task 03: read boundary energy and count the interface

The [runnable Ni coherent-twin exercise](ni_twin.md) supplies eight
readings digitized for this course from Fischer et al. (2019), Figure 3, a linear fit,
shared-face/two-plane normalization and one-mole Ni energy accounting. These
are samples of an integrated EAM simulation curve, with graphical reading
precision. The bulk/site construction
is explicitly illustrative. The simpler literature/count exercises follow.

1. For a literature-reading exercise, open Haremski et al.,
   [*Acta Materialia* 214 (2021), 116936, institutional paper](https://publikationen.bibliothek.kit.edu/1000134531/119247470).
   Read Fig. 1's caption and Table 1: distinguish a mean boundary energy,
   surface energy and their dimensionless ratio. Which experimental conditions
   differ across the literature points? Explain why such a compilation is not
   a temperature curve for one fully specified boundary.
2. Work **D4** of the [day-2 worksheet](../../primer_day2/worksheet.md), keeping
   its reference sheet visible. Count both boundaries, their sites and areas;
   distinguish occupancy from excess. Check both component counts and convert
   excess from atoms/nm² to mol/m². Read the matching **D4 answers** in the
   [answer sheet](../../primer_day2/answers.md) only after trying it.
3. For an optional state-energy illustration, work **D7** and its matching
   answers. Compare the two invented uniform states within each inventory row,
   include the baseline term and use the same amount normalization. A change
   of the lower-energy state is encoded by these supplied functions; it does
   not demonstrate a transition in Ni. D7 supplies selected model results,
   rather than asking you to reproduce a new optimizer.

For detail, use [Lesson 11 geometry](../../foundations/lesson_11_geometry.md)
and [Lesson 14 competing states](../../foundations/lesson_14_competing_states.md).
A site-molar energy becomes a total energy only after multiplying by the number
of moles of those sites. Energy per interface area additionally requires the
correct total area and a declared bulk/reference subtraction. An arbitrary
boundary-site function is not an absolute measured grain-boundary energy.

**Source curve:** Fischer et al.
[2019](https://doi.org/10.1016/j.actamat.2019.06.027). Figure 3's pure-Ni
coherent Σ3 {111} formation-energy branch is the factual numerical excerpt;
its rounded samples were read from the published figure for this course.
Haremski's compilation remains separate reading context. No source figure or
paper is redistributed; no physical boundary phase assessment is claimed.

## Task 04: enrichment with an open or finite bulk

The [runnable Cu–Ni example](segregation.md) couples the published FCC bulk
to an independently invented one-state boundary preference. It supplies code,
outputs and short exercises. Boundary preference,
capacity and site density are explicitly illustrative. No physical boundary
calibration or atomistic calculation is needed for this instructional mechanism.
The following A/B paper exercises remain a simpler option.

1. Work **D5** of the same worksheet: obtain the boundary occupancy from the
   supplied preference and reservoir composition. Convert it to the declared
   equal-site excess. Identify which component leaves when another arrives.
2. Work **D6**: close the cell, conserve both A and B, and allow the bulk
   composition to change. Check the supplied selected pair's component balance;
   explain why retaining the open reservoir composition changes the problem.
3. Check the matching **D5/D6 answers**. As a final check, set the preference
   to zero in D5: the boundary fraction equals the bulk fraction and this
   equal-site excess vanishes. The preference is an invented teaching input,
   not measured Cu–Ni segregation.

Optional depth: [Lesson 12 open reservoir](../../foundations/lesson_12_reservoir.md)
and [Lesson 13 finite inventory](../../foundations/lesson_13_finite_reservoir.md).
D7 may extend the comparison, but discovering competing physical boundary
states is not part of this introductory exercise.

**Not included:** a numerical Cu–Ni segregation curve tied
to a specified boundary, composition/excess convention and compatible bulk
model is absent. Fischer and Eich [2020](https://doi.org/10.1016/j.actamat.2020.09.039)
is a reading lead. The runnable packet supplies public bulk
thermodynamics and an explicitly
invented boundary; it does not fill this physical-calibration gap. The simpler
A/B bulk/preference remain synthetic. Do not relabel those as measured Cu/Ni
or fit missing physical observations.

## Delivery and checks

The D4–D7 route consists of paper/calculator exercises using the prepared
worksheet/answers. The runnable Task 03/04 examples use the same external
Cu–Ni database as Task 01, each with its own numerical checks.
No further database, source search or atomistic simulation is needed.

A successful learner answer keeps fractions, atom counts, moles and area units
separate; checks both components; uses one inventory for a state comparison;
and distinguishes the synthetic calculation from the cited observations.
Use only D4–D6 for the core route; D7 and detailed lessons are optional.
