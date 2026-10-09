"""Checks for the optional LP primer: its export against SciPy's linprog, and the numbers its page and sheet print."""
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import linprog

from course.self_study import lp_primer as p

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / 'course/self_study/generated/lp_primer.json'
LESSONS = ROOT / 'course/self_study/lessons.json'
SHEET = ROOT / 'course/day3/lp_primer_sheet.md'


@pytest.fixture(scope='module')
def data():
    return p.build()


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))


def test_best_charge_search_and_prices_agree_with_linprog(data):
    blend = data['blend']
    res = p.solve_blend(p.LOTS, p.TARGET)
    assert res.status == 0
    assert blend['best']['cost'] == pytest.approx(res.fun, abs=1e-6)
    assert [i for i, f in enumerate(res.x) if f > 1e-9] == blend['best']['used']
    frames = blend['swap']['frames']
    assert [f['used'] for f in frames] == [[0, 5], [0, 4], [2, 4]]
    assert [f['cost'] for f in frames] == sorted((f['cost'] for f in frames), reverse=True), 'the search never raises the cost'
    assert frames[-1]['enter'] is None and min(frames[-1]['gaps']) > -1e-9, 'no lot below the final line'
    base, slope = res.eqlin.marginals
    assert (blend['prices']['base'], blend['prices']['slope']) == pytest.approx((base, slope), abs=1e-6)
    assert blend['prices']['cu'] == pytest.approx(6.857143, abs=1e-6) and blend['prices']['ni'] == pytest.approx(12.0, abs=1e-6)
    assert base + slope * p.TARGET == pytest.approx(res.fun, abs=1e-9), 'floor meets ceiling'


def test_prices_hold_between_the_used_lots_and_the_offer_is_priced(data):
    blend = data['blend']
    nudged = p.solve_blend(p.LOTS, p.TARGET + p.NUDGE).fun - p.solve_blend(p.LOTS, p.TARGET).fun
    assert blend['nudge']['change'] == pytest.approx(nudged, abs=1e-6)
    for z in (0.31, 0.5, 0.64):   # inside 0.30-0.65 the slope does not move
        assert p.solve_blend(p.LOTS, z).eqlin.marginals[1] == pytest.approx(blend['prices']['slope'], abs=1e-6)
    far = p.solve_blend(p.LOTS, 0.70).fun - p.solve_blend(p.LOTS, p.TARGET).fun
    assert far != pytest.approx(blend['prices']['slope'] * 0.30, abs=0.1), 'past Monel the price changes'
    offer = blend['offer']
    assert offer['gap'] == pytest.approx(-0.228571, abs=1e-6)
    assert offer['best']['cost'] == pytest.approx(p.solve_blend(p.LOTS + [p.OFFER], p.TARGET).fun, abs=1e-6)
    assert offer['best']['cost'] == pytest.approx(8.80)


def test_every_target_frame_is_the_linprog_optimum(data):
    for frame in data['blend']['targets']:
        assert frame['cost'] == pytest.approx(p.solve_blend(p.LOTS, frame['z']).fun, abs=1e-6), frame['z']
        assert ('slope' in frame) != ('slopes' in frame)
    on_cuni30 = next(f for f in data['blend']['targets'] if f['z'] == 0.30)
    assert on_cuni30['used'] == [2] and on_cuni30['slopes'] == pytest.approx([3.333333, 5.142857], abs=1e-6)


def test_polygon_corners_optimum_prices_ties_and_infeasibility(data):
    poly = data['polygon']
    corners = poly['regions']['normal']
    assert len(corners) == 5 and all(len(c['tight']) >= 2 for c in corners)
    res, sign = p.solve_polygon('normal')
    assert poly['optimum']['f'] == pytest.approx(list(res.x), abs=1e-6)
    assert poly['optimum']['f'] == pytest.approx([0.714286, 0.285714], abs=1e-6)
    assert poly['optimum']['cost'] == pytest.approx(res.fun, abs=1e-6)
    assert poly['optimum']['cost'] == pytest.approx(data['blend']['best']['cost'], abs=1e-6), 'the same charge as the dots'
    assert poly['optimum']['duals'] == pytest.approx({'charge': 6.857143, 'ni': 5.142857, 'fe': 0.0, 'furnace': 0.0}, abs=1e-6)
    assert poly['optimum']['ni_range'] == pytest.approx([0.30, 0.45])
    assert poly['strict_status'] == 2 and poly['regions']['strict'] == []
    for q in poly['ties']:
        costs = [p.POLY_LOTS[0]['price'] * c['f'][0] + q * c['f'][1] for c in corners]
        assert sum(c - min(costs) < 1e-5 for c in costs) == 2, f'a tie at {q}'
    assert poly['ties'] == pytest.approx([8.40, 18.20])
    cheap = linprog([8.40, 8.00], A_ub=[[-1, -1], [-0.3, -0.65], [0.006, 0.02], [1, 1]], b_ub=[-1, -0.4, 0.012, 1.5], method='highs-ds')
    assert cheap.fun == pytest.approx(8.228571, abs=1e-6)   # the page's self-check answer


def _primer_text() -> str:
    module = next(m for m in json.loads(LESSONS.read_text())['modules'] if m['id'] == 'lp-primer')
    return json.dumps(module, ensure_ascii=False)


@pytest.mark.parametrize('number', ['8.914', '6.86', '12.00', '5.14', '10.64', '9.12', '9.43', '0.23', '8.80', '2.47', '0.29',
                                    '0.714', '0.286', '8.40', '18.20', '9.17', '12.99', '12.60', '11.20', '8.23', '9.017', '8.50'])
def test_page_and_sheet_print_the_generated_numbers(number):
    assert number in _primer_text(), f'page: {number}'
    if number not in ('8.23', '9.017', '8.50', '18.20'):   # self-check answers and the second tie live on the page only
        assert number in SHEET.read_text(), f'sheet: {number}'


def test_primer_sits_before_step_10_and_explains_the_words():
    modules = json.loads(LESSONS.read_text())['modules']
    ids = [m['id'] for m in modules]
    assert ids.index('lp-primer') + 1 == ids.index('menu')
    text = _primer_text()
    for words in ('subject to', 'while keeping these rules', 'feasible', 'optimal', 'variables', 'objective', 'constraints', 'infeasible', 'unbounded'):
        assert words in text, words
    assert 'invented' in text and 'certif' not in text
