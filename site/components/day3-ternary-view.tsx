'use client';
/** Advanced step 18 (optional): the lens with a third component on a triangle. */
import { useEffect, useMemo, useState } from 'react';
import RecordSlider from '@/components/record-slider';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';

export type TernaryView = 'triangle' | 'landscape' | 'harder';
export const ternaryPath = 'self_study/generated/day3_ternary.json';
type Used = { phase: string; x: number[]; f: number };
export type Ternary = {
  schema_version: 1; conditions: { T_K: number; z: number[] }; K: number[];
  edges: { 'A-B': number[]; 'C-B': number[] };
  rachford_rice: { V: number; x_SOLID: number[]; x_LIQUID: number[]; G: number };
  menu: { n: number; x: number[][]; g: Record<string, number[]>; used: Used[]; G_up: number; mu: number[] };
  rounds: { k: number; G_up: number; mu: number[]; best: string; dips: Record<string, { x: number[]; depth: number }>; G_low: number; remaining: number }[];
  final: { used: Used[]; mu: number[]; G_up: number };
  landscape: { n: number; x: number[][]; menu_plane: Record<string, number[]>; final_plane: Record<string, number[]> };
  harder: { omega_AC_J_per_mol: number; tangent_at: number[]; mu: number[]; gap: number[]; deepest: { x: number[]; depth: number } };
};

const W = 420, H = 380, PAD = 30, SIDE = W - 2 * PAD;
/** (A, B, C) fractions to the picture: A bottom left, B bottom right, C at the top. */
const at = (x: number[]) => [PAD + SIDE * (x[1] + x[2] / 2), H - PAD - SIDE * x[2] * Math.sqrt(3) / 2] as const;
const pts = (xs: number[][]) => xs.map(x => at(x).map(v => v.toFixed(1)).join(',')).join(' ');
/** Signed, compressed colour for a gap value: red below zero, blue above. */
const colour = (v: number, scale: number) => {
  const t = Math.sign(v) * Math.min(1, Math.log10(1 + Math.abs(v)) / Math.log10(1 + scale));
  return t < 0 ? `hsl(12 75% ${92 + t * 40}%)` : `hsl(220 55% ${92 - t * 45}%)`;
};

export default function Day3TernaryView({ initialView = 'triangle', kicker }: { initialView?: TernaryView; kicker?: string }) {
  const [data, setData] = useState<Ternary | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<Ternary>(ternaryPath).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the ternary data…</p>;
  return <Day3TernaryLab data={data} initialView={initialView} kicker={kicker} />;
}

export function Day3TernaryLab({ data, initialView = 'triangle', kicker = 'Interactive lab' }: { data: Ternary; initialView?: TernaryView; kicker?: string }) {
  const [view, setView] = useState<TernaryView>(initialView);
  const body = view === 'triangle' ? <Triangle data={data} /> : view === 'landscape' ? <Landscape data={data} /> : <Harder data={data} />;
  return <LabFrame kicker={kicker} title="Three components on a triangle"
    conditions={['1400 K', `z = (${data.conditions.z.map(v => v.toFixed(2)).join(', ')})`, 'ideal SOLID and LIQUID', 'C is invented']}
    actions={<Segmented label="Lab view" value={view} onChange={setView} options={[['triangle', 'Menu and plane'], ['landscape', 'Landscape'], ['harder', 'What gets harder']]} />}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes"><p>The lens of step 03 part C with an invented third component C (solid 1500 − 12T, liquid 9000 − 18T J/mol), ideal in both phases. All values were calculated in advance with the course code; the lab draws them.</p></div>}
    record={<RecordView value={{ K: data.K, rachford_rice: data.rachford_rice, menu_used: data.menu.used, menu_mu: data.menu.mu, final: data.final }} href="/learning/self_study/generated/day3_ternary.json" note="The numbers behind these views." />} />;
}

function Frame({ children, label }: { children: React.ReactNode; label: string }) {
  const corners = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  return <svg className="ternary" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
    <polygon className="ternary-frame" points={pts(corners)} />
    {children}
    {(['A', 'B', 'C'] as const).map((c, i) => { const [x, y] = at(corners[i]); return <text key={c} className="edge-flag" x={x + (i === 0 ? -14 : i === 1 ? 6 : -4)} y={y + (i === 2 ? -8 : 16)}>{c}</text>; })}
  </svg>;
}

