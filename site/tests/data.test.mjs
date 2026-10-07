import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { loadBundle,selectRecord,digest,sourceURL,validate,REPO_FILE_REF } from '../lib/data.ts';
const directory=new URL('../public/data/',import.meta.url);
const asset=(name)=>new Uint8Array(readFileSync(new URL(name,directory)));
const fetcher=async(url)=>new Response(asset(url.split('/').at(-1)));

test('loads actual synced bytes and selects exact worksheet/crossing rows',async()=>{
  const bundle=await loadBundle(fetcher);
  assert.equal(bundle.unary.records.length,201);
  assert.deepEqual(selectRecord(bundle.unary.records,'unary-000').gibbs_J_per_mol,[-7000,-5800]);
  const cross=selectRecord(bundle.unary.records,'unary-100');
  assert.equal(cross.T_K,1000);
  assert.equal(cross.phase_status,'equal_energy_fractions_underdetermined');
  assert.deepEqual(cross.gibbs_J_per_mol,[-9000,-9000]);
  assert.equal(bundle.unary.saved_comparison_rows.length,5);
  assert.throws(()=>selectRecord(bundle.unary.records,'unary-100.5'),/exact exported/);
  assert.throws(()=>selectRecord(bundle.unary.records,'unary-201'),/exact exported/);
  for(const route of bundle.manifest.reading_routes) assert.match(sourceURL(bundle.receipt.source_commit,route),new RegExp(`/blob/${REPO_FILE_REF??'[a-f0-9]{40}'}/course/`));
  assert.throws(()=>sourceURL(bundle.receipt.source_commit,'course/../../secret'),/Invalid source/);
});
test('missing or changed assets fail without a numerical fallback',async()=>{
  await assert.rejects(loadBundle(async()=>new Response('missing',{status:404})),/Missing exported asset/);
  await assert.rejects(loadBundle(async(url)=>url.endsWith('unary.json')?new Response('{}'):fetcher(url)),/hash mismatch/);
  await assert.rejects(loadBundle(async(url)=>url.endsWith('build_receipt.json')?new Response('{"schema_version":999}'):fetcher(url)),/Unsupported build receipt/);
});
test('schema rejects missing/nonfinite/version/domain and ID drift after hash validation',async()=>{
  const original=JSON.parse(new TextDecoder().decode(asset('unary.json')));
  const schema=JSON.parse(new TextDecoder().decode(asset('dataset.schema.json')));
  for(const fault of ['missing','nonfinite','version','domain']){
    const data=structuredClone(original);
    if(fault==='missing') delete data.records[100].equilibrium;
    if(fault==='nonfinite') data.records[100].equilibrium.GM=NaN;
    if(fault==='version') data.schema_version=true;
    if(fault==='domain') data.records[0].T_K=799;
    assert.throws(()=>validate(data,schema));
  }
  const shifted=structuredClone(original); shifted.records[100].id='wrong-id';
  const bytes=new TextEncoder().encode(JSON.stringify(shifted));
  const receipt=JSON.parse(new TextDecoder().decode(asset('build_receipt.json')));
  receipt.payload_sha256['unary.json']=await digest(bytes);
  await assert.rejects(loadBundle(async(url)=>{
    if(url.endsWith('unary.json'))return new Response(bytes);
    if(url.endsWith('build_receipt.json'))return new Response(JSON.stringify(receipt));
    return fetcher(url);
  }),/IDs\/order/);
});
test('binary and boundary readouts keep raw export values and both balance bases',async()=>{
  const bundle=await loadBundle(fetcher);
  assert.equal(bundle.binary.records.length,99);assert.equal(bundle.boundary.records.length,81);
  const binary=selectRecord(bundle.binary.records,'binary-049');
  assert.equal(binary.x_B,.5);assert.equal(binary.derivatives.slope,12000);
  const row=selectRecord(bundle.boundary.records,'boundary-000');
  assert.equal(row.closed.inventory.initial.B,850);assert.equal(row.closed.inventory.initial.A,7350);
  assert.equal(row.closed.result.theta,.17160753314081367);
  assert.equal(row.closed.result.theta_root,.17160752408695693);
  assert.notEqual(row.closed.result.theta,row.closed.result.theta_root);
  for(const component of ['A','B']) assert.ok(Math.abs(row.closed.inventory.residual_atoms[component])<1e-9);
  assert.ok(row.open.inventory.exchange_atoms.B<0);assert.equal(row.open.inventory.conserved,false);
  assert.ok(!('residual_atoms' in row.open.inventory));
  await assert.rejects(loadBundle(async(url)=>url.endsWith('boundary.json')?new Response('{}'):fetcher(url)),/hash mismatch/);
});
