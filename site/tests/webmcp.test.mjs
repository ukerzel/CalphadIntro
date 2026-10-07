import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedSelection,registerSelection} from '../lib/webmcp.ts';
const bundle=Object.fromEntries(['unary','binary','boundary'].map(panel=>[panel,JSON.parse(readFileSync(new URL(`../public/data/${panel}.json`,import.meta.url)))]));
test('selects actual row IDs and rejects fractional/out-of-view/extra input',()=>{
  assert.deepEqual(checkedSelection(bundle,{view:'binary',recordId:'binary-049'}),{view:'binary',recordId:'binary-049',index:49});
  for(const input of [{view:'binary',recordId:'unary-100'},{view:'unary',recordId:'unary-100.5'},{view:'boundary',recordId:'boundary-081'},{view:'unary',recordId:'unary-100',T:1000},null]) assert.throws(()=>checkedSelection(bundle,input));
});
test('optional registry has intentional state effects, signal cleanup and unsupported path',async()=>{
  let registration,signal,state;
  const cleanup=registerSelection({registerTool(tool,options){registration=tool;signal=options.signal;}},bundle,s=>{state=s;});
  assert.equal(registration.name,'select_exported_row');
  assert.equal(registration.annotations.readOnlyHint,false);
  assert.deepEqual(registration.execute({view:'boundary',recordId:'boundary-000'}),{view:'boundary',recordId:'boundary-000'});
  assert.equal(state.index,0);
  assert.throws(()=>registration.execute({view:'boundary',recordId:'boundary-999'}));
  assert.equal(state.recordId,'boundary-000');
  cleanup(); assert.equal(signal.aborted,true);
  registerSelection(undefined,bundle,()=>assert.fail())();
  let failure;
  registerSelection({registerTool(){throw Error('context unavailable');}},bundle,()=>assert.fail(),e=>{failure=e;})();
  assert.match(failure.message,/context unavailable/);
});
