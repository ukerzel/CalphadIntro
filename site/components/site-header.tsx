'use client';
import { DropdownMenu } from 'radix-ui';
import { ChevronDown, FlaskConical, Moon, Sun } from 'lucide-react';
import ReferenceDrawer from '@/components/reference-drawer';
import CardsDrawer from '@/components/cards-drawer';
import { lessons } from '@/lib/learning';
import type { LearningID } from '@/lib/learning';
import { isAdvanced, meta } from '@/lib/lesson-meta';
import type { ReactNode } from 'react';

export function Logo() {
  return <svg className="logo-mark" viewBox="0 0 32 32" aria-hidden><path d="M4 9 C 9 27, 22 27, 28 7" /><path className="logo-tangent" d="M2 22 L30 17" /><circle cx="14.6" cy="20" r="2.6" /></svg>;
}

export default function SiteHeader({ current, onHome, onLearn, onLab, theme, onTheme, map }: {
  current: LearningID | null; onHome: () => void; onLearn: (id: LearningID) => void; onLab: (id: LearningID) => void; theme: 'light' | 'dark'; onTheme: () => void; map?: ReactNode;
}) {
  return <header className="site-header">
    <a href="#/" className="brand" aria-label="CALPHAD course companion home" onClick={event => { event.preventDefault(); onHome(); }}><Logo /><span>CALPHAD <span>School 2026</span></span></a>
    <nav className="site-nav" aria-label="Site">
      {map}
      <DropdownMenu.Root>
        <DropdownMenu.Trigger className="nav-button" aria-label="Labs: open a lab directly"><FlaskConical aria-hidden /><span>Labs</span><ChevronDown aria-hidden className="chev" /></DropdownMenu.Trigger>
        <DropdownMenu.Portal><DropdownMenu.Content className="menu" align="end" sideOffset={8}>
          <DropdownMenu.Label className="menu-label">Open a lab directly</DropdownMenu.Label>
          {lessons.filter(item => meta[item.id].lab).map(item => <DropdownMenu.Item key={item.id} className="menu-item" onSelect={() => onLab(item.id)}>
            <span className="menu-number">{meta[item.id].number}</span><span><strong>{meta[item.id].labTitle}</strong><small>{meta[item.id].tag}{isAdvanced(item.id) ? ' · advanced' : ''}</small></span>
          </DropdownMenu.Item>)}
        </DropdownMenu.Content></DropdownMenu.Portal>
      </DropdownMenu.Root>
      {current && <CardsDrawer />}
      {current !== 'start' && <ReferenceDrawer onOpenPage={() => onLearn('start')} />}
      <button type="button" className="nav-button icon-only" onClick={onTheme} aria-label={theme === 'dark' ? 'Use light theme' : 'Use dark theme'}>{theme === 'dark' ? <Sun aria-hidden /> : <Moon aria-hidden />}</button>
    </nav>
  </header>;
}
