# Task 01 — Cu–Ni equilibrium and a lightweight magnetic comparison

**Notebook:** [task01_cuni_equilibria](../../../notebooks/task01_cuni_equilibria.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ukerzel/CalphadIntro/blob/v0.2.0/notebooks/task01_cuni_equilibria.ipynb): the same steps with try-first checks; locally `poetry run jupyter lab`.

For detailed download/member/hash and paper-access steps, use the
[source guide](../../sources/README.md). Only open-source software and the
published database are needed.

**First:** the [two-phase sheet](../../primer_day2/two_phase_sheet.md)
(common tangent, lever rule, tie line), or self-study step 03 parts A–C;
about 30 minutes. Optional: notebook f4, sections 1, 3 and 4.

Run Hallstedt's adapted Mey input in **pycalphad 0.11.2 / Python 3.12.14**.
Plot energies, read equilibrium phase amounts, and compare one explicit magnetic
contribution-off variant. This is a compact worked example after either primer.
Physical validity and exact reproduction of the original assessment
are not claimed.

Optional, with the advanced steps 12–13: [task01b_cuni_gap_curve](../../../notebooks/task01b_cuni_gap_curve.ipynb)
reads the gap curve and the driving force from the same database. Its saved numbers
(no-database mode) are [gap_curve.json](gap_curve.json), written by
[gap_curve.py](gap_curve.py) (`python -m course.materials.cuni.gap_curve --tdb …`).

Continue with [Task 02 — fit two isothermal FCC interaction values](fitting.md)
for a compact published-activity exercise using the same learner-fetched input.

## Where the inputs came from

