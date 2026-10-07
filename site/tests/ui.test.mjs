/** Routing, narration grouping and saved-output loading; no scientific values are computed here. */
import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {parseRoute,routeHash,recordIndex} from '../lib/route.ts';
import {fileURLToPath} from 'node:url';
import {createServer} from 'vite';
const content=JSON.parse(readFileSync(new URL('../public/learning/lessons.json',import.meta.url),'utf8'));
const asset=(path)=>readFileSync(new URL(`../public/learning/${path}`,import.meta.url));
const fetcher=(override={})=>async(url)=>{const path=url.replace('/learning/','');return path in override?new Response(override[path]):new Response(asset(path));};

let server,loadMaterial;
before(async()=>{const root=fileURLToPath(new URL('../',import.meta.url));server=await createServer({root,configFile:false,resolve:{alias:{'@':root}},server:{middlewareMode:true},appType:'custom'});({loadMaterial}=await server.ssrLoadModule('/lib/materials.ts'));});
after(async()=>{await server?.close();});

test('cross-reference routes: lesson anchors and named lab views round-trip; record IDs keep priority',()=>{
 for(const route of [{page:'lesson',id:'cuni',lab:false,anchor:'reading-the-diagram'},{page:'lesson',id:'start',lab:false,anchor:'g-lever-rule'},{page:'lesson',id:'twophase',lab:true,view:'part-b'},{page:'lesson',id:'ninb',lab:true,view:'mu-structure'}])
  assert.deepEqual(parseRoute(routeHash(route)),route);
 assert.deepEqual(parseRoute('#/boundary/lab/boundary-040'),{page:'lesson',id:'boundary',lab:true,recordId:'boundary-040'});
 assert.equal(parseRoute('#/cuni/at/Bad_Anchor').anchor,undefined);assert.equal(parseRoute('#/cuni/lab/x1').view,undefined);
});
test('every cross-reference in the narration resolves to a real step, stage, lab view or glossary row',async()=>{
 const {splitTerms}=await server.ssrLoadModule('/lib/learning.ts');const {parseTarget,describe}=await server.ssrLoadModule('/lib/xref.ts');
 const texts=[];const walk=b=>{if(b.type==='paragraph')texts.push(b.text);else if(b.type==='list')texts.push(...b.items);else if(b.type==='table')texts.push(...b.headers,...b.rows.flat());else if(b.type==='reveal'){texts.push(b.label);b.blocks.forEach(walk);}};
 content.modules.forEach(m=>m.blocks.forEach(walk));
 const refs=texts.flatMap(t=>splitTerms(t).filter(p=>typeof p==='object'&&'ref' in p));
 for(const ref of refs){const target=parseTarget(ref.ref);assert.ok(target&&describe(target),'unresolved cross-reference: '+ref.ref);}
 assert.equal(describe(parseTarget('twophase#no-such-stage')),null);assert.equal(describe(parseTarget('glossary#no-such-row')),null);assert.equal(describe(parseTarget('ninb/lab/nowhere')),null);
 return refs.length;
});
test('hash routes round-trip and accept only exact three-digit record IDs',()=>{
 for(const route of [{page:'home'},{page:'lesson',id:'start',lab:false},{page:'lesson',id:'boundary',lab:true,recordId:'boundary-040'},{page:'lesson',id:'cuni',lab:true}])
  assert.deepEqual(parseRoute(routeHash(route)),route);
 assert.deepEqual(parseRoute('#binary'),{page:'lesson',id:'binary',lab:false});
 assert.deepEqual(parseRoute('#/nowhere/lab'),{page:'home'});
 assert.equal(parseRoute('#/unary/lab/unary-1.5').recordId,undefined);
 assert.equal(recordIndex('unary-200','unary',201),200);
 for(const [id,view,count] of [['unary-201','unary',201],['binary-010','unary',201],['unary-10','unary',201],[undefined,'unary',201]])assert.equal(recordIndex(id,view,count),null);
});

