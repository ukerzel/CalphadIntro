'use client';
import { useEffect, useRef, useState } from 'react';

/** Text for a polite live region that only updates once a value stops changing, so sweeps stay silent. */
export function useSettled<T>(value: T, delay = 700): T {
  const [settled, setSettled] = useState(value);
  useEffect(() => { const timer = setTimeout(() => setSettled(value), delay); return () => clearTimeout(timer); }, [value, delay]);
  return settled;
}
export function LiveStatus({ text }: { text: string }) {
  const settled = useSettled(text);
  return <p className="sr-only" aria-live="polite" aria-atomic="true">{settled}</p>;
}
import type { ReactNode } from 'react';
import { Tabs } from 'radix-ui';
import { Pause, Play, StepBack, StepForward } from 'lucide-react';

export default function LabFrame({ kicker, title, conditions, actions, explore, model, record }: {
  kicker: string; title: string; conditions: string[]; actions?: ReactNode; explore: ReactNode; model: ReactNode; record: ReactNode;
}) {
  return <section className="lab" aria-label={`${title} · interactive lab`}>
    <header className="lab-head">
      <div><p className="lab-kicker">{kicker}</p><h2 className="lab-title">{title}</h2></div>
      {actions && <div className="lab-actions">{actions}</div>}
    </header>
    <ul className="chips" aria-label="Conditions">{conditions.map(item => <li key={item}>{item}</li>)}</ul>
    <Tabs.Root defaultValue="explore" className="lab-tabs">
      <Tabs.List className="tab-list" aria-label="Lab views">
        <Tabs.Trigger value="explore">Explore</Tabs.Trigger>
        <Tabs.Trigger value="model">Model</Tabs.Trigger>
        <Tabs.Trigger value="record">Data</Tabs.Trigger>
      </Tabs.List>
      <Tabs.Content value="explore" className="tab-panel">{explore}</Tabs.Content>
      <Tabs.Content value="model" className="tab-panel">{model}</Tabs.Content>
      <Tabs.Content value="record" className="tab-panel">{record}</Tabs.Content>
    </Tabs.Root>
  </section>;
}

/** Steps through the exported rows one by one. */
export function Player({ index, max, onChange, label, interval = 40 }: { index: number; max: number; onChange: (index: number) => void; label: string; interval?: number }) {
  const [playing, setPlaying] = useState(false);
  const state = useRef({ index, direction: 1, last: 0 });
  const change = useRef(onChange);
  state.current.index = index;
  change.current = onChange;
  useEffect(() => {
    if (!playing) return;
    let frame = 0;
    const tick = (time: number) => {
      const s = state.current;
      if (time - s.last >= interval) {
        s.last = time;
        let next = s.index + s.direction;
        if (next > max || next < 0) { s.direction *= -1; next = s.index + s.direction; }
        s.index = next;
        change.current(next);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, max, interval]);
  return <div className="player" role="group" aria-label={label}>
    <button type="button" className="icon-button" onClick={() => onChange(Math.max(0, index - 1))} aria-label="Previous step"><StepBack aria-hidden /></button>
    <button type="button" className="play-button" aria-pressed={playing} onClick={() => setPlaying(value => !value)}>
      {playing ? <Pause aria-hidden /> : <Play aria-hidden />}<span>{playing ? 'Pause' : 'Play sweep'}</span>
    </button>
    <button type="button" className="icon-button" onClick={() => onChange(Math.min(max, index + 1))} aria-label="Next step"><StepForward aria-hidden /></button>
  </div>;
}

export function Segmented<T extends string>({ value, options, onChange, label }: { value: T; options: [T, string][]; onChange: (value: T) => void; label: string }) {
  return <div className="segmented" role="group" aria-label={label}>
    {options.map(([key, text]) => <button key={key} type="button" aria-pressed={value === key} onClick={() => onChange(key)}>{text}</button>)}
  </div>;
}

export function Readout({ label, value, unit, tone }: { label: ReactNode; value: ReactNode; unit?: ReactNode; tone?: string }) {
  return <div className={`readout-item ${tone ? `tone-${tone}` : ''}`}><dt>{label}</dt><dd><span className="readout-value">{value}</span>{unit && <span className="readout-unit">{unit}</span>}</dd></div>;
}

export function RecordView({ value, href, note }: { value: unknown; href: string; note: string }) {
  return <div className="record-view">
    <p>{note} <a href={href}>Download all rows (JSON)</a>.</p>
    <pre tabIndex={0} role="region" aria-label="Numbers for the current selection"><code>{JSON.stringify(value, null, 2)}</code></pre>
  </div>;
}
