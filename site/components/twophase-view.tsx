'use client';
import { useEffect, useState } from 'react';
import RecordSlider from '@/components/record-slider';
import Plot, { Mark, nearest, path, ticks } from '@/components/plot';
import LabFrame, { LiveStatus, Player, Readout, RecordView, Segmented } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { loadLearningJSON } from '@/lib/materials';
import { num } from '@/lib/format';

type Region = { phase: string; x: number; f: number };
export type TwoPhaseData = {
  schema_version: 1;
  part_a: { T_K: number; x: number[]; GM: { ALPHA: number[]; BETA: number[] };
    coexistence: { x_ALPHA: number; x_BETA: number; mu_A: number; mu_B: number; GM_x_ALPHA: number; GM_x_BETA: number };
    states: { id: string; z: number; GM: number; regions: Region[]; homogeneous_GM: { ALPHA: number; BETA: number } }[] };
  part_b: { omega_J_per_mol: number; Tc_K: number; x: number[];
    rows: { id: string; T_K: number; GM: number[]; GM_mix: number[]; status: string; compositions: number[]; mu_A: number | null; mu_B: number | null; GM_mix_tangent: number | null }[] };
  part_c: { melting_K: { A: number; B: number }; x: number[];
    rows: { id: string; T_K: number; status: string; relative_GM: { SOLID: number[]; LIQUID: number[] }; x_SOLID: number | null; x_LIQUID: number | null; mu_A: number | null; mu_B: number | null; tangent_relative: [number, number] | null }[] };
};
export const twoPhasePath = 'self_study/generated/two_phase.json';
const kJ = (value: number) => num(value / 1000, 0);

export default function TwoPhaseView({ initialPart = 'a' }: { initialPart?: 'a' | 'b' | 'c' }) {
  const [data, setData] = useState<TwoPhaseData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<TwoPhaseData>(twoPhasePath).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the two-phase data…</p>;
  return <TwoPhaseLab data={data} initialPart={initialPart} />;
}

