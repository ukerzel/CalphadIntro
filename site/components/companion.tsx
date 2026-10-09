'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { FollowContext } from '@/components/xref';
import { LaneContext } from '@/lib/lane';
import type { Lane } from '@/lib/lane';
import { REPO_WEB, dataVersion } from '@/lib/data';
import NotebookLinks from '@/components/notebook-links';
import LearningPage from '@/components/learning-page';
import RouteMap from '@/components/route-map';
import RouteMapDrawer from '@/components/route-map-drawer';
import { loadProgress, markVisited, setRemember } from '@/lib/progress';
import type { Progress } from '@/lib/progress';
import AskConcept, { StepContext } from '@/components/ask-concept';
import { LabNames } from '@/components/lab-frame';
import LearningNavigation from '@/components/learning-navigation';
import SiteHeader, { Logo } from '@/components/site-header';
import Home from '@/components/home';
import MaterialExplorer from '@/components/material-explorer';
import TwoPhaseView from '@/components/twophase-view';
import EnergyLadder from '@/components/energy-ladder';
import UnaryView from '@/components/unary-view';
import BinaryView from '@/components/binary-view';
import BoundaryView from '@/components/boundary-view';
import Day3LineView from '@/components/day3-line-view';
import type { LineView } from '@/components/day3-line-view';
import Day3CgView from '@/components/day3-cg-view';
import type { CgView } from '@/components/day3-cg-view';
import Day3RegularView from '@/components/day3-regular-view';
import type { RegularView } from '@/components/day3-regular-view';
import Day3PreworkView from '@/components/day3-prework-view';
import type { PreworkView } from '@/components/day3-prework-view';
import Day3TernaryView from '@/components/day3-ternary-view';
import type { TernaryView } from '@/components/day3-ternary-view';
import LpPrimerView, { lpViews } from '@/components/lp-primer-view';
import type { LpView } from '@/components/lp-primer-view';
import { lesson, lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { labViews, meta, pageLabel, pagerDetour, pagerPrevious } from '@/lib/lesson-meta';
import { loadBundle } from '@/lib/data';
import type { Bundle, View } from '@/lib/data';
import { parseRoute, recordIndex, routeHash } from '@/lib/route';
import type { Route } from '@/lib/route';
import { registerSelection } from '@/lib/webmcp';
import type { ModelContext, Selection } from '@/lib/webmcp';

const views: View[] = ['unary', 'binary', 'boundary'];
const lineViews: LineView[] = ['menu', 'line', 'gap', 'move-z', 'temperature'];
const day3LineDefault: Partial<Record<LearningID, LineView>> = { 'menu': 'menu', 'price-line': 'line', 'gap-curve': 'gap' };
const cgViews: CgView[] = ['player', 'bounds', 'spacing'];
const day3CgDefault: Partial<Record<LearningID, CgView>> = { 'column-generation': 'player', 'bounds': 'bounds' };
const regularViews: RegularView[] = ['local', 'pricing', 'bnb', 'joint'];
const day3RegularDefault: Partial<Record<LearningID, RegularView>> = { 'local-global': 'local', 'branch-and-bound': 'bnb', 'two-questions': 'joint' };
const preworkViews: PreworkView[] = ['second-law', 'counter', 'builder', 'omega'];
const day3PreworkDefault: Partial<Record<LearningID, PreworkView>> = { 'from-materials': 'omega', 'from-or': 'second-law', 'or-prices': 'omega' };
const isView = (id: string): id is View => (views as string[]).includes(id);
const recordId = (view: View, index: number) => `${view}-${String(index).padStart(3, '0')}`;

export default function Companion() {
  const [route, setRoute] = useState<Route>({ page: 'home' });
  const [bundle, setBundle] = useState<Bundle | null>(null), [error, setError] = useState('');
  const [indices, setIndices] = useState<Record<View, number>>({ unary: 50, binary: 19, boundary: 0 });
  const [resume, setResume] = useState<LearningID | null>(null), [progress, setProgress] = useState<Progress>({ on: false, visited: [], last: null });
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [lane, setLaneState] = useState<Lane>(null);
  const heading = useRef<HTMLHeadingElement>(null), dock = useRef<HTMLDivElement>(null);
  const navigated = useRef(false), previous = useRef<Route>({ page: 'home' }), urlTimer = useRef(0), restoreY = useRef<number | null>(null);
  const [back, setBack] = useState<{ hash: string; y: number; label: string } | null>(null);

  useEffect(() => {
    const apply = () => { window.clearTimeout(urlTimer.current); navigated.current = true; setRoute(parseRoute(location.hash)); };
    setRoute(parseRoute(location.hash));
    const saved = loadProgress(); setProgress(saved); if (saved.last) setResume(saved.last);   // only if the learner chose "remember"
    try { const saved = localStorage.getItem('calphad-lane'); if (saved === 'M' || saved === 'O') setLaneState(saved); } catch { /* no saved lane */ }
    window.addEventListener('hashchange', apply);
    setTheme(document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light');
    return () => window.removeEventListener('hashchange', apply);
  }, []);
  useEffect(() => { let active = true; loadBundle().then(data => { if (active) setBundle(data); }).catch(e => { if (active) setError(String(e.message)); }); return () => { active = false; }; }, []);

  // The visited steps and the last step are stored only after the learner switches "remember" on (route map).
  useEffect(() => {
    if (route.page !== 'lesson') return;
    setResume(route.id);
    setProgress(markVisited(route.id));
  }, [route]);

  // Exact record IDs in the URL select the same row as the slider would.
  useEffect(() => {
    if (!bundle || route.page !== 'lesson' || !route.lab || !isView(route.id)) return;
    const index = recordIndex(route.recordId, route.id, bundle[route.id].records.length);
    if (index !== null) setIndices(previous => ({ ...previous, [route.id]: index }));
  }, [route, bundle]);

  useEffect(() => {
    const lab = route.page === 'lesson' && route.lab, before = previous.current;
    previous.current = route;
    // Closing a lab keeps the learner at the dock instead of jumping to the top.
    const closed = route.page === 'lesson' && !route.lab && before.page === 'lesson' && before.id === route.id && before.lab;
    const anchor = route.page === 'lesson' ? route.anchor : undefined, view = route.page === 'lesson' && route.lab ? route.view : undefined;
    if (!navigated.current && !lab && !anchor) return;
    let frame = 0, timer = 0;
    const deadline = performance.now() + 4000;
    const restore = restoreY.current;
    restoreY.current = null;
    // A named lab panel may appear only after its data loads: look for it for about two seconds.
    const findPanel = () => {
      const node = document.getElementById(`lab-${view}`);
      if (node) { node.scrollIntoView({ block: 'start' }); node.classList.add('is-target'); window.setTimeout(() => node.classList.remove('is-target'), 2400); }
      else if (performance.now() < deadline) frame = requestAnimationFrame(findPanel);
    };
    frame = requestAnimationFrame(() => {
      // Restore twice: once now, once after inline figures above have had time to load.
      if (restore !== null) { window.scrollTo(0, restore); timer = window.setTimeout(() => window.scrollTo(0, restore), 600); return; }
      if (anchor && route.page === 'lesson') {
        const node = document.getElementById(`${route.id}-${anchor}`);
        if (node) {
          node.scrollIntoView({ block: 'start' }); node.classList.add('is-target'); window.setTimeout(() => node.classList.remove('is-target'), 2400);
          const focus = node.querySelector<HTMLElement>('h2') ?? node; if (!focus.hasAttribute('tabindex')) focus.tabIndex = -1; focus.focus({ preventScroll: true });
          return;
        }
      }
      if ((lab || closed) && dock.current) { dock.current.scrollIntoView({ block: 'start' }); (closed ? dock.current.querySelector<HTMLElement>('button') ?? dock.current : dock.current).focus({ preventScroll: true }); if (view) findPanel(); }
      else { window.scrollTo(0, 0); heading.current?.focus({ preventScroll: true }); }
    });
    return () => { cancelAnimationFrame(frame); window.clearTimeout(timer); };
  }, [route]);

  const go = (next: Route) => { window.clearTimeout(urlTimer.current); navigated.current = true; const hash = routeHash(next); if (location.hash === hash) setRoute(next); else location.hash = hash; };
  const learn = (id: LearningID) => go({ page: 'lesson', id, lab: false });
  const learnAt = (id: LearningID, anchor: string) => go({ page: 'lesson', id, lab: false, anchor });
  // Cross-references remember the place they were followed from, for the "Back to …" chip.
  const follow = (next: Route, from: string) => { setBack({ hash: location.hash || '#/', y: window.scrollY, label: from }); go(next); };
  const goBack = () => {
    if (!back) return;
    restoreY.current = back.y; setBack(null);
    const target = parseRoute(back.hash);
    if (location.hash === back.hash) { navigated.current = true; setRoute({ ...target }); } else { navigated.current = true; location.hash = back.hash; }
  };
  const openLab = (id: LearningID, view?: string) => go({ page: 'lesson', id, lab: true, ...(view ? { view } : isView(id) ? { recordId: recordId(id, indices[id]) } : {}) });
  const update = (view: View) => (index: number) => {
    setIndices(previous => ({ ...previous, [view]: index }));
    // Debounced: sweeps and drags change rows faster than browsers allow history updates.
    window.clearTimeout(urlTimer.current);
    urlTimer.current = window.setTimeout(() => {
      try { history.replaceState(null, '', routeHash({ page: 'lesson', id: view, lab: true, recordId: recordId(view, index) })); } catch { /* URL stays at the previous row */ }
    }, 400);
  };
  const select = useCallback((s: Selection) => {
    flushSync(() => { navigated.current = true; setIndices(previous => ({ ...previous, [s.view]: s.index })); setRoute({ page: 'lesson', id: s.view, lab: true, recordId: s.recordId }); });
    try { history.pushState(null, '', routeHash({ page: 'lesson', id: s.view, lab: true, recordId: s.recordId })); } catch { /* state already applied */ }
  }, []);
  useEffect(() => {
    if (!bundle) return;
    const context = (document as Document & { modelContext?: ModelContext }).modelContext;
    return registerSelection(context, bundle, select);
  }, [bundle, select]);
  // The lane only changes which boxes open by default; it is remembered per browser (convenience only).
  const setLane = (value: Lane) => { setLaneState(value); try { if (value) localStorage.setItem('calphad-lane', value); else localStorage.removeItem('calphad-lane'); } catch { /* storage unavailable */ } };
  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next); document.documentElement.dataset.theme = next;
    try { localStorage.setItem('calphad-theme', next); } catch { /* storage unavailable: theme lasts for this visit */ }
  };

  const current = route.page === 'lesson' ? route.id : null;
  useEffect(() => {   // a title per page: browser tabs and history say where each one is
    const page = route.page === 'lesson' ? lessons.find(item => item.id === route.id) : null;
    document.title = page ? `${pageLabel(page.id)} · ${page.title.split(' · ')[0]} — CALPHAD School 2026` : 'CALPHAD School 2026 · guided self-study';
  }, [route]);
  /** The step's lab under the step's own names; the extra labs some steps open by view keep their own. */
  const labContent = (id: LearningID, view?: string) => {
    const extra = (id === 'start' && view === 'second-law') || (id === 'binary' && view === 'counter') || (id === 'twophase' && view === 'stability');
    const names = extra ? null : { title: meta[id].labTitle, views: Object.fromEntries((labViews[id] ?? []).map(([key, label]) => [key, label])) };
    return <LabNames.Provider value={names}>{labBody(id, view)}</LabNames.Provider>;
  };
  const labBody = (id: LearningID, view?: string) => {
    if (id === 'cuni' || id === 'ninb') return <MaterialExplorer id={id} />;
    const kicker = `${pageLabel(id)} · interactive lab`;
    if (id === 'start' && view === 'second-law') return <Day3PreworkView key="second-law" initialView="second-law" views={['second-law']} kicker={kicker} />;
    if (id === 'binary' && view === 'counter') return <Day3PreworkView key="counter" initialView="counter" views={['counter']} kicker={kicker} />;
    if (id === 'twophase' && view === 'stability') return <Day3PreworkView key="stability" initialView="omega" views={['omega']} kicker={kicker} />;
    if (id === 'twophase') return <TwoPhaseView key={view ?? 'default'} initialPart={view === 'part-b' ? 'b' : view === 'part-c' ? 'c' : view === 'part-d' ? 'd' : 'a'} />;
    if (id === 'start') return <EnergyLadder />;
    const lineDefault = day3LineDefault[id];
    if (lineDefault) return <Day3LineView key={view ?? 'default'} kicker={kicker} views={labViews[id]?.map(([v]) => v as LineView)} initialView={view && (lineViews as string[]).includes(view) ? view as LineView : lineDefault} />;
    const cgDefault = day3CgDefault[id];
    if (cgDefault) return <Day3CgView key={view ?? 'default'} kicker={kicker} views={labViews[id]?.map(([v]) => v as CgView)} initialView={view && (cgViews as string[]).includes(view) ? view as CgView : cgDefault} />;
    const regularDefault = day3RegularDefault[id];
    if (id === 'lp-primer') return <LpPrimerView key={view ?? 'default'} kicker={kicker} initialView={view && (lpViews as string[]).includes(view) ? view as LpView : 'chords'} />;
    if ((id as string) === 'three-components') return <Day3TernaryView key={view ?? 'default'} kicker={kicker} initialView={view === 'landscape' || view === 'harder' ? view as TernaryView : 'triangle'} />;
    const preworkDefault = day3PreworkDefault[id];
    if (preworkDefault) return <Day3PreworkView key={view ?? 'default'} kicker={kicker} views={labViews[id]?.map(([v]) => v as PreworkView)} initialView={view && (preworkViews as string[]).includes(view) ? view as PreworkView : preworkDefault} />;
    if (regularDefault) return <Day3RegularView key={view ?? 'default'} kicker={kicker} views={labViews[id]?.map(([v]) => v as RegularView)} initialView={view && (regularViews as string[]).includes(view) ? view as RegularView : regularDefault} />;
    if (!isView(id)) return null;
    if (error) return <div className="notice" role="alert"><h2>Data unavailable</h2><p>{error}. Rebuild from the checked repository exports.</p></div>;
    if (!bundle) return <p className="loading" role="status">Loading checked teaching data…</p>;
    const props = { bundle, index: indices[id], onChange: update(id) };
    return id === 'unary' ? <UnaryView {...props} /> : id === 'binary' ? <BinaryView {...props} />
      : <BoundaryView key={view ?? 'default'} {...props} initialView={view === 'tangent' || view === 'iteration' || view === 'match' ? view : 'cells'} />;
  };

  const mapProps = { current, progress, onLearn: learn, onAnchor: learnAt, onLab: (id: LearningID) => openLab(id), onRemember: (on: boolean) => setProgress(setRemember(on, current)) };
  const stepNow = current ? { step: pageLabel(current), title: lessons.find(item => item.id === current)?.title ?? '' } : null;
  return <FollowContext.Provider value={follow}><LaneContext.Provider value={{ lane, setLane }}><StepContext.Provider value={stepNow}>
    <svg width="0" height="0" aria-hidden className="defs"><defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="var(--paper-2)" /><line x1="0" y1="0" x2="0" y2="8" stroke="var(--rule-strong)" strokeWidth="2" /></pattern></defs></svg>
    <a className="skip-link" href="#content" onClick={event => { event.preventDefault(); document.getElementById('content')?.focus(); }}>Skip to content</a>
    <SiteHeader current={current} onHome={() => go({ page: 'home' })} onLearn={learn} onLab={openLab} theme={theme} onTheme={toggleTheme}
      map={<RouteMapDrawer {...mapProps} />} />
    {current && <LearningNavigation current={current} onLearn={learn} visited={progress.visited} />}
    <main id="content" tabIndex={-1}>
      {route.page === 'home'
        ? <Home key="home" bundle={bundle} onLearn={learn} onLab={openLab} headingRef={heading} resume={resume} routeMap={<RouteMap {...mapProps} />} />
        : <LessonScreen key={route.id} id={route.id} lab={route.lab} heading={heading} dock={dock}
          onOpen={view => openLab(route.id, view)} onClose={() => go({ page: 'lesson', id: route.id, lab: false })} onLearn={learn} content={labContent(route.id, route.lab ? route.view : undefined)} />}
      {back && <div className="back-chip" role="region" aria-label="Return to where you were">
        <button type="button" className="back-chip-go" onClick={goBack}><ArrowLeft aria-hidden />Back to {back.label}</button>
        <button type="button" className="back-chip-close" onClick={() => setBack(null)} aria-label="Dismiss"><X aria-hidden /></button>
      </div>}
    </main>
    <footer className="site-footer">
      <div className="footer-brand"><Logo /><p><strong>CALPHAD School 2026</strong> · guided self-study. Built from the course repository on GitHub.</p></div>
      <ul className="footer-facts">
        <li><a href={REPO_WEB}>Course repository</a></li>
        {bundle && <li>Data version <code>{dataVersion(bundle.receipt)}</code></li>}
        <li><a href="/fonts/README.md">Fonts: Inter and School Serif (from STIX Two), SIL OFL 1.1</a> · formulas typeset with KaTeX (MIT)</li>
      </ul>
    </footer>
  </StepContext.Provider></LaneContext.Provider></FollowContext.Provider>;
}

