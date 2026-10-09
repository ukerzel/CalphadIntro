"""Export every printed number and animation frame of advanced steps 10-17.

All values come from course/self_study/day3_core.py, which reuses the step 03
models (the part C melting lens and the part B regular solution); nothing here
is a new model. The browser draws these values and does only display
arithmetic on them (a line subtracted from exported energies, the lever rule
on exported dots); it never evaluates a Gibbs model.

Run from the repository root:
    .venv/bin/python -m course.self_study.day3_export
"""
from __future__ import annotations

import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np

from course.self_study import day3_core as d
from course.self_study import two_phase_export as tp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'day3.json'
PREWORK = HERE / 'generated' / 'day3_prework.json'   # steps 07-09 (kept apart: steps 10-18 do not need it)
MENU_X = [0.1, 0.3, 0.5, 0.7, 0.9]           # the S1 menu, both phase models; z = 0.40 is not on it
HOOK_X = [0.2, 0.4, 0.6, 0.8]                # step 03 part D's coarsest grid (n = 5)
SPACING = [(0.2, [round(0.1 + 0.2 * i, 3) for i in range(5)]),
           (0.1, [round(0.05 + 0.1 * i, 3) for i in range(10)]),
           (0.02, [round(0.01 + 0.02 * i, 3) for i in range(50)]),
           (0.002, [round(0.001 + 0.002 * i, 4) for i in range(500)])]   # not nested; z never on a menu
LENS_CURVE_X = [i / 400 for i in range(401)]
REG_CURVE_X = [i / 1000 for i in range(1001)]
T_SLIDER = sorted([1010.0 + 20 * i for i in range(40)] + [1400.0])  # 1010 ... 1790 K and the pages' 1400 K
T_CURVE_X = [i / 100 for i in range(101)]
Z_SLIDER = [round(0.10 + 0.01 * i, 2) for i in range(81)]
REVEAL_SLOPE = 20000.0
NUDGE = 0.01
EPS = 1.0                                    # J/mol atoms, the B&B tolerance
LOCAL_STARTS = [0.05, 0.15, 0.3, 0.5, 0.7, 0.9]


