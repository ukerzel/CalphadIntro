/** Saved author outputs for the material pages, verified against the content receipt. */
import { checkedJSON } from './data';

export type SamplePhase = { phase: string; atom_mole_fraction: number; x_NI?: number; x_NB?: number };
export type Sample = { T_K: number; X_NI?: number; X_NB?: number; phases: SamplePhase[] };
export type ModeResult = {
  balance_checks: { max_amount_error: number; max_component_error: Record<string, number> };
  phases_observed: string[]; highest_sampled_T_with_two_FCC_K: number;
  samples: Record<string, Sample>; near_pure_phase_sets: Record<string, string[]>;
};
export type CuNiResults = {
  source_sha256: string; python: string; pycalphad: string; phases_requested: string[];
  T_K: number[]; X_NI: number[]; P_Pa: number; N_mol_atoms: number; pdens: number;
  tolerances: { energy_abs: number; energy_rel: number; balance_abs: number };
  equilibrium: { magnetic_on: ModeResult; magnetic_off: ModeResult };
};
type Endmember = { formula_J_per_mol: number; atom_J_per_mol: number; magnetic_J_per_mol_atoms: number };
export type NiNbResults = {
  source_sha256: string; python: string; pycalphad: string; phases_requested: string[]; phases_observed: string[];
  P_Pa: number; N_mol_atoms: number; T_K: number[]; X_NB: number[]; pdens: number;
  tolerances: { energy_abs: number; energy_rel: number; balance_abs: number };
  energy_checks: { temperature_K: number; delta_NB_NB_NB: Endmember; mu_all_NI: Endmember };
  balance_checks: { max_amount_error: number; max_component_error: Record<string, number> };
  sample: Sample; near_pure_phase_sets: Record<string, string[]>;
};
type Receipt = { schema_version: 1; files: { canonical: string; public: string; sha256: string }[] };

function finite(value: unknown): void {
  if (typeof value === 'number' && !Number.isFinite(value)) throw Error('Nonfinite saved value');
  if (Array.isArray(value)) value.forEach(finite);
  else if (value && typeof value === 'object') Object.values(value).forEach(finite);
}

export async function loadMaterial<T>(id: 'cuni' | 'ninb', fetcher: typeof fetch = fetch): Promise<T> {
  return loadLearningJSON<T>(`materials/${id}/results.json`, fetcher);
}

/** Any learning JSON listed in the content receipt, hash-checked before use. */
export async function loadLearningJSON<T>(path: string, fetcher: typeof fetch = fetch): Promise<T> {
  const get = async (path: string) => {
    const response = await fetcher(`/learning/${path}`, { cache: 'no-store' });
    if (!response.ok) throw Error(`Missing saved output: ${path}`);
    return new Uint8Array(await response.arrayBuffer());
  };
  const receipt = JSON.parse(new TextDecoder().decode(await get('content_receipt.json'))) as Receipt;
  const entry = receipt.schema_version === 1 ? receipt.files?.find(file => file.public === path) : undefined;
  if (!entry) throw Error('Saved output is not in the content receipt');
  const data = await checkedJSON(await get(path), entry.sha256);
  finite(data);
  return data as T;
}
