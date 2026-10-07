/** Sketch: what is held fixed decides which energy is minimised. */
export default function ConstraintsFigure() {
  const panels: [string, string, string, string][] = [
    ['Isolated', 'fixed U, V, n', 'S is maximal', 'isolated'],
    ['Rigid box in a heat bath', 'fixed T, V, n', 'F is minimal', 'bath'],
    ['Piston in a heat bath', 'fixed T, p, n', 'G is minimal (this course)', 'piston'],
    ['Open to a reservoir', 'fixed T, p, μ, sites', 'G − Σ μn is minimal (step 04)', 'open'],
  ];
  return <figure className="constraints-figure">
    <div className="constraints-grid">{panels.map(([title, fixed, rule, kind]) => <div key={kind} className="constraint-card">
      <svg viewBox="0 0 120 84" aria-hidden>
        {kind !== 'isolated' && <rect className="cf-bath" x="6" y="6" width="108" height="72" rx="10" />}
        {kind === 'isolated' && <rect className="cf-wall-thick" x="28" y="16" width="64" height="52" rx="4" />}
        {(kind === 'bath' || kind === 'piston') && <rect className="cf-wall" x="34" y={kind === 'piston' ? 30 : 20} width="52" height={kind === 'piston' ? 40 : 46} rx="3" />}
        {kind === 'piston' && <><rect className="cf-piston" x="34" y="24" width="52" height="7" /><rect className="cf-weight" x="50" y="12" width="20" height="12" rx="2" /></>}
        {kind === 'open' && <><rect className="cf-wall cf-porous" x="34" y="20" width="52" height="46" rx="3" /><path className="cf-arrow" d="M18,43 L32,43 M28,39 L32,43 L28,47" /><path className="cf-arrow" d="M102,43 L88,43 M92,39 L88,43 L92,47" /></>}
        {Array.from({ length: 6 }, (_, i) => <circle key={i} className="cf-atom" cx={44 + (i % 3) * 16} cy={kind === 'piston' ? 44 + Math.floor(i / 3) * 14 : 36 + Math.floor(i / 3) * 16} r="4" />)}
      </svg>
      <strong>{title}</strong><span>{fixed}</span><em>{rule}</em>
    </div>)}</div>
    <figcaption>Sketch: what you hold fixed decides which energy the equilibrium minimises (or, for an isolated system, which quantity it maximises).</figcaption>
  </figure>;
}
