'use client';
/** Advanced steps 10–12: the menu builder, the draggable line, the gap curve, moving z and moving T (melting lens). */
import { useEffect, useState } from 'react';
import Plot, { nearest, path } from '@/components/plot';
import RecordSlider, { ValueSlider } from '@/components/record-slider';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented, Stepper } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';
import { below, bestOfBasket, day3Path, gapCurve, height, liftAndPivot } from '@/lib/day3';
import type { Day3Data, Dot } from '@/lib/day3';

export type LineView = 'menu' | 'line' | 'gap' | 'move-z' | 'temperature';
type Lens = Day3Data['lens'];

const kJ = (value: number) => num(value / 1000, 1);
const PHASES = ['SOLID', 'LIQUID'] as const;
const tone = (phase: string) => phase === 'SOLID' ? 'solid' : 'liquid';
const Y: [number, number] = [-21000, -11500];

export default function Day3LineView({ initialView = 'menu', kicker, views }: { initialView?: LineView; kicker?: string; views?: LineView[] }) {
  const [data, setData] = useState<Day3Data | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<Day3Data>(day3Path).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the lab data…</p>;
  return <Day3LineLab lens={data.lens} initialView={initialView} kicker={kicker} views={views} />;
}

export function Day3LineLab({ lens, initialView = 'menu', kicker = 'Interactive lab', views }: { lens: Lens; initialView?: LineView; kicker?: string; views?: LineView[] }) {
  const [view, setView] = useState<LineView>(initialView);
  const shown = ([['menu', 'Menu'], ['line', 'Line'], ['gap', 'Gap curve'], ['move-z', 'Move z'], ['temperature', 'Move T']] as [LineView, string][]).filter(([id]) => !views || views.includes(id) || id === initialView);
  const body = view === 'menu' ? <MenuBuilder lens={lens} /> : view === 'line' ? <DraggableLine lens={lens} />
    : view === 'gap' ? <GapCurve lens={lens} /> : view === 'move-z' ? <MoveZ lens={lens} /> : <MoveT lens={lens} />;
  return <LabFrame kicker={kicker} title="Menu, line and gap curve"
    conditions={['1400 K', `z = ${lens.z.toFixed(2)}`, 'SOLID and LIQUID', 'J/mol atoms']}
    actions={shown.length > 1 ? <Segmented label="Lab view" value={view} onChange={setView} options={shown} /> : undefined}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes">
      <p>Two invented ideal phase models, SOLID and LIQUID, at 1400 K: A melts at 1000 K, B at 1800 K (step 03 part C). Every energy shown was calculated in advance with the course code; the lab only draws them.</p>
      <p>What the lab does itself is arithmetic on those numbers: the lever rule on two dots, the height of a straight line, a line subtracted from the energies, and which dot a lifted or turned line touches first.</p>
    </div>}
    record={<RecordView value={{ menu: lens.menu, line_of_the_menu: lens.s2, true_tangent: lens.truth.line, gaps: lens.s4.gaps }} href="/learning/self_study/generated/day3.json" note="The numbers behind these views." />} />;
}

/** Shared drawing of the two curves (faint) and the menu dots. */
function Curves({ lens, x, y, faint = true }: { lens: Lens; x: (v: number) => number; y: (v: number) => number; faint?: boolean }) {
  return <>{PHASES.map(p => <path key={p} className={`line line-${tone(p)} ${faint ? 'is-dim' : ''}`} d={path(lens.curve.x.map((v, i) => [x(v), y(lens.curve[p][i])]))} />)}</>;
}

