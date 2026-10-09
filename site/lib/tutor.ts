/** Tutor prompts for the self-study steps.
 *
 * Used now by "Ask ChatGPT about this step" (the learner's own ChatGPT account,
 * opened in a new tab with the prompt filled in). Prepared for a course tutor on
 * an OpenAI-compatible API such as KI:connect; that part is not switched on.
 * Prompts carry the step's task, never its hints or worked answer.
 */
import { plainText, splitTerms } from './learning';
import type { Block, Lesson } from './learning';
import { lessons } from './learning';
import { meta, pageLabel, stages } from './lesson-meta';
import type { Stage } from './lesson-meta';

/** Extra rules by part of the course: the words and pitfalls where a chat model tends to go wrong. */
const PART_RULES: Partial<Record<string, string>> = {
  basics: 'Compute logarithms and other numbers with code or a calculator and show the formula; do not do six-digit arithmetic in your head.',
  databases: 'pycalphad 0.11.2 is pinned: write code for that version. GM is per mole of atoms, not per formula unit. The magnetic contribution is most negative at low temperature and does not vanish above the Curie temperature. Do not quote real-system values (temperatures, compositions, phase boundaries) without a source.',
  primer: 'This page is a linear-programming primer with an invented melt-shop example: amounts in kg, Ni content as a mass fraction, prices in € per kg. The variables are amounts f, never x. A price of a rule is the change of the best cost per unit change of its right-hand side; for a ≥ rule written as −(…) ≤ −b, SciPy\u2019s marginal flips sign.',
  advanced: 'Course words: a menu is a list of candidate states (one phase model at one composition); the ceiling is the energy of the best menu mixture (an upper bound) and a floor is a lower bound; the line under the dots has intercept μA and slope Δμ = μB − μA, the dual prices of the two atom balances; a state\u2019s gap is its energy minus the line (its reduced cost), and the driving force is minus the most negative gap. Amounts are f; x and z are compositions. Ceiling minus floor is the remaining uncertainty (the optimality gap); \u201cgap\u201d alone means a state\u2019s reduced cost. When z sits on a used dot the line can rotate and the prices are not unique (no simplex pivot is meant). Branch-and-bound here is spatial, on one continuous composition, not on integers, and in floating point it is a teaching check, not a rigorous proof. In step 18 the line becomes a plane with heights μA, μB, μC. Compute numbers with code and show the formula.',
};
const partOf = (id: string) => id === 'lp-primer' ? 'primer' : id === 'cuni' || id === 'ninb' ? 'databases' : ['start', 'unary', 'binary', 'twophase', 'boundary'].includes(id) ? 'basics' : 'advanced';
/** The tutor rules for a step: the general rules plus those of its part of the course. */
export const tutorRules = (id: string) => [TUTOR_RULES, PART_RULES[partOf(id)]].filter(Boolean).join(' ');

export const TUTOR_RULES = [
  'Act as a patient tutor for an introductory CALPHAD self-study course (invented example models first, then published Cu–Ni and Ni–Nb databases).',
  'Ask what I have tried before helping. Give one hint at a time; do not give the full worked answer unless I ask for it after showing my attempt.',
  'Keep to the definitions, units and amount basis stated in the task (for example J/mol of atoms). Point out unit or basis mistakes.',
  'The step’s models are invented unless the task says otherwise: do not claim they describe a real material, and do not invent material data or literature values.',
  'If my question goes beyond this step, say so briefly and suggest what to look up.',
].join(' ');

export type TutorContext = { step: string; title: string; question: string; stage: string; task: string; rules?: string; background?: Background };

const MAX_TASK = 1200, MAX_DATA = 1800, MAX_BACKGROUND = 1500; // characters of course text
const MAX_URL = 7500; // encoded characters of the whole ChatGPT link: longer links can fail to open

const clip = (text: string, max: number) => text.length <= max ? text : `${text.slice(0, text.lastIndexOf(' ', max))} …`;

/** Narration text for a prompt: formulas stay as $TeX$ (chat models read LaTeX), term notes and links become their words. */
export function promptText(text: string): string {
  return splitTerms(text).map(part => typeof part === 'string' ? part : 'tex' in part ? `$${part.tex}$` : part.shown).join('');
}

const tableText = (block: Extract<Block, { type: 'table' }>) => [block.headers, ...block.rows].map(row => row.map(cell => promptText(cell)).join(' | ')).join('\n');

