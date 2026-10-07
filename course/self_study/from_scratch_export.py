"""Export the self-study "from scratch vs pycalphad" frames (step 03, part D).

The model is the part C melting lens of two_phase_export: invented components A
and B, ideal SOLID and LIQUID solutions. At 1400 K and overall B fraction
z = 0.40 the frames show four ways to the same equilibrium, the same route as
notebooks/f4b_lens_from_scratch: every split, a grid with a linear programme,
Newton's method on the equal-chemical-potential equations, and continuation in
T for the lens. pycalphad solves the same model from a TDB string; its sampled
points, equilibrium and lens are exported next to the from-scratch values.
Energies are J/mol of atoms; "relative" energies are measured from the common
tangent of the 1400 K answer, (1 - x) mu_A + x mu_B. Subtracting a straight line
moves no touching point and keeps every chord and tangent straight; it makes the
answer the horizontal line at zero, so differences of a few J/mol are visible.

Run from the repository root:
    .venv/bin/python -m course.self_study.from_scratch_export
"""
from __future__ import annotations

import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from course.self_study import two_phase_export as tp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'from_scratch.json'
R = 8.3145  # J/(mol K), the value pycalphad uses
T0, Z0, P = 1400.0, 0.40, 100000.0
VIEW_X = (0.15, 0.65)                                               # composition window the lab draws
CURVE_X = [round(0.15 + 0.005 * i, 3) for i in range(101)]
BRUTE_X = [round(0.41 + 0.01 * i, 2) for i in range(20)]          # trial SOLID compositions
BRUTE_PARTNERS = np.linspace(0.001, 0.399, 399)                     # LIQUID partners, all below z
GRID_STEPS = [5, 10, 20, 50, 100, 500, 1000]                       # grid x = 1/n, 2/n, ..., (n-1)/n
DRAWN_UP_TO = 100                                                   # finer grids are too dense to draw point by point
NEWTON_START = (0.62, 0.20)
SAMPLE_EVERY = 20                                                   # thin pycalphad's sampled points for drawing
TDB = """
ELEMENT A BLANK 1.0 0.0 0.0 !
ELEMENT B BLANK 1.0 0.0 0.0 !
TYPE_DEFINITION % SEQ * !
PHASE SOLID % 1 1 !
CONSTITUENT SOLID :A,B: !
PARAMETER G(SOLID,A;0) 300 1000-10*T; 3000 N !
PARAMETER G(SOLID,B;0) 300 2000-10*T; 3000 N !
PHASE LIQUID % 1 1 !
CONSTITUENT LIQUID :A,B: !
PARAMETER G(LIQUID,A;0) 300 7000-16*T; 3000 N !
PARAMETER G(LIQUID,B;0) 300 20000-20*T; 3000 N !
"""


