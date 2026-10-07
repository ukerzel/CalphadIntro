'use client';
import { useEffect, useState } from 'react';

/** In-page stage list with scroll tracking; buttons, because the URL hash carries the route. */
export default function StageIndex({ lessonId, stages }: { lessonId: string; stages: { key: string; label: string; kind: string }[] }) {
  const [active, setActive] = useState(stages[0]?.key);
  const keys = stages.map(stage => stage.key).join('|');
  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') return;
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (visible) setActive(visible.target.id.slice(lessonId.length + 1));
    }, { rootMargin: '-20% 0px -65% 0px' });
    keys.split('|').forEach(key => { const node = document.getElementById(`${lessonId}-${key}`); if (node) observer.observe(node); });
    return () => observer.disconnect();
  }, [lessonId, keys]);
  const go = (key: string) => {
    const node = document.getElementById(`${lessonId}-${key}`);
    node?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    (node?.querySelector('h2') as HTMLElement | null)?.focus?.({ preventScroll: true });
  };
  return <nav className="stage-index" aria-label="On this page">
    <p className="stage-index-title">On this page</p>
    <ol>{stages.map(stage => <li key={stage.key} className={`kind-${stage.kind}`}>
      <button type="button" aria-current={active === stage.key ? 'location' : undefined} onClick={() => go(stage.key)}>{stage.label}</button>
    </li>)}</ol>
  </nav>;
}
