/** Presentation metadata and stage grouping for the finite narration. No science. */
import { COLAB_REPO } from './data';
import { plainText } from './learning';
import type { Block, Lesson, LearningID } from './learning';

export type LabKind = 'potentials' | 'unary' | 'binary' | 'twophase' | 'boundary' | 'cuni' | 'ninb' | 'day3-line' | 'day3-cg' | 'day3-regular' | 'day3-prework' | 'day3-ternary' | 'lp-primer';
export type Meta = { number: string; group: string; tag: string; lab: LabKind | null; labTitle: string | null; labLine: string | null };

/** Pager exceptions to the flat route order: the materials entry (07) and the OR entry (08–09) both lead to step 10,
 *  and the optional LP primer sits beside them. Unlisted pages go back to the page before them in the route. */
export const pagerPrevious: Partial<Record<LearningID, LearningID[]>> = {
  'from-or': ['ninb'], 'lp-primer': ['from-materials', 'or-prices'], menu: ['from-materials', 'or-prices'],
};
/** An optional detour offered beside "Next": from step 07 to the LP primer, for readers new to linear programmes. */
export const pagerDetour: Partial<Record<LearningID, [LearningID, string]>> = {
  'from-materials': ['lp-primer', 'New to linear programmes? Optional first'],
};

/** Steps 07–18: the advanced steps, tagged "Advanced" and set on a tinted card; same numbering as the rest. */
export const ADVANCED = 'Advanced';
export const isAdvanced = (id: LearningID) => meta[id].group === ADVANCED;
/** The optional linear-programming primer: an unnumbered page in the advanced part, before step 10. */
export const PRIMER: LearningID = 'lp-primer';
export const isPrimer = (id: LearningID) => id === PRIMER;
/** Pages no other page needs: the LP primer and step 18. Marked "Optional" everywhere they appear. */
export const isOptional = (id: LearningID) => id === PRIMER || id === 'three-components';
/** "Step 03"; lower-case for running text ("step 03"). The primer is "LP primer" ("the LP primer"). */
export const pageLabel = (id: LearningID, lower = false) => isPrimer(id) ? `${lower ? 'the ' : ''}LP primer` : `${lower ? 'step' : 'Step'} ${meta[id].number}`;

