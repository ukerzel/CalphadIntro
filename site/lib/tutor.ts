/** Tutor prompts for the self-study steps.
 *
 * Used now by "Ask ChatGPT about this step" (the learner's own ChatGPT account,
 * opened in a new tab with the prompt filled in). Prepared for a course tutor on
 * an OpenAI-compatible API such as KI:connect; that part is not switched on.
 * Prompts carry the step's task, never its hints or worked answer.
 */
import { plainText, splitTerms } from './learning';
import type { Block, Lesson } from './learning';
import { meta, stages } from './lesson-meta';

export const TUTOR_RULES = [
  'Act as a patient tutor for an introductory CALPHAD self-study course (invented example models first, then published Cu–Ni and Ni–Nb databases).',
  'Ask what I have tried before helping. Give one hint at a time; do not give the full worked answer unless I ask for it after showing my attempt.',
  'Keep to the definitions, units and amount basis stated in the task (for example J/mol of atoms). Point out unit or basis mistakes.',
  'The step’s models are invented unless the task says otherwise: do not claim they describe a real material, and do not invent material data or literature values.',
  'If my question goes beyond this step, say so briefly and suggest what to look up.',
].join(' ');

export type TutorContext = { step: string; title: string; question: string; stage: string; task: string };

const MAX_TASK = 1200, MAX_BACKGROUND = 1700; // characters: keeps the ChatGPT link a safe length

const clip = (text: string, max: number) => text.length <= max ? text : `${text.slice(0, text.lastIndexOf(' ', max))} …`;

/** Narration text for a prompt: formulas stay as $TeX$ (chat models read LaTeX), term notes and links become their words. */
export function promptText(text: string): string {
  return splitTerms(text).map(part => typeof part === 'string' ? part : 'tex' in part ? `$${part.tex}$` : part.shown).join('');
}

/** Learner-visible task text of a stage: paragraphs, lists and tables, never reveals (hints, answers, self-checks). */
export function taskText(blocks: Block[]): string {
  const parts: string[] = [];
  for (const block of blocks) {
    if (block.type === 'paragraph') parts.push(promptText(block.text));
    else if (block.type === 'list') parts.push(block.items.map(item => `- ${promptText(item)}`).join('\n'));
    else if (block.type === 'table') parts.push([block.headers, ...block.rows].map(row => row.map(cell => promptText(cell)).join(' | ')).join('\n'));
  }
  return parts.join('\n');
}

/** Context for one stage of a lesson: the stage's own task first, then the Problem stage as shortened background. */
export function tutorContext(lesson: Lesson, stageKey: string): TutorContext {
  const list = stages(lesson), stage = list.find(item => item.key === stageKey) ?? list[0];
  const problem = list.find(item => item.kind === 'problem');
  const own = clip(taskText(stage.blocks), MAX_TASK);
  const task = problem && problem.key !== stage.key ? `${own}\n\nBackground (${problem.label}):\n${clip(taskText(problem.blocks), MAX_BACKGROUND)}` : own;
  const first = lesson.blocks.find(block => block.type === 'paragraph');
  const question = first && first.type === 'paragraph' ? plainText(first.text).replace(/^[A-Z][A-Za-z :,-]{2,40} · /, '').split('?')[0] + '?' : lesson.title;
  return { step: meta[lesson.id].number, title: lesson.title, question, stage: stage.label, task };
}

/** The prompt a learner sends: rules, the step and its task, then room for their own attempt. */
export function tutorPrompt(context: TutorContext): string {
  return [
    TUTOR_RULES,
    '',
    `Step ${context.step} · ${context.title} (${context.stage})`,
    `Question: ${context.question}`,
    '',
    'Task:',
    context.task,
    '',
    'My attempt so far: ',
  ].join('\n');
}

/** chatgpt.com opens a new conversation with ?q= filled in; the learner edits and sends it. */
export const chatGPTLink = (context: TutorContext) => `https://chatgpt.com/?q=${encodeURIComponent(tutorPrompt(context))}`;

/* ---- Prepared for an OpenAI-compatible course tutor (not switched on) ---- */

export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };
export type ProviderSettings = { baseURL: string; model: string; apiKey: string };

/** KI:connect's documented OpenAI-compatible endpoint; the model ID is set when a course key exists. */
export const KICONNECT_BASE_URL = 'https://chat.kiconnect.nrw/api/v1';

/** Request for POST {baseURL}/chat/completions: the step context goes into the system message. */
export function chatRequest(settings: ProviderSettings, context: TutorContext, history: ChatMessage[]): { url: string; init: RequestInit } {
  const system = `${TUTOR_RULES}\n\nStep ${context.step} · ${context.title} (${context.stage})\nQuestion: ${context.question}\n\nTask:\n${context.task}`;
  const messages: ChatMessage[] = [{ role: 'system', content: system }, ...history.filter(m => m.role !== 'system').slice(-12)];
  return {
    url: `${settings.baseURL.replace(/\/$/, '')}/chat/completions`,
    init: { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${settings.apiKey}` },
      body: JSON.stringify({ model: settings.model, messages, temperature: 0.2, max_tokens: 700 }) },
  };
}

/** The reply text from an OpenAI-compatible response, or null if the response has none. */
export function chatReply(response: unknown): string | null {
  const choice = (response as { choices?: { message?: { content?: unknown } }[] })?.choices?.[0];
  return typeof choice?.message?.content === 'string' && choice.message.content.trim() ? choice.message.content : null;
}
