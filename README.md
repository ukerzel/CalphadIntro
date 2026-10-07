# CalphadIntro — an introduction to CALPHAD with open tools

Teaching material for a short introduction to CALPHAD (CALculation of PHAse
Diagrams) with open-source software ([pycalphad](https://pycalphad.org)) and
published thermodynamic databases.

- **Two one-day primers**, paper first: unary and binary Gibbs energies,
  chemical potentials, common tangents, phase diagrams and grain-boundary
  segregation.
- **Six worked examples** (Tasks 00–05): tools check, Cu–Ni equilibria, Cu–Ni
  activity fitting, Ni twin boundaries, Cu–Ni segregation and Ni–Nb ordered
  phases.
- **Notebooks** for every task and the computational lessons; they run locally
  or in Google Colab.
- **A self-study website** (steps 00–06) that walks through the same ideas with
  interactive labs.
- An optional **lesson library** for learners who want more depth.

## Where to start

| You are | Start with |
|---|---|
| A learner in a course | [Course index](course/README.md), then [primer day 1](course/primer/README.md) |
| A learner on your own | [Notebooks](notebooks/README.md) (Colab links in the table) or the self-study site (`site/`) |
| An instructor | [Instructor overview](course/instructor_overview.md) |

## Setup

Python 3.12 and [Poetry](https://python-poetry.org/docs/#installation) 2.x:

```bash
poetry install
poetry run jupyter lab        # then open notebooks/setup_check.ipynb
```

Details: [setup notes](course/setup.md). In Colab, the first cell of each
notebook downloads this release and installs the tested package versions.

## Published databases

The Cu–Ni and Ni–Nb databases used in Tasks 01–05 are **not** included. The
notebooks download them from the publishers' pages and check their size and
SHA-256; without them the task notebooks still run from saved results. Sources
and citations: [course/sources/README.md](course/sources/README.md). The two
small databases in `course/foundations/` are invented teaching models.

## Tests and the site

```bash
poetry run pytest                      # course code and notebooks
cd site && npm ci && npm test          # self-study site
npm run build                          # static site in site/dist/client
```

See [site/README.md](site/README.md).

## Licence

Apache License 2.0, see [LICENSE](LICENSE). The included article
`course/sources/hallstedt2025.pdf` keeps its own CC BY 4.0 licence (attribution
in [course/sources/README.md](course/sources/README.md)); the site's fonts are
under the SIL Open Font License (`site/public/fonts/`).

Each version of this repository is a tagged release (v0.1.0, v0.2.0, …).
