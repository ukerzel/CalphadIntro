'use client';
import type { ReactNode, RefObject } from 'react';
import { ArrowRight, ArrowUpRight } from 'lucide-react';
import HeroGraphic from '@/components/hero-graphic';
import VideoEmbed from '@/components/video-embed';
import { overviewVideo } from '@/lib/media';
import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { isAdvanced, isOptional, isPrimer, labViews, meta, pageLabel, question } from '@/lib/lesson-meta';
import { sourceURL } from '@/lib/data';
import type { Bundle } from '@/lib/data';

const method = [
  ['Problem', 'A concrete question with stated conditions, allowed phases and amount basis.'],
  ['Approach', 'Choose the potential, the constraints and the reference before any number.'],
  ['Attempt', 'Work it on paper. Supplied values make every step checkable by hand.'],
  ['Help', 'Two hints and a worked answer, closed until you decide to open them.'],
  ['Explore', 'Open the lab and check your numbers against the calculation.'],
  ['Interpret', 'Say what the result supports — and the real-material claim it cannot.'],
];

const trust = [
  ['Invented examples first', 'Steps 01–04 use made-up models small enough to check with a calculator, so you learn the method before the materials.'],
  ['Real alloys next', 'Steps 05 and 06 read Cu–Ni and Ni–Nb results calculated in advance from published databases.'],
  ['Then the solver itself', 'Advanced steps 07–18 ask how a program knows its equilibrium is the lowest, and read the calculation as an optimisation problem. Come from materials science or from operations research; an optional LP primer explains linear programmes from scratch.'],
  ['Nothing to install, nothing locked', 'Everything runs in the browser: no login, no grades. Optional notebooks rerun the calculations. Bring paper and a calculator.'],
];

/** Labs shown as cards on the home page; the advanced ones carry the Advanced tag. */
const labCards: LearningID[] = ['unary', 'binary', 'twophase', 'boundary', 'lp-primer', 'menu', 'price-line', 'column-generation', 'branch-and-bound', 'three-components'];

/** Printable packs: [title, one line, folder, [file, label][], answers file or null]. */
const paperPacks: [string, string, string, [string, string][], string | null][] = [
  ['Basics on paper', 'The Day 1 primer: thermodynamics, amounts and one invented element; follows steps 00–01.', 'primer', [['README.md', 'Overview'], ['worksheet.md', 'Worksheet'], ['instructor.md', 'Instructor notes']], 'answers.md'],
  ['Mixtures and boundaries on paper', 'The Day 2 primer: binary chemical potentials, two phases and open or closed boundaries; follows steps 02–04.', 'primer_day2', [['README.md', 'Overview'], ['worksheet.md', 'Worksheet'], ['two_phase_sheet.md', 'Two-phase sheet'], ['instructor.md', 'Instructor notes']], 'answers.md'],
  ['Advanced on paper', 'A picture sheet, a card deck, an LP primer sheet and a two-player game for menus, price lines, bounds and branch-and-bound; follows steps 07–18.', 'day3', [['README.md', 'Overview'], ['lp_primer_sheet.md', 'LP primer sheet'], ['picture_sheet.md', 'Picture sheet'], ['card_deck.md', 'Card deck'], ['game_kit.md', 'Game kit'], ['instructor.md', 'Instructor notes']], null],
];

