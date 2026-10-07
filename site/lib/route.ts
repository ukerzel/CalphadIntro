/** URL-addressable state: #/ · #/<lesson> · #/<lesson>/at/<anchor> · #/<lesson>/lab · #/<lesson>/lab/<exact record ID or view>. */
import type { LearningID } from './learning';

export const learningIDs: LearningID[] = ['start', 'unary', 'binary', 'twophase', 'boundary', 'cuni', 'ninb'];
export type Route = { page: 'home' } | { page: 'lesson'; id: LearningID; lab: boolean; recordId?: string; view?: string; anchor?: string };

export function parseRoute(hash: string): Route {
  const parts = hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  const id = parts[0] as LearningID | undefined;
  if (!id || !learningIDs.includes(id)) return { page: 'home' };
  const lab = parts[1] === 'lab';
  const recordId = lab && parts[2] && /^[a-z]+-\d{3}$/.test(parts[2]) ? parts[2] : undefined;
  const view = lab && parts[2] && /^[a-z][a-z-]*$/.test(parts[2]) ? parts[2] : undefined;
  const anchor = !lab && parts[1] === 'at' && parts[2] && /^[a-z0-9][a-z0-9-]*$/.test(parts[2]) ? parts[2] : undefined;
  return { page: 'lesson', id, lab, ...(recordId ? { recordId } : {}), ...(view ? { view } : {}), ...(anchor ? { anchor } : {}) };
}

export function routeHash(route: Route): string {
  if (route.page === 'home') return '#/';
  if (!route.lab) return `#/${route.id}${route.anchor ? `/at/${route.anchor}` : ''}`;
  return `#/${route.id}/lab${route.recordId ? `/${route.recordId}` : route.view ? `/${route.view}` : ''}`;
}

/** Exact exported row IDs only; anything else falls back to the view default. */
export function recordIndex(recordId: string | undefined, view: string, count: number): number | null {
  if (!recordId) return null;
  const match = new RegExp(`^${view}-(\\d{3})$`).exec(recordId);
  if (!match) return null;
  const index = Number(match[1]);
  return index < count ? index : null;
}
