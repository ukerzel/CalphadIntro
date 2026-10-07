'use client';
import { createContext, useContext, useRef, useState } from 'react';
import type { MouseEvent, PointerEvent, ReactNode } from 'react';
import { Popover } from 'radix-ui';
import { ArrowUpRight } from 'lucide-react';
import { describe, parseTarget } from '@/lib/xref';
import { routeHash } from '@/lib/route';
import type { Route } from '@/lib/route';

/** Provided by the app shell: follow a route and remember where the learner came from. */
export const FollowContext = createContext<(route: Route, from: string) => void>(route => { location.hash = routeHash(route); });

/** Where a link sits, for the "Back to …" chip: the step number and the stage heading around it. */
function origin(node: Element): string {
  const stage = node.closest('section.stage')?.querySelector('h2')?.textContent ?? '';
  const step = document.querySelector('.lesson-number')?.textContent ?? '';
  return [step, stage].filter(Boolean).join(' · ') || 'where you were';
}

/** A cross-reference: hover, focus or tap shows what is there; the button goes there. */
export default function XRef({ target, shown, render }: { target: string; shown: string; render: (text: string) => ReactNode }) {
  const follow = useContext(FollowContext), [open, setOpen] = useState(false), timer = useRef(0), trigger = useRef<HTMLButtonElement>(null), hovered = useRef(false);
  const parsed = parseTarget(target), info = parsed ? describe(parsed) : null;
  if (!info) return <>{shown}</>;
  const enter = (event: PointerEvent) => { if (event.pointerType !== 'mouse') return; window.clearTimeout(timer.current); if (!open) hovered.current = true; setOpen(true); };
  const leave = (event: PointerEvent) => { if (event.pointerType !== 'mouse') return; timer.current = window.setTimeout(() => { hovered.current = false; setOpen(false); }, 160); };
  const click = (event: MouseEvent) => { if (hovered.current && open) { event.preventDefault(); hovered.current = false; } };
  const go = (event: MouseEvent) => { event.preventDefault(); const from = trigger.current ? origin(trigger.current) : ''; setOpen(false); follow(info.route, from); };
  return <Popover.Root open={open} onOpenChange={setOpen}>
    <Popover.Trigger asChild><button ref={trigger} type="button" className={`xref xref-${parsed!.kind}`} data-xref={target} onPointerEnter={enter} onPointerLeave={leave} onClick={click}>
      {shown}<ArrowUpRight className="xref-mark" aria-hidden /><span className="sr-only"> (cross-reference: {info.title})</span>
    </button></Popover.Trigger>
    <Popover.Portal><Popover.Content className="term-pop xref-pop" sideOffset={6} collisionPadding={12} onPointerEnter={enter} onPointerLeave={leave} onOpenAutoFocus={event => { if (hovered.current) event.preventDefault(); }}>
      <p className="xref-title">{info.title}</p>
      {info.rich ? <p>{render(info.rich)}</p> : info.excerpt && <p className="xref-excerpt">{info.excerpt}</p>}
      <a className="xref-go" href={routeHash(info.route)} onClick={go}>{info.action}<ArrowUpRight aria-hidden /></a>
      <Popover.Arrow className="term-arrow" />
    </Popover.Content></Popover.Portal>
  </Popover.Root>;
}
