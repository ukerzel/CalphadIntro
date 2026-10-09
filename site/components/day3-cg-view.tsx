'use client';
/** Advanced steps 13–14: the column-generation player, ceiling and floor, and finer menus (melting lens). */
import { useEffect, useState } from 'react';
import Plot, { path } from '@/components/plot';
import RecordSlider, { ValueSlider } from '@/components/record-slider';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented, Stepper } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';
import { day3Path, gapCurve, height } from '@/lib/day3';
import type { Day3Data, Iteration } from '@/lib/day3';

export type CgView = 'player' | 'bounds' | 'spacing';
type Lens = Day3Data['lens'];
const PHASES = ['SOLID', 'LIQUID'] as const;
const tone = (phase: string) => phase === 'SOLID' ? 'solid' : 'liquid';
const STAGES = ['Master: the cheapest mixture of the menu and its line.', 'Pricer: the deepest dip of the gap curve against that line.', 'Add that state to the menu and solve again.'] as const;

export default function Day3CgView({ initialView = 'player', kicker, views }: { initialView?: CgView; kicker?: string; views?: CgView[] }) {
  const [data, setData] = useState<Day3Data | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<Day3Data>(day3Path).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the lab data…</p>;
  return <Day3CgLab lens={data.lens} initialView={initialView} kicker={kicker} views={views} />;
}

export function Day3CgLab({ lens, initialView = 'player', kicker = 'Interactive lab', views }: { lens: Lens; initialView?: CgView; kicker?: string; views?: CgView[] }) {
  const [view, setView] = useState<CgView>(initialView);
  const shown = ([['player', 'Iterations'], ['bounds', 'Ceiling and floor'], ['spacing', 'Finer menus']] as [CgView, string][]).filter(([id]) => !views || views.includes(id) || id === initialView);
  const body = view === 'player' ? <PlayerView lens={lens} /> : view === 'bounds' ? <Bounds lens={lens} /> : <Spacing lens={lens} />;
  return <LabFrame kicker={kicker} title="Column generation and bounds"
    conditions={['1400 K', `z = ${lens.z.toFixed(2)}`, 'seed: the step 10 menu', 'J/mol atoms']}
    actions={shown.length > 1 ? <Segmented label="Lab view" value={view} onChange={setView} options={shown} /> : undefined}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes">
      <p>Each round was calculated in advance with the course code: the master (a linear programme over the menu) gives the cheapest mixture and its line; the pricer finds the deepest dip of each phase model&apos;s gap curve with a formula, because both phase models are ideal.</p>
      <p>The ceiling is the master&apos;s energy. The floor is the line at z lowered by the deepest dip of the whole curve. The lab draws these numbers and subtracts lines from energies; it computes nothing else.</p>
    </div>}
    record={<RecordView value={lens.s6.iterations.map(({ k, used, G_up, line, best, G_low_raw, G_low_best, remaining }) => ({ k, used, G_up, line, best, G_low_raw, G_low_best, remaining }))} href="/learning/self_study/generated/day3.json" note="Every round of column generation." />} />;
}

