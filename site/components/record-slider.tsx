'use client';
import { Slider as Primitive } from 'radix-ui';
/** The one slider of every lab. Compose the installed Radix primitive: the catalog wrapper cannot pass
 * name/readout attributes to its actual Thumb. Keep vendor source unchanged. */
export function ValueSlider({value,min,max,step,onChange,labelId,valueText}:{value:number;min:number;max:number;step:number;onChange:(value:number)=>void;labelId:string;valueText:string}) {
  return <Primitive.Root className="record-slider" value={[value]} min={min} max={max} step={step} onValueChange={v=>onChange(v[0])}>
    <Primitive.Track className="record-track"><Primitive.Range className="record-range"/></Primitive.Track>
    <Primitive.Thumb className="record-thumb" aria-labelledby={labelId} aria-valuetext={valueText}/>
  </Primitive.Root>;
}
/** A slider over saved records: whole indices 0 … max. */
export default function RecordSlider({index,max,onChange,labelId,valueText}:{index:number;max:number;onChange:(index:number)=>void;labelId:string;valueText:string}) {
  return <ValueSlider value={index} min={0} max={max} step={1} onChange={onChange} labelId={labelId} valueText={valueText}/>;
}
