'use client';
/** Advanced steps 15–17: local search, keep pricing, branch-and-bound and the joint case (regular solution at 800 K). */
import { useEffect, useState } from 'react';
import Plot, { path } from '@/components/plot';
import RecordSlider from '@/components/record-slider';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented, Stepper } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';
import { day3Path, gapCurve, height } from '@/lib/day3';
import type { Day3Data, Node } from '@/lib/day3';

export type RegularView = 'local' | 'pricing' | 'bnb' | 'joint';
type Reg = Day3Data['regular'];

export default function Day3RegularView({ initialView = 'local', kicker, views }: { initialView?: RegularView; kicker?: string; views?: RegularView[] }) {
  const [data, setData] = useState<Day3Data | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<Day3Data>(day3Path).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the lab data…</p>;
  return <Day3RegularLab reg={data.regular} initialView={initialView} kicker={kicker} views={views} />;
}

export function Day3RegularLab({ reg, initialView = 'local', kicker = 'Interactive lab', views }: { reg: Reg; initialView?: RegularView; kicker?: string; views?: RegularView[] }) {
  const [view, setView] = useState<RegularView>(initialView);
  const shown = ([['local', 'Local search'], ['pricing', 'Keep pricing'], ['bnb', 'Branch-and-bound'], ['joint', 'Joint case']] as [RegularView, string][]).filter(([id]) => !views || views.includes(id) || id === initialView);
  const body = view === 'local' ? <LocalSearch reg={reg} /> : view === 'pricing' ? <KeepPricing reg={reg} /> : view === 'bnb' ? <IntervalPlayer reg={reg} /> : <Joint reg={reg} />;
  return <LabFrame kicker={kicker} title="Local search, pricing and a check"
    conditions={['800 K', `z = ${reg.z.toFixed(2)}`, `Ω = ${reg.omega} J/mol`, 'one phase model, ALPHA']}
    actions={shown.length > 1 ? <Segmented label="Lab view" value={view} onChange={setView} options={shown} /> : undefined}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes">
      <p>Step 02&apos;s ALPHA with its own B plus Ω x(1−x), Ω = 20000 J/mol, at 800 K (step 03 part B). Every energy, search path, round and interval floor was calculated in advance with the course code.</p>
      <p>The lab draws those numbers and subtracts straight lines from energies. The local search shown is the computer&apos;s search on the gap curve, not what atoms do.</p>
    </div>}
    record={<RecordView value={{ binodal: reg.binodal, spinodal: reg.spinodal, tangent: reg.s8.tangent, dip: reg.s8.dip, final: reg.s8b.final, branch_and_bound: { status: reg.s9.status, leaves: reg.s9.leaves, G_low: reg.s9.G_low } }} href="/learning/self_study/generated/day3.json" note="The numbers behind these views." />} />;
}

/** Stable, metastable and unstable bands under a plot. */
function Bands({ reg, x, top, bottom }: { reg: Reg; x: (v: number) => number; top: number; bottom: number }) {
  const [b0, b1] = reg.binodal, [s0, s1] = reg.spinodal;
  return <>
    <rect className="band band-meta" x={x(b0)} width={x(s0) - x(b0)} y={top} height={bottom - top} />
    <rect className="band band-meta" x={x(s1)} width={x(b1) - x(s1)} y={top} height={bottom - top} />
    <rect className="band band-unstable" x={x(s0)} width={x(s1) - x(s0)} y={top} height={bottom - top} />
  </>;
}

