'use client';
/** The route map: the main line 00–17 end to end, the branches that leave it and come back (the OR entry 08–09,
 *  the LP primer, step 03 part D, step 18), and each step's lab and notebooks as small marks. Hover, focus or tap
 *  a mark to read about it; click (or tap again) to go there. Horizontal on wide screens, vertical on phones. */
import { useRef, useState } from 'react';
import { ArrowRight, FlaskConical } from 'lucide-react';
import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { advancedMinutes, colabURL, isAdvanced, meta, notebooks, pageLabel, stepStory } from '@/lib/lesson-meta';
import { kindLabel, mainLine, stations, tracks } from '@/lib/route-map';
import type { Station } from '@/lib/route-map';
import type { Progress } from '@/lib/progress';

type Extra = { type: 'lab'; station: Station } | { type: 'notebooks'; station: Station; list: [string, string][] };
type Mark = { type: 'station'; station: Station } | Extra;
type Layout = { width: number; height: number; at: (t: number, o: number) => [number, number] };

const H: Layout = { width: 16.2 * 62 + 100, height: 230, at: (t, o) => [32 + t * 62, 100 + o * 46] };
const V: Layout = { width: 330, height: 16.2 * 42 + 70, at: (t, o) => [150 + o * 78, 36 + t * 42] };

const lesson = (id: LearningID) => lessons.find(item => item.id === id)!;
const titleOf = (s: Station) => s.anchor ? 'Step 03 · Part D: how a program finds the split' : `${pageLabel(s.id)} · ${lesson(s.id).title}`;
const numberOf = (s: Station) => s.short || meta[s.id].number;
const marksOf = (s: Station): Extra[] => s.anchor ? [] : [
  ...(meta[s.id].lab ? [{ type: 'lab' as const, station: s }] : []),
  ...(notebooks[s.id]?.length ? [{ type: 'notebooks' as const, station: s, list: notebooks[s.id]! }] : []),
];
const markKey = (m: Mark) => m.type === 'station' ? m.station.key : `${m.station.key}:${m.type}`;
const stationHash = (s: Station) => `#/${s.id}${s.anchor ? `/at/${s.anchor}` : ''}`;

function Diagram({ layout, className, current, progress, focus, onFocus, onGo }: {
  layout: Layout; className: string; current: LearningID | null; progress: Progress; focus: string; onFocus: (m: Mark) => void; onGo: (m: Mark) => void;
}) {
  const pointer = useRef('mouse');
  const path = (points: [number, number][]) => points.map(([t, o], i) => { const [x, y] = layout.at(t, o); return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`; }).join(' ');
  // Mouse: click goes there. Touch or pen: the first tap selects (the card shows what it is), a second tap goes there.
  const handle = (m: Mark) => (event: React.MouseEvent) => {
    event.preventDefault();
    if (pointer.current !== 'mouse' && focus !== markKey(m)) onFocus(m); else onGo(m);
  };
  const vertical = layout === V;
  return <svg className={`route-map-svg ${className}`} viewBox={`0 0 ${layout.width} ${layout.height}`} role="group" aria-label="Route map: the main line, its branches, labs and notebooks"
    onPointerDown={event => { pointer.current = event.pointerType; }}>
    {tracks.map((track, i) => <path key={i} className={`rm-track rm-track-${track.kind}`} d={path(track.points)} />)}
    {stations.map(s => {
      const [x, y] = layout.at(s.t, s.o), here = current === s.id && !s.anchor, seen = !s.anchor && progress.visited.includes(s.id);
      const marks = marksOf(s), side = s.o < 0 ? -1 : 1;
      return <g key={s.key} className={`rm-station is-${s.kind}${isAdvanced(s.id) ? ' is-advanced' : ''}${here ? ' is-current' : ''}${seen ? ' is-visited' : ''}${focus === s.key ? ' is-focus' : ''}`}>
        <a href={stationHash(s)} aria-label={`${titleOf(s)}. ${kindLabel[s.kind]}${here ? ', you are here' : seen ? ', visited' : ''}`} aria-current={here ? 'step' : undefined}
          onClick={handle({ type: 'station', station: s })} onMouseEnter={() => onFocus({ type: 'station', station: s })} onFocus={() => onFocus({ type: 'station', station: s })}>
          {here && <circle className="rm-halo" cx={x} cy={y} r={21} />}
          <circle className="rm-dot" cx={x} cy={y} r={15} />
          <text className="rm-number" x={x} y={y + 4} textAnchor="middle">{numberOf(s)}</text>
        </a>
        {marks.map((m, k) => {
          // beside the station, on the side away from the branches: below-right (above-right for a branch above the line)
          const along = 12 + k * 15, across = side * 27;
          const [mx, my] = vertical ? [x + across, y + along] : [x + along, y + across];
          const key = markKey(m), n = m.type === 'notebooks' ? m.list.length : 0;
          const label = m.type === 'lab' ? `Lab of ${pageLabel(s.id, true)}: ${meta[s.id].labTitle}` : `${n} notebook${n > 1 ? 's' : ''} for ${pageLabel(s.id, true)}`;
          return <a key={key} href={m.type === 'lab' ? `#/${s.id}/lab` : stationHash(s)} className={`rm-extra rm-${m.type}${focus === key ? ' is-focus' : ''}`} aria-label={label}
            onClick={handle(m)} onMouseEnter={() => onFocus(m)} onFocus={() => onFocus(m)}>
            {m.type === 'lab' ? <rect x={mx - 5} y={my - 5} width={10} height={10} rx={2} /> : <><circle cx={mx} cy={my} r={6.5} />{n > 1 && <text className="rm-count" x={mx} y={my + 3} textAnchor="middle">{n}</text>}</>}
          </a>;
        })}
      </g>;
    })}
  </svg>;
}

