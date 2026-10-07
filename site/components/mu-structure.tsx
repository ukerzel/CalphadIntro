'use client';
import { useEffect, useId, useMemo, useState } from 'react';
import RecordSlider from '@/components/record-slider';
import { Player, Segmented } from '@/components/lab-frame';
import { loadLearningJSON } from '@/lib/materials';

export type Occ = 'Ni' | 'Nb' | 'mix';
type Site = { site: string; wyckoff: string; atoms_per_cell: number; sublattice: string; CN: number; nearest_A: number; element_Nb7Ni6: string };
export type MuStructureData = { name: string; space_group: string; a_A: number; c_A: number; atoms_per_hexagonal_cell: number; sites: Site[];
  atoms: { site: string; wyckoff: string; xyz_A: [number, number, number] }[]; source: string };
export const muStructurePath = 'self_study/generated/mu_structure.json';

/** Database sublattice (index into the 2:2:2:6:1 site boxes) for each crystal site, as far as the site counts fix it. */
const SUBLATTICE_OF: Record<string, number | null> = { '3a': 4, '18h': 3, '6c_1': null, '6c_2': null, '6c_3': null };
const RADIUS: Record<Occ, number> = { Nb: 1.46, Ni: 1.25, mix: 1.36 }; // Å, metallic radii; drawn at 45 %

export default function MuStructure(props: { occ: Occ[]; selected: number | null }) {
  const [data, setData] = useState<MuStructureData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<MuStructureData>(muStructurePath).then(v => { if (active) setData(v); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <p className="caption" role="alert">Structure sketch unavailable: {error}.</p>;
  if (!data) return <p className="loading" role="status">Loading the structure sketch…</p>;
  return <MuStructureView data={data} {...props} />;
}

/** Ball sketch of the μ-phase prototype cell, coloured by the site-box occupation. Geometry is exported; the browser only rotates and projects it. */
export function MuStructureView({ data, occ, selected, initialStep = 3 }: { data: MuStructureData; occ: Occ[]; selected: number | null; initialStep?: number }) {
  const [view, setView] = useState<'side' | 'top'>('side');
  const [step, setStep] = useState(initialStep);
  const uid = useId(), ids = { title: `${uid}-title`, desc: `${uid}-desc`, rot: `${uid}-rot` }; // rotation about c, 10° per step
  const twoSiteSame = occ[0] === occ[1] && occ[1] === occ[2];
  const occOf = (site: string): Occ | 'unknown' => { const s = SUBLATTICE_OF[site]; return s === null ? (twoSiteSame ? occ[0] : 'unknown') : occ[s]; };
  const isSelected = (site: string) => selected !== null && (SUBLATTICE_OF[site] === selected || (SUBLATTICE_OF[site] === null && selected <= 2));
  const projected = useMemo(() => {
    const n = data.atoms.length, mean = [0, 1, 2].map(k => data.atoms.reduce((s, a) => s + a.xyz_A[k], 0) / n);
    const t = step * Math.PI / 18, c = Math.cos(t), s = Math.sin(t);
    return data.atoms.map(a => {
      const [x, y, z] = a.xyz_A.map((v, k) => v - mean[k]);
      const u = c * x - s * y, w = s * x + c * y; // rotated in the basal plane
      return view === 'side' ? { a, h: z, v: -w, d: u } : { a, h: u, v: -w, d: z };
    }).sort((p, q) => p.d - q.d);
  }, [data, step, view]);
  const span = view === 'side' ? data.c_A / 2 + 2.5 : 8.5, height = view === 'side' ? 6.5 : 8.5;
  const W = 640, H = view === 'side' ? 210 : 380, k = Math.min(W / (2 * span), H / (2 * height));
  const dRange = Math.max(...projected.map(p => Math.abs(p.d))) || 1;
  const counts = { Nb: 0, Ni: 0 } as Record<'Nb' | 'Ni', number>;
  return <figure className="mu-structure">
    <div className="legend-row">
      <Segmented label="View" value={view} onChange={setView} options={[['side', 'Side view (c axis across)'], ['top', 'Top view (down the c axis)']]} />
    </div>
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby={`${ids.title} ${ids.desc}`} className="mu-svg">
      <title id={ids.title}>μ phase structure sketch</title>
      <desc id={ids.desc}>{`${data.atoms.length} atoms from 2 × 2 hexagonal cells of the ${data.name} structure, coloured by the occupation chosen in the site boxes.`}</desc>
      {projected.map((p, i) => {
        const o = occOf(p.a.site); const fade = 0.55 + 0.45 * (p.d + dRange) / (2 * dRange);
        if (o === 'Nb' || o === 'Ni') counts[o] += 1;
        const r = 0.45 * k * (o === 'unknown' ? 1.36 : RADIUS[o]);
        return <circle key={i} cx={W / 2 + p.h * k} cy={H / 2 + p.v * k} r={r} className={`mu-atom occ-${o}${isSelected(p.a.site) ? ' is-selected' : ''}${selected !== null && !isSelected(p.a.site) ? ' is-dim' : ''}`} style={{ opacity: fade }} />;
      })}
      {view === 'side' && <g className="mu-axis"><line x1={W / 2 - data.c_A / 2 * k} x2={W / 2 + data.c_A / 2 * k} y1={H - 12} y2={H - 12} /><text x={W / 2} y={H - 16} textAnchor="middle">c = {data.c_A} Å (one cell, three formula units of 13 atoms)</text></g>}
    </svg>
    <div className="control-bar slider-stack">
      <label id={ids.rot} className="control-label">Turn about the c axis <strong>{step * 10}°</strong></label>
      <RecordSlider index={step} max={35} onChange={setStep} labelId={ids.rot} valueText={`${step * 10} degrees`} />
      <div className="control-row"><Player index={step} max={35} onChange={setStep} label="Spin" interval={160} /></div>
    </div>
    <table className="data-table compact"><thead><tr><th scope="col">Crystal site</th><th scope="col">Atoms per cell</th><th scope="col">Neighbours</th><th scope="col">Database sublattice</th></tr></thead>
      <tbody>{data.sites.map(s => <tr key={s.site} className={isSelected(s.site) ? 'is-selected' : ''}><th scope="row">{s.wyckoff}{s.wyckoff === '6c' ? ` (${s.site.slice(-1)})` : ''}</th><td>{s.atoms_per_cell}</td><td>{s.CN}</td><td>{s.sublattice}</td></tr>)}</tbody></table>
    <figcaption className="caption">
      A sketch, not a Ni–Nb measurement: positions and lattice spacing are those of the published μ-phase prototype structure.
      Per formula unit the database has 2 + 2 + 2 + 6 + 1 sites; per cell (3 formula units) the crystal has three sites with 6 atoms, one with 18 and one with 3.
      So the 6-site and 1-site sublattices sit on the 18-atom and 3-atom crystal sites. The three 2-site sublattices sit on the three 6-atom sites, but the database
      file does not say which is which: unless all three 2-site boxes hold the same element, those atoms are drawn grey. Drawn here: {counts.Nb} Nb, {counts.Ni} Ni.
      Positions: the Fe₇W₆ prototype (Arnfelt and Westgren 1935), from the AFLOW library of crystal prototypes.
    </figcaption>
  </figure>;
}
