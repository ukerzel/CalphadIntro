'use client';
import { BookOpen } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from '@/components/ui/sheet';
import LearningPage from '@/components/learning-page';
import { lesson } from '@/lib/learning';

/** The Start-here refresher, available beside every step without leaving it. */
export default function ReferenceDrawer({ onOpenPage }: { onOpenPage: () => void }) {
  const start = lesson('start');
  return <Sheet>
    <SheetTrigger className="nav-button" aria-label="Energy and terms reference"><BookOpen aria-hidden /><span>Energy and terms reference</span></SheetTrigger>
    <SheetContent className="reference-sheet">
      <SheetHeader><SheetTitle>{start.title}</SheetTitle><SheetDescription>Quantities, potentials and a glossary, beside your current step.</SheetDescription></SheetHeader>
      <div className="reference-body"><LearningPage lesson={start} variant="reference" /><button type="button" className="button-secondary" onClick={onOpenPage}>Open as a full page</button></div>
    </SheetContent>
  </Sheet>;
}
