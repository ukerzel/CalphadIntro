"""Checks for the optional step 18: the lens with a third component."""
import json
from pathlib import Path

import numpy as np
import pytest

from course.self_study import day3_ternary as t3

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/day3_ternary.json'


@pytest.fixture(scope='module')
def data():
    return t3.build()


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))


def test_binary_edges_reproduce_the_lens():
    s, l = t3.edge_tie(('A', 'B'))
    assert (round(l, 3), round(s, 3)) == (0.312, 0.441)          # the step 03 lens at 1400 K
    s, l = t3.edge_tie(('C', 'B'))
    assert (round(l, 3), round(s, 3)) == (0.154, 0.217)
    assert t3.edge_tie(('A', 'C')) is None                        # the A–C edge is all liquid


def test_partition_ratios_and_rachford_rice(data):
    assert [round(k, 3) for k in data['K']] == [1.229, 0.709, 1.080]
    rr = data['rachford_rice']
    assert rr['sum_zK'] > 1 and rr['sum_z_over_K'] > 1 and round(rr['V'], 3) == 0.771
    z = np.array(data['conditions']['z'])
    xs, xl = np.array(rr['x_SOLID']), np.array(rr['x_LIQUID'])
    assert np.allclose((1 - rr['V']) * xs + rr['V'] * xl, z, atol=1e-12)    # atom balance for all three
    assert xs.sum() == pytest.approx(1) and xl.sum() == pytest.approx(1)


def test_menu_uses_a_tie_triangle_and_the_plane_supports_it(data):
    menu = data['menu']
    assert len(menu['used']) == 3                                  # two neighbouring LIQUID dots and one SOLID
    assert sorted(u['phase'] for u in menu['used']) == ['LIQUID', 'LIQUID', 'SOLID']
    mu = np.array(menu['mu'])
    for phase in t3.PHASES:                                        # no menu dot below the plane
        gaps = np.array(menu['g'][phase]) - np.array(menu['x']) @ mu
        assert gaps.min() > -1e-8
    assert menu['G_up'] >= data['rachford_rice']['G']


def test_column_generation_converges_to_rachford_rice(data):
    rounds = data['rounds']
    ups = [r['G_up'] for r in rounds]
    assert all(b <= a + 1e-9 for a, b in zip(ups, ups[1:]))
    assert rounds[-1]['remaining'] <= t3.CG_TOL
    for r in rounds:
        assert r['G_low'] <= data['rachford_rice']['G'] + 1e-6
    for u in data['final']['used']:
        target = data['rachford_rice']['x_SOLID' if u['phase'] == 'SOLID' else 'x_LIQUID']
        assert np.allclose(u['x'], target, atol=2e-3)
    x, mu = np.array(data['rachford_rice']['x_LIQUID']), np.array(data['final']['mu'])
    xs = np.array(data['rachford_rice']['x_SOLID'])
    assert float(t3.g('LIQUID', x) - x @ mu) == pytest.approx(0, abs=0.01)   # both phases touch the plane
    assert float(t3.g('SOLID', xs) - xs @ mu) == pytest.approx(0, abs=0.01)


def test_closed_form_pricing_is_the_minimum():
    mu = np.array(t3.solve_master(['SOLID'] * 91 + ['LIQUID'] * 91, np.vstack([t3.grid(12)] * 2)).mu)
    fine = t3.grid(200)
    for phase in t3.PHASES:
        x, depth = t3.price(phase, mu)
        assert depth <= (t3.g(phase, fine) - fine @ mu).min() + 1e-9


def test_harder_landscape_hides_a_valley(data):
    h = data['harder']
    at = np.array(h['tangent_at'])
    assert float(t3.g_with_ac('LIQUID', at) - at @ np.array(h['mu'])) == pytest.approx(0, abs=1e-8)
    assert h['deepest']['depth'] < -700 and h['deepest']['x'][2] > 0.8      # far away, on the C-rich side
    assert data['scaling'][-1]['cells'] == pytest.approx(1e18)