export const meta: Record<LearningID, Meta> = {
  start: { number: '00', group: 'Basics', tag: 'Refresher', lab: 'potentials', labTitle: 'Energy ladder of U, H, F and G', labLine: 'Move T, S, p and V and see which terms matter.' },
  unary: { number: '01', group: 'Basics', tag: 'One component', lab: 'unary', labTitle: 'Gibbs energy against temperature', labLine: 'Drag through the crossing; watch which branch is the minimum.' },
  binary: { number: '02', group: 'Mixtures', tag: 'Two components', lab: 'binary', labTitle: 'Tangent and chemical potentials', labLine: 'Slide along the curve; read μA and μB off the tangent.' },
  twophase: { number: '03', group: 'Mixtures', tag: 'Two phases', lab: 'twophase', labTitle: 'Common tangent and lever rule', labLine: 'Move the overall composition; watch the sample split into two phases.' },
  boundary: { number: '04', group: 'Boundaries', tag: 'Grain boundary', lab: 'boundary', labTitle: 'Open reservoir or closed cell', labLine: 'Count A and B atoms in two different constraints.' },
  cuni: { number: '05', group: 'Real alloys', tag: 'Cu–Ni', lab: 'cuni', labTitle: 'Cu–Ni phase diagram and saved samples', labLine: 'Compare saved magnetic-on and magnetic-off samples.' },
  ninb: { number: '06', group: 'Real alloys', tag: 'Ni–Nb', lab: 'ninb', labTitle: 'Ni–Nb phase diagram and amount bases', labLine: 'See why one division by atoms per formula is enough.' },
  'from-materials': { number: '07', group: ADVANCED, tag: 'Entry from materials science', lab: 'day3-prework', labTitle: 'The Ω bump: stable, metastable, unstable', labLine: 'Raise Ω/RT: the curve bends down, and one line touches it twice.' },
  'from-or': { number: '08', group: ADVANCED, tag: 'Entry from operations research', lab: 'day3-prework', labTitle: 'Energy, entropy and cost curves', labLine: 'The second law, counting arrangements, building g(x) and the Ω bump.' },
  'or-prices': { number: '09', group: ADVANCED, tag: 'Entry from operations research, part 2', lab: 'day3-prework', labTitle: 'The Ω bump: stable, metastable, unstable', labLine: 'Raise Ω/RT and watch the binodal and spinodal appear.' },
  'lp-primer': { number: 'LP', group: ADVANCED, tag: 'Linear programmes', lab: 'lp-primer', labTitle: 'Scrap lots, swaps and corners', labLine: 'Mix scrap lots, watch the search swap them, then slide a cost line across a polygon.' },
  'menu': { number: '10', group: ADVANCED, tag: 'Menu', lab: 'day3-line', labTitle: 'Menu builder', labLine: 'Put dots in a basket; the lever rule mixes them at z = 0.40.' },
  'price-line': { number: '11', group: ADVANCED, tag: 'Price line', lab: 'day3-line', labTitle: 'A line under the dots', labLine: 'Make the line a floor, raise it at z, read μA and μB.' },
  'gap-curve': { number: '12', group: ADVANCED, tag: 'Gap curve', lab: 'day3-line', labTitle: 'Gap curve, moving z and T', labLine: 'Energy minus the line; then move the composition and the temperature.' },
  'column-generation': { number: '13', group: ADVANCED, tag: 'Column generation', lab: 'day3-cg', labTitle: 'Column generation, round by round', labLine: 'Solve the menu, find the deepest dip, add that state: watch the dip shrink.' },
  'bounds': { number: '14', group: ADVANCED, tag: 'Bounds', lab: 'day3-cg', labTitle: 'Ceiling and floor', labLine: 'Slide the line down by the deepest dip; the truth lies between.' },
  'local-global': { number: '15', group: ADVANCED, tag: 'Local or global', lab: 'day3-regular', labTitle: 'Local search and keep pricing', labLine: 'A downhill search from 0.15 stays put; a full scan finds the valley.' },
  'branch-and-bound': { number: '16', group: ADVANCED, tag: 'Branch-and-bound', lab: 'day3-regular', labTitle: 'Branch-and-bound, interval by interval', labLine: 'Prune or split, interval by interval, until no valley can hide.' },
  'two-questions': { number: '17', group: ADVANCED, tag: 'Two questions', lab: 'day3-regular', labTitle: 'Two samples, metastable and unstable', labLine: 'z = 0.15 and z = 0.50: metastable or unstable, and where the drive is largest.' },
  'three-components': { number: '18', group: ADVANCED, tag: 'Three components', lab: 'day3-ternary', labTitle: 'Three components on a triangle', labLine: 'The menu, the plane and the gap landscape on a triangle.' },
};

/** Stages of steps 00–06 that are dive deeper for every goal (collapsed, optional); everything else is main track. */
export const deeperStages: Partial<Record<LearningID, string[]>> = {
  twophase: ['part-d-from-scratch-and-with-pycalphad'],
  boundary: ['where-the-odds-formula-comes-from'],
  cuni: ['source-dependent-extensions'],
  ninb: ['source-dependent-extensions'],
};

/** One line on what the previous step concluded (the route strip's "story so far"). */
export const stepStory: Partial<Record<LearningID, string>> = {
  unary: 'Step 00 set the rule: at fixed temperature and pressure the lowest Gibbs energy wins.',
  binary: 'Step 01 chose between two straight lines for one element; the crossing is the melting point.',
  twophase: 'Step 02 built one curve for a mixture; its tangent gives μA and μB.',
  boundary: 'Step 03 split a sample along a common tangent, by the lever rule.',
  cuni: 'Step 04 compared an open boundary with a closed cell; the invented models end here.',
  ninb: 'Step 05 read a published Cu–Ni database; step 06 adds ordered phases and the formula basis.',
  'from-materials': 'Steps 00–06 are behind you, or you know CALPHAD from materials science. This step reads them as an optimisation problem.',
  'from-or': 'You know linear programming and duality; this step and step 09 supply the thermodynamics. No materials background assumed.',
  'or-prices': 'Step 08 built the cost curves: a straight line plus a mixing term, and the Ω bump.',
  'lp-primer': 'For anyone who has never met a linear programme: read it after step 07 and before step 10 (any time after step 03 works). Readers from operations research can skip it.',
  'menu': 'Step 07, or steps 08 and 09, prepared the common tangent, the lever rule and metastability.',
  'price-line': 'Step 10 found the cheapest mixture of a ten-dot menu, 43.6 J/mol atoms above the truth.',
  'gap-curve': 'Step 11 read the line under the dots: a floor for the menu, with μA and Δμ as its prices.',
  'column-generation': 'Step 12 showed the curves dipping below the line between the dots, deepest near SOLID 0.4489.',
  'bounds': 'Step 13 added missing states until the deepest dip was 0.0027 J/mol atoms.',
  'local-global': 'Step 14 turned the deepest dip into a floor: ceiling and floor now bracket the truth.',
  'branch-and-bound': 'Step 15 showed a local search missing a valley, and kept pricing until the split appeared.',
  'two-questions': 'Step 16 checked that no state lies more than 1 J/mol atoms below the final line.',
  'three-components': 'Steps 10–17 are done; this step adds a third component.',
};