function PlayerView({ lens }: { lens: Lens }) {
  const its = lens.s6.iterations;
  const last = its.length - 1, max = 3 * last;               // the last round only checks: nothing worth adding
  const [s, setS] = useState(0), [zoom, setZoom] = useState(false);
  const k = Math.min(Math.floor(s / 3), last), stage = s >= max ? 1 : s % 3, it = its[k];
  const gaps = Object.fromEntries(PHASES.map(p => [p, gapCurve(lens.curve.x, lens.curve[p], it.line.mu_A, it.line.d_mu)])) as Record<string, number[]>;
  const win = it.windows[it.best.phase];
  const depth = Math.abs(it.best.depth) || 1;
  const xDomain: [number, number] = zoom ? [win.x[0], win.x[win.x.length - 1]] : [0.2, 0.6];
  const yDomain: [number, number] = zoom ? [Math.min(...win.gap) * 1.3, Math.max(depth * 1.5, Math.max(...win.gap) * 0.5)] : [-Math.max(depth * 1.4, 2), Math.max(depth * 2.5, 6)];
  const added = stage === 2 && k < last ? its[k + 1].states.at(-1) : null;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the gap curve against the current line, with the menu&apos;s states as dots. Step through: the master solves, the pricer finds the deepest dip, the state is added, and the line moves. Zoom in when the dip gets too small to see.</p>
      <div className="cg-boxes">
        <div className={`cg-box ${stage === 0 ? 'is-on' : ''}`}><p className="lab-kicker">Master · menu → line</p><p>{it.used.map(u => `${u.phase} ${u.x.toFixed(4)} (${u.f.toFixed(3)})`).join(' + ')}</p><p>ceiling {num(it.G_up, 2)}</p></div>
        <div className={`cg-box ${stage === 1 ? 'is-on' : ''}`}><p className="lab-kicker">Pricer · curve → deepest dip</p><p>{it.best.phase} at {it.best.x.toFixed(4)}</p><p>dip {num(it.best.depth, 4)}</p></div>
      </div>
      <Plot title={`Gap curve in round ${k}`} desc="The gap curve of SOLID and LIQUID against the line of this round; menu states as dots; the deepest dip marked." height={360}
        xDomain={xDomain} yDomain={yDomain} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" yFormat={v => num(v, Math.abs(yDomain[0]) < 0.1 ? 4 : 1)}>
        {({ x, y }) => <>
          <line className="zero" x1={x(xDomain[0])} x2={x(xDomain[1])} y1={y(0)} y2={y(0)} />
          {zoom ? <path className={`line line-${tone(it.best.phase)}`} d={path(win.x.map((v, i) => [x(v), y(win.gap[i])]))} />
            : PHASES.map(p => <path key={p} className={`line line-${tone(p)}`} d={path(lens.curve.x.map((v, i) => [x(v), y(gaps[p][i])]))} />)}
          {it.states.map((st, i) => { const g = st.g - height(it.line.mu_A, it.line.d_mu, st.x); const used = it.used.some(u => u.x === st.x && u.phase === st.phase);
            return <circle key={i} className={`dot dot-${tone(st.phase)} ${used ? 'is-chosen' : ''}`} cx={x(st.x)} cy={y(g)} r={used ? 7 : 5} />; })}
          {stage >= 1 && <><line className="df-arrow" x1={x(it.best.x)} x2={x(it.best.x)} y1={y(0)} y2={y(it.best.depth)} /><circle className="dot dot-min" cx={x(it.best.x)} cy={y(it.best.depth)} r={7} /></>}
          {added && <circle className="dot dot-min is-chosen" cx={x(added.x)} cy={y(0)} r={9} />}
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-cg" className="control-label">Round {k} · {STAGES[stage]}</label>
        <RecordSlider index={s} max={max} onChange={setS} labelId="d3-cg" valueText={`round ${k}, ${STAGES[stage]}`} />
        <div className="control-row">
          <Stepper index={s} count={max + 1} onChange={setS} unit="stage" label="Stages of column generation" />
          <label className="check"><input type="checkbox" checked={zoom} onChange={e => setZoom(e.target.checked)} /> Zoom to the deepest dip</label>
        </div>
      </div>
      <Convergence its={its} k={k} truth={lens.truth.G} />
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Round ${k}: ceiling ${num(it.G_up, 2)}, deepest dip ${num(it.best.depth, 4)}`} />
      <p className="lab-kicker">Round {k}</p>
      <dl className="readouts">
        <Readout label="Ceiling" value={num(it.G_up, 2)} unit="J/mol atoms" tone="min" />
        <Readout label={<>Line: μ<sub>A</sub></>} value={num(it.line.mu_A, 1)} unit="J/mol" />
        <Readout label="Line: Δμ" value={num(it.line.d_mu, 1)} unit="J/mol" />
        {PHASES.map(p => <Readout key={p} label={`${p} deepest dip at ${it.dips[p].x.toFixed(4)}`} value={num(it.dips[p].depth, 4)} unit="J/mol atoms" tone={tone(p)} />)}
        <Readout label="Floor (best so far)" value={num(it.G_low_best, 2)} unit="J/mol atoms" />
        <Readout label="Remaining uncertainty" value={num(it.remaining, 4)} unit="J/mol atoms" />
      </dl>
    </aside>
  </div>;
}

/** Remaining uncertainty per round on a log axis, with the table of ceilings and floors. */
function Convergence({ its, k, truth }: { its: Iteration[]; k: number; truth: number }) {
  const rows = its.filter(it => it.remaining > 0);
  const logs = rows.map(it => Math.log10(it.remaining));
  return <div className="twin">
    <Plot compact title="Remaining uncertainty per round (log scale)" desc="Ceiling minus the best floor so far, on a logarithmic axis, for each round." height={220}
      xDomain={[-0.3, rows.length - 0.7]} yDomain={[Math.floor(Math.min(...logs)) - 0.2, Math.ceil(Math.max(...logs)) + 0.2]} xLabel="round" yLabel="J/mol atoms" xTicks={rows.map((_, i) => i)} xFormat={v => `${v}`} yFormat={v => `1e${v}`}>
      {({ x, y }) => <>
        <path className="line line-total" d={path(rows.map((it, i) => [x(i), y(Math.log10(it.remaining))]))} />
        {rows.map((it, i) => <circle key={i} className={`dot ${i === k ? 'dot-min is-chosen' : 'dot-solid'}`} cx={x(i)} cy={y(Math.log10(it.remaining))} r={i === k ? 7 : 4} />)}
      </>}
    </Plot>
    <div className="learning-table" tabIndex={0} role="region" aria-label="Ceiling and floor per round"><table>
      <thead><tr><th scope="col">Round</th><th scope="col">Ceiling</th><th scope="col">Floor (raw)</th><th scope="col">Floor (best)</th></tr></thead>
      <tbody>{its.map(it => <tr key={it.k} className={it.k === k ? 'is-current' : ''}><th scope="row">{it.k}</th><td>{num(it.G_up, 3)}</td><td>{num(it.G_low_raw, 3)}</td><td>{num(it.G_low_best, 3)}</td></tr>)}
        <tr><th scope="row">truth</th><td colSpan={3}>{num(truth, 3)}</td></tr></tbody>
    </table></div>
  </div>;
}

function Bounds({ lens }: { lens: Lens }) {
  const its = lens.s6.iterations, [k, setK] = useState(0), [slide, setSlide] = useState(1), it = its[k], z = lens.z;
  const lowered = it.line.mu_A + it.best.depth * slide;
  const atZ = height(it.line.mu_A, it.line.d_mu, z), floorAtZ = atZ + Math.min(0, it.best.depth) * slide;
  const yMid = lens.truth.G, span = Math.max(Math.abs(it.best.depth) * 3, 8);
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> slide the line down, keeping its tilt, until it touches the deepest dip. Its height at z is then a floor: no state of either phase model lies below the slid line. The truth is always between floor and ceiling.</p>
      <Plot title={`Ceiling and floor in round ${k}`} desc="The energies near z: both curves, the round's line through the ceiling and the same line slid down by the deepest dip; markers at z." height={360}
        xDomain={[0.28, 0.48]} yDomain={[yMid - span * 1.6, yMid + span * 1.4]} xLabel="B atom fraction x" yLabel="g (J/mol atoms)" yFormat={v => num(v, 0)}>
        {({ x, y, top, bottom }) => <>
          {PHASES.map(p => <path key={p} className={`line line-${tone(p)}`} d={path(lens.curve.x.map((v, i) => [x(v), y(lens.curve[p][i])]))} />)}
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          <line className="tangent" x1={x(0)} y1={y(it.line.mu_A)} x2={x(1)} y2={y(it.line.mu_B)} />
          <line className="learner-line status-optimal" x1={x(0)} y1={y(lowered)} x2={x(1)} y2={y(lowered + it.line.d_mu)} />
          <circle className="dot dot-min" cx={x(z)} cy={y(it.G_up)} r={6} />
          <circle className="dot dot-solid" cx={x(z)} cy={y(floorAtZ)} r={6} />
          <text className="edge-flag" x={x(z) + 8} y={y(it.G_up) - 6}>ceiling</text>
          <text className="edge-flag" x={x(z) + 8} y={y(floorAtZ) + 16}>floor</text>
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-round" className="control-label">Round <strong>{k}</strong></label>
        <RecordSlider index={k} max={its.length - 1} onChange={setK} labelId="d3-round" valueText={`round ${k}`} />
        <label id="d3-slide" className="control-label">Slide the line down <strong>{Math.round(slide * 100)}%</strong> of the deepest dip</label>
        <ValueSlider value={slide} min={0} max={1} step={0.05} onChange={setSlide} labelId="d3-slide" valueText={`${Math.round(slide * 100)} percent`} />
      </div>
      <NumberLine ceiling={it.G_up} floor={it.G_low_best} truth={lens.truth.G} />
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Round ${k}: ceiling ${num(it.G_up, 2)}, floor ${num(it.G_low_best, 2)}`} />
      <dl className="readouts">
        <Readout label="Ceiling (best mixture)" value={num(it.G_up, 2)} unit="J/mol atoms" tone="min" />
        <Readout label="Deepest dip" value={num(it.best.depth, 4)} unit="J/mol atoms" />
        <Readout label="Floor (line slid down, at z)" value={num(it.G_low_best, 2)} unit="J/mol atoms" tone="solid" />
        <Readout label="Remaining uncertainty" value={num(it.remaining, 4)} unit="J/mol atoms" />
        <Readout label="True answer" value={num(lens.truth.G, 2)} unit="J/mol atoms" />
      </dl>
      {slide < 1 && <p className="caption">Only the line slid all the way down is a floor: part-way, the curve may still dip below it.</p>}
    </aside>
  </div>;
}

