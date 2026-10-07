/** Presentation metadata and stage grouping for the finite narration. No science. */
import { COLAB_REPO } from './data';
import { plainText } from './learning';
import type { Block, Lesson, LearningID } from './learning';

export type LabKind = 'potentials' | 'unary' | 'binary' | 'twophase' | 'boundary' | 'cuni' | 'ninb';
export type Meta = { number: string; group: string; tag: string; lab: LabKind | null; labTitle: string | null; labLine: string | null };

export const meta: Record<LearningID, Meta> = {
  start: { number: '00', group: 'Basics', tag: 'Refresher', lab: 'potentials', labTitle: 'Energy ladder: U, H, F and G', labLine: 'Move T, S, p and V and see which terms matter.' },
  unary: { number: '01', group: 'Basics', tag: 'One component', lab: 'unary', labTitle: 'Gibbs energy versus temperature', labLine: 'Drag through the crossing; watch which branch is the minimum.' },
  binary: { number: '02', group: 'Mixtures', tag: 'Two components', lab: 'binary', labTitle: 'Tangent and chemical potentials', labLine: 'Slide along the curve; read μA and μB off the tangent.' },
  twophase: { number: '03', group: 'Mixtures', tag: 'Two phases', lab: 'twophase', labTitle: 'Common tangent and lever rule', labLine: 'Move the overall composition; watch the sample split into two phases.' },
  boundary: { number: '04', group: 'Boundaries', tag: 'Grain boundary', lab: 'boundary', labTitle: 'Open reservoir or closed cell', labLine: 'Count A and B atoms in two different constraints.' },
  cuni: { number: '05', group: 'Real alloys', tag: 'Cu–Ni', lab: 'cuni', labTitle: 'Saved Cu–Ni phase balances', labLine: 'Compare saved magnetic-on and magnetic-off samples.' },
  ninb: { number: '06', group: 'Real alloys', tag: 'Ni–Nb', lab: 'ninb', labTitle: 'Formula and atom bases', labLine: 'See why one division by atoms per formula is enough.' },
};

/** What each lab contains, in order: [view id, short label, one line]. A view id opens the lab there (#/<lesson>/lab/<view>). */
export const labViews: Partial<Record<LearningID, [string, string, string][]>> = {
  start: [['ladder', 'Energy ladder', 'U, H, F and G as bars you change with T, S, p and V.']],
  unary: [['crossing', 'Solid and liquid g(T)', 'Drag through the melting crossing.'], ['fractions', 'Phase-fraction line', 'g_mix against the liquid fraction at one T.']],
  binary: [['tangent', 'Curve, tangent and μ', 'The tangent at x and where it meets x = 0 and x = 1.'], ['slope', 'Exchange slope', 'μB − μA and where its sign changes.']],
  twophase: [['part-a', 'Part A · two different phases', 'Common tangent, split band and lever arms.'], ['part-b', 'Part B · one phase, two compositions', 'The regular-solution gap and its T–x diagram.'], ['part-c', 'Part C · melting and the lens', 'Solid and liquid curves and the lens they draw.']],
  boundary: [['cells', 'Open and closed cells', 'Occupancy, atom ledgers and where the B atoms go.'], ['tangent', 'Tangent picture · δ slider', 'Bulk curve, reservoir tangent and φ as a vertical gap.'], ['iteration', 'Closed cell by hand', 'The hand iteration, round by round.']],
  cuni: [['map', 'Clickable Cu–Ni phase diagram', 'Click any T and x: phases, amounts, tie line; play a cooling path.'], ['samples', 'Saved samples at x(Ni) = 0.5', 'Magnetic on and off at 600, 1500, 1540 and 1600 K.']],
  ninb: [['map', 'Clickable Ni–Nb phase diagram', 'Click any T and x; amounts in mol atoms or formula units.'], ['formula', 'One division, on the right basis', 'Formula energies divided by atoms per formula.'], ['sites', 'Build a formula unit', 'δ and μ site boxes you fill with Ni or Nb.'], ['mu-structure', 'Where the μ-phase atoms sit', 'A crystal sketch linked to the site boxes.']],
};

/** Course notebooks (notebooks/<file>.ipynb) to run after the attempt; RELEASE must match the notebooks' setup cell. */
export const NOTEBOOK_RELEASE = 'v0.1.2';
export const notebooks: Partial<Record<LearningID, [string, string][]>> = {
  start: [['f0_jupyter_and_potentials', 'Potentials: U, H, F and G']],
  unary: [['f1_unary_by_hand_and_code', 'One component, two phases: by hand and in code'], ['f2_unary_pycalphad', 'Optional: the same model in pycalphad']],
  binary: [['f3_binary_mixing_potentials', 'Binary mixtures: ideal mixing and chemical potentials']],
  twophase: [['f4_two_phases_and_diagrams', 'Two phases: common tangent, lever rule and phase diagrams'], ['f4b_lens_from_scratch', 'Optional: one melting lens from scratch in numpy/SciPy, then pycalphad']],
  boundary: [['f7_boundary_open_closed', 'A grain boundary in an open or closed cell'], ['f8_boundary_states', 'Extension: two candidate boundary states']],
  cuni: [['setup_check', 'First: check your setup and fetch the databases'], ['f5_binary_pycalphad', 'Optional: a binary in pycalphad, before the real alloy'], ['task01_cuni_equilibria', 'Task 01: Cu–Ni phase equilibria with a published database']],
  ninb: [['task05_ninb_sublattices', 'Task 05: Ni–Nb, sublattices and the amount basis']],
};
export const colabURL = (file: string) => `https://colab.research.google.com/github/${COLAB_REPO}/blob/${NOTEBOOK_RELEASE}/notebooks/${file}.ipynb`;

/** First question in the opening paragraph, as written in the narration. */
export function question(lesson: Lesson): string {
  const first = lesson.blocks.find(block => block.type === 'paragraph');
  if (!first || first.type !== 'paragraph') return lesson.title;
  const text = plainText(first.text).replace(/^(Problem · |Why CALPHAD\? )/, '');
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
      const prefix = /^([A-Z][A-Za-z :,-]{2,40}) · /.exec(block.text);
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
    if (!current) current = open(lesson.id === 'start' ? 'Refresher' : 'Overview');
    current.blocks.push(block);
  }
  return result;
}
