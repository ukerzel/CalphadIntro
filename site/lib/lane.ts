/** Which background the learner chose on the advanced steps (materials science or operations research). It changes only which boxes open by default, never content or completion. */
import { createContext } from 'react';

export type Lane = 'M' | 'O' | null;
export const LaneContext = createContext<{ lane: Lane; setLane: (lane: Lane) => void }>({ lane: null, setLane: () => {} });

/** A reveal opens by default when it belongs to the learner's lane. */
export const opensFor = (lane: Lane, kind: string) => (lane === 'M' && kind === 'lane-m') || (lane === 'O' && (kind === 'lane-o' || kind === 'deeper-or'));
