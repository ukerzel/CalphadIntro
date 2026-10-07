/** Actual React server markup. Browser layout, focus and events remain separate. */
import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createServer} from 'vite';
import react from '@vitejs/plugin-react';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
let server;
const root=fileURLToPath(new URL('../',import.meta.url));
const read=(name)=>JSON.parse(readFileSync(new URL(`../public/data/${name}.json`,import.meta.url)));
const bundle={manifest:read('manifest'),receipt:read('build_receipt'),unary:read('unary'),binary:read('binary'),boundary:read('boundary')};
before(async()=>{server=await createServer({root,configFile:false,plugins:[react()],resolve:{alias:{'@':root}},server:{middlewareMode:true},appType:'custom'});});
after(async()=>{await server?.close();});
async function markup(name,index){const module=await server.ssrLoadModule(`/components/${name}-view.tsx`);return renderToStaticMarkup(createElement(module.default,{bundle,index,onChange:()=>{}}));}
test('actual unary slider thumb names selected kelvin and readout explains equality',async()=>{
 const html=await markup('unary',100);
 assert.match(html,/role="slider"[^>]*aria-valuetext="1000 kelvin"|aria-valuetext="1000 kelvin"[^>]*role="slider"/);
 assert.match(html,/aria-labelledby="temperature-label"/);
 assert.match(html,/Equal energies; fractions undetermined/);
 assert.match(html,/−?9,000|-9,000/);
});
test('binary markup preserves ALPHA restriction and endpoint policy',async()=>{
 const html=await markup('binary',49);
 assert.match(html,/one ideal solution phase: ALPHA/);assert.match(html,/pure ends are left out because μ is undefined/);
 assert.match(html,/12,000/);assert.match(html,/aria-valuetext="0.50 B atom mole fraction"/);
});
test('boundary markup keeps initial/final counts, residual basis and distinct ensembles',async()=>{
 const html=await markup('boundary',0);
 for(const text of ['Fixed total A/B','Reservoir exchange','Residual','Final bulk','Final boundaries','7,350','850','Closed total Gibbs energy','Open grand potential','J\/mol all occupied cell sites','J\/mol boundary sites'])assert.match(html,new RegExp(text));
 assert.match(html,/9.094947e-13/);assert.match(html,/20 nm² per boundary/);
});
test('actual default companion renders the landing route without a graph or numerical data',async()=>{
 const module=await server.ssrLoadModule('/components/companion.tsx');
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const html=renderToStaticMarkup(createElement(module.default));
 assert.match(html,/<h1 tabindex="-1">Equilibrium is the lowest Gibbs energy/);
 for(const lesson of lessons)assert.ok(html.includes(lesson.title),lesson.id);
 assert.doesNotMatch(html,/data-plot|role="slider"|Loading checked teaching data|Data unavailable/);
 assert.doesNotMatch(html,/<details[^>]* open/);
});
test('start refresher keeps definitions and a closed self-check',async()=>{
 const {lesson}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const html=renderToStaticMarkup(createElement(Page,{lesson:lesson('start')}));
 assert.match(html,/<h1 tabindex="-1">Start here/);
 assert.match(html,/Why CALPHAD/);assert.match(html,/Internal energy/);
 assert.match(html,/<details><summary>Self-check/);
 assert.doesNotMatch(html,/<details[^>]* open|data-plot|role="slider"|type="range"/);
 assert.match(html,/F is minimal/);
 assert.match(html,/aria-pressed="true">Database<\/button>/);
});
const body=(html)=>html.slice(html.indexOf('class="lesson-body"'));
const escape=(text)=>text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
test('lab dock follows the attempt, its hints and the worked answer',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 for(const lesson of lessons.filter(item=>item.id!=='start')){
  const html=body(renderToStaticMarkup(createElement(Page,{lesson,dock:createElement('div',{id:'dock-probe'})})));
  assert.equal(html.split('dock-probe').length,2,lesson.id);
  for(const text of ['>Problem</h2>','>Attempt</h2>','Hint 1','Worked answer'])assert.ok(html.indexOf(text)>=0&&html.indexOf(text)<html.indexOf('dock-probe'),`${lesson.id}: ${text}`);
 }
});
test('lesson screen mounts lab content only when the lab is explicitly open',async()=>{
 const {LessonScreen}=await server.ssrLoadModule('/components/companion.tsx');
 const {default:UnaryView}=await server.ssrLoadModule('/components/unary-view.tsx');
 const props={id:'unary',heading:{current:null},dock:{current:null},onOpen(){},onClose(){},onLearn(){},content:createElement(UnaryView,{bundle,index:100,onChange(){}})};
 const closed=renderToStaticMarkup(createElement(LessonScreen,{...props,lab:false}));
 assert.match(closed,/Explore the calculation/);assert.doesNotMatch(closed,/role="slider"|data-plot/);
 const open=renderToStaticMarkup(createElement(LessonScreen,{...props,lab:true}));
 assert.match(open,/role="slider"/);assert.match(open,/data-plot/);assert.match(open,/Return to the activity/);
 assert.ok(open.indexOf('Worked answer')<open.indexOf('data-plot'));
});
test('multi-line narration keeps every line when commands are split from prose',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 let checked=0;
 for(const lesson of lessons){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  for(const block of lesson.blocks.flatMap(b=>b.type==='reveal'?b.blocks:[b]))if(block.type==='paragraph'&&block.text.includes('\n'))for(const line of block.text.split('\n')){assert.ok(html.includes(escape(line)),line);checked++;}
  if(['cuni','ninb'].includes(lesson.id))assert.match(html,/<pre class="code"[^>]*><code>mkdir -p/);
 }
 assert.ok(checked>20);
});
test('learner-facing markup stays free of audit jargon and worksheet codes',async()=>{
 const jargon=/exported|pinned|author (output|calculation|run)|\bI1\b|\bW\d|\bD\d|certif|ensemble/i;
 const {default:Companion,LessonScreen}=await server.ssrLoadModule('/components/companion.tsx');
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const pages=[renderToStaticMarkup(createElement(Companion))];
 for(const lesson of lessons)pages.push(renderToStaticMarkup(createElement(LessonScreen,{id:lesson.id,lab:false,heading:{current:null},dock:{current:null},onOpen(){},onClose(){},onLearn(){},content:null})).replace(/<footer class="lesson-sources">[\s\S]*?<\/footer>/,''));
 for(const name of ['unary','binary','boundary'])pages.push(await markup(name,0));
 for(const html of pages){const hit=jargon.exec(html.replace(/<[^>]+>/g,' '));assert.equal(hit,null,hit&&html.replace(/<[^>]+>/g,' ').slice(Math.max(0,hit.index-60),hit.index+60));}
});
test('formulas render with KaTeX markup and MathML',async()=>{
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const lesson={id:'unary',title:'Probe',sources:['course/primer/worksheet.md'],next:null,blocks:[{type:'paragraph',text:'Problem · Compare $g = h - Ts$ with {{mu_chem|μ_A}}.'}]};
 const html=renderToStaticMarkup(createElement(Page,{lesson}));
 assert.match(html,/<span class="math"><span class="katex">/);assert.match(html,/<math[^>]*>/);assert.match(html,/data-term="mu_chem"/);
 const {default:Eq}=await server.ssrLoadModule('/components/equation.tsx').then(m=>({default:m.Eq}));
 assert.match(renderToStaticMarkup(createElement(Eq,{label:'x',tex:'\\mu_A = g - x g\''})),/katex-display/);
});
test('μ and δ are always marked where they name phases or the boundary preference',async()=>{
 const {lesson}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 for(const id of ['boundary','ninb']){
  const html=renderToStaticMarkup(createElement(Page,{lesson:lesson(id)}));
  assert.match(html,/<aside class="heads-up" role="note">/,id);
  // Narration prose with $TeX$ formulas, {{term}} notes and the heads-up removed must not contain a bare symbol.
  const strings=[];const walk=v=>{if(typeof v==='string')strings.push(v);else if(v&&typeof v==='object')Object.values(v).forEach(walk);};
  walk(lesson(id).blocks.filter(b=>!(b.type==='paragraph'&&b.text.startsWith('Heads-up: '))).map(b=>b.type==='reveal'?b.blocks:b));
  const body=strings.join(' ').replace(/\$[^$\n]+\$/g,' ').replace(/\{\{[a-z_]+\|[^}]+\}\}/g,' ');
  const bare=id==='ninb'?/[μδ]/:/δ/;
  const hit=bare.exec(body);assert.equal(hit,null,hit&&`${id}: …${body.slice(Math.max(0,hit.index-60),hit.index+40)}…`);
 }
 const start=renderToStaticMarkup(createElement(Page,{lesson:lesson('start')}));
 assert.match(start,/One symbol|Meanings in this course/);assert.match(start,/data-term="mu_phase"/);
});
test('part D shows each from-scratch method next to pycalphad',async()=>{
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/from_scratch.json',import.meta.url)));
 const {ScratchLab}=await server.ssrLoadModule('/components/scratch-view.tsx');
 for(const [method,pattern] of [['brute',/Trial solid composition/],['grid',/Grid spacing/],['newton',/Newton step/],['walk',/Walk through temperature/]]){
  const html=renderToStaticMarkup(createElement(ScratchLab,{data,initialMethod:method}));
  assert.match(html,pattern);assert.match(html,/From scratch \(numpy\/SciPy\)[\s\S]*pycalphad/);
  assert.match(html,/0\.440517/);assert.match(html,/data-plot/);
 }
 const grid=renderToStaticMarkup(createElement(ScratchLab,{data,initialMethod:'grid'}));
 assert.match(grid,/one phase/);
});
test('two-phase lab shows the generated states and the gap',async()=>{
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/two_phase.json',import.meta.url)));
 const {TwoPhaseLab}=await server.ssrLoadModule('/components/twophase-view.tsx');
 const html=renderToStaticMarkup(createElement(TwoPhaseLab,{data}));
 assert.match(html,/aria-valuetext="0.50 overall B fraction"/);assert.match(html,/Two phases/);
 assert.match(html,/−10,762\.73/);assert.match(html,/ALPHA: x = 0\.1910, amount 0\.5000/);
 assert.match(html,/data-plot/);
 assert.match(html,/∝ f_β/);assert.match(html,/∝ f_α/);
 const outside=renderToStaticMarkup(createElement(TwoPhaseLab,{data,initialIndex:4}));
 assert.match(outside,/z outside the tie line: no split/);assert.doesNotMatch(outside,/∝ f_β/);
 const partB=renderToStaticMarkup(createElement(TwoPhaseLab,{data,initialPart:'b'}));
 assert.match(partB,/Mixing part<\/button>/);
 const partC=renderToStaticMarkup(createElement(TwoPhaseLab,{data,initialPart:'c'}));
 assert.match(partC,/Liquid and solid coexist/);assert.match(partC,/Melting lens: liquidus and solidus/);assert.match(partB,/Full g\(x\)<\/button>/);
});
test('step 05 teaches reading the diagram before its attempt',async()=>{
 const {lesson}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const html=renderToStaticMarkup(createElement(Page,{lesson:lesson('cuni')}));
 const diagram=html.indexOf('/learning/materials/cuni/phase_diagram.png');
 assert.ok(diagram>0&&diagram<html.indexOf('>Attempt</h2>'));
 assert.ok(html.indexOf('>Reading the diagram</h2>')<html.indexOf('>Attempt</h2>'));
 assert.match(html,/PARAMETER G\(DEMO,A;0\)/);assert.match(html,/Invented example line, not copied from any database/);
});
test('site boxes count atoms per formula unit for δ and μ',async()=>{
 const {SiteBoxes}=await server.ssrLoadModule('/components/material-explorer.tsx');
 const delta=renderToStaticMarkup(createElement(SiteBoxes,{name:'δ phase',sizes:[1,1,2],presets:[['NbNi₃',['Nb','Ni','Ni']]]}));
 assert.match(delta,/NB : NI : NI/);assert.match(delta,/1 \/ 4 = 0\.250/);assert.match(delta,/sublattice 3 · 2 sites/);
 const mu=renderToStaticMarkup(createElement(SiteBoxes,{name:'μ phase',sizes:[2,2,2,6,1],presets:[['Nb₇Ni₆',['Nb','Nb','Nb','Ni','Nb']]]}));
 assert.match(mu,/7 \/ 13 = 0\.538/);
});
test('energy ladder starts at the Try-it state and shows G − F = pV',async()=>{
 const {default:Ladder}=await server.ssrLoadModule('/components/energy-ladder.tsx');
 const html=renderToStaticMarkup(createElement(Ladder));
 assert.match(html,/U 1,498, H 1,500, F 298, G 300 joules/);assert.match(html,/G − F \(equals pV\)/);assert.match(html,/type="range"/);
});
test('step 04 tangent picture and hand iteration show the generated values',async()=>{
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/boundary_views.json',import.meta.url)));
 const {TangentPicture,HandIteration}=await server.ssrLoadModule('/components/boundary-views.tsx');
 const t=renderToStaticMarkup(createElement(TangentPicture,{data}));
 assert.match(t,/θ = 0\.169/);assert.match(t,/delta -5000 joule per mole of boundary sites/);assert.match(t,/data-plot/);
 const h=renderToStaticMarkup(createElement(HandIteration,{data}));
 assert.match(h,/0\.16856026/);assert.match(h,/Next round/);
});
test('clickable phase maps label regions and read saved cells',async()=>{
 const {PhaseMapView}=await server.ssrLoadModule('/components/phase-map.tsx');
 const cuni=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/cuni_grid.json',import.meta.url)));
 const html=renderToStaticMarkup(createElement(PhaseMapView,{data:cuni,modeLabels:{magnetic_on:'Magnetic on',magnetic_off:'Magnetic off'}}));
 assert.match(html,/>FCC \+ FCC</);assert.match(html,/>L</);assert.match(html,/highest two-FCC row 640 K/);assert.match(html,/highest two-FCC row 620 K/);
 const ninb=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/ninb_grid.json',import.meta.url)));
 const n=renderToStaticMarkup(createElement(PhaseMapView,{data:ninb}));
 assert.match(n,/mol formula units/);assert.match(n,/data-plot/);
});
test('cross-references render as previews; glossary rows carry anchors; closed labs list their views',async()=>{
 const {Rich,default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const html=renderToStaticMarkup(createElement(Rich,{text:'see [[twophase#approach|the approach]] and [[glossary#grand-potential|grand potential]], not [[twophase#nowhere|this]]'}));
 assert.match(html,/data-xref="twophase#approach"/);assert.match(html,/cross-reference: Step 03 · Approach/);assert.match(html,/Glossary · Grand potential/);
 assert.doesNotMatch(html,/data-xref="twophase#nowhere"/);assert.match(html,/not this/);
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const start=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='start')}));
 assert.match(start,/<tr id="start-g-grand-potential">/);
 const reference=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='start'),variant:'reference'}));
 assert.doesNotMatch(reference,/id="start-g-/);
 const C=await server.ssrLoadModule('/components/companion.tsx');
 const closed=renderToStaticMarkup(createElement(C.LessonScreen,{id:'twophase',lab:false,heading:{current:null},dock:{current:null},onOpen(){},onClose(){},onLearn(){},content:null}));
 assert.match(closed,/In the lab:/);assert.match(closed,/Part C · melting and the lens/);
});
test('inline figures sit where the text discusses them and draw exported values',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const page=id=>renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id===id)}));
 const section=(html,key)=>html.slice(html.indexOf(`id="${key}"`),html.indexOf('</section>',html.indexOf(`id="${key}"`)));
 assert.match(section(page('binary'),'binary-tangent-and-chemical-potentials'),/Where the tangent meets the edges/);
 assert.doesNotMatch(section(page('twophase'),'twophase-approach'),/Loading the figure/);assert.match(section(page('twophase'),'twophase-attempt'),/Worked answer[\s\S]*Loading the figure/);assert.match(section(page('twophase'),'twophase-reading-a-phase-diagram'),/Loading the figure/);
 assert.match(section(page('boundary'),'boundary-where-the-odds-formula-comes-from'),/Loading the figure/);
 assert.match(section(page('ninb'),'ninb-problem'),/δ phase \(DELTA\)/);
 const F=await server.ssrLoadModule('/components/lesson-figures.tsx');
 const two=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/two_phase.json',import.meta.url)));
 const views=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/boundary_views.json',import.meta.url)));
 assert.match(renderToStaticMarkup(createElement(F.CommonTangentFigure,{given:two})),/ALPHA, BETA and their common tangent[\s\S]*∝ f_β/);
 assert.match(renderToStaticMarkup(createElement(F.PhaseDiagramsFigure,{given:two})),/Miscibility gap \(part B\)[\s\S]*Melting lens \(part C\)/);
 assert.match(renderToStaticMarkup(createElement(F.BoundaryTangentFigure,{given:views})),/x<sub>b<\/sub> = 0.50/);
});
test('the lab card links the step notebooks in Colab, after the attempt',async()=>{
 const C=await server.ssrLoadModule('/components/companion.tsx');
 const props={heading:{current:null},dock:{current:null},onOpen(){},onClose(){},onLearn(){},content:null};
 const closed=renderToStaticMarkup(createElement(C.LessonScreen,{...props,id:'binary',lab:false}));
 const at=closed.indexOf('Run it yourself'),attempt=closed.indexOf('>Attempt</h2>');
 assert.ok(at>attempt&&attempt>0);const {colabURL}=await server.ssrLoadModule('/lib/lesson-meta.ts');assert.ok(closed.includes(`class="colab-button" href="${colabURL('f3_binary_mixing_potentials')}"`));
 assert.equal((closed.match(/class="colab-button"/g)||[]).length,1);
 const open=renderToStaticMarkup(createElement(C.LessonScreen,{...props,id:'cuni',lab:true}));
 assert.equal((open.match(/class="colab-button"/g)||[]).length,3);assert.match(open,/task01_cuni_equilibria\.ipynb/);
});
test('Ask ChatGPT links carry the task and tutor rules, never hints or answers',async()=>{
 const {lessons,plainText}=await server.ssrLoadModule('/lib/learning.ts');const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 let seen=0;
 for(const lesson of lessons){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  const links=[...html.matchAll(/href="https:\/\/chatgpt\.com\/\?q=([^"]+)"/g)];
  if(!html.includes('help-ladder')){assert.equal(links.length,0,lesson.id);continue;}
  assert.ok(links.length>=1,lesson.id);
  const reveals=lesson.blocks.filter(b=>b.type==='reveal').flatMap(b=>b.blocks).filter(b=>b.type==='paragraph').map(b=>plainText(b.text).slice(0,70)).filter(t=>t.length>=40);
  for(const [url,q] of links){
   assert.ok(url.length<8000,lesson.id);
   const prompt=decodeURIComponent(q.replace(/&amp;/g,'&'));
   assert.match(prompt,/do not give the full worked answer/);assert.match(prompt,/My attempt so far:/);assert.match(prompt,new RegExp(`Step \\d\\d`));
   for(const r of reveals)assert.ok(!prompt.includes(r),`${lesson.id}: prompt contains reveal text: ${r}`);
   seen++;
  }
 }
 assert.ok(seen>=6);
});
test('prepared course tutor builds an OpenAI-compatible request and reads the reply',async()=>{
 const T=await server.ssrLoadModule('/lib/tutor.ts');const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const context=T.tutorContext(lessons.find(l=>l.id==='binary'),'attempt');
 const history=Array.from({length:20},(_, i)=>({role:i%2?'assistant':'user',content:`m${i}`}));
 const {url,init}=T.chatRequest({baseURL:T.KICONNECT_BASE_URL+'/',model:'qwen-test',apiKey:'k'},context,history);
 assert.equal(url,'https://chat.kiconnect.nrw/api/v1/chat/completions');assert.equal(init.headers.Authorization,'Bearer k');
 const body=JSON.parse(init.body);assert.equal(body.model,'qwen-test');assert.equal(body.messages[0].role,'system');assert.match(body.messages[0].content,/Step 02/);assert.equal(body.messages.length,13);
 assert.equal(T.chatReply({choices:[{message:{content:'Try the balance first.'}}]}),'Try the balance first.');assert.equal(T.chatReply({error:'x'}),null);
});
test('μ-phase sketch draws the exported cell and links sublattices to crystal sites',async()=>{
 const {MuStructureView}=await server.ssrLoadModule('/components/mu-structure.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/mu_structure.json',import.meta.url)));
 const html=renderToStaticMarkup(createElement(MuStructureView,{data,occ:['Nb','Nb','Nb','Ni','Nb'],selected:null}));
 assert.equal((html.match(/<circle/g)||[]).length,156);assert.match(html,/Drawn here: 84 Nb, 72 Ni/);assert.match(html,/6-site sublattice/);
 const mixed=renderToStaticMarkup(createElement(MuStructureView,{data,occ:['Ni','Nb','Nb','Ni','Nb'],selected:4}));
 assert.equal((mixed.match(/occ-unknown/g)||[]).length,72);assert.equal((mixed.match(/mu-atom occ-Nb is-selected/g)||[]).length,12);
});
test('guided activities render closed help without mounting their explorers',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 for(const lesson of lessons.filter(item=>item.id!=='start')){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  const main=body(html);
  assert.ok(main.indexOf('>Problem</h2>')>=0&&main.indexOf('>Problem</h2>')<main.indexOf('Hint 1'),lesson.id);
  assert.ok(main.indexOf('>Approach</h2>')>=0&&main.indexOf('>Approach</h2>')<main.indexOf('Worked answer'),lesson.id);
  assert.match(html,/<details><summary>Hint 1/);assert.match(html,/<details><summary>Worked answer/);
  assert.doesNotMatch(html,/<details[^>]* open|role="slider"|data-plot/);
 }
});
