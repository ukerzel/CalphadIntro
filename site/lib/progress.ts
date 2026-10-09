/** "Remember my place": an explicit opt-in. Until the learner ticks it, nothing about the visit is stored.
 *  When on, the visited steps and the last step are kept in this browser's localStorage only: no cookies,
 *  nothing sent anywhere, and "Forget" removes it. (Theme and background are stored only when chosen.) */
import { lessons } from './learning';
import type { LearningID } from './learning';

const ON = 'calphad-remember', VISITED = 'calphad-visited', LAST = 'calphad-last';
export type Progress = { on: boolean; visited: LearningID[]; last: LearningID | null };
const known = (id: unknown): id is LearningID => typeof id === 'string' && lessons.some(item => item.id === id);

export function loadProgress(): Progress {
  try {
    if (localStorage.getItem(ON) !== '1') { localStorage.removeItem(LAST); return { on: false, visited: [], last: null }; }   // an earlier automatic "last step" is dropped
    const visited = (JSON.parse(localStorage.getItem(VISITED) ?? '[]') as unknown[]).filter(known);
    const last = localStorage.getItem(LAST);
    return { on: true, visited, last: known(last) ? last : null };
  } catch { return { on: false, visited: [], last: null }; }
}

export function setRemember(on: boolean, current: LearningID | null): Progress {
  try {
    if (!on) { [ON, VISITED, LAST].forEach(key => localStorage.removeItem(key)); return { on: false, visited: [], last: null }; }
    localStorage.setItem(ON, '1');
  } catch { return { on: false, visited: [], last: null }; }
  return current ? markVisited(current) : loadProgress();
}

export function markVisited(id: LearningID): Progress {
  const now = loadProgress();
  if (!now.on) return now;
  const visited = now.visited.includes(id) ? now.visited : [...now.visited, id];
  try { localStorage.setItem(VISITED, JSON.stringify(visited)); localStorage.setItem(LAST, id); } catch { /* storage full or blocked */ }
  return { on: true, visited, last: id };
}
