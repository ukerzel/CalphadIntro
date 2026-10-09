/** The route as a map: one main line (steps 00–17) and the branches and spurs that leave it and come back.
 *  Positions are abstract: t runs along the main line, o is the distance from it (negative above, positive below). */
import type { LearningID } from './learning';

export type StationKind = 'main' | 'entry' | 'detour' | 'spur' | 'optional';
export type Station = { key: string; id: LearningID; anchor?: string; kind: StationKind; t: number; o: number; short: string; note: string };
export type Track = { kind: 'main' | 'branch'; points: [number, number][] };

/** The things every learner does, in order. */
export const mainLine: LearningID[] = ['start', 'unary', 'binary', 'twophase', 'boundary', 'cuni', 'ninb', 'from-materials', 'menu', 'price-line',
  'gap-curve', 'column-generation', 'bounds', 'local-global', 'branch-and-bound', 'two-questions'];
const T = Object.fromEntries(mainLine.map((id, i) => [id, i])) as Record<LearningID, number>;

export const stations: Station[] = [
  ...mainLine.map(id => ({ key: id, id, kind: 'main' as const, t: T[id], o: 0, short: '', note: '' })),
  { key: 'part-d', id: 'twophase', anchor: 'part-d-from-scratch-and-with-pycalphad', kind: 'spur', t: 3, o: 1.3, short: 'D',
    note: 'Optional part of step 03: how a program finds the split. Step 10 repeats what it needs.' },
  { key: 'from-or', id: 'from-or', kind: 'entry', t: 6.4, o: 1.35, short: '08', note: 'The entry for readers from operations research, instead of step 07.' },
  { key: 'or-prices', id: 'or-prices', kind: 'entry', t: 7.6, o: 1.35, short: '09', note: 'Second half of the entry from operations research; then step 10.' },
  { key: 'lp-primer', id: 'lp-primer', kind: 'detour', t: 7.5, o: -1.35, short: 'LP', note: 'Optional detour after step 07 for anyone new to linear programmes; back to step 10.' },
  { key: 'three-components', id: 'three-components', kind: 'optional', t: 16.2, o: 0, short: '18', note: 'Optional extension: a third component. No other step needs it.' },
];

export const tracks: Track[] = [
  { kind: 'main', points: mainLine.map(id => [T[id], 0]) },
  // branches leave and rejoin the main line at right angles, clear of the lab and notebook marks
  { kind: 'branch', points: [[3, 0], [3, 1.3]] },
  { kind: 'branch', points: [[6, 0], [6, 1.35], [8, 1.35], [8, 0]] },
  { kind: 'branch', points: [[7, 0], [7, -1.35], [8, -1.35], [8, 0]] },
  { kind: 'branch', points: [[15, 0], [16.2, 0]] },
];

/** Where a branch page sits on the main line, for the slim rail's "you are here". */
export const joins: Partial<Record<LearningID, LearningID>> = { 'from-or': 'ninb', 'or-prices': 'ninb', 'lp-primer': 'from-materials', 'three-components': 'two-questions' };

export const kindLabel: Record<StationKind, string> = {
  main: 'Main line', entry: 'Entry for readers from operations research', detour: 'Optional detour', spur: 'Optional part', optional: 'Optional extension',
};