export default function Home({ bundle, onLearn, onLab, headingRef, resume, routeMap }: { bundle: Bundle | null; onLearn: (id: LearningID) => void; onLab?: (id: LearningID, view?: string) => void; routeMap?: ReactNode; headingRef?: RefObject<HTMLHeadingElement | null>; resume?: LearningID | null }) {
  const resumeLesson = resume ? lessons.find(item => item.id === resume) : undefined;
  const firstAdvanced = lessons.find(item => isAdvanced(item.id));
  const labs = new Set(lessons.filter(item => meta[item.id].lab && meta[item.id].group !== 'Real alloys').map(item => meta[item.id].lab)).size;
  const seen = new Set<string>();
  const pictureGroups = lessons.map(item => ({ item, views: (labViews[item.id] ?? []).filter(([, label]) => !seen.has(label) && !!seen.add(label)) })).filter(group => group.views.length);
  const numbered = lessons.filter(item => !isPrimer(item.id)).length;
  const explorers = lessons.filter(item => meta[item.id].lab && meta[item.id].group === 'Real alloys').length;
  return <div className="home">
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">CALPHAD School 2026 · Guided self-study</p>
        <h1 ref={headingRef} tabIndex={-1}>Equilibrium is the lowest Gibbs energy. <em>Learn to find it.</em></h1>
        <p className="hero-lede">A route from basic thermodynamics to real Cu–Ni and Ni–Nb phase calculations, then on to how a program checks that its equilibrium is the lowest. Work each problem on paper, then check it in an interactive lab.</p>
        <div className="hero-actions">
          {resumeLesson
            ? <><button type="button" className="button-primary" onClick={() => onLearn(resumeLesson.id)}>Continue: {resumeLesson.title.split(' · ')[0]} <ArrowRight aria-hidden /></button>
              <button type="button" className="button-secondary" onClick={() => onLearn('start')}>Back to the start</button></>
            : <><button type="button" className="button-primary" onClick={() => onLearn('start')}>Start with the refresher <ArrowRight aria-hidden /></button>
              <button type="button" className="button-secondary" onClick={() => onLearn('unary')}>Go to the first problem</button></>}
        </div>
        <p className="hero-door"><button type="button" className="text-button" onClick={() => onLearn('from-or')}>Coming from operations research? Start at step 08 <ArrowRight aria-hidden /></button></p>
        <ul className="hero-facts"><li><strong>{numbered}</strong>steps, 00–{meta[lessons.at(-1)!.id].number}, and an optional LP primer</li><li><strong>{labs}</strong>interactive labs</li><li><strong>{explorers}</strong>real-alloy explorers</li><li><strong>0</strong>logins, grades or locks</li></ul>
      </div>
      <HeroGraphic bundle={bundle} />
    </section>

    <section className="home-video" aria-labelledby="video-title">
      <h2 id="video-title">The course in one short video</h2>
      <VideoEmbed youtube={overviewVideo.youtube} title={overviewVideo.title} />
      <p className="caption">Steps 01–06, 10 and 14 have their own short video at the top of the page.</p>
    </section>

    <section className="home-section" id="route" aria-labelledby="route-title">
      <div className="section-head"><p className="section-number">01</p><div><h2 id="route-title">The route</h2><p>Step 00 is a refresher and glossary you can keep open; every later step poses one problem. Steps 01–06 build the thermodynamics and end with two real alloys; the advanced steps 07–18 read the same calculation as an optimisation problem. Follow them in order or jump in anywhere; none is locked.</p></div></div>
      {routeMap && <div className="home-route-map">{routeMap}</div>}
      <ul className="route-cards">{lessons.filter(item => !isAdvanced(item.id)).map(lesson => <RouteCard key={lesson.id} lesson={lesson} onLearn={onLearn} />)}</ul>
      {firstAdvanced && <div className="route-junction" role="group" aria-labelledby="junction-title">
        <p className="advanced-tag">Advanced · steps 07–18</p>
        <h3 id="junction-title">How does a program know its equilibrium is really the lowest?</h3>
        <p>The advanced steps read the calculation as an optimisation problem: a menu of states, a price line, bounds and a search that cannot miss a valley. Two starting points lead into the same steps 10–18: step 07 for materials readers, steps 08 and 09 for readers from operations research. Never met a linear programme? The optional LP primer, after step 07 and before step 10, starts from scratch.</p>
        <div className="junction-doors">
          <button type="button" className="button-secondary" onClick={() => onLearn('from-materials')}><span>Know CALPHAD from materials science, or followed steps 00–06?</span><strong>Step 07, then step 10 <ArrowRight aria-hidden /></strong></button>
          <button type="button" className="button-secondary" onClick={() => onLearn('from-or')}><span>Know methods from operations research?</span><strong>Steps 08 and 09, then step 10 <ArrowRight aria-hidden /></strong></button>
        </div>
      </div>}
      <ul className="route-cards" aria-label="Advanced steps 07–18">{lessons.filter(item => isAdvanced(item.id)).map(lesson => <RouteCard key={lesson.id} lesson={lesson} onLearn={onLearn} />)}</ul>
    </section>

    <section className="home-section" aria-labelledby="method-title">
      <div className="section-head"><p className="section-number">02</p><div><h2 id="method-title">How every step works</h2><p>Every step from 01 to 18 follows this pattern. Try first, then reveal; the lab comes after your own reasoning, not instead of it.</p></div></div>
      <ol className="method">{method.map(([title, text], i) => <li key={title}><span className="method-index">{String(i + 1).padStart(2, '0')}</span><h3>{title}</h3><p>{text}</p></li>)}</ol>
    </section>

    <section className="home-section" aria-labelledby="labs-title">
      <div className="section-head"><p className="section-number">03</p><div><h2 id="labs-title">Interactive labs</h2><p>Drag, scrub or play through the calculated states. Each lab opens inside its step once you have tried the problem; the Labs menu in the header opens them directly.</p></div></div>
      <div className="lab-cards">
        {labCards.map(id => <button key={id} type="button" className={`lab-card lab-card-${id}${isAdvanced(id) ? ' is-advanced' : ''}${isOptional(id) ? ' is-optional' : ''}`} onClick={() => onLearn(id)}>
          <LabArt id={id} /><span className="lab-card-tag">{pageLabel(id)} · {meta[id].tag}{isAdvanced(id) && <>{' '}<span className="advanced-tag">Advanced</span></>}</span><span className="lab-card-title">{meta[id].labTitle}</span><span className="lab-card-line">{meta[id].labLine}</span>
        </button>)}
      </div>
      {onLab && <div className="picture-index">
        <h3 id="pictures-title">Every lab chart and diagram</h3>
        <p className="caption">Looking for a picture you saw earlier? Each entry opens its lab at that view.</p>
        <div className="picture-groups">{pictureGroups.map(({ item, views }) => <section key={item.id} aria-label={`${pageLabel(item.id)} lab views`}>
          <p className="picture-step">{pageLabel(item.id)} · {meta[item.id].tag}</p>
          <ul>{views.map(([view, label, line]) => <li key={view}><button type="button" className="dock-view" onClick={() => onLab(item.id, view)}><strong>{label}</strong><span>{line}</span></button></li>)}</ul>
        </section>)}</div>
      </div>}
    </section>

    <section className="home-section trust" aria-labelledby="trust-title">
      <div className="section-head"><p className="section-number">04</p><div><h2 id="trust-title">How the course works</h2><p>Short steps. Each one asks a question, lets you work it out, and then shows the calculation.</p></div></div>
      <ul className="trust-grid">{trust.map(([title, text]) => <li key={title}><h3>{title}</h3><p>{text}</p></li>)}</ul>
    </section>

    {bundle && <section className="home-section paper-routes" aria-labelledby="paper-title">
      <div className="section-head"><p className="section-number">05</p><div><h2 id="paper-title">Printable worksheets</h2><p>Prefer paper? Three packs of worksheets, sheets and instructor notes, for a classroom or for working alone. The <a href={sourceURL(bundle.receipt.source_commit, 'course/course_map.md')}>course map</a> shows the goals, the junctions and a short path through each part.</p></div></div>
      <div className="paper-grid">{paperPacks.map(([title, line, folder, files, answers]) => <article key={folder} className={folder === 'day3' ? 'is-advanced' : undefined}><h3>{title}</h3><p>{line}</p>
        <nav aria-label={`${title}: paper resources`}>{files.map(([name, label]) => <a key={name} href={sourceURL(bundle.receipt.source_commit, `course/${folder}/${name}`)}>{label}</a>)}
          {answers && <details><summary>Answers — after your attempt</summary><a href={sourceURL(bundle.receipt.source_commit, `course/${folder}/${answers}`)}>Open answer guide</a></details>}</nav></article>)}</div>
    </section>}
  </div>;
}

