/** Finite exported records only. Rendering and selection perform no thermodynamics. */
/** Where the course files live. The public release build (release/build.py) rewrites these constants. */
export const REPO_WEB = 'https://github.com/ukerzel/CalphadIntro';
export const REPO_BLOB = `${REPO_WEB}/blob`;
/** Reference for file links: null = the commit recorded in the data receipt (development); a release tag in releases. */
export const REPO_FILE_REF: string | null = 'v0.1.4';
/** GitHub repository that Colab opens notebooks from: the public one (development opens its latest release, the main branch). */
export const COLAB_REPO = 'ukerzel/CalphadIntro';
/** Source files not in this copy of the course (the release build lists them); their links are left out. */
export const OMITTED_SOURCES: string[] = [];

export const fileURL = (ref: string, path: string) => `${REPO_BLOB}/${ref}/${path}`;
/** Version shown with the lab data: the release tag, or in development the commit the data were exported from. */
export const dataVersion = (receipt: Receipt) => REPO_FILE_REF ?? receipt.source_commit.slice(0, 12);

export type Panel = { id: string; record_count: number; units: Record<string,string>;
  conditions: Record<string,unknown>; limitations: string; review_scope: string;
  source_paths: string[]; task_ids: string[]; selection: {field:string;minimum:number;maximum:number;step:number} };
export type Manifest = { schema_version: 1; panels: Panel[]; reading_routes: string[]; day2_remaining_tasks: string[] };
export type Receipt = { schema_version: 1; source_commit: string; manifest_sha256: string;
  payload_sha256: Record<string,string>; adapter_sha256: Record<string,string>; status:string; baseline_full_suite:string };
export type UnaryRow = { id:string; T_K:number; gibbs_J_per_mol:[number,number];
  HM_J_per_mol:[number,number]; SM_J_per_mol_K:[number,number];
  equilibrium:{GM:number;fractions:{SOLID:number;LIQUID:number}};
  phase_status:'SOLID'|'LIQUID'|'equal_energy_fractions_underdetermined' };
export type UnaryData = { schema_version:1; panel_id:'unary'; units:Record<string,string>;
  records:UnaryRow[]; crossing_temperature_K:number; saved_comparison_rows:unknown[]; saved_comparison_status:string };
export type BinaryRow = {id:string;x_B:number;properties:Record<string,number>;derivatives:Record<string,number>};
export type BoundaryState = {result:Record<string,number|boolean>;inventory:{initial:{A:number;B:number};final:{A:number;B:number};bulk_final:{A:number;B:number};boundaries_final:{A:number;B:number};residual_atoms?:{A:number;B:number};exchange_atoms?:{A:number;B:number};conserved:boolean};bulk_amount_mol:number;boundary_amount_mol:number;B_boundary_excess_atoms:number;B_boundary_excess_mol:number;mu_A_J_per_mol:number;mu_B_J_per_mol:number};
export type BoundaryRow = {id:string;x_initial_or_reservoir_B:number;open:BoundaryState;closed:BoundaryState};
export type BinaryData = {schema_version:1;panel_id:'binary';units:Record<string,string>;records:BinaryRow[]};
export type BoundaryData = {schema_version:1;panel_id:'boundary';units:Record<string,string>;records:BoundaryRow[]};
export type Bundle = {manifest:Manifest;receipt:Receipt;unary:UnaryData;binary:BinaryData;boundary:BoundaryData};
export type View = 'unary'|'binary'|'boundary';
type Schema = { [key:string]:unknown; type?:string; const?:unknown; enum?:unknown[];
  oneOf?:Schema[];properties?:Record<string,Schema>;required?:string[];
  additionalProperties?:boolean;items?:Schema;minItems?:number;maxItems?:number;
  minLength?:number;minimum?:number;maximum?:number };

