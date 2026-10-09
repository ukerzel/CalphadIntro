'use client';
/** The optional LP primer: dots and chords, the search one swap at a time, moving the target, and the textbook polygon. */
import { useEffect, useState } from 'react';
import Plot, { path } from '@/components/plot';
import LabFrame, { LiveStatus, Readout, RecordView, Segmented, Stepper } from '@/components/lab-frame';
import RecordSlider, { ValueSlider } from '@/components/record-slider';
import { loadLearningJSON } from '@/lib/materials';
import { fixed } from '@/lib/format';
import { bestOfBasket, height, through } from '@/lib/day3';
import { asDots, cornerCost, lpPrimerPath, rawLever } from '@/lib/lp-primer';
import type { Corner, LpPrimerData, Rule } from '@/lib/lp-primer';

export type LpView = 'chords' | 'swap' | 'nudge' | 'polygon';
export const lpViews: LpView[] = ['chords', 'swap', 'nudge', 'polygon'];
type Blend = LpPrimerData['blend'];
type Poly = LpPrimerData['polygon'];

const euro = (value: number, digits = 2) => `€${fixed(value, digits)}`;
const Y: [number, number] = [6, 16.5];

export default function LpPrimerView({ initialView = 'chords', kicker }: { initialView?: LpView; kicker?: string }) {
  const [data, setData] = useState<LpPrimerData | null>(null), [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    loadLearningJSON<LpPrimerData>(lpPrimerPath).then(value => { if (active) setData(value); }).catch(e => { if (active) setError(String(e.message)); });
    return () => { active = false; };
  }, []);
  if (error) return <div className="notice" role="alert"><h3>Data unavailable</h3><p>{error}. Try reloading the page.</p></div>;
  if (!data) return <p className="loading" role="status">Loading the lab data…</p>;
  return <LpPrimerLab data={data} initialView={initialView} kicker={kicker} />;
}

export function LpPrimerLab({ data, initialView = 'chords', kicker = 'Interactive lab' }: { data: LpPrimerData; initialView?: LpView; kicker?: string }) {
  const [view, setView] = useState<LpView>(initialView);
  const blend = data.blend, poly = data.polygon;
  const body = view === 'chords' ? <Chords blend={blend} /> : view === 'swap' ? <Swap blend={blend} /> : view === 'nudge' ? <Nudge blend={blend} /> : <Polygon poly={poly} />;
  return <LabFrame kicker={kicker} title="Linear programmes: dots and corners"
    conditions={view === 'polygon' ? ['two lots', 'four rules', 'kg and €', 'invented prices'] : ['1 kg charge', `Ni content ${blend.target.toFixed(2)}`, 'six lots', 'invented prices']}
    actions={<Segmented label="Lab view" value={view} onChange={setView}
      options={[['chords', 'Dots and chords'], ['swap', 'One swap'], ['nudge', 'Move the target'], ['polygon', 'Textbook picture']]} />}
    explore={<div id={`lab-${view}`}>{body}</div>}
    model={<div className="model-notes">
      <p>An invented melt shop: six lots of scrap with a nickel content (kg Ni per kg) and a price (€ per kg). Prices, contents and caps are made up for the exercise; they are not market data. Every best charge, search round, price and corner was calculated in advance with the course code and SciPy&apos;s linprog.</p>
      <p>What the lab does itself is arithmetic on those numbers: the lever rule on two lots, the height of a straight line, and price times amount at a corner.</p>
    </div>}
    record={<RecordView value={{ lots: blend.lots, best: blend.best, prices: blend.prices, polygon_optimum: poly.optimum }} href="/learning/self_study/generated/lp_primer.json" note="The numbers behind these views." />} />;
}

