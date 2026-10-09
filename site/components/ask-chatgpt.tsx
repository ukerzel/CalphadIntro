import { useContext } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { LaneContext } from '@/lib/lane';
import type { Lesson } from '@/lib/learning';
import { chatGPTLink, tutorContext } from '@/lib/tutor';

/** Opens ChatGPT in a new tab with the step's task and tutor instructions filled in; the learner's own account, sent only when they choose. */
export default function AskChatGPT({ lesson, stageKey }: { lesson: Lesson; stageKey: string }) {
  const { lane } = useContext(LaneContext), background = lane === 'M' ? 'materials science' as const : lane === 'O' ? 'operations research' as const : undefined;
  return <p className="ask-chatgpt">
    <a className="ask-chatgpt-link" data-ask="task" href={chatGPTLink(tutorContext(lesson, stageKey, background))} target="_blank" rel="noreferrer">
      Still stuck? Ask ChatGPT about this step<ArrowUpRight aria-hidden /><span className="sr-only"> (opens in a new tab)</span>
    </a>
    <span className="caption">Opens ChatGPT in a new tab with this task filled in, asking it to hint rather than answer. It uses your own ChatGPT account; nothing is sent until you press send there.</span>
  </p>;
}
