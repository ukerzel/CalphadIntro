'use client';
import type { RefObject } from 'react';
import { ArrowRight, ArrowUpRight } from 'lucide-react';
import HeroGraphic from '@/components/hero-graphic';
import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { labViews, meta, question } from '@/lib/lesson-meta';
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
  ['Nothing to install', 'Everything runs in the browser. If you want to rerun the real calculations, optional steps explain how.'],
  ['Your own pace', 'No login, no grades, nothing locked. Bring paper and a calculator.'],
];

export default function Home({ bundle, onLearn, onLab, headingRef, resume }: { bundle: Bundle | null; onLearn: (id: LearningID) => void; onLab?: (id: LearningID, view?: string) => void; headingRef?: RefObject<HTMLHeadingElement | null>; resume?: LearningID | null }) {
  const resumeLesson = resume ? lessons.find(item => item.id === resume) : undefined;
  const labs = lessons.filter(item => meta[item.id].lab && meta[item.id].group !== 'Real alloys').length;
  const explorers = lessons.filter(item => meta[item.id].lab && meta[item.id].group === 'Real alloys').length;
  return <div className="home">
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">CALPHAD School 2026 · Guided self-study</p>
        <h1 ref={headingRef} tabIndex={-1}>Equilibrium is the lowest Gibbs energy. <em>Learn to find it.</em></h1>
        <p className="hero-lede">A short route from basic thermodynamics to real Cu–Ni and Ni–Nb phase calculations. Work each problem on paper, then check it in an interactive lab.</p>
        <div className="hero-actions">
          {resumeLesson
            ? <><button type="button" className="button-primary" onClick={() => onLearn(resumeLesson.id)}>Continue: {resumeLesson.title.split(' · ')[0]} <ArrowRight aria-hidden /></button>
              <button type="button" className="button-secondary" onClick={() => onLearn('start')}>Back to the start</button></>
            : <><button type="button" className="button-primary" onClick={() => onLearn('start')}>Start with the refresher <ArrowRight aria-hidden /></button>
              <button type="button" className="button-secondary" onClick={() => onLearn('unary')}>Go to the first problem</button></>}
        </div>
        <ul className="hero-facts"><li><strong>{lessons.length}</strong>steps, 00–{meta[lessons.at(-1)!.id].number}</li><li><strong>{labs}</strong>interactive labs</li><li><strong>{explorers}</strong>real-alloy explorers</li><li><strong>0</strong>logins, grades or locks</li></ul>
      </div>
      <HeroGraphic bundle={bundle} />
    </section>

    <section className="home-section" id="route" aria-labelledby="route-title">
      <div className="section-head"><p className="section-number">01</p><div><h2 id="route-title">The route</h2><p>Step 00 is a refresher and glossary you can keep open; every later step poses one problem. Follow them in order or jump in anywhere; none is locked.</p></div></div>
      <ol className="route-cards">
        {lessons.map(lesson => { const m = meta[lesson.id]; return <li key={lesson.id} className={`route-card group-${m.group.split(' ')[0].toLowerCase()}`}>
          <button type="button" onClick={() => onLearn(lesson.id)}>
            <span className="route-meta"><span className="route-number">{m.number}</span><span>{m.group}</span></span>
            <span className="route-title">{lesson.title}</span>
            <span className="route-question">{question(lesson)}</span>
            <span className="route-lab">{m.labTitle ? <>Lab · {m.labTitle}</> : 'Reference · terms, potentials and a glossary'}<ArrowUpRight aria-hidden /></span>
          </button>
        </li>; })}
      </ol>
    </section>

    <section className="home-section" aria-labelledby="method-title">
      <div className="section-head"><p className="section-number">02</p><div><h2 id="method-title">How every step works</h2><p>Every step from 01 on follows this pattern. Try first, then reveal; the lab comes after your own reasoning, not instead of it.</p></div></div>
      <ol className="method">{method.map(([title, text], i) => <li key={title}><span className="method-index">{String(i + 1).padStart(2, '0')}</span><h3>{title}</h3><p>{text}</p></li>)}</ol>
    </section>

    <section className="home-section" aria-labelledby="labs-title">
      <div className="section-head"><p className="section-number">03</p><div><h2 id="labs-title">Interactive labs</h2><p>Drag, scrub or play through the calculated states. Each lab opens inside its lesson once you have tried the problem; the Labs menu in the header opens them directly.</p></div></div>
      <div className="lab-cards">
        {(['unary', 'binary', 'twophase', 'boundary'] as LearningID[]).map(id => <button key={id} type="button" className={`lab-card lab-card-${id}`} onClick={() => onLearn(id)}>
          <LabArt id={id} /><span className="lab-card-tag">{meta[id].tag}</span><span className="lab-card-title">{meta[id].labTitle}</span><span className="lab-card-line">{meta[id].labLine}</span>
        </button>)}
      </div>
      {onLab && <div className="picture-index">
        <h3 id="pictures-title">Every lab chart and diagram</h3>
        <p className="caption">Looking for a picture you saw earlier? Each entry opens its lab at that view.</p>
        <div className="picture-groups">{lessons.filter(item => labViews[item.id]?.length).map(item => <section key={item.id} aria-label={`Step ${meta[item.id].number} lab views`}>
          <p className="picture-step">Step {meta[item.id].number} · {meta[item.id].tag}</p>
          <ul>{labViews[item.id]!.map(([view, label, line]) => <li key={view}><button type="button" className="dock-view" onClick={() => onLab(item.id, view)}><strong>{label}</strong><span>{line}</span></button></li>)}</ul>
        </section>)}</div>
      </div>}
    </section>

    <section className="home-section trust" aria-labelledby="trust-title">
      <div className="section-head"><p className="section-number">04</p><div><h2 id="trust-title">How the course works</h2><p>Short steps. Each one asks a question, lets you work it out, and then shows the calculation.</p></div></div>
      <ul className="trust-grid">{trust.map(([title, text]) => <li key={title}><h3>{title}</h3><p>{text}</p></li>)}</ul>
    </section>

    {bundle && <section className="home-section paper-routes" aria-labelledby="paper-title">
      <div className="section-head"><p className="section-number">05</p><div><h2 id="paper-title">Printable worksheets</h2><p>Prefer paper? These are the in-class worksheets and instructor notes for Day 1 and Day 2.</p></div></div>
      <div className="paper-grid">{['primer', 'primer_day2'].map((folder, i) => <article key={folder}><h3>Day {i + 1}</h3><p>{i === 0 ? 'Thermodynamics, amounts and a unary equilibrium' : 'Binary chemical potentials and open/closed boundaries'}</p>
        <nav aria-label={`Day ${i + 1} paper resources`}>{[['README.md', 'Overview'], ['worksheet.md', 'Worksheet'], ['instructor.md', 'Instructor notes']].map(([name, label]) => <a key={name} href={sourceURL(bundle.receipt.source_commit, `course/${folder}/${name}`)}>{label}</a>)}
          <details><summary>Answers — after your attempt</summary><a href={sourceURL(bundle.receipt.source_commit, `course/${folder}/answers.md`)}>Open answer guide</a></details></nav></article>)}</div>
    </section>}
  </div>;
}