function Triangle({ data }: { data: Ternary }) {
  const [phase, setPhase] = useState<'both' | 'SOLID' | 'LIQUID'>('both');
  const used = data.menu.used, z = data.conditions.z, mu = data.menu.mu;
  const height = z[0] * mu[0] + z[1] * mu[1] + z[2] * mu[2];
  const rr = data.rachford_rice;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the menu&apos;s dots on the triangle (both phase models share the grid), the sample as a star, and the three used dots joined into a small tie triangle. The true tie line, from the Rachford–Rice control, runs through the sample.</p>
      <Segmented label="Dots shown" value={phase} onChange={setPhase} options={[['both', 'Both'], ['SOLID', 'SOLID'], ['LIQUID', 'LIQUID']]} />
      <Frame label="The menu's dots on the composition triangle, the tie triangle of the used dots and the true tie line">
        {data.menu.x.map((x, i) => { const [cx, cy] = at(x); return <circle key={i} className={`tri-dot ${phase === 'LIQUID' ? 'is-liquid' : phase === 'SOLID' ? 'is-solid' : ''}`} cx={cx} cy={cy} r={2.2} />; })}
        <polygon className="tie-triangle" points={pts(used.map(u => u.x))} />
        {used.map((u, i) => { const [cx, cy] = at(u.x); return <circle key={`u${i}`} className={`dot dot-${u.phase === 'SOLID' ? 'solid' : 'liquid'} is-chosen`} cx={cx} cy={cy} r={6} />; })}
        <line className="tie" x1={at(rr.x_SOLID)[0]} y1={at(rr.x_SOLID)[1]} x2={at(rr.x_LIQUID)[0]} y2={at(rr.x_LIQUID)[1]} />
        <text className="edge-flag" x={at(z)[0] + 8} y={at(z)[1] - 6}>★ z</text>
      </Frame>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Menu: ${used.length} used dots, ceiling ${num(data.menu.G_up, 2)}`} />
      <p className="lab-kicker">The menu&apos;s answer</p>
      <dl className="readouts">
        {used.map((u, i) => <Readout key={i} label={`${u.phase} (${u.x.map(v => v.toFixed(3)).join(', ')})`} value={u.f.toFixed(3)} unit="of the sample" tone={u.phase === 'SOLID' ? 'solid' : 'liquid'} />)}
        <Readout label="Ceiling" value={num(data.menu.G_up, 2)} unit="J/mol atoms" tone="min" />
        <Readout label="Plane heights μA, μB, μC" value={mu.map(v => num(v, 1)).join(' · ')} unit="J/mol" />
        <Readout label="Plane at the sample" value={num(height, 2)} unit="J/mol atoms" />
        <Readout label="True split: liquid amount V" value={rr.V.toFixed(3)} />
      </dl>
    </aside>
  </div>;
}

/** Small triangles of the landscape grid, coloured by the mean gap of their corners. */
function useCells(n: number) {
  return useMemo(() => {
    const index: number[][] = [];
    let k = 0;
    for (let i = 0; i <= n; i++) { index.push([]); for (let j = 0; j <= n - i; j++) index[i].push(k++); }
    const cells: number[][] = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < n - i; j++) {
      cells.push([index[i][j], index[i + 1][j], index[i][j + 1]]);
      if (j + 1 <= n - i - 1) cells.push([index[i + 1][j], index[i + 1][j + 1], index[i][j + 1]]);
    }
    return cells;
  }, [n]);
}

function GapMap({ xs, gap, n, scale, label, marks }: { xs: number[][]; gap: number[]; n: number; scale: number; label: string; marks?: React.ReactNode }) {
  const cells = useCells(n);
  return <Frame label={label}>
    {cells.map((c, i) => <polygon key={i} points={pts(c.map(k => xs[k]))} style={{ fill: colour((gap[c[0]] + gap[c[1]] + gap[c[2]]) / 3, scale) }} />)}
    {marks}
  </Frame>;
}

function Landscape({ data }: { data: Ternary }) {
  const rounds = data.rounds, [k, setK] = useState(0), [phase, setPhase] = useState<'SOLID' | 'LIQUID'>('SOLID'), r = rounds[k];
  const xs = data.landscape.x;
  const gap = useMemo(() => xs.map((x, i) => gapAt(data, phase, x, i, r.mu)), [data, phase, xs, r.mu]);
  const dip = r.dips[phase];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the gap of one phase model against the plane of the chosen round, coloured: red below the plane (a missing state), blue above it. The ring marks that phase model&apos;s deepest point. Step through the rounds and watch the red shrink.</p>
      <Segmented label="Phase model" value={phase} onChange={setPhase} options={[['SOLID', 'SOLID'], ['LIQUID', 'LIQUID']]} />
      <GapMap xs={xs} gap={gap} n={data.landscape.n} scale={3000} label={`Gap landscape of ${phase} against the plane of round ${k}`}
        marks={<><circle className="tri-ring" cx={at(dip.x)[0]} cy={at(dip.x)[1]} r={7} /><text className="edge-flag" x={at(data.conditions.z)[0] + 8} y={at(data.conditions.z)[1] - 6}>★ z</text></>} />
      <div className="control-bar">
        <label id="d3-tri-round" className="control-label">Round <strong>{k}</strong></label>
        <RecordSlider index={k} max={rounds.length - 1} onChange={setK} labelId="d3-tri-round" valueText={`round ${k}`} />
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Round ${k}: remaining ${num(r.remaining, 4)}`} />
      <dl className="readouts">
        <Readout label="Ceiling" value={num(r.G_up, 3)} unit="J/mol atoms" tone="min" />
        <Readout label={`${phase} deepest dip`} value={num(dip.depth, 3)} unit="J/mol atoms" />
        <Readout label="Remaining uncertainty" value={num(r.remaining, 4)} unit="J/mol atoms" />
        <Readout label="Plane μA, μB, μC" value={r.mu.map(v => num(v, 1)).join(' · ')} unit="J/mol" />
      </dl>
    </aside>
  </div>;
}

