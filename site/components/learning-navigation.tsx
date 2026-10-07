import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { meta } from '@/lib/lesson-meta';

/** The six-step route; every step stays open, none is locked behind another. */
export default function LearningNavigation({ current, onLearn }: { current: LearningID | null; onLearn: (id: LearningID) => void }) {
  const position = lessons.findIndex(item => item.id === current);
  return <nav className="route-rail" aria-label="Learning steps">
    <ol style={{ ['--progress' as string]: `${Math.max(0, position) / (lessons.length - 1)}` }}>
      {lessons.map((item, i) => <li key={item.id} className={i < position ? 'is-before' : i === position ? 'is-current' : ''}>
        <button type="button" aria-current={current === item.id ? 'step' : undefined} onClick={() => onLearn(item.id)}>
          <span className="rail-dot" aria-hidden>{meta[item.id].number}</span><span className="rail-label">{item.title.split(' · ')[0]}</span>
        </button>
      </li>)}
    </ol>
  </nav>;
}
