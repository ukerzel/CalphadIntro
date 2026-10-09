/** Only original narration and five named course outputs may be published. */
import {readFileSync,writeFileSync,mkdirSync,readdirSync,existsSync,statSync} from 'node:fs';
import {resolve,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import katex from 'katex';
const repo=fileURLToPath(new URL('../../',import.meta.url));
const sheetFigures=['twophase_tangent','twophase_lens','twophase_regular'].map(name=>`course/primer_day2/figures/${name}.png`);
const day3Data=['course/self_study/generated/day3.json'];
const prework=['course/self_study/generated/day3_prework.json'];
const lpPrimer=['course/self_study/generated/lp_primer.json'];
const moduleAssets={start:prework,binary:[...prework,'course/primer_day2/figures/d3_tangent.png'],'from-materials':[...sheetFigures,...prework],'from-or':prework,'or-prices':prework,'lp-primer':lpPrimer,'menu':day3Data,'price-line':day3Data,'gap-curve':day3Data,'column-generation':day3Data,'bounds':day3Data,'local-global':day3Data,'branch-and-bound':day3Data,'two-questions':day3Data,'three-components':['course/self_study/generated/day3_ternary.json'],cuni:['course/materials/cuni/phase_diagram.png','course/materials/cuni/energy_magnetism.png','course/materials/cuni/results.json','course/self_study/generated/cuni_grid.json'],ninb:['course/materials/ninb/phase_diagram.png','course/materials/ninb/results.json','course/self_study/generated/ninb_grid.json','course/self_study/generated/mu_structure.json'],twophase:['course/self_study/generated/two_phase.json','course/self_study/generated/from_scratch.json',...prework],boundary:['course/self_study/generated/boundary_views.json']};
export const assetPaths=[...new Set(Object.values(moduleAssets).flat())];
const ids=['start','unary','binary','twophase','boundary','cuni','ninb','from-materials','from-or','or-prices','lp-primer','menu','price-line','gap-curve','column-generation','bounds','local-global','branch-and-bound','two-questions','three-components'];
const publicAsset=path=>'/learning/'+path.replace('course/','');
const validLink=href=>typeof href==='string' && (ids.map(id=>'#'+id).includes(href)||assetPaths.map(publicAsset).includes(href)||/^https:\/\/[^\s]+$/.test(href));
function exactKeys(value,required,optional=[]){
 if(!value||typeof value!=='object'||Array.isArray(value)||required.some(k=>!(k in value))||Object.keys(value).some(k=>![...required,...optional].includes(k)))throw Error('Invalid content fields');
}
function string(value){if(typeof value!=='string'||!value.trim())throw Error('Empty content text');}
/** Inline term notes: {{id|shown text}} with a defined id; no other braces or pipes. */
const token=/\{\{([a-z][a-z_]*)\|([^{}|]+)\}\}/g;
/** Formulas: $TeX$ spans, parsed by KaTeX at sync time so a broken formula fails the build. */
const math=/\$([^$\n]+)\$/g;
export function checkTeX(tex){katex.renderToString(tex,{throwOnError:true,strict:'error'});}
/** Cross-references: [[step|text]], [[step#stage|text]], [[step/lab/view|text]], [[glossary#row|text]] or [[card#id|text]]; stage, view and row names are checked by the site tests, card ids here. */
const xref=/\[\[([a-z][a-z0-9#/-]*)\|([^\[\]|$]+)\]\]/g;
const xrefTarget={test:target=>/^(?:glossary|card)#[a-z0-9-]+$/.test(target)||(()=>{const m=/^([a-z][a-z0-9-]*?)(?:#[a-z0-9-]+|\/lab(?:\/[a-z][a-z-]*)?)?$/.exec(target);return !!m&&ids.includes(m[1]);})()};
function rich(value,terms){string(value);for(const [,tex] of value.matchAll(math))checkTeX(tex);const prose=value.replace(math,'');for(const [,target] of prose.matchAll(xref))if(!xrefTarget.test(target))throw Error('Malformed cross-reference: '+target);const rest=prose.replace(xref,'');for(const [,id] of rest.matchAll(token))if(!terms.has(id))throw Error('Unknown term: '+id);if(/[{}|$]|\[\[|\]\]/.test(rest.replace(token,'')))throw Error('Malformed term, cross-reference or formula token');}
export function validateContent(content){
 exactKeys(content,['schema_version','modules'],['terms']);
 const terms=new Set();
 for(const term of content.terms??[]){exactKeys(term,['id','symbol','kind','meaning'],['elsewhere']);if(!/^[a-z][a-z_]*$/.test(term.id)||terms.has(term.id))throw Error('Invalid/duplicate term id');if(!['symbol','phase'].includes(term.kind))throw Error('Invalid term kind');[term.symbol,term.meaning].forEach(string);if('elsewhere' in term)string(term.elsewhere);terms.add(term.id);}
 if(content.schema_version!==1||!Array.isArray(content.modules)||!content.modules.length)throw Error('Unsupported learning content');
 const seen=new Set();
 function block(b,nested=false){
  if(b.type==='paragraph'){
   exactKeys(b,['type','text'],['links','image']);rich(b.text,terms);
   if(b.links){if(!Array.isArray(b.links))throw Error('Invalid links');for(const link of b.links){exactKeys(link,['label','href']);string(link.label);if(!validLink(link.href))throw Error('Invalid learning link');}}
   if(b.image){exactKeys(b.image,['src','alt']);string(b.image.alt);if(!assetPaths.filter(p=>p.endsWith('.png')).map(publicAsset).includes(b.image.src))throw Error('Unapproved image');}
  }else if(b.type==='list'){exactKeys(b,['type','items']);if(!Array.isArray(b.items)||!b.items.length)throw Error('Empty list');b.items.forEach(item=>rich(item,terms));
  }else if(b.type==='table'){exactKeys(b,['type','headers','rows']);if(!Array.isArray(b.headers)||!b.headers.length||!Array.isArray(b.rows)||!b.rows.length)throw Error('Empty table');b.headers.forEach(string);for(const row of b.rows){if(!Array.isArray(row)||row.length!==b.headers.length)throw Error('Invalid table row');row.forEach(cell=>rich(cell,terms));}
  }else if(b.type==='reveal'&&!nested){exactKeys(b,['type','label','blocks']);string(b.label);if(!Array.isArray(b.blocks)||!b.blocks.length)throw Error('Empty reveal');b.blocks.forEach(child=>block(child,true));
  }else throw Error('Unknown or nested block');
 }
 for(const mod of content.modules){
  exactKeys(mod,['id','title','sources','blocks','next']);
  if(!ids.includes(mod.id)||seen.has(mod.id))throw Error('Unknown/duplicate module');seen.add(mod.id);string(mod.title);
  if(!Array.isArray(mod.sources)||!mod.sources.length)throw Error('Missing sources');
  for(const source of mod.sources){if(!/^course\/[\w/.-]+\.md$/.test(source)||source.includes('..')||!existsSync(resolve(repo,source)))throw Error('Missing/invalid canonical source');}
  if(!Array.isArray(mod.blocks)||!mod.blocks.length)throw Error('Missing blocks');mod.blocks.forEach(b=>block(b));
 }
 if(content.modules[0].id!=='start')throw Error('Opening must be first');
 for(const mod of content.modules)if(mod.next!==null&&!seen.has(mod.next))throw Error('Unavailable next module');
 for(const mod of content.modules)for(const b of mod.blocks){const blocks=b.type==='reveal'?b.blocks:[b];for(const item of blocks)for(const link of item.links??[])if(link.href.startsWith('#')&&!seen.has(link.href.slice(1)))throw Error('Unavailable local link');}
 return content;
}
/** Side cards: one question, one claim, at most about 120 words, one level of card-to-card links. */
/** Card pages are step numbers, plus LP for the optional linear-programming primer. */
export const cardPages=[...Array.from({length:19},(_,i)=>String(i).padStart(2,'0')),'LP'];
const cardLinks=text=>[...text.replace(math,'').matchAll(xref)].map(m=>m[1]).filter(t=>t.startsWith('card#')).map(t=>t.slice(5));
const words=text=>text.replace(math,'X').replace(xref,'$2').split(/\s+/).filter(Boolean).length;
export function validateCards(cards,content){
 exactKeys(cards,['schema_version','closing','cards']);
 if(cards.schema_version!==1||!Array.isArray(cards.cards)||!cards.cards.length)throw Error('Unsupported cards');
 string(cards.closing);
 const terms=new Set((content.terms??[]).map(t=>t.id)),ids=new Set(),links=new Map();
 for(const card of cards.cards){
  exactKeys(card,['id','deck','kind','title','core','pages','symbols','blocks']);
  if(!/^[a-z][a-z0-9-]*$/.test(card.id)||ids.has(card.id))throw Error('Invalid/duplicate card id');ids.add(card.id);
  if(!['M','O','both'].includes(card.deck))throw Error('Invalid card deck');
  if(!['term','hang-on','maths','thermo'].includes(card.kind))throw Error('Invalid card kind');
  string(card.title);if(!card.title.trim().endsWith('?'))throw Error('A card title is the learner\'s question: '+card.id);
  if(typeof card.core!=='boolean')throw Error('Invalid card core flag');
  if(!Array.isArray(card.pages)||!card.pages.length||card.pages.some(p=>!cardPages.includes(p)))throw Error('Unknown card page: '+card.id);
  if(!Array.isArray(card.symbols))throw Error('Invalid card symbols');card.symbols.forEach(string);
  if(!Array.isArray(card.blocks)||!card.blocks.length)throw Error('Empty card');
  let count=0;const texts=[];
  for(const b of card.blocks){
   if(b.type==='paragraph'){exactKeys(b,['type','text']);texts.push(b.text);if(!b.text.startsWith('Where you met it: '))count+=words(b.text);}
   else if(b.type==='list'){exactKeys(b,['type','items']);if(!Array.isArray(b.items)||!b.items.length)throw Error('Empty card list');texts.push(...b.items);count+=b.items.reduce((n,i)=>n+words(i),0);}
   else throw Error('Cards hold paragraphs and lists only');
  }
  texts.forEach(t=>rich(t,terms));
  if(count>130)throw Error(`Card too long (${count} words): `+card.id);
  links.set(card.id,texts.flatMap(cardLinks));
 }
 for(const [id,targets] of links)for(const target of targets){
  if(!ids.has(target))throw Error('Unknown card link: '+target);
  if(target===id||links.get(target).length)throw Error('Cards link at most one level deep: '+id+' → '+target);
 }
 return cards;
}
export function syncContent({check=false,destination=resolve(repo,'site/public/learning')}={}){
 const input='course/self_study/lessons.json',cardInput='course/self_study/cards.json';
 const content=validateContent(JSON.parse(readFileSync(resolve(repo,input),'utf8')));
 const cards=validateCards(JSON.parse(readFileSync(resolve(repo,cardInput),'utf8')),content);
 const cardIds=new Set(cards.cards.map(c=>c.id));
 for(const target of JSON.stringify(content.modules).matchAll(/\[\[card#([a-z0-9-]+)\|/g))if(!cardIds.has(target[1]))throw Error('Unknown card link: '+target[1]);
 const assets=[...new Set(content.modules.flatMap(m=>moduleAssets[m.id]??[]))];
 const entries=[{canonical:input,public:'lessons.json'},{canonical:cardInput,public:'cards.json'},...assets.map(p=>({canonical:p,public:p.replace('course/','')}))];
 const receipt={schema_version:1,files:entries.map(entry=>({...entry,sha256:createHash('sha256').update(readFileSync(resolve(repo,entry.canonical))).digest('hex')}))};
 const expected=new Set(['content_receipt.json',...entries.map(e=>e.public)]);
 function inventory(folder){if(!existsSync(folder))return [];return readdirSync(folder).flatMap(name=>{const path=resolve(folder,name);return statSync(path).isDirectory()?inventory(path):[relative(destination,path)];});}
 for(const path of inventory(destination))if(!expected.has(path))throw Error('Unallowlisted public learning file: '+path);
 for(const entry of entries){const bytes=readFileSync(resolve(repo,entry.canonical)),target=resolve(destination,entry.public);if(check){if(!existsSync(target)||!readFileSync(target).equals(bytes))throw Error('Stale learning copy: '+entry.public);}else{mkdirSync(dirname(target),{recursive:true});writeFileSync(target,bytes);}}
 const bytes=JSON.stringify(receipt,null,2)+'\n',target=resolve(destination,'content_receipt.json');
 if(check){if(!existsSync(target)||readFileSync(target,'utf8')!==bytes)throw Error('Stale learning receipt');}else writeFileSync(target,bytes);
 return receipt;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){syncContent({check:process.argv.includes('--check')});console.log('Learning content/allowlist '+(process.argv.includes('--check')?'fresh':'synced'));}
