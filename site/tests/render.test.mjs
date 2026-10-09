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
 assert.match(html,/U 1,498, H 1,500, F 298, G 300 joules/);assert.match(html,/G − F \(equals pV\)/);assert.match(html,/role="slider"/);
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
 assert.equal((open.match(/class="colab-button"/g)||[]).length,4);assert.match(open,/f5b_tdb_anatomy\.ipynb/);assert.match(open,/task01_cuni_equilibria\.ipynb/);
});
test('Ask ChatGPT links carry the task and tutor rules, never hints or answers',async()=>{
 const {lessons,plainText}=await server.ssrLoadModule('/lib/learning.ts');const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 let seen=0;
 for(const lesson of lessons){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  const links=[...html.matchAll(/<a [^>]*data-ask="task"[^>]*>/g)].map(m=>/href="(https:\/\/chatgpt\.com\/\?q=([^"]+))"/.exec(m[0])).map(m=>[m[1],m[2]]);
  if(!html.includes('help-ladder')){assert.equal(links.length,0,lesson.id);continue;}
  assert.ok(links.length>=1,lesson.id);
  const reveals=lesson.blocks.filter(b=>b.type==='reveal').flatMap(b=>b.blocks).filter(b=>b.type==='paragraph').map(b=>plainText(b.text).slice(0,70)).filter(t=>t.length>=40);
  for(const [url,q] of links){
   assert.ok(url.length<8000,lesson.id);
   const prompt=decodeURIComponent(q.replace(/&amp;/g,'&'));
   assert.match(prompt,/do not give the full worked answer/);assert.match(prompt,/My attempt so far:/);assert.match(prompt,/Step \d\d · |LP primer · /);
   for(const r of reveals)assert.ok(!prompt.includes(r),`${lesson.id}: prompt contains reveal text: ${r}`);
   seen++;
  }
 }
 assert.ok(seen>=6);
});
test('Ask ChatGPT step prompts carry the tables an attempt points to, and stay a safe link length',async()=>{
 const T=await server.ssrLoadModule('/lib/tutor.ts');const {lessons}=await server.ssrLoadModule('/lib/learning.ts');const M=await server.ssrLoadModule('/lib/lesson-meta.ts');
 let checked=0;
 for(const lesson of lessons)for(const stage of M.stages(lesson)){
  const context=T.tutorContext(lesson,stage.key);assert.ok(T.chatGPTLink(context).length<=7500,`${lesson.id}/${stage.key}: link too long`);
  const own=T.taskText(stage.blocks);
  if(!/table (above|of lots|of step)|numbers above|menu of step|setup above|from the \d+ K table/i.test(own))continue;
  const data=T.dataText(lesson,stage);assert.ok(data,`${lesson.id}/${stage.key}: no data`);
  const row=data.split('\n').find(line=>(line.includes(' | ')||/numbers|setup/.test(own))&&/\d/.test(line)&&!line.endsWith(':'));
  assert.ok(row&&T.tutorPrompt(context).includes(row),`${lesson.id}/${stage.key}: prompt lacks ${row}`);
  checked++;
 }
 assert.ok(checked>=8,`only ${checked} attempts point to tables`);
});
test('pager: both entry steps lead to step 10, step 07 offers the LP primer, and step 10 goes back to either entry',async()=>{
 const {LessonScreen}=await server.ssrLoadModule('/components/companion.tsx');
 const pager=id=>{const html=renderToStaticMarkup(createElement(LessonScreen,{id,lab:false,heading:{current:null},dock:{current:null},onOpen(){},onClose(){},onLearn(){},content:null}));return html.slice(html.indexOf('class="pager"'));};
 const seven=pager('from-materials');assert.match(seven,/Optional first · LP primer/);assert.match(seven,/Next · Step 10/);
 const ten=pager('menu');assert.match(ten,/Previous · Step 07[\s\S]*Previous · Step 09/);assert.doesNotMatch(ten,/Previous · LP primer/);
 assert.match(pager('from-or'),/Previous · Step 06/);assert.match(pager('lp-primer'),/Previous · Step 07[\s\S]*Next · Step 10/);
 assert.match(pager('three-components'),/Step 18 was optional/);
});
test('a step names its lab once: the dock title is the lab heading, and view buttons use the step\'s view labels',async()=>{
 const {LabNames}=await server.ssrLoadModule('/components/lab-frame.tsx');const {Day3LineLab}=await server.ssrLoadModule('/components/day3-line-view.tsx');
 const {meta,labViews}=await server.ssrLoadModule('/lib/lesson-meta.ts');const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url)));
 const views=labViews['gap-curve'];
 const html=renderToStaticMarkup(createElement(LabNames.Provider,{value:{title:meta['gap-curve'].labTitle,views:Object.fromEntries(views.map(([k,l])=>[k,l]))}},createElement(Day3LineLab,{lens:data.lens,initialView:'gap',views:views.map(([k])=>k)})));
 assert.match(html,new RegExp(`<h2 class="lab-title">${meta['gap-curve'].labTitle}</h2>`));
 for(const [,label] of views)assert.ok(html.includes(`>${label}</button>`),label);
});
test('check, quiz and section prompts carry questions and course text, never hints or answers; the step button follows the hints',async()=>{
 const {lessons,plainText}=await server.ssrLoadModule('/lib/learning.ts');const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const count={check:0,quiz:0,section:0};
 for(const lesson of lessons){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  const isQuestionBox=(b,i)=>/^(Self-check|Check)\b/.test(b.label)&&!/answer/i.test(b.label)&&lesson.blocks[i+1]?.type==='reveal'&&/answer/i.test(lesson.blocks[i+1].label);
  const answers=lesson.blocks.filter((b,i)=>b.type==='reveal'&&(/^(Hint \d|Worked answer|Answers)\b/.test(b.label)||(/^(Self-check|Check)\b/.test(b.label)&&!isQuestionBox(b,i)))).flatMap(b=>b.blocks).flatMap(b=>b.type==='paragraph'?[b.text]:b.type==='list'?b.items:[]).map(t=>plainText(t).slice(0,60)).filter(t=>t.length>=40);
  for(const m of html.matchAll(/<a [^>]*data-ask="(check|quiz|section)"[^>]*>/g)){
   const prompt=decodeURIComponent(/href="https:\/\/chatgpt\.com\/\?q=([^"]+)"/.exec(m[0])[1].replace(/&amp;/g,'&'));count[m[1]]++;
   for(const a of answers)assert.ok(!plainText(prompt).includes(a),`${lesson.id} ${m[1]} prompt contains answer text: ${a}`);
   if(m[1]==='check')assert.match(prompt,/Do not show model answers/);
  }
  const ladder=html.indexOf('help-ladder');if(ladder>=0)assert.ok(html.indexOf('data-ask="task"',ladder)>html.indexOf('Hint 1',ladder),`${lesson.id}: the step button comes after the hints`);
 }
 assert.ok(count.check>=6&&count.quiz>=10&&count.section>=10,JSON.stringify(count));
});
test('cards drawer: "This step" keeps only the cards offered on the current page',async()=>{
 const {findCards}=await server.ssrLoadModule('/components/cards-drawer.tsx');
 const lp=findCards('','this','LP');assert.ok(lp.length>=5&&lp.every(card=>card.pages.includes('LP')));assert.ok(lp.some(card=>card.id==='lp-names'));
 assert.ok(findCards('','all').length>lp.length);assert.equal(findCards('','this').length,findCards('','all').length,'no page: every card');
});
test('one control design in every lab: no native range inputs or ad-hoc previous/next buttons; the gap curve has a probe',async()=>{
 const {readdirSync}=await import('node:fs');
 for(const name of readdirSync(new URL('../components/',import.meta.url)).filter(f=>f.endsWith('.tsx'))){
  const src=readFileSync(new URL(`../components/${name}`,import.meta.url),'utf8');
  assert.doesNotMatch(src,/type="range"/,`${name}: use ValueSlider or RecordSlider`);
  assert.doesNotMatch(src,/>(Previous( round| stage)?|Next (swap|stage|interval|pivot|round))</,`${name}: use Stepper`);
  if(/-view\.tsx$|^material-explorer\.tsx$|^energy-ladder\.tsx$/.test(name)&&!/^(boundary-figure|scratch-view)/.test(name))assert.match(src,/className="how-to"/,`${name}: every lab says what to try`);
 }
 const {Day3LineLab}=await server.ssrLoadModule('/components/day3-line-view.tsx');const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url)));
 const gap=renderToStaticMarkup(createElement(Day3LineLab,{lens:data.lens,initialView:'gap'}));
 assert.doesNotMatch(gap,/Read the gaps at x/,'no probe before the curves are faded in');
});
test('stage labels may use any letters: step 08 has its own "The Ω bump" section',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');const M=await server.ssrLoadModule('/lib/lesson-meta.ts');
 assert.ok(M.stages(lessons.find(l=>l.id==='from-or')).some(st=>st.label==='The Ω bump'));
});
test('new attempts of steps 11, 13–16: their cases are not answered above, and the ChatGPT prompt carries the data but not the answers',async()=>{
 const T=await server.ssrLoadModule('/lib/tutor.ts');const {lessons,plainText}=await server.ssrLoadModule('/lib/learning.ts');const M=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const cases={'price-line':[['z=0.60','−20568.44'],['5789.0','−23462.9','−19931.65']],'column-generation':[['0.31209','−20316.40'],['0.643','−1770.7','−19763.8']],
  bounds:[['−1.547','−20472.07'],['−20473.61']],'local-global':[['z=0.10','4002.6'],['−1185.5','0.965','5188.1']],'branch-and-bound':[['−0.426'],['−5585.53']]};
 for(const [id,[data,answers]] of Object.entries(cases)){
  const lesson=lessons.find(l=>l.id===id),stage=M.stages(lesson).find(st=>st.kind==='attempt');
  const prompt=plainText(T.tutorPrompt(T.tutorContext(lesson,stage.key))).replace(/-/g,'−');
  for(const d of data)assert.ok(prompt.includes(d),`${id}: prompt lacks ${d}`);
  for(const a of answers)assert.ok(!prompt.includes(a),`${id}: prompt gives away ${a}`);
  const above=M.stages(lesson).slice(0,M.stages(lesson).indexOf(stage)).map(st=>T.taskText(st.blocks)).join(' ').replace(/-/g,'−');
  for(const a of answers)assert.ok(!plainText(above).includes(a),`${id}: the text above the attempt already gives ${a}`);
 }
});
test('route map: main line and branches as links, labs and notebooks as marks, you-are-here, and remembering is opt-in',async()=>{
 const {default:RouteMap}=await server.ssrLoadModule('/components/route-map.tsx');const {mainLine,stations}=await server.ssrLoadModule('/lib/route-map.ts');
 const M=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const props={current:'lp-primer',progress:{on:false,visited:[],last:null},onLearn(){},onAnchor(){},onLab(){},onRemember(){}};
 const html=renderToStaticMarkup(createElement(RouteMap,props));
 const h=html.slice(0,html.indexOf('route-map-v'));
 assert.equal(mainLine.length,16);assert.equal((h.match(/class="rm-station is-main/g)||[]).length,16);
 for(const st of stations)assert.ok(h.includes(`href="#/${st.id}${st.anchor?`/at/${st.anchor}`:''}"`),st.key);
 assert.match(h,/class="rm-station is-detour[^"]*is-current/);assert.match(h,/aria-current="step"/);
 const labs=stations.filter(st=>!st.anchor&&M.meta[st.id].lab).length,nbs=stations.filter(st=>!st.anchor).reduce((n,st)=>n+(M.notebooks[st.id]?.length??0),0);
 assert.equal((h.match(/class="rm-extra rm-lab/g)||[]).length,labs);assert.equal((h.match(/class="rm-extra rm-notebooks/g)||[]).length,stations.filter(st=>!st.anchor&&(M.notebooks[st.id]?.length??0)>0).length);assert.ok(nbs>20);
 assert.match(html,/Off: nothing about your visit is stored/);assert.doesNotMatch(html,/Forget my progress/);
 const on=renderToStaticMarkup(createElement(RouteMap,{...props,progress:{on:true,visited:['start','unary'],last:'unary'}}));
 assert.match(on,/2 of 16 main-line steps visited/);assert.match(on,/Forget my progress/);assert.match(on,/is-visited/);
});
test('progress is stored only after the learner opts in, and forgetting removes it',async()=>{
 const store=new Map();globalThis.localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
 try{
  const P=await server.ssrLoadModule('/lib/progress.ts');
  store.set('calphad-last','unary');assert.deepEqual(P.loadProgress(),{on:false,visited:[],last:null});assert.equal(store.size,0,'an earlier automatic last step is dropped');
  P.markVisited('binary');assert.equal(store.size,0,'nothing stored while off');
  assert.deepEqual(P.setRemember(true,'binary').visited,['binary']);P.markVisited('twophase');
  assert.deepEqual(P.loadProgress(),{on:true,visited:['binary','twophase'],last:'twophase'});
  P.setRemember(false,null);assert.equal(store.size,0,'forget removes everything');
 }finally{delete globalThis.localStorage;}
});
test('slim rail: only the main line; on a branch a chip says so',async()=>{
 const {default:Nav}=await server.ssrLoadModule('/components/learning-navigation.tsx');
 const main=renderToStaticMarkup(createElement(Nav,{current:'menu',onLearn(){}}));assert.equal((main.match(/<li /g)||[]).length,16);assert.doesNotMatch(main,/On a branch/);
 const branch=renderToStaticMarkup(createElement(Nav,{current:'lp-primer',onLearn(){}}));assert.match(branch,/On a branch: LP primer/);assert.match(branch,/is-join/);
});
test('home video: a local placeholder, nothing loaded from YouTube before play',async()=>{
 const {default:Home}=await server.ssrLoadModule('/components/home.tsx');
 const html=renderToStaticMarkup(createElement(Home,{bundle,onLearn(){},onLab(){}}));
 assert.match(html,/The course in one short video/);assert.match(html,/Play “[^”]+” \(loads the YouTube player\)/);
 assert.doesNotMatch(html,/<iframe|ytimg|youtube-nocookie|<img[^>]+youtube/,'no third-party request before the learner presses play');
 assert.match(html,/href="https:\/\/youtu\.be\/2bX2GEzmYt8"/);
});
test('step videos: each sits on an existing stage, as a play row that loads nothing before play',async()=>{
 const {stepVideos}=await server.ssrLoadModule('/lib/media.ts');const {stages}=await server.ssrLoadModule('/lib/lesson-meta.ts');const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:LearningPage}=await server.ssrLoadModule('/components/learning-page.tsx');
 const ids=new Set();
 for(const [id,list] of Object.entries(stepVideos)){
  const lesson=lessons.find(l=>l.id===id);assert.ok(lesson,id);const keys=stages(lesson).map(s=>s.key);
  const html=renderToStaticMarkup(createElement(LearningPage,{lesson}));
  for(const {stage,video} of list){
   assert.ok(keys.includes(stage),`${id}: no stage ${stage}`);assert.match(video.youtube,/^[\w-]{11}$/);assert.ok(!ids.has(video.youtube),'each video once');ids.add(video.youtube);
   const at=html.indexOf(`id="${id}-${stage}"`),next=html.indexOf('<section',at+1);
   assert.ok(html.slice(at,next<0?undefined:next).includes(`href="https://youtu.be/${video.youtube}"`),`${id}: video at ${stage}`);
  }
  assert.doesNotMatch(html,/<iframe|youtube-nocookie|ytimg/,`${id}: nothing from YouTube before play`);
  assert.doesNotMatch(renderToStaticMarkup(createElement(LearningPage,{lesson,variant:'reference'})),/youtu/,`${id}: no video in the reference view`);
 }
 assert.equal(ids.size,9);
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
test('advanced steps 07–18 and the optional LP primer: step label, Advanced tag, plain-words box, card links and lane/deeper reveals',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const {isAdvanced,isPrimer}=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const advanced=lessons.filter(l=>isAdvanced(l.id));
 assert.deepEqual(advanced.map(l=>l.id),lessons.slice(7).map(l=>l.id),'advanced steps follow steps 00–06');
 assert.deepEqual(advanced.filter(l=>isPrimer(l.id)).map(l=>l.id),['lp-primer']);
 assert.equal(lessons[lessons.findIndex(l=>l.id==='lp-primer')+1].id,'menu','the primer sits just before step 10');
 for(const [i,lesson] of advanced.filter(l=>!isPrimer(l.id)).entries()){
  const html=renderToStaticMarkup(createElement(Page,{lesson}));
  assert.match(html,new RegExp(`<span class="lesson-number">Step ${String(7+i).padStart(2,'0')}</span><span class="advanced-tag">Advanced</span>`),lesson.id);
  assert.match(html,new RegExp(`Step ${String(7+i).padStart(2,'0')} of 18 · advanced`),lesson.id);
  assert.equal((html.match(/class="plain-words"/g)||[]).length,1,lesson.id+': one plain-words box per page');
  assert.match(html,/class="cards-needed"/,lesson.id);
  const cards=(html.match(/class="cards-needed"[\s\S]*?<\/aside>/)[0].match(/data-xref="card#/g)||[]).length;
  assert.ok(cards>=1&&cards<=5,`${lesson.id}: ${cards} cards in "Cards you may need"`);
  assert.doesNotMatch(html,/\bS\d+\b(?![^<]*<\/annotation>)/,lesson.id+': plan step names stay out of learner text');
 }
 const primer=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='lp-primer')}));
 assert.match(primer,/<span class="lesson-number">LP primer<\/span><span class="advanced-tag">Advanced<\/span><span class="optional-tag">Optional<\/span>/);
 assert.match(primer,/Optional primer, after step 07, before step 10 · advanced · about 60 minutes/);
 assert.equal((primer.match(/class="plain-words"/g)||[]).length,1);assert.match(primer,/class="cards-needed"/);
 for(const word of ['subject to','feasible','objective','variables','constraints'])assert.match(primer,new RegExp(word),'the primer explains '+word);
 const m=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='from-materials')}));
 assert.match(m,/class="reveal reveal-deeper"/);assert.match(m,/primer_day2\/figures\/twophase_regular\.png/);
});
test('LP primer lab renders every view from the exported data, with the reference answers',async()=>{
 const {LpPrimerLab}=await server.ssrLoadModule('/components/lp-primer-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/lp_primer.json',import.meta.url),'utf8'));
 for(const view of ['chords','swap','nudge','polygon']){
  const html=renderToStaticMarkup(createElement(LpPrimerLab,{data,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.match(html,/data-plot/,view);
  assert.doesNotMatch(html,/NaN|Infinity|undefined/,view);
 }
 const swap=renderToStaticMarkup(createElement(LpPrimerLab,{data,initialView:'swap'}));
 assert.match(swap,/Round 1 of 3/);assert.match(swap,/Monel lies 2\.47 € below the line: it comes in, Ni \(same side of 0\.40\) goes out/);
 const nudge=renderToStaticMarkup(createElement(LpPrimerLab,{data,initialView:'nudge'}));
 assert.match(nudge,/Price of nickel content: 5\.14 € per unit, while CuNi30 and Monel stay in use/);
 const polygon=renderToStaticMarkup(createElement(LpPrimerLab,{data,initialView:'polygon'}));
 assert.equal((polygon.match(/class="lp-rule /g)||[]).length,4);assert.equal((polygon.match(/role="slider"/g)||[]).length,2);
 assert.match(polygon,/5 corners/);assert.match(polygon,/Ties at a Monel price of €8\.40 and €18\.20/);
});
test('Day 3 line lab renders every view from the exported data',async()=>{
 const {Day3LineLab}=await server.ssrLoadModule('/components/day3-line-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url),'utf8'));
 for(const view of ['menu','line','gap','move-z','temperature']){
  const html=renderToStaticMarkup(createElement(Day3LineLab,{lens:data.lens,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.match(html,/data-plot/,view);
  assert.doesNotMatch(html,/NaN|Infinity/,view);
 }
 const line=renderToStaticMarkup(createElement(Day3LineLab,{lens:data.lens,initialView:'line'}));
 assert.equal((line.match(/role="slider"/g)||[]).length,2);assert.match(line,/Not a floor|A floor for these dots/);
 const own=renderToStaticMarkup(createElement(Day3LineLab,{lens:data.lens,initialView:'gap',views:['gap','move-z','temperature']}));
 assert.match(own,/Move z/);assert.doesNotMatch(own,/>Menu</,'a step shows only its own views');
 assert.doesNotMatch(renderToStaticMarkup(createElement(Day3LineLab,{lens:data.lens,initialView:'menu',views:['menu']})),/aria-label="Lab view"/,'one view needs no switch');
});
test('Day 3 column-generation lab renders every view and every stage',async()=>{
 const {Day3CgLab}=await server.ssrLoadModule('/components/day3-cg-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url),'utf8'));
 for(const view of ['player','bounds','spacing']){
  const html=renderToStaticMarkup(createElement(Day3CgLab,{lens:data.lens,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.match(html,/data-plot/,view);assert.doesNotMatch(html,/NaN|Infinity/,view);
 }
});
test('Day 3 regular-solution lab renders every view',async()=>{
 const {Day3RegularLab}=await server.ssrLoadModule('/components/day3-regular-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url),'utf8'));
 for(const view of ['local','pricing','bnb','joint']){
  const html=renderToStaticMarkup(createElement(Day3RegularLab,{reg:data.regular,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.match(html,/data-plot/,view);assert.doesNotMatch(html,/NaN|Infinity/,view);
 }
 const bnb=renderToStaticMarkup(createElement(Day3RegularLab,{reg:data.regular,initialView:'bnb'}));
 assert.match(bnb,/Interval 1 of 27/);assert.match(bnb,/class="interval-bar act-split is-current"/);
});
test('Day 3 pre-work lab renders every view',async()=>{
 const {Day3PreworkLab}=await server.ssrLoadModule('/components/day3-prework-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3_prework.json',import.meta.url),'utf8'));
 for(const view of ['second-law','counter','builder','omega']){
  const html=renderToStaticMarkup(createElement(Day3PreworkLab,{data,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.doesNotMatch(html,/NaN|Infinity/,view);
 }
 assert.match(renderToStaticMarkup(createElement(Day3PreworkLab,{data,initialView:'second-law'})),/Total entropy up, G down/);
});
test('advanced lane toggle opens only its own boxes; route strip and cards search work',async()=>{
 const {lessons}=await server.ssrLoadModule('/lib/learning.ts');
 const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const {LaneContext}=await server.ssrLoadModule('/lib/lane.ts');
 const lesson=lessons.find(l=>l.id==='price-line');
 const render=lane=>renderToStaticMarkup(createElement(LaneContext.Provider,{value:{lane,setLane(){}}},createElement(Page,{lesson})));
 const none=render(null),m=render('M'),o=render('O');
 assert.doesNotMatch(none,/<details open/);assert.match(none,/class="route-strip"/);assert.match(none,/Step 11 of 18 · advanced · about 30–40 minutes without the optional boxes/);assert.match(none,/>materials science<\/button><button[^>]*>operations research</);
 const openLabels=html=>[...html.matchAll(/<details open=""><summary>([^<]+)</g)].map(x=>x[1]);
 assert.deepEqual(openLabels(m),['Coming from materials']);
 assert.ok(openLabels(o).includes('Coming from operations research')&&openLabels(o).some(l=>l.startsWith('Dive deeper for operations research'))&&!openLabels(o).includes('Coming from materials'));
 const plain=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='twophase')}));assert.doesNotMatch(plain,/lane-toggle|advanced-tag/);assert.match(plain,/class="route-strip"/);assert.match(plain,/Step 03 of 18 · “Dive deeper” sections are optional</);assert.match(plain,/Part D</);
 const odds=renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='boundary')}));assert.match(odds,/class="deeper-flag">Optional</);assert.match(odds,/<div class="reveal reveal-deeper"><details><summary>Dive deeper · where the odds formula comes from \(optional section\)/);
 const {findCards}=await server.ssrLoadModule('/components/cards-drawer.tsx');
 assert.ok(findCards('lever','all').some(c=>c.id==='lever-rule'));
 assert.ok(findCards('Ω','all').some(c=>c.id==='regular-omega'));
 assert.equal(findCards('','core').length,14);
 assert.ok(findCards('','M').some(c=>c.deck==='both')&&!findCards('','M').some(c=>c.deck==='O'));
 assert.equal(findCards('no such word anywhere','all').length,0);
});
test('Day 3 triangle lab renders every view',async()=>{
 const {Day3TernaryLab}=await server.ssrLoadModule('/components/day3-ternary-view.tsx');
 const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3_ternary.json',import.meta.url),'utf8'));
 for(const view of ['triangle','landscape','harder']){
  const html=renderToStaticMarkup(createElement(Day3TernaryLab,{data,initialView:view}));
  assert.match(html,new RegExp(`id="lab-${view}"`),view);assert.doesNotMatch(html,/NaN|Infinity/,view);
 }
 const land=renderToStaticMarkup(createElement(Day3TernaryLab,{data,initialView:'landscape'}));
 assert.equal((land.match(/<polygon points=/g)||[]).length,40*40);
});
test('home: one route 00–18 with the advanced junction, advanced lab cards, how-it-works item and printable pack',async()=>{
 const {default:Home}=await server.ssrLoadModule('/components/home.tsx');
 const html=renderToStaticMarkup(createElement(Home,{bundle,onLearn(){},onLab(){}}));
 assert.doesNotMatch(html,/advanced-box|Day 3|Page [MOA]/);
 assert.equal((html.match(/class="route-card /g)||[]).length,20);
 assert.equal((html.match(/class="route-card group-advanced"/g)||[]).length,11);
 assert.equal((html.match(/class="route-card group-advanced is-optional"/g)||[]).length,2,"the LP primer and step 18 are dashed and optional");
 assert.match(html,/<strong>19<\/strong>steps, 00–18, and an optional LP primer/);
 assert.ok(html.indexOf('LP primer · the cheapest mix')>html.indexOf('Prices and metastability · ')&&html.indexOf('LP primer · the cheapest mix')<html.indexOf('Menu · equilibrium'),'the primer card sits between steps 09 and 10');
 const junction=html.indexOf('class="route-junction"'),seven=html.indexOf('From materials science · ');
 assert.ok(junction>html.indexOf('Ni–Nb')&&junction<seven,'the junction sits between step 06 and step 07');
 assert.match(html,/Know CALPHAD from materials science, or followed steps 00–06\?[\s\S]*?Step 07, then step 10/);
 assert.match(html,/Know methods from operations research\?[\s\S]*?Steps 08 and 09, then step 10/);assert.match(html,/Coming from operations research\? Start at step 08/);
 assert.ok((html.match(/class="lab-card lab-card-[a-z-]+ is-advanced"/g)||[]).length>=4);
 assert.match(html,/Then the solver itself/);
 assert.match(html,/Advanced on paper[\s\S]*?course\/day3\/lp_primer_sheet\.md[\s\S]*?course\/day3\/picture_sheet\.md/);
});

test('concept links: every step can ask about any term; dive-deeper and background boxes and cards ask about their concept, never with hints or answers',async()=>{
 const {lessons,plainText}=await server.ssrLoadModule('/lib/learning.ts');const {default:Page}=await server.ssrLoadModule('/components/learning-page.tsx');
 const {isAdvanced}=await server.ssrLoadModule('/lib/lesson-meta.ts');
 const prompts=html=>[...html.matchAll(/<a [^>]*data-ask="concept"[^>]*>/g)].map(m=>/href="https:\/\/chatgpt\.com\/\?q=([^"]+)"/.exec(m[0])).map(m=>decodeURIComponent(m[1].replace(/&amp;/g,'&')));
 for(const lesson of lessons){
  const html=renderToStaticMarkup(createElement(Page,{lesson})),list=prompts(html);
  assert.ok(list.some(p=>p.includes('Concept: a term of my choice')),lesson.id+': ask about another term');
  if(isAdvanced(lesson.id))assert.ok(list.length>=2,lesson.id+': concept links in its boxes');
  const help=lesson.blocks.filter(b=>b.type==='reveal'&&/^(Hint \d|Worked answer)/.test(b.label)).flatMap(b=>b.blocks).filter(b=>b.type==='paragraph').map(b=>plainText(b.text).slice(0,60)).filter(t=>t.length>=40);
  for(const p of list){
   assert.match(p,/Explain the concept below at the level of the course/);assert.match(p,/My question: $/);assert.ok(encodeURIComponent(p).length<8000,lesson.id);
   for(const h of help)assert.ok(!p.includes(h),`${lesson.id}: concept prompt contains help text: ${h}`);
  }
 }
 const or=prompts(renderToStaticMarkup(createElement(Page,{lesson:lessons.find(l=>l.id==='price-line')})));
 assert.ok(or.some(p=>/My background: operations research\./.test(p)&&/Concept: /.test(p)));
 assert.ok(or.some(p=>/My background: materials science\./.test(p)));
 const {CardList}=await server.ssrLoadModule('/components/cards-drawer.tsx');
 const cardsHtml=renderToStaticMarkup(createElement(CardList,{query:'lever',filter:'all'}));
 assert.ok(prompts(cardsHtml).some(p=>p.includes('Concept: Hang on: what was the lever rule?')&&p.includes('What the course says:')));
 const {default:Drawer}=await server.ssrLoadModule('/components/cards-drawer.tsx');assert.ok(Drawer);
});
