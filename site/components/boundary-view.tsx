'use client';
import { useState } from 'react';
import RecordSlider from '@/components/record-slider';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableCaption } from '@/components/ui/table';
import SourceDrawer from '@/components/source-drawer';
import Plot, { Mark, nearest, path } from '@/components/plot';
import LabFrame, { LiveStatus, Player, Segmented, RecordView } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { selectRecord } from '@/lib/data';
import type { Bundle, BoundaryRow, BoundaryState } from '@/lib/data';
import { full, num, sci } from '@/lib/format';
import BoundaryViews from '@/components/boundary-views';

type Mode = 'compare' | 'open' | 'closed';

export default function BoundaryView({ bundle, index, onChange, initialView = 'cells' }: { bundle: Bundle; index: number; onChange: (index: number) => void; initialView?: 'cells' | 'tangent' | 'iteration' | 'match' }) {
  const data = bundle.boundary, row = selectRecord(data.records, `boundary-${String(index).padStart(3, '0')}`);
  const panel = bundle.manifest.panels.find(p => p.id === 'boundary')!;
  const [mode, setMode] = useState<Mode>('compare');
  const [view, setView] = useState<'cells' | 'tangent' | 'iteration' | 'match'>(initialView);
  const xs = data.records.map(r => r.x_initial_or_reservoir_B);
  const scrub = (value: number) => onChange(nearest(xs, value));
  const shown = (['open', 'closed'] as const).filter(m => mode === 'compare' || mode === m);

  const cells = <>
    <div className="boundary-top">
      <div className="lab-main">
        <p className="how-to"><strong>Try it:</strong> pick a starting B fraction and predict which cell puts more B on the boundary: the open one, where a reservoir keeps the bulk at that fraction, or the closed one, where the boundary takes its B from a fixed inventory. Then compare the two curves across the whole range.</p>
        <div className="legend-row">
          <div className="legend" aria-hidden><span className="key key-open">Open reservoir</span><span className="key key-closed">Closed inventory</span><span className="key key-diag">no preference (θ = x)</span></div>
          <Segmented label="Ensemble focus" value={mode} onChange={setMode} options={[['compare', 'Compare'], ['open', 'Open'], ['closed', 'Closed']]} />
        </div>
        <Plot title="Open and closed boundary occupancies by starting composition" desc="Boundary B occupancy of the open and closed cells; the diagonal marks occupancy equal to the starting or reservoir fraction."
          height={330} xDomain={[0.1, 0.9]} yDomain={[0, 1]} xLabel="Starting / reservoir B atom fraction" yLabel="B boundary occupancy θ (B atoms/site)" onScrub={scrub}>
          {({ x, y }) => <>
            <line className="diagonal" x1={x(0.1)} y1={y(0.1)} x2={x(0.9)} y2={y(0.9)} />
            {(['open', 'closed'] as const).map(m => <path key={m} className={`line line-${m} ${shown.includes(m) ? '' : 'is-dim'}`} d={path(data.records.map(r => [x(r.x_initial_or_reservoir_B), y(Number(r[m].result.theta))]))} />)}
            <text className="line-tag tag-open" x={x(0.5)} y={y(Number(data.records[40].open.result.theta)) - 16} textAnchor="end">OPEN</text>
            <text className="line-tag tag-closed" x={x(0.52)} y={y(Number(data.records[42].closed.result.theta)) + 22} textAnchor="start">CLOSED</text>
            {shown.map(m => <Mark key={m} x={x(row.x_initial_or_reservoir_B)} y={y(Number(row[m].result.theta))} className={`mark-${m}`} />)}
          </>}
        </Plot>
        <h3 className="panel-title">Where the B atoms go</h3>
        <p className="panel-lede">The occupancies nearly agree; the source of the atoms does not. The open cell trades B with its reservoir (below); the closed cell cannot, so the same B moves between its bulk and boundaries instead and this exchange is zero by construction.</p>
        <Plot compact title="B atoms exchanged with the reservoir by the open cell" desc="Open-cell exchange of B atoms with the reservoir; positive means taken from the reservoir, negative means returned."
          height={210} xDomain={[0.1, 0.9]} yDomain={[-30, 150]} xLabel="Starting / reservoir B atom fraction" yLabel="B atoms from the reservoir" onScrub={scrub}>
          {({ x, y, left, right }) => <>
            <line className="zero" x1={left} x2={right} y1={y(0)} y2={y(0)} />
            <text className="hatch-label" x={left + 6} y={y(0) - 6}>taken from the reservoir ↑</text>
            <text className="hatch-label" x={left + 6} y={y(0) + 14}>returned to the reservoir ↓</text>
            <path className="line line-open" d={path(data.records.map(r => [x(r.x_initial_or_reservoir_B), y(r.open.inventory.exchange_atoms!.B)]))} />
            <Mark x={x(row.x_initial_or_reservoir_B)} y={y(row.open.inventory.exchange_atoms!.B)} r={5} className="mark-open" />
          </>}
        </Plot>
        <div className="control-bar">
          <label id="boundary-composition" className="control-label">Starting / reservoir B fraction <strong>{row.x_initial_or_reservoir_B.toFixed(2)}</strong></label>
          <RecordSlider index={index} max={data.records.length - 1} onChange={onChange} labelId="boundary-composition" valueText={`${row.x_initial_or_reservoir_B.toFixed(2)} starting or reservoir B fraction`} />
          <div className="control-row"><Player index={index} max={data.records.length - 1} onChange={onChange} label="Composition sweep" interval={90} /></div>
          <p className="caption">The two occupancy curves nearly coincide because the bulk is large. 0.10–0.90 in steps of 0.01 · both cells start at boundary occupancy 0.25 · 8000 bulk sites · two 100-site boundaries · 20 nm² per boundary</p>
        </div>
      </div>
    </div>
    <LiveStatus text={`Starting fraction ${row.x_initial_or_reservoir_B.toFixed(2)}: open occupancy ${Number(row.open.result.theta).toFixed(4)}, closed occupancy ${Number(row.closed.result.theta).toFixed(4)}`} />
    <div className={`boundary-columns ${shown.length === 1 ? 'is-single' : ''}`}>
      {shown.map(m => <EnsembleCard key={m} mode={m} row={row} />)}
    </div>
  </>;
  const explore = <>
    <Segmented label="View" value={view} onChange={setView} options={[['cells', 'Cells and ledgers'], ['tangent', 'Tangent picture · δ slider'], ['iteration', 'Closed cell by hand'], ['match', 'Which reservoir matches?']]} />
    <div className="part-body">{view === 'cells' ? cells : <BoundaryViews mode={view} />}</div>
  </>;

  const model = <div className="model">
    <div className="equations">
      <Eq label="Boundary function" tex={String.raw`g_{\mathrm s}(\theta) = g_{\mathrm b}(\theta) + \delta\,\theta, \qquad \delta = -5000\ \mathrm{J/mol\ boundary\ sites}`} />
      <Eq label="Open objective at fixed reservoir μ" tex={String.raw`\varphi = g_{\mathrm s}(\theta) - (1-\theta)\,\mu_{\mathrm A} - \theta\,\mu_{\mathrm B}`} />
      <Eq label="Open equilibrium odds" tex={String.raw`\frac{\theta}{1-\theta} = \frac{x_{\mathrm b}}{1-x_{\mathrm b}}\,\exp\!\left(\frac{5000}{8314.5}\right)`} />
      <Eq label="Closed inventory" tex={String.raw`B_{\mathrm{tot}} = 8000\,x_0 + 200\,\theta_0, \qquad x_{\mathrm b}(\theta) = \frac{B_{\mathrm{tot}} - 200\,\theta}{8000}`} />
      <Eq label="Closed cell energy" tex={String.raw`G_{\mathrm{cell}} = \frac{8000\,g_{\mathrm b}(x_{\mathrm b}) + 200\,g_{\mathrm s}(\theta)}{N_{\mathrm{Av}}}`} />
    </div>
    <p>An open reservoir fixes x<sub>b</sub>, μ<sub>A</sub> and μ<sub>B</sub> while the cell exchanges atoms; a closed cell fixes both A and B totals and its bulk composition adjusts. The two cells minimise different energies, so their values are never ranked against each other.</p>
    <p className="fine">{panel.limitations}</p>
  </div>;

  return <LabFrame kicker="Step 04 · interactive lab" title="Open reservoir or closed inventory?"
    conditions={['1000 K', '100000 Pa', 'invented −5000 J/mol boundary-site preference', 'ALPHA bulk from step 02']}
    actions={<SourceDrawer bundle={bundle} panel={panel} />} explore={explore} model={model}
    record={<RecordView value={row} href="/data/boundary.json" note="Both cells for the selected starting composition." />} />;
}

