'use client';
import { useRef, useState } from 'react';
import type { MouseEvent, PointerEvent } from 'react';
import { Popover } from 'radix-ui';
import { terms } from '@/lib/learning';

/** "μ_A" → μ with subscript A; symbols are italic, phase names upright. */
function Shown({ text, italic }: { text: string; italic: boolean }) {
  const cut = text.indexOf('_'), base = cut > 0 ? text.slice(0, cut) : text, sub = cut > 0 ? text.slice(cut + 1) : '';
  return <>{italic ? <var>{base}</var> : base}{sub && <sub>{sub}</sub>}</>;
}

/** A marked symbol or name: opens its meaning on hover, focus, click or tap. */
export default function Term({ id, shown }: { id: string; shown: string }) {
  const term = terms[id], [open, setOpen] = useState(false), timer = useRef(0), hovered = useRef(false);
  if (!term) return <>{shown}</>;
  const enter = (event: PointerEvent) => { if (event.pointerType !== 'mouse') return; window.clearTimeout(timer.current); if (!open) hovered.current = true; setOpen(true); };
  const leave = (event: PointerEvent) => { if (event.pointerType !== 'mouse') return; timer.current = window.setTimeout(() => { hovered.current = false; setOpen(false); }, 160); };
  // A click right after a hover-open keeps the note open instead of toggling it shut.
  const click = (event: MouseEvent) => { if (hovered.current && open) { event.preventDefault(); hovered.current = false; } };
  return <Popover.Root open={open} onOpenChange={setOpen}>
    <Popover.Trigger asChild><button type="button" className={`term term-${term.kind}`} data-term={id} onPointerEnter={enter} onPointerLeave={leave} onClick={click}>
      {term.kind === 'symbol' ? <Shown text={shown} italic /> : shown}<span className="term-mark" aria-hidden>°</span><span className="sr-only"> (meaning)</span>
    </button></Popover.Trigger>
    <Popover.Portal><Popover.Content className="term-pop" sideOffset={6} collisionPadding={12} onPointerEnter={enter} onPointerLeave={leave} onOpenAutoFocus={event => { if (hovered.current) event.preventDefault(); }}>
      <p className="term-symbol">{term.symbol}</p><p>{term.meaning}</p>
      {term.elsewhere && <p className="term-else"><strong>Elsewhere:</strong> {term.elsewhere}</p>}
      <Popover.Arrow className="term-arrow" />
    </Popover.Content></Popover.Portal>
  </Popover.Root>;
}