export function TwoPhaseLab({ data, initialPart = 'a', initialIndex = 49 }: { data: TwoPhaseData; initialPart?: 'a' | 'b' | 'c'; initialIndex?: number }) {
  const [part, setPart] = useState<'a' | 'b' | 'c'>(initialPart);
  const [ic, setIc] = useState(14);
  const [ia, setIa] = useState(initialIndex), [ib, setIb] = useState(0);
  const [curveView, setCurveView] = useState<'mix' | 'full'>('mix');
  const A = data.part_a, B = data.part_b, state = A.states[ia], row = B.rows[ib];
  const zs = A.states.map(s => s.z), co = A.coexistence;
  const split = state.regions.length === 2;

  const partA = <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> at the overall composition z the sample takes the lowest of three options: the ALPHA curve, the BETA curve, or the gold common tangent between the two touching points. On the tangent the sample is split into two phases.</p>
      <div className="legend" aria-hidden><span className="key key-solid">ALPHA</span><span className="key key-open">BETA</span><span className="key key-min">equilibrium</span></div>
      <Plot title="ALPHA and BETA Gibbs energies with their common tangent" desc="Two curves at 1000 K; the common tangent touches ALPHA and BETA at the coexisting compositions. Markers show the homogeneous energies and the equilibrium at the selected overall composition."
        height={380} xDomain={[0, 1]} yDomain={[-12000, 4000]} xLabel="B atom fraction (x for a phase, z for the sample)" yLabel="Gibbs energy (kJ/mol atoms)" yFormat={kJ}
        onScrub={value => setIa(nearest(zs, value))}>
        {({ x, y, top, bottom }) => <>
          <rect className="band band-split" x={x(co.x_ALPHA)} width={x(co.x_BETA) - x(co.x_ALPHA)} y={top} height={bottom - top} />
          <path className="line line-solid" d={path(A.x.map((v, i) => [x(v), y(A.GM.ALPHA[i])]))} />
          <path className="line line-open" d={path(A.x.map((v, i) => [x(v), y(A.GM.BETA[i])]))} />
          <line className="tangent-ext" x1={x(0)} y1={y(co.mu_A)} x2={x(1)} y2={y(co.mu_B)} />
          <line className="tangent-solid" x1={x(co.x_ALPHA)} y1={y(co.GM_x_ALPHA)} x2={x(co.x_BETA)} y2={y(co.GM_x_BETA)} />
          <line className="ghost" x1={x(co.x_ALPHA)} x2={x(co.x_ALPHA)} y1={top} y2={bottom} /><line className="ghost" x1={x(co.x_BETA)} x2={x(co.x_BETA)} y1={top} y2={bottom} />
          <g className="glide" style={{ transform: `translateX(${x(state.z).toFixed(2)}px)` }}><line className="cursor" x1={0} x2={0} y1={top} y2={bottom} /></g>
          <Mark x={x(state.z)} y={y(state.homogeneous_GM.ALPHA)} r={5} className="mark-solid" />
          <Mark x={x(state.z)} y={y(state.homogeneous_GM.BETA)} r={5} className="mark-open" />
          <Mark x={x(state.z)} y={y(state.GM)} r={7} className="mark-min" label="equilibrium" />
        </>}
      </Plot>
      <div className="control-bar">
        <label id="twophase-z" className="control-label">Overall composition z <strong>{state.z.toFixed(2)}</strong></label>
        <RecordSlider index={ia} max={A.states.length - 1} onChange={setIa} labelId="twophase-z" valueText={`${state.z.toFixed(2)} overall B fraction`} />
        <div className="control-row"><Player index={ia} max={A.states.length - 1} onChange={setIa} label="Composition sweep" interval={70} />
          <button type="button" className="ghost-button" onClick={() => setIa(nearest(zs, 0.5))}>z = 0.50</button>
          <button type="button" className="ghost-button" onClick={() => setIa(nearest(zs, 0.35))}>z = 0.35</button></div>
        <p className="caption">0.01–0.99 in steps of 0.01 · the shaded band is where the sample splits ({co.x_ALPHA.toFixed(5)} to {co.x_BETA.toFixed(5)}). The faint extensions of the tangent end at μA (x = 0) and μB (x = 1); outside the band they cannot be reached, because the lever rule would need a negative amount.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`z ${state.z.toFixed(2)}: ${split ? 'two phases' : `one phase, ${state.regions[0].phase}`}; energy ${num(state.GM)} J/mol atoms`} />
      <p className="lab-kicker">Selected state · {state.id}</p>
      <p className="big-number">z = {state.z.toFixed(2)}</p>
      <p className={`status-pill ${split ? 'pill-equal' : state.regions[0].phase === 'ALPHA' ? 'pill-solid' : 'pill-open'}`}>{split ? 'Two phases' : `Only ${state.regions[0].phase}`}</p>
      <Lever regions={state.regions} />
      <LeverArms xAlpha={co.x_ALPHA} xBeta={co.x_BETA} z={state.z} />
      <dl className="readouts">
        <Readout label="Equilibrium energy" value={num(state.GM)} unit="J/mol atoms" tone="min" />
        <Readout label="All ALPHA at z" value={num(state.homogeneous_GM.ALPHA)} unit="J/mol atoms" tone="solid" />
        <Readout label="All BETA at z" value={num(state.homogeneous_GM.BETA)} unit="J/mol atoms" tone="open" />
        <Readout label={<>μ<sub>A</sub> = μ<sub>B</sub> on the tangent</>} value={num(co.mu_A)} unit="J/mol" />
      </dl>
    </aside>
  </div>;

  const full = curveView === 'full', curve = full ? row.GM : row.GM_mix, lo = Math.min(...curve), hi = Math.max(...curve), pad = (hi - lo) * 0.12 || 100;
  const gapRows = B.rows.filter(r => r.compositions.length === 2);
  const partB = <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> left, the mixing part of g(x) for one phase at the selected temperature; the straight reference line is removed so the shape is visible. Switch to the full g(x): the tangent tilts, but it touches at the same two compositions (dotted lines). Below Tc the curve has a hump, and the gold tangent touches it twice. Right, those two compositions plotted against temperature draw the miscibility gap.</p>
      <Segmented label="Curve shown" value={curveView} onChange={setCurveView} options={[['mix', 'Mixing part'], ['full', 'Full g(x)']]} />
      <div className="twin">
        <Plot compact title={`${full ? 'Full' : 'Mixing part of the'} Gibbs energy at ${row.T_K} K`} desc={full ? "One phase's full molar Gibbs energy; when two compositions coexist, the common tangent from mu_A to mu_B touches the curve at both." : "Mixing part of one phase's molar Gibbs energy; when two compositions coexist, the horizontal common tangent touches the curve at both."}
          height={300} xDomain={[0, 1]} yDomain={[lo - pad, hi + pad]} yTicks={ticks(lo - pad, hi + pad, 4)} xLabel="x" yLabel={full ? 'g (kJ/mol atoms)' : 'mixing part of g (kJ/mol atoms)'} yFormat={value => num(value / 1000, 1)}>
          {({ x, y, top, bottom }) => <>
            <path className="line line-solid" d={path(B.x.map((v, i) => [x(v), y(curve[i])]))} />
            {full ? row.mu_A !== null && row.mu_B !== null && <line className="tangent" x1={x(0)} y1={y(row.mu_A)} x2={x(1)} y2={y(row.mu_B)} />
              : row.GM_mix_tangent !== null && <line className="tangent" x1={x(0)} y1={y(row.GM_mix_tangent)} x2={x(1)} y2={y(row.GM_mix_tangent)} />}
            {row.compositions.map(c => <line key={c} className="ghost" x1={x(c)} x2={x(c)} y1={top} y2={bottom} />)}
          </>}
        </Plot>
        <Plot compact title="Miscibility gap: coexisting compositions by temperature" desc="Left and right coexisting compositions at each exported temperature; the horizontal line is the selected temperature and its tie line."
          height={300} xDomain={[0, 1]} yDomain={[580, 1320]} xLabel="x" yLabel="T (K)" yFormat={value => `${value}`}>
          {({ x, y, left, right }) => <>
            <path className="gap-area" d={`${path(gapRows.map(r => [x(r.compositions[0]), y(r.T_K)]))}L${x(0.5).toFixed(2)},${y(B.Tc_K).toFixed(2)}L${[...gapRows].reverse().map(r => `${x(r.compositions[1]).toFixed(2)},${y(r.T_K).toFixed(2)}`).join('L')}Z`} />
            <line className="crossing" x1={left} x2={right} y1={y(B.Tc_K)} y2={y(B.Tc_K)} />
            <text className="hatch-label" x={right - 4} y={y(B.Tc_K) - 6} textAnchor="end">Tc ≈ {B.Tc_K.toFixed(0)} K</text>
            {gapRows.map(r => r.compositions.map(c => <circle key={`${r.id}${c}`} className="gap-point" cx={x(c)} cy={y(r.T_K)} r="2.6" />))}
            <g className="glide" style={{ transform: `translateY(${y(row.T_K).toFixed(2)}px)` }}><line className="cursor" x1={left} x2={right} y1={0} y2={0} /></g>
            {row.compositions.length === 2 && <line className="tie" x1={x(row.compositions[0])} x2={x(row.compositions[1])} y1={y(row.T_K)} y2={y(row.T_K)} />}
            <text className="hatch-label" x={x(0.5)} y={y(800)} textAnchor="middle">two compositions</text>
            <text className="hatch-label" x={x(0.5)} y={y(1290)} textAnchor="middle">one phase</text>
          </>}
        </Plot>
      </div>
      <div className="control-bar">
        <label id="twophase-T" className="control-label">Temperature <strong>{row.T_K} K</strong></label>
        <RecordSlider index={ib} max={B.rows.length - 1} onChange={setIb} labelId="twophase-T" valueText={`${row.T_K} kelvin`} />
        <div className="control-row"><Player index={ib} max={B.rows.length - 1} onChange={setIb} label="Temperature sweep" interval={160} /></div>
        <p className="caption">600–1200 K in 25 K steps, then 1225–1300 K · Ω = {num(B.omega_J_per_mol)} J/mol.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`${row.T_K} K: ${row.compositions.length === 2 ? `two compositions ${row.compositions.map(c => c.toFixed(3)).join(' and ')}` : 'one phase'}`} />
      <p className="lab-kicker">Selected state · {row.id}</p>
      <p className="big-number">{row.T_K}<span> K</span></p>
      <p className={`status-pill ${row.compositions.length === 2 ? 'pill-equal' : 'pill-solid'}`}>{row.compositions.length === 2 ? 'Two compositions' : 'One phase'}</p>
      <dl className="readouts">
        {row.compositions.length === 2 ? <>
          <Readout label="B-poor region x" value={row.compositions[0].toFixed(6)} />
          <Readout label="B-rich region x" value={row.compositions[1].toFixed(6)} />
          <Readout label={<>μ<sub>A</sub> · μ<sub>B</sub> in both regions</>} value={`${num(row.mu_A!)} · ${num(row.mu_B!)}`} unit="J/mol" />
        </> : <Readout label="Above Tc" value="no hump, no gap" />}
      </dl>
    </aside>
  </div>;

  const explore = <>
    <Segmented label="Part" value={part} onChange={setPart} options={[['a', 'A · two different phases'], ['b', 'B · one phase, two compositions'], ['c', 'C · melting and the lens']]} />
    <div className="part-body">{part === 'a' ? partA : part === 'b' ? partB : <LensPart data={data.part_c} index={ic} onChange={setIc} />}</div>
  </>;

  const model = <div className="model">
    <div className="equations">
      <Eq label="Part A, two invented phases at 1000 K" tex={String.raw`g_\alpha = -9000 + 12000\,x + RT\,q(x), \qquad g_\beta = 3000 - 12000\,x + RT\,q(x)`} />
      <Eq label="Balance (lever rule)" tex={String.raw`f_\alpha + f_\beta = 1, \qquad f_\alpha x_\alpha + f_\beta x_\beta = z \;\Rightarrow\; f_\beta = \frac{z - x_\alpha}{x_\beta - x_\alpha}`} />
      <Eq label="Coexistence (common tangent)" tex={String.raw`\mu_{\mathrm A}^{\alpha} = \mu_{\mathrm A}^{\beta}, \qquad \mu_{\mathrm B}^{\alpha} = \mu_{\mathrm B}^{\beta}`} />
      <Eq label="Part B, one phase with a mixing penalty" tex={String.raw`g = 1000 + 12000\,x - 10\,T + RT\,q(x) + \Omega\,x(1-x), \qquad T_{\mathrm c} = \frac{\Omega}{2R}`} />
    </div>
    <p>Both parts use the course’s own invented models (foundations lessons 5–7). The curves, tangents, compositions and amounts in the lab come from a calculation stored in the repository; nothing is recalculated in your browser.</p>
  </div>;

  return <LabFrame kicker="Step 03 · interactive lab" title="Why two phases?"
    conditions={['100000 Pa', '1 mol atoms', 'part A: ALPHA and BETA at 1000 K', 'part B: one phase, 600–1300 K', 'part C: solid and liquid, 950–1850 K']}
    explore={explore} model={model}
    record={<RecordView value={part === 'a' ? state : { ...row, GM: `${row.GM.length} values on x = 0.01…0.99`, GM_mix: `${row.GM_mix.length} values on x = 0.01…0.99` }} href={`/learning/${twoPhasePath}`} note="The numbers behind the current view." />} />;
}

