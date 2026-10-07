'use client';
import { useEffect, useMemo, useState } from 'react';
import Plot, { nearest } from '@/components/plot';
import RecordSlider from '@/components/record-slider';
import { LiveStatus, Player, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';

type Cell = [number, number, number][]; // [phase index, amount NP, phase composition]
export type GridData = { system: string; element: string; phases: string[]; T_K: number[]; x: number[]; P_Pa: number; pdens: number;
  rounding_digits: number; atoms_per_formula?: Record<string, number>; modes: Record<string, Cell[][]> };

const SHORT: Record<string, string> = { LIQUID: 'L', FCC_A1: 'FCC', BCC_A2: 'BCC', HCP_A3: 'HCP', DELTA: 'δ', MU_PHASE: 'μ', NBNI8: 'NbNi₈', BCC_B2: 'B2' };
const FILLS = ['#c9d8f4', '#f6cdbd', '#c6e7dc', '#e4d4f4', '#f3e4b9', '#d9d3c5', '#b9d5f6', '#f1c0d1', '#cfe9ba', '#e2cba9', '#bde0e9', '#ebbebe', '#d2e0f0', '#f0d9c4'];
const PHASE_DOT = ['#2445c4', '#cf4418', '#0c7a6e', '#7a3fc0', '#8f6400', '#3c4350', '#b0306a', '#4f7d1f'];
const key = (cell: Cell, phases: string[]) => cell.map(c => SHORT[phases[c[0]]] ?? phases[c[0]]).join(' + ');

export default function PhaseMap({ path, modeLabels }: { path: string; modeLabels?: Record<string, string> }) {
  const [data, setData] = useState<GridData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<GridData>(path).then(v => { if (active) setData(v); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, [path]);
  if (error) return <div className="notice" role="alert"><h3>Phase diagram unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the phase diagram…</p>;
  return <PhaseMapView data={data} modeLabels={modeLabels} />;
}

/** Clickable equilibrium grid: each cell coloured by its phase assemblage; tie line, amounts and a cooling path. Saved values only. */
export function PhaseMapView({ data, modeLabels }: { data: GridData; modeLabels?: Record<string, string> }) {
  const modes = Object.keys(data.modes);
  const [mode, setMode] = useState(modes[0]);
  const [it, setIt] = useState(Math.round(data.T_K.length * 0.4)), [ix, setIx] = useState(Math.floor(data.x.length / 2));
  const [basis, setBasis] = useState<'atoms' | 'formula'>('atoms');
  const rows = data.modes[mode], cell = rows[it][ix], T = data.T_K[it], X = data.x[ix];
  const el = data.element === 'NI' ? 'Ni' : 'Nb', other = data.element === 'NI' ? 'Cu' : 'Ni';
  const dx = data.x[1] - data.x[0], dT = data.T_K[1] - data.T_K[0];
  const { colour, labels } = useMemo(() => {
    const colour: Record<string, string> = {}, sums: Record<string, [number, number, number]> = {};
    rows.forEach((row, i) => row.forEach((c, j) => {
      const k = key(c, data.phases);
      if (!(k in colour)) colour[k] = FILLS[Object.keys(colour).length % FILLS.length];
      const s = sums[k] ?? (sums[k] = [0, 0, 0]); s[0] += data.x[j]; s[1] += data.T_K[i]; s[2] += 1;
    }));
    const labels = Object.entries(sums).filter(([, s]) => s[2] >= 12).map(([k, s]) => ({ k, x: s[0] / s[2], T: s[1] / s[2] }));
    return { colour, labels };
  }, [rows, data]);
  const gapTops = useMemo(() => {
    const fcc = data.phases.indexOf('FCC_A1');
    if (fcc < 0) return [];
    return modes.map(m => ({ m, T: Math.max(-Infinity, ...data.T_K.filter((t, i) => data.modes[m][i].some(c => c.filter(p => p[0] === fcc).length >= 2))) })).filter(g => Number.isFinite(g.T));
  }, [data, modes]);
  const pick = (x: number, y: number) => { setIx(nearest(data.x, x)); setIt(nearest(data.T_K, y)); };
  const phasesHere = cell.map(c => ({ name: data.phases[c[0]], np: c[1], x: c[2], dot: PHASE_DOT[c[0] % PHASE_DOT.length], apf: data.atoms_per_formula?.[data.phases[c[0]]] }));
  const xsHere = phasesHere.map(p => p.x);
  const coolingStack = rows.map(row => row[ix]);
  return <div className="phase-map">
    <div className="legend-row">
      {modes.length > 1 && <Segmented label="Model setting" value={mode} onChange={setMode} options={modes.map(m => [m, modeLabels?.[m] ?? m] as [string, string])} />}
      <p className="caption">Click a point, or use the sliders. Colours mark which phases are present, named from low to high composition{data.system === 'Ni-Nb' ? ' (so L + δ, with liquid on the Ni-rich side, and δ + L are different regions)' : ''}. Edges are only as sharp as one grid step{data.system === 'Ni-Nb' ? '; a line compound narrower than that, like NbNi₈, shows up only as the edge between two regions' : ''}. Play cools or heats along the selected composition.</p>
    </div>
    <div className="pm-grid">
      <Plot title={`${data.system} equilibrium grid`} desc={`Each cell is a saved equilibrium at one temperature and overall composition, coloured by the phases present. The selected cell shows its tie line.`}
        height={430} xDomain={[0, 1]} yDomain={[data.T_K[0] - dT / 2, data.T_K.at(-1)! + dT / 2]} xLabel={`overall x(${el})`} yLabel="T (K)" yFormat={v => `${v}`} onPick={pick}>
        {({ x, y }) => <>
          {rows.map((row, i) => row.map((c, j) => <rect key={`${i}-${j}`} x={x(data.x[j] - dx / 2)} y={y(data.T_K[i] + dT / 2)} width={x(dx) - x(0) + 0.6} height={y(0) - y(dT) + 0.6} fill={colour[key(c, data.phases)]} />))}
          {labels.map(l => <text key={l.k} className="pm-label" x={x(l.x)} y={y(l.T)} textAnchor="middle">{l.k}</text>)}
          {gapTops.map((g, k) => <g key={g.m}><line className={`pm-gaptop ${g.m === mode ? 'is-current' : ''}`} x1={x(0)} x2={x(1)} y1={y(g.T)} y2={y(g.T)} /><text className="pm-gaplabel" x={k === 0 ? x(1) - 4 : x(0) + 4} y={k === 0 ? y(g.T) - 5 : y(g.T) + 13} textAnchor={k === 0 ? 'end' : 'start'}>{modeLabels?.[g.m] ?? g.m}: highest two-FCC row {g.T} K</text></g>)}
          <line className="pm-path" x1={x(X)} x2={x(X)} y1={y(data.T_K[0])} y2={y(data.T_K.at(-1)!)} />
          {phasesHere.length > 1 && <line className="tie" x1={x(Math.min(...xsHere))} x2={x(Math.max(...xsHere))} y1={y(T)} y2={y(T)} />}
          {phasesHere.map((p, i) => <circle key={i} className="pm-phase" cx={x(p.x)} cy={y(T)} r="5" style={{ fill: p.dot }} />)}
          <rect className="pm-selected" x={x(X - dx / 2)} y={y(T + dT / 2)} width={x(dx) - x(0)} height={y(0) - y(dT)} />
        </>}
      </Plot>
      <Plot compact title="Phase amounts along the cooling path" desc="Stacked saved phase amounts at the selected overall composition, at every temperature." height={430}
        xDomain={[0, 1]} yDomain={[data.T_K[0] - dT / 2, data.T_K.at(-1)! + dT / 2]} xTicks={[0, 0.5, 1]} xLabel="amount (mol atoms in phase / mol atoms)" yLabel="T (K)" yFormat={v => `${v}`} margin={{ top: 18, right: 12, bottom: 40, left: 46 }}>
        {({ x, y }) => <>
          {coolingStack.map((c, i) => { let start = 0; return c.map((p, k) => { const x0 = start; start += p[1]; return <rect key={`${i}-${k}`} x={x(x0)} y={y(data.T_K[i] + dT / 2)} width={Math.max(0, x(p[1]) - x(0))} height={y(0) - y(dT) + 0.5} style={{ fill: PHASE_DOT[p[0] % PHASE_DOT.length], opacity: 0.75 }} />; }); })}
          <line className="cursor" x1={x(0)} x2={x(1)} y1={y(T)} y2={y(T)} />
        </>}
      </Plot>
    </div>
    <p className="site-legend">Amounts chart: {[...new Set(rows.flat().flat().map(c => c[0]))].sort((p, q) => p - q).map(i => <span key={i}><span className="occ-dot" style={{ background: PHASE_DOT[i % PHASE_DOT.length] }} /> {data.phases[i]} </span>)}</p>
    <div className="control-bar slider-stack">
      <label id="pm-T" className="control-label">Temperature <strong>{T} K</strong></label>
      <RecordSlider index={it} max={data.T_K.length - 1} onChange={setIt} labelId="pm-T" valueText={`${T} kelvin`} />
      <label id="pm-x" className="control-label">Overall x({el}) <strong>{X.toFixed(4)}</strong></label>
      <RecordSlider index={ix} max={data.x.length - 1} onChange={setIx} labelId="pm-x" valueText={`overall ${el} fraction ${X.toFixed(4)}`} />
      <div className="control-row"><Player index={it} max={data.T_K.length - 1} onChange={setIt} label="Cool or heat at this composition" interval={220} />
        <button type="button" className="ghost-button" onClick={() => setIt(data.T_K.length - 1)}>Go to the highest temperature</button></div>
    </div>
    <div className="pm-readout" aria-live="off">
      <LiveStatus text={`${T} K, overall x ${X.toFixed(3)}: ${phasesHere.map(p => `${p.name} ${p.np.toFixed(3)} at x ${p.x.toFixed(3)}`).join('; ')}`} />
      <p className="lab-kicker">{T} K · overall x({el}) = {X.toFixed(4)} · {phasesHere.length === 1 ? 'one phase' : `${phasesHere.length} phases`}</p>
      {data.atoms_per_formula && <Segmented label="Amount basis" value={basis} onChange={setBasis} options={[['atoms', 'mol atoms'], ['formula', 'mol formula units']]} />}
      <table className="data-table"><thead><tr><th scope="col">Phase</th><th scope="col">Amount{basis === 'formula' ? ' (mol formula units per mol atoms)' : ' (mol atoms in the phase / mol atoms)'}</th><th scope="col">x({el}) in the phase</th></tr></thead>
        <tbody>{phasesHere.map((p, i) => <tr key={i}><th scope="row"><span className="occ-dot" style={{ background: p.dot }} /> {p.name}</th>
          <td>{basis === 'formula' && p.apf ? `${(p.np / p.apf).toFixed(5)} (= ${p.np.toFixed(6)} ÷ ${p.apf})` : basis === 'formula' ? `${p.np.toFixed(6)} (1 atom per formula unit)` : p.np.toFixed(6)}</td><td>{p.x.toFixed(6)}</td></tr>)}</tbody></table>
      <p className="caption">{phasesHere.length > 1 ? `The tie line joins the phase compositions; the lever rule gives the amounts. Pure ${other} is on the left, pure ${el} on the right.` : 'A single phase: its composition equals the overall composition.'} Saved values rounded to {data.rounding_digits} decimals; {data.T_K.length} temperatures × {data.x.length} compositions at {data.P_Pa} Pa.{basis === 'formula' ? ' Balances always use mol atoms; formula units are only another way of counting the same amount.' : ''}</p>
    </div>
  </div>;
}
