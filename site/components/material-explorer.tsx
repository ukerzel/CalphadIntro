'use client';
import { useEffect, useState } from 'react';
import LabFrame, { Segmented } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { loadMaterial } from '@/lib/materials';
import type { CuNiResults, NiNbResults, Sample } from '@/lib/materials';
import { num, sci } from '@/lib/format';
import PhaseMap from '@/components/phase-map';
import MuStructure, { type Occ } from '@/components/mu-structure';

export default function MaterialExplorer({ id }: { id: 'cuni' | 'ninb' }) {
  const [data, setData] = useState<CuNiResults | NiNbResults | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadMaterial<CuNiResults | NiNbResults>(id).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, [id]);
  if (error) return <div className="notice" role="alert"><h3>Results unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the results…</p>;
  return id === 'cuni' ? <CuNi data={data as CuNiResults} /> : <NiNb data={data as NiNbResults} />;
}

const phaseTone = (phase: string) => ({ LIQUID: 'liquid', FCC_A1: 'fcc', DELTA: 'delta', MU_PHASE: 'mu', BCC_A2: 'bcc', NBNI8: 'nbni8' } as Record<string, string>)[phase] ?? 'other';

const nextOcc: Record<Occ, Occ> = { Ni: 'Nb', Nb: 'mix', mix: 'Ni' };
/** Atom bookkeeping sketch for one formula unit: counts sites only, no energies. */
export function SiteBoxes({ name, sizes, presets, value, onValue, onSelect }: { name: string; sizes: number[]; presets: [string, Occ[]][];
  value?: Occ[]; onValue?: (occ: Occ[]) => void; onSelect?: (sublattice: number | null) => void }) {
  const [own, setOwn] = useState<Occ[]>(presets[0][1]);
  const occ = value ?? own;
  const setOcc = (next: Occ[] | ((previous: Occ[]) => Occ[])) => { const v = typeof next === 'function' ? next(occ) : next; setOwn(v); onValue?.(v); };
  const total = sizes.reduce((a, b) => a + b, 0);
  const nb = sizes.reduce((sum, size, i) => sum + size * (occ[i] === 'Nb' ? 1 : occ[i] === 'mix' ? 0.5 : 0), 0);
  const label = occ.map(o => o === 'mix' ? 'Nb,Ni' : o.toUpperCase()).join(' : ');
  const uniform = occ.every(o => o === occ[0]) && occ[0] !== 'mix';
  return <article className="site-card">
    <h4>{name}</h4>
    <div className="preset-row" role="group" aria-label={`${name} presets`}>{presets.map(([text, value]) => <button key={text} type="button" className="ghost-button" aria-pressed={value.join() === occ.join()} onClick={() => setOcc(value)}>{text}</button>)}</div>
    <div className="site-row">{sizes.map((size, i) => <button key={i} type="button" className={`sublattice-btn occ-${occ[i]}`} onClick={() => { setOcc(previous => previous.map((o, k) => k === i ? nextOcc[o] : o)); onSelect?.(i); }}
      onMouseEnter={() => onSelect?.(i)} onFocus={() => onSelect?.(i)}
      aria-label={`Sublattice ${i + 1}, ${size} site${size > 1 ? 's' : ''}: ${occ[i] === 'mix' ? 'half Nb, half Ni' : occ[i]}. Click to change.`}>
      <span className="site-boxes">{Array.from({ length: size }, (_, k) => <i key={k} />)}</span>
      <small>sublattice {i + 1} · {size} site{size > 1 ? 's' : ''}</small>
    </button>)}</div>
    <dl className="readouts compact" aria-live="polite">
      <div className="readout-item"><dt>Occupation</dt><dd className="mono">{label}</dd></div>
      <div className="readout-item"><dt>Atoms per formula unit · Nb atoms</dt><dd>{total} · {nb}</dd></div>
      <div className="readout-item tone-key"><dt>x(Nb) in this arrangement</dt><dd>{nb} / {total} = {(nb / total).toFixed(3)}</dd></div>
    </dl>
    <p className="caption">{uniform ? 'One element on every sublattice: a hypothetical endmember, a building block of the model rather than a stable compound.' : occ.includes('mix') ? 'A mixed sublattice moves the composition between the endmembers; this is how the phase spans a composition range.' : 'An ordered arrangement; other arrangements can give the same x(Nb).'}</p>
    <p className="site-legend"><span className="occ-dot occ-Ni" /> Ni <span className="occ-dot occ-Nb" /> Nb <span className="occ-dot occ-mix" /> mixed</p>
  </article>;
}

