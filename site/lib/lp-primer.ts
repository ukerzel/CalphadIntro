/** The optional LP primer's data (course/self_study/generated/lp_primer.json) and the display arithmetic its lab may do.
 *
 * Invented teaching numbers: scrap lots with a Ni content and a price. The
 * browser may apply the lever rule to two exported lots, draw a straight line
 * through two of them, and multiply exported prices by exported corner
 * amounts. Reference answers (the best charge, the search, the prices, the
 * corners and their tight rules) come from the export.
 */
import type { Dot } from '@/lib/day3';

export const lpPrimerPath = 'self_study/generated/lp_primer.json';

export type Lot = { name: string; short: string; w: number; price: number };
export type Charge = { used: number[]; f: number[]; cost: number };
export type SwapFrame = Charge & { line: { base: number; slope: number; top: number }; gaps: number[]; enter: number | null; leave: number | null };
export type TargetFrame = Charge & { z: number; slope?: number; slopes?: [number | null, number | null] };
export type Rule = { id: string; label: string; a: [number, number]; sense: '>=' | '<='; b: number | null; unit: string };
export type Corner = { f: [number, number]; tight: string[] };

export type LpPrimerData = {
  schema_version: 1; note: string;
  blend: {
    target: number; units: Record<string, string>; lots: Lot[]; best: Charge; pairs_tried: number;
    swap: { start: number[]; frames: SwapFrame[] };
    prices: { base: number; slope: number; cu: number; ni: number; range: [number, number] };
    nudge: { dz: number; change: number; cost: number };
    offer: { lot: Lot; line_height: number; gap: number; best: Charge };
    hull: number[]; targets: TargetFrame[];
  };
  polygon: {
    lots: { name: string; short: string; ni: number; fe: number; price: number }[];
    rules: Rule[]; fe_cap: { normal: number; strict: number };
    price_q: { default: number; range: [number, number] };
    regions: { normal: Corner[]; strict: Corner[] };
    optimum: { f: [number, number]; cost: number; duals: Record<string, number>; tight: string[]; ni_range: [number, number] };
    ties: number[]; strict_status: number; exact: { f: [number, number] };
  };
};

/** Lots as the dots of lib/day3 (content on x, price on g), so its lever rule and line helpers apply. */
export const asDots = (lots: Lot[]): Dot[] => lots.map(lot => ({ phase: lot.short, x: lot.w, g: lot.price }));

/** The lever amounts of two lots at content z, even when one is negative (the lab shows why such a pair is impossible). */
export function rawLever(a: Lot, b: Lot, z: number): [number, number] | null {
  if (a.w === b.w) return null;
  const fb = (z - a.w) / (b.w - a.w);
  return [1 - fb, fb];
}

/** Cost of a charge of the two polygon lots at an exported corner, for a chosen price of the second lot. */
export const cornerCost = (pricePerKg: [number, number], f: [number, number]) => pricePerKg[0] * f[0] + pricePerKg[1] * f[1];
