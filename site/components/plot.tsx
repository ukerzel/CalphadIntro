'use client';
/** Coordinate drawing for exported values. Scales map numbers to pixels; nothing here evaluates a model. */
import { useCallback, useEffect, useId, useRef, useState } from 'react';
import type { ReactNode } from 'react';

export type Scale = ((value: number) => number) & { invert: (pixel: number) => number; domain: [number, number]; range: [number, number] };

export function linear(domain: [number, number], range: [number, number]): Scale {
  const [d0, d1] = domain, [r0, r1] = range, span = d1 - d0 || 1;
  const scale = ((value: number) => r0 + (value - d0) / span * (r1 - r0)) as Scale;
  scale.invert = pixel => d0 + (pixel - r0) / (r1 - r0 || 1) * span;
  scale.domain = domain; scale.range = range;
  return scale;
}

export function ticks(min: number, max: number, count = 5): number[] {
  const raw = (max - min) / Math.max(count, 1), power = 10 ** Math.floor(Math.log10(raw)), unit = raw / power;
  const step = (unit >= 5 ? 10 : unit >= 2 ? 5 : unit >= 1 ? 2 : 1) * power;
  const values: number[] = [];
  for (let value = Math.ceil(min / step) * step; value <= max + step * 1e-9; value += step) values.push(Math.round(value / step) * step || 0);
  return values;
}

export const path = (points: [number, number][]) => points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`).join('');

/** Width of the wrapper, so that axis text stays legible instead of scaling with a viewBox. */
export function useWidth(initial = 720): [(node: HTMLDivElement | null) => void, number] {
  const [width, setWidth] = useState(initial);
  const observer = useRef<ResizeObserver | null>(null);
  const ref = useCallback((node: HTMLDivElement | null) => {
    observer.current?.disconnect();
    if (!node || typeof ResizeObserver === 'undefined') return;
    observer.current = new ResizeObserver(([entry]) => setWidth(Math.max(260, Math.round(entry.contentRect.width))));
    observer.current.observe(node);
  }, []);
  useEffect(() => () => observer.current?.disconnect(), []);
  return [ref, width];
}

export type Frame = { x: Scale; y: Scale; width: number; height: number; left: number; top: number; right: number; bottom: number };

type PlotProps = {
  title: string; desc: string; height: number; xDomain: [number, number]; yDomain: [number, number];
  xLabel: string; yLabel: string; xTicks?: number[]; yTicks?: number[];
  xFormat?: (value: number) => string; yFormat?: (value: number) => string;
  margin?: { top: number; right: number; bottom: number; left: number };
  onScrub?: (value: number) => void; onHover?: (value: number | null) => void; onPick?: (x: number, y: number) => void;
  children: (frame: Frame) => ReactNode; overlay?: (frame: Frame) => ReactNode; className?: string; compact?: boolean;
};

const minus = (text: string) => text.replace(/^-/, '−');
const defaultFormat = (value: number) => minus(value.toLocaleString('en-US', { maximumFractionDigits: 2 }));

export default function Plot({ title, desc, height, xDomain, yDomain, xLabel, yLabel, xTicks, yTicks, xFormat = defaultFormat, yFormat = defaultFormat, margin, onScrub, onHover, onPick, children, overlay, className, compact }: PlotProps) {
  const [ref, width] = useWidth(compact ? 360 : 720);
  const clip = useId().replace(/:/g, '');
  const m = margin ?? { top: 18, right: 22, bottom: compact ? 40 : 50, left: compact ? 58 : 76 };
  const x = linear(xDomain, [m.left, width - m.right]), y = linear(yDomain, [height - m.bottom, m.top]);
  const frame: Frame = { x, y, width, height, left: m.left, top: m.top, right: width - m.right, bottom: height - m.bottom };
  const pressed = useRef(false);
  const domainAt = (event: React.PointerEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    return x.invert(m.left + (event.clientX - box.left) / (box.width || 1) * (frame.right - frame.left));
  };
  const yAt = (event: React.PointerEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    return y.invert(m.top + (event.clientY - box.top) / (box.height || 1) * (frame.bottom - frame.top));
  };
  const xs = xTicks ?? ticks(xDomain[0], xDomain[1], width < 480 ? 4 : 6);
  const ys = yTicks ?? ticks(yDomain[0], yDomain[1], compact ? 4 : 5);
  return <div ref={ref} className={`plot ${className ?? ''}`}>
    <svg data-plot width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
      <title>{title}</title><desc>{desc}</desc>
      <defs><clipPath id={clip}><rect x={frame.left} y={frame.top - 2} width={frame.right - frame.left} height={frame.bottom - frame.top + 4} /></clipPath></defs>
      <g className="plot-grid">
        {ys.map(value => <g key={`y${value}`}><line x1={frame.left} x2={frame.right} y1={y(value)} y2={y(value)} /><text x={frame.left - 10} y={y(value)} dy="0.32em" textAnchor="end">{yFormat(value)}</text></g>)}
        {xs.map(value => <g key={`x${value}`}><line className="plot-tick" x1={x(value)} x2={x(value)} y1={frame.bottom} y2={frame.bottom + 5} /><text x={x(value)} y={frame.bottom + 20} textAnchor="middle">{xFormat(value)}</text></g>)}
        <line className="plot-axis" x1={frame.left} x2={frame.right} y1={frame.bottom} y2={frame.bottom} />
      </g>
      <text className="plot-label" x={(frame.left + frame.right) / 2} y={height - 6} textAnchor="middle">{xLabel}</text>
      <text className="plot-label" x={frame.left} y={10} textAnchor="start">{yLabel}</text>
      <g clipPath={`url(#${clip})`}>{children(frame)}</g>
      {overlay?.(frame)}
      {(onScrub || onHover || onPick) && <rect className="plot-hit" x={frame.left} y={frame.top} width={frame.right - frame.left} height={frame.bottom - frame.top}
        onPointerDown={event => { if (!onScrub && !onPick) return; pressed.current = true; event.currentTarget.setPointerCapture(event.pointerId); onScrub?.(domainAt(event)); onPick?.(domainAt(event), yAt(event)); }}
        onPointerMove={event => { const value = domainAt(event); if (pressed.current) { onScrub?.(value); onPick?.(value, yAt(event)); } onHover?.(value); }}
        onPointerUp={() => { pressed.current = false; }} onPointerCancel={() => { pressed.current = false; }}
        onPointerLeave={() => onHover?.(null)} />}
    </svg>
  </div>;
}

/** A marker that glides between exported positions (CSS transform transition). */
export function Mark({ x, y, r = 6, className = '', label }: { x: number; y: number; r?: number; className?: string; label?: string }) {
  return <g className={`mark ${className}`} style={{ transform: `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px)` }}>
    <circle r={r + 5} className="mark-halo" /><circle r={r} />
    {label && <text y={-r - 9} textAnchor="middle">{label}</text>}
  </g>;
}

export function nearest(values: number[], target: number): number {
  let best = 0;
  for (let i = 1; i < values.length; i++) if (Math.abs(values[i] - target) < Math.abs(values[best] - target)) best = i;
  return best;
}