/** Advanced steps: main-track minutes (estimates, untested), shown in the route strip. */
export const advancedMinutes: Partial<Record<LearningID, string>> = {
  'from-materials': 'about 100', 'from-or': 'about 75', 'or-prices': 'about 75', 'lp-primer': 'about 60', 'menu': '30–40', 'price-line': '30–40', 'gap-curve': '30–40',
  'column-generation': '30–40', 'bounds': '30–40', 'local-global': '30–40', 'branch-and-bound': '30–40', 'two-questions': '30–40', 'three-components': 'about 40',
};

/** What each lab contains, in order: [view id, short label, one line]. A view id opens the lab there (#/<lesson>/lab/<view>). */
export const labViews: Partial<Record<LearningID, [string, string, string][]>> = {
  start: [['ladder', 'Energy ladder', 'U, H, F and G as bars you change with T, S, p and V.'], ['second-law', 'Second law', 'Melt part of a sample in a heat bath: total entropy up exactly when G falls.']],
  unary: [['crossing', 'Solid and liquid g(T)', 'Drag through the melting crossing.'], ['fractions', 'Phase-fraction line', 'g_mix against the liquid fraction at one T.']],
  binary: [['tangent', 'Curve, tangent and μ', 'The tangent at x and where it meets x = 0 and x = 1.'], ['slope', 'Exchange slope', 'μB − μA and where its sign changes.'], ['counter', 'Count arrangements', 'k B atoms on N sites: where the mixing bonus comes from.']],
  twophase: [['part-a', 'Part A · two different phases', 'Common tangent, split band and lever arms.'], ['part-b', 'Part B · one phase model, two phases', 'The regular-solution gap and its T–x diagram.'], ['part-c', 'Part C · melting and the lens', 'Solid and liquid curves and the lens they draw.'], ['part-d', 'Part D · from scratch and pycalphad', 'Four ways to the same equilibrium, side by side with pycalphad.'], ['stability', 'The Ω bump: stable, metastable, unstable', 'Raise Ω/RT: the binodal, the spinodal and the bands between them.']],
  boundary: [['cells', 'Open and closed cells', 'Occupancy, atom ledgers and where the B atoms go.'], ['tangent', 'Tangent picture · δ slider', 'Bulk curve, reservoir tangent and φ as a vertical gap.'], ['iteration', 'Closed cell by hand', 'The hand iteration, round by round.'], ['match', 'Which reservoir matches?', 'Find the reservoir at which the open boundary holds what the closed cell holds.']],
  cuni: [['map', 'Clickable Cu–Ni phase diagram', 'Click any T and x: phases, amounts, tie line; play a cooling path.'], ['samples', 'Saved samples at x(Ni) = 0.5', 'Magnetic on and off at 600, 1500, 1540 and 1600 K.']],
  'from-materials': [['omega', 'The Ω bump', 'Raise Ω/RT: binodal, spinodal and the bands between them.']],
  'from-or': [['second-law', 'Second law', 'Melt part of a sample in a heat bath: total entropy up exactly when G falls.'], ['counter', 'Count arrangements', 'k B atoms on N sites: ln W / N approaches the mixing entropy.'], ['builder', 'Build g(x)', 'End line plus mixing term, at any temperature.'], ['omega', 'The Ω bump', 'Raise Ω/RT until the curve stops being convex.']],
  'or-prices': [['omega', 'The Ω bump', 'Binodal, spinodal and the bands between them.']],
  'lp-primer': [['chords', 'Dots and chords', 'Put scrap lots in a basket; the lever rule mixes them to 0.40 Ni.'], ['swap', 'One swap at a time', 'The search: a line through the used pair, the lot furthest below comes in.'], ['nudge', 'Move the target', 'Best cost against the target content; its slope is the price.'], ['polygon', 'The textbook picture', 'Two amounts on the axes, four rules, a cost line that slides to a corner.']],
  'menu': [['menu', 'Menu builder', 'Tap dots into a basket; the lever rule mixes them at z = 0.40.']],
  'price-line': [['line', 'A line under the dots', 'Make it a floor, raise it at z, then let the lab lift and turn it.']],
  'gap-curve': [['gap', 'Gap curve', 'Energy minus the line; the curves dip below it between the dots.'], ['move-z', 'Move z', 'The line stays while z lies between the used dots.'], ['temperature', 'Move T', 'The curves move and trace the lens.']],
  'column-generation': [['player', 'Iteration player', 'Solve the menu, find the deepest dip, add that state, round by round.']],
  'bounds': [['bounds', 'Ceiling and floor', 'Slide the line down; ceiling, floor and truth on one number line.'], ['spacing', 'Finer menus', 'Evenly spaced menus from 0.2 down to 0.002.']],
  'local-global': [['local', 'Local search', 'Downhill searches from several starts, and a full scan.'], ['pricing', 'Keep pricing', 'Round by round, with the solver\'s and the chosen lines labelled.']],
  'branch-and-bound': [['bnb', 'Interval player', 'Prune or split; the check against the final line, a search run, and a run stopped early.']],
  'three-components': [['triangle', 'Menu and plane', 'The menu on a triangle, its tie triangle and the plane.'], ['landscape', 'Landscape', 'The gap of each phase model over the triangle, round by round.'], ['harder', 'What gets harder', 'A hidden valley in a liquid with an A–C interaction.']],
  'two-questions': [['joint', 'Joint case', 'Gap curves at z = 0.15 and z = 0.50 with stability bands.']],
  ninb: [['map', 'Clickable Ni–Nb phase diagram', 'Click any T and x; amounts in mol atoms or formula units.'], ['formula', 'One division, on the right basis', 'Formula energies divided by atoms per formula.'], ['sites', 'Build a formula unit', 'δ and μ site boxes you fill with Ni or Nb.'], ['mu-structure', 'Where the μ-phase atoms sit', 'A crystal sketch linked to the site boxes.']],
};