export default function RouteMap({ current, progress, onLearn, onAnchor, onLab, onRemember, onNavigate }: {
  current: LearningID | null; progress: Progress; onLearn: (id: LearningID) => void; onAnchor: (id: LearningID, anchor: string) => void;
  onLab: (id: LearningID) => void; onRemember: (on: boolean) => void; onNavigate?: () => void;
}) {
  const start = stations.find(s => s.id === current && !s.anchor) ?? stations[0];
  const [mark, setMark] = useState<Mark>({ type: 'station', station: start });
  const s = mark.station, here = current === s.id && !s.anchor, seen = progress.visited.includes(s.id);
  const go = (m: Mark) => {
    if (m.type === 'notebooks') { setMark(m); return; }   // the card lists them, each with its own Colab link
    onNavigate?.();
    if (m.type === 'lab') onLab(m.station.id); else if (m.station.anchor) onAnchor(m.station.id, m.station.anchor); else onLearn(m.station.id);
  };
  const done = mainLine.filter(id => progress.visited.includes(id)).length;
  const props = { current, progress, focus: markKey(mark), onFocus: setMark, onGo: go };
  return <div className="route-map">
    <div className="route-map-figure">
      <Diagram layout={H} className="route-map-h" {...props} />
      <Diagram layout={V} className="route-map-v" {...props} />
      <ul className="route-map-legend" aria-label="Legend">
        <li><span className="lg-main" aria-hidden />main line, steps 00–17</li><li><span className="lg-branch" aria-hidden />branch or optional part</li>
        <li><span className="lg-lab" aria-hidden />lab</li><li><span className="lg-nb" aria-hidden />notebook</li>
        <li><span className="lg-here" aria-hidden />you are here</li>{progress.on && <li><span className="lg-seen" aria-hidden />visited</li>}
      </ul>
    </div>
    <aside className="route-map-card" aria-live="polite">
      <p className="lab-kicker">{kindLabel[s.kind]}{isAdvanced(s.id) ? ' · advanced' : ''}{here ? ' · you are here' : progress.on && seen ? ' · visited' : ''}</p>
      {mark.type === 'station' ? <>
        <h3>{titleOf(s)}</h3>
        <p>{s.note || stepStory[s.id] || 'The refresher and glossary: energies, terms and why CALPHAD.'}</p>
        {!s.anchor && advancedMinutes[s.id] && <p className="caption">About {advancedMinutes[s.id]!.replace(/^about /, '')} minutes without the optional boxes (an estimate).</p>}
        {!s.anchor && marksOf(s).length > 0 && <p className="caption">{meta[s.id].lab ? 'One lab' : 'No lab'}{(notebooks[s.id]?.length ?? 0) ? `, ${notebooks[s.id]!.length} notebook${notebooks[s.id]!.length > 1 ? 's' : ''}` : ''}: hover or tap the small marks beside the station.</p>}
        <button type="button" className="button-primary" onClick={() => go(mark)}>{here ? 'Back to this step' : s.anchor ? 'Open part D' : `Open ${pageLabel(s.id, true)}`}<ArrowRight aria-hidden /></button>
      </> : mark.type === 'lab' ? <>
        <h3><FlaskConical aria-hidden className="inline-icon" /> {meta[s.id].labTitle}</h3>
        <p>{meta[s.id].labLine}</p><p className="caption">The lab of {pageLabel(s.id, true)}. Try the step&apos;s problem first.</p>
        <button type="button" className="button-primary" onClick={() => go(mark)}>Open the lab<ArrowRight aria-hidden /></button>
      </> : <>
        <h3>Notebooks for {pageLabel(s.id, true)}</h3>
        <ul className="route-map-notebooks">{mark.list.map(([file, label]) => <li key={file}><a href={colabURL(file)} target="_blank" rel="noreferrer">{label}</a><span className="caption"> · {file}, opens Colab in a new tab</span></li>)}</ul>
      </>}
      <div className="route-map-remember">
        <label className="check"><input type="checkbox" checked={progress.on} onChange={e => onRemember(e.target.checked)} /> Remember the steps I visit in this browser</label>
        <p className="caption">{progress.on ? `${done} of ${mainLine.length} main-line steps visited. Stored only in this browser, never sent anywhere.` : 'Off: nothing about your visit is stored. If you switch it on, the visited steps stay only in this browser, and you can forget them any time.'}</p>
        {progress.on && <button type="button" className="ghost-button" onClick={() => onRemember(false)}>Forget my progress</button>}
      </div>
    </aside>
  </div>;
}
