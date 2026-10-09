'use client';
/** Advanced steps 07–09: the second law, counting arrangements, building g(x) and the Ω bump. */
import { useEffect, useState } from 'react';
import Plot, { nearest, path } from '@/components/plot';
import RecordSlider, { ValueSlider } from '@/components/record-slider';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';

export type PreworkView = 'second-law' | 'counter' | 'builder' | 'omega';
export const preworkPath = 'self_study/generated/day3_prework.json';
export type Prework = {
  schema_version: 1;
  second_law: { model: string; frames: { T_K: number; dH: number; dS_sample: number; dS_bath: number; dS_total: number; dG: number }[] };
  counting: { N: number; k: number[]; lnW_per_N: number[]; limit: number[] }[];
  builder: { x: number[]; frames: { T_K: number; mixing: number[]; SOLID: { end_line: number[]; g: number[] }; LIQUID: { end_line: number[]; g: number[] } }[] };
  omega: { x: number[]; frames: { omega_over_RT: number; g_mix_over_RT: number[]; spinodal: number[]; binodal: number[] }[] };
};

const preworkOptions: [PreworkView, string][] = [['second-law', 'Second law'], ['counter', 'Count arrangements'], ['builder', 'Build g(x)'], ['omega', 'The Ω bump']];

export default function Day3PreworkView({ initialView = 'omega', kicker, views }: { initialView?: PreworkView; kicker?: string; views?: PreworkView[] }) {
  const [data, setData] = useState<Prework | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<Prework>(preworkPath).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the lab data…</p>;
  return <Day3PreworkLab data={data} initialView={initialView} kicker={kicker} views={views} />;
}

export function Day3PreworkLab({ data, initialView = 'omega', kicker = 'Interactive lab', views }: { data: Prework; initialView?: PreworkView; kicker?: string; views?: PreworkView[] }) {
  const [view, setView] = useState<PreworkView>(initialView);
  const shown = preworkOptions.filter(([id]) => !views || views.includes(id));
  const body = view === 'second-law' ? <SecondLaw data={data} /> : view === 'counter' ? <Counter data={data} /> : view === 'builder' ? <Builder data={data} /> : <OmegaBump data={data} />;
  return <LabFrame kicker={kicker} title={shown.length === 1 ? shown[0][1] : 'Energy, entropy and cost curves'}
    conditions={['invented models', 'per mole of atoms']}
    actions={shown.length > 1 ? <Segmented label="Lab view" value={view} onChange={setView} options={shown} /> : undefined}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes">
      <p>Second law: pure A of step 01 melting (solid 1000 − 10T, liquid 7000 − 16T J/mol). Counting: the exact number of arrangements of k B atoms on N sites. Building g(x): the lens of step 03 part C. The Ω bump: the mixing part of a regular solution, in units of RT.</p>
      <p>All values were calculated in advance with the course code; the lab draws them and multiplies by the melted fraction.</p>
    </div>}
    record={<RecordView value={{ second_law: data.second_law, omega_frames: data.omega.frames.map(({ omega_over_RT, spinodal, binodal }) => ({ omega_over_RT, spinodal, binodal })) }} href="/learning/self_study/generated/day3_prework.json" note="The numbers behind these views." />} />;
}

