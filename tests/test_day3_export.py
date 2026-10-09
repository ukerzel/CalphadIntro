"""Checks for the advanced steps: the shared helper (day3_core) and every printed number of its export."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from course.self_study import day3_core as d
from course.self_study import day3_export as export
from course.self_study import two_phase_export as tp

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/day3.json'


@pytest.fixture(scope='module')
def data():
    return export.build()


def r(value, digits):
    return round(value, digits)


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))
    assert json.loads(export.PREWORK.read_text()) == json.loads(json.dumps(export.build_prework()))


def test_prework_frames():
    pre = export.build_prework()
    melt = {f['T_K']: f for f in pre['second_law']['frames']}
    assert melt[1000.0]['dG'] == 0 and melt[1000.0]['dS_total'] == 0       # the melting point
    for f in pre['second_law']['frames']:                                    # total entropy up exactly when G down
        assert f['dS_total'] == pytest.approx(-f['dG'] / f['T_K'], abs=1e-12)
    n100 = next(c for c in pre['counting'] if c['N'] == 100)
    assert (r(n100['lnW_per_N'][40], 3), r(n100['limit'][40], 3)) == (0.648, 0.673)
    big = next(c for c in pre['counting'] if c['N'] == 1000)
    assert abs(big['lnW_per_N'][400] - big['limit'][400]) < abs(n100['lnW_per_N'][40] - n100['limit'][40])
    at3 = next(o for o in pre['omega']['frames'] if o['omega_over_RT'] == 3.0)
    assert (r(at3['binodal'][0], 3), r(at3['spinodal'][0], 3)) == (0.071, 0.211)
    assert all(not o['binodal'] for o in pre['omega']['frames'] if o['omega_over_RT'] <= 2)
    b1400 = next(f for f in pre['builder']['frames'] if f['T_K'] == 1400.0)
    assert r(b1400['LIQUID']['g'][30], 2) == -20290.64 and r(b1400['mixing'][40], 0) == -7834.0


# --- the melting lens (steps 10-14) -------------------------------------------------
def test_lens_models_are_step_03_part_c():
    models = d.lens_models()
    for x in (0.05, 0.4, 0.95):
        for phase in ('SOLID', 'LIQUID'):
            assert float(models[phase].g(x)) == pytest.approx(tp.lens_g(phase, x, 1400.0), abs=1e-9)
    for phase in ('SOLID', 'LIQUID'):           # endpoint-safe: pure ends are the end line, no log(0)
        assert math.isfinite(float(models[phase].g(0.0))) and math.isfinite(float(models[phase].g(1.0)))


def test_hook_and_s1_numbers(data):
    L = data['lens']
    assert L['hook']['used'] == [{'phase': 'SOLID', 'x': 0.4, 'f': 1.0, 'g': pytest.approx(-20434.0577, abs=1e-4)}]
    assert r(L['hook']['G_up'], 2) == -20434.06
    assert r(L['truth']['G'], 2) == -20473.12
    assert r(L['hook']['above_truth'], 1) == 39.1
    assert L['hook']['line']['d_mu'] == 0.0          # degenerate: z sits on a used dot
    s1 = L['s1']
    assert [(u['phase'], u['x'], r(u['f'], 12)) for u in s1['used']] == [('SOLID', 0.5, 0.5), ('LIQUID', 0.3, 0.5)]
    assert r(s1['G_up'], 2) == -20429.54
    assert r(s1['above_hook'], 1) == 4.5
    assert (r(L['truth']['x_LIQUID'], 3), r(L['truth']['x_SOLID'], 3)) == (0.312, 0.441)


def test_s2_s3_s4_line_numbers(data):
    L = data['lens']
    dots = {(p['phase'], p['x']): p['g'] for p in L['menu']['dots']}
    assert (r(dots[('SOLID', 0.5)], 2), r(dots[('LIQUID', 0.3)], 2)) == (-20568.44, -20290.64)
    s2 = L['s2']
    assert r(s2['d_mu'], 1) == -1389.0 and r(s2['mu_A'], 1) == -19873.9 and r(s2['mu_B'], 1) == -21262.9
    assert s2['mu_A'] + s2['d_mu'] * 0.4 == pytest.approx(L['s1']['G_up'], abs=1e-8)      # strong duality
    assert r(L['s3']['nudge_energy'], 1) == -13.9
    assert (r(L['s3']['true_line']['mu_A'], 1), r(L['s3']['true_line']['d_mu'], 1)) == (-19760.0, -1782.8)
    gaps = {(g['phase'], g['x']): g['gap'] for g in L['s4']['gaps']}
    assert r(gaps[('SOLID', 0.3)], 1) == 480.0 and r(gaps[('LIQUID', 0.5)], 1) == 800.0
    assert gaps[('SOLID', 0.5)] == pytest.approx(0, abs=1e-8) and gaps[('LIQUID', 0.3)] == pytest.approx(0, abs=1e-8)
    assert min(gaps.values()) > -1e-8                   # dual feasible over the menu


def test_s5_ranging_and_s5b(data):
    L = data['lens']
    inside = [f for f in L['s5']['frames'] if 0.3 < f['z'] < 0.5]
    for frame in inside:
        assert frame['line']['d_mu'] == pytest.approx(L['s2']['d_mu'], abs=1e-6)
        assert sorted(u['x'] for u in frame['used']) == [0.3, 0.5]
    outside = next(f for f in L['s5']['frames'] if f['z'] == 0.6)
    assert sorted(u['x'] for u in outside['used']) != [0.3, 0.5]
    for frame in L['s5b']['frames']:
        assert frame['x_LIQUID'] < frame['x_SOLID']
        assert sum(u['f'] for u in frame['used']) == pytest.approx(1, abs=1e-10)


def test_s6_column_generation(data):
    it = data['lens']['s6']['iterations']
    first = it[0]
    assert (r(first['dips']['SOLID']['x'], 4), r(first['dips']['SOLID']['depth'], 1)) == (0.4489, -61.2)
    assert (r(first['dips']['LIQUID']['x'], 4), r(first['dips']['LIQUID']['depth'], 1)) == (0.3197, -10.5)
    second = it[1]
    used = {(u['phase'], r(u['x'], 4)): r(u['f'], 3) for u in second['used']}
    assert used == {('LIQUID', 0.3): 0.328, ('SOLID', 0.4489): 0.672}
    assert r(second['G_up'], 2) == -20470.64
    assert (r(second['line']['mu_A'], 1), r(second['line']['d_mu'], 1)) == (-19750.7, -1800.0)
    remaining = [x['remaining'] for x in it]
    assert [r(v, 2) for v in remaining[:3]] == [61.18, 3.99, 1.55]
    assert r(remaining[3], 4) == 0.0027 and r(remaining[4], 4) == 0.0015   # two more additions after the first, then a fourth
    ups = [x['G_up'] for x in it]
    assert all(b <= a + 1e-9 for a, b in zip(ups, ups[1:]))          # the ceiling never rises
    truth = data['lens']['truth']['G']
    for x in it:
        assert x['G_low_raw'] <= truth + 1e-8 <= x['G_up'] + 2e-8      # floor below, ceiling above the truth
    assert it[-1]['G_up'] == pytest.approx(truth, abs=1e-6)           # the closed-form control


def test_s7_bounds_and_spacing(data):
    s7 = data['lens']['s7']
    assert r(s7['G_low'], 2) == -20490.72 and r(s7['remaining'], 1) == 61.2
    assert [r(s['remaining'], p) for s, p in zip(s7['spacing'], (2, 2, 2, 4))] == [61.18, 51.97, 1.99, 0.0095]
    truth = data['lens']['truth']['G']
    for s in s7['spacing']:
        assert s['G_low'] <= truth <= s['G_up']                          # a grid answer is never below the truth
    assert r(data['lens']['RT'], 0) == 11640.0


def test_reveal_pivots_until_the_contacts_bracket_z(data):
    frames = data['lens']['reveal']['frames']
    dots = data['lens']['menu']['dots']
    names = [(dots[f['touch'][-1]]['phase'], dots[f['touch'][-1]]['x']) for f in frames]
    assert names == [('SOLID', 0.9), ('SOLID', 0.7), ('SOLID', 0.5), ('LIQUID', 0.3)]
    assert [r(f['d_mu'], 3) for f in frames] == [20000.0, 17632.902, 5788.987, -1388.987]
    for f in frames:                                  # every frame is a floor for the menu
        assert all(p['g'] >= f['mu_A'] + f['d_mu'] * p['x'] - 1e-8 for p in dots)


def test_bad_seed_is_infeasible_and_pure_ends_work():
    models = d.lens_models()
    with pytest.raises(ValueError):
        d.solve_master(d.menu_states(models, [0.6, 0.8]), 0.4)        # every dot right of z: no mixture makes z
    hist = d.column_generation(models, d.menu_states(models, [0.0, 1.0]), 0.4, tol=1e-9, max_iter=40)
    assert hist[-1].master.G_up == pytest.approx(export.lens()['truth']['G'], abs=1e-6)


# --- the regular solution (steps 15-17) ---------------------------------------------
def test_regular_model_is_step_03_part_b():
    alpha = d.regular_models()['ALPHA']
    for x in (0.0, 0.07, 0.5, 1.0):
        assert float(alpha.g(x)) == pytest.approx(float(d.bf.regular_properties(800.0, x)['GM']), abs=1e-9)


def test_s8_numbers(data):
    R = data['regular']
    s8 = R['s8']
    assert r(s8['tangent']['d_mu'], 1) == 14462.1 and r(s8['tangent']['g'], 1) == -5461.7
    assert r(s8['dip']['x'], 3) == 0.958 and r(s8['dip']['depth'], 1) == -2082.0
    assert s8['dip']['x_print'] == 0.958 and r(s8['dip']['g_print'], 1) == 4141.7
    assert [r(c, 0) for c in (R['curvature']['0.15'], R['curvature']['0.5'])] == [12169.0, -13394.0]
    assert [r(v, 3) for v in R['binodal']] == [0.070, 0.930]
    assert [r(v, 3) for v in R['spinodal']] == [0.211, 0.789]
    assert r(R['Tc_K'], 0) == 1203.0
    ends = {p['start']: r(p['end'], 3) for p in s8['local_search']}
    assert ends[0.15] == 0.15 and ends[0.05] == 0.15 and ends[0.5] == 0.958 and ends[0.9] == 0.958


def test_s8b_degenerate_master_and_convergence(data):
    s8b = data['regular']['s8b']
    it = s8b['iterations']
    assert it[0]['line_label'].startswith('chosen for illustration')
    flat = it[1]
    assert flat['line_label'] == 'returned by the solver'
    assert flat['used'] == [{'phase': 'ALPHA', 'x': 0.15, 'f': 1.0, 'g': pytest.approx(-5461.6918, abs=1e-4)}]
    assert flat['line']['d_mu'] == 0.0
    assert (r(flat['best']['x'], 3), r(flat['best']['depth'], 1)) == (0.008, -1593.6)
    assert r(s8b['dual_slope_max'], 0) == 11885.0
    assert (r(s8b['two_dot_line']['dip']['x'], 3), r(s8b['two_dot_line']['dip']['depth'], 1)) == (0.068, -132.7)
    final = sorted(u['x'] for u in s8b['final']['used'])
    assert [r(v, 3) for v in final] == [0.070, 0.930]                 # two ALPHA states kept apart
    assert {u['phase'] for u in s8b['final']['used']} == {'ALPHA'}
    below = next(x for x in it if x['remaining'] < 0.01)
    assert below['k'] - flat['k'] == 4                                 # four more iterations after the flat line


def test_s9_branch_and_bound(data):
    s9 = data['regular']['s9']
    assert s9['status'] == 'proved'
    leaves = s9['leaves']
    assert leaves[0]['lo'] == 0.0 and leaves[-1]['hi'] == 1.0
    assert all(a['hi'] == b['lo'] for a, b in zip(leaves, leaves[1:]))
    assert all(l['floor'] >= -s9['eps'] for l in leaves)
    assert s9['G_low'] == pytest.approx(s9['line_at_z'] + min(0.0, s9['lowest_floor']))
    assert s9['line_at_z'] - s9['eps'] <= s9['G_low'] <= s9['G_up']
    assert s9['remaining'] <= s9['eps']
    assert r(s9['width_scale'], 3) == 0.014
    u = s9['unresolved']
    assert u['status'] == 'unresolved' and len(u['nodes']) == u['max_nodes'] == 9
    opened = [l for l in u['leaves'] if l['action'] == 'open']
    assert len(opened) == 4 and all(l['floor'] is None for l in opened)      # never examined: no floor
    assert all(l['floor'] >= -s9['eps'] for l in u['leaves'] if l['action'] == 'prune')
    assert s9['verifier']['accepted'] and not any(p['accepted'] for p in s9['verifier']['perturbed'])
    found = data['regular']['s9_discovery']['found']
    assert (r(found['x'], 2), r(found['gap_at_x'], 0)) == (0.96, -2082.0)


def test_chord_floor_is_below_the_gap_and_follows_the_line(data):
    alpha = d.regular_models()['ALPHA']
    s9 = data['regular']['s9']
    for n in s9['nodes']:
        xs = np.linspace(n['lo'], n['hi'], 41)
        gap = alpha.g(xs) - s9['line']['mu_A'] - s9['line']['d_mu'] * xs
        assert n['floor'] <= gap.min() + 1e-9                           # an implementation test, not the proof
        assert n['gap_at_x'] - n['floor'] <= d.looseness(alpha, n['lo'], n['hi']) + 1e-9   # at most w h^2/4 loose
    tangent = data['regular']['s8']['tangent']
    a = d.chord_floor(alpha, s9['line']['mu_A'], s9['line']['d_mu'], 0.9, 1.0)[0]
    b = d.chord_floor(alpha, tangent['mu_A'], tangent['d_mu'], 0.9, 1.0)[0]
    assert a != b                                                        # floors belong to one line: recompute when it moves


def test_width_is_a_scale_not_a_guarantee():
    alpha = d.regular_models()['ALPHA']
    left = d.bf.regular_binodal(800.0)['compositions'][0]
    mu_a = float(alpha.g(left)) - float(alpha.slope(left)) * left
    d_mu = float(alpha.slope(left))
    h = 2 * math.sqrt(1.0 / alpha.w)
    exact = d.chord_floor(alpha, mu_a, d_mu, left - h / 2, left + h / 2)[0]
    raised = d.chord_floor(alpha, mu_a + 0.005, d_mu, left - h / 2, left + h / 2)[0]
    assert r(exact, 3) == -1.0 and r(raised, 3) == -1.005                 # floor -eps - delta at that width
    safe = 2 * math.sqrt((1.0 - 0.005) / alpha.w) * 0.999
    assert d.chord_floor(alpha, mu_a + 0.005, d_mu, left - safe / 2, left + safe / 2)[0] > -1.0


def test_joint_case(data):
    joint = data['regular']['joint']
    a, b = joint['dips_at_half']
    assert a['depth'] == pytest.approx(b['depth'], abs=1e-6)            # two equal dips at z = 0.50
    assert (r(a['x'], 3), r(b['x'], 3)) == (0.070, 0.930)
