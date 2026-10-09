/** Cross-references in the narration: [[target|shown]]. Targets name a step, a step's stage, a lab view or a glossary row. */
import { lesson, lessons, plainText, slug } from './learning';
import type { LearningID, PlainBlock } from './learning';
import { labViews, meta, pageLabel, stages } from './lesson-meta';
import { cards, deckName } from './cards';
import type { Route } from './route';

export type Target =
  | { kind: 'lesson'; id: LearningID }
  | { kind: 'stage'; id: LearningID; anchor: string }
  | { kind: 'lab'; id: LearningID; view?: string }
  | { kind: 'glossary'; anchor: string }
  | { kind: 'card'; id: string };

const ids = lessons.map(item => item.id) as string[];

/** "binary", "binary#approach", "twophase/lab/part-b", "glossary#lever-rule", "card#lever-rule", "menu#problem"; null when malformed. */
export function parseTarget(text: string): Target | null {
  const glossary = /^glossary#([a-z0-9-]+)$/.exec(text);
  if (glossary) return { kind: 'glossary', anchor: glossary[1] };
  const card = /^card#([a-z0-9-]+)$/.exec(text);
  if (card) return { kind: 'card', id: card[1] };
  const match = /^([a-z][a-z0-9-]*?)(?:#([a-z0-9-]+)|\/lab(?:\/([a-z][a-z-]*))?)?$/.exec(text);
  if (!match || !ids.includes(match[1])) return null;
  const id = match[1] as LearningID;
  if (match[2]) return { kind: 'stage', id, anchor: match[2] };
  if (text.includes('/lab')) return { kind: 'lab', id, ...(match[3] ? { view: match[3] } : {}) };
  return { kind: 'lesson', id };
}

export const glossaryRows = () => {
  const stage = stages(lesson('start')).find(item => item.kind === 'glossary');
  const table = stage?.blocks.find(block => block.type === 'table');
  return table && table.type === 'table' ? table.rows.map(row => ({ anchor: slug(row[0]), term: row[0], meaning: row[1] })) : [];
};

const clip = (text: string, length = 260) => text.length <= length ? text : `${text.slice(0, text.lastIndexOf(' ', length))} …`;

export type Described = { title: string; excerpt?: string; rich?: string; blocks?: PlainBlock[]; closing?: string; action: string; route?: Route };

/** Everything the popover shows, or null when the target does not exist (tests reject those). */
export function describe(target: Target): Described | null {
  if (target.kind === 'glossary') {
    const row = glossaryRows().find(item => item.anchor === target.anchor);
    return row ? { title: `Glossary · ${plainText(row.term)}`, rich: row.meaning, action: 'Open the glossary here', route: { page: 'lesson', id: 'start', lab: false, anchor: `g-${row.anchor}` } } : null;
  }
  if (target.kind === 'card') {
    const card = cards.cards.find(item => item.id === target.id);
    return card ? { title: card.title, excerpt: `Card · ${deckName[card.deck]}`, blocks: card.blocks, closing: cards.closing, action: '' } : null;
  }
  const m = meta[target.id], item = lesson(target.id), label = pageLabel(target.id), lower = pageLabel(target.id, true);
  if (target.kind === 'lesson') return { title: `${label} · ${item.title}`, action: `Go to ${lower}`, route: { page: 'lesson', id: target.id, lab: false } };
  if (target.kind === 'stage') {
    const stage = stages(item).find(entry => entry.key === target.anchor);
    if (!stage) return null;
    const first = stage.blocks.find(block => block.type === 'paragraph');
    return { title: `${label} · ${stage.label}`, excerpt: first && first.type === 'paragraph' ? clip(plainText(first.text)) : undefined,
      action: `Go to ${lower} · ${stage.label}`, route: { page: 'lesson', id: target.id, lab: false, anchor: target.anchor } };
  }
  if (!m.lab) return null;
  const views = labViews[target.id] ?? [], view = target.view ? views.find(entry => entry[0] === target.view) : undefined;
  if (target.view && !view) return null;
  return { title: `${label} lab · ${view ? view[1] : m.labTitle}`, excerpt: view ? view[2] : m.labLine ?? undefined,
    action: 'Open the lab here', route: { page: 'lesson', id: target.id, lab: true, ...(view ? { view: view[0] } : {}) } };
}