test('stage grouping keeps every narration block, in order, with its label restored',async()=>{
 const {stages}=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const restore=(stage,block,i)=>i||!stage.prefix?block:{...block,text:stage.prefix+block.text};
 for(const lesson of content.modules)assert.deepEqual(stages(lesson).flatMap(stage=>stage.blocks.map((block,i)=>restore(stage,block,i))),lesson.blocks,lesson.id);
 const unary=stages(content.modules.find(m=>m.id==='unary')).map(s=>s.kind);
 assert.deepEqual(unary.slice(0,4),['problem','approach','attempt','explore']);
 assert.deepEqual(stages(content.modules[0]).map(s=>s.label),['Why CALPHAD?','Refresher','Try it','Glossary']);
});

test('two-phase data loads only with its receipt hash',async()=>{
 const {loadLearningJSON}=await server.ssrLoadModule('/lib/materials.ts');
 const path='self_study/generated/two_phase.json';
 const data=await loadLearningJSON(path,fetcher());
 assert.equal(data.part_a.states.length,99);
 const changed=JSON.parse(asset(path));changed.part_a.T_K=1001;
 await assert.rejects(loadLearningJSON(path,fetcher({[path]:JSON.stringify(changed)})),/hash mismatch/);
});
test('saved material outputs load only with the receipt hash',async()=>{
 const cuni=await loadMaterial('cuni',fetcher());
 assert.equal(cuni.equilibrium.magnetic_on.samples['600'].phases.length,2);
 const ninb=await loadMaterial('ninb',fetcher());
 assert.equal(ninb.energy_checks.delta_NB_NB_NB.atom_J_per_mol,-30500.005040464013);
 const changed=JSON.parse(asset('materials/cuni/results.json'));changed.pdens=61;
 await assert.rejects(loadMaterial('cuni',fetcher({'materials/cuni/results.json':JSON.stringify(changed)})),/hash mismatch/);
 await assert.rejects(loadMaterial('ninb',async()=>new Response('missing',{status:404})),/Missing saved output/);
});
test('every listed lab view lands somewhere: a panel id, an initial part/view, or the top of its lab',()=>{
 const src=f=>readFileSync(new URL(`../components/${f}`,import.meta.url),'utf8');
 const panels=['unary-view.tsx','binary-view.tsx','material-explorer.tsx'].map(src).join('\n'),shell=src('companion.tsx');
 const meta=readFileSync(new URL('../lib/lesson-meta.ts',import.meta.url),'utf8');
 const block=meta.slice(meta.indexOf('export const labViews'),meta.indexOf('};',meta.indexOf('export const labViews')));
 for(const line of block.split('\n').filter(l=>/^\s+[a-z]+: \[\[/.test(l))){
  const views=[...line.matchAll(/\['([a-z-]+)', '/g)].map(m=>m[1]);
  views.slice(1).forEach(view=>assert.ok(panels.includes(`id="lab-${view}"`)||shell.includes(`view === '${view}'`),`lab view ${view} has no target`));
 }
});
test('Run-it-yourself links name existing notebooks at the release the notebooks clone',async()=>{
 const {notebooks,NOTEBOOK_RELEASE,colabURL}=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const setup=readFileSync(new URL('../../notebooks/helpers.py',import.meta.url),'utf8');
 assert.match(setup,new RegExp(`RELEASE = "${NOTEBOOK_RELEASE}"`));
 for(const [id,list] of Object.entries(notebooks))for(const [file] of list){
  for(const ext of ['py','ipynb'])assert.ok(existsSync(new URL(`../../notebooks/${file}.${ext}`,import.meta.url)),`${id}: notebooks/${file}.${ext} missing`);
  assert.match(colabURL(file),new RegExp(`/blob/${NOTEBOOK_RELEASE}/notebooks/${file}\\.ipynb$`));
 }
});
