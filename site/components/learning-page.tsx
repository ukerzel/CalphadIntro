import { useContext } from 'react';
import type { ReactNode, RefObject } from 'react';
import { LaneContext, opensFor } from '@/lib/lane';
import type { Lane } from '@/lib/lane';
import type { Block, Lesson, PlainBlock } from '@/lib/learning';
import { advancedMinutes, deeperStages, isAdvanced, isOptional, isPrimer, meta, pageLabel, stages, stepStory } from '@/lib/lesson-meta';
import { lessons } from '@/lib/learning';
import type { Stage } from '@/lib/lesson-meta';
import StageIndex from '@/components/stage-index';
import AskChatGPT from '@/components/ask-chatgpt';
import AskConcept from '@/components/ask-concept';
import { CHECK_RULES, QUIZ_RULES, conceptText } from '@/lib/tutor';
import type { Background } from '@/lib/tutor';
import Term from '@/components/term';
import XRef from '@/components/xref';
import Tex from '@/components/math';
import BoundaryFigure from '@/components/boundary-figure';
import ConstraintsFigure from '@/components/constraints-figure';
import { PipelineFigure, TdbLineFigure } from '@/components/calphad-figures';
import { BoundaryTangentFigure, CommonTangentFigure, PhaseDiagramsFigure, SublatticeFigure, TangentSketch } from '@/components/lesson-figures';
import { slug, splitTerms } from '@/lib/learning';
import { fileURL, REPO_FILE_REF } from '@/lib/data';

/** Narration text with its marked terms. */
export function Rich({ text }: { text: string }) {
  return <>{splitTerms(text).map((part, i) => typeof part === 'string' ? part : 'tex' in part ? <Tex key={i} tex={part.tex} />
    : 'ref' in part ? <XRef key={i} target={part.ref} shown={part.shown} render={value => <Rich text={value} />} /> : <Term key={i} id={part.id} shown={part.shown} />)}</>;
}

/** Multi-line narration: the first line and capitalised sentences are prose, other lines are commands. */
function Text({ text }: { text: string }) {
  const lines = text.split('\n');
  if (lines.length === 1 && /^In plain words: /.test(text))
    return <aside className="plain-words" role="note"><strong>In plain words</strong><p><Rich text={text.slice(16)} /></p></aside>;
  if (lines.length === 1 && /^Cards you may need: /.test(text))
    return <aside className="cards-needed" role="note"><strong>Cards you may need</strong><p><Rich text={text.slice(20)} /></p>
      <p className="ask-concept-row"><AskConcept concept="a term of my choice, named in my question" text="" label="Ask ChatGPT about another term" /></p></aside>;
  if (lines.length === 1) return /^Heads-up: /.test(text)
    ? <aside className="heads-up" role="note"><strong>Heads-up</strong><p><Rich text={text.slice(10)} /></p></aside>
    : <p><Rich text={text} /></p>;
  const groups: { code: boolean; lines: string[] }[] = [];
  lines.forEach((line, i) => {
    const code = i > 0 && !/^[A-Z][a-z’']+[ ,]/.test(line);
    const last = groups.at(-1);
    if (last && last.code === code) last.lines.push(line); else groups.push({ code, lines: [line] });
  });
  return <>{groups.map((group, i) => group.code
    ? <pre key={i} className="code" tabIndex={0} role="region" aria-label="Commands"><code>{group.lines.join('\n')}</code></pre>
    : <p key={i}><Rich text={group.lines.join(' ')} /></p>)}</>;
}

function Plain({ block, rowIds }: { block: PlainBlock; rowIds?: string }) {
  if (block.type === 'list') return <ul>{block.items.map((text, i) => <li key={i}><Rich text={text} /></li>)}</ul>;
  if (block.type === 'table') return <div className="learning-table" tabIndex={0} role="region" aria-label="Lesson table"><table><thead><tr>{block.headers.map((text, i) => <th key={i} scope="col">{text}</th>)}</tr></thead><tbody>{block.rows.map((row, i) => <tr key={i} id={rowIds && slug(row[0]) ? `${rowIds}${slug(row[0])}` : undefined}>{row.map((text, j) => j === 0 ? <th key={j} scope="row"><Rich text={text} /></th> : <td key={j}><Rich text={text} /></td>)}</tr>)}</tbody></table></div>;
  return <>
    <Text text={block.text} />
    {block.links && <ul className="learning-links">{block.links.map(link => <li key={link.href}><a href={link.href}>{link.label}</a></li>)}</ul>}
    {block.image && <figure className="saved-figure"><img src={block.image.src} alt={block.image.alt} loading="lazy" /><figcaption><a href={block.image.src}>Open the full-size image</a></figcaption></figure>}
  </>;
}

const isHelp = (block: Block) => block.type === 'reveal' && /^(Hint \d|Worked answer)/.test(block.label);
const revealKind = (label: string) => /^Show previously/.test(label) ? 'outputs' : /^Optional setup/.test(label) ? 'setup' : /^(Self-check|Check|Answers)\b/.test(label) ? 'check'
  : /^Dive deeper for operations research/.test(label) ? 'deeper-or' : /^Dive deeper/.test(label) ? 'deeper' : /^Coming from materials/.test(label) ? 'lane-m' : /^Coming from operations research/.test(label) ? 'lane-o' : 'practice';

/** Concept boxes (dive deeper, one background) get "Ask ChatGPT about this"; the concept is the box's own title, or the stage's for background boxes. */
const conceptBackground: Record<string, Background | undefined> = { 'deeper-or': 'operations research', 'lane-o': 'operations research', 'lane-m': 'materials science' };
function conceptOf(label: string, stage?: string): string | null {
  const kind = revealKind(label);
  if (kind === 'deeper' || kind === 'deeper-or') return label.replace(/^Dive deeper( for operations research)? · /, '').replace(/\s*\(about [^)]*\)$/, '');
  if (kind === 'lane-m' || kind === 'lane-o') return stage ?? 'this section';
  return null;
}

