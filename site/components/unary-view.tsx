'use client';
import { useState } from 'react';
import RecordSlider from '@/components/record-slider';
import SourceDrawer from '@/components/source-drawer';
import Plot, { Mark, nearest, path } from '@/components/plot';
import LabFrame, { LiveStatus, Player, Readout, RecordView } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { selectRecord } from '@/lib/data';
import type { Bundle, UnaryRow } from '@/lib/data';
import { num } from '@/lib/format';

const Y: [number, number] = [-12500, -5500];
const kelvin = (value: number) => `${value}`;
const energy = (value: number) => num(value / 1000, 1);

/** Contiguous exported rows with the same selected status, for background bands. */
function bands(records: UnaryRow[]) {
  const out: { status: UnaryRow['phase_status']; from: number; to: number }[] = [];
  for (const row of records) {
    const last = out.at(-1);
    if (last && last.status === row.phase_status) last.to = row.T_K;
    else out.push({ status: row.phase_status, from: row.T_K, to: row.T_K });
  }
  return out;
}

export default function UnaryView({ bundle, index, onChange }: { bundle: Bundle; index: number; onChange: (index: number) => void }) {
  const { unary, manifest } = bundle;
  const row = selectRecord(unary.records, `unary-${String(index).padStart(3, '0')}`);
  const panel = manifest.panels.find(p => p.id === 'unary')!;
  const temperatures = unary.records.map(r => r.T_K);
  const [hover, setHover] = useState<number | null>(null), [lpView, setLpView] = useState(false);
  const ghost = hover === null ? null : unary.records[hover];
  const crossing = unary.records.findIndex(r => r.T_K === unary.crossing_temperature_K);
  const equal = row.phase_status === 'equal_energy_fractions_underdetermined';
  const scrub = (value: number) => onChange(nearest(temperatures, value));
  const status = equal ? 'Equal energies' : `${row.phase_status} is lower`;

  const explore = <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> before you drag, predict at which temperature the cheaper line changes, and how much of the sample is liquid just below and just above it. Then drag through that temperature and watch the minimum jump from one end of the phase-fraction line to the other.</p>
      <div className="legend" aria-hidden><span className="key key-solid">SOLID</span><span className="key key-liquid">LIQUID</span><span className="key key-min">selected minimum</span></div>
      <Plot title="Gibbs energies of SOLID and LIQUID by temperature" desc="Two straight lines cross at 1000 kelvin. The selected values are also listed beside the chart."
        height={380} xDomain={[800, 1200]} yDomain={Y} xLabel="Temperature (K)" yLabel="Gibbs energy (kJ/mol atoms)" xFormat={kelvin} yFormat={energy}
        onScrub={scrub} onHover={value => setHover(value === null ? null : nearest(temperatures, value))}>
        {({ x, y, top, bottom }) => <>
          {bands(unary.records).map(band => <rect key={band.from} className={`band band-${band.status === 'SOLID' ? 'solid' : band.status === 'LIQUID' ? 'liquid' : 'equal'}`}
            x={x(band.from)} width={Math.max(2, x(band.to) - x(band.from))} y={top} height={bottom - top} />)}
          <path className="line line-min" d={path(unary.records.map(r => [x(r.T_K), y(r.equilibrium.GM)]))} />
          <path className="line line-solid" d={path(unary.records.map(r => [x(r.T_K), y(r.gibbs_J_per_mol[0])]))} />
          <path className="line line-liquid" d={path(unary.records.map(r => [x(r.T_K), y(r.gibbs_J_per_mol[1])]))} />
          <line className="crossing" x1={x(unary.crossing_temperature_K)} x2={x(unary.crossing_temperature_K)} y1={top} y2={bottom} />
          {ghost && <line className="ghost" x1={x(ghost.T_K)} x2={x(ghost.T_K)} y1={top} y2={bottom} />}
          <g className="glide" style={{ transform: `translateX(${x(row.T_K).toFixed(2)}px)` }}><line className="cursor" x1={0} x2={0} y1={top} y2={bottom} /></g>
          <text className="line-tag tag-solid" x={x(1196)} y={y(unary.records.at(-3)!.gibbs_J_per_mol[0]) - 12} textAnchor="end">SOLID</text>
          <text className="line-tag tag-liquid" x={x(1196)} y={y(unary.records.at(-3)!.gibbs_J_per_mol[1]) - 12} textAnchor="end">LIQUID</text>
          <Mark x={x(row.T_K)} y={y(row.gibbs_J_per_mol[0])} className="mark-solid" />
          <Mark x={x(row.T_K)} y={y(row.gibbs_J_per_mol[1])} className="mark-liquid" />
        </>}
      </Plot>
      {ghost && <p className="hover-note" aria-hidden>{ghost.T_K} K · SOLID {num(ghost.gibbs_J_per_mol[0])} · LIQUID {num(ghost.gibbs_J_per_mol[1])} J/mol atoms</p>}
      <div className="control-bar">
        <label id="temperature-label" className="control-label">Temperature <strong>{row.T_K} K</strong></label>
        <RecordSlider index={index} max={unary.records.length - 1} onChange={onChange} labelId="temperature-label" valueText={`${row.T_K} kelvin`} />
        <div className="control-row">
          <Player index={index} max={unary.records.length - 1} onChange={onChange} label="Temperature sweep" />
          <button type="button" className="ghost-button" onClick={() => onChange(crossing)}>Jump to the crossing</button>
        </div>
        <p className="caption">800–1200 K in 2 K steps · drag on the chart or use the arrow keys. Shading shows which phase is lower.</p>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`${row.T_K} K: ${status}; selected minimum ${num(row.equilibrium.GM)} J/mol atoms`} />
      <p className="lab-kicker">Selected state · {row.id}</p>
      <p className="big-number">{row.T_K}<span> K</span></p>
      <p className={`status-pill ${equal ? 'pill-equal' : row.phase_status === 'SOLID' ? 'pill-solid' : 'pill-liquid'}`}>{status}</p>
      <dl className="readouts">
        <Readout label="SOLID Gibbs energy" value={num(row.gibbs_J_per_mol[0])} unit="J/mol atoms" tone="solid" />
        <Readout label="LIQUID Gibbs energy" value={num(row.gibbs_J_per_mol[1])} unit="J/mol atoms" tone="liquid" />
        <Readout label="Selected minimum" value={num(row.equilibrium.GM)} unit="J/mol atoms" tone="min" />
      </dl>
      <Specimen liquid={row.equilibrium.fractions.LIQUID} />
      <div className="notice">{equal
        ? <><h3>Equal energies; fractions undetermined</h3><p>At {unary.crossing_temperature_K} K every SOLID/LIQUID split has the same energy. The program returned SOLID {row.equilibrium.fractions.SOLID}, LIQUID {row.equilibrium.fractions.LIQUID}, but any split is equally good.</p></>
        : <><h3>{row.phase_status} has lower Gibbs energy</h3><p>The equilibrium is all {row.phase_status.toLowerCase()}: SOLID {row.equilibrium.fractions.SOLID}, LIQUID {row.equilibrium.fractions.LIQUID}.</p></>}</div>
    </aside>
    <div className="lab-wide">
      <h3 className="panel-title" id="lab-fractions">The same state as a phase-fraction question</h3>
      <p className="panel-lede">A mixture of solid and liquid lies on the straight line between the two phase energies, at f<sub>L</sub> = 0 (all solid) and f<sub>L</sub> = 1 (all liquid). The lower end is the minimum. Fractions outside 0 to 1 are impossible.</p>
      <Plot compact title="Mixture energy across liquid phase fraction" desc="Line between the SOLID and LIQUID energies at the selected temperature; hatched zones mark inadmissible fractions." height={240}
        xDomain={[-0.25, 1.25]} yDomain={Y} xTicks={[0, 0.25, 0.5, 0.75, 1]} xLabel="Liquid phase amount fraction fL" yLabel="g_mix (kJ/mol atoms)" yFormat={energy}>
        {({ x, y, top, bottom }) => <>
          <rect className="hatch" x={x(-0.25)} width={x(0) - x(-0.25)} y={top} height={bottom - top} />
          <rect className="hatch" x={x(1)} width={x(1.25) - x(1)} y={top} height={bottom - top} />
          <text className="hatch-label" x={(x(-0.25) + x(0)) / 2} y={top + 16} textAnchor="middle">fL &lt; 0</text>
          <text className="hatch-label" x={(x(1) + x(1.25)) / 2} y={top + 16} textAnchor="middle">fL &gt; 1</text>
          <line className={`seesaw ${equal ? 'seesaw-equal' : ''}`} x1={x(0)} x2={x(1)} y1={y(row.gibbs_J_per_mol[0])} y2={y(row.gibbs_J_per_mol[1])} />
          <Mark x={x(0)} y={y(row.gibbs_J_per_mol[0])} r={5} className="mark-solid" />
          <Mark x={x(1)} y={y(row.gibbs_J_per_mol[1])} r={5} className="mark-liquid" />
          {lpView && <><line className="lp-feasible" x1={x(0)} x2={x(1)} y1={bottom - 6} y2={bottom - 6} /><text className="hatch-label" x={x(0.5)} y={bottom - 12} textAnchor="middle">feasible: 0 ≤ fL ≤ 1</text>
            <text className="hatch-label" x={x(0.5)} y={top + 16} textAnchor="middle">{equal ? 'objective flat: every fraction ties' : `objective falls towards fL = ${row.gibbs_J_per_mol[1] < row.gibbs_J_per_mol[0] ? 1 : 0}`}</text></>}
          <Mark x={x(row.equilibrium.fractions.LIQUID)} y={y(row.equilibrium.GM)} r={7} className="mark-min" label={equal ? 'one minimizer' : 'minimum'} />
        </>}
      </Plot>
      <label className="check"><input type="checkbox" checked={lpView} onChange={e => setLpView(e.target.checked)} /> LP view: the feasible segment and the direction in which the objective falls</label>
      {lpView && <p className="caption">A linear programme with one variable: minimise a straight-line objective over the segment 0 ≤ fL ≤ 1. The answer is an end of the segment, unless the objective is flat, when every point is optimal. Advanced step 10 grows this into many candidate states.</p>}
    </div>
  </div>;

  const model = <div className="model">
    <div className="equations">
      <Eq label="Branch energy at fixed T, p" tex={String.raw`g_\phi(T) = h_\phi - T\,s_\phi`} />
      <Eq label="Balanced two-phase trial" tex={String.raw`g_{\mathrm{mix}} = (1-f_{\mathrm L})\,g_{\mathrm S} + f_{\mathrm L}\,g_{\mathrm L}, \qquad 0 \le f_{\mathrm L} \le 1`} />
      <Eq label="Equilibrium question" tex={String.raw`\min_{0 \le f_{\mathrm L} \le 1}\; g_{\mathrm{mix}}(f_{\mathrm L})`} />
    </div>
    <table className="data-table"><caption>Phase parameters</caption>
      <thead><tr><th scope="col">Phase</th><th scope="col">h, J/mol atoms</th><th scope="col">s, J/(mol atoms K)</th></tr></thead>
      <tbody>{['SOLID', 'LIQUID'].map((phase, i) => <tr key={phase}><th scope="row">{phase}</th><td>{num(row.HM_J_per_mol[i])}</td><td>{num(row.SM_J_per_mol_K[i])}</td></tr>)}</tbody></table>
    <p className="fine">{panel.limitations}</p>
  </div>;

  const record = <>
    <RecordView value={row} href="/data/unary.json" note="The numbers behind the current view." />
    <table className="data-table"><caption>The same states solved two ways: with pycalphad and with a plain SciPy minimiser</caption>
      <thead><tr><th scope="col">T, K</th><th scope="col">Plain GM</th><th scope="col">pycalphad GM</th><th scope="col">pycalphad fractions</th><th scope="col">SciPy fractions</th></tr></thead>
      <tbody>{(unary.saved_comparison_rows as { T_K: number; plain_GM_J_per_mol: number[]; pycalphad_GM_J_per_mol: number[]; pycalphad_equilibrium: { fractions: Record<string, number> }; scipy_equilibrium: { fractions: Record<string, number> } }[]).map(saved =>
        <tr key={saved.T_K}><th scope="row">{saved.T_K}</th><td>{saved.plain_GM_J_per_mol.map(v => num(v)).join(' / ')}</td><td>{saved.pycalphad_GM_J_per_mol.map(v => num(v)).join(' / ')}</td>
          <td>{Object.entries(saved.pycalphad_equilibrium.fractions).map(([k, v]) => `${k} ${v}`).join('; ')}</td><td>{Object.entries(saved.scipy_equilibrium.fractions).map(([k, v]) => `${k} ${v}`).join('; ')}</td></tr>)}</tbody></table>
  </>;

  return <LabFrame kicker="Step 01 · interactive lab" title="Which phase has lower Gibbs energy?"
    conditions={['Invented component A', '1 mol atoms', '100000 Pa', 'SOLID and LIQUID only']}
    actions={<SourceDrawer bundle={bundle} panel={panel} />} explore={explore} model={model} record={record} />;
}