def _f(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('nonfinite value')
    return number


# pycalphad's last digits vary from run to run (about 1e-15 in x, 1e-10 J/mol in energy); store them rounded.
def _x(value) -> float:
    return round(_f(value), 12)


def _e(value) -> float:
    return round(_f(value), 6)


def _small(value) -> float:
    return float(f'{_f(value):.2e}')


def g0(component: str, phase: str, t: float) -> float:
    return tp.lens_g0(component, phase, t)


def _tangent_ends() -> tuple[float, float]:
    x_s, _ = tp.lens_coexistence(T0)
    return mu('SOLID', x_s, T0)


def reference(x: float, t: float = T0) -> float:
    """Height of the 1400 K common tangent at x; every relative energy is measured from it."""
    mu_a, mu_b = _tangent_ends()
    return (1 - x) * mu_a + x * mu_b


def g(phase: str, x, t: float):
    x = np.asarray(x, dtype=float)
    return (1 - x) * g0('A', phase, t) + x * g0('B', phase, t) + R * t * (x * np.log(x) + (1 - x) * np.log(1 - x))


def g_rel(phase: str, x: float, t: float) -> float:
    return _f(g(phase, x, t) - reference(x, t))


def mu(phase: str, x: float, t: float) -> tuple[float, float]:
    return g0('A', phase, t) + R * t * math.log(1 - x), g0('B', phase, t) + R * t * math.log(x)


def tangent_rel(phase: str, x: float, t: float) -> list[float]:
    """Heights of the tangent at x, relative to the reference line, at x = 0 and x = 1."""
    mu_a, mu_b = mu(phase, x, t)
    return [_f(mu_a - reference(0.0)), _f(mu_b - reference(1.0))]


def lever_liquid(z: float, x_solid: float, x_liquid: float) -> float:
    return (z - x_solid) / (x_liquid - x_solid)


def residuals(x_solid: float, x_liquid: float, t: float) -> tuple[float, float]:
    (a_s, b_s), (a_l, b_l) = mu('SOLID', x_solid, t), mu('LIQUID', x_liquid, t)
    return a_s - a_l, b_s - b_l


def newton(start: tuple[float, float], t: float, tol: float = 1e-9) -> list[tuple[float, float]]:
    """Newton's method on the two equal-mu equations; returns every iterate."""
    v = np.array(start, dtype=float)
    path = [tuple(v)]
    for _ in range(50):
        f = np.array(residuals(*v, t))
        if np.abs(f).max() < tol:
            return path
        s, l = v
        jac = R * t * np.array([[-1 / (1 - s), 1 / (1 - l)], [1 / s, -1 / l]])
        v = v - np.linalg.solve(jac, f)
        if not (0 < v[0] < 1 and 0 < v[1] < 1):
            raise ValueError('Newton step left 0 < x < 1')
        path.append(tuple(v))
    raise ValueError('Newton did not converge')


def solve(t: float, guess: tuple[float, float]) -> tuple[float, float]:
    return newton(guess, t)[-1]


def curves() -> dict:
    return {'x': CURVE_X, 'SOLID': [g_rel('SOLID', x, T0) for x in CURVE_X], 'LIQUID': [g_rel('LIQUID', x, T0) for x in CURVE_X]}


def answer() -> dict:
    x_s, x_l = tp.lens_coexistence(T0)
    f_l = lever_liquid(Z0, x_s, x_l)
    gm = (1 - f_l) * float(g('SOLID', x_s, T0)) + f_l * float(g('LIQUID', x_l, T0))
    mu_a, mu_b = mu('SOLID', x_s, T0)
    return {'x_SOLID': _f(x_s), 'x_LIQUID': _f(x_l), 'f_LIQUID': _f(f_l), 'GM': _f(gm), 'GM_relative': _f(gm - reference(Z0, T0)),
            'mu_A': _f(mu_a), 'mu_B': _f(mu_b), 'tangent_relative': tangent_rel('SOLID', x_s, T0),
            'g_relative': {'SOLID': g_rel('SOLID', x_s, T0), 'LIQUID': g_rel('LIQUID', x_l, T0)},
            'homogeneous_GM': {phase: _f(g(phase, Z0, T0)) for phase in ('SOLID', 'LIQUID')},
            'homogeneous_GM_relative': {phase: g_rel(phase, Z0, T0) for phase in ('SOLID', 'LIQUID')}}


def brute() -> list[dict]:
    """For each trial SOLID composition, the LIQUID partner (on a 0.001 grid) that gives the lowest split energy."""
    frames = []
    for i, x_s in enumerate(BRUTE_X):
        f_l = lever_liquid(Z0, x_s, BRUTE_PARTNERS)
        energy = (1 - f_l) * g('SOLID', x_s, T0) + f_l * g('LIQUID', BRUTE_PARTNERS, T0)
        k = int(np.argmin(energy))
        x_l = float(BRUTE_PARTNERS[k])
        frames.append({'id': f'brute-{i:02d}', 'x_SOLID': x_s, 'x_LIQUID': round(x_l, 3), 'f_LIQUID': _f(f_l[k]), 'GM': _f(energy[k]),
                       'GM_relative': _f(energy[k] - reference(Z0, T0)),
                       'g_relative': {'SOLID': g_rel('SOLID', x_s, T0), 'LIQUID': g_rel('LIQUID', x_l, T0)}})
    return frames


def grid(exact_gm: float) -> list[dict]:
    frames = []
    for n in GRID_STEPS:
        xs = np.arange(1, n) / n
        m = len(xs)
        energies = np.concatenate([g('SOLID', xs, T0), g('LIQUID', xs, T0)])
        x_all = np.concatenate([xs, xs])
        result = linprog(energies, A_eq=[np.ones_like(x_all), x_all], b_eq=[1.0, Z0], bounds=(0, None), method='highs')
        if not result.success:
            raise ValueError('linprog failed')
        chosen = [{'phase': 'SOLID' if k < m else 'LIQUID', 'x': _f(x_all[k]), 'f': _f(result.x[k]),
                   'g_relative': g_rel('SOLID' if k < m else 'LIQUID', x_all[k], T0)} for k in np.flatnonzero(result.x > 1e-9)]
        if abs(sum(c['f'] for c in chosen) - 1) > 1e-9 or abs(sum(c['f'] * c['x'] for c in chosen) - Z0) > 1e-9:
            raise ValueError('grid split does not balance')
        drawn = n <= DRAWN_UP_TO
        frames.append({'id': f'grid-{n}', 'spacing': 1 / n, 'points': m, 'x': [_f(v) for v in xs] if drawn else [],
                       'g_relative': {phase: [g_rel(phase, v, T0) for v in xs] if drawn else [] for phase in ('SOLID', 'LIQUID')},
                       'chosen': chosen, 'GM': _f(result.fun), 'GM_relative': _f(result.fun - reference(Z0, T0)),
                       'above_exact': _f(result.fun - exact_gm)})
    return frames


def newton_frames() -> list[dict]:
    frames = []
    for i, (x_s, x_l) in enumerate(newton(NEWTON_START, T0)):
        r_a, r_b = residuals(x_s, x_l, T0)
        frames.append({'id': f'newton-{i}', 'iteration': i, 'x_SOLID': _f(x_s), 'x_LIQUID': _f(x_l),
                       'residual_mu_A': _f(r_a), 'residual_mu_B': _f(r_b),
                       'g_relative': {'SOLID': g_rel('SOLID', x_s, T0), 'LIQUID': g_rel('LIQUID', x_l, T0)},
                       'tangent_relative': {'SOLID': tangent_rel('SOLID', x_s, T0), 'LIQUID': tangent_rel('LIQUID', x_l, T0)}})
    return frames


def continuation() -> list[dict]:
    """Solve at 1400 K, then walk up to 1790 K and down to 1010 K, each solve starting from the previous answer."""
    start = tp.lens_coexistence(T0)
    rows, order = [], 0
    for temps in (np.arange(T0, 1800.0, 10.0), np.arange(T0 - 10, 1000.0, -10.0)):
        guess = start
        for t in temps:
            t = float(t)
            guess = solve(t, guess)
            exact = tp.lens_coexistence(t)
            if max(abs(guess[0] - exact[0]), abs(guess[1] - exact[1])) > 1e-9:
                raise ValueError('continuation differs from the closed form')
            rows.append({'id': f'walk-{order:02d}', 'T_K': t, 'x_SOLID': _f(guess[0]), 'x_LIQUID': _f(guess[1])})
            order += 1
    return rows


def pycalphad_part(walk: list[dict]) -> dict:
    from pycalphad import Database, calculate, equilibrium, variables as v
    db = Database(TDB)
    sample = {}
    for phase in ('SOLID', 'LIQUID'):
        calc = calculate(db, ['A', 'B'], phase, T=T0, P=P, N=1, output='GM')
        xb = calc.X.sel(component='B').values.reshape(-1)
        gm = calc.GM.values.reshape(-1)
        keep = [k for k in sorted(range(len(xb)), key=lambda k: xb[k]) if VIEW_X[0] <= xb[k] <= VIEW_X[1]]   # drawn window only
        sample[phase] = {'count': len(xb),
                         'x': [_f(xb[k]) for k in keep[::SAMPLE_EVERY]],
                         'g_relative': [_e(gm[k] - reference(xb[k], T0)) for k in keep[::SAMPLE_EVERY]]}

    def split(t: float, z: float) -> dict:
        eq = equilibrium(db, ['A', 'B'], ['SOLID', 'LIQUID'], {v.T: t, v.P: P, v.N: 1, v.X('B'): z})
        names = eq.Phase.values.squeeze()
        np_ = eq.NP.values.squeeze()
        xb = eq.X.sel(component='B').values.squeeze()
        regions = {str(n): (float(a), float(c)) for n, a, c in zip(names, np_, xb) if n}
        return {'regions': regions, 'GM': float(eq.GM.values.squeeze()),
                'mu_A': float(eq.MU.sel(component='A').values.squeeze()), 'mu_B': float(eq.MU.sel(component='B').values.squeeze())}

    at = split(T0, Z0)
    if set(at['regions']) != {'SOLID', 'LIQUID'}:
        raise ValueError('pycalphad did not split at 1400 K')
    result = {'phases': ['SOLID', 'LIQUID'], 'x_SOLID': _x(at['regions']['SOLID'][1]), 'x_LIQUID': _x(at['regions']['LIQUID'][1]),
              'f_LIQUID': _x(at['regions']['LIQUID'][0]), 'GM': _e(at['GM']), 'mu_A': _e(at['mu_A']), 'mu_B': _e(at['mu_B']),
              'GM_relative': _e(at['GM'] - reference(Z0, T0)),
              'tangent_relative': [_e(at['mu_A'] - reference(0.0)), _e(at['mu_B'] - reference(1.0))]}
    lens = []
    for row in sorted(walk, key=lambda r: r['T_K']):
        mid = 0.5 * (row['x_SOLID'] + row['x_LIQUID'])
        s = split(row['T_K'], mid)
        if set(s['regions']) != {'SOLID', 'LIQUID'}:
            raise ValueError(f"pycalphad did not split at {row['T_K']} K")
        lens.append({'T_K': row['T_K'], 'x_SOLID': _x(s['regions']['SOLID'][1]), 'x_LIQUID': _x(s['regions']['LIQUID'][1])})
    return {'version': version('pycalphad'), 'tdb': TDB.strip(), 'sample': sample, 'sample_every': SAMPLE_EVERY,
            'result': result, 'lens': lens}


def build() -> dict:
    ans = answer()
    walk = continuation()
    pyc = pycalphad_part(walk)
    diff = {key: _small(ans[key] - pyc['result'][key]) for key in ('x_SOLID', 'x_LIQUID', 'f_LIQUID', 'GM', 'mu_A', 'mu_B')}
    if max(abs(diff[k]) for k in ('x_SOLID', 'x_LIQUID', 'f_LIQUID')) > 1e-8 or max(abs(diff[k]) for k in ('GM', 'mu_A', 'mu_B')) > 1e-6:
        raise ValueError('pycalphad and the from-scratch route disagree')
    lens_diff = max(max(abs(a['x_SOLID'] - b['x_SOLID']), abs(a['x_LIQUID'] - b['x_LIQUID']))
                    for a, b in zip(sorted(walk, key=lambda r: r['T_K']), pyc['lens']))
    return {
        'schema_version': 1,
        'description': 'Step 03 part D: one equilibrium of the part C lens found from scratch and by pycalphad. '
                       'Energies J/mol of atoms; relative energies are measured from the 1400 K common tangent.',
        'conditions': {'T_K': T0, 'z': Z0, 'P_Pa': P, 'R': R, 'melting_K': {'A': 1000.0, 'B': 1800.0}},
        'view': {'x': list(VIEW_X), 'relative_to': 'the common tangent at 1400 K, (1 - x) mu_A + x mu_B'},
        'curves': curves(),
        'answer': ans,
        'brute': brute(),
        'grid': grid(ans['GM']),
        'newton': {'start': list(NEWTON_START), 'frames': newton_frames()},
        'continuation': walk,
        'pycalphad': pyc,
        'difference': {**diff, 'lens_max_x': _small(lens_diff)},
        'environment': {'python': platform.python_version(), 'numpy': version('numpy'), 'scipy': version('scipy')},
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=1, ensure_ascii=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(HERE.parents[1])}')


if __name__ == '__main__':
    main()
