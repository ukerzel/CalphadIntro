import { useEffect, useRef } from 'react';
import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { isAdvanced, meta, pageLabel } from '@/lib/lesson-meta';
import { joins, mainLine } from '@/lib/route-map';

/** The slim route rail: only the main line, steps 00–17, so it shows what to do next. On a branch page (the OR entry,
 *  the LP primer, step 18) a chip says so and the rail marks where the branch leaves the line; the route map shows all. */
export default function LearningNavigation({ current, onLearn, visited = [] }: { current: LearningID | null; onLearn: (id: LearningID) => void; visited?: LearningID[] }) {
  const onLine = current !== null && mainLine.includes(current), at = current === null ? -1 : mainLine.indexOf(onLine ? current : joins[current] ?? current);
  const rail = useRef<HTMLElement>(null);
  useEffect(() => {   // on a narrow screen the rail scrolls sideways: bring the current step into view
    const nav = rail.current, item = nav?.querySelector<HTMLElement>('[aria-current="step"], .is-join button');
    if (nav && item && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = item.offsetLeft - (nav.clientWidth - item.offsetWidth) / 2;
  }, [current]);
  const title = (id: LearningID) => lessons.find(item => item.id === id)!.title;
  return <nav ref={rail} className="route-rail" aria-label="Main line, steps 00–17">
    <ol style={{ ['--progress' as string]: `${Math.max(0, at) / (mainLine.length - 1)}` }}>
      {mainLine.map((id, i) => <li key={id} className={`${i < at ? 'is-before' : i === at ? (onLine ? 'is-current' : 'is-join') : ''}${isAdvanced(id) ? ' is-advanced' : ''}${visited.includes(id) ? ' is-visited' : ''}`}>
        <button type="button" aria-current={current === id ? 'step' : undefined} onClick={() => onLearn(id)}>
          <span className="rail-dot" aria-hidden>{meta[id].number}</span><span className="rail-label">{title(id).split(' · ')[0]}{visited.includes(id) && <span className="sr-only"> (visited)</span>}</span>
        </button>
      </li>)}
      {current && !onLine && <li className="rail-branch"><span className="branch-chip">On a branch: {pageLabel(current)}</span></li>}
    </ol>
  </nav>;
}