/** Lots as dots: blue, used ones ringed, the dealer's offer orange. */
function Lots({ blend, x, y, used = [], bad = [], offer = false }: { blend: Blend; x: (v: number) => number; y: (v: number) => number; used?: number[]; bad?: number[]; offer?: boolean }) {
  return <>
    {blend.lots.map((lot, i) => <g key={lot.short}><circle className={`dot dot-solid ${used.includes(i) ? 'is-chosen' : ''} ${bad.includes(i) ? 'is-bad' : ''}`} cx={x(lot.w)} cy={y(lot.price)} r={used.includes(i) ? 8 : 6} />
      <text className="dot-label" x={x(lot.w) + (lot.w > 0.9 ? -8 : 8)} y={y(lot.price) - 9} textAnchor={lot.w > 0.9 ? 'end' : 'start'}>{lot.short}</text></g>)}
    {offer && <g><circle className="dot dot-liquid is-chosen" cx={x(blend.offer.lot.w)} cy={y(blend.offer.lot.price)} r={7} /><text className="dot-label" x={x(blend.offer.lot.w) + 8} y={y(blend.offer.lot.price) + 16}>{blend.offer.lot.short}</text></g>}
  </>;
}

function Chords({ blend }: { blend: Blend }) {
  const [basket, setBasket] = useState<number[]>([]);
  const lots = blend.lots, z = blend.target, dots = asDots(lots);
  const toggle = (i: number) => setBasket(b => b.includes(i) ? b.filter(j => j !== i) : [...b, i]);
  const chosen = basket.map(i => dots[i]), best = chosen.length ? bestOfBasket(chosen, z) : null;
  const used = best ? best.used.map(i => basket[i]) : [];
  const pair = basket.length === 2 && !best ? rawLever(lots[basket[0]], lots[basket[1]], z) : null;
  const status = best ? `Cheapest charge from your basket: ${euro(best.G, 3)} per kg` : basket.length ? 'No valid amounts for this basket' : 'Basket empty';
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> tap lots to put them in your basket. The lab mixes 1 kg at 0.40 Ni in the cheapest way the basket allows: one lot below 0.40 and one above, by the lever rule. Which pair is cheapest of all? Try two lots on the same side, too.</p>
      <div className="legend" aria-hidden><span className="key key-solid">a lot of scrap</span><span className="key key-min">your charge</span></div>
      <Plot title="Six lots: price against nickel content" desc="Six scrap lots as dots; the chord between the chosen pair and the charge's cost at 0.40 Ni."
        height={380} xDomain={[0, 1]} yDomain={Y} xLabel="Ni content w (kg Ni per kg)" yLabel="price (€ per kg)"
        onPick={(px, py) => { const scores = lots.map(l => Math.hypot((l.w - px) * 10, (l.price - py) / 1.2)); toggle(scores.indexOf(Math.min(...scores))); }}>
        {({ x, y, top, bottom }) => <>
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          {used.length === 2 && <line className="tangent-solid" x1={x(lots[used[0]].w)} y1={y(lots[used[0]].price)} x2={x(lots[used[1]].w)} y2={y(lots[used[1]].price)} />}
          <Lots blend={blend} x={x} y={y} used={basket} />
          {best && <circle className="dot dot-min" cx={x(z)} cy={y(best.G)} r={7} />}
        </>}
      </Plot>
      <div className="control-bar">
        <div className="dot-picker" role="group" aria-label="Scrap lots">
          {lots.map((lot, i) => <button key={lot.short} type="button" className="dot-chip chip-solid" aria-pressed={basket.includes(i)} onClick={() => toggle(i)}>{lot.short} · {lot.w.toFixed(2)}</button>)}
        </div>
        <div className="control-row"><button type="button" className="ghost-button" onClick={() => setBasket([])}>Empty the basket</button></div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={status} />
      <p className="lab-kicker">Your basket</p>
      <p className="big-number">{basket.length} {basket.length === 1 ? 'lot' : 'lots'}</p>
      {basket.length > 0 && !best && <p className="status-pill pill-warn">No valid amounts: the basket needs a lot below 0.40 and one above</p>}
      {pair && <p className="caption">The lever rule would ask for {fixed(pair[0], 2)} kg {lots[basket[0]].short} and {fixed(pair[1], 2)} kg {lots[basket[1]].short}: a negative amount, which cannot be bought.</p>}
      <dl className="readouts">
        {best && <Readout label="Cost of 1 kg at 0.40 Ni" value={euro(best.G, 3)} unit="per kg" tone="min" />}
        {best && used.map((i, k) => <Readout key={i} label={lots[i].name} value={fixed(best.f[k], 3)} unit="kg" tone="solid" />)}
        <Readout label="Pairs that can make 0.40" value={blend.pairs_tried} unit="of 15 pairs" />
        {best && <Readout label="Compared with every pair" value={best.G - blend.best.cost < 1e-9 ? 'cheapest of all' : 'a cheaper pair exists'} unit="" />}
      </dl>
    </aside>
  </div>;
}

