'use client';
import { FileCheck2 } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from '@/components/ui/sheet';
import { OMITTED_SOURCES, dataVersion, sourceURL } from '@/lib/data';
import type { Bundle, Panel } from '@/lib/data';
export default function SourceDrawer({ bundle, panel }: { bundle: Bundle; panel: Panel }) {
  return <Sheet><SheetTrigger className="source-button"><FileCheck2 aria-hidden />About this data</SheetTrigger><SheetContent className="source-sheet"><SheetHeader><SheetTitle>About this data</SheetTitle><SheetDescription>Invented teaching model, calculated in advance in the course repository.</SheetDescription></SheetHeader>
    <div className="source-body"><p>{panel.limitations}</p><p>The lab shows the saved results; nothing is recalculated in your browser. <a href={`/data/${panel.id}.json`}>Download the data file</a> for full precision.</p><p>Data version <code>{dataVersion(bundle.receipt)}</code></p><p>Code and notes that produced it:</p><ul>{panel.source_paths.filter(path => !OMITTED_SOURCES.includes(path)).map(path => <li key={path}><a href={sourceURL(bundle.receipt.source_commit, path)}>{path.split('/').at(-1)}</a></li>)}</ul></div>
  </SheetContent></Sheet>;
}
