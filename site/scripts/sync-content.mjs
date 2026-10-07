/** Only original narration and five named course outputs may be published. */
import {readFileSync,writeFileSync,mkdirSync,readdirSync,existsSync,statSync} from 'node:fs';
import {resolve,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import katex from 'katex';
const repo=fileURLToPath(new URL('../../',import.meta.url));
const moduleAssets={cuni:['course/materials/cuni/phase_diagram.png','course/materials/cuni/energy_magnetism.png','course/materials/cuni/results.json','course/self_study/generated/cuni_grid.json'],ninb:['course/materials/ninb/phase_diagram.png','course/materials/ninb/results.json','course/self_study/generated/ninb_grid.json','course/self_study/generated/mu_structure.json'],twophase:['course/self_study/generated/two_phase.json','course/self_study/generated/from_scratch.json'],boundary:['course/self_study/generated/boundary_views.json']};
export const assetPaths=Object.values(moduleAssets).flat();
const ids=['start','unary','binary','twophase','boundary','cuni','ninb'];
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
/** Cross-references: [[step|text]], [[step#stage|text]], [[step/lab/view|text]] or [[glossary#row|text]]; stage, view and row names are checked by the site tests. */
const xref=/\[\[([a-z][a-z0-9#/-]*)\|([^\[\]|$]+)\]\]/g;
const xrefTarget=/^(?:glossary#[a-z0-9-]+|(start|unary|binary|twophase|boundary|cuni|ninb)(?:#[a-z0-9-]+|\/lab(?:\/[a-z][a-z-]*)?)?)$/;
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
export function syncContent({check=false,destination=resolve(repo,'site/public/learning')}={}){
 const input='course/self_study/lessons.json';
 const content=validateContent(JSON.parse(readFileSync(resolve(repo,input),'utf8')));
 const assets=content.modules.flatMap(m=>moduleAssets[m.id]??[]);
 const entries=[{canonical:input,public:'lessons.json'},...assets.map(p=>({canonical:p,public:p.replace('course/','')}))];
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