function Swap({ blend }: { blend: Blend }) {
  const frames = blend.swap.frames, [k, setK] = useState(0), [offer, setOffer] = useState(false);
  const frame = frames[k], last = k === frames.length - 1, lots = blend.lots, z = blend.target;
  const below = frame.gaps.flatMap((g, i) => g < -1e-9 ? [i] : []);
  const caption = last && offer ? `The ${blend.offer.lot.short.toLowerCase()} lies ${fixed(-blend.offer.gap, 2)} € below the line: this list is finished, but a new candidate would improve it (${euro(blend.offer.best.cost)}).`
    : last ? 'No lot lies below the line: the search stops. The line is a floor for every charge, and this charge reaches it.'
    : `${lots[frame.enter!].short} lies ${fixed(-frame.gaps[frame.enter!] + 1e-9, 2)} € below the line: it comes in, ${lots[frame.leave!].short} (same side of 0.40) goes out.`;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> the search starts from copper scrap and nickel cathode. Before each step, predict which lot comes in and which goes out. Every lot below the line is cheaper than the line offers at its content.</p>
      <div className="legend" aria-hidden><span className="key key-solid">a lot</span><span className="key key-min">line through the used pair</span><span className="key key-liquid">below the line</span></div>
      <Plot title="The search, one swap at a time" desc="Six lots, the line through the used pair, and the vertical distance of every lot below that line."
        height={380} xDomain={[0, 1]} yDomain={Y} xLabel="Ni content w (kg Ni per kg)" yLabel="price (€ per kg)">
        {({ x, y, top, bottom }) => <>
          <line className="cursor" x1={x(z)} x2={x(z)} y1={top} y2={bottom} />
          <line className="learner-line" x1={x(0)} y1={y(frame.line.base)} x2={x(1)} y2={y(frame.line.top)} />
          {below.map(i => <line key={i} className="df-arrow" x1={x(lots[i].w)} x2={x(lots[i].w)} y1={y(lots[i].price)} y2={y(height(frame.line.base, frame.line.slope, lots[i].w))} />)}
          {last && offer && <line className="df-arrow" x1={x(blend.offer.lot.w)} x2={x(blend.offer.lot.w)} y1={y(blend.offer.lot.price)} y2={y(blend.offer.line_height)} />}
          <Lots blend={blend} x={x} y={y} used={frame.used} bad={below} offer={last && offer} />
          <circle className="dot dot-min" cx={x(z)} cy={y(frame.cost)} r={7} />
          <text className="edge-flag" x={x(0) + 6} y={y(frame.line.base) + 18}>{euro(frame.line.base)}</text>
          <text className="edge-flag" x={x(1) - 6} y={y(frame.line.top) - 8} textAnchor="end">{euro(frame.line.top)}</text>
        </>}
      </Plot>
      <div className="control-bar"><div className="control-row">
        <Stepper index={k} count={frames.length} onChange={setK} unit="round" label="Rounds of the search" />
        <span className="caption">{caption}</span>
        {last && <label className="check"><input type="checkbox" checked={offer} onChange={e => setOffer(e.target.checked)} /> Show the dealer&apos;s offer</label>}
      </div></div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={`Round ${k + 1}: ${caption}`} />
      <p className="lab-kicker">Round {k + 1} of {frames.length}</p>
      <p className="big-number">{euro(frame.cost, 3)}</p>
      <p className="caption">{frame.used.map((i, j) => `${fixed(frame.f[j], 3)} kg ${lots[i].short}`).join(' + ')}</p>
      <dl className="readouts">
        {lots.map((lot, i) => <Readout key={lot.short} label={`${lot.short}: price minus line`} value={fixed(frame.gaps[i], 3)} unit="€ per kg" tone={frame.gaps[i] < -1e-9 ? 'liquid' : undefined} />)}
        {last && <Readout label="Worth of 1 kg Cu, 1 kg Ni" value={`${euro(blend.prices.cu)}, ${euro(blend.prices.ni)}`} unit="the line's ends" tone="min" />}
        {last && offer && <Readout label={`${blend.offer.lot.short} at ${blend.offer.lot.w.toFixed(2)}: price minus line`} value={fixed(blend.offer.gap, 3)} unit={`€; new best ${euro(blend.offer.best.cost)}`} tone="liquid" />}
      </dl>
    </aside>
  </div>;
}

