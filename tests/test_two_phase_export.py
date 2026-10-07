"""Checks for the self-study two-phase export against the foundation lessons."""
import json
from pathlib import Path

import pytest

from course.self_study import two_phase_export as export

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/two_phase.json'


@pytest.fixture(scope='module')
def data():
    return export.build()


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))


def test_part_a_matches_lessons_5_and_6(data):
    a = data['part_a']
    co = a['coexistence']
    assert co['x_ALPHA'] == pytest.approx(0.191040753, abs=1e-9)
    assert co['x_BETA'] == pytest.approx(0.808959247, abs=1e-9)
    # Horizontal common line: both chemical potentials equal the line energy.
    assert co['mu_A'] == pytest.approx(-10762.730017, abs=1e-6)
    assert co['mu_B'] == pytest.approx(-10762.730017, abs=1e-6)
    assert co['GM_x_ALPHA'] == pytest.approx(-10762.730017, abs=1e-6)
    assert co['GM_x_BETA'] == pytest.approx(-10762.730017, abs=1e-6)
    half = next(s for s in a['states'] if s['z'] == 0.5)
    assert half['homogeneous_GM']['ALPHA'] == pytest.approx(-8763.172233, abs=1e-6)
    assert half['GM'] == pytest.approx(-10762.730017, abs=1e-6)
    assert [r['phase'] for r in half['regions']] == ['ALPHA', 'BETA']


def test_part_a_balances_and_single_phase_ends(data):
    for state in data['part_a']['states']:
        regions = state['regions']
        assert sum(r['f'] for r in regions) == pytest.approx(1, abs=1e-12)
        assert sum(r['f'] * r['x'] for r in regions) == pytest.approx(state['z'], abs=1e-12)
        assert state['GM'] <= min(state['homogeneous_GM'].values()) + 1e-9
    first, last = data['part_a']['states'][0], data['part_a']['states'][-1]
    assert [r['phase'] for r in first['regions']] == ['ALPHA']
    assert [r['phase'] for r in last['regions']] == ['BETA']


def test_part_b_matches_lesson_7_and_closes_above_tc(data):
    b = data['part_b']
    at600 = next(r for r in b['rows'] if r['T_K'] == 600)
    assert at600['compositions'][0] == pytest.approx(0.021032752, abs=1e-9)
    assert at600['compositions'][1] == pytest.approx(0.978967248, abs=1e-9)
    for row in b['rows']:
        if row['T_K'] < b['Tc_K']:
            assert row['status'] == 'two_compositions'
            left, right = row['compositions']
            assert 0 < left < 0.5 < right < 1
        else:
            assert row['status'] == 'single_phase' and row['compositions'] == []
    for row in b['rows']:
        # GM minus GM_mix is the straight reference line 1000+12000x-10T.
        for x, total, mixing in zip(b['x'], row['GM'], row['GM_mix']):
            assert total - mixing == pytest.approx(1000 + 12000 * x - 10 * row['T_K'], abs=1e-8)
        if row['compositions']:
            assert min(row['GM_mix']) >= row['GM_mix_tangent'] - 1e-6
    widths = [r['compositions'][1] - r['compositions'][0] for r in b['rows'] if r['compositions']]
    assert widths == sorted(widths, reverse=True)


def test_part_c_lens_matches_step_01_and_closes_at_the_melting_points(data):
    c = data['part_c']
    for row in c['rows']:
        t = row['T_K']
        if t <= 1000 or t >= 1800:
            assert row['x_SOLID'] is None and row['status'] != 'SOLID + LIQUID'
            continue
        x_s, x_l = row['x_SOLID'], row['x_LIQUID']
        assert 0 < x_l < x_s < 1  # the solid is richer in the higher-melting B
        # Independent check: numerical derivatives of each phase curve give equal mu.
        def mu(phase, x, h=1e-6):
            g = lambda v: export.lens_g(phase, v, t)
            slope = (g(x + h) - g(x - h)) / (2 * h)
            return g(x) - x * slope, g(x) + (1 - x) * slope
        (a_s, b_s), (a_l, b_l) = mu('SOLID', x_s), mu('LIQUID', x_l)
        assert a_s == pytest.approx(a_l, abs=1e-3) and b_s == pytest.approx(b_l, abs=1e-3)
        assert row['mu_A'] == pytest.approx(a_s, abs=1e-3)
    # Pure A melts at 1000 K as in step 01; pure B at 1800 K.
    assert export.lens_g0('A', 'SOLID', 1000) == export.lens_g0('A', 'LIQUID', 1000) == -9000
    assert export.lens_g0('B', 'SOLID', 1800) == export.lens_g0('B', 'LIQUID', 1800)
    widths = [r['x_SOLID'] - r['x_LIQUID'] for r in c['rows'] if r['x_SOLID'] is not None]
    assert max(widths) > 0.1 and min(widths) < 0.05