def _f(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('nonfinite value')
    return number + 0.0   # no negative zero in the export


def used(master: d.Master) -> list[dict]:
    return [{'phase': s.phase, 'x': _f(s.x), 'f': _f(f), 'g': _f(s.g)} for s, f in master.used()]


def line(master_or_pair) -> dict:
    mu_a, d_mu = (master_or_pair.mu_A, master_or_pair.d_mu) if isinstance(master_or_pair, d.Master) else master_or_pair
    return {'mu_A': _f(mu_a), 'd_mu': _f(d_mu), 'mu_B': _f(mu_a + d_mu)}


def dip(value: d.Dip) -> dict:
    return {'phase': value.phase, 'x': _f(value.x), 'depth': _f(value.depth)}


def iteration(it: d.Iteration, label: str) -> dict:
    return {'k': it.k, 'states': [{'phase': s.phase, 'x': _f(s.x), 'g': _f(s.g)} for s in it.master.states],
            'used': used(it.master), 'G_up': _f(it.master.G_up), 'line': line(it.master), 'line_label': label,
            'dips': {p: dip(v) for p, v in it.dips.items()}, 'best': dip(it.best),
            'G_low_raw': _f(it.G_low_raw), 'G_low_best': _f(it.G_low_best), 'remaining': _f(it.gap)}


def dip_window(model: d.PhaseModel, mu_a: float, d_mu: float, at: d.Dip, points: int = 61) -> dict:
    """The gap curve sampled finely around a dip, wide enough to show where it crosses zero (for zooming in)."""
    curv = float(model.curvature(min(max(at.x, 1e-6), 1 - 1e-6)))
    half = max(3 * math.sqrt(2 * abs(at.depth) / curv), 2e-4) if curv > 0 else 0.02
    lo, hi = max(at.x - half, 0.0), min(at.x + half, 1.0)
    xs = np.linspace(lo, hi, points)
    return {'x': [_f(v) for v in xs], 'gap': [_f(v) for v in model.g(xs) - mu_a - d_mu * xs]}


def node(n: d.Node) -> dict:
    opt = lambda v: None if v is None else _f(v)
    return {'n': n.n, 'lo': _f(n.lo), 'hi': _f(n.hi), 'floor': opt(n.floor), 'x': opt(n.x_floor),
            'gap_at_x': opt(n.gap_at_x), 'action': n.action}


# ---------------------------------------------------------------------------
# Steps 10–14: the melting lens at 1400 K, z = 0.40.
# ---------------------------------------------------------------------------
def lens() -> dict:
    T, z = d.LENS_T, d.LENS_Z
    models = d.lens_models(T)
    x_s, x_l = tp.lens_coexistence(T)
    f_l, f_s = d.lever(z, x_l, x_s)
    truth_G = f_l * float(models['LIQUID'].g(x_l)) + f_s * float(models['SOLID'].g(x_s))
    true_d_mu = float(models['SOLID'].slope(x_s))
    true_mu_a = float(models['SOLID'].g(x_s)) - true_d_mu * x_s
    if abs(true_mu_a + true_d_mu * z - truth_G) > 1e-8:
        raise ValueError('the true common tangent does not pass through the equilibrium energy')

    hook_master = d.solve_master(d.menu_states(models, HOOK_X), z)
    menu = d.menu_states(models, MENU_X)
    s1 = d.solve_master(menu, z)
    if [(s.phase, s.x) for s, _ in s1.used()] != [('SOLID', 0.5), ('LIQUID', 0.3)]:
        raise ValueError('the S1 menu no longer chooses SOLID 0.5 and LIQUID 0.3')
    if any(s.g < s1.line(s.x) - 1e-9 for s in menu):
        raise ValueError('a menu dot lies below the S1 line')
    if abs(float(s1.line(z)) - s1.G_up) > 1e-8:
        raise ValueError('strong duality fails for the S1 menu')
    best, dips = d.deepest(models, s1.mu_A, s1.d_mu)
    s7_low = d.floor(float(s1.line(z)), best.depth)
    if not s7_low <= truth_G <= s1.G_up:
        raise ValueError('the S7 floor and ceiling do not bracket the true answer')

    cg = d.column_generation(models, menu, z, tol=1e-9, max_iter=8)
    if abs(cg[-1].master.G_up - truth_G) > 1e-6:
        raise ValueError('column generation does not reach the closed-form lens answer')

    z_frames = []
    for zz in Z_SLIDER:
        m = d.solve_master(menu, zz)
        z_frames.append({'z': zz, 'used': used(m), 'G_up': _f(m.G_up), 'line': line(m)})
    t_frames = []
    for t in T_SLIDER:
        mt = d.lens_models(t)
        xs_t, xl_t = tp.lens_coexistence(t)
        m = d.solve_master(d.menu_states(mt, MENU_X), z)
        t_frames.append({'T_K': t, 'x_SOLID': _f(xs_t), 'x_LIQUID': _f(xl_t), 'used': used(m),
                         'g': {p: [_f(v) for v in mt[p].g(np.array(T_CURVE_X))] for p in ('SOLID', 'LIQUID')}})
    spacing = []
    for step, xs in SPACING:
        if z in xs:
            raise ValueError('z must not be on a spacing menu')
        m = d.solve_master(d.menu_states(models, xs), z)
        b, _ = d.deepest(models, m.mu_A, m.d_mu)
        low = d.floor(float(m.line(z)), b.depth)
        spacing.append({'spacing': step, 'dots_per_phase': len(xs), 'G_up': _f(m.G_up), 'G_low': _f(low),
                        'remaining': _f(m.G_up - low), 'used': used(m)})
    reveal = d.lift_and_pivot(menu, z, REVEAL_SLOPE)
    if abs(reveal[-1]['mu_A'] - s1.mu_A) > 1e-6 or abs(reveal[-1]['d_mu'] - s1.d_mu) > 1e-6:
        raise ValueError('the reveal animation does not end on the S1 line')

    return {
        'T_K': T, 'z': z, 'RT': _f(d.R * T),
        'models': {p: {'a': _f(m.a), 'b': _f(m.b)} for p, m in models.items()},
        'curve': {'x': LENS_CURVE_X, **{p: [_f(v) for v in m.g(np.array(LENS_CURVE_X))] for p, m in models.items()}},
        'truth': {'x_LIQUID': _f(x_l), 'x_SOLID': _f(x_s), 'f_LIQUID': _f(f_l), 'f_SOLID': _f(f_s), 'G': _f(truth_G),
                  'line': line((true_mu_a, true_d_mu))},
        'hook': {'x': HOOK_X, 'dots': [{'phase': s.phase, 'x': s.x, 'g': _f(s.g)} for s in hook_master.states],
                 'used': used(hook_master), 'G_up': _f(hook_master.G_up), 'line': line(hook_master),
                 'above_truth': _f(hook_master.G_up - truth_G)},
        'menu': {'x': MENU_X, 'dots': [{'phase': s.phase, 'x': s.x, 'g': _f(s.g)} for s in menu]},
        's1': {'used': used(s1), 'G_up': _f(s1.G_up), 'above_hook': _f(s1.G_up - hook_master.G_up),
               'above_truth': _f(s1.G_up - truth_G)},
        's2': line(s1),
        's3': {'nudge': NUDGE, 'nudge_energy': _f(s1.d_mu * NUDGE), 'true_line': line((true_mu_a, true_d_mu))},
        's4': {'gaps': [{'phase': s.phase, 'x': s.x, 'gap': _f(s.g - s1.line(s.x))} for s in menu]},
        's5': {'range': [0.3, 0.5], 'frames': z_frames},
        's5b': {'z': z, 'x': T_CURVE_X, 'frames': t_frames},
        's6': {'seed': 'the S1 menu', 'iterations': [{**iteration(it, 'returned by the solver'),
                                                       'windows': {p: dip_window(models[p], it.master.mu_A, it.master.d_mu, v) for p, v in it.dips.items()}}
                                                      for it in cg]},
        's7': {'G_up': _f(s1.G_up), 'G_low': _f(s7_low), 'remaining': _f(s1.G_up - s7_low), 'dips': {p: dip(v) for p, v in dips.items()},
               'spacing': spacing},
        'reveal': {'start_slope': REVEAL_SLOPE, 'frames': reveal},
    }


# ---------------------------------------------------------------------------
# Steps 15–17: the regular solution at 800 K, z = 0.15.
# ---------------------------------------------------------------------------
def regular() -> dict:
    T, z = d.REG_T, d.REG_Z
    models = d.regular_models(T)
    alpha = models['ALPHA']
    gap = d.bf.regular_binodal(T)
    left, right = gap['compositions']
    spin_left, spin_right = gap['spinodal']
    if not left < z < spin_left:
        raise ValueError('z = 0.15 is no longer between binodal and spinodal')
    curv = {str(v): _f(alpha.curvature(v)) for v in (0.15, 0.5)}
    if not (curv['0.15'] > 0 > curv['0.5']):
        raise ValueError('expected metastable at 0.15 and unstable at 0.50')

    g_z = float(alpha.g(z))
    t_slope = float(alpha.slope(z))
    t_mu_a = g_z - t_slope * z
    s8_dip = d.price_scan(alpha, t_mu_a, t_slope)
    x_print = round(s8_dip.x, 3)
    paths = []
    for start in LOCAL_STARTS:
        p = d.local_descent(alpha, t_mu_a, t_slope, start)
        paths.append({'start': start, 'path': [_f(v) for v in p], 'end': _f(p[-1]),
                      'gap_end': _f(alpha.g(p[-1]) - t_mu_a - t_slope * p[-1])})

    seed = [d.State('ALPHA', z, g_z)]
    cg = d.column_generation(models, seed, z, tol=1e-9, max_iter=12,
                             line=lambda m, k: (t_mu_a, t_slope) if k == 0 else (m.mu_A, m.d_mu))
    labels = ['chosen for illustration: the tangent at 0.15 (a one-state master leaves the slope free)'] + \
             ['returned by the solver'] * (len(cg) - 1)
    second = cg[1].master.states[1]
    two_dot = ((second.g - g_z) / (second.x - z))
    two_dot_mu_a = g_z - two_dot * z
    final = cg[-1].master
    final_x = sorted(s.x for s, _ in final.used())
    if abs(final_x[0] - left) > 1e-5 or abs(final_x[1] - right) > 1e-5:
        raise ValueError('column generation does not reach the binodal')

    proof = d.branch_and_bound(alpha, final.mu_A, final.d_mu, eps=EPS)
    if proof.status != 'proved':
        raise ValueError('the completion B&B did not close every interval')
    line_at_z = float(final.line(z))
    g_low = proof.G_low(line_at_z)
    if not line_at_z - EPS <= g_low <= final.G_up:
        raise ValueError('the B&B floor is outside [line - eps, ceiling]')
    unresolved = d.branch_and_bound(alpha, final.mu_A, final.d_mu, eps=EPS, max_nodes=9)
    discovery = d.bb_deepest(alpha, t_mu_a, t_slope, tol=EPS)

    answer = d.Answer([(s.phase, s.x, f) for s, f in final.used()], final.mu_A, final.d_mu,
                      [(nd.lo, nd.hi) for nd in proof.leaves], EPS, z, EPS, final.G_up, g_low)
    ok, problems = d.verify(answer, alpha)
    if not ok:
        raise ValueError(f'the verifier rejects the final answer: {problems}')
    perturbed = []
    for change, edit in (('one interval removed', dict(intervals=answer.intervals[1:])),
                         ('the line raised by 2 J/mol', dict(mu_A=answer.mu_A + 2.0)),
                         ('a claimed floor 1 J/mol higher', dict(claimed_G_low=answer.claimed_G_low + 1.0))):
        bad = d.Answer(**{**answer.__dict__, **edit})
        ok_bad, why = d.verify(bad, alpha)
        if ok_bad:
            raise ValueError(f'the verifier accepts a perturbed answer: {change}')
        perturbed.append({'change': change, 'accepted': ok_bad, 'problems': why})

    half = 0.5
    joint_slope = float(alpha.slope(half))
    joint_mu_a = float(alpha.g(half)) - joint_slope * half
    joint_dips = [d.price_scan(alpha, joint_mu_a, joint_slope)]
    mirror = d.Dip('ALPHA', 1 - joint_dips[0].x, float(alpha.g(1 - joint_dips[0].x) - joint_mu_a - joint_slope * (1 - joint_dips[0].x)))
    joint_dips.append(mirror)

    return {
        'T_K': T, 'z': z, 'omega': _f(alpha.w), 'Tc_K': _f(d.bf.TC_R1), 'RT': _f(d.R * T),
        'model': {'a': _f(alpha.a), 'b': _f(alpha.b), 'w': _f(alpha.w)},
        'curve': {'x': REG_CURVE_X, 'ALPHA': [_f(v) for v in alpha.g(np.array(REG_CURVE_X))]},
        'binodal': [_f(left), _f(right)], 'spinodal': [_f(spin_left), _f(spin_right)], 'curvature': curv,
        's8': {'tangent': {**line((t_mu_a, t_slope)), 'x': z, 'g': _f(g_z)},
               'dip': {**dip(s8_dip), 'g': _f(alpha.g(s8_dip.x)), 'x_print': x_print, 'g_print': _f(alpha.g(x_print))},
               'local_search': paths},
        's8b': {'iterations': [{**iteration(it, label), 'line_label': label,
                                'windows': {'ALPHA': dip_window(alpha, it.master.mu_A, it.master.d_mu, it.best)}} for it, label in zip(cg, labels)],
                'two_dot_line': {**line((two_dot_mu_a, two_dot)), 'through': [z, _f(second.x)],
                                 'dip': dip(d.price_scan(alpha, two_dot_mu_a, two_dot)), 'label': 'chosen for illustration'},
                'dual_slope_max': _f(two_dot),
                'final': {'used': used(final), 'G_up': _f(final.G_up), 'line': line(final)}},
        's9': {'eps': EPS, 'line': line(final), 'G_up': _f(final.G_up), 'line_at_z': _f(line_at_z),
               'nodes': [node(n) for n in proof.nodes], 'leaves': [node(n) for n in proof.leaves],
               'status': proof.status, 'lowest_floor': _f(proof.m), 'G_low': _f(g_low), 'remaining': _f(final.G_up - g_low),
               'width_scale': _f(2 * math.sqrt(EPS / alpha.w)),
               'unresolved': {'max_nodes': 9, 'status': unresolved.status, 'nodes': [node(n) for n in unresolved.nodes],
                              'leaves': [node(n) for n in unresolved.leaves]},
               'verifier': {'accepted': ok, 'perturbed': perturbed}},
        's9_discovery': {'line': line((t_mu_a, t_slope)), 'tol': EPS, 'nodes': [node(n) for n in discovery.nodes],
                         'found': node(discovery.found), 'status': discovery.status},
        'joint': {'z': [z, half], 'line_at_half': line((joint_mu_a, joint_slope)),
                  'dips_at_half': [dip(v) for v in joint_dips]},
    }


# ---------------------------------------------------------------------------
# Preparation steps 07-09: second law, counting arrangements, building g(x), the Omega bump.
# ---------------------------------------------------------------------------
UNARY_T = [800.0 + 50 * i for i in range(13)]        # 800 ... 1400 K
COUNT_N = [10, 20, 50, 100, 200, 500, 1000]
BUILD_T = [1000.0 + 50 * i for i in range(17)]       # 1000 ... 1800 K
BUILD_X = [i / 100 for i in range(101)]
OMEGA_RT = sorted([round(0.1 * i, 1) for i in range(41)] + [round(20000 / (d.R * 800), 4)])  # 0 to 4, and the 800 K value of steps 15–17
OMEGA_X = [i / 200 for i in range(201)]


def prework() -> dict:
    # Melting pure A (step 01's lines): solid 1000 - 10 T, liquid 7000 - 16 T, J/mol.
    second_law = []
    for t in UNARY_T:
        dh, ds = 6000.0, 6.0                          # liquid minus solid
        second_law.append({'T_K': t, 'dH': dh, 'dS_sample': ds, 'dS_bath': _f(-dh / t), 'dS_total': _f(ds - dh / t), 'dG': _f(dh - t * ds)})
    counting = []
    for n in COUNT_N:
        ks = list(range(n + 1))
        ln_w = [math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) for k in ks]
        counting.append({'N': n, 'k': ks, 'lnW_per_N': [_f(v / n) for v in ln_w],
                         'limit': [_f(-float(d.q(k / n))) for k in ks]})
    builder = []
    xs = np.array(BUILD_X)
    for t in BUILD_T:
        models = d.lens_models(t)
        builder.append({'T_K': t, 'mixing': [_f(v) for v in d.R * t * d.q(xs)],
                        **{p: {'end_line': [_f(v) for v in m.a + m.b * xs], 'g': [_f(v) for v in m.g(xs)]} for p, m in models.items()}})
    omega = []
    ox = np.array(OMEGA_X)
    for a in OMEGA_RT:
        curve = d.q(ox) + a * ox * (1 - ox)            # mixing part of g, in units of RT
        row = {'omega_over_RT': a, 'g_mix_over_RT': [_f(v) for v in curve], 'spinodal': [], 'binodal': []}
        if a > 2:
            sp = (1 - math.sqrt(1 - 2 / a)) / 2
            from scipy.optimize import brentq
            left = brentq(lambda v: math.log(v / (1 - v)) + a * (1 - 2 * v), 1e-300, sp)
            row.update(spinodal=[_f(sp), _f(1 - sp)], binodal=[_f(left), _f(1 - left)])
        omega.append(row)
    return {'second_law': {'model': 'pure A from step 01: solid 1000 - 10 T, liquid 7000 - 16 T (J/mol)', 'frames': second_law},
            'counting': counting, 'builder': {'x': BUILD_X, 'frames': builder},
            'omega': {'x': OMEGA_X, 'frames': omega}}