function EnsembleCard({ mode, row }: { mode: 'open' | 'closed'; row: BoundaryRow }) {
  const state = row[mode], closed = mode === 'closed';
  return <section className={`boundary-card card-${mode}`}>
    <p className="lab-kicker">{row.id}</p>
    <h3 className="card-title">{closed ? 'Closed inventory' : 'Open reservoir'}</h3>
    <p className="card-lede">{closed ? 'Fixed total A/B; final bulk composition adjusts.' : 'Reservoir composition and chemical potentials fixed; cell A/B exchange allowed.'}</p>
    <Cell mode={mode} row={row} />
    <dl className="readouts compact">
      <div className="readout-item"><dt>Starting bulk / reservoir B fraction</dt><dd>{row.x_initial_or_reservoir_B.toFixed(2)}</dd></div>
      <div className="readout-item"><dt>{closed ? 'Current bulk B fraction' : 'Bulk B fraction (fixed by reservoir)'}</dt><dd>{full(closed ? state.result.x_bulk : row.x_initial_or_reservoir_B)}</dd></div>
      <div className="readout-item tone-key"><dt>Boundary B occupancy · direct minimum</dt><dd>{full(state.result.theta)} <span className="readout-unit">B atoms/site</span></dd></div>
      <div className="readout-item"><dt>{closed ? 'Check: occupancy from the exchange condition' : 'Check: occupancy from the analytic formula'}</dt><dd>{full(closed ? state.result.theta_root : state.result.theta_analytic)} <span className="readout-unit">B atoms/site</span></dd></div>
      <div className="readout-item"><dt>B excess per boundary</dt><dd>{num(state.B_boundary_excess_atoms, 3)} <span className="readout-unit">B atoms</span> · <span className="mono">{sci(Number(state.result.gamma_B_mol_per_m2), 4)}</span> <span className="readout-unit">mol/m²</span></dd></div>
    </dl>
    <Ledger state={state} closed={closed} />
    <details className="energy-details"><summary>{closed ? 'Closed total Gibbs energy' : 'Open grand potential'} · energy value</summary>
      <p>{closed ? `${full(state.result.G_molar_J_per_mol_sites)} J/mol all occupied cell sites` : `${full(state.result.phi_J_per_mol_sites)} J/mol boundary sites`}</p>
      {closed && <p>{sci(Number(state.result.G_cell_J))} J for this cell</p>}
      <p>Open and closed cells minimise different energies on different bases; never compare these two numbers.</p></details>
  </section>;
}