function RouteCard({ lesson, onLearn }: { lesson: (typeof lessons)[number]; onLearn: (id: LearningID) => void }) {
  const m = meta[lesson.id], advanced = isAdvanced(lesson.id);
  return <li className={`route-card group-${m.group.split(' ')[0].toLowerCase()}${isOptional(lesson.id) ? ' is-optional' : ''}`}>
    <button type="button" onClick={() => onLearn(lesson.id)}>
      <span className="route-meta"><span className="route-number">{m.number}</span>{advanced ? <span className="advanced-tag">Advanced</span> : <span>{m.group}</span>}{isOptional(lesson.id) && <span className="optional-tag">Optional</span>}</span>
      <span className="route-title">{lesson.title}</span>
      <span className="route-question">{question(lesson)}</span>
      <span className="route-lab">{m.labTitle ? <>Lab · {m.labTitle}</> : 'Reference · terms, potentials and a glossary'}<ArrowUpRight aria-hidden /></span>
    </button>
  </li>;
}

/** Hand-drawn decorative motifs (not data). */
function LabArt({ id }: { id: LearningID }) {
  if (id === 'unary') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M20,30 L220,92" /><path className="art-b" d="M20,16 L220,106" /><path className="art-min" d="M20,30 L120,61 L220,106" /><line className="art-cursor" x1="120" x2="120" y1="8" y2="114" /><circle className="art-dot" cx="120" cy="61" r="6" /></svg>;
  if (id === 'twophase') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M20,30 C50,110 90,105 120,70" /><path className="art-b" d="M120,70 C150,105 190,110 220,30" /><path className="art-tangent" d="M10,96 L230,96" /><circle className="art-dot" cx="62" cy="96" r="5" /><circle className="art-dot" cx="178" cy="96" r="5" /></svg>;
  if (id === 'binary') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-min" d="M20,40 C60,110 150,110 220,20" /><path className="art-tangent" d="M10,96 L230,58" /><circle className="art-dot" cx="96" cy="83" r="6" /><circle className="art-a-dot" cx="14" cy="95" r="4" /><circle className="art-b-dot" cx="226" cy="59" r="4" /></svg>;
  if (id === 'menu') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M20,30 C70,100 130,100 170,60" /><path className="art-b" d="M70,90 C120,40 180,30 225,20" />{[[38,58],[62,80],[86,90],[110,92],[134,86],[158,70]].map(([x, y]) => <circle key={`s${x}`} className="art-a-dot" cx={x} cy={y} r="4" />)}{[[96,68],[120,52],[144,43],[168,35],[192,29]].map(([x, y]) => <circle key={`l${x}`} className="art-b-dot" cx={x} cy={y} r="4" />)}<path className="art-min" d="M110,92 L144,43" /><circle className="art-dot" cx="126" cy="70" r="6" /></svg>;
  if (id === 'price-line') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden>{[[30,40],[60,72],[90,88],[120,92],[150,84],[180,66],[210,44]].map(([x, y]) => <circle key={x} className="art-a-dot" cx={x} cy={y} r="5" />)}<path className="art-tangent" d="M10,100 L230,70" /><path className="art-min" d="M10,104 L230,78" /><line className="art-cursor" x1="120" x2="120" y1="8" y2="114" /><circle className="art-dot" cx="120" cy="91" r="6" /></svg>;
  if (id === 'column-generation') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-tangent" d="M10,50 L230,50" /><path className="art-a" d="M20,20 C60,70 90,92 120,86 C150,80 170,40 220,22" /><path className="art-b" d="M20,30 C70,48 100,58 130,52 C160,46 190,34 220,26" /><line className="art-cursor" x1="112" x2="112" y1="50" y2="88" /><circle className="art-dot" cx="112" cy="88" r="6" /></svg>;
  if (id === 'branch-and-bound') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M15,30 C50,80 80,95 110,70 C135,50 160,55 185,85 C205,105 220,70 228,40" />{[[15,45,'art-gb'],[60,45,'art-gb'],[105,40,'art-gb'],[145,40,'art-tangent'],[185,43,'art-gb']].map(([x, w, c]) => <rect key={x as number} className={c as string} x={x as number} y="100" width={w as number} height="12" rx="4" fill="none" />)}<circle className="art-dot" cx="168" cy="106" r="5" /></svg>;
  if (id === 'lp-primer') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-min" d="M40,98 L95,40 L200,30 L215,72 L120,104 Z" fill="none" />{[[60,86],[150,44],[205,58]].map(([x, y]) => <circle key={x} className="art-a-dot" cx={x} cy={y} r="4" />)}<path className="art-tangent" d="M20,30 L150,120" /><circle className="art-dot" cx="120" cy="104" r="6" /></svg>;
  if (id === 'three-components') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-min" d="M120,10 L210,110 L30,110 Z" fill="none" /><path className="art-a" d="M75,60 C110,62 140,70 170,86" fill="none" /><path className="art-tangent" d="M92,74 L160,82" /><circle className="art-a-dot" cx="92" cy="74" r="5" /><circle className="art-b-dot" cx="160" cy="82" r="5" /><circle className="art-dot" cx="128" cy="78" r="6" /></svg>;
  return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden>{Array.from({ length: 60 }, (_, i) => { const c = i % 12, r = Math.floor(i / 12); const gb = c === 5 || c === 11; return <circle key={i} cx={22 + c * 18} cy={22 + r * 19} r={gb ? 6 : 5} className={gb ? (r % 2 ? 'art-b-site' : 'art-gb-site') : (i % 7 === 0 ? 'art-b-site' : 'art-a-site')} />; })}<rect className="art-gb" x="102" y="8" width="20" height="104" rx="6" /><rect className="art-gb" x="210" y="8" width="20" height="104" rx="6" /></svg>;
}
