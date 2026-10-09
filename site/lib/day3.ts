/** Advanced-step data (course/self_study/generated/day3.json) and the display arithmetic its labs may do.
 *
 * The browser never evaluates a Gibbs model. It may subtract a straight line
 * from exported energies, apply the lever rule to exported dots, multiply the
 * exchange price by a nudge, and find which exported dot a lifted or pivoted
 * line touches first. Reference answers (lines, dips, bounds, floors) come
 * from the export.
 */
export const day3Path = 'self_study/generated/day3.json';

export type Dot = { phase: string; x: number; g: number };
export type Used = Dot & { f: number };
export type Line = { mu_A: number; d_mu: number; mu_B: number };
export type Dip = { phase: string; x: number; depth: number };
export type Iteration = {
  k: number; states: Dot[]; used: Used[]; G_up: number; line: Line; line_label: string;
  dips: Record<string, Dip>; best: Dip; G_low_raw: number; G_low_best: number; remaining: number;
};
/** One interval of branch-and-bound; floor, x and gap are null for intervals never examined (an early stop). */
export type Node = { n: number; lo: number; hi: number; floor: number | null; x: number | null; gap_at_x: number | null; action: string };

export type Day3Data = {
  schema_version: 1;
  lens: {
    T_K: number; z: number; RT: number;
    curve: { x: number[]; SOLID: number[]; LIQUID: number[] };
    truth: { x_LIQUID: number; x_SOLID: number; f_LIQUID: number; f_SOLID: number; G: number; line: Line };
    hook: { x: number[]; dots: Dot[]; used: Used[]; G_up: number; line: Line; above_truth: number };
    menu: { x: number[]; dots: Dot[] };
    s1: { used: Used[]; G_up: number; above_hook: number; above_truth: number };
    s2: Line;
    s3: { nudge: number; nudge_energy: number; true_line: Line };
    s4: { gaps: { phase: string; x: number; gap: number }[] };
    s5: { range: [number, number]; frames: { z: number; used: Used[]; G_up: number; line: Line }[] };
    s5b: { z: number; x: number[]; frames: { T_K: number; x_SOLID: number; x_LIQUID: number; used: Used[]; g: { SOLID: number[]; LIQUID: number[] } }[] };
    s6: { seed: string; iterations: (Iteration & { windows: Record<string, { x: number[]; gap: number[] }> })[] };
    s7: { G_up: number; G_low: number; remaining: number; dips: Record<string, Dip>;
      spacing: { spacing: number; dots_per_phase: number; G_up: number; G_low: number; remaining: number; used: Used[] }[] };
    reveal: { start_slope: number; frames: { mu_A: number; d_mu: number; touch: number[] }[] };
  };
  regular: {
    T_K: number; z: number; omega: number; Tc_K: number; RT: number;
    curve: { x: number[]; ALPHA: number[] };
    binodal: [number, number]; spinodal: [number, number]; curvature: Record<string, number>;
    s8: { tangent: Line & { x: number; g: number }; dip: Dip & { g: number; x_print: number; g_print: number };
      local_search: { start: number; path: number[]; end: number; gap_end: number }[] };
    s8b: { iterations: (Iteration & { windows: Record<string, { x: number[]; gap: number[] }> })[]; two_dot_line: Line & { through: number[]; dip: Dip; label: string }; dual_slope_max: number;
      final: { used: Used[]; G_up: number; line: Line } };
    s9: { eps: number; line: Line; G_up: number; line_at_z: number; nodes: Node[]; leaves: Node[]; status: string;
      lowest_floor: number; G_low: number; remaining: number; width_scale: number;
      unresolved: { max_nodes: number; status: string; nodes: Node[]; leaves: Node[] };
      verifier: { accepted: boolean; perturbed: { change: string; accepted: boolean; problems: string[] }[] } };
    s9_discovery: { line: Line; tol: number; nodes: Node[]; found: Node; status: string };
    joint: { z: number[]; line_at_half: Line; dips_at_half: Dip[] };
  };
};