/** Part C: invented ideal solid and liquid; the touching points at each T draw the lens. Exported values only. */
function LensPart({ data, index, onChange }: { data: TwoPhaseData['part_c']; index: number; onChange: (i: number) => void }) {
  const row = data.rows[index], two = row.x_SOLID !== null && row.x_LIQUID !== null;
  const all = [...row.relative_GM.SOLID, ...row.relative_GM.LIQUID], lo = Math.min(...all), hi = Math.max(...all), pad = (hi - lo) * 0.1 || 100;
  const lens = data.rows.filter(r => r.x_SOLID !== null);
  const liquidus = [[0, data.melting_K.A] as [number, number], ...lens.map(r => [r.x_LIQUID!, r.T_K] as [number, number]), [1, data.melting_K.B] as [number, number]];
  const solidus = [[0, data.melting_K.A] as [number, number], ...lens.map(r => [r.x_SOLID!, r.T_K] as [number, number]), [1, data.melting_K.B] as [number, number]];
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> left, the solid and liquid curves at the selected temperature, both measured from the straight line joining the pure solids (this does not move the touching points). Between the two melting points the curves cross and the gold common tangent touches each once. Right, those two touching compositions plotted against temperature draw the lens.</p>
      <div className="twin">
        <Plot compact title={`Solid and liquid Gibbs energies at ${row.T_K} K`} desc="Solid and liquid curves measured from the pure-solid reference line, with the common tangent when they coexist."
          height={300} xDomain={[0, 1]} yDomain={[lo - pad, hi + pad]} yTicks={ticks(lo - pad, hi + pad, 4)} xLabel="x" yLabel="g − solid reference (kJ/mol atoms)" yFormat={value => num(value / 1000, 1)}>
          {({ x, y, top, bottom }) => <>
            <path className="line line-solid" d={path(data.x.map((v, i) => [x(v), y(row.relative_GM.SOLID[i])]))} />
            <path className="line line-liquid" d={path(data.x.map((v, i) => [x(v), y(row.relative_GM.LIQUID[i])]))} />
            {row.tangent_relative && <line className="tangent" x1={x(0)} y1={y(row.tangent_relative[0])} x2={x(1)} y2={y(row.tangent_relative[1])} />}
            {two && [row.x_LIQUID!, row.x_SOLID!].map(c => <line key={c} className="ghost" x1={x(c)} x2={x(c)} y1={top} y2={bottom} />)}
          </>}
        </Plot>
        <Plot compact title="Melting lens: liquidus and solidus" desc="Touching compositions of liquid and solid at each temperature, closed by the two pure melting points."
          height={300} xDomain={[0, 1]} yDomain={[930, 1870]} xLabel="x" yLabel="T (K)" yFormat={value => `${value}`}>
          {({ x, y, left, right }) => <>
            <path className="lens-area" d={`${path(liquidus.map(([c, t]) => [x(c), y(t)]))}L${[...solidus].reverse().map(([c, t]) => `${x(c).toFixed(2)},${y(t).toFixed(2)}`).join('L')}Z`} />
            <path className="line line-liquid" d={path(liquidus.map(([c, t]) => [x(c), y(t)]))} />
            <path className="line line-solid" d={path(solidus.map(([c, t]) => [x(c), y(t)]))} />
            <text className="hatch-label" x={x(0.2)} y={y(1700)}>LIQUID</text>
            <text className="hatch-label" x={x(0.65)} y={y(1100)}>SOLID</text>
            <text className="hatch-label" x={x(0.5)} y={y(1505)} textAnchor="middle">L + S</text>
            <g className="glide" style={{ transform: `translateY(${y(row.T_K).toFixed(2)}px)` }}><line className="cursor" x1={left} x2={right} y1={0} y2={0} /></g>
            {two && <line className="tie" x1={x(row.x_LIQUID!)} x2={x(row.x_SOLID!)} y1={y(row.T_K)} y2={y(row.T_K)} />}
          </>}
        </Plot>
      </div>
      <div className="control-bar">
        <label id="twophase-Tc" className="control-label">Temperature <strong>{row.T_K} K</strong></label>
        <RecordSlider index={index} max={data.rows.length - 1} onChange={onChange} labelId="twophase-Tc" valueText={`${row.T_K} kelvin`} />
        <div className="control-row"><Player index={index} max={data.rows.length - 1} onChange={onChange} label="Temperature sweep" interval={180} /></div>
        <p className="caption">950–1850 K in 20 K steps · A melts at {data.melting_K.A} K (step 01), the invented B at {data.melting_K.B} K · both phases ideal solutions.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`${row.T_K} K: ${row.status}${two ? `, liquid ${row.x_LIQUID!.toFixed(3)}, solid ${row.x_SOLID!.toFixed(3)}` : ''}`} />
      <p className="lab-kicker">Selected state · {row.id}</p>
      <p className="big-number">{row.T_K}<span> K</span></p>
      <p className={`status-pill ${two ? 'pill-equal' : row.status === 'all SOLID' ? 'pill-solid' : 'pill-liquid'}`}>{row.status === 'all SOLID' ? 'Solid at every x' : row.status === 'all LIQUID' ? 'Liquid at every x' : 'Liquid and solid coexist'}</p>
      <dl className="readouts">{two ? <>
        <Readout label="Liquid touching point x" value={row.x_LIQUID!.toFixed(4)} tone="liquid" />
        <Readout label="Solid touching point x" value={row.x_SOLID!.toFixed(4)} tone="solid" />
        <Readout label={<>μ<sub>A</sub> · μ<sub>B</sub> in both phases</>} value={`${num(row.mu_A!)} · ${num(row.mu_B!)}`} unit="J/mol" />
      </> : <Readout label="Common tangent" value="none: one curve is lower everywhere" />}</dl>
    </aside>
  </div>;
}

