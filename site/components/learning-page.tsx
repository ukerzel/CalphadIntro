import type { ReactNode, RefObject } from 'react';
import type { Block, Lesson, PlainBlock } from '@/lib/learning';
import { meta, stages } from '@/lib/lesson-meta';
import type { Stage } from '@/lib/lesson-meta';
import StageIndex from '@/components/stage-index';
import AskChatGPT from '@/components/ask-chatgpt';
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
const revealKind = (label: string) => /^Show previously/.test(label) ? 'outputs' : /^Optional setup/.test(label) ? 'setup' : /^Self-check/.test(label) ? 'check' : 'practice';

function Reveal({ block }: { block: Extract<Block, { type: 'reveal' }> }) {
  return <details><summary>{block.label}</summary><div className="reveal-body">{block.blocks.map((child, i) => <Plain key={i} block={child} />)}</div></details>;
}

function Blocks({ blocks, figures = {}, rowIds, ask }: { blocks: Block[]; figures?: Record<number, ReactNode>; rowIds?: string; ask?: ReactNode }) {
  const out: ReactNode[] = [];
  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    if (isHelp(block)) {
      const ladder: Block[] = [];
      while (i < blocks.length && isHelp(blocks[i])) ladder.push(blocks[i++]);
      i--;
      out.push(<div key={i} className="help-ladder" role="group" aria-label="Help, one step at a time">
        <p className="help-title">Stuck? Open help one step at a time.</p>
        {ask}
        {ladder.map((step, k) => step.type === 'reveal' && <div key={k} className={`help-step ${/^Worked/.test(step.label) ? 'is-answer' : ''}`}><span className="help-index" aria-hidden>{k + 1}</span><Reveal block={step} /></div>)}
      </div>);
    } else if (block.type === 'reveal') {
      out.push(<div key={i} className={`reveal reveal-${revealKind(block.label)}`}><Reveal block={block} /></div>);
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
  const reference = variant === 'reference';
  const id = (key: string) => reference ? undefined : `${lesson.id}-${key}`;
  return <article className={`learning-page ${reference ? 'is-reference' : ''}`} id={reference ? undefined : lesson.id}>
    {!reference && <header className="lesson-head">
      <p className="lesson-kicker"><span className="lesson-number">Step {m.number}</span><span>{m.group}</span><span aria-hidden>·</span><span>{m.tag}</span></p>
      <h1 ref={headingRef} tabIndex={-1}>{lesson.title}</h1>
    </header>}
    <div className="lesson-layout">
      {!reference && <StageIndex lessonId={lesson.id} stages={list.map(({ key, label, kind }) => ({ key, label, kind }))} />}
      <div className="lesson-body">
        {list.map(stage => <section key={stage.key} id={id(stage.key)} className={`stage stage-${stage.kind}`} aria-labelledby={id(`${stage.key}-h`)}>
          <h2 id={id(`${stage.key}-h`)} className="stage-label" tabIndex={-1}><span className="stage-mark" aria-hidden />{stage.label}</h2>
          <div className="stage-body"><Blocks blocks={stage.blocks} figures={stageFigures(lesson.id, stage)} rowIds={!reference && stage.kind === 'glossary' ? `${lesson.id}-g-` : undefined}
            ask={reference ? undefined : <AskChatGPT lesson={lesson} stageKey={stage.key} />} /></div>
          {stage.key === target && dock}
        </section>)}
        {!reference && <footer className="lesson-sources"><p>Course source files for this step:</p><ul>{lesson.sources.map(source => <li key={source}><a href={fileURL(REPO_FILE_REF ?? 'main', source)}>{source}</a></li>)}</ul></footer>}
      </div>
    </div>
  </article>;
}