def build() -> dict:
    data = {
        'schema_version': 1,
        'description': 'The advanced steps: the melting lens (steps 10-14) and the regular solution (steps 15-17). '
                       'Energies J/mol of atoms; x and z are B atom fractions; lines are mu_A + d_mu x.',
        'units': {'energy': 'J/mol atoms', 'x': 'B atom fraction', 'f': 'mol atoms per mol sample', 'T': 'K'},
        'conditions': {'P_Pa': 100000, 'R': d.R},
        'environment': {'python': platform.python_version(), 'numpy': version('numpy'), 'scipy': version('scipy')},
        'lens': lens(),
        'regular': regular(),
    }
    json.dumps(data, allow_nan=False)
    return data


def build_prework() -> dict:
    data = {'schema_version': 1,
            'description': 'The advanced steps pre-work pages: the second law for melting pure A, counting arrangements, '
                           'building g(x) for the lens, and the regular-solution mixing curve for a range of Omega/RT.',
            'units': {'energy': 'J/mol atoms', 'entropy': 'J/(mol K)', 'x': 'B atom fraction'},
            **prework()}
    json.dumps(data, allow_nan=False)
    return data


def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)
    for path, data in ((OUTPUT, build()), (PREWORK, build_prework())):
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False, allow_nan=False) + '\n')
        print(f'wrote {path.relative_to(HERE.parents[1])} ({path.stat().st_size // 1024} kB)')


if __name__ == '__main__':
    main()