/** The lever drawn on the composition axis: each phase's amount goes with the arm on the OTHER side of z. Geometry only. */
export function LeverArms({ xAlpha, xBeta, z }: { xAlpha: number; xBeta: number; z: number }) {
  const X = (v: number) => 14 + v * 252, inside = z > xAlpha && z < xBeta;
  return <figure className="lever-arms">
    <svg viewBox="0 0 280 92" role="img" aria-label={inside ? 'Lever: the arm from z to the BETA end measures the ALPHA amount, the arm from the ALPHA end to z measures the BETA amount.' : 'z lies outside the tie line, so no split with these ends is possible.'}>
      <line className="la-axis" x1={X(0)} x2={X(1)} y1="62" y2="62" />
      <text className="la-tick" x={X(0)} y="80" textAnchor="middle">0</text><text className="la-tick" x={X(1)} y="80" textAnchor="middle">1</text>
      <line className="la-tie" x1={X(xAlpha)} x2={X(xBeta)} y1="40" y2="40" />
      <circle className="la-end la-alpha" cx={X(xAlpha)} cy="40" r="5" /><circle className="la-end la-beta" cx={X(xBeta)} cy="40" r="5" />
      {inside ? <>
        <line className="la-arm la-arm-beta" x1={X(xAlpha)} x2={X(z)} y1="40" y2="40" />
        <line className="la-arm la-arm-alpha" x1={X(z)} x2={X(xBeta)} y1="40" y2="40" />
        <text className="la-label la-label-beta" x={(X(xAlpha) + X(z)) / 2} y="28" textAnchor="middle">∝ f_β</text>
        <text className="la-label la-label-alpha" x={(X(z) + X(xBeta)) / 2} y="28" textAnchor="middle">∝ f_α</text>
      </> : <text className="la-warn" x="140" y="20" textAnchor="middle">z outside the tie line: no split</text>}
      <g style={{ transform: `translate(${X(z).toFixed(2)}px, 42px)` }} className="la-fulcrum"><path d="M0,0 L7,13 L-7,13 Z" /><text y="-12" textAnchor="middle">z</text></g>
    </svg>
    <figcaption>{inside ? 'The amount of each phase goes with the arm on the other side of z: the closer z is to an end, the more of that phase.' : 'Outside the tie line the lever rule would need a negative amount, so the sample stays one phase.'}</figcaption>
  </figure>;
}

/** Amount bar: segment widths are the saved phase fractions. */
function Lever({ regions }: { regions: Region[] }) {
  return <figure className="lever">
    <div className="lever-bar">{regions.map((r, i) => <span key={i} className={`lever-seg seg-${r.phase.toLowerCase()}`} style={{ width: `${r.f * 100}%` }}>{r.f > 0.14 && `${r.phase} ${r.f.toFixed(2)}`}</span>)}</div>
    <figcaption>{regions.map(r => `${r.phase}: x = ${r.x.toFixed(4)}, amount ${r.f.toFixed(4)}`).join(' · ')}</figcaption>
  </figure>;
}
