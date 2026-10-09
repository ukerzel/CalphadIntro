/** Finite original narration; no evaluation of scientific expressions. */
import content from '../public/learning/lessons.json';
export type LearningID = 'start'|'unary'|'binary'|'twophase'|'boundary'|'cuni'|'ninb'|'from-materials'|'from-or'|'or-prices'|'lp-primer'|'menu'|'price-line'|'gap-curve'|'column-generation'|'bounds'|'local-global'|'branch-and-bound'|'two-questions'|'three-components';
export type Link = {label:string;href:string};
export type PlainBlock = {type:'paragraph';text:string;links?:Link[];image?:{src:string;alt:string}} | {type:'list';items:string[]} | {type:'table';headers:string[];rows:string[][]};
export type Block = PlainBlock | {type:'reveal';label:string;blocks:PlainBlock[]};
export type Lesson = {id:LearningID;title:string;sources:string[];blocks:Block[];next:LearningID|null};
export type Term = {id:string;symbol:string;kind:'symbol'|'phase';meaning:string;elsewhere?:string};
export const lessons = content.modules as Lesson[];
export const terms: Record<string,Term> = Object.fromEntries(((content as {terms?:Term[]}).terms ?? []).map(term=>[term.id,term]));
export type RichPart = string | {id:string;shown:string} | {tex:string} | {ref:string;shown:string};
/** Split narration into prose, $TeX$ formulas, {{id|shown}} term notes and [[target|shown]] cross-references (validated at sync and in tests). */
export function splitTerms(text:string):RichPart[] {
 const parts:RichPart[]=[];let last=0;
 for(const match of text.matchAll(/\$([^$\n]+)\$|\{\{([a-z][a-z_]*)\|([^{}|]+)\}\}|\[\[([a-z][a-z0-9#/-]*)\|([^\[\]|$]+)\]\]/g)){
  if(match.index>last)parts.push(text.slice(last,match.index));
  parts.push(match[1]!==undefined?{tex:match[1]}:match[4]!==undefined?{ref:match[4],shown:match[5]}:{id:match[2],shown:match[3]});
  last=match.index+match[0].length;
 }
 if(last<text.length)parts.push(text.slice(last));
 return parts;
}
export const plainText=(text:string)=>splitTerms(text).map(part=>typeof part==='string'?part:'tex' in part?part.tex.replace(/\\[a-zA-Z]+\s?|[{}^_]/g,''):'ref' in part?part.shown:part.shown.replace('_','')).join('');
/** Anchor slug for glossary rows: the row's plain first cell. */
export const slug=(text:string)=>plainText(text).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
export function lesson(id:LearningID):Lesson {
 const value=lessons.find(item=>item.id===id);
 if(!value)throw Error('Unavailable learning step');
 return value;
}
