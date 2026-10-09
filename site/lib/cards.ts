/** Side cards: short answers to "hang on, what was this?" (course/self_study/cards.json). No science is computed. */
import content from '../public/learning/cards.json';
import type { PlainBlock } from './learning';

export type Deck = 'M' | 'O' | 'both';
export type Card = { id: string; deck: Deck; kind: 'term' | 'hang-on' | 'maths' | 'thermo'; title: string; core: boolean; pages: string[]; symbols: string[]; blocks: PlainBlock[] };
export const cards = content as { schema_version: number; closing: string; cards: Card[] };
export const deckName: Record<Deck, string> = { M: 'maths and optimisation', O: 'thermodynamics', both: 'both decks' };
