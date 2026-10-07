'use client';
/** Part D of the step 03 lab: one equilibrium of the part C lens found from scratch (left) and by pycalphad (right). Saved frames only. */
import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import RecordSlider from '@/components/record-slider';
import Plot, { Mark, path, ticks } from '@/components/plot';
import type { Frame } from '@/components/plot';
import { LiveStatus, Player, Readout, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { fixed, num } from '@/lib/format';

type Pair = { SOLID: number; LIQUID: number };
type Line = [number, number];
type Chosen = { phase: 'SOLID' | 'LIQUID'; x: number; f: number; g_relative: number };
type Sample = { count: number; x: number[]; g_relative: number[] };
export type ScratchData = {
  schema_version: 1;
  conditions: { T_K: number; z: number; P_Pa: number; R: number; melting_K: { A: number; B: number } };
  view: { x: [number, number]; relative_to: string };
  curves: { x: number[]; SOLID: number[]; LIQUID: number[] };
  answer: { x_SOLID: number; x_LIQUID: number; f_LIQUID: number; GM: number; GM_relative: number; mu_A: number; mu_B: number;
    tangent_relative: Line; g_relative: Pair; homogeneous_GM: Pair; homogeneous_GM_relative: Pair };
  brute: { id: string; x_SOLID: number; x_LIQUID: number; f_LIQUID: number; GM: number; GM_relative: number; g_relative: Pair }[];
  grid: { id: string; spacing: number; points: number; x: number[]; g_relative: { SOLID: number[]; LIQUID: number[] }; chosen: Chosen[]; GM: number; GM_relative: number; above_exact: number }[];
  newton: { start: Line; frames: { id: string; iteration: number; x_SOLID: number; x_LIQUID: number; residual_mu_A: number; residual_mu_B: number;
    g_relative: Pair; tangent_relative: { SOLID: Line; LIQUID: Line } }[] };
  continuation: { id: string; T_K: number; x_SOLID: number; x_LIQUID: number }[];
  pycalphad: { version: string; tdb: string; sample_every: number; sample: { SOLID: Sample; LIQUID: Sample };
    result: { phases: string[]; x_SOLID: number; x_LIQUID: number; f_LIQUID: number; GM: number; GM_relative: number; mu_A: number; mu_B: number; tangent_relative: Line };
    lens: { T_K: number; x_SOLID: number; x_LIQUID: number }[] };
  difference: { x_SOLID: number; x_LIQUID: number; f_LIQUID: number; GM: number; mu_A: number; mu_B: number; lens_max_x: number };
};
export const scratchPath = 'self_study/generated/from_scratch.json';
export type Method = 'brute' | 'grid' | 'newton' | 'walk';
const sci = (value: number) => (value === 0 ? '0' : Math.abs(value).toExponential(1).replace('e-', ' × 10⁻').replace('e+', ' × 10^').replace(/⁻(\d+)/, (_, d: string) => `⁻${d.split('').map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[Number(c)]).join('')}`));
const along = ([t0, t1]: Line, x: number) => t0 + (t1 - t0) * x;   // height of a straight line at x (geometry only)

export default function ScratchPart({ initialMethod = 'brute' }: { initialMethod?: Method }) {
  const [data, setData] = useState<ScratchData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<ScratchData>(scratchPath).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the from-scratch frames…</p>;
  return <ScratchLab data={data} initialMethod={initialMethod} />;
}

/** Both phases' curves at 1400 K, measured from the final common tangent (the line at 0), plus whatever the caller draws on top. */
function EnergyPlot({ data, title, desc, top, children }: { data: ScratchData; title: string; desc: string; top: number; children: (frame: Frame) => ReactNode }) {
  const c = data.curves, hi = Math.min(Math.max(...c.SOLID, ...c.LIQUID), top), lo = -0.08 * hi;
  return <Plot compact title={title} desc={desc} height={300} xDomain={data.view.x} yDomain={[lo, hi]} yTicks={ticks(lo, hi, 4)}
    xLabel="B atom fraction x" yLabel="g − common tangent (J/mol atoms)" yFormat={value => num(value, 0)}>
    {frame => <>
      <path className="line line-solid" d={path(c.x.map((v, i) => [frame.x(v), frame.y(c.SOLID[i])]))} />
      <path className="line line-liquid" d={path(c.x.map((v, i) => [frame.x(v), frame.y(c.LIQUID[i])]))} />
      <line className="ghost" x1={frame.x(data.conditions.z)} x2={frame.x(data.conditions.z)} y1={frame.top} y2={frame.bottom} />
      <line className="zero-line" x1={frame.left} x2={frame.right} y1={frame.y(0)} y2={frame.y(0)} />
      {children(frame)}
    </>}
  </Plot>;
}

/** pycalphad's answer drawn on the same axes: its common tangent, its two touching points and the sample energy at z. */
function PycalphadAnswer({ data, samples, top }: { data: ScratchData; samples: boolean; top: number }) {
  const r = data.pycalphad.result, s = data.pycalphad.sample;
  return <EnergyPlot data={data} top={top} title={samples ? 'pycalphad: sampled points and its answer' : 'pycalphad: its answer'}
    desc={samples ? 'The same two curves; dots are compositions pycalphad evaluated before refining, the gold dashed line is the common tangent it returns.' : 'The same two curves with the common tangent pycalphad returns (gold dashed) and its two touching points.'}>
    {({ x, y }) => <>
      {samples && (['SOLID', 'LIQUID'] as const).map(phase => s[phase].x.map((v, i) => <circle key={`${phase}${i}`} className={`sample-dot dot-${phase.toLowerCase()}`} cx={x(v)} cy={y(s[phase].g_relative[i])} r="2.2" />))}
      <line className="tangent" x1={x(0)} y1={y(r.tangent_relative[0])} x2={x(1)} y2={y(r.tangent_relative[1])} />
      <Mark x={x(r.x_LIQUID)} y={y(along(r.tangent_relative, r.x_LIQUID))} r={5} className="mark-liquid" />
      <Mark x={x(r.x_SOLID)} y={y(along(r.tangent_relative, r.x_SOLID))} r={5} className="mark-solid" />
      <Mark x={x(data.conditions.z)} y={y(r.GM_relative)} r={6} className="mark-min" label="pycalphad" />
    </>}
  </EnergyPlot>;
}

export function ScratchLab({ data, initialMethod = 'brute', initialFrame = 0 }: { data: ScratchData; initialMethod?: Method; initialFrame?: number }) {
  const [method, setMethodState] = useState<Method>(initialMethod);
  const [zoom, setZoom] = useState<'close' | 'wide'>(initialMethod === 'newton' ? 'wide' : 'close');
  const setMethod = (m: Method) => { setMethodState(m); setZoom(m === 'newton' ? 'wide' : 'close'); };
  const top = zoom === 'close' ? 150 : 800;
  const start = (m: Method) => (m === initialMethod ? initialFrame : 0);
  const [ib, setIb] = useState(start('brute')), [ig, setIg] = useState(start('grid')), [inw, setIn] = useState(start('newton')), [iw, setIw] = useState(start('walk'));
  const { z, T_K } = data.conditions, ans = data.answer, pyc = data.pycalphad.result;
  const B = data.brute[ib], G = data.grid[ig], N = data.newton.frames[inw], W = data.continuation[iw];
  const bestSoFar = data.brute.slice(0, ib + 1).reduce((a, b) => (b.GM < a.GM ? b : a));
  const walked = data.continuation.slice(0, iw + 1);
  const pycLens = new Map(data.pycalphad.lens.map(r => [r.T_K, r]));
  const lensT: [number, number] = [930, 1870];

  const intro: Record<Method, string> = {
    brute: 'Left: each trial solid composition (above z) with the liquid composition (below z) that gives the lowest split energy. The black chord joins the two; its height at z is the energy of that split above the answer. The small blue marker at z is the sample as all solid. Right: pycalphad also starts by evaluating each phase at many compositions (dots), then returns the common tangent.',
    grid: 'Left: candidate compositions on a grid (dots) and the cheapest mixture of them that keeps all atoms and all B atoms, found by a linear programme. Coarse grids miss the split; finer grids close in on it. Right: pycalphad samples each phase more densely and then refines the best candidates.',
    newton: 'Left: Newton’s method on the two equations μA(solid) = μA(liquid) and μB(solid) = μB(liquid), from a rough first guess (the notebook’s fsolve takes Newton-like steps for you). Each phase’s tangent is drawn in its colour; when they become one line, the equations are solved. Right: pycalphad’s answer, the same common tangent.',
    walk: 'Left: starting from the 1400 K answer, each temperature is solved with the previous answer as the first guess (continuation), up to 1790 K and then down to 1010 K. Right: pycalphad’s equilibrium at the same temperatures.',
  };

  let left: ReactNode, right: ReactNode, controls: ReactNode, side: ReactNode, status: string;
  if (method === 'brute') {
    left = <EnergyPlot data={data} top={top} title={`From scratch: trial split ${ib + 1} of ${data.brute.length}`} desc="Solid and liquid curves; a chord joins the trial solid composition and its best liquid partner; the gold marker is the split energy at z, the small blue marker the all-solid energy at z.">
      {({ x, y }) => <>
        <line className="chord" x1={x(B.x_LIQUID)} y1={y(B.g_relative.LIQUID)} x2={x(B.x_SOLID)} y2={y(B.g_relative.SOLID)} />
        <Mark x={x(B.x_LIQUID)} y={y(B.g_relative.LIQUID)} r={5} className="mark-liquid" />
        <Mark x={x(B.x_SOLID)} y={y(B.g_relative.SOLID)} r={5} className="mark-solid" />
        <Mark x={x(z)} y={y(ans.homogeneous_GM_relative.SOLID)} r={4} className="mark-solid" />
        <Mark x={x(z)} y={y(B.GM_relative)} r={6} className="mark-min" label="split" />
      </>}
    </EnergyPlot>;
    right = <PycalphadAnswer data={data} samples top={top} />;
    controls = <>
      <label id="scratch-brute" className="control-label">Trial solid composition <strong>{B.x_SOLID.toFixed(2)}</strong></label>
      <RecordSlider index={ib} max={data.brute.length - 1} onChange={setIb} labelId="scratch-brute" valueText={`solid ${B.x_SOLID.toFixed(2)}`} />
      <div className="control-row"><Player index={ib} max={data.brute.length - 1} onChange={setIb} label="Try every split" interval={260} /></div>
      <p className="caption">Trial solid 0.41–0.60 in steps of 0.01; liquid partners 0.001–0.399 in steps of 0.001 · z = {z.toFixed(2)}, {T_K} K.</p>
    </>;
    side = <dl className="readouts">
      <Readout label="Trial solid x · best liquid x" value={`${B.x_SOLID.toFixed(2)} · ${B.x_LIQUID.toFixed(3)}`} />
      <Readout label="Liquid amount (lever rule)" value={B.f_LIQUID.toFixed(4)} tone="liquid" />
      <Readout label="Above the answer" value={num(B.GM_relative, 3)} unit="J/mol" />
      <Readout label="Split energy" value={num(B.GM, 3)} unit="J/mol atoms" tone="min" />
      <Readout label={`Lowest so far (solid ${bestSoFar.x_SOLID.toFixed(2)})`} value={num(bestSoFar.GM, 3)} unit="J/mol atoms" />
      <Readout label="All solid at z (for comparison)" value={num(ans.homogeneous_GM.SOLID, 3)} unit="J/mol atoms" tone="solid" />
      <Readout label="pycalphad" value={num(pyc.GM, 3)} unit="J/mol atoms" />
    </dl>;
    status = `trial solid ${B.x_SOLID.toFixed(2)}, split energy ${num(B.GM, 1)} J/mol`;
  } else if (method === 'grid') {
    const two = G.chosen.length === 2, solid = G.chosen.find(c => c.phase === 'SOLID'), liquid = G.chosen.find(c => c.phase === 'LIQUID');
    left = <EnergyPlot data={data} top={top} title={`From scratch: grid spacing 1/${Math.round(1 / G.spacing)}`} desc="Grid points on both curves; the chosen candidates are marked and joined; the gold marker is the grid energy at z.">
      {({ x, y }) => <>
        {(['SOLID', 'LIQUID'] as const).map(phase => G.x.map((v, i) => <circle key={`${phase}${i}`} className={`grid-dot dot-${phase.toLowerCase()}`} cx={x(v)} cy={y(G.g_relative[phase][i])} r="3" />))}
        {two && <line className="chord" x1={x(liquid!.x)} y1={y(liquid!.g_relative)} x2={x(solid!.x)} y2={y(solid!.g_relative)} />}
         {G.chosen.map((c, i) => <Mark key={`${c.phase}${i}`} x={x(c.x)} y={y(c.g_relative)} r={5} className={`mark-${c.phase.toLowerCase()}`} />)}
        <Mark x={x(z)} y={y(G.GM_relative)} r={6} className="mark-min" label={two ? 'split' : 'one phase'} />
      </>}
    </EnergyPlot>;
    right = <PycalphadAnswer data={data} samples top={top} />;
    controls = <>
      <label id="scratch-grid" className="control-label">Grid spacing <strong>1/{Math.round(1 / G.spacing)}</strong></label>
      <RecordSlider index={ig} max={data.grid.length - 1} onChange={setIg} labelId="scratch-grid" valueText={`spacing 1/${Math.round(1 / G.spacing)}`} />
      <div className="control-row"><Player index={ig} max={data.grid.length - 1} onChange={setIg} label="Refine the grid" interval={900} /></div>
      <p className="caption">Grids 1/5 to 1/1000; points are drawn up to 1/100 · pycalphad evaluates {data.pycalphad.sample.SOLID.count} compositions per phase (every {data.pycalphad.sample_every}th in this window drawn).</p>
    </>;
    side = <dl className="readouts">
      <Readout label="Points per phase" value={G.points} />
      <Readout label="Chosen candidates" value={G.chosen.map(c => `${c.phase} x ${c.x.toFixed(3)}, amount ${c.f.toFixed(3)}`).join(' + ')} />
      <Readout label="Grid energy" value={num(G.GM, 3)} unit="J/mol atoms" tone="min" />
      <Readout label="Above the exact answer" value={num(G.above_exact, 4)} unit="J/mol" />
      <Readout label="pycalphad" value={num(pyc.GM, 3)} unit="J/mol atoms" />
    </dl>;
    status = `grid 1 over ${Math.round(1 / G.spacing)}: ${two ? 'split' : 'one phase'}, ${num(G.above_exact, 3)} J/mol above the exact answer`;
  } else if (method === 'newton') {
    const res = Math.max(Math.abs(N.residual_mu_A), Math.abs(N.residual_mu_B));
    left = <EnergyPlot data={data} top={top} title={`From scratch: Newton step ${N.iteration}`} desc="Tangent to the solid curve at its current composition (blue) and to the liquid curve (orange); they merge into one common tangent.">
      {({ x, y }) => <>
        <line className="tangent-phase tangent-solid-phase" x1={x(0)} y1={y(N.tangent_relative.SOLID[0])} x2={x(1)} y2={y(N.tangent_relative.SOLID[1])} />
        <line className="tangent-phase tangent-liquid-phase" x1={x(0)} y1={y(N.tangent_relative.LIQUID[0])} x2={x(1)} y2={y(N.tangent_relative.LIQUID[1])} />
        <Mark x={x(N.x_LIQUID)} y={y(N.g_relative.LIQUID)} r={5} className="mark-liquid" />
        <Mark x={x(N.x_SOLID)} y={y(N.g_relative.SOLID)} r={5} className="mark-solid" />
      </>}
    </EnergyPlot>;
    right = <PycalphadAnswer data={data} samples={false} top={top} />;
    controls = <>
      <label id="scratch-newton" className="control-label">Newton step <strong>{N.iteration}</strong></label>
      <RecordSlider index={inw} max={data.newton.frames.length - 1} onChange={setIn} labelId="scratch-newton" valueText={`step ${N.iteration}`} />
      <div className="control-row"><Player index={inw} max={data.newton.frames.length - 1} onChange={setIn} label="Newton steps" interval={1100} /></div>
      <p className="caption">First guess: solid {data.newton.start[0].toFixed(2)}, liquid {data.newton.start[1].toFixed(2)} · each step replaces the two equations by straight lines and solves those.</p>
    </>;
    side = <dl className="readouts">
      <Readout label="Solid x · liquid x" value={`${N.x_SOLID.toFixed(6)} · ${N.x_LIQUID.toFixed(6)}`} />
      <Readout label={<>Mismatch μ(solid) − μ(liquid), for A · B</>} value={`${num(N.residual_mu_A, 3)} · ${num(N.residual_mu_B, 3)}`} unit="J/mol" />
      <Readout label="Distance to pycalphad (solid x)" value={sci(N.x_SOLID - pyc.x_SOLID)} />
      <Readout label="pycalphad solid x · liquid x" value={`${pyc.x_SOLID.toFixed(6)} · ${pyc.x_LIQUID.toFixed(6)}`} />
    </dl>;
    status = `Newton step ${N.iteration}: largest mismatch ${num(res, 3)} J/mol`;
  } else {
    const p = pycLens.get(W.T_K);
    const lensPlot = (title: string, desc: string, rows: { T_K: number; x_SOLID: number; x_LIQUID: number }[], mark: 'ours' | 'pyc') =>
      <Plot compact title={title} desc={desc} height={300} xDomain={[0, 1]} yDomain={lensT} xLabel="B atom fraction" yLabel="T (K)" yFormat={value => `${value}`}>
        {({ x, y, left: l, right: r }) => <>
          <circle className="gap-point" cx={x(0)} cy={y(data.conditions.melting_K.A)} r="3.5" /><circle className="gap-point" cx={x(1)} cy={y(data.conditions.melting_K.B)} r="3.5" />
          <text className="hatch-label" x={x(0) + 6} y={y(data.conditions.melting_K.A) - 6}>A melts</text>
          <text className="hatch-label" x={x(1) - 6} y={y(data.conditions.melting_K.B) + 14} textAnchor="end">B melts</text>
          {rows.map(row => <g key={row.T_K}>
            <circle className={`lens-dot dot-liquid ${mark}`} cx={x(row.x_LIQUID)} cy={y(row.T_K)} r="2.8" />
            <circle className={`lens-dot dot-solid ${mark}`} cx={x(row.x_SOLID)} cy={y(row.T_K)} r="2.8" />
          </g>)}
          <g className="glide" style={{ transform: `translateY(${y(W.T_K).toFixed(2)}px)` }}><line className="cursor" x1={l} x2={r} y1={0} y2={0} /></g>
          {mark === 'ours' ? <line className="tie" x1={x(W.x_LIQUID)} x2={x(W.x_SOLID)} y1={y(W.T_K)} y2={y(W.T_K)} />
            : p && <line className="tie" x1={x(p.x_LIQUID)} x2={x(p.x_SOLID)} y1={y(W.T_K)} y2={y(W.T_K)} />}
          <text className="hatch-label" x={x(0.15)} y={y(1700)}>LIQUID</text>
          <text className="hatch-label" x={x(0.75)} y={y(1150)}>SOLID</text>
        </>}
      </Plot>;
    left = lensPlot(`From scratch: ${W.T_K} K (solve ${iw + 1} of ${data.continuation.length})`, 'Liquidus and solidus points found so far by continuation, with the current tie line.', walked, 'ours');
    right = lensPlot(`pycalphad: ${W.T_K} K`, 'pycalphad equilibrium at the same temperatures, with its tie line.', walked.map(row => pycLens.get(row.T_K)!).filter(Boolean), 'pyc');
    controls = <>
      <label id="scratch-walk" className="control-label">Temperature <strong>{W.T_K} K</strong></label>
      <RecordSlider index={iw} max={data.continuation.length - 1} onChange={setIw} labelId="scratch-walk" valueText={`${W.T_K} kelvin`} />
      <div className="control-row"><Player index={iw} max={data.continuation.length - 1} onChange={setIw} label="Walk through temperature" interval={120} /></div>
      <p className="caption">1400 → 1790 K, then 1390 → 1010 K, in 10 K steps · each solve starts from the previous answer.</p>
    </>;
    side = <dl className="readouts">
      <Readout label="Liquid x (liquidus)" value={W.x_LIQUID.toFixed(6)} tone="liquid" />
      <Readout label="Solid x (solidus)" value={W.x_SOLID.toFixed(6)} tone="solid" />
      {p && <Readout label="pycalphad liquid x · solid x" value={`${p.x_LIQUID.toFixed(6)} · ${p.x_SOLID.toFixed(6)}`} />}
      <Readout label="Largest difference over the whole lens" value={sci(data.difference.lens_max_x)} />
    </dl>;
    status = `${W.T_K} K: liquid ${W.x_LIQUID.toFixed(3)}, solid ${W.x_SOLID.toFixed(3)}`;
  }

  const rows: [ReactNode, number, number, number][] = [
    [<>Solid composition x<sub>S</sub></>, ans.x_SOLID, pyc.x_SOLID, 6], [<>Liquid composition x<sub>L</sub></>, ans.x_LIQUID, pyc.x_LIQUID, 6], [<>Liquid amount f<sub>L</sub></>, ans.f_LIQUID, pyc.f_LIQUID, 6],
    ['Gibbs energy G (J/mol atoms)', ans.GM, pyc.GM, 4], [<>μ<sub>A</sub> (J/mol)</>, ans.mu_A, pyc.mu_A, 4], [<>μ<sub>B</sub> (J/mol)</>, ans.mu_B, pyc.mu_B, 4]];
  return <div className="lab-grid">
    <div className="lab-main">
      <Segmented label="Method" value={method} onChange={setMethod} options={[['brute', '1 · Try every split'], ['grid', '2 · Grid + linear programme'], ['newton', '3 · Equal μ: Newton'], ['walk', '4 · The lens, step by step']]} />
      <p className="how-to"><strong>How to read it:</strong> {method !== 'walk' && 'Both plots show g measured from the final common tangent, so the answer lies on the dashed grey line at 0; the faint vertical line marks the sample, z = 0.40. Zoom in to see differences of a few J/mol. '}{intro[method]}</p>
      {method !== 'walk' && <Segmented label="Vertical scale" value={zoom} onChange={setZoom} options={[['close', 'Zoom: 0–150 J/mol'], ['wide', 'Wide: 0–800 J/mol']]} />}
      <div className="twin scratch-twin"><div><p className="twin-head">From scratch (numpy/SciPy)</p>{left}</div><div><p className="twin-head">pycalphad</p>{right}</div></div>
      <div className="control-bar">{controls}</div>
      <table className="data-table">
        <caption>{T_K} K, z = {z.toFixed(2)}: the answer both ways (pycalphad {data.pycalphad.version})</caption>
        <thead><tr><th scope="col">Quantity</th><th scope="col">From scratch</th><th scope="col">pycalphad</th><th scope="col">Size of difference</th></tr></thead>
        <tbody>{rows.map(([label, ours, theirs, digits], i) => <tr key={i}><th scope="row">{label}</th><td>{fixed(ours, digits)}</td><td>{fixed(theirs, digits)}</td><td>{sci(ours - theirs)}</td></tr>)}</tbody>
      </table>
    </div>
    <aside className="lab-side">
      <LiveStatus text={status} />
      <p className="lab-kicker">Part D · {T_K} K, z = {z.toFixed(2)}</p>
      <p className="big-number">{method === 'walk' ? <>{W.T_K}<span> K</span></> : method === 'newton' ? <>step {N.iteration}</> : method === 'grid' ? <>1/{Math.round(1 / G.spacing)}</> : <>x<sub>S</sub> {B.x_SOLID.toFixed(2)}</>}</p>
      {side}
    </aside>
  </div>;
}
