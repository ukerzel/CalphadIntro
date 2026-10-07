'use client';
import { useState } from 'react';
import RecordSlider from '@/components/record-slider';
import SourceDrawer from '@/components/source-drawer';
import Plot, { Mark, nearest, path } from '@/components/plot';
import LabFrame, { LiveStatus, Player, Readout, RecordView } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { selectRecord } from '@/lib/data';
import type { Bundle } from '@/lib/data';
import { num } from '@/lib/format';

const kJ = (value: number) => num(value / 1000, 0);
const Y: [number, number] = [-12000, 4000];

export default function BinaryView({ bundle, index, onChange }: { bundle: Bundle; index: number; onChange: (index: number) => void }) {
  const data = bundle.binary;
  const row = selectRecord(data.records, `binary-${String(index).padStart(3, '0')}`);
  const panel = bundle.manifest.panels.find(p => p.id === 'binary')!;
  const xs = data.records.map(r => r.x_B);
  const [layers, setLayers] = useState({ reference: true, mixing: true, tangent: true });
  const [hover, setHover] = useState<number | null>(null);
  const ghost = hover === null ? null : data.records[hover];
  const scrub = (value: number) => onChange(nearest(xs, value));
  const hoverAt = (value: number | null) => setHover(value === null ? null : nearest(xs, value));
  const { mu_A, mu_B, slope } = row.derivatives;
  const inside = (value: number) => value >= Y[0] && value <= Y[1];
  const toggle = (key: keyof typeof layers) => setLayers(previous => ({ ...previous, [key]: !previous[key] }));
  const bCount = Math.round(row.x_B * 100);

  const explore = <div className="lab-grid">
    <div className="lab-main">
      <div className="layer-toggles" role="group" aria-label="Chart layers">
        <span className="key key-total">Total g<sub>b</sub></span>
        {([['tangent', 'Tangent at x'], ['reference', 'Reference line'], ['mixing', 'Mixing term']] as const).map(([key, label]) =>
          <button key={key} type="button" className={`layer layer-${key}`} aria-pressed={layers[key]} onClick={() => toggle(key)}>{label}</button>)}
      </div>
      <p className="how-to"><strong>How to read it:</strong> the gold dashed line is the tangent at your composition. Where it meets the left edge (x = 0) is μ<sub>A</sub>; where it meets the right edge (x = 1) is μ<sub>B</sub>.</p>
      <Plot title="Homogeneous ALPHA Gibbs energy by B composition" desc="Molar Gibbs energy of ALPHA; the tangent at the selected composition meets x=0 at mu_A and x=1 at mu_B."
        height={400} xDomain={[0, 1]} yDomain={Y} xLabel="B atom mole fraction x" yLabel="Gibbs energy (kJ/mol atoms)" yFormat={kJ}
        onScrub={scrub} onHover={hoverAt}
        overlay={({ x, y, top, bottom }) => layers.tangent && <>
          {inside(mu_A) ? <Mark x={x(0)} y={y(mu_A)} r={5} className="mark-muA" label="μA" /> : <EdgeFlag x={x(0) + 6} y={mu_A < Y[0] ? bottom - 8 : top + 14} text={`μA ${mu_A < Y[0] ? '↓' : '↑'} ${num(mu_A, 0)}`} anchor="start" />}
          {inside(mu_B) ? <Mark x={x(1)} y={y(mu_B)} r={5} className="mark-muB" label="μB" /> : <EdgeFlag x={x(1) - 6} y={mu_B < Y[0] ? bottom - 8 : top + 14} text={`μB ${mu_B < Y[0] ? '↓' : '↑'} ${num(mu_B, 0)}`} anchor="end" />}
        </>}>
        {({ x, y, top, bottom }) => <>
          {layers.mixing && <path className="line line-mixing" d={path(data.records.map(r => [x(r.x_B), y(r.properties.GM_mix)]))} />}
          {layers.reference && <path className="line line-reference" d={path(data.records.map(r => [x(r.x_B), y(r.properties.GM_reference)]))} />}
          <path className="line line-total" d={path(data.records.map(r => [x(r.x_B), y(r.properties.GM)]))} />
          {ghost && <line className="ghost" x1={x(ghost.x_B)} x2={x(ghost.x_B)} y1={top} y2={bottom} />}
          {layers.tangent && <line className="tangent" x1={x(0)} y1={y(mu_A)} x2={x(1)} y2={y(mu_B)} />}
          <Mark x={x(row.x_B)} y={y(row.properties.GM)} className="mark-total" />
        </>}
      </Plot>
      {ghost && <p className="hover-note" aria-hidden>x = {ghost.x_B.toFixed(2)} · g<sub>b</sub> {num(ghost.properties.GM)} J/mol atoms</p>}
      <div className="control-bar">
        <label id="binary-composition" className="control-label">B composition <strong>{row.x_B.toFixed(2)}</strong></label>
        <RecordSlider index={index} max={data.records.length - 1} onChange={onChange} labelId="binary-composition" valueText={`${row.x_B.toFixed(2)} B atom mole fraction`} />
        <div className="control-row"><Player index={index} max={data.records.length - 1} onChange={onChange} label="Composition sweep" interval={70} />
          <button type="button" className="ghost-button" onClick={() => onChange(nearest(xs, 0.2))}>x = 0.20 attempt</button>
          <button type="button" className="ghost-button" onClick={() => onChange(nearest(xs, 0.5))}>x = 0.50 check</button></div>
        <p className="caption">0.01–0.99 in steps of 0.01 · the pure ends are left out because μ is undefined there.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`x B ${row.x_B.toFixed(2)}: Gibbs energy ${num(row.properties.GM)}, mu A ${num(mu_A)}, mu B ${num(mu_B)} J/mol`} />
      <p className="lab-kicker">Selected state · {row.id}</p>
      <p className="big-number">x<sub>B</sub> = {row.x_B.toFixed(2)}</p>
      <Composition b={bCount} />
      <dl className="readouts">
        <Readout label="ALPHA Gibbs energy" value={num(row.properties.GM)} unit="J/mol atoms" tone="total" />
        <Readout label={<>μ<sub>A</sub> · addition chemical potential</>} value={num(mu_A)} unit="J/mol A atoms" tone="muA" />
        <Readout label={<>μ<sub>B</sub> · addition chemical potential</>} value={num(mu_B)} unit="J/mol B atoms" tone="muB" />
        <Readout label={<>Exchange slope · μ<sub>B</sub> − μ<sub>A</sub></>} value={num(slope)} unit="J/mol atoms" />
        <Readout label="Reference / mixing parts" value={`${num(row.properties.GM_reference)} / ${num(row.properties.GM_mix)}`} unit="J/mol atoms" />
        <Readout label="Enthalpy · entropy" value={`${num(row.properties.HM)} · ${num(row.properties.SM)}`} unit="J/mol atoms · J/(mol atoms K)" />
      </dl>
    </aside>
    <div className="lab-wide twin">
      <div>
        <h3 className="panel-title">Chemical potentials along the curve</h3>
        <Plot compact title="Chemical potentials of A and B" desc="mu_A and mu_B across composition, with the selected composition marked." height={230}
          xDomain={[0, 1]} yDomain={[-50000, 8000]} xLabel="x" yLabel="μ (kJ/mol)" yFormat={kJ} onScrub={scrub} onHover={hoverAt}>
          {({ x, y, top, bottom }) => <>
            <path className="line line-muA" d={path(data.records.map(r => [x(r.x_B), y(r.derivatives.mu_A)]))} />
            <path className="line line-muB" d={path(data.records.map(r => [x(r.x_B), y(r.derivatives.mu_B)]))} />
            {ghost && <line className="ghost" x1={x(ghost.x_B)} x2={x(ghost.x_B)} y1={top} y2={bottom} />}
            <Mark x={x(row.x_B)} y={y(mu_A)} r={5} className="mark-muA" /><Mark x={x(row.x_B)} y={y(mu_B)} r={5} className="mark-muB" />
          </>}
        </Plot>
      </div>
      <div>
        <h3 className="panel-title" id="lab-slope">Exchange slope and its sign</h3>
        <Plot compact title="Exchange slope mu_B minus mu_A" desc="Slope of the ALPHA curve with zero marked; a sign change is a local comparison, not a phase transition." height={230}
          xDomain={[0, 1]} yDomain={[-30000, 55000]} xLabel="x" yLabel="g′ (kJ/mol atoms)" yFormat={kJ} onScrub={scrub} onHover={hoverAt}>
          {({ x, y, top, bottom }) => <>
            <line className="zero" x1={x(0)} x2={x(1)} y1={y(0)} y2={y(0)} />
            <path className="line line-slope" d={path(data.records.map(r => [x(r.x_B), y(r.derivatives.slope)]))} />
            {ghost && <line className="ghost" x1={x(ghost.x_B)} x2={x(ghost.x_B)} y1={top} y2={bottom} />}
            <Mark x={x(row.x_B)} y={y(slope)} r={5} className={slope < 0 ? 'mark-muB' : 'mark-muA'} />
          </>}
        </Plot>
      </div>
      <p className="caption">Only ALPHA is allowed here, so a slope that changes sign does not mean two phases appear.</p>
    </div>
  </div>;

  const model = <div className="model">
    <div className="equations">
      <Eq label="Molar curve, per mole of atoms" tex={String.raw`g_{\mathrm b}(x) = (1-x)\,g_{\mathrm A} + x\,g_{\mathrm B} + RT\left[(1-x)\ln(1-x) + x\ln x\right]`} />
      <Eq label="Exchange slope" tex={String.raw`g_{\mathrm b}' = \mu_{\mathrm B} - \mu_{\mathrm A}`} />
      <Eq label="Tangent intercepts" tex={String.raw`\mu_{\mathrm A} = g_{\mathrm b} - x\,g_{\mathrm b}', \qquad \mu_{\mathrm B} = g_{\mathrm b} + (1-x)\,g_{\mathrm b}'`} />
    </div>
    <p>The tangent in the lab is the straight line from (0, μ<sub>A</sub>) to (1, μ<sub>B</sub>); it touches the curve at the selected composition. At the pure ends 0 ln 0 = 0 for the energy, but μ is undefined there.</p>
    <p className="fine">{panel.limitations}</p>
  </div>;

  return <LabFrame kicker="Step 02 · interactive lab" title="Composition and chemical potentials"
    conditions={['1000 K', '100000 Pa', 'one ideal solution phase: ALPHA', 'x = B atom fraction']}
    actions={<SourceDrawer bundle={bundle} panel={panel} />} explore={explore} model={model}
    record={<RecordView value={row} href="/data/binary.json" note="The numbers behind the current view." />} />;
}

function EdgeFlag({ x, y, text, anchor }: { x: number; y: number; text: string; anchor: 'start' | 'end' }) {
  return <text className="edge-flag" x={x} y={y} textAnchor={anchor}>{text}</text>;
}

/** 100-site sketch of the selected composition (rounded to whole squares). */
function Composition({ b }: { b: number }) {
  return <figure className="composition">
    <svg viewBox="0 0 200 40" role="img" aria-label={`${b} of 100 sketch sites drawn as B`}>
      {Array.from({ length: 100 }, (_, i) => <rect key={i} x={(i % 25) * 8} y={Math.floor(i / 25) * 10} width="6.5" height="8.5" rx="1.5" className={i < b ? 'site-b' : 'site-a'} />)}
    </svg>
    <figcaption><span className="key key-a">A</span><span className="key key-b">B</span> 100-site sketch of x, rounded</figcaption>
  </figure>;
}
