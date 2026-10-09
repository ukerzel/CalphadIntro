"""The advanced steps, optional step 18: the melting lens with a third component.

The lens of step 03 part C (components A and B, ideal SOLID and LIQUID) gains an
invented third component C, labelled synthetic: C melts at 1250 K, with
g°(C, SOLID) = 1500 − 12 T and g°(C, LIQUID) = 9000 − 18 T J/mol. Both phase
models stay ideal: g(x) = Σ x_i g°_i + RT Σ x_i ln x_i over (A, B, C).
Everything carries over from the binary pages: the menu has three rows
(amounts, B atoms, C atoms), the line becomes a plane with three heights
μA, μB, μC, and the gap becomes a landscape over the triangle.

An independent control: for two ideal phases, the split of a sample z follows
from the partition ratios K_i = x_L,i / x_S,i = exp((g°_S,i − g°_L,i)/RT) by the
Rachford–Rice equation Σ z_i (K_i − 1) / (1 + V (K_i − 1)) = 0 for the liquid
amount V, valid only when 0 < V < 1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, linprog

from course.self_study import two_phase_export as tp

R = tp.bf.R
T0 = 1400.0
Z0 = (0.50, 0.30, 0.20)                       # overall (A, B, C)
C_G0 = {'SOLID': (1500.0, 12.0), 'LIQUID': (9000.0, 18.0)}   # (h, s) of the invented C
COMPONENTS = ('A', 'B', 'C')
PHASES = ('SOLID', 'LIQUID')


def g0(component: str, phase: str, t: float = T0) -> float:
    if component == 'C':
        h, s = C_G0[phase]
        return h - s * t
    return tp.lens_g0(component, phase, t)


def g(phase: str, x, t: float = T0):
    """Molar Gibbs energy of an ideal ternary phase; x has shape (..., 3) with rows summing to 1."""
    x = np.asarray(x, dtype=float)
    ends = np.array([g0(c, phase, t) for c in COMPONENTS])
    with np.errstate(divide='ignore', invalid='ignore'):
        mix = np.where(x > 0, x * np.log(np.where(x > 0, x, 1.0)), 0.0).sum(axis=-1)
    return x @ ends + R * t * mix


def partition(t: float = T0) -> np.ndarray:
    """K_i = x_L,i / x_S,i at coexistence of two ideal phases."""
    return np.array([math.exp((g0(c, 'SOLID', t) - g0(c, 'LIQUID', t)) / (R * t)) for c in COMPONENTS])


def rachford_rice(z=Z0, t: float = T0) -> dict:
    """Liquid amount V and both compositions from the Rachford–Rice equation, or the single phase."""
    z, k = np.asarray(z, dtype=float), partition(t)
    if (z * k).sum() <= 1:
        return {'status': 'all SOLID'}
    if (z / k).sum() <= 1:
        return {'status': 'all LIQUID'}
    f = lambda v: float((z * (k - 1) / (1 + v * (k - 1))).sum())
    v = brentq(f, 1e-14, 1 - 1e-14, xtol=1e-15)
    xs = z / (1 + v * (k - 1))
    return {'status': 'split', 'V': v, 'x_SOLID': xs, 'x_LIQUID': k * xs}


def edge_tie(pair: tuple[str, str], t: float = T0) -> tuple[float, float] | None:
    """Coexisting fractions of the second component on a binary edge (closed form for two ideal phases)."""
    i, j = (COMPONENTS.index(c) for c in pair)
    k = partition(t)
    a, b = k[i], k[j]                      # x_L = k x_S for each component on the edge
    # solid: x_j s + x_i (1-s); liquid: a (1-s) + b s = 1  ->  s = (1-a)/(b-a)
    if (a - 1) * (b - 1) >= 0:
        return None
    s = (1 - a) / (b - a)
    return s, b * s                        # (solid, liquid) fraction of the second component


def grid(n: int) -> np.ndarray:
    """All points (i, j, k)/n of the triangle with i + j + k = n, as (A, B, C) fractions."""
    pts = [(i / n, j / n, (n - i - j) / n) for i in range(n + 1) for j in range(n + 1 - i)]
    return np.array(pts)


@dataclass
class Master:
    phases: list[str]
    x: np.ndarray            # (m, 3) compositions of the states
    f: np.ndarray            # amounts
    G_up: float
    mu: np.ndarray           # (μA, μB, μC): the plane's heights at the three corners


def solve_master(phases: list[str], x: np.ndarray, z=Z0, t: float = T0) -> Master:
    """Cheapest mixture of a menu with rows: amounts, B atoms, C atoms (HiGHS dual simplex).

    The multipliers (π0, πB, πC) of these rows give the plane π0 + πB xB + πC xC;
    its corner heights are μA = π0, μB = π0 + πB, μC = π0 + πC.
    """
    x = np.asarray(x, dtype=float)
    c = np.array([float(g(p, xi, t)) for p, xi in zip(phases, x)])
    A = np.vstack([np.ones(len(x)), x[:, 1], x[:, 2]])
    r = linprog(c, A_eq=A, b_eq=[1.0, z[1], z[2]], bounds=(0, None), method='highs-ds')
    if not r.success:
        raise ValueError(r.message)
    p0, pb, pc = r.eqlin.marginals
    return Master(list(phases), x, np.where(r.x > 1e-14, r.x, 0.0), float(r.fun), np.array([p0, p0 + pb, p0 + pc]))


def price(phase: str, mu: np.ndarray, t: float = T0) -> tuple[np.ndarray, float]:
    """Deepest point of an ideal phase's gap g(x) − Σ x_i μ_i, in closed form.

    Minimising Σ x_i (g°_i − μ_i) + RT Σ x_i ln x_i on the triangle gives
    x_i ∝ exp(−(g°_i − μ_i)/RT); the minimum is −RT ln Σ exp(−(g°_i − μ_i)/RT).
    """
    a = np.array([g0(c, phase, t) for c in COMPONENTS]) - mu
    w = -a / (R * t)
    w -= w.max()
    x = np.exp(w) / np.exp(w).sum()
    return x, float(g(phase, x, t) - x @ mu)


def column_generation(seed_n: int = 10, z=Z0, t: float = T0, tol: float = 1e-9, max_iter: int = 30) -> list[dict]:
    pts = grid(seed_n)
    phases = [p for p in PHASES for _ in pts]
    x = np.vstack([pts, pts])
    out, low = [], -np.inf
    for k in range(max_iter + 1):
        m = solve_master(phases, x, z, t)
        dips = {p: price(p, m.mu, t) for p in PHASES}
        best = min(dips, key=lambda p: dips[p][1])
        low = max(low, m.G_up + min(0.0, dips[best][1]))   # keep the best floor so far, as in step 14
        out.append({'k': k, 'master': m, 'dips': dips, 'best': best, 'G_low': low, 'remaining': m.G_up - low})
        if m.G_up - low <= tol:
            break
        phases.append(best)
        x = np.vstack([x, dips[best][0]])
    return out


# --- T6: what gets harder: an A–C interaction in the LIQUID makes the landscape non-convex
OMEGA_AC = 30000.0


HARDER_AT = (0.75, 0.05, 0.20)                # an A-rich liquid between the A–C binodal and spinodal


def g_with_ac(phase: str, x, t: float = T0, omega: float = OMEGA_AC):
    x = np.asarray(x, dtype=float)
    extra = omega * x[..., 0] * x[..., 2] if phase == 'LIQUID' else 0.0
    return g(phase, x, t) + extra


def mu_with_ac(x, t: float = T0, omega: float = OMEGA_AC) -> np.ndarray:
    """Chemical potentials of the liquid with the A–C term: the tangent plane's corner heights at x."""
    xa, _, xc = x
    ends = np.array([g0(c, 'LIQUID', t) for c in COMPONENTS])
    return ends + R * t * np.log(np.asarray(x, dtype=float)) + omega * np.array([xc * (1 - xa), -xa * xc, xa * (1 - xc)])