/** Height of the line mu_A + d_mu x. */
export const height = (mu_A: number, d_mu: number, x: number) => mu_A + d_mu * x;

/** The line through two exported dots. */
export function through(a: Dot, b: Dot): { mu_A: number; d_mu: number } {
  const d_mu = (b.g - a.g) / (b.x - a.x);
  return { mu_A: a.g - d_mu * a.x, d_mu };
}

/** Dots strictly below the line (beyond a display tolerance): the line is then not a floor for them. */
export function below(dots: Dot[], mu_A: number, d_mu: number, tol = 1e-6): number[] {
  return dots.flatMap((dot, i) => dot.g < height(mu_A, d_mu, dot.x) - tol ? [i] : []);
}

/** Lever rule for two dots and an overall composition; null when the pair cannot make z with non-negative amounts. */
export function lever(a: Dot, b: Dot, z: number): { fa: number; fb: number; G: number } | null {
  if (a.x === b.x) return a.x === z ? { fa: 1, fb: 0, G: Math.min(a.g, b.g) } : null;
  const fb = (z - a.x) / (b.x - a.x), fa = 1 - fb;
  if (fa < -1e-12 || fb < -1e-12) return null;
  return { fa, fb, G: fa * a.g + fb * b.g };
}

/** The cheapest mixture that a basket of dots can make at z: one dot at z, or the best bracketing pair. */
export function bestOfBasket(dots: Dot[], z: number): { used: [number, number] | [number]; G: number; f: number[] } | null {
  let best: { used: [number, number] | [number]; G: number; f: number[] } | null = null;
  dots.forEach((dot, i) => { if (Math.abs(dot.x - z) < 1e-12 && (!best || dot.g < best.G)) best = { used: [i], G: dot.g, f: [1] }; });
  for (let i = 0; i < dots.length; i++) for (let j = i + 1; j < dots.length; j++) {
    const m = lever(dots[i], dots[j], z);
    if (m && dots[i].x !== dots[j].x && (!best || m.G < best.G - 1e-12)) best = { used: [i, j], G: m.G, f: [m.fa, m.fb] };
  }
  return best;
}

/** Reveal animation: lift a line of the given slope until it touches a dot, then pivot from dot to dot
 * (raising the height at z) until two touching dots lie on opposite sides of z or one sits at z.
 * Every frame stays on or below all dots. */
export function liftAndPivot(dots: Dot[], z: number, slope: number): { mu_A: number; d_mu: number; touch: number[] }[] {
  let k = 0;
  dots.forEach((dot, i) => { if (dot.g - slope * dot.x < dots[k].g - slope * dots[k].x) k = i; });
  const frames = [{ mu_A: dots[k].g - slope * dots[k].x, d_mu: slope, touch: [k] }];
  for (let step = 0; step < dots.length; step++) {
    const c = dots[k];
    if (Math.abs(c.x - z) < 1e-12) break;
    let next = -1, s = c.x > z ? -Infinity : Infinity;
    dots.forEach((dot, j) => {
      if (c.x > z && dot.x < c.x - 1e-12) { const t = (c.g - dot.g) / (c.x - dot.x); if (t > s) { s = t; next = j; } }
      if (c.x < z && dot.x > c.x + 1e-12) { const t = (dot.g - c.g) / (dot.x - c.x); if (t < s) { s = t; next = j; } }
    });
    if (next < 0) break;
    frames.push({ mu_A: c.g - s * c.x, d_mu: s, touch: [k, next] });
    if ((dots[next].x - z) * (c.x - z) <= 0) break;
    k = next;
  }
  return frames;
}

/** A curve minus a line, point by point (the gap curve). */
export const gapCurve = (xs: number[], gs: number[], mu_A: number, d_mu: number) => xs.map((x, i) => gs[i] - height(mu_A, d_mu, x));