function Ledger({ state, closed }: { state: BoundaryState; closed: boolean }) {
  const rows = [['Initial', state.inventory.initial], ['Final bulk', state.inventory.bulk_final], ['Final boundaries', state.inventory.boundaries_final], ['Final cell', state.inventory.final],
    [closed ? 'Residual' : 'Reservoir exchange', closed ? state.inventory.residual_atoms! : state.inventory.exchange_atoms!]] as [string, { A: number; B: number }][];
  return <div className="ledger" tabIndex={0} role="region" aria-label="Atom ledger">
    <Table><TableCaption>{closed ? 'Residual = final minus initial; both elements are conserved (differences are rounding).' : 'Exchange = final minus initial cell counts; positive means taken from the reservoir.'}</TableCaption>
      <TableHeader><TableRow><TableHead scope="col">Atoms</TableHead><TableHead scope="col">A</TableHead><TableHead scope="col">B</TableHead></TableRow></TableHeader>
      <TableBody>{rows.map(([label, counts]) => <TableRow key={label} className={label.startsWith('Final cell') ? 'row-total' : ''}><TableHead scope="row">{label}</TableHead>
        <TableCell>{label === 'Residual' ? sci(counts.A) : num(counts.A)}</TableCell><TableCell>{label === 'Residual' ? sci(counts.B) : num(counts.B)}</TableCell></TableRow>)}</TableBody></Table>
  </div>;
}

/** Stable pseudo-random site order: raising a fraction recolours more sites instead of reshuffling. */
const order = (count: number, seed: number) => Array.from({ length: count }, (_, i) => i)
  .map(i => { const h = Math.sin((i + 1) * seed) * 43758.5453; return [h - Math.floor(h), i] as const; })
  .sort((a, b) => a[0] - b[0]).map(([, i]) => i);