/** Ceiling, truth and floor as marks on one number line. */
function NumberLine({ ceiling, floor, truth }: { ceiling: number; floor: number; truth: number }) {
  const lo = Math.min(floor, truth), hi = Math.max(ceiling, truth), pad = (hi - lo) * 0.15 || 0.01;
  return <Plot compact title="Ceiling, truth and floor on one number line" desc="The remaining uncertainty is the distance between the floor and the ceiling; the truth lies between." height={110}
    xDomain={[lo - pad, hi + pad]} yDomain={[0, 1]} xLabel="energy at z (J/mol atoms)" yLabel="" yTicks={[]} xFormat={v => num(v, 2)} margin={{ top: 8, right: 22, bottom: 40, left: 22 }}>
    {({ x, y }) => <>
      <line className="tie" x1={x(floor)} x2={x(ceiling)} y1={y(0.5)} y2={y(0.5)} />
      <circle className="dot dot-solid" cx={x(floor)} cy={y(0.5)} r={6} /><text className="edge-flag" x={x(floor)} y={y(0.5) - 12} textAnchor="middle">floor</text>
      <circle className="dot dot-min" cx={x(ceiling)} cy={y(0.5)} r={6} /><text className="edge-flag" x={x(ceiling)} y={y(0.5) - 12} textAnchor="middle">ceiling</text>
      <line className="cursor" x1={x(truth)} x2={x(truth)} y1={y(0.15)} y2={y(0.85)} />
    </>}
  </Plot>;
}