# ---------------------------------------------------------------------------
# Export for step 18: every printed number and every frame of the triangle lab.
# Run from the repository root:  .venv/bin/python -m course.self_study.day3_ternary
# ---------------------------------------------------------------------------
import json
import platform
from importlib.metadata import version
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / 'generated' / 'day3_ternary.json'
MENU_N = 12                                    # the step 18 menu: 91 points per phase model; z is not on it
FINE_N = 40                                    # the landscape grid: 861 points
CG_TOL = 1e-4


def _f(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('nonfinite value')
    return number + 0.0


def _xs(x) -> list[float]:
    return [_f(v) for v in x]


def build() -> dict:
    z = np.array(Z0)
    rr = rachford_rice()
    if rr['status'] != 'split' or not 0 < rr['V'] < 1:
        raise ValueError('the sample no longer splits')
    g_true = (1 - rr['V']) * float(g('SOLID', rr['x_SOLID'])) + rr['V'] * float(g('LIQUID', rr['x_LIQUID']))
    menu = grid(MENU_N)
    if any(np.allclose(p, z) for p in menu):
        raise ValueError('z must not be on the menu')
    phases = [p for p in PHASES for _ in menu]
    master = solve_master(phases, np.vstack([menu, menu]))
    used = [{'phase': p, 'x': _xs(xi), 'f': _f(fi)} for p, xi, fi in zip(master.phases, master.x, master.f) if fi > 0]
    if len(used) > 3:
        raise ValueError('a basic solution of three rows uses at most three states')
    rounds = column_generation(seed_n=MENU_N, tol=CG_TOL, max_iter=60)
    final = rounds[-1]['master']
    if abs(final.G_up - g_true) > 1e-3:
        raise ValueError('column generation does not reach the Rachford–Rice answer')
    fine = grid(FINE_N)

    def gaps(mu, fn=g):
        return {p: _xs(fn(p, fine) - fine @ mu) for p in PHASES}
    at = np.array(HARDER_AT)
    mu_at = mu_with_ac(at)
    hard = _xs(g_with_ac('LIQUID', fine) - fine @ mu_at)
    scan = grid(160)
    scan_gap = g_with_ac('LIQUID', scan) - scan @ mu_at
    k_low = int(np.argmin(scan_gap))
    if abs(float(g_with_ac('LIQUID', at) - at @ mu_at)) > 1e-8 or scan_gap[k_low] > -100:
        raise ValueError('expected a tangent at the A-rich point and a hidden C-rich valley')
    return {
        'schema_version': 1,
        'description': 'The advanced steps, optional step 18: the melting lens with an invented third component C. '
                       'Energies J/mol of atoms; compositions are (A, B, C) atom fractions.',
        'conditions': {'T_K': T0, 'z': _xs(z), 'R': R},
        'g0': {c: {p: _f(g0(c, p)) for p in PHASES} for c in COMPONENTS},
        'melting_K': {'A': 1000.0, 'B': 1800.0, 'C': 1250.0},
        'K': _xs(partition()),
        'edges': {'A-B': _xs(edge_tie(('A', 'B'))), 'C-B': _xs(edge_tie(('C', 'B'))), 'A-C': None},
        'rachford_rice': {'V': _f(rr['V']), 'x_SOLID': _xs(rr['x_SOLID']), 'x_LIQUID': _xs(rr['x_LIQUID']), 'G': _f(g_true),
                          'sum_zK': _f((z * partition()).sum()), 'sum_z_over_K': _f((z / partition()).sum())},
        'menu': {'n': MENU_N, 'x': [_xs(p) for p in menu], 'g': {p: _xs(g(p, menu)) for p in PHASES},
                 'used': used, 'G_up': _f(master.G_up), 'mu': _xs(master.mu)},
        'rounds': [{'k': r['k'], 'G_up': _f(r['master'].G_up), 'mu': _xs(r['master'].mu), 'best': r['best'],
                    'dips': {p: {'x': _xs(v[0]), 'depth': _f(v[1])} for p, v in r['dips'].items()},
                    'G_low': _f(r['G_low']), 'remaining': _f(r['remaining'])} for r in rounds],
        'final': {'used': [{'phase': p, 'x': _xs(xi), 'f': _f(fi)} for p, xi, fi in zip(final.phases, final.x, final.f) if fi > 1e-9],
                  'mu': _xs(final.mu), 'G_up': _f(final.G_up)},
        'landscape': {'n': FINE_N, 'x': [_xs(p) for p in fine], 'menu_plane': gaps(master.mu), 'final_plane': gaps(final.mu)},
        'harder': {'omega_AC_J_per_mol': OMEGA_AC, 'phase': 'LIQUID', 'tangent_at': _xs(at), 'mu': _xs(mu_at), 'gap': hard,
                   'deepest': {'x': _xs(scan[k_low]), 'depth': _f(scan_gap[k_low])}},
        'scaling': [{'h': h, 'd': dd, 'cells': _f((1 / h) ** dd)} for h in (0.1, 0.01) for dd in (1, 2, 9)],
        'environment': {'python': platform.python_version(), 'numpy': version('numpy'), 'scipy': version('scipy')},
    }


def main() -> None:
    data = build()
    OUTPUT.write_text(json.dumps(data, indent=1, ensure_ascii=False, allow_nan=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(OUTPUT.parents[3])} ({OUTPUT.stat().st_size // 1024} kB)')


if __name__ == '__main__':
    main()
