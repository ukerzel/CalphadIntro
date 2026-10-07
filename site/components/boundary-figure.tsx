/** Static sketch of the step 04 cell geometry (counts and areas from the narration). */
export default function BoundaryFigure() {
  const dots = (x0: number, cols: number, cls: string) => Array.from({ length: cols * 6 }, (_, i) =>
    <circle key={`${x0}-${i}`} className={cls} cx={x0 + (i % cols) * 14} cy={58 + Math.floor(i / cols) * 14} r="4.2" />);
  return <figure className="cell-figure">
    <svg viewBox="0 0 640 210" role="img" aria-label="Periodic cell: a bulk region of 8000 sites between two boundaries of 100 sites and 20 square nanometres each; the pattern repeats left and right.">
      <rect className="cf-cell" x="40" y="40" width="560" height="104" rx="10" />
      <line className="cf-period" x1="40" x2="40" y1="24" y2="160" /><line className="cf-period" x1="600" x2="600" y1="24" y2="160" />
      <text className="cf-small" x="20" y="100" textAnchor="middle">…</text><text className="cf-small" x="620" y="100" textAnchor="middle">…</text>
      {dots(62, 16, 'cf-bulk')}{dots(352, 16, 'cf-bulk')}
      <rect className="cf-gb" x="290" y="44" width="40" height="96" rx="6" />{dots(303, 2, 'cf-gbsite')}
      <rect className="cf-gb" x="580" y="44" width="40" height="96" rx="6" />{dots(593, 2, 'cf-gbsite')}
      <text className="cf-label" x="170" y="172" textAnchor="middle">bulk: 8000 sites in total, B fraction xb</text>
      <text className="cf-label cf-gbtext" x="310" y="30" textAnchor="middle">boundary 1</text>
      <text className="cf-label cf-gbtext" x="600" y="30" textAnchor="end">boundary 2</text>
      <text className="cf-small" x="320" y="192" textAnchor="middle">each boundary: 100 sites, 20 nm², B occupancy θ · the cell repeats; boundary 2 sits on its edge</text>
    </svg>
    <figcaption>Sketch of the cell (not to scale): dots stand for many sites each.</figcaption>
  </figure>;
}