function Spacing({ lens }: { lens: Lens }) {
  const rows = lens.s7.spacing, [i, setI] = useState(0), r = rows[i];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Finer menus instead of added states:</strong> each menu has evenly spaced dots and never a dot at 0.40. The menus are not nested, so finer is not guaranteed to be better; what helps is a dot near the true compositions.</p>
      <NumberLine ceiling={r.G_up} floor={r.G_low} truth={lens.truth.G} />
      <div className="control-bar">
        <label id="d3-spacing" className="control-label">Spacing <strong>{r.spacing}</strong> · {r.dots_per_phase} dots per phase model</label>
        <RecordSlider index={i} max={rows.length - 1} onChange={setI} labelId="d3-spacing" valueText={`spacing ${r.spacing}`} />
      </div>
      <div className="learning-table" tabIndex={0} role="region" aria-label="Finer menus"><table>
        <thead><tr><th scope="col">Spacing</th><th scope="col">Dots per phase</th><th scope="col">Ceiling</th><th scope="col">Floor</th><th scope="col">Remaining</th></tr></thead>
        <tbody>{rows.map((row, k) => <tr key={row.spacing} className={k === i ? 'is-current' : ''}><th scope="row">{row.spacing}</th><td>{row.dots_per_phase}</td><td>{num(row.G_up, 3)}</td><td>{num(row.G_low, 3)}</td><td>{num(row.remaining, 4)}</td></tr>)}</tbody>
      </table></div>
    </div>
    <aside className="lab-side">
      <dl className="readouts">
        {r.used.map(u => <Readout key={`${u.phase}${u.x}`} label={`Uses ${u.phase} ${u.x}`} value={u.f.toFixed(3)} unit="of the sample" tone={tone(u.phase)} />)}
        <Readout label="Remaining uncertainty" value={num(r.remaining, 4)} unit="J/mol atoms" tone="min" />
      </dl>
    </aside>
  </div>;
}