/** Hand-drawn decorative motifs (not data). */
function LabArt({ id }: { id: LearningID }) {
  if (id === 'unary') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M20,30 L220,92" /><path className="art-b" d="M20,16 L220,106" /><path className="art-min" d="M20,30 L120,61 L220,106" /><line className="art-cursor" x1="120" x2="120" y1="8" y2="114" /><circle className="art-dot" cx="120" cy="61" r="6" /></svg>;
  if (id === 'twophase') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-a" d="M20,30 C50,110 90,105 120,70" /><path className="art-b" d="M120,70 C150,105 190,110 220,30" /><path className="art-tangent" d="M10,96 L230,96" /><circle className="art-dot" cx="62" cy="96" r="5" /><circle className="art-dot" cx="178" cy="96" r="5" /></svg>;
  if (id === 'binary') return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden><path className="art-min" d="M20,40 C60,110 150,110 220,20" /><path className="art-tangent" d="M10,96 L230,58" /><circle className="art-dot" cx="96" cy="83" r="6" /><circle className="art-a-dot" cx="14" cy="95" r="4" /><circle className="art-b-dot" cx="226" cy="59" r="4" /></svg>;
  return <svg className="lab-art" viewBox="0 0 240 120" aria-hidden>{Array.from({ length: 60 }, (_, i) => { const c = i % 12, r = Math.floor(i / 12); const gb = c === 5 || c === 11; return <circle key={i} cx={22 + c * 18} cy={22 + r * 19} r={gb ? 6 : 5} className={gb ? (r % 2 ? 'art-b-site' : 'art-gb-site') : (i % 7 === 0 ? 'art-b-site' : 'art-a-site')} />; })}<rect className="art-gb" x="102" y="8" width="20" height="104" rx="6" /><rect className="art-gb" x="210" y="8" width="20" height="104" rx="6" /></svg>;
}
