'use client';
/** "Route map" in the header: the whole map in a wide sheet, from any page. Choosing a destination closes it. */
import { useState } from 'react';
import type { ComponentProps } from 'react';
import { Map as MapIcon } from 'lucide-react';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import RouteMap from '@/components/route-map';

export default function RouteMapDrawer(props: Omit<ComponentProps<typeof RouteMap>, 'onNavigate'>) {
  const [open, setOpen] = useState(false);
  return <Sheet open={open} onOpenChange={setOpen}>
    <SheetTrigger className="nav-button" aria-label="Route map: the main line, its branches, labs and notebooks"><MapIcon aria-hidden /><span>Route map</span></SheetTrigger>
    <SheetContent className="reference-sheet map-sheet">
      <SheetHeader><SheetTitle>Route map</SheetTitle>
        <SheetDescription>The main line runs from step 00 to step 17. Dashed branches are optional or for another background, and come back to the main line.</SheetDescription></SheetHeader>
      <div className="reference-body">{open && <RouteMap {...props} onNavigate={() => setOpen(false)} />}</div>
    </SheetContent>
  </Sheet>;
}