/** Gap of a phase at landscape point i against a plane: exported energies minus the plane (display arithmetic). */
function gapAt(data: Ternary, phase: string, x: number[], i: number, mu: number[]): number {
  const g0 = data.landscape.menu_plane[phase][i] + (x[0] * data.menu.mu[0] + x[1] * data.menu.mu[1] + x[2] * data.menu.mu[2]);
  return g0 - (x[0] * mu[0] + x[1] * mu[1] + x[2] * mu[2]);
}

function Harder({ data }: { data: Ternary }) {
  const h = data.harder;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the liquid with an A–C interaction (Ω = {h.omega_AC_J_per_mol} J/mol) against its tangent plane at an A-rich composition. The landscape is zero there and rises nearby, so a local search stays put; a full scan finds the hidden valley on the C-rich side.</p>
      <GapMap xs={data.landscape.x} gap={h.gap} n={data.landscape.n} scale={3000} label="Gap landscape of the liquid with an A–C interaction against its tangent plane at an A-rich point"
        marks={<><circle className="tri-ring" cx={at(h.tangent_at)[0]} cy={at(h.tangent_at)[1]} r={7} /><circle className="tri-ring is-deep" cx={at(h.deepest.x)[0]} cy={at(h.deepest.x)[1]} r={7} /></>} />
    </div>
    <aside className="lab-side">
      <dl className="readouts">
        <Readout label="Tangent point" value={`(${h.tangent_at.map(v => v.toFixed(2)).join(', ')})`} />
        <Readout label="Hidden valley" value={`(${h.deepest.x.map(v => v.toFixed(2)).join(', ')})`} />
        <Readout label="Its depth" value={num(h.deepest.depth, 1)} unit="J/mol atoms" tone="min" />
      </dl>
      <p className="caption">Checking that no valley is left needs floors on pieces of the triangle; a uniform grid of spacing h has about (1/h)<sup>d</sup>/d! of them, and the number still grows steeply with the number of components.</p>
    </aside>
  </div>;
}