/** Learner-visible task text of a stage: paragraphs, lists and (unless left out) tables, never reveals (hints, answers, self-checks). */
export function taskText(blocks: Block[], tables = true): string {
  const parts: string[] = [];
  for (const block of blocks) {
    if (block.type === 'paragraph') parts.push(promptText(block.text));
    else if (block.type === 'list') parts.push(block.items.map(item => `- ${promptText(item)}`).join('\n'));
    else if (block.type === 'table' && tables) parts.push(tableText(block));
  }
  return parts.join('\n');
}

/** Tables a task may rely on ("use the table above", "the menu of step 10"): the page's earlier stages, nearest first,
 *  then the tables of any step the task names. Only stage tables, never those inside hints or answers. */
export function dataText(lesson: Lesson, stage: Stage): string {
  const list = stages(lesson), at = list.findIndex(item => item.key === stage.key);
  const tablesOf = (items: Stage[], from = '') => items.flatMap(item => item.blocks.flatMap(block => block.type === 'table' ? [`${from}${item.label}:\n${tableText(block)}`] : []));
  const earlier = list.slice(0, Math.max(at, 0)).reverse(), own = taskText(stage.blocks);
  const parts = /\b(?:numbers|setup|rules) above\b/i.test(own)   // the data sit in the text of the stages just above
    ? earlier.filter(item => item.kind !== 'problem').map(item => `${item.label}:\n${taskText(item.blocks)}`)
    : tablesOf(earlier);
  const named = [...own.matchAll(/\b(?:table|menu|rounds|numbers) of step (\d\d)\b/gi)].map(m => m[1]);
  for (const number of new Set(named)) {
    const other = lessons.find(item => meta[item.id].number === number && item.id !== lesson.id);
    if (other) parts.push(...tablesOf(stages(other), `Step ${number}, `));
  }
  return parts.join('\n\n');
}

/** Context for one stage of a lesson: the stage's own task, the tables it relies on, then the Problem stage as shortened
 *  background (its tables already count as data). Background, then data, shrink until the ChatGPT link is short enough. */
export function tutorContext(lesson: Lesson, stageKey: string, background?: Background): TutorContext {
  const list = stages(lesson), stage = list.find(item => item.key === stageKey) ?? list[0];
  const problem = list.find(item => item.kind === 'problem');
  const own = clip(taskText(stage.blocks), MAX_TASK), data = dataText(lesson, stage);
  const problemText = problem && problem.key !== stage.key ? taskText(problem.blocks, false) : '';
  const first = lesson.blocks.find(block => block.type === 'paragraph' && !/^(In plain words|Heads-up|Cards you may need): /.test(block.text));
  const question = first && first.type === 'paragraph' ? plainText(first.text).replace(/^\p{Lu}[\p{L} :,-]{2,40} · /u, '').split('?')[0] + '?' : lesson.title;
  const build = (dataMax: number, backgroundMax: number): TutorContext => ({
    step: pageLabel(lesson.id), title: lesson.title, question, stage: stage.label, rules: tutorRules(lesson.id), background,
    task: [own, data && `Data from the course page:\n${clip(data, dataMax)}`, problemText && `Background (${problem!.label}):\n${clip(problemText, backgroundMax)}`].filter(Boolean).join('\n\n'),
  });
  let dataMax = MAX_DATA, backgroundMax = MAX_BACKGROUND, context = build(dataMax, backgroundMax);
  while (chatGPTLink(context).length > MAX_URL && dataMax > 200) {
    if (backgroundMax > 300) backgroundMax -= 150; else dataMax -= 150;
    context = build(dataMax, backgroundMax);
  }
  return context;
}