function LocalSearch({ reg }: { reg: Reg }) {
  const t = reg.s8.tangent, xs = reg.curve.x, gaps = gapCurve(xs, reg.curve.ALPHA, t.mu_A, t.d_mu);
  const starts = reg.s8.local_search, [si, setSi] = useState(starts.findIndex(p => p.start === 0.15)), [step, setStep] = useState(0);
  const [all, setAll] = useState(false), [scan, setScan] = useState(false);
  const run = starts[si], k = Math.min(step, run.path.length - 1), at = run.path[k];
  const gapAt = (v: number) => gaps[Math.min(xs.length - 1, Math.max(0, Math.round(v * (xs.length - 1))))];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> the gap curve against the tangent at 0.15. Pick a start and step the computer&apos;s downhill search along the curve: from 0.15 it never moves. Then run a full scan of the whole curve.</p>
      <div className="legend" aria-hidden><span className="key key-meta">metastable band</span><span className="key key-unstable">unstable band</span><span className="key key-min">search</span></div>
      <Plot title="Gap curve against the tangent at 0.15" desc="The regular solution's gap curve against its tangent at z = 0.15, with metastable and unstable bands and the local search path from the chosen start." height={380}
        xDomain={[0, 1]} yDomain={[-2300, 1500]} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" yFormat={v => num(v, 0)}>
        {({ x, y, top, bottom }) => <>
          <Bands reg={reg} x={x} top={top} bottom={bottom} />
          <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
          <path className="line line-solid" d={path(xs.map((v, i) => [x(v), y(gaps[i])]))} />
          {(all ? starts : [run]).map(p => <path key={p.start} className="line line-mixing" d={path(p.path.map(v => [x(v), y(gapAt(v))]))} />)}
          <circle className="dot dot-min is-chosen" cx={x(at)} cy={y(gapAt(at))} r={8} />
          {scan && <><line className="df-arrow" x1={x(reg.s8.dip.x)} x2={x(reg.s8.dip.x)} y1={y(0)} y2={y(reg.s8.dip.depth)} /><text className="edge-flag" x={x(reg.s8.dip.x) - 8} y={y(reg.s8.dip.depth) + 16} textAnchor="end">full scan: {num(reg.s8.dip.depth, 1)} near {reg.s8.dip.x_print}</text></>}
        </>}
      </Plot>
      <div className="control-bar">
        <div className="dot-picker" role="group" aria-label="Start of the local search">
          {starts.map((p, i) => <button key={p.start} type="button" className="dot-chip chip-solid" aria-pressed={i === si} onClick={() => { setSi(i); setStep(0); }}>start {p.start}</button>)}
        </div>
        {run.path.length > 1 ? <><label id="d3-local" className="control-label">Search step <strong>{k}</strong> of {run.path.length - 1}</label>
          <RecordSlider index={k} max={run.path.length - 1} onChange={setStep} labelId="d3-local" valueText={`step ${k}, x ${at.toFixed(3)}`} /></>
          : <p className="control-label">From {run.start} the search does not move: the gap curve is flat there and rises on both sides.</p>}
        <div className="control-row">
          <label className="check"><input type="checkbox" checked={all} onChange={e => setAll(e.target.checked)} /> Overlay all starts</label>
          <button type="button" className="ghost-button" onClick={() => setScan(true)}>Full scan</button>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Start ${run.start}: search at ${at.toFixed(3)}`} />
      <dl className="readouts">
        <Readout label="Search from" value={run.start.toFixed(2)} />
        <Readout label="Ends at" value={run.end.toFixed(3)} tone="min" />
        <Readout label="Gap there" value={num(run.gap_end, 1)} unit="J/mol atoms" />
        <Readout label="Tangent slope Δμ" value={num(t.d_mu, 1)} unit="J/mol" />
        <Readout label="Curvature at 0.15" value={num(reg.curvature['0.15'] / 1000, 1)} unit="kJ/mol atoms" />
      </dl>
      <p className="caption">Binodal {reg.binodal.map(v => v.toFixed(3)).join(' and ')}; spinodal {reg.spinodal.map(v => v.toFixed(3)).join(' and ')}.</p>
    </aside>
  </div>;
}

function KeepPricing({ reg }: { reg: Reg }) {
  const its = reg.s8b.iterations;
  const [k, setK] = useState(0), [twoDot, setTwoDot] = useState(false), [zoom, setZoom] = useState(false);
  const it = its[k], line = twoDot && k === 1 ? reg.s8b.two_dot_line : it.line, xs = reg.curve.x;
  const dip = twoDot && k === 1 ? reg.s8b.two_dot_line.dip : it.best;
  const gaps = gapCurve(xs, reg.curve.ALPHA, line.mu_A, line.d_mu), win = it.windows.ALPHA;
  const span = Math.max(Math.abs(dip.depth) * 1.4, 0.02);
  const xDomain: [number, number] = zoom && !twoDot ? [win.x[0], win.x[win.x.length - 1]] : [0, 1];
  const yDomain: [number, number] = zoom && !twoDot ? [Math.min(...win.gap) * 1.3 - 1e-6, span] : [-span, Math.max(span * 1.5, 50)];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> each round, the gap curve against that round&apos;s line and the deepest dip of a full scan. The label says whether the line was returned by the solver or chosen for illustration. One added state is not enough: keep pricing.</p>
      <p className={`status-pill ${it.line_label.startsWith('returned') ? 'pill-solid' : 'pill-open'}`}>{twoDot && k === 1 ? 'Chosen for illustration: the line through 0.15 and 0.958' : it.line_label}</p>
      <Plot title={`Keep pricing: round ${k}`} desc="Gap curve of the regular solution against the round's line, with the menu's states and the deepest dip." height={360}
        xDomain={xDomain} yDomain={yDomain} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" yFormat={v => num(v, span < 1 ? 4 : 0)}>
        {({ x, y }) => <>
          <line className="zero" x1={x(xDomain[0])} x2={x(xDomain[1])} y1={y(0)} y2={y(0)} />
          {zoom && !twoDot ? <path className="line line-solid" d={path(win.x.map((v, i) => [x(v), y(win.gap[i])]))} />
            : <path className="line line-solid" d={path(xs.map((v, i) => [x(v), y(gaps[i])]))} />}
          {it.states.map((st, i) => <circle key={i} className={`dot dot-solid ${it.used.some(u => u.x === st.x) ? 'is-chosen' : ''}`} cx={x(st.x)} cy={y(st.g - height(line.mu_A, line.d_mu, st.x))} r={6} />)}
          <line className="df-arrow" x1={x(dip.x)} x2={x(dip.x)} y1={y(0)} y2={y(dip.depth)} /><circle className="dot dot-min" cx={x(dip.x)} cy={y(dip.depth)} r={7} />
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-pricing" className="control-label">Round <strong>{k}</strong></label>
        <RecordSlider index={k} max={its.length - 1} onChange={v => { setK(v); setTwoDot(false); }} labelId="d3-pricing" valueText={`round ${k}`} />
        <div className="control-row">
          {k === 1 && <label className="check"><input type="checkbox" checked={twoDot} onChange={e => setTwoDot(e.target.checked)} /> Try the line through the 0.15 and 0.958 dots instead</label>}
          <label className="check"><input type="checkbox" checked={zoom} onChange={e => setZoom(e.target.checked)} /> Zoom to the deepest dip</label>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Round ${k}: deepest dip ${num(dip.depth, 4)} near ${dip.x.toFixed(4)}`} />
      <dl className="readouts">
        {it.used.map(u => <Readout key={u.x} label={`Uses ALPHA at ${u.x.toFixed(4)}`} value={u.f.toFixed(4)} unit="of the sample" tone="solid" />)}
        <Readout label="Ceiling" value={num(it.G_up, 2)} unit="J/mol atoms" tone="min" />
        <Readout label="Line slope Δμ" value={num(line.d_mu, 1)} unit="J/mol" />
        <Readout label={`Deepest dip near ${dip.x.toFixed(4)}`} value={num(dip.depth, 4)} unit="J/mol atoms" />
      </dl>
      {k === 1 && <p className="caption">With only 0.15 and 0.958 on the menu and no state left of 0.15, the only mixture is the state at 0.15 itself: every line through it that stays below the 0.958 dot (slope up to about {num(reg.s8b.dual_slope_max, 0)}) is optimal. The solver returned the flat one.</p>}
    </aside>
  </div>;
}

