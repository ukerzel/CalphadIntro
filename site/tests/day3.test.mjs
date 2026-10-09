/** Day 3 display arithmetic against the exported reference answers; no science is computed here. */
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {below,bestOfBasket,height,lever,liftAndPivot,through,gapCurve} from '../lib/day3.ts';
const data=JSON.parse(readFileSync(new URL('../public/learning/self_study/generated/day3.json',import.meta.url),'utf8'));
const lens=data.lens,dots=lens.menu.dots,z=lens.z;
test('the reveal animation from slope 20000 reproduces the exported frames and ends on the menu line',()=>{
 const frames=liftAndPivot(dots,z,lens.reveal.start_slope);
 assert.equal(frames.length,lens.reveal.frames.length);
 frames.forEach((f,i)=>{const e=lens.reveal.frames[i];assert.ok(Math.abs(f.mu_A-e.mu_A)<1e-6&&Math.abs(f.d_mu-e.d_mu)<1e-6);assert.deepEqual(f.touch,e.touch);});
 for(const f of frames)assert.equal(below(dots,f.mu_A,f.d_mu,1e-6).length,0);
 for(const slope of [-15000,-5000,0,3000,9000,20000]){const last=liftAndPivot(dots,z,slope).at(-1);assert.ok(Math.abs(last.mu_A-lens.s2.mu_A)<1e-6&&Math.abs(last.d_mu-lens.s2.d_mu)<1e-6,`slope ${slope}`);}
});
test('basket arithmetic: the whole menu gives the exported cheapest mixture; one-sided baskets give none',()=>{
 const best=bestOfBasket(dots,z);assert.ok(Math.abs(best.G-lens.s1.G_up)<1e-8);
 assert.deepEqual(best.used.map(i=>[dots[i].phase,dots[i].x]).sort(),lens.s1.used.map(u=>[u.phase,u.x]).sort());
 assert.equal(bestOfBasket(dots.filter(d=>d.x>z),z),null);
 assert.equal(lever(dots[3],dots[4],z),null);
 const hook=bestOfBasket(lens.hook.dots,z);assert.ok(Math.abs(hook.G-lens.hook.G_up)<1e-8);
});
test('line arithmetic agrees with the exported line, gaps and nudge',()=>{
 const used=lens.s1.used,line=through(used[1],used[0]);
 assert.ok(Math.abs(line.mu_A-lens.s2.mu_A)<1e-6&&Math.abs(line.d_mu-lens.s2.d_mu)<1e-6);
 assert.equal(below(dots,lens.s2.mu_A,lens.s2.d_mu).length,0);
 for(const g of lens.s4.gaps){const d=dots.find(p=>p.phase===g.phase&&p.x===g.x);assert.ok(Math.abs(d.g-height(lens.s2.mu_A,lens.s2.d_mu,d.x)-g.gap)<1e-6);}
 assert.ok(Math.abs(lens.s2.d_mu*lens.s3.nudge-lens.s3.nudge_energy)<1e-9);
 const gaps=gapCurve(lens.curve.x,lens.curve.SOLID,lens.s2.mu_A,lens.s2.d_mu);
 assert.ok(Math.min(...gaps)<0&&Math.min(...gaps)>=lens.s7.dips.SOLID.depth-1e-9,'the drawn curve dips below the line, never deeper than the exported dip');
});
test('zoom windows contain each round\'s deepest dip',()=>{
 for(const it of lens.s6.iterations){const w=it.windows[it.best.phase];const m=Math.min(...w.gap);
  assert.ok(m<=it.best.depth+Math.max(1e-6,Math.abs(it.best.depth)*0.05)&&m>=it.best.depth-1e-9,`round ${it.k}: ${m} vs ${it.best.depth}`);}
});
test('regular-solution exports agree with the drawn gap curves',()=>{
 const reg=data.regular,t=reg.s8.tangent,xs=reg.curve.x;
 const gaps=gapCurve(xs,reg.curve.ALPHA,t.mu_A,t.d_mu);
 assert.ok(Math.abs(gaps[150])<1e-6,'the tangent touches at 0.15');
 assert.ok(Math.min(...gaps)>=reg.s8.dip.depth-1e-9&&Math.min(...gaps)<reg.s8.dip.depth+1,'the drawn dip matches the exported one');
 for(const nd of reg.s9.nodes){const inside=xs.flatMap((v,i)=>v>=nd.lo&&v<=nd.hi?[reg.curve.ALPHA[i]-height(reg.s9.line.mu_A,reg.s9.line.d_mu,v)]:[]);
  if(inside.length)assert.ok(nd.floor<=Math.min(...inside)+1e-9,`node ${nd.n}: the floor is below the drawn curve`);}
 const leaves=reg.s9.leaves;assert.equal(leaves[0].lo,0);assert.equal(leaves.at(-1).hi,1);
 for(let i=1;i<leaves.length;i++)assert.equal(leaves[i].lo,leaves[i-1].hi);
});
