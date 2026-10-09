'use client';
import { useEffect, useState } from 'react';
import Plot, { Mark, path, ticks } from '@/components/plot';
import RecordSlider from '@/components/record-slider';
import { LiveStatus, Readout, Segmented, Stepper } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';

type Case = { delta: number; theta: number; phi: number; gs_theta: number; gs: number[]; parallel_tangent: [number, number] };
type Reservoir = { x_b: number; mu_A: number; mu_B: number; gb_x_b: number; cases: Case[] };
export type BoundaryViewsData = { x: number[]; gb: number[]; reservoirs: Reservoir[];
  iteration: { x0: number; theta0: number; delta: number; B_total: number; steps: { k: number; x_b_used: number; theta: number; boundary_B: number; bulk_B: number }[]; closed_theta_direct: number; closed_theta_root: number };
  closed_match: { delta: number; x_scan: number[]; theta_open: number[]; x_b_closed: number; theta_closed: number; exchange_price: number } };
export const boundaryViewsPath = 'self_study/generated/boundary_views.json';

export default function BoundaryViews({ mode }: { mode: 'tangent' | 'iteration' | 'match' }) {
  const [data, setData] = useState<BoundaryViewsData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<BoundaryViewsData>(boundaryViewsPath).then(v => { if (active) setData(v); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading…</p>;
  return mode === 'tangent' ? <TangentPicture data={data} /> : mode === 'match' ? <ClosedMatch data={data} /> : <HandIteration data={data} />;
}

/** Which reservoir makes the open boundary hold what the closed cell holds? Exported scan only. */
export function ClosedMatch({ data }: { data: BoundaryViewsData }) {
  const m = data.closed_match, [i, setI] = useState(0), x = m.x_scan[i], theta = m.theta_open[i];
  const close = Math.abs(x - m.x_b_closed) < 0.00026;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> move the reservoir composition until the open boundary holds as much B as the closed cell does (θ = {m.theta_closed.toFixed(4)}). The reservoir you find is the closed cell&apos;s own final bulk: the closed cell behaves like an open one whose price of B is set so that every atom stays in the box.</p>
      <Plot title="Open boundary occupancy against the reservoir composition" desc="The open boundary's B occupancy for each reservoir composition, the closed cell's occupancy as a horizontal line, and the selected reservoir." height={300}
        xDomain={[m.x_scan[0], m.x_scan.at(-1)!]} yDomain={[Math.min(...m.theta_open) - 0.002, Math.max(...m.theta_open) + 0.002]} xLabel="reservoir B fraction x_b" yLabel="open occupancy θ" xFormat={v => v.toFixed(3)} yFormat={v => v.toFixed(3)}>
        {({ x: X, y: Y, left, right, top, bottom }) => <>
          <line className="tangent" x1={left} x2={right} y1={Y(m.theta_closed)} y2={Y(m.theta_closed)} />
          <line className="ghost" x1={X(m.x_b_closed)} x2={X(m.x_b_closed)} y1={top} y2={bottom} />
          <path className="line line-gs" d={path(m.x_scan.map((v, k) => [X(v), Y(m.theta_open[k])]))} />
          <Mark x={X(x)} y={Y(theta)} r={6} className={close ? 'mark-min' : 'mark-gs'} label="θ" />
        </>}
      </Plot>
      <div className="control-bar">
        <label id="match-label" className="control-label">Reservoir composition <strong>{x.toFixed(4)}</strong></label>
        <RecordSlider index={i} max={m.x_scan.length - 1} onChange={setI} labelId="match-label" valueText={`reservoir ${x.toFixed(4)}`} />
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`reservoir ${x.toFixed(4)}: open theta ${theta.toFixed(4)}`} />
      <dl className="readouts">
        <Readout label="Open occupancy at this reservoir" value={theta.toFixed(5)} tone="key" />
        <Readout label="Closed cell's occupancy" value={m.theta_closed.toFixed(5)} />
        <Readout label="Closed cell's final bulk" value={m.x_b_closed.toFixed(5)} />
        <Readout label="Price of the B balance, μB − μA there" value={num(m.exchange_price, 1)} unit="J/mol" tone="min" />
      </dl>
      <p className="caption">Optimisation reading: the open cell is the closed cell with its B balance priced instead of enforced (a Lagrangian relaxation); the right price makes both agree.</p>
    </aside>
  </div>;
}

/** The open boundary as a tangent picture: reservoir line, tilted boundary curve, and phi as the vertical gap. Exported values only. */
export function TangentPicture({ data }: { data: BoundaryViewsData }) {
  const [ir, setIr] = useState(0), [id, setId] = useState(10);
  const res = data.reservoirs[ir], c = res.cases[id];
  const all = [...data.gb, ...c.gs, res.mu_A, res.mu_B], lo = Math.min(...all), hi = Math.max(...all), pad = (hi - lo) * 0.06;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the dark curve is the bulk g<sub>b</sub>; the gold line is its tangent at the reservoir composition, ending at μ<sub>A</sub> and μ<sub>B</sub>: the reservoir&apos;s price line. The violet curve is the boundary g<sub>s</sub> = g<sub>b</sub> + δθ. The boundary settles where a line parallel to the gold one touches g<sub>s</sub>; the grand potential φ is the gap there between g<sub>s</sub> and the reservoir&apos;s price line. (Optimisation reading: φ is the boundary&apos;s reduced cost at the reservoir&apos;s prices.)</p>
      <div className="legend-row"><Segmented label="Reservoir composition" value={String(ir)} onChange={v => setIr(Number(v))} options={data.reservoirs.map((r, i) => [String(i), `x_b = ${r.x_b.toFixed(2)}`] as [string, string])} /></div>
      <Plot title="Bulk curve, reservoir tangent and boundary curve" desc="Bulk g_b, its tangent at the reservoir composition, the tilted boundary curve g_s, and the parallel line touching it at the boundary occupancy."
        height={340} xDomain={[0, 1]} yDomain={[lo - pad, hi + pad]} yTicks={ticks(lo - pad, hi + pad, 5)} xLabel="B fraction (x for the bulk, θ for the boundary)" yLabel="g (kJ/mol sites)" yFormat={v => num(v / 1000, 0)}>
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
      <div className="control-bar">
        <label id="delta-label" className="control-label">Boundary preference δ <strong>{num(c.delta)} J/mol</strong></label>
        <RecordSlider index={id} max={res.cases.length - 1} onChange={setId} labelId="delta-label" valueText={`delta ${c.delta} joule per mole of boundary sites`} />
        <p className="caption">−10000 to +5000 J/mol boundary sites in steps of 500 · δ = 0 gives θ = x<sub>b</sub>; negative δ pulls B to the boundary, positive δ pushes it out.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`delta ${c.delta}: theta ${c.theta.toFixed(4)}, phi ${num(c.phi)}`} />
      <p className="lab-kicker">Open cell at x_b = {res.x_b.toFixed(2)}</p>
      <p className="big-number">θ = {c.theta.toFixed(3)}</p>
      <dl className="readouts">
        <Readout label="Boundary occupancy θ" value={c.theta.toFixed(6)} tone="key" />
        <Readout label="Bulk (reservoir) fraction" value={res.x_b.toFixed(2)} />
        <Readout label="φ: the gap to the reservoir's price line" value={num(c.phi)} unit="J/mol boundary sites" tone="min" />
      </dl>
    </aside>
  </div>;
}

