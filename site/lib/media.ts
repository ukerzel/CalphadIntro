/** Videos hosted elsewhere (kept out of Git). Change the address here to move a video, e.g. from unlisted to public. */
import type { LearningID } from '@/lib/learning';

export type Video = { youtube: string; title: string };
export const overviewVideo: Video = { youtube: '2bX2GEzmYt8', title: 'CALPHAD School 2026: the course in one overview' };
/** Short videos per step, each at the top of one stage (the stage key from stages(); 'overview' is the step's opening). */
export const stepVideos: Partial<Record<LearningID, { stage: string; video: Video }[]>> = {
  unary: [{ stage: 'overview', video: { youtube: 'YfHRqN7KvLs', title: 'Lowest g wins' } }],
  binary: [{ stage: 'overview', video: { youtube: 'zF9x6_FcRA0', title: 'The tangent and chemical potentials' } }],
  twophase: [
    { stage: 'overview', video: { youtube: 'dBCCNOvOBmE', title: 'From the tangent to the lens' } },
    { stage: 'part-b-one-phase-model-two-phases', video: { youtube: '1hCD0P53HFo', title: 'The bump: one phase model, two phases' } },
  ],
  boundary: [{ stage: 'overview', video: { youtube: 'dnz_o-Z14_s', title: 'Open or closed boundary' } }],
  cuni: [{ stage: 'overview', video: { youtube: 'Yg1gyknRGhw', title: 'From a database file to a diagram' } }],
  ninb: [{ stage: 'overview', video: { youtube: 'yl4ByNCSW7c', title: 'Sublattices in Ni–Nb' } }],
  menu: [{ stage: 'overview', video: { youtube: '5Tw4s7Co4zQ', title: 'Equilibrium as a menu' } }],
  bounds: [{ stage: 'overview', video: { youtube: 'ZvMAIgCP4ks', title: 'Ceiling, floor and branch-and-bound' } }],
};
export const youtubeWatch = (id: string) => `https://youtu.be/${id}`;
/** youtube-nocookie and loaded only after a click: nothing reaches Google before the learner asks for the video. */
export const youtubeEmbed = (id: string) => `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