/** The prompt a learner sends: rules, the step and its task, then room for their own attempt. */
export function tutorPrompt(context: TutorContext): string {
  return [
    context.rules ?? TUTOR_RULES,
    '',
    `${context.step} · ${context.title} (${context.stage})`,
    ...(context.background ? [`My background: ${context.background}; connect the help to what I know from it.`] : []),
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

/* ---- Concepts: "Ask ChatGPT about this" on dive-deeper boxes, background boxes and side cards ---- */

export const CONCEPT_RULES = [
  'Act as a patient tutor for a self-study course on CALPHAD (phase equilibria from Gibbs energies) that also reads the equilibrium calculation as an optimisation problem (linear programming, duality and prices, column generation, bounds, branch-and-bound).',
  'Explain the concept below at the level of the course, starting from the course text quoted here and keeping its symbols and units (for example J/mol of atoms).',
  'If my background is given, connect the idea to what I already know from it, and translate the other field’s words into mine.',
  'Use one small example where it helps, check my understanding with one short question, and offer to go deeper.',
  'If you go beyond the course text, say so. The course models are invented unless the text says otherwise: do not claim they describe a real material, and do not invent material data or literature values.',
].join(' ');

export type Background = 'materials science' | 'operations research';
export type ConceptContext = { step?: string; title?: string; concept: string; text: string; around?: string; background?: Background };

const MAX_CONCEPT = 2000, MAX_AROUND = 900; // characters of course text: keeps the ChatGPT link a safe length

/** Hints, worked answers, self-checks and answers stay out of every prompt. */
const isAnswer = (label: string) => /^(Hint \d|Worked answer|Self-check|Check\b|Answers)/.test(label);

/** Course text of a box or card: paragraphs and list items, formulas as $TeX$, links as their words; never hints or answers. */
export function conceptText(blocks: Block[]): string {
  const parts: string[] = [];
  for (const block of blocks) {
    if (block.type === 'paragraph') parts.push(promptText(block.text));
    else if (block.type === 'list') parts.push(block.items.map(item => `- ${promptText(item)}`).join('\n'));
    else if (block.type === 'table') parts.push([block.headers, ...block.rows].map(row => row.map(cell => promptText(cell)).join(' | ')).join('\n'));
    else if (block.type === 'reveal' && !isAnswer(block.label)) parts.push(conceptText(block.blocks));
  }
  return parts.join('\n');
}

/** Check my answers: the questions only (never the course's answers); the tutor marks the learner's own answers. */
export const CHECK_RULES = 'Act as a patient tutor for a self-study course on CALPHAD and its optimisation view. Below are questions from the course; I will add my own answers. Do not show model answers first. For each of my answers, say whether it is right; if it is not, point to the mistake with one hint and let me try again. Compute numbers with code, not in your head, and keep the course\u2019s symbols and units.';
/** Quiz me: short questions on the course text of one section, one at a time. */
export const QUIZ_RULES = 'Act as a patient tutor for a self-study course on CALPHAD and its optimisation view. Quiz me on the course text below: ask three short questions, one at a time, and wait for my answer each time; then say whether it is right and why. Use the course\u2019s numbers, symbols and units, and do not go beyond the text unless I ask.';

/** The prompt for a concept (or a check or quiz with their own rules): rules, where the learner is, the course text, then room for the learner. */
export function conceptPrompt(context: ConceptContext, rules = CONCEPT_RULES, ending = 'My question: '): string {
  return [
    rules,
    '',
    context.step ? `I am in ${context.step}${context.title ? ` · ${context.title}` : ''}.` : '',
    context.background ? `My background: ${context.background}.` : '',
    `Concept: ${context.concept}`,
    ...(context.text ? ['', 'What the course says:', clip(context.text, MAX_CONCEPT)] : []),
    ...(context.around ? ['', 'Around it in the step:', clip(context.around, MAX_AROUND)] : []),
    '',
    ending,
  ].filter((line, i, all) => line !== '' || all[i - 1] !== '').join('\n');
}

export const conceptLink = (context: ConceptContext, rules?: string, ending?: string) => `https://chatgpt.com/?q=${encodeURIComponent(conceptPrompt(context, rules, ending))}`;

/* ---- Prepared for an OpenAI-compatible course tutor (not switched on) ---- */

export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };
export type ProviderSettings = { baseURL: string; model: string; apiKey: string };

/** KI:connect's documented OpenAI-compatible endpoint; the model ID is set when a course key exists. */
export const KICONNECT_BASE_URL = 'https://chat.kiconnect.nrw/api/v1';

/** Request for POST {baseURL}/chat/completions: the step context goes into the system message. */
export function chatRequest(settings: ProviderSettings, context: TutorContext, history: ChatMessage[]): { url: string; init: RequestInit } {
  const system = `${context.rules ?? TUTOR_RULES}\n\n${context.step} · ${context.title} (${context.stage})\nQuestion: ${context.question}\n\nTask:\n${context.task}`;
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
