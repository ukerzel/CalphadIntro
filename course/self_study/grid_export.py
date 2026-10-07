"""Export the full equilibrium grids behind the Cu-Ni and Ni-Nb phase diagrams.

Reuses the unchanged course scripts' conditions and helpers
(course/materials/{cuni,ninb}/worked_example.py): same hash-checked published
database, phases, temperature/composition grids, pressure, pdens=60 and, for
Cu-Ni, the magnetic-off control. Only the equilibrium results are saved; the
database itself is never copied. Cross-checks the saved samples in results.json.

Run from the repository root with the learner-fetched inputs outside the checkout:
    .venv/bin/python -m course.self_study.grid_export --cuni /path/CuNi-92Mey-LB.tdb \
        --ninb /path/calpha_102563_Nb-Ni_new_mmc1.tdb
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from pycalphad import equilibrium, variables as v

from course.materials.cuni import worked_example as cuni
from course.materials.ninb import worked_example as ninb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIGITS = 6  # display rounding of saved amounts and compositions


def grid(eq, element: str, phases: list[str], balance) -> list:
    """rows[T][x] = [[phase index, amount NP, phase x(element)], ...] for positive amounts."""
    balance(eq)
    names, amounts = eq.Phase.values, eq.NP.values
    xs = eq.X.sel(component=element).values
    out = []
    for it in range(names.shape[2]):
        row = []
        for ix in range(names.shape[3]):
            cell = []
            for p, n, x in zip(names[0, 0, it, ix], amounts[0, 0, it, ix], xs[0, 0, it, ix]):
                if p and np.isfinite(n) and n > 1e-8:
                    cell.append([phases.index(str(p)), round(float(n), DIGITS), round(float(x), DIGITS)])
            cell.sort(key=lambda c: c[2])
            row.append(cell)
        out.append(row)
    return out


def check_sample(rows: list, temperatures, compositions, sample: dict, phases: list[str], key: str) -> None:
    it = int(np.argmin(np.abs(np.asarray(temperatures) - sample['T_K'])))
    ix = int(np.argmin(np.abs(np.asarray(compositions) - sample[key])))
    saved = sorted([[phases.index(p['phase']), p['atom_mole_fraction'], p['x_' + key[2:]]] for p in sample['phases']], key=lambda c: c[2])
    cell = rows[it][ix]
    if len(cell) != len(saved) or any(a[0] != b[0] or abs(a[1] - b[1]) > 2e-6 or abs(a[2] - b[2]) > 2e-6 for a, b in zip(cell, saved)):
        raise ValueError(f'grid disagrees with the saved sample at T={sample["T_K"]}')


def export_cuni(source: Path) -> dict:
    db = cuni.load_source(source)
    cond = {v.T: cuni.TEMPERATURES, v.X('NI'): cuni.COMPOSITIONS, v.P: cuni.PRESSURE, v.N: 1}
    modes = {'magnetic_on': equilibrium(db, cuni.COMPONENTS, cuni.PHASES, cond, calc_opts={'pdens': 60}),
             'magnetic_off': equilibrium(db, cuni.COMPONENTS, cuni.PHASES, cond, model=cuni.MagneticOffModel, calc_opts={'pdens': 60})}
    saved = json.loads((ROOT / 'course/materials/cuni/results.json').read_text())
    data = {'system': 'Cu-Ni', 'element': 'NI', 'phases': cuni.PHASES, 'T_K': cuni.TEMPERATURES.tolist(), 'x': cuni.COMPOSITIONS.tolist(),
            'P_Pa': cuni.PRESSURE, 'pdens': 60, 'source_sha256': cuni.SOURCE_SHA, 'rounding_digits': DIGITS, 'modes': {}}
    for mode, eq in modes.items():
        rows = grid(eq, 'NI', cuni.PHASES, cuni.balance_checks)
        for sample in saved['equilibrium'][mode]['samples'].values():
            check_sample(rows, cuni.TEMPERATURES, cuni.COMPOSITIONS, sample, cuni.PHASES, 'X_NI')
        data['modes'][mode] = rows
    return data


def export_ninb(source: Path) -> dict:
    db = ninb.load_source(source)
    eq = equilibrium(db, ninb.COMPONENTS, ninb.PHASES, {v.T: ninb.TEMPERATURES, v.X('NB'): ninb.COMPOSITIONS, v.P: ninb.PRESSURE, v.N: 1},
                     calc_opts={'pdens': 60})
    rows = grid(eq, 'NB', ninb.PHASES, ninb.balance_checks)
    saved = json.loads((ROOT / 'course/materials/ninb/results.json').read_text())
    check_sample(rows, ninb.TEMPERATURES, ninb.COMPOSITIONS, saved['sample'], ninb.PHASES, 'X_NB')
    return {'system': 'Ni-Nb', 'element': 'NB', 'phases': ninb.PHASES, 'T_K': ninb.TEMPERATURES.tolist(), 'x': ninb.COMPOSITIONS.tolist(),
            'P_Pa': ninb.PRESSURE, 'pdens': 60, 'source_sha256': ninb.SOURCE_SHA, 'rounding_digits': DIGITS,
            'atoms_per_formula': {'DELTA': 4, 'MU_PHASE': 13, 'NBNI8': 9}, 'modes': {'model': rows}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cuni', type=Path, required=True)
    parser.add_argument('--ninb', type=Path, required=True)
    args = parser.parse_args()
    for name, data in (('cuni_grid.json', export_cuni(args.cuni)), ('ninb_grid.json', export_ninb(args.ninb))):
        out = HERE / 'generated' / name
        out.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False) + '\n')
        print(f'wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