function Nudge({ blend }: { blend: Blend }) {
  const frames = blend.targets, start = frames.findIndex(f => Math.abs(f.z - blend.target) < 1e-9);
  const [i, setI] = useState(start), frame = frames[i], lots = blend.lots, dots = asDots(lots);
  const hull = blend.hull.map(k => lots[k]);
  const line = frame.used.length === 2 ? through(dots[frame.used[0]], dots[frame.used[1]]) : null;
  const side = (s: number | null, where: string) => s === null ? `no charge exists to the ${where}` : `the price is ${fixed(s, 2)} to the ${where}`;
  const status = frame.slopes ? `At ${frame.z.toFixed(2)} the target sits on a lot: ${side(frame.slopes[0], 'left')} and ${side(frame.slopes[1], 'right')}.`
    : `Price of nickel content: ${fixed(frame.slope!, 2)} € per unit, while ${frame.used.map(k => lots[k].short).join(' and ')} stay in use.`;
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> move the target content. The dashed curve is the cheapest charge for every target: it bends only at lots. Its slope is the price of nickel content. Where does the price stay the same, and where does it jump?</p>
      <div className="legend" aria-hidden><span className="key key-solid">a lot</span><span className="key key-min">cheapest charge</span><span className="key key-diag">cheapest cost for every target</span></div>
      <Plot title="Cheapest cost against the target content" desc="Six lots, the lowest chord under them for every target, and the current charge with its price line."
        height={380} xDomain={[0, 1]} yDomain={Y} xLabel="target Ni content (kg Ni per kg)" yLabel="price (€ per kg)" onScrub={value => setI(Math.max(0, Math.min(frames.length - 1, Math.round(value * 100))))}>
        {({ x, y, top, bottom }) => <>
          <path className="tangent-ext" d={path(hull.map(l => [x(l.w), y(l.price)]))} />
          <line className="cursor" x1={x(frame.z)} x2={x(frame.z)} y1={top} y2={bottom} />
          {line && <line className="tangent" x1={x(0)} y1={y(line.mu_A)} x2={x(1)} y2={y(line.mu_A + line.d_mu)} />}
          <Lots blend={blend} x={x} y={y} used={frame.used} />
          <circle className="dot dot-min" cx={x(frame.z)} cy={y(frame.cost)} r={7} />
        </>}
      </Plot>
      <div className="control-bar">
        <label id="lp-target" className="control-label">Target Ni content <strong>{frame.z.toFixed(2)}</strong></label>
        <RecordSlider index={i} max={frames.length - 1} onChange={setI} labelId="lp-target" valueText={frame.z.toFixed(2)} />
        <div className="control-row"><button type="button" className="ghost-button" onClick={() => setI(start)}>Back to 0.40</button>
          <button type="button" className="ghost-button" onClick={() => setI(start + 1)}>Nudge to 0.41</button></div>
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={status} />
      <p className="lab-kicker">Target {frame.z.toFixed(2)}</p>
      <p className="big-number">{euro(frame.cost, 3)}</p>
      <p className="caption">{frame.used.map((k, j) => `${fixed(frame.f[j], 3)} kg ${lots[k].short}`).join(' + ')}</p>
      <p className={`status-pill ${frame.slopes ? 'pill-open' : 'pill-equal'}`}>{status}</p>
      <dl className="readouts">
        <Readout label="From 0.40 to 0.41" value={`+${euro(blend.nudge.change, 3)}`} unit={`= ${fixed(blend.prices.slope, 2)} × 0.01`} />
        <Readout label="Same price while the target is between" value={`${blend.prices.range[0].toFixed(2)} and ${blend.prices.range[1].toFixed(2)}`} unit="CuNi30 and Monel in use" />
      </dl>
    </aside>
  </div>;
}

