'use client';
import { useEffect, useState } from 'react';
import Plot, { Mark, path, ticks } from '@/components/plot';
import RecordSlider from '@/components/record-slider';
import { LiveStatus, Readout, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';

type Case = { delta: number; theta: number; phi: number; gs_theta: number; gs: number[]; parallel_tangent: [number, number] };
type Reservoir = { x_b: number; mu_A: number; mu_B: number; gb_x_b: number; cases: Case[] };
export type BoundaryViewsData = { x: number[]; gb: number[]; reservoirs: Reservoir[];
  iteration: { x0: number; theta0: number; delta: number; B_total: number; steps: { k: number; x_b_used: number; theta: number; boundary_B: number; bulk_B: number }[]; closed_theta_direct: number; closed_theta_root: number } };
export const boundaryViewsPath = 'self_study/generated/boundary_views.json';

export default function BoundaryViews({ mode }: { mode: 'tangent' | 'iteration' }) {
  const [data, setData] = useState<BoundaryViewsData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<BoundaryViewsData>(boundaryViewsPath).then(v => { if (active) setData(v); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading…</p>;
  return mode === 'tangent' ? <TangentPicture data={data} /> : <HandIteration data={data} />;
}

/** The open boundary as a tangent picture: reservoir line, tilted boundary curve, and phi as the vertical gap. Exported values only. */
export function TangentPicture({ data }: { data: BoundaryViewsData }) {
  const [ir, setIr] = useState(0), [id, setId] = useState(10);
  const res = data.reservoirs[ir], c = res.cases[id];
  const all = [...data.gb, ...c.gs, res.mu_A, res.mu_B], lo = Math.min(...all), hi = Math.max(...all), pad = (hi - lo) * 0.06;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the dark curve is the bulk g<sub>b</sub>; the gold line is its tangent at the reservoir composition, ending at μ<sub>A</sub> and μ<sub>B</sub>. The violet curve is the boundary g<sub>s</sub> = g<sub>b</sub> + δθ. The boundary settles where a line parallel to the gold one touches g<sub>s</sub>; the grand potential φ is the vertical gap there between g<sub>s</sub> and the gold line.</p>
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
        <Readout label="Grand potential φ (vertical gap)" value={num(c.phi)} unit="J/mol boundary sites" tone="min" />
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
      <button type="button" className="ghost-button" onClick={() => setK(Math.min(it.steps.length, k + 1))} disabled={k >= it.steps.length}>Next round</button>
      <button type="button" className="ghost-button" onClick={() => setK(1)}>Start again</button>
    </div>
    <p className="caption">{k >= it.steps.length ? `Settled: θ ≈ ${it.steps.at(-1)!.theta.toFixed(5)}. The saved closed result is ${it.closed_theta_root.toFixed(8)} (exchange condition) and ${it.closed_theta_direct.toFixed(8)} (direct minimum).` : 'Boundary B plus bulk B always adds up to the fixed total; only how it is split changes.'}</p>
  </div>;
}