const COLS = 18, ROWS = 10, BULK = COLS * 2 * ROWS, GB = ROWS;
const bulkOrder = order(BULK, 12.9898), gbOrder = [order(GB, 78.233), order(GB, 39.425)];
const rank = (list: number[]) => { const out: number[] = []; list.forEach((site, r) => { out[site] = r; }); return out; };
const bulkRank = rank(bulkOrder), gbRank = gbOrder.map(rank);

/** Cross-section sketch. Dots are rounded colourings of exported fractions; gauges show the exact values. */
function Cell({ mode, row }: { mode: 'open' | 'closed'; row: BoundaryRow }) {
  const state = row[mode], closed = mode === 'closed';
  const xb = closed ? Number(state.result.x_bulk) : row.x_initial_or_reservoir_B, theta = Number(state.result.theta);
  const bulkB = Math.round(xb * BULK), gbB = Math.round(theta * GB);
  const exchange = state.inventory.exchange_atoms?.B ?? 0;
  const offset = closed ? 18 : 92, step = 14, gap = 22;
  const column = (c: number) => offset + (c < COLS ? c * step : c < COLS * 2 ? c * step + gap * 2 : 0);
  const gbX = [offset + COLS * step + gap - step / 2 + 4, offset + COLS * 2 * step + gap * 2 + gap - step / 2 + 4];
  const width = gbX[1] + 22;
  return <figure className="cell">
    <svg viewBox={`0 0 ${width} 200`} role="img" aria-label={`${closed ? 'Closed' : 'Open'} cell sketch: bulk B fraction ${xb.toFixed(4)}, boundary occupancy ${theta.toFixed(4)}`}>
      {!closed && <g className="reservoir">
        <rect x="6" y="34" width="64" height="146" rx="12" /><text x="38" y="26" textAnchor="middle">reservoir</text>
        <text x="38" y="112" textAnchor="middle" className="reservoir-x">x = {row.x_initial_or_reservoir_B.toFixed(2)}</text>
        <g className={`flow ${exchange >= 0 ? 'flow-in' : 'flow-out'}`}><line x1="72" x2="88" y1="107" y2="107" /><path d={exchange >= 0 ? 'M84,101 L90,107 L84,113' : 'M76,101 L70,107 L76,113'} /></g>
      </g>}
      <rect className={`cell-wall ${closed ? 'is-closed' : 'is-open'}`} x={offset - 10} y="34" width={width - offset} height="146" rx="10" />
      {gbX.map((gx, g) => <rect key={g} className="gb-band" x={gx - 9} y="36" width="18" height="142" rx="6" />)}
      {Array.from({ length: BULK }, (_, i) => {
        const c = Math.floor(i / ROWS), r = i % ROWS;
        return <circle key={`b${i}`} className={bulkRank[i] < bulkB ? 'site-b' : 'site-a'} cx={column(c) + 4} cy={50 + r * 13.5} r="4.4" />;
      })}
      {gbX.map((gx, g) => Array.from({ length: GB }, (_, r) => <circle key={`g${g}${r}`} className={`gb-site ${gbRank[g][r] < gbB ? 'site-b' : 'site-a'}`} cx={gx} cy={50 + r * 13.5} r="5.2" />))}
      <g className="gauges">
        <Gauge x={offset} label="bulk xb" value={xb} width={COLS * step - 6} />
        <Gauge x={gbX[0] + 16} label="boundary θ" value={theta} width={COLS * step - 20} accent />
      </g>
    </svg>
    <figcaption>{closed ? `Closed: the totals stay fixed; the boundaries went from θ0 = 0.25 to ${theta.toFixed(3)} and the bulk adjusted.` : `Open: the boundaries went from θ0 = 0.25 to ${theta.toFixed(3)}; the cell ${exchange >= 0 ? 'took' : 'returned'} ${num(Math.abs(exchange), 2)} B atoms ${exchange >= 0 ? 'from' : 'to'} the reservoir.`} Dots are a rounded sketch; the bars and the ledger give exact values.</figcaption>
  </figure>;
}

function Gauge({ x, label, value, width, accent }: { x: number; label: string; value: number; width: number; accent?: boolean }) {
  return <g className={`gauge ${accent ? 'gauge-accent' : ''}`} transform={`translate(${x}, 6)`}>
    <rect className="gauge-track" width={width} height="6" rx="3" y="14" />
    <rect className="gauge-fill" width={Math.max(0, Math.min(1, value)) * width} height="6" rx="3" y="14" />
    <text y="9">{label} {value.toFixed(3)}</text>
  </g>;
}