function Reveal({ block, stage, around, questions }: { block: Extract<Block, { type: 'reveal' }>; stage?: string; around?: string; questions?: boolean }) {
  const { lane } = useContext(LaneContext), kind = revealKind(block.label), open = opensFor(lane, kind), concept = conceptOf(block.label, stage);
  return <details key={lane ?? 'none'} open={open || undefined}><summary>{block.label}</summary><div className="reveal-body">{block.blocks.map((child, i) => <Plain key={i} block={child} />)}
    {concept && <p className="ask-concept-row"><AskConcept concept={concept} text={conceptText(block.blocks)} around={around} background={conceptBackground[kind]} /></p>}
    {questions && <p className="ask-concept-row"><AskConcept kind="check" label="Check my answers with ChatGPT" concept={`my answers to “${block.label.replace(/^(Self-check|Check) · /, '')}”`} text={conceptText(block.blocks)} rules={CHECK_RULES} ending="My answers:" /></p>}</div></details>;
}

/** Route strip on every step after 00: what the last step concluded, where you are; on the advanced steps also the time and which boxes open. */
function RouteStrip({ lesson }: { lesson: Lesson }) {
  const id = lesson.id, { lane, setLane } = useContext(LaneContext), m = meta[id], last = meta[lessons[lessons.length - 1].id].number;
  const choose = (value: Lane) => setLane(lane === value ? null : value);
  const advanced = isAdvanced(id), minutes = advancedMinutes[id];
  const hasLaneBoxes = JSON.stringify(lesson.blocks).includes('"label":"Coming from');
  return <div className="route-strip" role="group" aria-label="Where you are">
    {stepStory[id] && <p className="route-story">{stepStory[id]}</p>}
    <p className="route-where">{isPrimer(id) ? 'Optional primer, after step 07, before step 10' : `Step ${m.number} of ${last}`}{advanced ? ' · advanced' : ''}{minutes ? ` · about ${minutes.replace(/^about /, '')} minutes without the optional boxes` : ''}{advanced || deeperStages[id] ? ' · “Dive deeper” sections are optional' : ''}</p>
    {hasLaneBoxes && <div className="segmented lane-toggle" role="group" aria-label="Open the boxes for your background">
      <span className="caption">Open the boxes for readers from:</span>
      <button type="button" aria-pressed={lane === 'M'} onClick={() => choose('M')}>materials science</button>
      <button type="button" aria-pressed={lane === 'O'} onClick={() => choose('O')}>operations research</button>
    </div>}
  </div>;
}