const MU_PRESETS: [string, Occ[]][] = [['Nb₇Ni₆, Ni on the 6-site sublattice', ['Nb', 'Nb', 'Nb', 'Ni', 'Nb']], ['also 7 Nb: Nb on the 6- and 1-site sublattices', ['Ni', 'Ni', 'Ni', 'Nb', 'Nb']], ['all Ni (the endmember in the energy table)', ['Ni', 'Ni', 'Ni', 'Ni', 'Ni']], ['all Nb', ['Nb', 'Nb', 'Nb', 'Nb', 'Nb']]];
/** μ-phase site boxes beside the structure sketch: clicking or hovering a sublattice highlights its crystal sites. */
export function MuSites() {
  const [occ, setOcc] = useState<Occ[]>(MU_PRESETS[0][1]), [selected, setSelected] = useState<number | null>(null);
  return <div className="mu-sites" onMouseLeave={() => setSelected(null)}>
    <SiteBoxes name="μ phase (MU_PHASE)" sizes={[2, 2, 2, 6, 1]} presets={MU_PRESETS} value={occ} onValue={setOcc} onSelect={setSelected} />
    <MuStructure occ={occ} selected={selected} />
  </div>;
}

/** Composition axis with phase compositions and saved amounts; it draws, it does not sum. */
function Balance({ sample, element, other }: { sample: Sample; element: 'NI' | 'NB'; other: string }) {
  const bulk = (element === 'NI' ? sample.X_NI : sample.X_NB)!;
  const phases = sample.phases.map(p => ({ ...p, x: (element === 'NI' ? p.x_NI : p.x_NB)! }));
  const X = (value: number) => 40 + value * 520;
  const xsorted = [...phases].sort((a, b) => a.x - b.x);
  let start = 0;
  return <figure className="balance">
    <svg viewBox="0 0 600 190" role="img" aria-label={`Saved sample at ${sample.T_K} K: ${phases.map(p => `${p.phase} amount ${p.atom_mole_fraction.toFixed(4)} at x(${element}) ${p.x.toFixed(4)}`).join('; ')}`}>
      <text className="balance-caption" x="40" y="18">Phase amounts · atom-mole fractions (bar length)</text>
      {phases.map((p, i) => { const x0 = start; start += p.atom_mole_fraction; return <g key={i} className={`amount tone-${phaseTone(p.phase)}`}>
        <rect x={X(0) + x0 * 520} y="28" width={Math.max(1, p.atom_mole_fraction * 520 - 2)} height="26" rx="5" />
        {p.atom_mole_fraction > 0.12 && <text x={X(0) + (x0 + p.atom_mole_fraction / 2) * 520} y="45" textAnchor="middle">{p.phase} · {p.atom_mole_fraction.toFixed(3)}</text>}
      </g>; })}
      <line className="axis" x1={X(0)} x2={X(1)} y1="130" y2="130" />
      {[0, 0.25, 0.5, 0.75, 1].map(t => <line key={t} className="axis" x1={X(t)} x2={X(t)} y1="130" y2="136" />)}
      <text className="tick" x={X(0)} y="154" textAnchor="middle">0</text><text className="tick" x={X(1)} y="154" textAnchor="middle">1</text>
      <text className="tick" x={X(0)} y="176" textAnchor="start">pure {other}</text><text className="tick" x={X(1)} y="176" textAnchor="end">pure {element === 'NI' ? 'Ni' : 'Nb'}</text>
      <text className="tick" x="300" y="176" textAnchor="middle">x({element === 'NI' ? 'Ni' : 'Nb'}) within each phase · ticks every 0.25</text>
      {xsorted.length > 1 && <line className="tie" x1={X(xsorted[0].x)} x2={X(xsorted.at(-1)!.x)} y1="114" y2="114" />}
      {phases.map((p, i) => <g key={i} className={`phase-dot tone-${phaseTone(p.phase)}`} style={{ transform: `translate(${X(p.x)}px, 114px)` }}><circle r="8" /><text y="-14" textAnchor="middle">{p.phase}</text></g>)}
      <g className="fulcrum" style={{ transform: `translate(${X(bulk)}px, 118px)` }}><path d="M0,0 L7,13 L-7,13 Z" /><text y="30" textAnchor="middle">bulk {bulk.toFixed(4)}</text></g>
    </svg>
    <figcaption>Dots: composition of each phase. Triangle: overall alloy composition. Check the balance yourself: multiply each amount by its composition and add.</figcaption>
  </figure>;
}

function PhaseTable({ sample, element }: { sample: Sample; element: 'NI' | 'NB' }) {
  return <table className="data-table"><caption>{sample.T_K} K · full precision</caption>
    <thead><tr><th scope="col">Phase</th><th scope="col">Atom-mole amount fraction</th><th scope="col">Phase x({element === 'NI' ? 'Ni' : 'Nb'})</th></tr></thead>
    <tbody>{sample.phases.map((p, i) => <tr key={i}><th scope="row">{p.phase}</th><td>{p.atom_mole_fraction}</td><td>{element === 'NI' ? p.x_NI : p.x_NB}</td></tr>)}</tbody></table>;
}

