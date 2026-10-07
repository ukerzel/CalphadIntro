"""Checks on the committed Cu-Ni / Ni-Nb grid exports (no database needed)."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / 'course/self_study/generated'


def load(name):
    return json.loads((GEN / name).read_text())


@pytest.mark.parametrize('name', ['cuni_grid.json', 'ninb_grid.json'])
def test_every_grid_point_balances(name):
    data = load(name)
    for rows in data['modes'].values():
        assert len(rows) == len(data['T_K']) and all(len(r) == len(data['x']) for r in rows)
        for row in rows:
            for x, cell in zip(data['x'], row):
                assert cell, 'every grid point has at least one phase'
                assert sum(c[1] for c in cell) == pytest.approx(1, abs=1e-5)
                assert sum(c[1] * c[2] for c in cell) == pytest.approx(x, abs=1e-5)


def test_cuni_matches_saved_samples_and_gap_tops():
    data = load('cuni_grid.json')
    saved = json.loads((ROOT / 'course/materials/cuni/results.json').read_text())['equilibrium']
    fcc = data['phases'].index('FCC_A1')
    for mode, rows in data['modes'].items():
        two_fcc = [t for t, row in zip(data['T_K'], rows) if any(sum(1 for c in cell if c[0] == fcc) >= 2 for cell in row)]
        assert max(two_fcc) == saved[mode]['highest_sampled_T_with_two_FCC_K']
        ix = data['x'].index(0.5)
        for sample in saved[mode]['samples'].values():
            cell = rows[data['T_K'].index(sample['T_K'])][ix]
            got = sorted((data['phases'][c[0]], c[1], c[2]) for c in cell)
            want = sorted((p['phase'], p['atom_mole_fraction'], p['x_NI']) for p in sample['phases'])
            for (pa, na, xa), (pb, nb, xb) in zip(got, want):
                assert pa == pb and na == pytest.approx(nb, abs=2e-6) and xa == pytest.approx(xb, abs=2e-6)


def test_ninb_matches_the_saved_sample():
    data = load('ninb_grid.json')
    sample = json.loads((ROOT / 'course/materials/ninb/results.json').read_text())['sample']
    it = data['T_K'].index(sample['T_K'])
    ix = min(range(len(data['x'])), key=lambda i: abs(data['x'][i] - sample['X_NB']))
    got = sorted((data['phases'][c[0]], c[1], c[2]) for c in data['modes']['model'][it][ix])
    want = sorted((p['phase'], p['atom_mole_fraction'], p['x_NB']) for p in sample['phases'])
    assert [g[0] for g in got] == [w[0] for w in want]
    for g, w in zip(got, want):
        assert g[1] == pytest.approx(w[1], abs=2e-6) and g[2] == pytest.approx(w[2], abs=2e-6)


def test_ninb_formula_units_cover_every_ordered_phase():
    data = load('ninb_grid.json')
    apf = data['atoms_per_formula']
    present = {data['phases'][c[0]] for row in data['modes']['model'] for cell in row for c in cell}
    assert present - {'LIQUID', 'FCC_A1', 'BCC_A2'} <= set(apf)
    nbni8 = data['phases'].index('NBNI8')  # the one line compound here: 1 Nb in 9 atoms
    found = [c[2] for row in data['modes']['model'] for cell in row for c in cell if c[0] == nbni8]
    assert found and all(x == pytest.approx(1 / apf['NBNI8'], abs=1e-5) for x in found)


def test_ninb_eutectic_rows_quoted_in_step_06():
    data = load('ninb_grid.json')
    rows, names = data['modes']['model'], data['phases']

    def phases(T, x):
        ix = min(range(len(data['x'])), key=lambda i: abs(data['x'][i] - x))
        return sorted(names[c[0]] for c in rows[data['T_K'].index(T)][ix])
    assert phases(1470.0, 0.40) == ['LIQUID'] and phases(1425.0, 0.40) == ['DELTA', 'MU_PHASE']
    assert phases(1560.0, 0.16) == ['LIQUID'] and phases(1515.0, 0.16) == ['DELTA', 'FCC_A1']