/** Course notebooks (notebooks/<file>.ipynb) to run after the attempt; RELEASE must match the notebooks' setup cell. */
export const NOTEBOOK_RELEASE = 'v0.2.1';
export const notebooks: Partial<Record<LearningID, [string, string][]>> = {
  start: [['f0_jupyter_and_potentials', 'Potentials: U, H, F and G']],
  unary: [['f1_unary_by_hand_and_code', 'One component, two phases: by hand and in code'], ['f2_unary_pycalphad', 'Optional: the same model in pycalphad']],
  binary: [['f3_binary_mixing_potentials', 'Binary mixtures: ideal mixing and chemical potentials']],
  twophase: [['f4_two_phases_and_diagrams', 'Two phases: common tangent, lever rule and phase diagrams'], ['f4b_lens_from_scratch', 'Optional: one melting lens from scratch in numpy/SciPy, then pycalphad']],
  boundary: [['f7_boundary_open_closed', 'A grain boundary in an open or closed cell'], ['f8_boundary_states', 'Extension: two candidate boundary states']],
  cuni: [['setup_check', 'First: check your setup and fetch the databases'], ['f5_binary_pycalphad', 'Optional: a binary in pycalphad, before the real alloy'], ['f5b_tdb_anatomy', 'Optional: how a TDB file is built, line by line'], ['task01_cuni_equilibria', 'Task 01: Cu–Ni phase equilibria with a published database']],
  ninb: [['task05_ninb_sublattices', 'Task 05: Ni–Nb, sublattices and the amount basis'], ['f5b_tdb_anatomy', 'Optional: how a TDB file is built, site ratios and the amount basis'], ['task02_cuni_activity_fit', 'Further task: fit Cu–Ni interaction parameters'], ['task03_ni_twin', 'Further task: Ni grain-boundary energies'], ['task04_cuni_segregation', 'Further task: Cu–Ni boundary segregation']],
  'from-materials': [['f4_two_phases_and_diagrams', 'Optional: the common tangent, a grid and its linear programme, in code']],
  'from-or': [['f4o_thermo_for_optimisers', 'Recommended if you come from operations research: thermodynamics for optimisers, in code']],
  'or-prices': [['f4o_thermo_for_optimisers', 'Recommended if you come from operations research: prices, bending and metastability, in code']],
  'lp-primer': [['f4p_lp_primer', 'Optional: linear programmes from scratch, by hand and with SciPy']],
  'menu': [['f4c_master_and_dual', 'Optional (recommended for readers from operations research): the menu as a linear programme, in code']],
  'price-line': [['f4c_master_and_dual', 'Optional (recommended for readers from operations research): the line and its prices, in code']],
  'gap-curve': [['f4c_master_and_dual', 'Optional (recommended for readers from operations research): the gap curve and ranging, in code'], ['task01b_cuni_gap_curve', 'Optional: the gap curve and the driving force in the published Cu–Ni database (sections 1–4)']],
  'column-generation': [['f4d_column_generation', 'Optional (recommended for readers from operations research): column generation, in code']],
  'bounds': [['f4d_column_generation', 'Optional (recommended for readers from operations research): ceiling and floor every round, in code'], ['task01b_cuni_gap_curve', 'Optional: ceiling, floor and added states on real Cu–Ni curves (section 5)'], ['f4g_dual_view', 'Optional: every floor is a value of the dual function']],
  'local-global': [['f4e_global_pricing', 'Optional (recommended for readers from operations research): local search and keep pricing, in code'], ['f4g_dual_view', 'Optional: why the solver\'s line jumps, and a stabilised run']],
  'branch-and-bound': [['f4e_global_pricing', 'Optional (recommended for readers from operations research): branch-and-bound and a verifier, in code']],
  'two-questions': [['f4e_global_pricing', 'Optional: the joint case and the exercises, in code'], ['f6b_fit_an_elephant', 'Optional: is the model good enough? Fit an elephant']],
  'three-components': [['f4f_ternary', 'Optional: three components, in code']],
};
export const colabURL = (file: string) => `https://colab.research.google.com/github/${COLAB_REPO}/blob/${NOTEBOOK_RELEASE}/notebooks/${file}.ipynb`;