function MenuBuilder({ lens }: { lens: Lens }) {
  const [basket, setBasket] = useState<number[]>([]), [hook, setHook] = useState(false), [curves, setCurves] = useState(false);
  const dots = lens.menu.dots, z = lens.z;
  const chosen = basket.map(i => dots[i]), best = chosen.length ? bestOfBasket(chosen, z) : null;
  const toggle = (i: number) => setBasket(b => b.includes(i) ? b.filter(j => j !== i) : [...b, i]);
  const used = best ? best.used.map(i => chosen[i]) : [];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> tap dots to put them in your basket. The lab mixes the basket in the cheapest way that makes the sample at z = 0.40: the lever rule on one dot left and one right of z. Which pair is cheapest of all?</p>
      <div className="legend" aria-hidden><span className="key key-solid">SOLID</span><span className="key key-liquid">LIQUID</span><span className="key key-min">your mixture</span></div>
      <Plot title="The menu: ten dots on the lens" desc="Five SOLID and five LIQUID dots at x 0.1 to 0.9; the chord between the chosen pair and the mixture's energy at z = 0.40."
        height={380} xDomain={[0, 1]} yDomain={Y} xLabel="B atom fraction x" yLabel="g (kJ/mol atoms)" yFormat={kJ}
        onPick={(px, py) => { const scores = dots.map(d => Math.hypot((d.x - px) * 10, (d.g - py) / 500)); toggle(scores.indexOf(Math.min(...scores))); }}>
        {({ x, y, top, bottom }) => <>
          {curves && <Curves lens={lens} x={x} y={y} />}
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          {used.length === 2 && <line className="tangent-solid" x1={x(used[0].x)} y1={y(used[0].g)} x2={x(used[1].x)} y2={y(used[1].g)} />}
          {hook && lens.hook.dots.map((d, i) => <circle key={`h${i}`} className={`dot-hollow dot-${tone(d.phase)}`} cx={x(d.x)} cy={y(d.g)} r={7} />)}
          {dots.map((d, i) => <circle key={i} className={`dot dot-${tone(d.phase)} ${basket.includes(i) ? 'is-chosen' : ''}`} cx={x(d.x)} cy={y(d.g)} r={basket.includes(i) ? 8 : 6} />)}
          {best && <circle className="dot dot-min" cx={x(z)} cy={y(best.G)} r={7} />}
        </>}
      </Plot>
      <div className="control-bar">
        <div className="dot-picker" role="group" aria-label="Menu dots">
          {dots.map((d, i) => <button key={i} type="button" className={`dot-chip chip-${tone(d.phase)}`} aria-pressed={basket.includes(i)} onClick={() => toggle(i)}>{d.phase} {d.x.toFixed(1)}</button>)}
        </div>
        <div className="control-row">
          <button type="button" className="ghost-button" onClick={() => setBasket([])}>Empty the basket</button>
          <label className="check"><input type="checkbox" checked={hook} onChange={e => setHook(e.target.checked)} /> Show step 03 part D&apos;s coarse grid</label>
          <label className="check"><input type="checkbox" checked={curves} onChange={e => setCurves(e.target.checked)} /> Show the curves</label>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={best ? `Basket mixture at z 0.40: ${num(best.G, 2)} J/mol atoms` : chosen.length ? 'No valid amounts for this basket' : 'Basket empty'} />
      <p className="lab-kicker">Your basket</p>
      <p className="big-number">{chosen.length} {chosen.length === 1 ? 'dot' : 'dots'}</p>
      {chosen.length > 0 && !best && <p className="status-pill pill-warn">No valid amounts: the basket needs a dot on each side of 0.40</p>}
      <dl className="readouts">
        {best && <Readout label="Energy at z = 0.40" value={num(best.G, 2)} unit="J/mol atoms" tone="min" />}
        {best && used.map((d, i) => <Readout key={i} label={`${d.phase} ${d.x.toFixed(1)}`} value={best.f[i].toFixed(3)} unit="of the sample" tone={tone(d.phase)} />)}
        <Readout label="Best of the whole menu" value={num(lens.s1.G_up, 2)} unit="J/mol atoms" />
        <Readout label="Part D's single SOLID" value={num(lens.hook.G_up, 2)} unit="J/mol atoms" />
        <Readout label="True answer" value={num(lens.truth.G, 2)} unit="J/mol atoms" />
      </dl>
    </aside>
  </div>;
}

