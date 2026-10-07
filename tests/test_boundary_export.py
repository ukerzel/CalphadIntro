"""Checks for the step 04 tangent-picture and hand-iteration export."""
import json
import math
from pathlib import Path

import pytest

from course.self_study import boundary_export as export

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/boundary_views.json'


@pytest.fixture(scope='module')
def data():
    return export.build()


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))


def test_open_cases_match_the_lesson_odds_formula(data):
    rt = 8.3145 * 1000
    for res in data['reservoirs']:
        odds_b = res['x_b'] / (1 - res['x_b'])
        for case in res['cases']:
            odds = odds_b * math.exp(-case['delta'] / rt)
            assert case['theta'] == pytest.approx(odds / (1 + odds), abs=2e-6)
            if case['delta'] == 0:
                assert case['theta'] == pytest.approx(res['x_b'], abs=2e-6)
    lesson = next(c for c in data['reservoirs'][0]['cases'] if c['delta'] == -5000)
    assert lesson['theta'] == pytest.approx(0.16856026, abs=1e-7)  # step 04 worked answer


def test_parallel_tangent_touches_gs_at_theta(data):
    for res in data['reservoirs']:
        slope = res['mu_B'] - res['mu_A']
        for case in res['cases']:
            y0, y1 = case['parallel_tangent']
            assert y1 - y0 == pytest.approx(slope, abs=1e-9)
            assert y0 + slope * case['theta'] == pytest.approx(case['gs_theta'], abs=1e-9)


def test_hand_iteration_reaches_the_closed_result(data):
    it = data['iteration']
    assert it['B_total'] == 850
    assert it['steps'][0]['theta'] == pytest.approx(0.16856026, abs=1e-7)
    assert it['steps'][-1]['theta'] == pytest.approx(0.17160752408695693, abs=1e-6)
    for step in it['steps']:
        assert step['boundary_B'] + step['bulk_B'] == pytest.approx(850, abs=1e-9)
