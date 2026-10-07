"""Export the self-study "two phases" step data from existing course models.

Part A uses the I2 ALPHA/BETA model at 1000 K (foundations lessons 5-6);
part B uses the R1 regular solution (lesson 7). Only existing functions in
course/foundations/binary_family.py are called; no model or parameter is new.
Energies are J/mol of atoms, x and z are B atom fractions, p = 100000 Pa.

Run from the repository root:
    .venv/bin/python -m course.self_study.two_phase_export
"""
from __future__ import annotations

import json
import math
from importlib.metadata import version
from pathlib import Path
import platform

from course.foundations import binary_family as bf

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'two_phase.json'
GRID = [i / 100 for i in range(1, 100)]
T_A = 1000.0
T_B = [600.0 + 25 * i for i in range(25)] + [1225.0, 1250.0, 1275.0, 1300.0]
# Balances checked at 1e-12 (stricter than the contract's 1e-10); mu residuals at the contract's 1e-6 J/mol.
BALANCE_TOL, MU_TOL = 1e-12, 1e-6


def _f(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('nonfinite value')
    return number


def part_a() -> dict:
    alpha = [_f(bf.ideal_properties(T_A, x, 'ALPHA')['GM']) for x in GRID]
    beta = [_f(bf.ideal_properties(T_A, x, 'BETA')['GM']) for x in GRID]
    left = 1.0 / (1.0 + math.exp(bf.DELTA / (bf.R * T_A)))
    split = bf.ideal_equilibrium(T_A, 0.5)['regions']
    x_alpha, x_beta = split[0]['x'], split[1]['x']
    if abs(x_alpha - left) > 1e-15:
        raise ValueError('I2 coexistence differs from its closed form')
    mu_alpha = bf.ideal_derivatives(T_A, x_alpha, 'ALPHA')
    mu_beta = bf.ideal_derivatives(T_A, x_beta, 'BETA')
    residual = {k: abs(_f(mu_alpha[k]) - _f(mu_beta[k])) for k in ('mu_A', 'mu_B')}
    if max(residual.values()) > MU_TOL:
        raise ValueError('I2 chemical potentials differ between the phases')
    # Energies at the touching points; both must lie on the tangent mu_A + (mu_B - mu_A) x.
    g_alpha = _f(bf.ideal_properties(T_A, x_alpha, 'ALPHA')['GM'])
    g_beta = _f(bf.ideal_properties(T_A, x_beta, 'BETA')['GM'])
    for x_touch, g_touch in ((x_alpha, g_alpha), (x_beta, g_beta)):
        if abs(_f(mu_alpha['mu_A']) + (_f(mu_alpha['mu_B']) - _f(mu_alpha['mu_A'])) * x_touch - g_touch) > MU_TOL:
            raise ValueError('I2 touching point is not on the common tangent')
    states = []
    for i, z in enumerate(GRID):
        eq = bf.ideal_equilibrium(T_A, z)
        regions = [{'phase': r['phase'], 'x': _f(r['x']), 'f': _f(r['f'])} for r in eq['regions']]
        if abs(sum(r['f'] for r in regions) - 1) > BALANCE_TOL or abs(sum(r['f'] * r['x'] for r in regions) - z) > BALANCE_TOL:
            raise ValueError(f'I2 balance failed at z={z}')
        if _f(eq['GM']) > min(alpha[i], beta[i]) + 1e-9:
            raise ValueError(f'I2 equilibrium above a homogeneous state at z={z}')
        states.append({'id': f'twophase-a-{i:03d}', 'z': z, 'GM': _f(eq['GM']), 'regions': regions,
                       'homogeneous_GM': {'ALPHA': alpha[i], 'BETA': beta[i]}})
    return {'model': 'I2', 'T_K': T_A, 'phases': ['ALPHA', 'BETA'], 'x': GRID,
            'GM': {'ALPHA': alpha, 'BETA': beta},
            'coexistence': {'x_ALPHA': _f(x_alpha), 'x_BETA': _f(x_beta),
                            'mu_A': _f(mu_alpha['mu_A']), 'mu_B': _f(mu_alpha['mu_B']),
                            'GM_x_ALPHA': g_alpha, 'GM_x_BETA': g_beta,
                            'mu_residual_J_per_mol': residual},
            'states': states}


def part_b() -> dict:
    rows = []
    for i, t in enumerate(T_B):
        props = [bf.regular_properties(t, x) for x in GRID]
        curve = [_f(p['GM']) for p in props]
        # Mixing part: GM minus the straight reference line; same touching points, visible hump.
        mixing = [_f(p['GM_mix']) for p in props]
        gap = bf.regular_binodal(t)
        row = {'id': f'twophase-b-{i:03d}', 'T_K': t, 'GM': curve, 'GM_mix': mixing, 'status': gap['status'], 'compositions': [],
               'mu_A': None, 'mu_B': None, 'GM_mix_tangent': None}
        if gap['status'] == 'two_compositions':
            left, right = gap['compositions']
            if abs(left + right - 1) > 1e-12:
                raise ValueError('R1 binodal is not symmetric')
            d_left, d_right = bf.regular_derivatives(t, left), bf.regular_derivatives(t, right)
            if max(abs(_f(d_left[k]) - _f(d_right[k])) for k in ('mu_A', 'mu_B')) > MU_TOL:
                raise ValueError(f'R1 chemical potentials differ at T={t}')
            m_left, m_right = _f(bf.regular_properties(t, left)['GM_mix']), _f(bf.regular_properties(t, right)['GM_mix'])
            if abs(m_left - m_right) > MU_TOL:
                raise ValueError(f'R1 mixing tangent is not horizontal at T={t}')
            row.update(compositions=[_f(left), _f(right)], mu_A=_f(d_left['mu_A']), mu_B=_f(d_left['mu_B']), GM_mix_tangent=m_left)
        rows.append(row)
    return {'model': 'R1', 'omega_J_per_mol': bf.OMEGA_R1, 'Tc_K': _f(bf.TC_R1), 'x': GRID, 'rows': rows}


# Part C: invented ideal SOLID/LIQUID binary for the melting lens. Component A is
# step 01's (h, s per phase); B is invented and melts at 1800 K. J/mol atoms.
LENS_H = {'A': {'SOLID': 1000.0, 'LIQUID': 7000.0}, 'B': {'SOLID': 2000.0, 'LIQUID': 20000.0}}
LENS_S = {'A': {'SOLID': 10.0, 'LIQUID': 16.0}, 'B': {'SOLID': 10.0, 'LIQUID': 20.0}}
T_C = [950.0 + 20 * i for i in range(46)]


def lens_g0(element: str, phase: str, t: float) -> float:
    return LENS_H[element][phase] - t * LENS_S[element][phase]


def lens_g(phase: str, x: float, t: float) -> float:
    q = (1 - x) * math.log(1 - x) + x * math.log(x)
    return (1 - x) * lens_g0('A', phase, t) + x * lens_g0('B', phase, t) + bf.R * t * q


def lens_mu(phase: str, x: float, t: float) -> tuple[float, float]:
    rt = bf.R * t
    return lens_g0('A', phase, t) + rt * math.log(1 - x), lens_g0('B', phase, t) + rt * math.log(x)


def lens_coexistence(t: float) -> tuple[float, float] | None:
    """Ideal solutions: equal mu_A and mu_B give x_S = (1-a)/(b-a), x_L = b x_S."""
    rt = bf.R * t
    a = math.exp((lens_g0('A', 'SOLID', t) - lens_g0('A', 'LIQUID', t)) / rt)
    b = math.exp((lens_g0('B', 'SOLID', t) - lens_g0('B', 'LIQUID', t)) / rt)
    if not (a > 1 > b):
        return None
    x_s = (1 - a) / (b - a)
    return x_s, b * x_s


def part_c() -> dict:
    rows = []
    for i, t in enumerate(T_C):
        ref = [(1 - x) * lens_g0('A', 'SOLID', t) + x * lens_g0('B', 'SOLID', t) for x in GRID]
        rel = {ph: [_f(lens_g(ph, x, t) - r) for x, r in zip(GRID, ref)] for ph in ('SOLID', 'LIQUID')}
        coex = lens_coexistence(t)
        row = {'id': f'twophase-c-{i:03d}', 'T_K': t, 'relative_GM': rel, 'x_SOLID': None, 'x_LIQUID': None,
               'mu_A': None, 'mu_B': None, 'tangent_relative': None,
               'status': 'all SOLID' if t <= 1000 else 'all LIQUID' if t >= 1800 else 'SOLID + LIQUID'}
        if coex:
            x_s, x_l = coex
            if not 0 < x_l < x_s < 1:
                raise ValueError(f'lens compositions out of order at T={t}')
            mu_s, mu_l = lens_mu('SOLID', x_s, t), lens_mu('LIQUID', x_l, t)
            if max(abs(mu_s[k] - mu_l[k]) for k in (0, 1)) > MU_TOL:
                raise ValueError(f'lens chemical potentials differ at T={t}')
            row.update(x_SOLID=_f(x_s), x_LIQUID=_f(x_l), mu_A=_f(mu_s[0]), mu_B=_f(mu_s[1]),
                       tangent_relative=[_f(mu_s[0] - lens_g0('A', 'SOLID', t)), _f(mu_s[1] - lens_g0('B', 'SOLID', t))])
        rows.append(row)
    return {'model': 'invented ideal SOLID/LIQUID; A from step 01, B melts at 1800 K',
            'h_J_per_mol': LENS_H, 's_J_per_mol_K': LENS_S, 'melting_K': {'A': 1000.0, 'B': 1800.0},
            'x': GRID, 'rows': rows}


def build() -> dict:
    data = {'schema_version': 1,
            'units': {'T_K': 'K', 'GM': 'J/mol atoms', 'mu': 'J/mol of that element', 'x': 'B atom fraction', 'f': 'mol phase/mol atoms'},
            'conditions': {'P_Pa': 100000, 'amount_mol_atoms': 1},
            'source': 'course/foundations/binary_family.py (I2: lessons 5-6; R1: lesson 7)',
            'versions': {'python': platform.python_version(), 'numpy': version('numpy'), 'scipy': version('scipy')},
            'part_a': part_a(), 'part_b': part_b(), 'part_c': part_c()}
    json.dumps(data, allow_nan=False)
    return data


def main() -> None:
    data = build()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=1, sort_keys=True, allow_nan=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(HERE.parents[1])} ({OUTPUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