type Status = 'not-floor' | 'floor' | 'optimal';

function DraggableLine({ lens }: { lens: Lens }) {
  const dots = lens.menu.dots, z = lens.z, ceiling = lens.s1.G_up;
  const [hz, setHz] = useState(-20700), [slope, setSlope] = useState(4000), [truth, setTruth] = useState(false);
  const [frames, setFrames] = useState<ReturnType<typeof liftAndPivot> | null>(null), [frame, setFrame] = useState(0);
  const muA = frames ? frames[frame].mu_A : hz - slope * z, dmu = frames ? frames[frame].d_mu : slope;
  const atZ = height(muA, dmu, z), bad = below(dots, muA, dmu, 1e-6);
  const status: Status = bad.length ? 'not-floor' : Math.abs(atZ - ceiling) < 0.5 ? 'optimal' : 'floor';
  const set = (h: number, s: number) => { setFrames(null); setFrame(0); setHz(h); setSlope(s); };
  const check = () => { const f = liftAndPivot(dots, z, dmu); setFrames(f); setFrame(0); };
  const message = { 'not-floor': `Not a floor: ${bad.length} ${bad.length === 1 ? 'dot lies' : 'dots lie'} below the line.`, floor: 'A floor for these dots. Can it go higher at z?', optimal: 'The highest floor at z: it meets the ceiling.' }[status];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> make the line a floor (no dot below it), then raise it at z as far as it goes. Predict which dots it will touch and the value of μA, then press <em>Check</em>. Drag near z to move the line up and down; drag elsewhere to turn it about z.</p>
      <div className="legend" aria-hidden><span className="key key-solid">SOLID</span><span className="key key-liquid">LIQUID</span><span className="key key-min">your line</span>{truth && <span className="key key-open">true common tangent</span>}</div>
      <Plot title="A line under the menu's dots" desc="Ten menu dots and a straight line; dots below the line are marked. The line's heights at x = 0 and x = 1 are μA and μB."
        height={400} xDomain={[0, 1]} yDomain={Y} xLabel="B atom fraction x" yLabel="g (kJ/mol atoms)" yFormat={kJ}
        onPick={(px, py) => { if (Math.abs(px - z) < 0.06) set(py, dmu); else set(atZ, (py - atZ) / (px - z)); }}>
        {({ x, y, top, bottom }) => <>
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          {truth && <line className="tangent" x1={x(0)} y1={y(lens.truth.line.mu_A)} x2={x(1)} y2={y(lens.truth.line.mu_B)} />}
          <line className={`learner-line status-${status}`} x1={x(0)} y1={y(muA)} x2={x(1)} y2={y(muA + dmu)} />
          {dots.map((d, i) => <g key={i}><circle className={`dot dot-${tone(d.phase)} ${bad.includes(i) ? 'is-bad' : ''} ${frames?.[frame].touch.includes(i) ? 'is-chosen' : ''}`} cx={x(d.x)} cy={y(d.g)} r={6} />
            {bad.includes(i) && <text className="dot-label" x={x(d.x) + 9} y={y(d.g) + 16}>below</text>}</g>)}
          <circle className="handle" cx={x(z)} cy={y(atZ)} r={8} />
          <text className="edge-flag" x={x(0) + 6} y={y(muA) - 8}>μA {num(muA, 1)}</text>
          <text className="edge-flag" x={x(1) - 6} y={y(muA + dmu) - 8} textAnchor="end">μB {num(muA + dmu, 1)}</text>
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-height" className="control-label">Height at z = 0.40 <strong>{num(atZ, 1)}</strong></label>
        <ValueSlider value={atZ} min={-21000} max={-20000} step={0.5} onChange={v => set(v, dmu)} labelId="d3-height" valueText={`${num(atZ, 1)} J/mol atoms`} />
        <label id="d3-slope" className="control-label">Slope Δμ <strong>{num(dmu, 1)}</strong></label>
        <ValueSlider value={dmu} min={-15000} max={20000} step={1} onChange={v => set(atZ, v)} labelId="d3-slope" valueText={`${num(dmu, 1)} J/mol atoms`} />
        <div className="control-row">
          <button type="button" className="button-primary" onClick={check}>Check: lift and turn the line</button>
          {frames && <><Stepper index={frame} count={frames.length} onChange={setFrame} unit="move" label="Moves of the line" />
            <span className="caption">{frame === 0 ? 'Lifted until it touches a dot.' : frame < frames.length - 1 ? 'Turned about the touching dot until the next one touches.' : 'Two touching dots on opposite sides of z: done.'}</span></>}
          <label className="check"><input type="checkbox" checked={truth} onChange={e => setTruth(e.target.checked)} /> Show the true common tangent</label>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={message} />
      <p className="lab-kicker">Your line</p>
      <p className={`status-pill pill-${status === 'not-floor' ? 'warn' : status === 'optimal' ? 'equal' : 'solid'}`}>{message}</p>
      <FloorMeter value={atZ} ceiling={ceiling} ok={status !== 'not-floor'} />
      <dl className="readouts">
        <Readout label={<>μ<sub>A</sub> (height at x = 0)</>} value={num(muA, 1)} unit="J/mol atoms" />
        <Readout label={<>μ<sub>B</sub> (height at x = 1)</>} value={num(muA + dmu, 1)} unit="J/mol atoms" />
        <Readout label="Δμ (slope)" value={num(dmu, 1)} unit="J/mol atoms" />
        <Readout label="Ceiling (best mixture)" value={num(ceiling, 2)} unit="J/mol atoms" tone="min" />
        {status === 'optimal' && <Readout label="Nudge z by 0.01: energy changes by" value={num(dmu * 0.01, 1)} unit="J/mol atoms" />}
      </dl>
    </aside>
  </div>;
}

/** A vertical bar: the line's height at z against the ceiling. */
function FloorMeter({ value, ceiling, ok }: { value: number; ceiling: number; ok: boolean }) {
  const lo = ceiling - 600, frac = Math.max(0, Math.min(1, (value - lo) / (ceiling - lo)));
  return <div className="floor-meter" aria-hidden>
    <div className="floor-meter-track"><div className={`floor-meter-fill ${ok ? '' : 'is-bad'}`} style={{ height: `${(frac * 100).toFixed(1)}%` }} /><div className="floor-meter-ceiling" /></div>
    <p className="caption">{ok ? `Floor ${num(ceiling - value, 1)} below the ceiling` : 'Not a floor'}</p>
  </div>;
}

function GapCurve({ lens }: { lens: Lens }) {
  const line = lens.s2, xs = lens.curve.x;
  const [curves, setCurves] = useState(false), [hover, setHover] = useState<number | null>(null);
  const [probe, setProbe] = useState(() => nearest(xs, lens.s7.dips.SOLID?.x ?? 0.45));   // a probe set by click, tap, drag or the slider; a mouse hover only previews
  const gaps = Object.fromEntries(PHASES.map(p => [p, gapCurve(xs, lens.curve[p], line.mu_A, line.d_mu)])) as Record<string, number[]>;
  const i = curves ? (hover === null ? probe : nearest(xs, hover)) : null;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> every energy minus the line of the menu. Used dots sit at zero, unused dots above it. Predict, then switch on the curves: where do they dip below zero?</p>
      <div className="legend" aria-hidden><span className="key key-solid">SOLID</span><span className="key key-liquid">LIQUID</span><span className="key key-min">driving force (deepest dip)</span></div>
      <Plot title="The gap curve: energy minus the line" desc="Gaps of the ten menu dots as bars from zero; optionally the gap of the continuous curves, which dips below zero between the dots."
        height={380} xDomain={[0, 1]} yDomain={[-120, 900]} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" onHover={curves ? setHover : undefined} onScrub={curves ? value => setProbe(nearest(xs, value)) : undefined}>
        {({ x, y, top, bottom }) => <>
          <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
          {curves && PHASES.map(p => <path key={p} className={`line line-${tone(p)}`} d={path(xs.map((v, k) => [x(v), y(Math.min(gaps[p][k], 1000))]))} />)}
          {lens.s4.gaps.map((g, k) => <g key={k}><line className={`gap-bar bar-${tone(g.phase)}`} x1={x(g.x) + (g.phase === 'SOLID' ? -4 : 4)} x2={x(g.x) + (g.phase === 'SOLID' ? -4 : 4)} y1={y(0)} y2={y(Math.min(g.gap, 900))} />
            <circle className={`dot dot-${tone(g.phase)}`} cx={x(g.x) + (g.phase === 'SOLID' ? -4 : 4)} cy={y(Math.min(g.gap, 900))} r={5} /></g>)}
          {curves && Object.values(lens.s7.dips).map(d => <g key={d.phase}><line className="df-arrow" x1={x(d.x)} x2={x(d.x)} y1={y(0)} y2={y(d.depth)} /><text className="edge-flag" x={x(d.x) + 6} y={y(d.depth) + 14}>{num(d.depth, 1)}</text></g>)}
          {i !== null && <line className="cursor" x1={x(xs[i])} x2={x(xs[i])} y1={top} y2={bottom} />}
        </>}
      </Plot>
      <div className="control-bar">
        {curves && <><label id="d3-probe" className="control-label">Read the gaps at x = <strong>{xs[probe].toFixed(3)}</strong> (tap or drag on the plot, or use the slider)</label>
          <RecordSlider index={probe} max={xs.length - 1} onChange={setProbe} labelId="d3-probe" valueText={`x ${xs[probe].toFixed(3)}`} /></>}
        <div className="control-row">
        <label className="check"><input type="checkbox" checked={curves} onChange={e => setCurves(e.target.checked)} /> Fade in the continuous curves</label>
        <span className="caption">Gaps above 900 are cut off; the table in the step lists them.</span></div></div>
    </div>
    <aside className="lab-side">
      <p className="lab-kicker">Line of the menu</p>
      <dl className="readouts">
        <Readout label={<>μ<sub>A</sub></>} value={num(line.mu_A, 1)} unit="J/mol atoms" />
        <Readout label="Δμ" value={num(line.d_mu, 1)} unit="J/mol atoms" />
        {i !== null && PHASES.map(p => <Readout key={p} label={`${p} gap at x = ${xs[i].toFixed(3)}`} value={num(gaps[p][i], 1)} unit="J/mol atoms" tone={tone(p)} />)}
        {curves && Object.values(lens.s7.dips).map(d => <Readout key={d.phase} label={`${d.phase} deepest dip at ${d.x.toFixed(4)}`} value={num(d.depth, 1)} unit="J/mol atoms" tone="min" />)}
      </dl>
    </aside>
  </div>;
}

/** Slopes of the lower envelope of the dots to the left and right of the dot at x (null at an end): the range a pivoting line can take. */
function envelopeSlopes(dots: Dot[], x: number): [number | null, number | null] {
  const hull: Dot[] = [];
  for (const d of [...dots].sort((a, b) => a.x - b.x || a.g - b.g)) {
    if (hull.length && Math.abs(hull[hull.length - 1].x - d.x) < 1e-12) continue;
    while (hull.length > 1) {
      const [p, q] = [hull[hull.length - 2], hull[hull.length - 1]];
      if ((q.g - p.g) * (d.x - p.x) >= (d.g - p.g) * (q.x - p.x)) hull.pop(); else break;
    }
    hull.push(d);
  }
  const k = hull.findIndex(d => Math.abs(d.x - x) < 1e-12);
  const slope = (a: Dot, b: Dot) => (b.g - a.g) / (b.x - a.x);
  return [k > 0 ? slope(hull[k - 1], hull[k]) : null, k >= 0 && k < hull.length - 1 ? slope(hull[k], hull[k + 1]) : null];
}

function MoveZ({ lens }: { lens: Lens }) {
  const frames = lens.s5.frames, [i, setI] = useState(nearest(frames.map(f => f.z), 0.40)), f = frames[i];
  const [lo, hi] = lens.s5.range;
  const onDot = f.used.length === 1, [left, right] = onDot ? envelopeSlopes(lens.menu.dots, f.z) : [null, null];
  const pivot = !onDot ? '' : left === null ? `at most ${num(right!, 1)} (no dot lies to the left)` : right === null ? `at least ${num(left, 1)} (no dot lies to the right)` : `from ${num(left, 1)} to ${num(right, 1)}`;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> move z. Between 0.3 and 0.5 the same two dots are used and the line does not move: the prices stay the same across the two-phase region. Leave that range and watch the used dots change.</p>
      <Plot title="Moving the overall composition on the menu" desc="The menu dots, the line returned for the selected z, and the used dots; the band shows where the line stays the same."
        height={380} xDomain={[0, 1]} yDomain={Y} xLabel="B atom fraction x" yLabel="g (kJ/mol atoms)" yFormat={kJ}>
        {({ x, y, top, bottom }) => <>
          <rect className="band band-split" x={x(lo)} width={x(hi) - x(lo)} y={top} height={bottom - top} />
          <line className="ghost" x1={x(lens.truth.x_LIQUID)} x2={x(lens.truth.x_LIQUID)} y1={top} y2={bottom} /><line className="ghost" x1={x(lens.truth.x_SOLID)} x2={x(lens.truth.x_SOLID)} y1={top} y2={bottom} />
          {!onDot && <line className="tangent" x1={x(0)} y1={y(f.line.mu_A)} x2={x(1)} y2={y(f.line.mu_B)} />}
          {lens.menu.dots.map((d, k) => <circle key={k} className={`dot dot-${tone(d.phase)} ${f.used.some(u => u.x === d.x && u.phase === d.phase) ? 'is-chosen' : ''}`} cx={x(d.x)} cy={y(d.g)} r={6} />)}
          <line className="cursor" x1={x(f.z)} x2={x(f.z)} y1={top} y2={bottom} />
          <circle className="dot dot-min" cx={x(f.z)} cy={y(f.G_up)} r={7} />
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-z" className="control-label">Overall composition z <strong>{f.z.toFixed(2)}</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="d3-z" valueText={`z ${f.z.toFixed(2)}`} />
        <p className="caption">Shaded: 0.3 to 0.5, where this menu&apos;s line stays put. Faint lines: the true two-phase region, 0.312 to 0.441.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`z ${f.z.toFixed(2)}: ${f.used.map(u => `${u.phase} ${u.x} ${u.f.toFixed(2)}`).join(', ')}`} />
      <p className="big-number">z = {f.z.toFixed(2)}</p>
      <dl className="readouts">
        {f.used.map(u => <Readout key={`${u.phase}${u.x}`} label={`${u.phase} ${u.x.toFixed(1)}`} value={u.f.toFixed(3)} unit="of the sample" tone={tone(u.phase)} />)}
        <Readout label="Cheapest energy" value={num(f.G_up, 2)} unit="J/mol atoms" tone="min" />
        {!onDot && <Readout label={<>μ<sub>A</sub></>} value={num(f.line.mu_A, 1)} unit="J/mol atoms" />}
        {!onDot && <Readout label="Δμ" value={num(f.line.d_mu, 1)} unit="J/mol atoms" />}
      </dl>
      {onDot && <p className="caption">At z = {f.z.toFixed(2)} the sample sits on a used dot, so many lines touch the dots there: the line can rotate about that dot, with Δμ anywhere {pivot} J/mol atoms. The solver returns one of them, so no μ<sub>A</sub> and Δμ are shown.</p>}
    </aside>
  </div>;
}

function MoveT({ lens }: { lens: Lens }) {
  const frames = lens.s5b.frames, [i, setI] = useState(nearest(frames.map(f => f.T_K), 1400)), f = frames[i];
  const all = frames.flatMap(fr => [...fr.g.SOLID, ...fr.g.LIQUID]), lo = Math.min(...all), hi = Math.max(...all);
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> move the temperature. The curves move, the true coexisting compositions trace the lens, and the menu&apos;s answer jumps between dots.</p>
      <div className="twin">
        <Plot compact title={`The two curves at ${f.T_K} K`} desc="SOLID and LIQUID Gibbs energies at the selected temperature, with the coexisting compositions marked." height={300}
          xDomain={[0, 1]} yDomain={[lo, hi]} xLabel="x" yLabel="g (kJ/mol atoms)" yFormat={kJ}>
          {({ x, y, top, bottom }) => <>
            {PHASES.map(p => <path key={p} className={`line line-${tone(p)}`} d={path(lens.s5b.x.map((v, k) => [x(v), y(f.g[p][k])]))} />)}
            <line className="ghost" x1={x(f.x_LIQUID)} x2={x(f.x_LIQUID)} y1={top} y2={bottom} /><line className="ghost" x1={x(f.x_SOLID)} x2={x(f.x_SOLID)} y1={top} y2={bottom} />
            <line className="cursor" x1={x(lens.s5b.z)} x2={x(lens.s5b.z)} y1={top} y2={bottom} />
          </>}
        </Plot>
        <Plot compact title="The lens" desc="Coexisting liquid and solid compositions at each temperature, the selected temperature and the menu's used dots." height={300}
          xDomain={[0, 1]} yDomain={[1000, 1800]} xLabel="x" yLabel="T (K)" yFormat={v => `${v}`}>
          {({ x, y, left, right }) => <>
            <path className="line line-liquid" d={path(frames.map(fr => [x(fr.x_LIQUID), y(fr.T_K)]))} />
            <path className="line line-solid" d={path(frames.map(fr => [x(fr.x_SOLID), y(fr.T_K)]))} />
            <line className="cursor" x1={left} x2={right} y1={y(f.T_K)} y2={y(f.T_K)} />
            <line className="tie" x1={x(f.x_LIQUID)} x2={x(f.x_SOLID)} y1={y(f.T_K)} y2={y(f.T_K)} />
            {f.used.map(u => <circle key={`${u.phase}${u.x}`} className={`dot dot-${tone(u.phase)} is-chosen`} cx={x(u.x)} cy={y(f.T_K)} r={5} />)}
          </>}
        </Plot>
      </div>
      <div className="control-bar">
        <label id="d3-t" className="control-label">Temperature <strong>{f.T_K} K</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="d3-t" valueText={`${f.T_K} K`} />
      </div>
    </div>
    <aside className="lab-side">
      <p className="big-number">{f.T_K} K</p>
      <dl className="readouts">
        <Readout label="Liquid composition" value={f.x_LIQUID.toFixed(3)} tone="liquid" />
        <Readout label="Solid composition" value={f.x_SOLID.toFixed(3)} tone="solid" />
        {f.used.map(u => <Readout key={`${u.phase}${u.x}`} label={`Menu uses ${u.phase} ${u.x.toFixed(1)}`} value={u.f.toFixed(3)} unit="of the sample" tone={tone(u.phase)} />)}
      </dl>
    </aside>
  </div>;
}

export type { Dot };