function Chips({ requested, observed }: { requested: string[]; observed: string[] }) {
  return <ul className="phase-chips" aria-label="Enabled phases">{requested.map(phase => <li key={phase} className={observed.includes(phase) ? 'is-seen' : 'is-unseen'}>{phase}<span>{observed.includes(phase) ? 'appears' : 'allowed, never appears'}</span></li>)}</ul>;
}

export function CuNi({ data }: { data: CuNiResults }) {
  const [mode, setMode] = useState<'magnetic_on' | 'magnetic_off'>('magnetic_on');
  const result = data.equilibrium[mode];
  const keys = Object.keys(result.samples).sort((a, b) => result.samples[a].T_K - result.samples[b].T_K);
  const [key, setKey] = useState('600');
  const sample = result.samples[key] ?? result.samples[keys[0]];
  const explore = <div className="material-grid">
    <h3 className="panel-title" id="lab-map">The phase diagram, point by point</h3>
    <PhaseMap path="self_study/generated/cuni_grid.json" modeLabels={{ magnetic_on: 'Magnetic on', magnetic_off: 'Magnetic off' }} />
    <h3 className="panel-title" id="lab-samples">Saved samples at x(Ni) = 0.5</h3>
    <div className="material-controls">
      <Segmented label="Magnetic contribution" value={mode} onChange={setMode} options={[['magnetic_on', 'Magnetic on'], ['magnetic_off', 'Magnetic off']]} />
      <Segmented label="Temperature" value={key} onChange={setKey} options={keys.map(k => [k, `${result.samples[k].T_K} K${k === 'FCC_liquid_example' ? ' · L+FCC' : ''}`] as [string, string])} />
    </div>
    <Balance sample={sample} element="NI" other="Cu" />
    <PhaseTable sample={sample} element="NI" />
    <dl className="facts">
      <div><dt>Highest sampled temperature with two FCC compositions</dt><dd>{result.highest_sampled_T_with_two_FCC_K} K <span>on a 20 K grid, so approximate</span></dd></div>
      <div><dt>Phases found near the pure ends</dt><dd>{Object.entries(result.near_pure_phase_sets).map(([x, phases]) => `x(Ni) = ${x}: ${phases.join(', ')}`).join(' · ')}<span>somewhere between {data.T_K[0]} and {data.T_K.at(-1)} K, not all at once</span></dd></div>
    </dl>
    <Chips requested={data.phases_requested} observed={result.phases_observed} />
  </div>;
  const model = <div className="model">
    <div className="equations">
      <Eq label="Balance for each element" tex={String.raw`\sum_i f_i\,x_i(\mathrm{Ni}) = z(\mathrm{Ni}), \qquad \sum_i f_i = 1`} />
      <Eq label="Magnetic control" tex={String.raw`G_{\mathrm{total}} = G_{\mathrm{chemical}} + G_{\mathrm{magnetic}} \quad \text{(already included: never add it again)}`} />
    </div>
    <p>MagneticOffModel overrides only the magnetic energy at model assembly; references, excess terms, grid, phase list and source parameters stay fixed. It is a computational control, not a newly assessed nonmagnetic alloy.</p>
  </div>;
  return <LabFrame kicker="Step 05 · calculated in advance" title="Cu–Ni phase balances, magnetic on and off"
    conditions={[`${num(data.P_Pa)} Pa`, 'overall x(Ni) = 0.5', 'LIQUID, FCC_A1, BCC_A2, HCP_A3 allowed']}
    explore={explore} model={model} record={<Provenance data={data} checks={result.balance_checks} file="/learning/materials/cuni/results.json" />} />;
}

