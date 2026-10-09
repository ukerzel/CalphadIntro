'use client';
import { createContext, useContext, useEffect, useRef, useState } from 'react';

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

/** The step's own names for its lab (lesson-meta's lab title and view labels), so a lab has one name wherever it
 *  appears: dock card, lab heading and view buttons. Labs used outside a step keep their own names. */
export const LabNames = createContext<{ title: string | null; views: Record<string, string> } | null>(null);
const InLabActions = createContext(false);

export default function LabFrame({ kicker, title, conditions, actions, explore, model, record }: {
  kicker: string; title: string; conditions: string[]; actions?: ReactNode; explore: ReactNode; model: ReactNode; record: ReactNode;
}) {
  const heading = useContext(LabNames)?.title ?? title;
  return <section className="lab" aria-label={`${heading} · interactive lab`}>
    <header className="lab-head">
      <div><p className="lab-kicker">{kicker}</p><h2 className="lab-title">{heading}</h2></div>
      {actions && <div className="lab-actions"><InLabActions.Provider value={true}>{actions}</InLabActions.Provider></div>}
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

/** The one stepper of every lab: back and forward around "Round 2 of 3", or around a Play button when a sweep can run by itself. */
export function Stepper({ index, count, onChange, unit, label, status, play, interval = 40, nextDisabled = false }: {
  index: number; count: number; onChange: (index: number) => void; unit: string; label: string; status?: ReactNode; play?: boolean; interval?: number; nextDisabled?: boolean;
}) {
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
        if (next > count - 1 || next < 0) { s.direction *= -1; next = s.index + s.direction; }
        s.index = next;
        change.current(next);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, count, interval]);
  return <div className="stepper" role="group" aria-label={label}>
    <button type="button" className="icon-button" disabled={index <= 0} onClick={() => onChange(Math.max(0, index - 1))} aria-label={`Previous ${unit}`}><StepBack aria-hidden /></button>
    {play ? <button type="button" className="play-button" aria-pressed={playing} onClick={() => setPlaying(value => !value)}>
      {playing ? <Pause aria-hidden /> : <Play aria-hidden />}<span>{playing ? 'Pause' : 'Play sweep'}</span>
    </button> : <span className="stepper-status" aria-live="polite">{status ?? `${unit[0].toUpperCase()}${unit.slice(1)} ${index + 1} of ${count}`}</span>}
    <button type="button" className="icon-button" disabled={index >= count - 1 || nextDisabled} onClick={() => onChange(Math.min(count - 1, index + 1))} aria-label={`Next ${unit}`}><StepForward aria-hidden /></button>
  </div>;
}

/** Steps through the exported rows one by one, or plays them as a sweep. */
export function Player({ index, max, onChange, label, interval = 40 }: { index: number; max: number; onChange: (index: number) => void; label: string; interval?: number }) {
  return <Stepper index={index} count={max + 1} onChange={onChange} unit="step" label={label} play interval={interval} />;
}

export function Segmented<T extends string>({ value, options, onChange, label }: { value: T; options: [T, string][]; onChange: (value: T) => void; label: string }) {
  const inActions = useContext(InLabActions), labNames = useContext(LabNames);
  const names = inActions ? labNames?.views : undefined;   // a lab's view switch uses the step's view labels
  return <div className="segmented" role="group" aria-label={label}>
    {options.map(([key, text]) => <button key={key} type="button" aria-pressed={value === key} onClick={() => onChange(key)}>{names?.[key] ?? text}</button>)}
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
