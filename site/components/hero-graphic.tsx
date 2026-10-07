'use client';
import { useEffect, useRef, useState } from 'react';
import type { Bundle } from '@/lib/data';
import { path } from '@/components/plot';

/** Decorative sweep through the exported unary rows. */
export default function HeroGraphic({ bundle }: { bundle: Bundle | null }) {
  const [index, setIndex] = useState(150);
  const node = useRef<SVGSVGElement>(null);
  useEffect(() => {
    if (!bundle || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let frame = 0, last = 0, direction = 1, current = 150, visible = true;
    const observer = typeof IntersectionObserver === 'undefined' ? null : new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
    if (node.current) observer?.observe(node.current);
    const tick = (time: number) => {
      if (visible && time - last > 55) {
        last = time;
        if (current + direction > 200 || current + direction < 0) direction *= -1;
        current += direction;
        setIndex(current);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => { cancelAnimationFrame(frame); observer?.disconnect(); };
  }, [bundle]);
  const W = 640, H = 460, X = (t: number) => 40 + (t - 800) / 400 * (W - 80), Y = (g: number) => 40 + (-5000 - g) / 8000 * (H - 110);
  if (!bundle) return <div className="hero-graphic is-empty" aria-hidden><div className="hero-placeholder" /></div>;
  const records = bundle.unary.records, row = records[index];
  const winner = row.phase_status === 'equal_energy_fractions_underdetermined' ? 'EQUAL' : row.phase_status;
  const gx = X(row.T_K), gy = Y(row.equilibrium.GM);
  return <div className="hero-graphic">
    <svg ref={node} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Animation: the Gibbs energies of SOLID and LIQUID cross at 1000 K; below it SOLID is lower, above it LIQUID is lower.">
      <defs>
        <pattern id="hero-dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" className="hero-dot" /></pattern>
        <linearGradient id="hero-fade" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="currentColor" stopOpacity=".16" /><stop offset="1" stopColor="currentColor" stopOpacity="0" /></linearGradient>
        <filter id="hero-glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6" /></filter>
      </defs>
      <rect width={W} height={H} fill="url(#hero-dots)" />
      <path className="hero-area" d={`${path(records.map(r => [X(r.T_K), Y(r.equilibrium.GM)]))}L${X(1200)},${H - 50}L${X(800)},${H - 50}Z`} fill="url(#hero-fade)" />
      <path className="hero-line hero-solid" d={path(records.map(r => [X(r.T_K), Y(r.gibbs_J_per_mol[0])]))} />
      <path className="hero-line hero-liquid" d={path(records.map(r => [X(r.T_K), Y(r.gibbs_J_per_mol[1])]))} />
      <path className="hero-min-glow" d={path(records.map(r => [X(r.T_K), Y(r.equilibrium.GM)]))} filter="url(#hero-glow)" />
      <path className="hero-min" d={path(records.map(r => [X(r.T_K), Y(r.equilibrium.GM)]))} />
      <text className="hero-tag hero-tag-solid" x={X(1190)} y={Y(records[195].gibbs_J_per_mol[0]) - 12} textAnchor="end">SOLID</text>
      <text className="hero-tag hero-tag-liquid" x={X(1190)} y={Y(records[195].gibbs_J_per_mol[1]) + 26} textAnchor="end">LIQUID</text>
      <line className="hero-scan" x1={gx} x2={gx} y1={30} y2={H - 50} />
      <circle className="hero-point" cx={gx} cy={gy} r="9" />
      <g transform={`translate(${Math.min(gx + 16, W - 170)}, ${Math.max(gy - 64, 30)})`} className="hero-readout">
        <rect width="150" height="46" rx="10" /><text x="14" y="20" className="hero-readout-t">{row.T_K} K</text><text x="14" y="37" className="hero-readout-w">{winner === 'EQUAL' ? 'equal energies' : `${winner} lower`}</text>
      </g>
      <line className="hero-axis" x1={40} x2={W - 40} y1={H - 50} y2={H - 50} />
      {[800, 900, 1000, 1100, 1200].map(t => <text key={t} className="hero-tick" x={X(t)} y={H - 28} textAnchor="middle">{t} K</text>)}
      <text className="hero-tick" x={40} y={22}>G, kJ/mol atoms · invented component A</text>
    </svg>
  </div>;
}
