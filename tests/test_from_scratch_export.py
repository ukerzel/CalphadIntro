"""Checks for the self-study part D export: the four from-scratch routes and pycalphad agree."""
import json
from pathlib import Path

import pytest

from course.self_study import from_scratch_export as export
from course.self_study import two_phase_export as tp

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/from_scratch.json'


@pytest.fixture(scope='module')
def data():
    return export.build()


def test_committed_file_matches_a_fresh_build(data):
    # pycalphad's values are stored rounded; its last digits can still differ between runs.
    committed, fresh = json.loads(GENERATED.read_text()), json.loads(json.dumps(data))
    pyc_c, pyc_f = committed.pop('pycalphad'), fresh.pop('pycalphad')
    diff_c, diff_f = committed.pop('difference'), fresh.pop('difference')
    assert committed == fresh
    assert _close(pyc_c, pyc_f)
    assert set(diff_c) == set(diff_f) and all(abs(diff_c[k]) < 1e-8 and abs(diff_f[k]) < 1e-8 for k in ('x_SOLID', 'x_LIQUID', 'f_LIQUID', 'lens_max_x'))


def _close(a, b) -> bool:
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_close(u, v) for u, v in zip(a, b))
    if isinstance(a, float):
        return abs(a - b) <= 1e-6
    return a == b


def test_answer_matches_part_c_and_the_notebook(data):
    a = data['answer']
    x_s, x_l = tp.lens_coexistence(1400.0)
    assert a['x_SOLID'] == pytest.approx(x_s, abs=1e-12) and a['x_SOLID'] == pytest.approx(0.440517, abs=1e-6)
    assert a['x_LIQUID'] == pytest.approx(x_l, abs=1e-12) and a['x_LIQUID'] == pytest.approx(0.312410, abs=1e-6)
    assert a['f_LIQUID'] == pytest.approx(0.316275, abs=1e-6)
    assert a['GM'] == pytest.approx(-20473.124218, abs=1e-6)
    assert a['homogeneous_GM']['SOLID'] - a['GM'] == pytest.approx(39.066511, abs=1e-6)


def test_every_method_approaches_the_answer_from_above(data):
    exact = data['answer']['GM']
    assert all(f['GM'] >= exact - 1e-9 for f in data['brute'])
    assert min(f['GM'] for f in data['brute']) - exact < 0.1
    gaps = [f['above_exact'] for f in data['grid']]
    assert all(g >= -1e-9 for g in gaps) and gaps[-1] < 0.01
    assert [len(f['chosen']) for f in data['grid']][:2] == [1, 1]          # coarse grids miss the split
    for f in data['grid']:
        assert sum(c['f'] for c in f['chosen']) == pytest.approx(1, abs=1e-9)
        assert sum(c['f'] * c['x'] for c in f['chosen']) == pytest.approx(0.4, abs=1e-9)


def test_newton_converges_and_continuation_equals_the_closed_form(data):
    frames = data['newton']['frames']
    residual = [max(abs(f['residual_mu_A']), abs(f['residual_mu_B'])) for f in frames]
    assert residual[0] > 1e3 and residual[-1] < 1e-9 and len(frames) <= 8
    assert all(b < a for a, b in zip(residual, residual[1:-1]))          # each step closer
    for row in data['continuation']:
        x_s, x_l = tp.lens_coexistence(row['T_K'])
        assert row['x_SOLID'] == pytest.approx(x_s, abs=1e-9) and row['x_LIQUID'] == pytest.approx(x_l, abs=1e-9)
    assert len(data['continuation']) == 79


def test_pycalphad_agrees_with_the_from_scratch_route(data):
    d = data['difference']
    assert max(abs(d[k]) for k in ('x_SOLID', 'x_LIQUID', 'f_LIQUID')) < 1e-8
    assert max(abs(d[k]) for k in ('GM', 'mu_A', 'mu_B')) < 1e-6
    assert d['lens_max_x'] < 1e-8
    assert data['pycalphad']['sample']['SOLID']['count'] > 1000
