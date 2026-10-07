'use client';
import { useState } from 'react';

const STEPS: [string, string, string][] = [
  ['Database', 'A TDB file: for every phase, the model and its fitted parameters.', 'Steps 05–06 (optional setup: you fetch the file yourself).'],
  ['Phase models', 'For each phase, Gibbs energy as a function of temperature and composition.', 'Invented in steps 01–04; assessed in steps 05–06.'],
  ['calculate', 'Evaluates one phase at the conditions you give, even if that phase is not stable.', 'Step 01 (the two branch energies); step 02 (one curve).'],
  ['equilibrium', 'Searches all allowed phases for the lowest total G that still contains the right amounts.', 'Step 01 (the lower branch), step 03 (common tangent), steps 05–06 (saved results).'],
  ['Phase diagram', 'Equilibrium repeated over a grid of temperatures and compositions.', 'Step 03 part B (miscibility gap), steps 05–06 (Cu–Ni, Ni–Nb).'],
];

/** Sketch of the CALPHAD chain; click a box for what it does and where you meet it. */
export function PipelineFigure() {
  const [open, setOpen] = useState(0);
  return <figure className="pipeline">
    <ol className="pipeline-row">{STEPS.map(([name], i) => <li key={name}>
      <button type="button" aria-pressed={open === i} onClick={() => setOpen(i)}>{name}</button>
    </li>)}</ol>
    <div className="pipeline-detail" aria-live="polite"><strong>{STEPS[open][0]}.</strong> {STEPS[open][1]} <span>Where you meet it: {STEPS[open][2]}</span></div>
    <figcaption>Sketch of the chain from database to phase diagram. Loading a database alone gives no equilibrium.</figcaption>
  </figure>;
}

const PARTS: [string, string][] = [
  ['PARAMETER G(DEMO,A;0)', 'Gibbs energy of the endmember with A on its site, in an invented phase DEMO; ;0 is the order of the term.'],
  ['298.15', 'Lowest temperature (K) at which the first expression applies.'],
  ['-1000+10*T;', 'First expression in J/mol, a function of T.'],
  ['2000 Y', 'Upper limit (K) of the first range; Y means another range follows.'],
  ['-3000+11*T;', 'Second expression, used above 2000 K.'],
  ['6000 N', 'Upper limit of the last range; N means no more ranges.'],
  ['REF0 !', 'Reference key for the source, then ! ends the entry.'],
];

/** An invented TDB parameter line, annotated part by part. Not taken from any database. */
export function TdbLineFigure() {
  const [open, setOpen] = useState(2);
  return <figure className="tdb-line">
    <p className="tdb-code" role="group" aria-label="Invented example database line">{PARTS.map(([text], i) => <button key={i} type="button" aria-pressed={open === i} onClick={() => setOpen(i)}>{text}</button>)}</p>
    <p className="pipeline-detail" aria-live="polite"><strong>{PARTS[open][0]}</strong>: {PARTS[open][1]}</p>
    <figcaption>Invented example line, not copied from any database. To evaluate at 1500 K you would use the first expression: −1000 + 10 × 1500 = 14000 J/mol.</figcaption>
  </figure>;
}
