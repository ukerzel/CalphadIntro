'use client';
import { createContext, useContext } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { LaneContext } from '@/lib/lane';
import { conceptLink } from '@/lib/tutor';
import type { Background } from '@/lib/tutor';

/** The step being read (label and title), for concept prompts asked from the cards drawer or a card popover. */
export const StepContext = createContext<{ step: string; title: string } | null>(null);

/** "Ask ChatGPT about this": opens ChatGPT in a new tab with the concept, the course's own text and the learner's background filled in. */
export default function AskConcept({ concept, text, around, background, label = 'Ask ChatGPT about this', rules, ending, kind = 'concept' }: {
  concept: string; text: string; around?: string; background?: Background; label?: string; rules?: string; ending?: string; kind?: 'concept' | 'check' | 'quiz' | 'section' | 'lab';
}) {
  const where = useContext(StepContext), { lane } = useContext(LaneContext);
  const chosen: Background | undefined = background ?? (lane === 'M' ? 'materials science' : lane === 'O' ? 'operations research' : undefined);
  const href = conceptLink({ step: where?.step, title: where?.title, concept, text, around, background: chosen }, rules, ending);
  return <a className="ask-chatgpt-link ask-concept" href={href} target="_blank" rel="noreferrer" data-ask={kind}
    title="Opens ChatGPT in a new tab with this text filled in. It uses your own ChatGPT account; nothing is sent until you press send there.">
    {label}<ArrowUpRight aria-hidden /><span className="sr-only"> (opens ChatGPT in a new tab; nothing is sent until you press send)</span>
  </a>;
}