function SecondLaw({ data }: { data: Prework }) {
  const frames = data.second_law.frames, [i, setI] = useState(nearest(frames.map(f => f.T_K), 1100)), [melted, setMelted] = useState(0.5), f = frames[i];
  const bars: [string, number, string][] = [['sample', f.dS_sample * melted, 'solid'], ['bath', f.dS_bath * melted, 'liquid'], ['total', f.dS_total * melted, 'min']];
  const up = f.dS_total > 1e-12, flat = Math.abs(f.dS_total) <= 1e-12;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> melt part of a sample of pure A in a heat bath. The sample takes heat from the bath, so the bath loses entropy. Melting can only happen on its own if the total entropy rises, which is the same as G of the sample falling.</p>
      <svg className="bath-sketch" viewBox="0 0 360 150" role="img" aria-label="A sample inside a heat bath; heat flows from the bath into the sample when it melts">
        <rect className="bath" x="10" y="10" width="340" height="130" rx="14" /><text className="hatch-label" x="24" y="32">heat bath at {f.T_K} K</text>
        <rect className="sample" x="140" y="48" width="90" height="70" rx="8" /><rect className="sample-liquid" x="140" y={48 + 70 * (1 - melted)} width="90" height={70 * melted} rx="8" />
        <text className="hatch-label" x="185" y="136" textAnchor="middle">sample: {Math.round(melted * 100)}% liquid</text>
        {melted > 0 && <path className="heat-arrow" d="M60,84 L130,84" />}
      </svg>
      <Plot compact title="Entropy changes of sample, bath and total" desc="Bars for the entropy change of the sample, of the bath and their total for the chosen melted fraction." height={220}
        xDomain={[-0.5, 2.5]} yDomain={[-8, 8]} xLabel="" yLabel="J/(mol K)" xTicks={[]} yFormat={v => num(v, 0)}>
        {({ x, y }) => <>
          <line className="zero" x1={x(-0.5)} x2={x(2.5)} y1={y(0)} y2={y(0)} />
          {bars.map(([label, v, t], k) => <g key={label}><rect className={`entropy-bar bar-${t}`} x={x(k) - 28} width={56} y={Math.min(y(0), y(v))} height={Math.abs(y(v) - y(0))} />
            <text className="edge-flag" x={x(k)} y={y(0) + (v >= 0 ? 16 : -8)} textAnchor="middle">{label}</text></g>)}
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-T" className="control-label">Temperature <strong>{f.T_K} K</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="d3-T" valueText={`${f.T_K} K`} />
        <label id="d3-melted" className="control-label">Melted fraction <strong>{melted.toFixed(2)}</strong></label>
        <ValueSlider value={melted} min={0} max={1} step={0.05} onChange={setMelted} labelId="d3-melted" valueText={melted.toFixed(2)} />
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`${f.T_K} K: total entropy change ${num(f.dS_total * melted, 2)}, G change ${num(f.dG * melted, 0)}`} />
      <p className={`status-pill ${flat ? 'pill-equal' : up ? 'pill-solid' : 'pill-open'}`}>{flat ? 'Melting point: nothing changes' : up ? 'Total entropy up, G down: melting happens' : 'Total entropy would fall: no melting'}</p>
      <dl className="readouts">
        <Readout label="Heat taken by the sample, ΔH" value={num(f.dH * melted, 0)} unit="J/mol" />
        <Readout label="Sample entropy change" value={num(f.dS_sample * melted, 2)} unit="J/(mol K)" tone="solid" />
        <Readout label="Bath entropy change, −ΔH/T" value={num(f.dS_bath * melted, 2)} unit="J/(mol K)" tone="liquid" />
        <Readout label="Total entropy change" value={num(f.dS_total * melted, 3)} unit="J/(mol K)" tone="min" />
        <Readout label="ΔG of the sample" value={num(f.dG * melted, 0)} unit="J/mol" />
      </dl>
      <p className="caption">ΔG = −T × (total entropy change): one is positive exactly when the other is negative.</p>
    </aside>
  </div>;
}

/** A fixed, scrambled order of sites so that the first k positions look like one random arrangement. */
const order = (n: number) => Array.from({ length: n }, (_, i) => i).sort((a, b) => ((a * 7919) % n) - ((b * 7919) % n) || a - b);

