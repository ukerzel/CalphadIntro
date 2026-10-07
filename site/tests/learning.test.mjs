import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {validateContent,syncContent,checkTeX} from '../scripts/sync-content.mjs';
import {readdirSync} from 'node:fs';
const content=JSON.parse(readFileSync(new URL('../../course/self_study/lessons.json',import.meta.url),'utf8'));
test('published content is fresh; stale bytes and unallowlisted files fail',()=>{
 syncContent({check:true});
 const destination=mkdtempSync(join(tmpdir(),'calphad-learning-'));
 try{
  syncContent({destination});syncContent({destination,check:true});
  writeFileSync(join(destination,'lessons.json'),'{}');
  assert.throws(()=>syncContent({destination,check:true}),/Stale learning copy/);
  syncContent({destination});writeFileSync(join(destination,'private.tdb'),'excluded');
  assert.throws(()=>syncContent({destination,check:true}),/Unallowlisted/);
 }finally{rmSync(destination,{recursive:true,force:true});}
});
test('finite content rejects unsafe paths, HTML blocks, nested reveals and unavailable routes',()=>{
 for(const change of [
  c=>{c.modules[0].sources=['course/../private.md'];},
  c=>{c.modules[0].blocks.push({type:'html',text:'<script/>'});},
  c=>{c.modules[0].blocks.push({type:'reveal',label:'bad',blocks:[{type:'reveal',label:'nested',blocks:[]}]});},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'bad',image:{src:'/private.png',alt:'private'}});},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'bad',links:[{label:'unsafe',href:'javascript:alert(1)'}]});},
  c=>{c.modules[0].next='missing';},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'bad {{no_such_term|μ}} token'});},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'unbalanced {{mu_chem|μ token'});},
  c=>{c.terms.push({...c.terms[0]});},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'broken $\\frac{1}{$ formula'});},
  c=>{c.modules[0].blocks.push({type:'paragraph',text:'a stray $ sign'});},
 ]){const mutated=structuredClone(content);change(mutated);assert.throws(()=>validateContent(mutated));}
});
test('every defined term is used and every token resolves',()=>{
 const used=new Set(JSON.stringify(content.modules).match(/\{\{[a-z_]+\|/g).map(t=>t.slice(2,-1)));
 assert.deepEqual([...used].sort(),content.terms.map(t=>t.id).sort());
 validateContent(content);
});
test('every lab equation parses as strict KaTeX',()=>{
 const dir=new URL('../components/',import.meta.url);let count=0;
 for(const name of readdirSync(dir).filter(n=>n.endsWith('.tsx'))){
  for(const [,tex] of readFileSync(new URL(name,dir),'utf8').matchAll(/<Eq label="[^"]*" tex=\{String\.raw`([^`]*)`\}/g)){checkTeX(tex);count++;}
 }
 assert.ok(count>=19,`only ${count} equations found`);
});
test('unary worked table matches canonical exports including the tie',()=>{
 const module=content.modules.find(m=>m.id==='unary');
 const table=module.blocks.find(b=>b.label==='Worked answer').blocks.find(b=>b.type==='table');
 const unary=JSON.parse(readFileSync(new URL('../../course/site/generated/unary.json',import.meta.url)));
 for(const row of table.rows){const record=unary.records.find(r=>r.T_K===Number(row[0]));assert.deepEqual(row.slice(1,3).map(x=>Number(x.replace('−','-'))),record.gibbs_J_per_mol);}
});
test('binary worked answer retains existing D2/D3 precision and ALPHA domain',()=>{
 const module=content.modules.find(m=>m.id==='binary');
 const answer=module.blocks.find(b=>b.label==='Worked answer').blocks[0].text;
 const binary=JSON.parse(readFileSync(new URL('../../course/site/generated/binary.json',import.meta.url)));
 const row=binary.records.find(r=>r.x_B===.2);
 assert.ok(Math.abs(row.properties.GM-(-10760.596))<.001);
 assert.ok(Math.abs(row.derivatives.slope-473.656)<.001);
 assert.match(answer,/−10760.596/);assert.match(answer,/473.656/);
});
test('binary end-member h and s inputs reproduce the exported enthalpy and entropy',()=>{
 const module=content.modules.find(m=>m.id==='binary');
 const row=module.blocks.find(b=>b.type==='table').rows.find(r=>r[1].includes('13000'));
 const [hA,hB,sA,sB]=row[1].match(/[\d.]+/g).slice(0,4).map(Number);
 const binary=JSON.parse(readFileSync(new URL('../../course/site/generated/binary.json',import.meta.url)));
 for(const r of binary.records){
  assert.ok(Math.abs((1-r.x_B)*hA+r.x_B*hB-r.properties.HM)<1e-9,`HM ${r.x_B}`);
  assert.ok(Math.abs((1-r.x_B)*sA+r.x_B*sB+r.properties.SM_mix-r.properties.SM)<1e-9,`SM ${r.x_B}`);
 }
});
test('two-phase narration agrees with the generated course data',()=>{
 const module=content.modules.find(m=>m.id==='twophase');
 const text=JSON.stringify(module.blocks);
 const data=JSON.parse(readFileSync(new URL('../../course/self_study/generated/two_phase.json',import.meta.url)));
 const co=data.part_a.coexistence, half=data.part_a.states.find(s=>s.z===0.5);
 assert.match(text,new RegExp(co.x_ALPHA.toFixed(5).replace('.','\\.')));assert.match(text,new RegExp(co.x_BETA.toFixed(5).replace('.','\\.')));
 assert.match(text,new RegExp(co.mu_A.toFixed(3).replace('-','−').replace('.','\\.')));
 assert.match(text,new RegExp(half.homogeneous_GM.ALPHA.toFixed(3).replace('-','−').replace('.','\\.')));
 assert.match(text,/−10760\.596/);
 const at02=data.part_a.x.indexOf(0.2);assert.ok(Math.abs(data.part_a.GM.ALPHA[at02]-(-10760.596))<5e-4);
 const r600=data.part_b.rows.find(r=>r.T_K===600);
 assert.match(text,new RegExp(`${r600.compositions[0].toFixed(3)} and ${r600.compositions[1].toFixed(3)}`.replaceAll('.','\\.')));
 assert.match(text,new RegExp(`\\\\approx ${data.part_b.Tc_K.toFixed(0)}\\$ K`));
 assert.equal(data.part_c.melting_K.A,1000);assert.equal(data.part_c.melting_K.B,1800);assert.match(text,/melts at 1000 K/);assert.match(text,/melts at 1800 K/);
 assert.equal(module.next,'boundary');assert.equal(content.modules.find(m=>m.id==='binary').next,'twophase');
});
test('boundary answer uses both balances and the original normalization',()=>{
 const module=content.modules.find(m=>m.id==='boundary');
 const answer=module.blocks.find(b=>b.label==='Worked answer').blocks.map(b=>b.text).join(' ');
 const data=JSON.parse(readFileSync(new URL('../../course/site/generated/boundary.json',import.meta.url)));
 const row=data.records[0].closed;
 assert.equal(row.inventory.initial.B,850);assert.equal(row.inventory.initial.A,7350);
 for(const component of ['A','B'])assert.ok(Math.abs(row.inventory.final[component]-row.inventory.initial[component])<1e-9);
 assert.match(answer,new RegExp(String(row.result.theta).replaceAll('.','\\.')));
 assert.match(answer,/48.78049/);assert.ok(Math.abs(200*2000/8200-48.78049)<.00001);
 assert.match(answer,/0.17160752408695693/);
});
test('Cu–Ni supplied balance exercise agrees with full-precision saved results',()=>{
 const module=content.modules.find(m=>m.id==='cuni');
 const table=module.blocks.find(b=>b.type==='table');
 const result=JSON.parse(readFileSync(new URL('../../course/materials/cuni/results.json',import.meta.url)));
 const phases=result.equilibrium.magnetic_on.samples['600'].phases;
 assert.deepEqual(table.rows.map(row=>[Number(row[1]),Number(row[2])]),phases.map(p=>[p.atom_mole_fraction,p.x_NI]));
 for(const complement of [false,true])assert.ok(Math.abs(phases.reduce((sum,p)=>sum+p.atom_mole_fraction*(complement?1-p.x_NI:p.x_NI),0)-.5)<result.tolerances.balance_abs);
});
test('Ni–Nb conversion exercise matches the saved formula and atom bases',()=>{
 const module=content.modules.find(m=>m.id==='ninb');
 const table=module.blocks.find(b=>b.type==='table');
 const result=JSON.parse(readFileSync(new URL('../../course/materials/ninb/results.json',import.meta.url)));
 const checks=[result.energy_checks.delta_NB_NB_NB,result.energy_checks.mu_all_NI];
 table.rows.forEach((row,i)=>{
  assert.equal(Number(row[1].replace('−','-')),checks[i].formula_J_per_mol);
  assert.ok(Math.abs(Number(row[1].replace('−','-'))/Number(row[2])-checks[i].atom_J_per_mol)<result.tolerances.energy_abs);
 });
 const answer=module.blocks.find(b=>b.label==='Worked answer').blocks[0].text;
 for(const check of checks)assert.ok(answer.includes(String(check.atom_J_per_mol).replace('-','−')));
 for(const component of ['NB','NI'])assert.ok(Math.abs(result.sample.phases.reduce((s,p)=>s+p.atom_mole_fraction*(component==='NB'?p.x_NB:1-p.x_NB),0)-(component==='NB'?result.sample.X_NB:1-result.sample.X_NB))<result.tolerances.balance_abs);
});