function same(a:unknown,b:unknown):boolean {
  if (a === b) return true;
  if (typeof a !== typeof b || a === null || b === null) return false;
  if (Array.isArray(a) && Array.isArray(b)) return a.length===b.length && a.every((x,i)=>same(x,b[i]));
  if (typeof a==='object' && typeof b==='object' && !Array.isArray(a) && !Array.isArray(b)) {
    const aa=a as Record<string,unknown>, bb=b as Record<string,unknown>;
    return Object.keys(aa).length===Object.keys(bb).length && Object.keys(aa).every(k=>k in bb && same(aa[k],bb[k]));
  }
  return false;
}
function finite(value:unknown):void {
  if (typeof value==='number' && !Number.isFinite(value)) throw Error('Nonfinite exported value');
  if (Array.isArray(value)) value.forEach(finite);
  else if (value && typeof value==='object') Object.values(value).forEach(finite);
}
export function validate(value:unknown,schema:Schema):void {
  finite(value);
  const vocabulary=['$schema','oneOf','type','const','enum','properties','required','additionalProperties','items','minItems','maxItems','minLength','minimum','maximum'];
  if (Object.keys(schema).some(k=>!vocabulary.includes(k))) throw Error('Unsupported schema keyword');
  if (schema.oneOf) {
    const count=schema.oneOf.filter(s=>{try {validate(value,s);return true;} catch {return false;}}).length;
    if(count!==1) throw Error('Export does not match its scientific schema');
  }
  if ('const' in schema && !same(value,schema.const)) throw Error('Wrong schema version or scientific metadata');
  if (schema.enum && !schema.enum.some(x=>same(x,value))) throw Error('Unknown exported label');
  if(schema.type==='object') {
    if(!value || typeof value!=='object' || Array.isArray(value)) throw Error('Expected object');
    const object=value as Record<string,unknown>, props=schema.properties??{};
    if(schema.required?.some(k=>!(k in object))) throw Error('Missing scientific field');
    if(schema.additionalProperties===false && Object.keys(object).some(k=>!(k in props))) throw Error('Unexpected scientific field');
    Object.entries(object).forEach(([k,v])=>{if(props[k]) validate(v,props[k]);});
  } else if(schema.type==='array') {
    if(!Array.isArray(value) || value.length<(schema.minItems??0) || value.length>(schema.maxItems??Infinity)) throw Error('Wrong record count');
    value.forEach(v=>validate(v,schema.items??{}));
  } else if(schema.type==='number'||schema.type==='integer') {
    if(typeof value!=='number' || (schema.type==='integer'&&!Number.isInteger(value)) || value<(schema.minimum??-Infinity)||value>(schema.maximum??Infinity)) throw Error('Invalid numeric domain');
  } else if(schema.type==='string') {
    if(typeof value!=='string'||value.length<(schema.minLength??0)) throw Error('Missing text');
  } else if(schema.type==='boolean' && typeof value!=='boolean') throw Error('Invalid status');
  else if(schema.type && !['object','array','number','integer','string','boolean'].includes(schema.type)) throw Error('Unsupported schema type');
}
export async function digest(raw:Uint8Array):Promise<string> {
  const bytes=new Uint8Array(raw); // own ArrayBuffer for WebCrypto across TS lib versions
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
}
export async function checkedJSON(raw:Uint8Array,expected:string):Promise<unknown> {
  if(!/^[a-f0-9]{64}$/.test(expected)||await digest(raw)!==expected) throw Error('Export hash mismatch');
  return JSON.parse(new TextDecoder().decode(raw));
}
export async function loadBundle(fetcher:typeof fetch=fetch):Promise<Bundle> {
  async function bytes(name:string):Promise<Uint8Array> {
    const response=await fetcher(`/data/${name}`,{cache:'no-store'});
    if(!response.ok) throw Error(`Missing exported asset: ${name}`);
    return new Uint8Array(await response.arrayBuffer());
  }
  const receipt=JSON.parse(new TextDecoder().decode(await bytes('build_receipt.json'))) as Receipt;
  if(receipt.schema_version!==1 || !/^[a-f0-9]{40}$/.test(receipt.source_commit)||!receipt.payload_sha256||!receipt.adapter_sha256) throw Error('Unsupported build receipt');
  const manifestSchema=await checkedJSON(await bytes('manifest.schema.json'),receipt.adapter_sha256['course/site/schemas/manifest.schema.json']) as Schema;
  const dataSchema=await checkedJSON(await bytes('dataset.schema.json'),receipt.adapter_sha256['course/site/schemas/dataset.schema.json']) as Schema;
  const manifest=await checkedJSON(await bytes('manifest.json'),receipt.manifest_sha256) as Manifest;
  validate(manifest,manifestSchema);
  const [unary,binary,boundary]=await Promise.all(['unary','binary','boundary'].map(async panel=>{
    const dataset=await checkedJSON(await bytes(`${panel}.json`),receipt.payload_sha256[`${panel}.json`]) as UnaryData|BinaryData|BoundaryData;
    validate(dataset,dataSchema);
    if(dataset.panel_id!==panel||dataset.records.some((r,i)=>r.id!==`${panel}-${String(i).padStart(3,'0')}`)) throw Error(`Wrong ${panel} row IDs/order`);
    return dataset;
  }));
  return {manifest,receipt,unary:unary as UnaryData,binary:binary as BinaryData,boundary:boundary as BoundaryData};
}
export function selectRecord<T extends {id:string}>(records:T[],id:string):T {
  const row=records.find(r=>r.id===id);
  if(!row) throw Error('Choose an exact exported row ID');
  return row;
}
export function sourceURL(commit:string,path:string):string {
  if(!/^[a-f0-9]{40}$/.test(commit)||!/^course\/[A-Za-z0-9_./-]+$/.test(path)||path.includes('..')) throw Error('Invalid source reference');
  return fileURL(REPO_FILE_REF ?? commit,path);
}