function Counter({ data }: { data: Prework }) {
  const [ni, setNi] = useState(data.counting.findIndex(c => c.N === 100)), c = data.counting[ni];
  const [k, setK] = useState(Math.round(c.N * 0.4)), kk = Math.min(k, c.N), x = kk / c.N;
  const sites = order(Math.min(c.N, 100)), shown = Math.min(c.N, 100), filled = new Set(sites.slice(0, Math.round(x * shown)));
  const log10W = c.lnW_per_N[kk] * c.N / Math.LN10;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> put k B atoms on N sites. Count the arrangements W: ln W / N, the entropy per site in units of k<sub>B</sub>, approaches −[x ln x + (1−x) ln(1−x)] as N grows.</p>
      <div className="twin">
        <svg className="site-grid" viewBox="0 0 220 220" role="img" aria-label={`${shown} sites with ${filled.size} B atoms, one of the possible arrangements`}>
          {Array.from({ length: shown }, (_, i) => <circle key={i} cx={11 + (i % 10) * 22} cy={11 + Math.floor(i / 10) * 22} r={8} className={filled.has(i) ? 'site-b' : 'site-a'} />)}
        </svg>
        <Plot compact title="Entropy per site from counting, and its limit" desc="ln W / N for the chosen N against x = k/N, with the large-N limit." height={240}
          xDomain={[0, 1]} yDomain={[0, 0.75]} xLabel="x = k/N" yLabel="ln W / N" yFormat={v => v.toFixed(2)}>
          {({ x: X, y: Y }) => <>
            <path className="line line-reference" d={path(c.k.map((v, i) => [X(v / c.N), Y(c.limit[i])]))} />
            <path className="line line-solid" d={path(c.k.map((v, i) => [X(v / c.N), Y(c.lnW_per_N[i])]))} />
            <circle className="dot dot-min" cx={X(x)} cy={Y(c.lnW_per_N[kk])} r={6} />
          </>}
        </Plot>
      </div>
      <div className="control-bar">
        <Segmented label="Number of sites N" value={String(c.N)} onChange={v => { const j = data.counting.findIndex(r => String(r.N) === v); setNi(j); setK(Math.round(data.counting[j].N * x)); }}
          options={data.counting.map(r => [String(r.N), `N = ${r.N}`] as [string, string])} />
        <label id="d3-k" className="control-label">B atoms k <strong>{kk}</strong> (x = {x.toFixed(3)})</label>
        <RecordSlider index={kk} max={c.N} onChange={setK} labelId="d3-k" valueText={`k ${kk} of ${c.N}`} />
        {c.N > 100 && <p className="caption">The picture shows 100 of the {c.N} sites.</p>}
      </div>
    </div>
    <aside className="lab-side">
      <dl className="readouts">
        <Readout label="Arrangements W" value={`about 10^${log10W.toFixed(1)}`} />
        <Readout label="ln W / N (counted)" value={c.lnW_per_N[kk].toFixed(4)} tone="solid" />
        <Readout label="−[x ln x + (1−x) ln(1−x)]" value={c.limit[kk].toFixed(4)} />
      </dl>
      <p className="caption">Per mole of atoms the mixing entropy is R times this limit; −T times it is the mixing term of g(x).</p>
    </aside>
  </div>;
}

function Builder({ data }: { data: Prework }) {
  const frames = data.builder.frames, xs = data.builder.x, [i, setI] = useState(nearest(frames.map(f => f.T_K), 1400)), f = frames[i];
  const [phase, setPhase] = useState<'SOLID' | 'LIQUID'>('LIQUID'), part = f[phase];
  const all = [...part.end_line, ...part.g], lo = Math.min(...all), hi = Math.max(...all);
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> a cost curve is the straight line between the pure ends plus the mixing term. Move the temperature: the end line tilts and shifts, and the mixing term deepens.</p>
      <Segmented label="Phase model" value={phase} onChange={setPhase} options={[['SOLID', 'SOLID'], ['LIQUID', 'LIQUID']]} />
      <div className="twin">
        <Plot compact title={`${phase} at ${f.T_K} K: end line and g(x)`} desc="The straight line between the pure ends and the full curve g(x)." height={280}
          xDomain={[0, 1]} yDomain={[lo - 300, hi + 300]} xLabel="x" yLabel="J/mol atoms" yFormat={v => num(v / 1000, 1) + 'k'}>
          {({ x, y }) => <>
            <path className="line line-reference" d={path(xs.map((v, k) => [x(v), y(part.end_line[k])]))} />
            <path className={`line line-${phase === 'SOLID' ? 'solid' : 'liquid'}`} d={path(xs.map((v, k) => [x(v), y(part.g[k])]))} />
          </>}
        </Plot>
        <Plot compact title={`Mixing term at ${f.T_K} K`} desc="RT [x ln x + (1 − x) ln(1 − x)], the same for both phase models." height={280}
          xDomain={[0, 1]} yDomain={[-12000, 500]} xLabel="x" yLabel="J/mol atoms" yFormat={v => num(v / 1000, 0) + 'k'}>
          {({ x, y }) => <>
            <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
            <path className="line line-mixing" d={path(xs.map((v, k) => [x(v), y(f.mixing[k])]))} />
          </>}
        </Plot>
      </div>
      <div className="control-bar">
        <label id="d3-build" className="control-label">Temperature <strong>{f.T_K} K</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="d3-build" valueText={`${f.T_K} K`} />
      </div>
    </div>
    <aside className="lab-side">
      <dl className="readouts">
        <Readout label={`${phase} at x = 0 (pure A)`} value={num(part.g[0], 1)} unit="J/mol" />
        <Readout label={`${phase} at x = 1 (pure B)`} value={num(part.g[xs.length - 1], 1)} unit="J/mol" />
        <Readout label="Mixing term at x = 0.4" value={num(f.mixing[40], 1)} unit="J/mol atoms" />
        <Readout label={`${phase} g at x = 0.3`} value={num(part.g[30], 2)} unit="J/mol atoms" tone={phase === 'SOLID' ? 'solid' : 'liquid'} />
      </dl>
    </aside>
  </div>;
}

