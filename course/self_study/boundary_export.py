"""Export the step 04 tangent picture and hand iteration from existing course models.

Uses only course/foundations/binary_family.py (ALPHA bulk curve, chemical
potentials) and boundary_one_state.py / boundary_closed.py (open and closed
boundary equilibria). T = 1000 K, p = 100000 Pa, energies in J/mol of sites.

Run from the repository root:
    .venv/bin/python -m course.self_study.boundary_export
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from course.foundations import binary_family as bf
from course.foundations import boundary_closed as closed
from course.foundations import boundary_one_state as opened

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'boundary_views.json'
T = opened.TEMPERATURE
GRID = [i / 100 for i in range(1, 100)]
RESERVOIRS = [0.10, 0.20, 0.50]
DELTAS = [-10000.0 + 500 * i for i in range(31)]  # -10000 ... +5000 J/mol boundary sites
TOL = 1e-6  # contract mu/energy residual tolerance, J/mol


def _f(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('nonfinite value')
    return number


def gb(x: float) -> float:
    return _f(bf.ideal_properties(T, x, 'ALPHA')['GM'])


def reservoir(x_b: float) -> dict:
    mu = bf.ideal_derivatives(T, x_b, 'ALPHA')
    mu_a, mu_b = _f(mu['mu_A']), _f(mu['mu_B'])
    cases = []
    for delta in DELTAS:
        state = opened.open_equilibrium(x_b, delta)
        theta = _f(state['theta'])
        gs_theta = gb(theta) + delta * theta
        phi = _f(state['phi_J_per_mol_sites'])
        # phi is the vertical gap at theta between g_s and the reservoir line.
        if abs(gs_theta - ((1 - theta) * mu_a + theta * mu_b) - phi) > TOL:
            raise ValueError(f'phi is not the tangent gap at x_b={x_b}, delta={delta}')
        slope = mu_b - mu_a
        y0 = gs_theta - slope * theta
        cases.append({'delta': delta, 'theta': theta, 'phi': phi, 'gs_theta': _f(gs_theta),
                      'gs': [_f(gb(x) + delta * x) for x in GRID], 'parallel_tangent': [_f(y0), _f(y0 + slope)]})
    return {'x_b': x_b, 'mu_A': mu_a, 'mu_B': mu_b, 'gb_x_b': gb(x_b), 'cases': cases}


def hand_iteration(x0: float = 0.10, theta0: float = 0.25, delta: float = -5000.0, rounds: int = 6) -> dict:
    """The narration's hand method: odds formula at the current bulk fraction, then update the bulk."""
    nb, ns = 8000, closed.BOUNDARY_SITES  # bulk sites; both boundaries' sites
    b_total = nb * x0 + ns * theta0
    x_b, steps = x0, []
    for k in range(rounds):
        theta = _f(opened.open_equilibrium(x_b, delta)['theta_analytic'])
        steps.append({'k': k + 1, 'x_b_used': _f(x_b), 'theta': theta, 'boundary_B': _f(ns * theta), 'bulk_B': _f(b_total - ns * theta)})
        x_b = (b_total - ns * theta) / nb
    final = closed.closed_equilibrium(x0, delta, nb)
    if abs(steps[-1]['theta'] - final['theta_root']) > 1e-6:
        raise ValueError('hand iteration does not reach the closed result')
    return {'x0': x0, 'theta0': theta0, 'delta': delta, 'B_total': b_total, 'steps': steps,
            'closed_theta_direct': _f(final['theta']), 'closed_theta_root': _f(final['theta_root'])}


def closed_match(x0: float = 0.10, theta0: float = 0.25, delta: float = -5000.0) -> dict:
    """Which reservoir composition makes the open boundary hold what the closed cell holds?

    A scan of reservoir compositions x_b with the open occupancy θ at each, the
    closed cell's final bulk x_b and θ, and the exchange price μB − μA there:
    the closed cell's multiplier for its B balance (per mole of B).
    """
    nb, ns = 8000, closed.BOUNDARY_SITES
    final = closed.closed_equilibrium(x0, delta, nb)
    theta_c = _f(final['theta_root'])
    x_c = (nb * x0 + ns * theta0 - ns * theta_c) / nb
    scan = [round(0.095 + 0.0005 * i, 4) for i in range(25)]
    theta_open = [_f(opened.open_equilibrium(x, delta)['theta_analytic']) for x in scan]
    at_closed = _f(opened.open_equilibrium(x_c, delta)['theta_analytic'])
    if abs(at_closed - theta_c) > 1e-6:
        raise ValueError('the open boundary at the closed bulk composition differs from the closed result')
    d = bf.ideal_derivatives(T, x_c, 'ALPHA')
    return {'delta': delta, 'x_scan': scan, 'theta_open': theta_open, 'x_b_closed': _f(x_c), 'theta_closed': theta_c,
            'exchange_price': _f(d['mu_B'] - d['mu_A'])}


def build() -> dict:
    data = {'schema_version': 1, 'T_K': T, 'units': {'energy': 'J/mol sites', 'x': 'B fraction', 'delta': 'J/mol boundary sites'},
            'source': 'course/foundations/binary_family.py, boundary_one_state.py, boundary_closed.py',
            'x': GRID, 'gb': [gb(x) for x in GRID], 'reservoirs': [reservoir(x) for x in RESERVOIRS],
            'iteration': hand_iteration(), 'closed_match': closed_match()}
    json.dumps(data, allow_nan=False)
    return data


def main() -> None:
    data = build()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=1, sort_keys=True, allow_nan=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(HERE.parents[1])} ({OUTPUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
