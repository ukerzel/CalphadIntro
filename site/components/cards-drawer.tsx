'use client';
/** The side cards in a drawer: search by words or symbols, filter by deck, open one card at a time. */
import { useContext, useMemo, useState } from 'react';
import { Layers } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from '@/components/ui/sheet';
import { Rich } from '@/components/learning-page';
import { Segmented } from '@/components/lab-frame';
import { plainText } from '@/lib/learning';
import { cards, deckName } from '@/lib/cards';
import { conceptText } from '@/lib/tutor';
import AskConcept, { StepContext } from '@/components/ask-concept';
import type { Card } from '@/lib/cards';

type Filter = 'this' | 'all' | 'core' | 'M' | 'O';
const text = (card: Card) => [card.title, ...card.symbols, ...card.blocks.flatMap(b => b.type === 'list' ? b.items : b.type === 'paragraph' ? [b.text] : [])].map(plainText).join(' ').toLowerCase();

/** Filtered cards for a query and deck; exported for tests. */
export function findCards(query: string, filter: Filter, page?: string): Card[] {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  return cards.cards.filter(card => (filter === 'all' || (filter === 'this' ? !page || card.pages.includes(page) : filter === 'core' ? card.core : card.deck === filter || card.deck === 'both'))
    && words.every(word => text(card).includes(word)));
}

export function CardList({ query, filter, page }: { query: string; filter: Filter; page?: string }) {
  const list = useMemo(() => findCards(query, filter, page), [query, filter, page]);
  if (!list.length) return <p className="caption">No card matches. Try a shorter word or a symbol such as μ or Ω.</p>;
  return <ul className="card-list">{list.map(card => <li key={card.id}><details className="card-item" id={`card-${card.id}`}>
    <summary>{card.core && <span className="card-star" aria-label="core card">★</span>}<span>{card.title}</span><span className="card-deck">{deckName[card.deck]}</span></summary>
    <div className="card-body">
      {card.blocks.map((block, i) => block.type === 'list' ? <ul key={i}>{block.items.map((item, k) => <li key={k}><Rich text={item} /></li>)}</ul>
        : block.type === 'paragraph' ? <p key={i} className={/^Where you met it: /.test(block.text) ? 'card-met' : undefined}><Rich text={block.text} /></p> : null)}
      <p className="card-closing">{cards.closing}</p>
      <p className="caption">Needed for {card.pages.map(p => p === 'LP' ? 'the LP primer' : `step ${p}`).join(', ')}</p>
      <p className="ask-concept-row"><AskConcept concept={card.title} text={conceptText(card.blocks)} /></p>
    </div>
  </details></li>)}</ul>;
}

export default function CardsDrawer() {
  const where = useContext(StepContext), page = where?.step === 'LP primer' ? 'LP' : /^Step (\d\d)$/.exec(where?.step ?? '')?.[1];
  const [query, setQuery] = useState(''), [chosen, setFilter] = useState<Filter | null>(null), filter: Filter = chosen ?? (page ? 'this' : 'all');
  return <Sheet>
    <SheetTrigger className="nav-button" aria-label="Cards: short answers to hang-on questions"><Layers aria-hidden /><span>Cards</span></SheetTrigger>
    <SheetContent className="reference-sheet cards-sheet">
      <SheetHeader><SheetTitle>Cards</SheetTitle><SheetDescription>Short answers to &quot;hang on, what was this?&quot;, beside your current step. ★ marks the core cards.</SheetDescription></SheetHeader>
      <div className="reference-body">
        <label className="control-label" htmlFor="cards-search">Search words or symbols</label>
        <input id="cards-search" className="cards-search" type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="for example lever, μ, floor" />
        <Segmented label="Deck" value={filter} onChange={setFilter} options={[...(page ? [['this', 'This step'] as [Filter, string]] : []), ['all', 'All'], ['core', '★ Core'], ['M', 'Maths and optimisation'], ['O', 'Thermodynamics']]} />
        <CardList query={query} filter={filter} page={page} />
        <div className="ask-any" role="group" aria-label="Ask about any other term">
          <p className="caption">Looking for a term the cards do not cover, such as price and bound or convex hull?</p>
          <AskConcept concept={query.trim() || 'a term of my choice, named in my question'} text="" label={query.trim() ? `Ask ChatGPT about “${query.trim()}”` : 'Ask ChatGPT about any other term'} />
        </div>
      </div>
    </SheetContent>
  </Sheet>;
}