function OmegaBump({ data }: { data: Prework }) {
  const frames = data.omega.frames, xs = data.omega.x, day3 = nearest(frames.map(f => f.omega_over_RT), 3.0068), [i, setI] = useState(day3), f = frames[i];
  const [b0, b1] = f.binodal, [s0, s1] = f.spinodal, level = b0 !== undefined ? f.g_mix_over_RT[nearest(xs, b0)] : null;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> raise Ω/RT. Above 2 the curve bends down in the middle: no longer convex. One straight line then touches it twice (the binodal); between the bending points (the spinodal) a uniform state is unstable.</p>
      <div className="legend" aria-hidden><span className="key key-meta">metastable</span><span className="key key-unstable">unstable</span><span className="key key-min">one tangent, touching twice</span></div>
      <Plot title={`Mixing part of a regular solution, Ω/RT = ${f.omega_over_RT.toFixed(1)}`} desc="The mixing part of g divided by RT for the chosen Omega/RT, with stable, metastable and unstable bands." height={360}
        xDomain={[0, 1]} yDomain={[-0.75, 0.5]} xLabel="B atom fraction x" yLabel="mixing part of g, in units of RT" yFormat={v => v.toFixed(2)}>
        {({ x, y, top, bottom }) => <>
          {b0 !== undefined && <><rect className="band band-meta" x={x(b0)} width={x(s0) - x(b0)} y={top} height={bottom - top} />
            <rect className="band band-meta" x={x(s1)} width={x(b1) - x(s1)} y={top} height={bottom - top} />
            <rect className="band band-unstable" x={x(s0)} width={x(s1) - x(s0)} y={top} height={bottom - top} /></>}
          <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
          <path className="line line-solid" d={path(xs.map((v, k) => [x(v), y(f.g_mix_over_RT[k])]))} />
          {level !== null && <line className="tangent-solid" x1={x(0)} x2={x(1)} y1={y(level)} y2={y(level)} />}
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-omega" className="control-label">Ω/RT <strong>{f.omega_over_RT.toFixed(i === day3 ? 3 : 1)}</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="d3-omega" valueText={`Omega over RT ${f.omega_over_RT.toFixed(1)}`} />
        <div className="control-row">
          <button type="button" className="ghost-button" onClick={() => setI(nearest(frames.map(r => r.omega_over_RT), 2.0))}>Ω/RT = 2: the edge, still convex but flat in the middle</button>
          <button type="button" className="ghost-button" onClick={() => setI(day3)}>Ω/RT ≈ 3.007: the regular solution of steps 15–17 at 800 K</button>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <p className={`status-pill ${b0 !== undefined ? 'pill-open' : 'pill-solid'}`}>{b0 !== undefined ? 'Not convex: one phase model, two phases' : 'Convex: one phase everywhere'}</p>
      <dl className="readouts">
        {b0 !== undefined ? <><Readout label="Binodal (touching points)" value={`${b0.toFixed(3)} and ${b1.toFixed(3)}`} tone="min" />
          <Readout label="Spinodal (bending points)" value={`${s0.toFixed(3)} and ${s1.toFixed(3)}`} /></>
          : <Readout label="Binodal" value="none" />}
      </dl>
      <p className="caption">At 800 K with Ω = 20000 J/mol, Ω/RT is about 3.0: binodal 0.070 and 0.930, spinodal 0.211 and 0.789.</p>
    </aside>
  </div>;
}
