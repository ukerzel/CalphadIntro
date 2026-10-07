/** Optional browser-native state selection; no thermodynamic calculation. */
import type { Bundle,View } from './data';
export type Selection = {view:View;index:number;recordId:string};
export type ModelContext = {registerTool:(tool:{name:string;title:string;description:string;inputSchema:object;annotations:{readOnlyHint:boolean;untrustedContentHint:boolean};execute:(input:unknown)=>unknown},options:{signal:AbortSignal})=>void|Promise<void>};
export function checkedSelection(bundle:Bundle,input:unknown):Selection {
  if(!input||typeof input!=='object'||Array.isArray(input)) throw Error('Expected view and exact recordId');
  const object=input as Record<string,unknown>;
  if(Object.keys(object).length!==2||typeof object.view!=='string'||!['unary','binary','boundary'].includes(object.view)||typeof object.recordId!=='string') throw Error('Expected view and exact recordId');
  const view=object.view as View, records=bundle[view].records;
  const index=records.findIndex(r=>r.id===object.recordId);
  if(index<0) throw Error('Unknown exported recordId for this view');
  return {view,index,recordId:object.recordId};
}
export function registerSelection(context:ModelContext|undefined,bundle:Bundle,select:(s:Selection)=>void,onError:(error:unknown)=>void=console.error):()=>void {
  if(!context?.registerTool) return ()=>{};
  const lifecycle=new AbortController();
  try {
    void Promise.resolve(context.registerTool({
      name:'select_exported_row',title:'Select an exported teaching state',
      description:'Change the visible view and selected row. Use an exact exported record ID; no science is calculated.',
      inputSchema:{type:'object',properties:{view:{type:'string',enum:['unary','binary','boundary']},recordId:{type:'string'}},required:['view','recordId'],additionalProperties:false},
      annotations:{readOnlyHint:false,untrustedContentHint:false},
      execute(input:unknown){const selection=checkedSelection(bundle,input);select(selection);return {view:selection.view,recordId:selection.recordId};},
    },{signal:lifecycle.signal})).catch(onError);
  } catch(error) {onError(error);}
  return ()=>lifecycle.abort();
}