export function NiNb({ data }: { data: NiNbResults }) {
  const checks = [
    { name: 'δ phase · all Nb', ratio: [1, 1, 2], tone: 'delta', value: data.energy_checks.delta_NB_NB_NB },
    { name: 'μ phase · all Ni', ratio: [2, 2, 2, 6, 1], tone: 'mu', value: data.energy_checks.mu_all_NI },
  ];
  const explore = <div className="material-grid">
    <h3 className="panel-title" id="lab-map">The phase diagram, point by point</h3>
    <PhaseMap path="self_study/generated/ninb_grid.json" />
    <h3 className="panel-title" id="lab-formula">One division, on the right basis</h3>
    <div className="basis-grid">{checks.map(check => { const atoms = check.ratio.reduce((a, b) => a + b, 0); return <article key={check.name} className={`basis-card tone-${check.tone}`}>
      <p className="lab-kicker">Endmember at {data.energy_checks.temperature_K} K</p><h4>{check.name}</h4>
      <p className="caption">Sublattices {check.ratio.join(' : ')} · {atoms} atoms per formula unit</p>
      <dl className="readouts compact">
        <div className="readout-item"><dt>Per mole of formula units</dt><dd className="mono">{num(check.value.formula_J_per_mol, 6)} <span className="readout-unit">J/mol formula</span></dd></div>
        <div className="readout-item divide"><dt>Atoms per formula</dt><dd>÷ {atoms}</dd></div>
        <div className="readout-item tone-key"><dt>Per mole of atoms</dt><dd className="mono">{num(check.value.atom_J_per_mol, 6)} <span className="readout-unit">J/mol atoms</span></dd></div>
      </dl></article>; })}</div>
    <p className="caption">GM and NP are already per mole of atoms; dividing them again would be wrong.</p>
    <h3 className="panel-title" id="lab-sites">Build a formula unit</h3>
    <p className="panel-lede">Click a sublattice to switch it between Ni, Nb and a 50/50 mix. The model allows either element on every sublattice, so several arrangements give the same composition (with different energies). This sketch only counts atoms.</p>
    <div className="basis-grid">
      <SiteBoxes name="δ phase (DELTA)" sizes={[1, 1, 2]} presets={[['NbNi₃, Nb on sublattice 1', ['Nb', 'Ni', 'Ni']], ['NbNi₃, Nb on sublattice 2', ['Ni', 'Nb', 'Ni']], ['all Nb (the endmember in the energy table)', ['Nb', 'Nb', 'Nb']], ['all Ni', ['Ni', 'Ni', 'Ni']]]} />
    </div>
    <h3 className="panel-title" id="lab-mu-structure">Where the μ-phase atoms sit</h3>
    <p className="panel-lede">The same μ site boxes, next to a sketch of the crystal. Hover or click a sublattice to see which atoms it stands for; turn the cell with the slider.</p>
    <MuSites />
    <h3 className="panel-title">A two-phase state at {data.sample.T_K} K</h3>
    <Balance sample={data.sample} element="NB" other="Ni" />
    <PhaseTable sample={data.sample} element="NB" />
    <dl className="facts">
      <div><dt>Phases found near the pure ends</dt><dd>{Object.entries(data.near_pure_phase_sets).map(([x, phases]) => `x(Nb) = ${x}: ${phases.join(', ')}`).join(' · ')}<span>somewhere between {data.T_K[0]} and {data.T_K.at(-1)} K, not all at once</span></dd></div>
    </dl>
    <Chips requested={data.phases_requested} observed={data.phases_observed} />
  </div>;
  const model = <div className="model">
    <div className="equations">
      <Eq label="Formula to atom basis" tex={String.raw`G_{\mathrm{atom}} = \frac{G_{\mathrm{formula}}}{\text{atoms per formula unit}}`} />
      <Eq label="Balance on the atom-mole basis" tex={String.raw`\sum_i \mathrm{NP}_i\,x_i(\mathrm{Nb}) = z(\mathrm{Nb})`} />
    </div>
    <p>δ has three sublattices in ratio 1:1:2 (four atoms per formula) and μ has five in ratio 2:2:2:6:1 (thirteen). Fixed vacancy sites add no real atoms. Model.GM and equilibrium NP are already on the real-atom basis.</p>
  </div>;
  return <LabFrame kicker="Step 06 · calculated in advance" title="Ni–Nb: ordered phases and amount bases"
    conditions={[`${num(data.P_Pa)} Pa`, `sample at ${data.sample.T_K} K`, 'eight phases allowed']}
    explore={explore} model={model} record={<Provenance data={data} checks={data.balance_checks} file="/learning/materials/ninb/results.json" />} />;
}

function Provenance({ data, checks, file }: { data: CuNiResults | NiNbResults; checks: { max_amount_error: number; max_component_error: Record<string, number> }; file: string }) {
  return <div className="record-view">
    <p>Calculated in advance by the course authors from the published database, which is not included here (the optional setup in the lesson explains how to get it).</p>
    <dl className="facts">
      <div><dt>Software</dt><dd>pycalphad {data.pycalphad} · Python {data.python}</dd></div>
      <div><dt>Grid</dt><dd>{data.T_K.length} temperatures · {('X_NI' in data ? data.X_NI : data.X_NB).length} compositions · pdens {data.pdens}</dd></div>
      <div><dt>Largest balance errors</dt><dd className="mono">amount {sci(checks.max_amount_error, 2)} · {Object.entries(checks.max_component_error).map(([el, v]) => `${el} ${sci(v, 2)}`).join(' · ')}</dd></div>
      <div><dt>Database file fingerprint (SHA-256)</dt><dd className="mono">{data.source_sha256}</dd></div>
    </dl>
    <p><a href={file}>Download the full results (JSON)</a></p>
  </div>;
}