/** First question in the opening paragraph, as written in the narration. */
export function question(lesson: Lesson): string {
  const first = lesson.blocks.find(block => block.type === 'paragraph' && !/^(In plain words|Heads-up|Cards you may need): /.test(block.text));
  if (!first || first.type !== 'paragraph') return lesson.title;
  const symbols: Record<string, string> = { mu: 'μ', Delta: 'Δ', varepsilon: 'ε', approx: '≈', Omega: 'Ω', le: '≤', ge: '≥', times: '×' };
  const text = plainText(first.text.replace(/\\(mu|Delta|varepsilon|approx|Omega|le|ge|times)(?![a-zA-Z])/g, (_, name: string) => symbols[name]))
    .replace(/^(Problem · |Why CALPHAD\? )/, '');
  const end = text.indexOf('?');
  return end > 0 ? text.slice(0, end + 1) : text.split('. ')[0];
}

/** prefix: the exact text removed from the stage's first paragraph ('' when none). */
export type Stage = { key: string; label: string; kind: string; prefix: string; blocks: Block[] };
const kinds: [RegExp, string][] = [
  [/^Problem/, 'problem'], [/^Approach/, 'approach'], [/^Attempt|^Try/, 'attempt'],
  [/^Explore/, 'explore'], [/^Interpret|^Recover|^Wrap-up/, 'interpret'], [/^Glossary/, 'glossary'], [/^Refresher/, 'refresher'],
  [/^Next|^Continue/, 'next'], [/^Source-dependent/, 'extension'], [/^Attribution/, 'attribution'],
  [/^Why CALPHAD/, 'why'],
];
const kindOf = (label: string) => kinds.find(([pattern]) => pattern.test(label))?.[1] ?? 'note';

/** Split on the narration's own “Label · ” prefixes; the label becomes the stage heading. */
export function stages(lesson: Lesson): Stage[] {
  const result: Stage[] = [];
  const open = (label: string, prefix = '') => {
    const base = label.toLowerCase().replace(/[^a-z]+/g, '-').replace(/^-|-$/g, '');
    const key = result.some(stage => stage.key === base) ? `${base}-${result.length}` : base;
    const stage = { key, label, kind: kindOf(label), prefix, blocks: [] as Block[] };
    result.push(stage);
    return stage;
  };
  let current: Stage | null = null;
  for (const block of lesson.blocks) {
    if (block.type === 'paragraph') {
      const prefix = /^(\p{Lu}[\p{L} :,-]{2,40}) · /u.exec(block.text);   // letters of any script, so a label like "The Ω bump" works
      const why = /^Why CALPHAD\? /.exec(block.text);
      const tryThis = /^Try this /.test(block.text);
      if (prefix) {
        current = open(prefix[1], prefix[0]);
        current.blocks.push({ ...block, text: block.text.slice(prefix[0].length) });
        continue;
      }
      if (why) { current = open('Why CALPHAD?', why[0]); current.blocks.push({ ...block, text: block.text.slice(why[0].length) }); continue; }
      if (tryThis) { current = open('Try it'); current.blocks.push(block); continue; }
    }
    if (!current) current = open(lesson.id === 'start' && !(block.type === 'paragraph' && /^(In plain words|Cards you may need): /.test(block.text)) ? 'Refresher' : 'Overview');
    current.blocks.push(block);
  }
  return result;
}