| Item | Source and identity | Course use |
|---|---|---|
| Original assessment paper | S. an Mey, “Thermodynamic re-evaluation of the Cu–Ni system,” *Calphad* 16 (1992), 255–260. [DOI](https://doi.org/10.1016/0364-5916(92)90022-P). Inspected PDF: 408,129 bytes, SHA-256 `ef4ab2a3aaac46baf37cdbec302d36b924a23d89dbb29c5cfdf7ff5cff8b7542`. | Fig. 1, printed p.256 / PDF p.2: liquidus/solidus. Fig. 7, printed p.259 / PDF p.5: miscibility gap. Table 2, printed p.257 / PDF p.3: selected chemical coefficients. Link the paper; its text, page images and figures are not redistributed here. |
| Evaluated TDB | [Direct CuNi-92Mey-LB.tdb download](https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb), [listing and collection plot](https://phasediagrams.org/phase-diagram/CuNi-92Mey-LB.tdb). 6,789 bytes, SHA-256 `7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1`. The script checks this identity. | External, unchanged calculation input. This is Hallstedt's adaptation of Mey's assessment; it is not known to be byte-identical to Mey's original file. |
| Publisher provenance | B. Hallstedt, “The SGTE collection of binary datasets,” *Calphad* 89 (2025), 102833. [DOI](https://doi.org/10.1016/j.calphad.2025.102833), [institutional article](https://publications.rwth-aachen.de/record/1011611/files/1011611.pdf), [original supplement ZIP](https://ars.els-cdn.com/content/image/1-s2.0-S0364591625000367-mmc3.zip). Member `datasets/datasets/CuNi-92Mey-LB.tdb` matches the direct download. | Source attribution and learner-fetch route. The archive and complete TDB are not shipped. |

Fetch the exact TDB yourself, or extract
that member from the publisher supplement; keep a local copy without editing it.

### The relevant numerical excerpt included here

[mey1992_binary_parameters.csv](mey1992_binary_parameters.csv) is an independently
formatted transcription of **four numerical chemical-interaction rows** from
Mey's Table 2. It records phase, Redlich–Kister order, coefficient units and
source page. The coefficient meaning is $L_\nu(T)=a_\nu+b_\nu T$, with the
composition convention $(x_{Cu}-x_{Ni})^\nu$ in the excess term. These are
fitted mathematical coefficients, not independent experimental observations.
No scan, publisher caption or table layout is reproduced, and the CSV is not
used to reconstruct or replace the database.

Underlying facts and mathematical concepts are distinct from copyright in
expression or a compilation's arrangement; see [WIPO's explanation](https://www.wipo.int/copyright/en/).
This selected factual transcription does not assert unrestricted reuse of every
table, database, figure or paper. Hallstedt's article prints CC BY, and
[Elsevier's policy](https://www.elsevier.support/publishing/answer/which-license-should-i-select-when-posting-my-research-data)
connects open-access supplements to the article licence. Whether that licence
also covers the unary data embedded in the complete TDB is unclear, so the
course does not redistribute the TDB: learners fetch it themselves. This
question does not affect running the calculation locally or the small
numerical excerpt above.

**Observed difference:** printed Mey Table 2 gives liquid order-zero
$b_0=1.29093$ J/(mol K); the hash-pinned TDB uses **1.29893**. Its FCC binary
magnetic-moment coefficients also differ slightly from those printed in that
table. No value is silently corrected or declared erroneous. The paper-data CSV
preserves the printed values; the calculation preserves the supplied TDB.
This is a difference between the two sources; you do not need to resolve it.

## Run and quantities

From the repository root, using the locked course environment ([setup](../../setup.md)):

```bash
mkdir -p /tmp/cuni-mpl
export MPLCONFIGDIR=/tmp/cuni-mpl MPLBACKEND=Agg
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
(ulimit -v 4194304; timeout 600 .venv/bin/python course/materials/cuni/worked_example.py --tdb /absolute/path/to/CuNi-92Mey-LB.tdb --output /tmp/cuni-output)
```

The Linux command limits address space to 4 GiB and elapsed time to 10 minutes,
with one numerical process and one BLAS/OMP thread. No network fetch occurs.
Outputs: [phase diagram](phase_diagram.png), [energies/magnetism](energy_magnetism.png)
and [numeric results](results.json), together below 20 MiB. Source hash is checked
before and after evaluation.

Grid: **300–1900 K, 81 points (20 K spacing)**; bulk **x(Ni)=0.005–0.995,
61 points**; **101325 Pa**, **one mole of real atoms**, `pdens=60`.
The figure caption does not specify pressure; this is the lesson's convention.
This stays within the relevant function ranges and does not use the 6000 K file
header as a physical extrapolation licence. LIQUID, FCC_A1, BCC_A2 and HCP_A3
are all enabled in both modes. Metastable-extension terms are not removed.

`GM` is J/mol real atoms; `NP` is the phase amount fraction on that atom-mole
basis; phase `X(NI)` is composition. The metal site contributes one real atom;
the fixed VA sublattice in FCC does not add another atom. The amount divisor is
one for FCC and liquid. Do not divide FCC `GM` by two merely because two
sublattices are written in the file. Energies use the source reference basis;
SER does not imply that Gibbs energy vanishes at 298.15 K.

`MagneticOffModel` overrides only `magnetic_energy` during model assembly.
Chemical references, ideal/excess terms, grid and phase list stay fixed, and
no source parameter is edited. It is a computational illustration, not a newly
assessed nonmagnetic alloy. Total Gibbs energy already includes the magnetic
term; adding it again would double-count it. Transition temperature and magnetic
moment introduce temperature/composition dependence. The pure FCC Ni panel marks
the source Curie temperature, without deriving its magnetic branch function.
Effects can occur above the Curie temperature too; the contribution is not a
simple switch set to zero there.

## Short exercise

1. Read the local TDB's pure liquid Cu branch containing 1500 K. Evaluate it
   with a calculator and compare with `energy_checks` in the JSON. The branch
   expression remains in your fetched file; it is not copied here.
2. Inspect the 600 K, x(Ni)=0.5 sample in both modes. Why can two vertices
   both be called FCC_A1? Reconstruct the bulk composition from amounts and
   phase compositions. Does switching magnetism off eliminate demixing?
3. Read `FCC_liquid_example`, the first sampled temperature at x(Ni)=0.5
   with both phases present, and apply the lever-rule balance. Compare the
   single-phase samples at 1500 and 1600 K. Interpret the energy curves at 1600 K using their
   common reference basis; their minimum at a different composition is not a
   reason to violate your fixed bulk composition.
4. Compare the magnetic-on diagram against Mey Fig. 1 and Fig. 7. Which broad
   features match? Explain why two highest sampled demixing temperatures cannot
   measure an exact magnetic shift of the critical temperature.
5. Read the CSV's four coefficient rows and source note. Does agreement with
   these fitted coefficients constitute independent physical validation? Why
   must the paper's and adapted TDB's distinct numbers retain separate labels?

[Answers and observed comparison](answers.md) report the actual run. Fixed
criteria: hand/magnetic-control/normalization checks use absolute **1e-8 J/mol**
and relative **1e-12** tolerances; amount/component balances use absolute
**1e-6**. Pure liquid endpoint energies must be finite; inspect near-pure phase
sets without calling them exact melting-point tests.

The scatter shows sampled equilibrium phase compositions, including single-phase
fields, rather than exact smooth boundary traces. Grid/sampling, source adaptations,
magnetic edge cases, regularization, extrapolation and gas-constant conventions
limit reproduction. The critical point is not refined here (notebook task01b
refines the top of the FCC gap to about 642 K), and no second solver
is used for comparison. This evaluates one database in one pinned
implementation; it does not validate physics or show equivalence with Mey's
original files or other software.
