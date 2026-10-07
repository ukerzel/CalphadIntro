# CALPHAD self-study companion

A static web companion to the introductory CALPHAD course: seven short steps
(00–06) from the energy refresher to the published Cu–Ni and Ni–Nb databases,
each with an attempt-first task, hints, a worked answer and an interactive lab.
The course repository owns the science and the text; this directory only
presents them. `npm run build` copies the narration and the exported lab data
from `course/` into `public/`, and the static export in `dist/client` is what
gets served. Nothing is edited on the hosting side.

## Running it

Node 22.13 or newer (Node 24 works). Keep `package-lock.json`.

```bash
cd site
npm ci                 # or: npm run install:ci
npm run dev            # local development server with hot reload
npm test               # node --test over tests/*.test.mjs
npm run typecheck      # tsc --noEmit
npm run build          # sync-content, then a static export to dist/client
```

After editing the narration, run `npm run sync-content` (or let `npm run build`
do it); `node scripts/sync-content.mjs --check` is read-only and fails if
`public/learning` is stale or holds extra files. No Python environment is
needed for narration changes.

## Where the content comes from

**Narration.** `course/self_study/lessons.json` holds the original learner text
(see [its README](../course/self_study/README.md)). `scripts/sync-content.mjs`
uses Node built-ins and KaTeX and validates it before copying:

- four block types (paragraph, list, table, reveal; reveals do not nest);
- marked terms `{{id|shown}}`, whose ids must exist in the glossary;
- formulas `$TeX$`, each parsed by KaTeX in strict mode, so a broken formula
  fails the build;
- cross-references `[[target|text]]` to a step, a stage (`step#stage-key`), a
  lab view (`step/lab/view`) or a glossary row (`glossary#row`); malformed
  targets are rejected at sync and the tests resolve every one;
- links and images only to an allowlist of course outputs: the Cu–Ni and Ni–Nb
  phase-diagram figures, the Cu–Ni energy/magnetism figure and the
  `results.json` files from `course/materials/`, and
  the generated `two_phase`, `from_scratch`, `boundary_views`, `cuni_grid`,
  `ninb_grid` and `mu_structure` JSON files from `course/self_study/generated/`.

It then writes the narration and those assets to `public/learning/` with
`content_receipt.json`, which lists each canonical path and its SHA-256. The
material explorers check that receipt before displaying a file.

The generated JSON files come from scripts in `course/self_study/`:
`two_phase_export.py` (the invented ideal melting lens of step 03 part C),
`from_scratch_export.py` (step 03 part D: that lens at 1400 K solved four ways
from scratch, frame by frame, and by pycalphad from a ten-line database in the
script, as in notebook f4b),
`boundary_export.py` (the step 04 tangent picture and δ iteration),
`grid_export.py` (the clickable Cu–Ni and Ni–Nb phase maps; it needs the
databases each learner fetches, and only the calculated grids are committed)
and `mu_structure.py` (the μ-phase sketch: Fe₇W₆ prototype geometry from the
AFLOW library; only the 18h and 3a sites are matched to database sublattices,
by count). No TDB file, publisher figure or private file is copied.

**Lab data.** `public/data/` holds the unary, binary and boundary lab exports
of the invented teaching models, calculated in advance.
In the browser, the loader checks
receipt version, schema and payload hashes, finite numeric fields and ordered
record IDs; a failure shows a visible error, with no fallback values.

The browser never evaluates a thermodynamic model: readouts select exported
record IDs, and the page only maps numbers to pixels and formats them.

## Structure

One static page with hash routes, so every state can be linked:

- `#/` landing page; `#/<step>` a step; `#/<step>/at/<anchor>` a place in it;
  `#/<step>/lab` and `#/<step>/lab/<view>` a lab; `#/<step>/lab/<record ID>` an
  exact exported row (for example `#/unary/lab/unary-125`). Step IDs: `start`,
  `unary`, `binary`, `twophase`, `boundary`, `cuni`, `ninb`. Old `#<step>` links
  still open the step. Routing is in `lib/route.ts`.