export function LessonScreen({ id, lab, heading, dock, onOpen, onClose, onLearn, content }: {
  id: LearningID; lab: boolean; heading: React.RefObject<HTMLHeadingElement | null>; dock: React.RefObject<HTMLDivElement | null>;
  onOpen: (view?: string) => void; onClose: () => void; onLearn: (id: LearningID) => void; content: React.ReactNode;
}) {
  const item = lesson(id), m = meta[id], position = lessons.findIndex(l => l.id === id);
  const previous = (pagerPrevious[id] ?? (position > 0 ? [lessons[position - 1].id] : [])).map(lesson), next = item.next ? lesson(item.next) : null;
  const detour = pagerDetour[id];
  const material = id === 'cuni' || id === 'ninb';
  const labDock = m.lab ? <div ref={dock} tabIndex={-1} role="region" className={`dock ${lab ? 'is-open' : ''}`} aria-label="Interactive lab">
    {lab ? <>
      <div className="dock-bar"><span className="dock-flag">{material ? 'Results explorer' : 'Interactive lab'}</span><NotebookLinks id={id} compact />
        {m.labTitle && <AskConcept kind="lab" label="Ask ChatGPT about this lab" concept={`the interactive lab “${m.labTitle}”`} text={[m.labLine, ...(labViews[id] ?? []).map(([, label, line]) => `${label}: ${line}`)].filter(Boolean).join('\n')} />}<button type="button" className="ghost-button" onClick={onClose}><X aria-hidden />Return to the activity</button></div>
      {content}
    </> : <div className="dock-closed">
      <div><p className="lab-kicker">After your attempt</p>
        <h3>{m.labTitle}</h3><p>{m.labLine}</p>
        {(labViews[id]?.length ?? 0) > 1 && <><p className="dock-views-title">In the lab:</p><ul className="dock-views">{labViews[id]!.map(([view, label, line]) => <li key={view}>
          <button type="button" className="dock-view" onClick={() => onOpen(view)}><strong>{label}</strong><span>{line}</span></button></li>)}</ul></>}
        <NotebookLinks id={id} /></div>
      <button type="button" className="button-primary" onClick={() => onOpen()}>{material ? 'Explore the results' : 'Explore the calculation'}<ArrowRight aria-hidden /></button>
    </div>}
  </div> : undefined;
  return <div className="page-enter">
    <LearningPage lesson={item} headingRef={heading} dock={labDock} />
    <nav className="pager" aria-label="Activity controls">
      {previous.length ? <div className="pager-stack">{previous.map(item => <button key={item.id} type="button" onClick={() => onLearn(item.id)}><span className="pager-dir"><ArrowLeft aria-hidden />Previous · {pageLabel(item.id)}</span><span className="pager-title">{item.title}</span></button>)}</div> : <span />}
      {next ? <div className="pager-stack">
        {detour && <button type="button" className="is-detour" onClick={() => onLearn(detour[0])}><span className="pager-dir">{detour[1]} · {pageLabel(detour[0])}<ArrowRight aria-hidden /></span><span className="pager-title">{lesson(detour[0]).title}</span></button>}
        <button type="button" className="is-next" onClick={() => onLearn(next.id)}><span className="pager-dir">Next · {pageLabel(next.id)}<ArrowRight aria-hidden /></span><span className="pager-title">{next.title}</span></button></div>
        : <p className="pager-end">You have reached the end of the route. Step 18 was optional. Steps 05 and 06 apply the same thermodynamics to published databases, and the optional notebook task01b reads the gap curve of the Cu–Ni one; every step and lab stays open to revisit.</p>}
    </nav>
  </div>;
}
