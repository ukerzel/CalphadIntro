import { ArrowUpRight } from 'lucide-react';
import type { Lesson } from '@/lib/learning';
import { chatGPTLink, tutorContext } from '@/lib/tutor';

/** Opens ChatGPT in a new tab with the step's task and tutor instructions filled in; the learner's own account, sent only when they choose. */
export default function AskChatGPT({ lesson, stageKey }: { lesson: Lesson; stageKey: string }) {
  return <p className="ask-chatgpt">
    <a className="ask-chatgpt-link" href={chatGPTLink(tutorContext(lesson, stageKey))} target="_blank" rel="noreferrer">
      Ask ChatGPT about this step<ArrowUpRight aria-hidden />
    </a>
    <span className="caption">Opens ChatGPT in a new tab with this task filled in, asking it to hint rather than answer. It uses your own ChatGPT account; nothing is sent until you press send there.</span>
  </p>;
}
