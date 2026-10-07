import type { ReactNode } from 'react';
import Tex from '@/components/math';

/** Typeset relation restated from the course narration; display only, never evaluated. */
export function Eq({ label, tex, children }: { label: string; tex?: string; children?: ReactNode }) {
  return <figure className="eq"><figcaption>{label}</figcaption>{tex ? <div className="eq-body"><Tex tex={tex} display /></div> : <p className="eq-body">{children}</p>}</figure>;
}
export function V({ children }: { children: ReactNode }) {
  return <var>{children}</var>;
}