function Blocks({ blocks, figures = {}, rowIds, ask, stage }: { blocks: Block[]; figures?: Record<number, ReactNode>; rowIds?: string; ask?: ReactNode; stage?: string }) {
  const out: ReactNode[] = [], around = conceptText(blocks.filter(block => block.type !== 'reveal'));
  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    if (isHelp(block)) {
      const ladder: Block[] = [];
      while (i < blocks.length && isHelp(blocks[i])) ladder.push(blocks[i++]);
      i--;
      out.push(<div key={i} className="help-ladder" role="group" aria-label="Help, one step at a time">
        <p className="help-title">Stuck? Open help one step at a time.</p>
        {ladder.map((step, k) => step.type === 'reveal' && <div key={k} className={`help-step ${/^Worked/.test(step.label) ? 'is-answer' : ''}`}><span className="help-index" aria-hidden>{k + 1}</span><Reveal block={step} /></div>)}
        {ask}
      </div>);
    } else if (block.type === 'reveal') {
      const next = blocks[i + 1], questions = revealKind(block.label) === 'check' && !/answer/i.test(block.label) && next?.type === 'reveal' && /answer/i.test(next.label);   // a question box with a separate answers box
      out.push(<div key={i} className={`reveal reveal-${revealKind(block.label)}`}><Reveal block={block} stage={stage} around={around} questions={questions} /></div>);
    } else out.push(<Plain key={i} block={block} rowIds={block.type === 'table' ? rowIds : undefined} />);
    if (figures[i]) out.push(<div key={`figure-${i}`}>{figures[i]}</div>);
  }
  return <>{out}</>;
}

/** Stage that receives the explicitly opened lab: Explore, or the saved-output reveal on material pages. */
function dockStage(list: Stage[]): string | undefined {
  return (list.find(stage => stage.kind === 'explore')
    ?? list.find(stage => stage.blocks.some(block => block.type === 'reveal' && /^Show previously/.test(block.label)))
    ?? list.find(stage => stage.kind === 'attempt')
    ?? list.at(-1))?.key;
}

/** Static sketches placed after a given block of a stage (index within the stage). */
function stageFigures(lessonId: string, stage: Stage): Record<number, ReactNode> {
  if (lessonId === 'boundary' && stage.kind === 'problem') return { 0: <BoundaryFigure /> };
  if (lessonId === 'start' && stage.kind === 'why') return { 0: <PipelineFigure /> };
  if (lessonId === 'cuni' && stage.kind === 'extension') return { 0: <TdbLineFigure /> };
  if (lessonId === 'binary' && stage.key === 'tangent-and-chemical-potentials') return { 0: <TangentSketch /> };
  if (lessonId === 'twophase' && stage.kind === 'attempt') {
    const i = stage.blocks.findIndex(block => block.type === 'reveal' && block.label === 'Worked answer');
    return i >= 0 ? { [i]: <CommonTangentFigure /> } : {};
  }
  if (lessonId === 'twophase' && stage.key === 'reading-a-phase-diagram') return { 0: <PhaseDiagramsFigure /> };
  if (lessonId === 'boundary' && stage.key === 'where-the-odds-formula-comes-from') return { 0: <BoundaryTangentFigure /> };
  if (lessonId === 'ninb' && stage.kind === 'problem') {
    const i = stage.blocks.findIndex(block => block.type === 'paragraph' && block.text.startsWith('A sublattice is a group'));
    return i >= 0 ? { [i]: <SublatticeFigure /> } : {};
  }
  if (lessonId === 'start' && stage.kind === 'refresher') {
    const i = stage.blocks.findIndex(block => block.type === 'paragraph' && block.text.startsWith('The minimum rules above'));
    return i >= 0 ? { [i]: <ConstraintsFigure /> } : {};
  }
  return {};
}