/** Sketch only: dot count follows the exported phase fraction; positions are decorative. */
function Specimen({ liquid }: { liquid: number }) {
  const atoms = Array.from({ length: 48 }, (_, i) => {
    const row = Math.floor(i / 8), col = i % 8;
    const sx = 34 + col * 24 + (row % 2) * 12, sy = 150 - row * 21;
    const h = Math.sin(i * 12.9898) * 43758.5453, r = h - Math.floor(h), h2 = Math.sin(i * 78.233) * 12345.678, r2 = h2 - Math.floor(h2);
    // Liquid: same count on a looser, jittered grid so dots never overlap.
    return { sx, sy, lx: 36 + col * 26 + (r - 0.5) * 10, ly: 34 + row * 23 + (r2 - 0.5) * 10 };
  });
  const count = Math.round(liquid * atoms.length);
  return <figure className="specimen">
    <svg viewBox="0 0 260 180" role="img" aria-label={`Schematic sample: ${count} of ${atoms.length} dots drawn as liquid`}>
      <rect className="specimen-vessel" x="10" y="10" width="240" height="160" rx="22" />
      {atoms.map((atom, i) => {
        const isLiquid = i >= atoms.length - count;
        return <g key={i} className={`atom ${isLiquid ? 'atom-liquid' : 'atom-solid'}`} style={{ transform: `translate(${isLiquid ? atom.lx : atom.sx}px, ${isLiquid ? atom.ly : atom.sy}px)`, transitionDelay: `${(i % 8) * 18}ms` }}>
          <circle r="7.5" style={{ animationDelay: `${-(i * 0.37) % 3}s` }} />
        </g>;
      })}
    </svg>
    <figcaption>Sketch: the share of liquid dots follows the phase fraction; positions are decorative.</figcaption>
  </figure>;
}