- **Landing** (`components/home.tsx`, `hero-graphic.tsx`): a hero that steps
  through exported unary rows, the route of steps, the attempt-first method,
  lab previews and the limitations panel. “Continue” remembers the last step in
  `localStorage`.
- **Steps** (`components/learning-page.tsx`, `lib/learning.ts`,
  `lib/lesson-meta.ts`): the narration's own “Label · ” prefixes become stage
  headings, and a test checks that every block is restored exactly. Hints and
  worked answers stay closed native `<details>` elements in a help sequence.
  Marked terms open popovers (`components/term.tsx`); cross-references show a
  preview and a “Back to …” chip (`components/xref.tsx`, `lib/xref.ts`).
  Inline figures (`components/lesson-figures.tsx`, `calphad-figures.tsx`,
  `energy-ladder.tsx`, `constraints-figure.tsx`, `mu-structure.tsx`) reuse the
  labs' exported files. Every step stays open; there is no grading.
- **Labs** (`components/{unary,binary,twophase,boundary}-view.tsx`, `scratch-view.tsx`,
  `boundary-views.tsx`, `phase-map.tsx`): Explore / Model / Data tabs; drag on
  a chart, use the keyboard slider or play a sweep through exported rows; the
  Data tab shows the selected row verbatim. Lab views are listed in
  `lib/lesson-meta.ts` (`labViews`). Charts are original SVG
  (`components/plot.tsx`) sized to their container. Model-tab equations are
  rendered by `components/math.tsx` (KaTeX HTML plus MathML), and a test parses
  every one.
- **Material explorers** (`components/material-explorer.tsx`,
  `lib/materials.ts`): saved Cu–Ni and Ni–Nb outputs, hash-checked against the
  content receipt; the page displays them without recalculating anything.
- **Reference sheet** (`components/reference-drawer.tsx`): energies and terms,
  available from every step. “About this data” (`components/source-drawer.tsx`)
  lists the code and notes that produced each lab.
- **Ask ChatGPT** (`lib/tutor.ts`, `components/ask-chatgpt.tsx`): each step's
  help box links to ChatGPT in a new tab with the task and tutor rules filled
  in, using the learner's own account; no key is held on the course side.
  Prompts carry the task, never the hints or worked answer. A course tutor on an
  OpenAI-compatible API is prepared in `lib/tutor.ts` but not switched on.
- **WebMCP** (`lib/webmcp.ts`): an optional `select_exported_row` tool changes
  the same tab and row state as the UI; it never calculates.
- Light and dark themes (stored choice, else the system setting), reduced
  motion, a skip link, and focus moved to the new heading or opened lab on
  navigation. `RecordSlider` composes the Radix slider directly so the thumb
  carries an accessible name and value text.

Fonts are self-hosted OFL subsets ([public/fonts/README.md](public/fonts/README.md));
KaTeX (MIT) CSS and fonts are bundled into the site's own assets. The page
itself makes no third-party requests.

## Tests

`tests/` holds Node tests for the data loader and balance checks (`data`),
the narration and its sync (`learning`), server-rendered markup with a check
that learner-facing text carries no worksheet codes or internal jargon
(`render`), routes, cross-references and receipt-checked loading (`ui`), and
the WebMCP registry against a mock (`webmcp`). They run on the actual synced
assets. They do not cover layout, mobile or keyboard
behaviour in a real browser, nor a live WebMCP context. Nothing has been timed
with learners yet.

## Starter scaffolding

The site is built on a Vinext static-export starter. These parts belong to the
starter and are kept unchanged: `build/`, `db/`, `drizzle/`, `hooks/`,
`vendor/`, `components/ui/`, `lib/connector*`, `examples/`, `app/chatgpt-auth.ts`,
`scripts/` (except `sync-content.mjs`), `.npmrc`,
`components.json`, `cloudflare-env.d.ts`, `drizzle.config.ts`,
`eslint.config.mjs`, `postcss.config.mjs`, `vite.config.ts`, `next.config.ts`,
`tsconfig.json` and `.openai/hosting.json` (static output to `dist/client`).
No storage, authentication or connector flow is switched on.
