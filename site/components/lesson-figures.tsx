'use client';
import { useContext, useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { ArrowUpRight } from 'lucide-react';
import Plot, { Mark, path } from '@/components/plot';
import { FollowContext } from '@/components/xref';
import { LeverArms, twoPhasePath } from '@/components/twophase-view';
import type { TwoPhaseData } from '@/components/twophase-view';
import { boundaryViewsPath } from '@/components/boundary-views';
import type { BoundaryViewsData } from '@/components/boundary-views';
import { SiteBoxes, MuSites } from '@/components/material-explorer';
import { loadLearningJSON } from '@/lib/materials';
import type { LearningID } from '@/lib/learning';

function useJSON<T>(file: string, given?: T) {
  const [data, setData] = useState<T | null>(given ?? null), [error, setError] = useState('');
  useEffect(() => {
    if (given) return;
    let active = true;
    loadLearningJSON<T>(file).then(v => { if (active) setData(v); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, [file, given]);
  return { data, error };
}

/** "Open this in the lab": follows like a cross-reference, so the Back chip returns here. */
function LabLink({ id, view, children }: { id: LearningID; view: string; children: ReactNode }) {
  const follow = useContext(FollowContext), self = useRef<HTMLAnchorElement>(null);
  const from = () => { const stage = self.current?.closest('section.stage')?.querySelector('h2')?.textContent ?? ''; const step = document.querySelector('.lesson-number')?.textContent ?? ''; return [step, stage].filter(Boolean).join(' · '); };
  return <a ref={self} className="xref-go" href={`#/${id}/lab/${view}`} onClick={event => { event.preventDefault(); follow({ page: 'lesson', id, lab: true, view }, from()); }}>{children}<ArrowUpRight aria-hidden /></a>;
}

function Figure({ title, caption, link, children }: { title: string; caption: ReactNode; link?: ReactNode; children: ReactNode }) {
  return <figure className="lesson-figure"><p className="lesson-figure-title">{title}</p>{children}<figcaption className="caption">{caption}{link && <> {link}</>}</figcaption></figure>;
}

// Reserves roughly the figure's height so content below does not jump when the data arrives.
const Pending = ({ error }: { error: string }) => error ? <p className="caption" role="alert">Figure unavailable: {error}.</p> : <div className="lesson-figure is-pending"><p className="loading" role="status">Loading the figure…</p></div>;

/** Step 02: the shape of the tangent argument, without numbers. */
export function TangentSketch() {
  // Shape only: a convex curve f(x) = (x − 0.55)² + 0.02 and its tangent at x₀ = 0.25, mapped to the drawing.
  const W = 520, H = 260, X = (v: number) => 60 + v * 400, Y = (v: number) => 30 + (0.34 - v) / 0.72 * 190;
  const f = (x: number) => (x - 0.55) ** 2 + 0.02, x0 = 0.25, slope = 2 * (x0 - 0.55), at = (x: number) => f(x0) + slope * (x - x0);
  const g = (x: number) => Y(f(x));
  const curve = Array.from({ length: 41 }, (_, i) => i / 40).map(x => `${X(x).toFixed(1)},${g(x).toFixed(1)}`).join('L');
  return <Figure title="Where the tangent meets the edges" caption={<>A sketch of the shape only. The tangent at x₀ meets the left edge (pure A) at μ<sub>A</sub> and the right edge (pure B) at μ<sub>B</sub>; move x₀ and both values change. The lab draws this for the real step 02 curve.</>}
    link={<LabLink id="binary" view="tangent">After your attempt: the tangent in the lab</LabLink>}>
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Sketch: a curved g(x) with its tangent at x0; the tangent meets x = 0 at mu A and x = 1 at mu B." className="sketch-svg">
      <line className="sk-axis" x1={X(0)} x2={X(0)} y1={20} y2={H - 30} /><line className="sk-axis" x1={X(1)} x2={X(1)} y1={20} y2={H - 30} />
      <path className="sk-curve" d={`M${curve}`} />
      <line className="sk-tangent" x1={X(0)} y1={Y(at(0))} x2={X(1)} y2={Y(at(1))} />
      <line className="sk-guide" x1={X(x0)} x2={X(x0)} y1={g(x0)} y2={H - 30} />
      <circle className="sk-point" cx={X(x0)} cy={g(x0)} r="5" /><circle className="sk-end" cx={X(0)} cy={Y(at(0))} r="5" /><circle className="sk-end" cx={X(1)} cy={Y(at(1))} r="5" />
      <text className="sk-label" x={X(0) - 8} y={Y(at(0)) + 4} textAnchor="end">μ<tspan className="sk-sub" dy="4">A</tspan></text><text className="sk-label" x={X(1) + 8} y={Y(at(1)) + 4}>μ<tspan className="sk-sub" dy="4">B</tspan></text>
      <text className="sk-label" x={X(0.62)} y={g(0.62) - 10}>g(x)</text>
      <text className="sk-tick" x={X(0)} y={H - 12} textAnchor="middle">x = 0 (pure A)</text><text className="sk-tick" x={X(x0)} y={H - 12} textAnchor="middle">x₀</text><text className="sk-tick" x={X(1)} y={H - 12} textAnchor="middle">x = 1 (pure B)</text>
    </svg>
  </Figure>;
}

/** Step 03 part A: the common tangent between ALPHA and BETA, and the lever at z = 0.35. Exported values only. */
export function CommonTangentFigure({ given }: { given?: TwoPhaseData }) {
  const { data, error } = useJSON<TwoPhaseData>(twoPhasePath, given);
  if (!data) return <Pending error={error} />;
  const A = data.part_a, co = A.coexistence, z = 0.35;
  return <Figure title="Part A in one picture" caption="ALPHA (left curve) and BETA (right curve) at 1000 K. The common tangent touches both; any overall z between the touching points splits into those two compositions, and the lever arms give the amounts."
    link={<LabLink id="twophase" view="part-a">Move z yourself in part A of the lab</LabLink>}>
    <Plot compact title="ALPHA, BETA and their common tangent" desc="Two curves at 1000 K with the common tangent between the touching points and the overall composition z = 0.35 marked."
      height={260} xDomain={[0, 1]} yDomain={[-12000, 4000]} xLabel="B atom fraction" yLabel="g (kJ/mol atoms)" yFormat={v => `${v / 1000}`}>
      {({ x, y, top, bottom }) => <>
        <rect className="band band-split" x={x(co.x_ALPHA)} width={x(co.x_BETA) - x(co.x_ALPHA)} y={top} height={bottom - top} />
        <path className="line line-solid" d={path(A.x.map((v, i) => [x(v), y(A.GM.ALPHA[i])]))} />
        <path className="line line-open" d={path(A.x.map((v, i) => [x(v), y(A.GM.BETA[i])]))} />
        <line className="tangent-solid" x1={x(co.x_ALPHA)} y1={y(co.GM_x_ALPHA)} x2={x(co.x_BETA)} y2={y(co.GM_x_BETA)} />
        <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
        <Mark x={x(co.x_ALPHA)} y={y(co.GM_x_ALPHA)} r={5} className="mark-solid" /><Mark x={x(co.x_BETA)} y={y(co.GM_x_BETA)} r={5} className="mark-open" />
      </>}
    </Plot>
    <LeverArms xAlpha={co.x_ALPHA} xBeta={co.x_BETA} z={z} />
  </Figure>;
}

/** Step 03: the two phase diagrams that parts B and C draw. Exported values only. */
export function PhaseDiagramsFigure({ given }: { given?: TwoPhaseData }) {
  const { data, error } = useJSON<TwoPhaseData>(twoPhasePath, given);
  if (!data) return <Pending error={error} />;
  const B = data.part_b, C = data.part_c, gap = B.rows.filter(r => r.compositions.length === 2), lens = C.rows.filter(r => r.x_SOLID !== null);
  const liquidus = [[0, C.melting_K.A], ...lens.map(r => [r.x_LIQUID!, r.T_K]), [1, C.melting_K.B]] as [number, number][];
  const solidus = [[0, C.melting_K.A], ...lens.map(r => [r.x_SOLID!, r.T_K]), [1, C.melting_K.B]] as [number, number][];
  return <Figure title="Touching points against temperature: two phase diagrams" caption="Left, part B: the two compositions of one phase close at Tc, a miscibility gap. Right, part C: liquid and solid touching points draw a lens between the two melting points. Inside either outline the sample splits; a horizontal tie line joins the two compositions at one temperature."
    link={<><LabLink id="twophase" view="part-b">Part B in the lab</LabLink> · <LabLink id="twophase" view="part-c">Part C in the lab</LabLink></>}>
    <div className="twin">
      <Plot compact title="Miscibility gap (part B)" desc="Coexisting compositions of one phase by temperature, closing at the critical temperature." height={240} xDomain={[0, 1]} yDomain={[580, 1320]} xLabel="x" yLabel="T (K)" yFormat={v => `${v}`}>
        {({ x, y }) => <>
          <path className="gap-area" d={`${path(gap.map(r => [x(r.compositions[0]), y(r.T_K)]))}L${x(0.5).toFixed(2)},${y(B.Tc_K).toFixed(2)}L${[...gap].reverse().map(r => `${x(r.compositions[1]).toFixed(2)},${y(r.T_K).toFixed(2)}`).join('L')}Z`} />
          <text className="hatch-label" x={x(0.5)} y={y(800)} textAnchor="middle">two compositions</text>
          <text className="hatch-label" x={x(0.5)} y={y(1290)} textAnchor="middle">one phase</text>
        </>}
      </Plot>
      <Plot compact title="Melting lens (part C)" desc="Liquidus and solidus of two ideal phases between the melting points of A and B." height={240} xDomain={[0, 1]} yDomain={[930, 1870]} xLabel="x" yLabel="T (K)" yFormat={v => `${v}`}>
        {({ x, y }) => <>
          <path className="lens-area" d={`${path(liquidus.map(([c, t]) => [x(c), y(t)]))}L${[...solidus].reverse().map(([c, t]) => `${x(c).toFixed(2)},${y(t).toFixed(2)}`).join('L')}Z`} />
          <path className="line line-liquid" d={path(liquidus.map(([c, t]) => [x(c), y(t)]))} />
          <path className="line line-solid" d={path(solidus.map(([c, t]) => [x(c), y(t)]))} />
          <text className="hatch-label" x={x(0.2)} y={y(1700)}>LIQUID</text><text className="hatch-label" x={x(0.65)} y={y(1100)}>SOLID</text>
        </>}
      </Plot>
    </div>
  </Figure>;
}

/** Step 04: the open boundary as a tangent picture at one illustrative state (x_b = 0.50, δ = −5000). Exported values only. */
export function BoundaryTangentFigure({ given }: { given?: BoundaryViewsData }) {
  const { data, error } = useJSON<BoundaryViewsData>(boundaryViewsPath, given);
  if (!data) return <Pending error={error} />;
  const res = data.reservoirs.find(r => r.x_b === 0.5) ?? data.reservoirs[0], c = res.cases.find(k => k.delta === -5000) ?? res.cases[0];
  const all = [...data.gb, ...c.gs, res.mu_A, res.mu_B], lo = Math.min(...all), hi = Math.max(...all), pad = (hi - lo) * 0.06;
  return <Figure title="The odds formula as a picture" caption={<>Dark: the bulk curve g<sub>b</sub>; gold: its tangent at the reservoir composition (here x<sub>b</sub> = {res.x_b.toFixed(2)}), ending at μ<sub>A</sub> and μ<sub>B</sub>. Violet: the boundary curve g<sub>s</sub> = g<sub>b</sub> + δθ (δ = −5000 J/mol boundary sites). The boundary settles where a line parallel to the gold one touches g<sub>s</sub>; the vertical gap there is φ.</>}
    link={<LabLink id="boundary" view="tangent">After your attempt: change δ and x<sub>b</sub> in the lab</LabLink>}>
    <Plot compact title="Bulk curve, reservoir tangent and boundary curve" desc="Bulk g_b with its tangent at the reservoir composition, the tilted boundary curve g_s and the parallel line touching it." height={260}
      xDomain={[0, 1]} yDomain={[lo - pad, hi + pad]} xLabel="B fraction (x or θ)" yLabel="g (kJ/mol sites)" yFormat={v => `${Math.round(v / 1000)}`}>
      {({ x, y }) => <>
        <path className="line line-total" d={path(data.x.map((v, i) => [x(v), y(data.gb[i])]))} />
        <path className="line line-gs" d={path(data.x.map((v, i) => [x(v), y(c.gs[i])]))} />
        <line className="tangent" x1={x(0)} y1={y(res.mu_A)} x2={x(1)} y2={y(res.mu_B)} />
        <line className="tangent-parallel" x1={x(0)} y1={y(c.parallel_tangent[0])} x2={x(1)} y2={y(c.parallel_tangent[1])} />
        <line className="phi-gap" x1={x(c.theta)} x2={x(c.theta)} y1={y(c.gs_theta)} y2={y(c.gs_theta - c.phi)} />
        <Mark x={x(res.x_b)} y={y(res.gb_x_b)} r={5} className="mark-total" label="x_b" />
        <Mark x={x(c.theta)} y={y(c.gs_theta)} r={6} className="mark-gs" label="θ" />
      </>}
    </Plot>
  </Figure>;
}

/** Step 06: site boxes for δ and μ, and the μ crystal sketch, right where sublattices are introduced. */
export function SublatticeFigure() {
  return <Figure title="Fill the sublattices yourself" caption="Counting only: each box is a site of one formula unit. The μ-phase sketch shows where those sites sit in the crystal, as far as the database’s site counts allow."
    link={<LabLink id="ninb" view="mu-structure">After your attempt: the same sketch in the results explorer</LabLink>}>
    <div className="basis-grid">
      <SiteBoxes name="δ phase (DELTA)" sizes={[1, 1, 2]} presets={[['NbNi₃, Nb on sublattice 1', ['Nb', 'Ni', 'Ni']], ['NbNi₃, Nb on sublattice 2', ['Ni', 'Nb', 'Ni']], ['all Nb (the endmember in the energy table)', ['Nb', 'Nb', 'Nb']], ['all Ni', ['Ni', 'Ni', 'Ni']]]} />
    </div>
    <MuSites />
  </Figure>;
}
