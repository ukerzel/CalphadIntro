'use client';
import { Slider as Primitive } from 'radix-ui';
/** Compose the installed Radix primitive: the catalog wrapper cannot pass
 * name/readout attributes to its actual Thumb. Keep vendor source unchanged. */
export default function RecordSlider({index,max,onChange,labelId,valueText}:{index:number;max:number;onChange:(index:number)=>void;labelId:string;valueText:string}) {
  return <Primitive.Root className="record-slider" value={[index]} min={0} max={max} step={1} onValueChange={v=>onChange(v[0])}>
    <Primitive.Track className="record-track"><Primitive.Range className="record-range"/></Primitive.Track>
    <Primitive.Thumb className="record-thumb" aria-labelledby={labelId} aria-valuetext={valueText}/>
  </Primitive.Root>;
}