/** Step-through of the narration's hand method for the closed cell. Exported iterates only. */
export function HandIteration({ data }: { data: BoundaryViewsData }) {
  const it = data.iteration, [k, setK] = useState(1), shown = it.steps.slice(0, k);
  return <div className="iteration">
    <p className="how-to"><strong>How it works:</strong> start with the bulk fraction x<sub>b</sub> = x<sub>0</sub> = {it.x0}. Use the odds formula to get θ, then put the B that went to the boundaries back into the count: x<sub>b</sub> = (B<sub>tot</sub> − 200θ)/8000 with B<sub>tot</sub> = {it.B_total}. Repeat.</p>
    <table className="data-table"><caption>Closed cell, δ = {num(it.delta)} J/mol boundary sites, θ<sub>0</sub> = {it.theta0}</caption>
      <thead><tr><th scope="col">Round</th><th scope="col">x_b used</th><th scope="col">θ from the odds formula</th><th scope="col">Boundary B</th><th scope="col">Bulk B</th></tr></thead>
      <tbody>{shown.map(s => <tr key={s.k}><th scope="row">{s.k}</th><td>{s.x_b_used.toFixed(6)}</td><td>{s.theta.toFixed(8)}</td><td>{num(s.boundary_B, 3)}</td><td>{num(s.bulk_B, 3)}</td></tr>)}</tbody></table>
    <div className="control-row">
      <Stepper index={k - 1} count={it.steps.length} onChange={i => setK(i + 1)} unit="round" label="Rounds of the iteration" />
      <button type="button" className="ghost-button" onClick={() => setK(1)}>Start again</button>
    </div>
    <p className="caption">{k >= it.steps.length ? `Settled: θ ≈ ${it.steps.at(-1)!.theta.toFixed(5)}. The saved closed result is ${it.closed_theta_root.toFixed(8)} (exchange condition) and ${it.closed_theta_direct.toFixed(8)} (direct minimum).` : 'Boundary B plus bulk B always adds up to the fixed total; only how it is split changes.'}</p>
  </div>;
}