const ACTION: Record<string, string> = { prune: 'prune', split: 'split', 'dip found': 'dip found → add column', open: 'unresolved' };

function IntervalPlayer({ reg }: { reg: Reg }) {
  const [run, setRun] = useState<'proof' | 'discovery' | 'unresolved'>('proof'), [n, setN] = useState(0), [zoom, setZoom] = useState(false);
  const [guess, setGuess] = useState<Record<number, string>>({}), [decide, setDecide] = useState(false);
  const s9 = reg.s9, disc = reg.s9_discovery;
  const nodes: Node[] = run === 'discovery' ? disc.nodes : run === 'unresolved' ? [...s9.unresolved.nodes, ...s9.unresolved.leaves.filter(l => l.floor === null)] : s9.nodes;
  const line = run === 'discovery' ? disc.line : s9.line, eps = s9.eps, k = Math.min(n, nodes.length - 1), node = nodes[k];
  const xs = reg.curve.x, gaps = gapCurve(xs, reg.curve.ALPHA, line.mu_A, line.d_mu);
  const shown = nodes.slice(0, k + 1), current = shown.filter(nd => !shown.some(o => o.n !== nd.n && o.lo >= nd.lo && o.hi <= nd.hi && o.hi - o.lo < nd.hi - nd.lo));
  const hidden = decide && run === 'proof' && guess[node.n] === undefined;
  const xDomain: [number, number] = zoom ? [0.04, 0.11] : [0, 1];
  const yDomain: [number, number] = run === 'discovery' ? [-2500, 1200] : zoom ? [-3, 6] : [-40, 900];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> the bars along the bottom are the intervals: grey to decide, green pruned, gold split, red a dip found. Each interval&apos;s floor is drawn dashed under the gap curve{run === 'discovery' ? '; this run looks for the deepest dip, so an interval is dropped once its floor cannot beat the best dip found so far by more than ε' : ', with the line at −ε'}. Intervals pile up near the touching points, where the curve is close to the line.</p>
      <Segmented label="Which run" value={run} onChange={v => { setRun(v); setN(0); }} options={[['proof', 'Check against the final line'], ['discovery', 'Search against the tangent at 0.15'], ['unresolved', 'Stopped early']]} />
      <Plot title="Interval player: branch-and-bound on the gap curve" desc="The gap curve against the chosen line, the floors of the intervals handled so far, the minus-epsilon line and the interval bars." height={400}
        xDomain={xDomain} yDomain={yDomain} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" yFormat={v => num(v, zoom ? 1 : 0)}>
        {({ x, y, bottom }) => <>
          <line className="zero" x1={x(xDomain[0])} x2={x(xDomain[1])} y1={y(0)} y2={y(0)} />
          {run !== 'discovery' && <line className="crossing" x1={x(xDomain[0])} x2={x(xDomain[1])} y1={y(-eps)} y2={y(-eps)} />}
          <path className="line line-solid" d={path(xs.map((v, i) => [x(v), y(gaps[i])]))} />
          {current.map(nd => nd.floor !== null && <line key={`f${nd.n}-${nd.lo}`} className={`floor-seg act-${nd === node && hidden ? 'todo' : nd.action.replace(' ', '-')}`} x1={x(nd.lo)} x2={x(nd.hi)} y1={y(Math.max(nd.floor, yDomain[0]))} y2={y(Math.max(nd.floor, yDomain[0]))} />)}
          {current.map(nd => <rect key={`b${nd.n}-${nd.lo}`} className={`interval-bar act-${nd === node && hidden ? 'todo' : nd.action.replace(' ', '-')} ${nd === node ? 'is-current' : ''}`} x={x(nd.lo) + 1} width={Math.max(x(nd.hi) - x(nd.lo) - 2, 1)} y={bottom - 16} height={12} rx={3} />)}
          {run === 'discovery' && disc.found.x !== null && disc.found.gap_at_x !== null && <circle className="dot dot-min" cx={x(disc.found.x)} cy={y(disc.found.gap_at_x)} r={7} />}
        </>}
      </Plot>
      <div className="control-bar">
        <label id="d3-bnb" className="control-label">Interval {k + 1} of {nodes.length}: [{node.lo.toFixed(4)}, {node.hi.toFixed(4)}]</label>
        <RecordSlider index={k} max={nodes.length - 1} onChange={setN} labelId="d3-bnb" valueText={`interval ${k + 1}`} />
        <div className="control-row">
          <Stepper index={k} count={nodes.length} onChange={setN} unit="interval" label="Intervals of the search" nextDisabled={hidden} />
          {run === 'proof' && <label className="check"><input type="checkbox" checked={decide} onChange={e => setDecide(e.target.checked)} /> I decide prune or split</label>}
          <label className="check"><input type="checkbox" checked={zoom} onChange={e => setZoom(e.target.checked)} /> Zoom near 0.07</label>
        </div>
        {hidden && <div className="control-row" role="group" aria-label="Your decision">
          <span className="caption">Floor {node.floor === null ? '—' : num(node.floor, 3)} against −ε = −{eps}:</span>
          {['prune', 'split'].map(a => <button key={a} type="button" className="ghost-button" onClick={() => setGuess(g => ({ ...g, [node.n]: a }))}>{a}</button>)}
        </div>}
        {decide && guess[node.n] && <p className="caption">{guess[node.n] === node.action ? 'Right: ' : 'Not quite: '}{node.action} (floor {node.floor === null ? "not examined" : num(node.floor, 3)}).</p>}
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Interval ${k + 1}: ${node.floor === null ? 'not examined' : `floor ${num(node.floor, 3)}`}, ${hidden ? 'your decision' : ACTION[node.action]}`} />
      <p className="lab-kicker">{run === 'discovery' ? 'Search for the deepest dip' : `Prune if the floor is at least −${eps}`}</p>
      <dl className="readouts">
        <Readout label="Interval" value={`${node.lo.toFixed(4)} to ${node.hi.toFixed(4)}`} />
        <Readout label="Floor (chord bound)" value={node.floor === null ? 'not examined' : num(node.floor, 3)} unit={node.floor === null ? undefined : 'J/mol atoms'} tone="min" />
        <Readout label="Gap at the evaluated point" value={node.gap_at_x === null ? '—' : num(node.gap_at_x, 3)} unit={node.gap_at_x === null ? undefined : 'J/mol atoms'} />
        <Readout label="Decision" value={hidden ? '?' : ACTION[node.action]} />
        {run === 'proof' && k === nodes.length - 1 && <><Readout label="Lowest floor" value={num(s9.lowest_floor, 3)} unit="J/mol atoms" />
          <Readout label="Floor for the sample" value={num(s9.G_low, 2)} unit="J/mol atoms" /><Readout label="Ceiling minus floor" value={num(s9.remaining, 2)} unit="J/mol atoms" tone="solid" /></>}
        {run === 'discovery' && k === nodes.length - 1 && disc.found.gap_at_x !== null && disc.found.x !== null && <Readout label="Deepest dip found" value={num(disc.found.gap_at_x, 1)} unit={`near ${disc.found.x.toFixed(3)}`} tone="solid" />}
        {run === 'unresolved' && k === nodes.length - 1 && <Readout label="Result" value="unresolved" unit="intervals still open" />}
      </dl>
    </aside>
  </div>;
}

function Joint({ reg }: { reg: Reg }) {
  const [z, setZ] = useState<0.15 | 0.5>(0.15), xs = reg.curve.x;
  const line = z === 0.15 ? reg.s8.tangent : reg.joint.line_at_half;
  const gaps = gapCurve(xs, reg.curve.ALPHA, line.mu_A, line.d_mu);
  const dips = z === 0.15 ? [reg.s8.dip] : reg.joint.dips_at_half;
  const curv = reg.curvature[z === 0.15 ? '0.15' : '0.5'];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Predict first:</strong> metastable or unstable? If metastable, where is the bulk drive largest? Then compare with the final compositions, 0.070 and 0.930.</p>
      <Segmented label="Sample" value={z === 0.15 ? 'a' : 'b'} onChange={v => setZ(v === 'a' ? 0.15 : 0.5)} options={[['a', 'z = 0.15'], ['b', 'z = 0.50']]} />
      <Plot title={`Gap curve against the tangent at ${z}`} desc="The regular solution's gap curve against its tangent at the chosen sample composition, with stability bands and the dips." height={360}
        xDomain={[0, 1]} yDomain={[-2300, 1500]} xLabel="B atom fraction x" yLabel="gap (J/mol atoms)" yFormat={v => num(v, 0)}>
        {({ x, y, top, bottom }) => <>
          <Bands reg={reg} x={x} top={top} bottom={bottom} />
          <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
          <path className="line line-solid" d={path(xs.map((v, i) => [x(v), y(gaps[i])]))} />
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          {dips.map(d => <g key={d.x}><line className="df-arrow" x1={x(d.x)} x2={x(d.x)} y1={y(0)} y2={y(d.depth)} /><circle className="dot dot-min" cx={x(d.x)} cy={y(d.depth)} r={6} /></g>)}
          {reg.binodal.map(b => <line key={b} className="ghost" x1={x(b)} x2={x(b)} y1={top} y2={bottom} />)}
        </>}
      </Plot>
    </div>
    <aside className="lab-side">
      <p className={`status-pill ${curv > 0 ? 'pill-solid' : 'pill-open'}`}>{curv > 0 ? 'Metastable: bends up, but a split is lower' : 'Unstable: bends down, no barrier'}</p>
      <dl className="readouts">
        <Readout label="Curvature at z" value={num(curv / 1000, 1)} unit="kJ/mol atoms" />
        {dips.map(d => <Readout key={d.x} label={`Dip at ${d.x.toFixed(3)}`} value={num(d.depth, 1)} unit="J/mol atoms" tone="min" />)}
        <Readout label="Equilibrium compositions" value={reg.binodal.map(v => v.toFixed(3)).join(' and ')} />
      </dl>
      <p className="caption">The dip is where the bulk drive is largest; the final compositions come from the converged calculation; a real nucleus also depends on interface and elastic energy.</p>
    </aside>
  </div>;
}
