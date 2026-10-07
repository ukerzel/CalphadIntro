'use client';
import { useState } from 'react';
import LabFrame, { Readout, RecordView } from '@/components/lab-frame';
import { Eq } from '@/components/equation';
import { num } from '@/lib/format';

const TRY_IT = { U: 1498, T: 300, S: 4, p: 100000, V: 0.00002 };

/** Definitions applied to the learner's own inputs (the step 00 Try-it state); not a material calculation. */
export default function EnergyLadder() {
  const [s, setS] = useState(TRY_IT);
  const set = (key: keyof typeof TRY_IT) => (value: number) => setS(previous => ({ ...previous, [key]: value }));
  const pV = s.p * s.V, TS = s.T * s.S, H = s.U + pV, F = s.U - TS, G = H - TS;
  const values = [s.U, H, F, G, 0], lo = Math.min(...values), hi = Math.max(...values), span = hi - lo || 1;
  const X = (v: number) => 92 + (v - lo) / span * 360;
  const bars: [string, number, string][] = [['U', s.U, 'internal energy'], ['H = U + pV', H, 'enthalpy'], ['F = U − TS', F, 'Helmholtz energy'], ['G = H − TS', G, 'Gibbs energy']];
  const sliders: [keyof typeof TRY_IT, string, number, number, number, (v: number) => string][] = [
    ['U', 'Internal energy U (J)', 0, 3000, 1, v => num(v, 0)],
    ['T', 'Temperature T (K)', 0, 1000, 1, v => num(v, 0)],
    ['S', 'Entropy S (J/K)', 0, 10, 0.01, v => num(v, 2)],
    ['p', 'Pressure p (Pa)', 0, 1000000, 1000, v => num(v, 0)],
    ['V', 'Volume V (m³)', 0, 0.03, 0.00001, v => v.toExponential(2)],
  ];
  const explore = <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>How to read it:</strong> each bar starts at zero. H adds the pV term to U; F subtracts TS from U; G subtracts TS from H. For a solid the pV term is tiny, so G and F are almost equal; try the gas-like volume.</p>
      <svg className="ladder" viewBox="0 0 540 210" role="img" aria-label={`U ${num(s.U)}, H ${num(H)}, F ${num(F)}, G ${num(G)} joules`}>
        <line className="ladder-zero" x1={X(0)} x2={X(0)} y1="8" y2="190" />
        {bars.map(([label, v, name], i) => <g key={label} transform={`translate(0, ${16 + i * 46})`}>
          <text className="ladder-label" x="84" y="16" textAnchor="end">{label.split(' ')[0]}</text>
          <text className="ladder-name" x="84" y="30" textAnchor="end">{name}</text>
          <rect className={`ladder-bar bar-${i}`} x={Math.min(X(0), X(v))} width={Math.max(1, Math.abs(X(v) - X(0)))} y="4" height="24" rx="4" />
          <text className="ladder-value" x={Math.max(X(0), X(v)) + 6} y="21">{num(v, 1)} J</text>
        </g>)}
      </svg>
      <div className="control-bar slider-stack">
        {sliders.map(([key, label, min, max, step, show]) => <label key={key} className="range-row">
          <span>{label}</span>
          <input type="range" min={min} max={max} step={step} value={s[key]} onChange={event => set(key)(Number(event.target.value))} />
          <strong>{show(s[key])}</strong>
        </label>)}
        <div className="control-row">
          <button type="button" className="ghost-button" onClick={() => setS(TRY_IT)}>Try-it state (a solid)</button>
          <button type="button" className="ghost-button" onClick={() => setS({ ...s, T: 300, p: 100000, V: 0.02494 })}>Gas-like volume (1 mol, 300 K, 1 bar)</button>
        </div>
      </div>
    </div>
    <aside className="lab-side">
      <p className="lab-kicker">Your state</p>
      <dl className="readouts">
        <Readout label="pV" value={num(pV, 2)} unit="J" />
        <Readout label="TS" value={num(TS, 2)} unit="J" />
        <Readout label="G − F (equals pV)" value={num(G - F, 2)} unit="J" tone="min" />
      </dl>
      <div className="notice"><h3>Which one is minimised?</h3><p>That depends on what is held fixed, not on which number is smallest: see the four sketches in the refresher. In this course, fixed T and p, so G.</p></div>
    </aside>
  </div>;
  const model = <div className="model"><div className="equations">
    <Eq label="Enthalpy" tex={String.raw`H = U + pV`} />
    <Eq label="Helmholtz energy" tex={String.raw`F = U - TS`} />
    <Eq label="Gibbs energy" tex={String.raw`G = H - TS = F + pV`} />
  </div><p>These are definitions applied to the numbers you set; nothing here is a material calculation.</p></div>;
  return <LabFrame kicker="Step 00 · energy ladder" title="U, H, F and G side by side" conditions={['your own inputs', 'start: the Try-it state']}
    explore={explore} model={model} record={<RecordView value={{ ...s, pV, TS, H, F, G }} href="#/start" note="Your current inputs and the resulting values." />} />;
}