const FP: [number, number] = [0, 1.7], FQ: [number, number] = [0, 0.8];

/** Two points of a rule's boundary line a·f = b, across the plot. */
function ruleEnds(a: [number, number], b: number): [[number, number], [number, number]] {
  if (Math.abs(a[1]) < 1e-12) return [[b / a[0], FQ[0]], [b / a[0], FQ[1]]];
  return [[FP[0], (b - a[0] * FP[0]) / a[1]], [FP[1], (b - a[0] * FP[1]) / a[1]]];
}
const ruleB = (rule: Rule, poly: Poly, cap: 'normal' | 'strict') => rule.id === 'fe' ? poly.fe_cap[cap] : rule.b!;

function Polygon({ poly }: { poly: Poly }) {
  const [priceQ, setPriceQ] = useState(poly.price_q.default), [cap, setCap] = useState<'normal' | 'strict'>('normal'), [exact, setExact] = useState(false);
  const [level, setLevel] = useState(10.5), [shown, setShown] = useState(false);
  const prices: [number, number] = [poly.lots[0].price, priceQ];
  const corners: Corner[] = exact ? (cap === 'normal' ? [{ f: poly.exact.f, tight: ['charge', 'ni'] }] : []) : poly.regions[cap];
  const costs = corners.map(c => cornerCost(prices, c.f)), min = costs.length ? Math.min(...costs) : null;
  const best = min === null ? [] : costs.flatMap((c, i) => c - min < 1e-9 ? [i] : []);
  const C = shown && min !== null ? min : level;
  const max = costs.length ? Math.max(...costs) : null;
  const reaches = min !== null && C >= min - 1e-9, beyond = max !== null && C > max + 1e-9;
  const status = !corners.length ? 'Infeasible: no charge keeps every rule.'
    : shown ? (best.length > 1 ? `A tie: the cost line lies along an edge, every charge on it costs ${euro(min!, 3)}.` : `Cheapest corner: ${fixed(corners[best[0]].f[0], 3)} kg CuNi30 and ${fixed(corners[best[0]].f[1], 3)} kg Monel, ${euro(min!, 3)}.`)
    : beyond ? `No allowed charge costs as much as ${euro(C)}; slide lower.` : reaches ? `Some allowed charges cost ${euro(C)}; slide lower.` : `No allowed charge costs as little as ${euro(C)}.`;
  const label: Record<string, string> = { charge: 'weight', ni: 'nickel', fe: 'iron', furnace: 'furnace', 'no-P': 'no CuNi30', 'no-Q': 'no Monel' };
  return <div className="lab-grid">
    <div className="lab-main">
      <p className="how-to"><strong>Try it:</strong> the shaded polygon holds every allowed charge of CuNi30 (<i>f</i><sub>P</sub>) and Monel (<i>f</i><sub>Q</sub>). Slide the cost line down until it is about to leave the polygon, and predict the corner before you press <em>Show the cheapest corner</em>. Then change the Monel price, make the iron cap strict, or make both tight rules exact.</p>
      <div className="legend" aria-hidden><span className="key key-solid">rule boundary</span><span className="key key-min">cost line</span><span className="key key-open">allowed charges</span></div>
      <Plot title="The textbook picture: allowed charges and a cost line" desc="Two amounts on the axes, four rule lines, the polygon of allowed charges and a straight line of equal cost."
        height={400} xDomain={FP} yDomain={FQ} xLabel="kg of CuNi30 scrap (fP)" yLabel="kg of Monel offcuts (fQ)">
        {({ x, y }) => <>
          {corners.length > 2 && <path className="lp-region" d={`${path(corners.map(c => [x(c.f[0]), y(c.f[1])]))}Z`} />}
          {poly.rules.map(rule => { const [p, q] = ruleEnds(rule.a, ruleB(rule, poly, cap)); const exactRule = exact && (rule.id === 'charge' || rule.id === 'ni');
            return <g key={rule.id}><line className={`lp-rule ${exactRule ? 'is-exact' : ''}`} x1={x(p[0])} y1={y(p[1])} x2={x(q[0])} y2={y(q[1])} /></g>; })}
          {poly.rules.map(rule => { const [p, q] = ruleEnds(rule.a, ruleB(rule, poly, cap)); const t = rule.id === 'furnace' || rule.id === 'charge' ? 0.12 : rule.id === 'fe' && cap === 'strict' ? 0.2 : 0.55;
            const lx = p[0] + (q[0] - p[0]) * t, ly = p[1] + (q[1] - p[1]) * t;
            const sign = exact && (rule.id === 'charge' || rule.id === 'ni') ? '=' : rule.sense === '>=' ? '≥' : '≤';
            return <text key={rule.id} className="dot-label" x={x(lx) + 4} y={y(ly) - 6}>{label[rule.id]} {sign} {fixed(ruleB(rule, poly, cap), 3)}</text>; })}
          <line className="learner-line" x1={x(0)} y1={y(C / prices[1])} x2={x(C / prices[0])} y2={y(0)} />
          {corners.map((c, i) => <circle key={i} className={`dot dot-solid ${shown && best.includes(i) ? 'is-chosen' : ''}`} cx={x(c.f[0])} cy={y(c.f[1])} r={shown && best.includes(i) ? 8 : 5} />)}
        </>}
      </Plot>
      <div className="control-bar">
        <label id="lp-level" className="control-label">Cost line <strong>{euro(C)}</strong></label>
        <ValueSlider value={C} min={7} max={14} step={0.01} onChange={v => { setShown(false); setLevel(v); }} labelId="lp-level" valueText={euro(C)} />
        <label id="lp-price" className="control-label">Monel price <strong>{euro(priceQ)} per kg</strong></label>
        <ValueSlider value={priceQ} min={poly.price_q.range[0]} max={poly.price_q.range[1]} step={0.1} onChange={setPriceQ} labelId="lp-price" valueText={`${euro(priceQ)} per kg`} />
        <div className="control-row">
          <button type="button" className="button-primary" onClick={() => setShown(true)}>Show the cheapest corner</button>
          <button type="button" className="ghost-button" onClick={() => setPriceQ(poly.price_q.default)}>Monel back to {euro(poly.price_q.default)}</button>
          <label className="check"><input type="checkbox" checked={cap === 'strict'} onChange={e => setCap(e.target.checked ? 'strict' : 'normal')} /> Strict iron cap, {fixed(poly.fe_cap.strict, 3)} kg</label>
          <label className="check"><input type="checkbox" checked={exact} onChange={e => setExact(e.target.checked)} /> Weight and nickel rules exact</label>
        </div>
        {!exact && cap === 'normal' && <p className="caption">Ties at a Monel price of {poly.ties.map(t => euro(t)).join(' and ')}: there the cost line lies along an edge.</p>}
      </div>
    </div>
    <aside className="lab-side">
      <LiveStatus text={status} />
      <p className="lab-kicker">{corners.length ? `${corners.length} ${corners.length === 1 ? 'allowed charge' : 'corners'}` : 'No allowed charge'}</p>
      <p className={`status-pill ${!corners.length ? 'pill-warn' : shown ? 'pill-equal' : 'pill-solid'}`}>{status}</p>
      <dl className="readouts">
        {corners.map((c, i) => <Readout key={i} label={`(${fixed(c.f[0], 3)}, ${fixed(c.f[1], 3)}) · ${c.tight.map(t => label[t]).join(', ')}`} value={shown ? euro(costs[i], 3) : '?'} unit="cost" tone={shown && best.includes(i) ? 'min' : undefined} />)}
        {shown && !exact && cap === 'normal' && priceQ === poly.price_q.default && <>
          <Readout label="Price of the weight rule" value={euro(poly.optimum.duals.charge)} unit="per kg" />
          <Readout label="Price of the nickel rule" value={euro(poly.optimum.duals.ni)} unit={`per kg Ni, for ${poly.optimum.ni_range[0].toFixed(2)}–${poly.optimum.ni_range[1].toFixed(2)} kg (above ${poly.optimum.ni_range[1].toFixed(2)} the iron cap takes over from the weight rule and the price jumps)`} />
          <Readout label="Iron and furnace rules" value={euro(poly.optimum.duals.fe)} unit="room to spare: price zero" />
        </>}
      </dl>
    </aside>
  </div>;
}
