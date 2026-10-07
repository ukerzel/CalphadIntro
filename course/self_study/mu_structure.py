"""Export atom positions for the step 06 mu-phase structure sketch.

Geometry: the Fe7W6 (D8_5, mu-phase) prototype, space group R-3m (No. 166),
hexagonal setting, from the AFLOW Library of Crystallographic Prototypes,
https://aflow.org/prototype-encyclopedia/A7B6_hR13_166_ah_3c-001 (Mehl et al.,
Comput. Mater. Sci. 136 (2017) S1, doi:10.1016/j.commatsci.2017.01.017;
original structure: Arnfelt and Westgren, Jernkontorets Ann. 119 (1935) 185).
Only the five published site parameters below are used; the symmetry expansion
is ours. The lattice is the Fe7W6 one, not a Nb-Ni measurement: a sketch.

Link to the Ni-Nb database: MU_PHASE has five sublattices with 2:2:2:6:1 sites
per formula unit. Per hexagonal cell (3 formula units) the 18h site has 18
atoms and 3a has 3, so the 6-site and 1-site sublattices map onto them by count.
The three 2-site sublattices map onto the three 6c sites, but the database file
does not say in which order, so the export does not assign them.

Run from the repository root:
    .venv/bin/python -m course.self_study.mu_structure
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'mu_structure.json'
A, C = 4.757, 25.84  # Angstrom, Fe7W6 prototype
SITES = [  # label, Wyckoff, fractional (x, y, z), prototype element, element in ideal Nb7Ni6
    ('3a', '3a', (0.0, 0.0, 0.0), 'Fe', 'Nb'),
    ('6c_1', '6c', (0.0, 0.0, 0.167), 'W', 'Nb'),
    ('6c_2', '6c', (0.0, 0.0, 0.346), 'W', 'Nb'),
    ('6c_3', '6c', (0.0, 0.0, 0.448), 'W', 'Nb'),
    ('18h', '18h', (0.4999966667, 0.5000033333, 0.5900033333), 'Fe', 'Ni'),
]
SUBLATTICE = {'3a': '1-site sublattice', '18h': '6-site sublattice', '6c': 'one of the three 2-site sublattices'}
OPS = [  # the 12 point operations of R-3m (hexagonal setting), as functions of (x, y, z)
    lambda x, y, z: (x, y, z), lambda x, y, z: (-y, x - y, z), lambda x, y, z: (-x + y, -x, z),
    lambda x, y, z: (y, x, -z), lambda x, y, z: (x - y, -y, -z), lambda x, y, z: (-x, -x + y, -z),
    lambda x, y, z: (-x, -y, -z), lambda x, y, z: (y, -x + y, -z), lambda x, y, z: (x - y, x, -z),
    lambda x, y, z: (-y, -x, z), lambda x, y, z: (-x + y, y, z), lambda x, y, z: (x, x - y, z)]
CENTRING = [(0, 0, 0), (2 / 3, 1 / 3, 1 / 3), (1 / 3, 2 / 3, 2 / 3)]
CUTOFF = 3.3  # Angstrom, first-shell neighbour cutoff for the coordination count


def _wrap(v: float) -> float:
    v %= 1.0
    return 0.0 if v > 1 - 1e-6 else v


def expand(xyz) -> list[tuple[float, float, float]]:
    x, y, z = xyz
    out: list[tuple[float, float, float]] = []
    for op in OPS:
        base = op(x, y, z)
        for t in CENTRING:
            p = tuple(_wrap(b + s) for b, s in zip(base, t))
            if not any(all(min(abs(p[i] - q[i]), 1 - abs(p[i] - q[i])) < 1e-4 for i in range(3)) for q in out):
                out.append(p)
    return out


def cart(f) -> tuple[float, float, float]:
    return (A * f[0] - A / 2 * f[1], A * math.sqrt(3) / 2 * f[1], C * f[2])


def build() -> dict:
    cell = [(label, wy, p, nb) for label, wy, xyz, _, nb in SITES for p in expand(xyz)]
    coordination = {}
    for label, _, xyz, _, _ in SITES:
        f0, n, nearest = expand(xyz)[0], 0, math.inf
        for _, _, q, _ in cell:
            for s in itertools.product((-1, 0, 1), repeat=3):
                d = math.dist(cart(f0), cart([q[i] + s[i] for i in range(3)]))
                if 0.1 < d < CUTOFF:
                    n, nearest = n + 1, min(nearest, d)
        coordination[label] = {'CN': n, 'nearest_A': round(nearest, 3)}
    atoms = []
    for i, j in itertools.product(range(2), repeat=2):  # 2 x 2 cells in the basal plane
        for label, wy, p, nb in cell:
            x, y, z = cart((p[0] + i, p[1] + j, p[2]))
            atoms.append({'site': label, 'wyckoff': wy, 'element_Nb7Ni6': nb, 'xyz_A': [round(x, 4), round(y, 4), round(z, 4)]})
    return {'schema_version': 1, 'name': 'mu phase, Fe7W6 (D8_5) prototype', 'space_group': 'R-3m (166), hexagonal setting',
            'a_A': A, 'c_A': C, 'atoms_per_hexagonal_cell': len(cell), 'formula_units_per_cell': len(cell) // 13,
            'sites': [{'site': label, 'wyckoff': wy, 'fractional': list(xyz), 'prototype_element': el, 'element_Nb7Ni6': nb,
                       'atoms_per_cell': sum(1 for a in cell if a[0] == label), 'sublattice': SUBLATTICE[wy],
                       **coordination[label]} for label, wy, xyz, el, nb in SITES],
            'supercell': '2 x 2 x 1 hexagonal cells', 'atoms': atoms,
            'source': 'AFLOW prototype A7B6_hR13_166_ah_3c-001 (Mehl et al. 2017); Arnfelt and Westgren 1935'}


def main() -> None:
    data = build()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(HERE.parents[1])} ({OUTPUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