export default function LearningPage({ lesson, headingRef, dock, variant = 'page' }: { lesson: Lesson; headingRef?: RefObject<HTMLHeadingElement | null>; dock?: ReactNode; variant?: 'page' | 'reference' }) {
  const list = stages(lesson), m = meta[lesson.id], target = dock ? dockStage(list) : undefined;
  const quizStage = list.filter(item => item.kind === 'interpret').at(-1)?.key;   // one quiz per step, at its last Interpret stage
  const reference = variant === 'reference';
  const id = (key: string) => reference ? undefined : `${lesson.id}-${key}`;
  return <article className={`learning-page ${reference ? 'is-reference' : ''}`} id={reference ? undefined : lesson.id}>
    {!reference && <header className="lesson-head">
      <p className="lesson-kicker"><span className="lesson-number">{pageLabel(lesson.id)}</span>{isAdvanced(lesson.id) ? <span className="advanced-tag">Advanced</span> : <span>{m.group}</span>}{isOptional(lesson.id) && <span className="optional-tag">Optional</span>}<span aria-hidden>·</span><span>{m.tag}</span></p>
      <h1 ref={headingRef} tabIndex={-1}>{lesson.title}</h1>
      {lesson.id !== 'start' && <RouteStrip lesson={lesson} />}
    </header>}
    <div className="lesson-layout">
      {!reference && <StageIndex lessonId={lesson.id} stages={list.map(({ key, label, kind }) => ({ key, label, kind }))} />}
      <div className="lesson-body">
        {list.map(stage => <section key={stage.key} id={id(stage.key)} className={`stage stage-${stage.kind}`} aria-labelledby={id(`${stage.key}-h`)}>
          <h2 id={id(`${stage.key}-h`)} className="stage-label" tabIndex={-1}><span className="stage-mark" aria-hidden />{stage.label}
            {deeperStages[lesson.id]?.includes(stage.key) && <span className="deeper-flag">Optional</span>}</h2>
          {deeperStages[lesson.id]?.includes(stage.key)
            ? <div className="reveal reveal-deeper"><details><summary>Dive deeper · {stage.label[0].toLowerCase() + stage.label.slice(1)} (optional section)</summary><div className="reveal-body"><Blocks blocks={stage.blocks} figures={stageFigures(lesson.id, stage)} stage={stage.label}
              ask={reference ? undefined : <AskChatGPT lesson={lesson} stageKey={stage.key} />} />
              {!reference && <p className="ask-concept-row"><AskConcept concept={stage.label} text={conceptText(stage.blocks)} /></p>}</div></details></div>
            : <div className="stage-body"><Blocks blocks={stage.blocks} figures={stageFigures(lesson.id, stage)} stage={stage.label} rowIds={!reference && stage.kind === 'glossary' ? `${lesson.id}-g-` : undefined}
              ask={reference ? undefined : <AskChatGPT lesson={lesson} stageKey={stage.key} />} />
              {!reference && (stage.kind === 'note' || stage.kind === 'approach') && <p className="ask-concept-row"><AskConcept kind="section" label="Ask ChatGPT to explain this section" concept={stage.label} text={conceptText(stage.blocks)} /></p>}
              {!reference && stage.key === quizStage && lesson.id !== 'start' && <p className="ask-concept-row"><AskConcept kind="quiz" label="Quiz me on this step with ChatGPT" concept={`${lesson.title}`} text={[...list.filter(item => item.kind === 'problem'), stage].map(item => conceptText(item.blocks)).join('\n')} rules={QUIZ_RULES} ending="Start the quiz." /></p>}</div>}
          {stage.key === target && dock}
        </section>)}
        {!reference && <footer className="lesson-sources"><p>Course source files for this step:</p><ul>{lesson.sources.map(source => <li key={source}><a href={fileURL(REPO_FILE_REF ?? 'main', source)}>{source}</a></li>)}</ul></footer>}
      </div>
    </div>
  </article>;
}
