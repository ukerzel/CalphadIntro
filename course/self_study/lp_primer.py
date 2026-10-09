"""The optional linear-programming primer: a foundry charge, as dots and as the textbook picture.

Everything here is an invented teaching example (prices, contents and caps are
made up), not market data and not a thermodynamic model. Two pictures:

- dots and chords: lots of scrap with a Ni content w (kg Ni per kg) and a price
  (EUR per kg); mix 1 kg at a target content as cheaply as possible. This LP has
  exactly the shape of the menu of advanced step 10 (two equality rows and
  amounts that cannot be negative), so its answer is the lowest chord above the
  target and its prices draw a line under the dots;
- the textbook picture: two lots, amounts f_P and f_Q (kg) on the axes, four
  rules ("at least" and "at most"), a polygon of allowed charges and a cost line
  that slides to a corner.

The browser draws the exported values and does only display arithmetic on them
(the lever rule on two exported dots, a line's height, cost = price times
amount at an exported corner). Run from the repository root:
    .venv/bin/python -m course.self_study.lp_primer
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'generated' / 'lp_primer.json'
TOL = 1e-9


@dataclass(frozen=True)
class Lot:
    name: str
    short: str
    w: float      # Ni content, kg Ni per kg of lot
    price: float  # EUR per kg of lot


LOTS = [Lot('Copper scrap', 'Cu', 0.00, 7.40), Lot('CuNi10 scrap', 'CuNi10', 0.10, 7.90),
        Lot('CuNi30 scrap', 'CuNi30', 0.30, 8.40), Lot('Constantan scrap', 'CuNi45', 0.45, 10.00),
        Lot('Monel offcuts', 'Monel', 0.65, 10.20), Lot('Nickel cathode', 'Ni', 1.00, 15.50)]
TARGET = 0.40                      # kg Ni per kg of charge
START = (0, 5)                     # the swap path starts from copper scrap and nickel cathode
OFFER = Lot('Swarf offered by a dealer', 'Swarf', 0.50, 9.20)
NUDGE = 0.01
TARGETS = [round(0.01 * i, 2) for i in range(101)]

# The textbook picture: amounts f_P (CuNi30 scrap) and f_Q (Monel offcuts), kg.
POLY_LOTS = [{'name': 'CuNi30 scrap', 'short': 'P', 'ni': 0.30, 'fe': 0.006, 'price': 8.40},
             {'name': 'Monel offcuts', 'short': 'Q', 'ni': 0.65, 'fe': 0.020, 'price': 10.20}]
FE_CAP = {'normal': 0.012, 'strict': 0.005}  # kg Fe allowed in the charge
RULES = [  # a_P f_P + a_Q f_Q (sense) b; 'fe' takes its b from FE_CAP
    {'id': 'charge', 'label': 'charge at least 1 kg', 'a': [1.0, 1.0], 'sense': '>=', 'b': 1.0, 'unit': 'kg'},
    {'id': 'ni', 'label': 'Ni at least 0.40 kg', 'a': [0.30, 0.65], 'sense': '>=', 'b': 0.40, 'unit': 'kg Ni'},
    {'id': 'fe', 'label': 'Fe at most 0.012 kg', 'a': [0.006, 0.020], 'sense': '<=', 'b': None, 'unit': 'kg Fe'},
    {'id': 'furnace', 'label': 'furnace holds at most 1.5 kg', 'a': [1.0, 1.0], 'sense': '<=', 'b': 1.5, 'unit': 'kg'},
]
PRICE_Q = (6.0, 20.0)              # slider range for the Monel price, EUR per kg


def r(value: float, digits: int = 6) -> float:
    out = round(float(value), digits)
    return 0.0 if out == 0 else out


# ---------------------------------------------------------------- dots and chords

def lever(a: Lot, b: Lot, z: float) -> tuple[float, float] | None:
    """Amounts of a and b that make 1 kg at content z; None if one would be negative."""
    if a.w == b.w:
        return None
    fb = (z - a.w) / (b.w - a.w)
    return None if fb < -TOL or fb > 1 + TOL else (1 - fb, fb)


def best_pair(lots: list[Lot], z: float) -> dict:
    """Try every pair (the hand method): the cheapest 1 kg at content z, by the lever rule."""
    best = None
    for i, a in enumerate(lots):   # one lot at z first: on a tie it beats a pair that gives the other lot zero
        if abs(a.w - z) < TOL and (best is None or a.price < best['cost'] - TOL):
            best = {'used': [i], 'f': [1.0], 'cost': a.price}
    for i, a in enumerate(lots):
        for j in range(i + 1, len(lots)):
            f = lever(a, lots[j], z)
            if f is not None:
                cost = f[0] * a.price + f[1] * lots[j].price
                if best is None or cost < best['cost'] - TOL:
                    best = {'used': [i, j], 'f': list(f), 'cost': cost}
    if best is None:
        raise ValueError('no pair of lots can make this content')
    return best


def line_through(a: Lot, b: Lot) -> tuple[float, float]:
    """Base price (height at w = 0) and Ni premium (slope) of the line through two lots."""
    slope = (b.price - a.price) / (b.w - a.w)
    return a.price - slope * a.w, slope


def gaps(lots: list[Lot], base: float, slope: float) -> list[float]:
    """Each lot's price minus the line's height at its content (its reduced cost)."""
    return [lot.price - (base + slope * lot.w) for lot in lots]


def swap_path(lots: list[Lot], z: float, start: tuple[int, int]) -> list[dict]:
    """The simplex method on this two-row problem, one swap per frame.

    Start from a pair that brackets z. Draw the line through it; the lot furthest
    below the line comes in; it replaces the used lot on the same side of z (the
    only swap that keeps both amounts non-negative). Stop when no lot is below.
    """
    used = sorted(start, key=lambda k: lots[k].w)
    frames = []
    for _ in range(len(lots)):
        a, b = (lots[k] for k in used)
        base, slope = line_through(a, b)
        f = lever(a, b, z)
        g = gaps(lots, base, slope)
        enter = int(np.argmin(g))
        done = g[enter] > -TOL
        same_side = [k for k in used if (lots[k].w - z) * (lots[enter].w - z) > 0]
        # a lot exactly at z has no side: if one enters or is used, the used lot nearest z leaves
        leave = None if done else same_side[0] if same_side else min(used, key=lambda k: abs(lots[k].w - z))
        frames.append({'used': list(used), 'f': [r(v) for v in f], 'cost': r(f[0] * a.price + f[1] * b.price),
                       'line': {'base': r(base), 'slope': r(slope), 'top': r(base + slope)},
                       'gaps': [r(v) for v in g], 'enter': None if done else enter, 'leave': leave})
        if done:
            return frames
        used = sorted([k for k in used if k != leave] + [enter], key=lambda k: lots[k].w)
    raise RuntimeError('swap path did not finish')


def solve_blend(lots: list[Lot], z: float, method: str = 'highs-ds'):
    """The same problem in SciPy's linprog: minimise sum f_j price_j, sum f_j = 1, sum f_j w_j = z, f >= 0."""
    c = [lot.price for lot in lots]
    return linprog(c, A_eq=[[1.0] * len(lots), [lot.w for lot in lots]], b_eq=[1.0, z], bounds=(0, None), method=method)


def hull(lots: list[Lot]) -> list[int]:
    """Lots on the lower convex hull of (w, price), left to right: the best cost for every target."""
    order = sorted(range(len(lots)), key=lambda k: (lots[k].w, lots[k].price))
    out: list[int] = []
    for k in order:
        while len(out) >= 2:
            (x1, y1), (x2, y2), (x3, y3) = ((lots[j].w, lots[j].price) for j in (out[-2], out[-1], k))
            if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) <= 0:
                out.pop()
            else:
                break
        out.append(k)
    return out


def target_frames(lots: list[Lot]) -> list[dict]:
    """Best cost and its price line for every target content on the slider (0.00 ... 1.00).

    When the target sits exactly on a used lot the line is not unique: the
    frame then gives the slopes of the two hull segments that meet there.
    """
    h = hull(lots)
    frames = []
    for z in TARGETS:
        best = best_pair(lots, z)
        res = solve_blend(lots, z)
        assert res.status == 0 and abs(res.fun - best['cost']) < 1e-9
        segment = next(i for i in range(len(h) - 1) if lots[h[i]].w - TOL <= z <= lots[h[i + 1]].w + TOL)
        on_dot = [k for k in h if abs(lots[k].w - z) < TOL]
        frame = {'z': z, 'used': best['used'], 'f': [r(v) for v in best['f']], 'cost': r(best['cost'])}
        if on_dot:
            i = h.index(on_dot[0])
            left = line_through(lots[h[i - 1]], lots[h[i]])[1] if i > 0 else None
            right = line_through(lots[h[i]], lots[h[i + 1]])[1] if i < len(h) - 1 else None
            frame['slopes'] = [None if left is None else r(left), None if right is None else r(right)]
        else:
            frame['slope'] = r(line_through(lots[h[segment]], lots[h[segment + 1]])[1])
        frames.append(frame)
    return frames


def blend() -> dict:
    best = best_pair(LOTS, TARGET)
    path = swap_path(LOTS, TARGET, START)
    final = path[-1]
    assert final['used'] == best['used'] and abs(final['cost'] - best['cost']) < 1e-6
    a, b = (LOTS[k] for k in best['used'])
    base, slope = line_through(a, b)          # exact, not the rounded frame values
    with_offer = LOTS + [OFFER]
    offer_best = best_pair(with_offer, TARGET)
    offer_gap = OFFER.price - (base + slope * OFFER.w)
    return {
        'target': TARGET, 'units': {'amount': 'kg', 'content': 'kg Ni per kg', 'price': 'EUR per kg'},
        'lots': [{'name': lot.name, 'short': lot.short, 'w': lot.w, 'price': lot.price} for lot in LOTS],
        'best': {'used': best['used'], 'f': [r(v) for v in best['f']], 'cost': r(best['cost'])},
        'pairs_tried': sum(1 for i in range(len(LOTS)) for j in range(i + 1, len(LOTS)) if lever(LOTS[i], LOTS[j], TARGET)),
        'swap': {'start': list(START), 'frames': path},
        'prices': {'base': r(base), 'slope': r(slope), 'cu': r(base), 'ni': r(base + slope),
                   'range': [a.w, b.w]},
        'nudge': {'dz': NUDGE, 'change': r(slope * NUDGE), 'cost': r(best_pair(LOTS, TARGET + NUDGE)['cost'])},
        'offer': {'lot': {'name': OFFER.name, 'short': OFFER.short, 'w': OFFER.w, 'price': OFFER.price},
                  'line_height': r(base + slope * OFFER.w), 'gap': r(offer_gap),
                  'best': {'used': offer_best['used'], 'f': [r(v) for v in offer_best['f']], 'cost': r(offer_best['cost'])}},
        'hull': hull(LOTS),
        'targets': target_frames(LOTS),
    }


# ---------------------------------------------------------------- the textbook picture

def rules(cap: str) -> list[dict]:
    return [{**rule, 'b': FE_CAP[cap] if rule['id'] == 'fe' else rule['b']} for rule in RULES]


def allowed(f: tuple[float, float], rs: list[dict], tol: float = 1e-9) -> bool:
    if min(f) < -tol:
        return False
    for rule in rs:
        lhs = rule['a'][0] * f[0] + rule['a'][1] * f[1]
        if (rule['sense'] == '>=' and lhs < rule['b'] - tol) or (rule['sense'] == '<=' and lhs > rule['b'] + tol):
            return False
    return True


def corners(rs: list[dict]) -> list[dict]:
    """Corners of the allowed region: where two boundary lines meet and every rule holds. Counter-clockwise."""
    lines = [(rule['a'], rule['b'], rule['id']) for rule in rs] + [([1.0, 0.0], 0.0, 'no-P'), ([0.0, 1.0], 0.0, 'no-Q')]
    found: list[dict] = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            (a1, b1, n1), (a2, b2, n2) = lines[i], lines[j]
            det = a1[0] * a2[1] - a1[1] * a2[0]
            if abs(det) < 1e-12:
                continue
            f = ((b1 * a2[1] - a1[1] * b2) / det, (a1[0] * b2 - b1 * a2[0]) / det)
            if allowed(f, rs) and not any(math.dist(f, c['f']) < 1e-9 for c in found):
                tight = [rule['id'] for rule in rs if abs(rule['a'][0] * f[0] + rule['a'][1] * f[1] - rule['b']) < 1e-9]
                tight += [name for name, v in (('no-P', f[0]), ('no-Q', f[1])) if abs(v) < 1e-9]
                found.append({'f': [r(f[0]), r(f[1])], 'tight': tight})
    if found:
        cx = sum(c['f'][0] for c in found) / len(found)
        cy = sum(c['f'][1] for c in found) / len(found)
        found.sort(key=lambda c: math.atan2(c['f'][1] - cy, c['f'][0] - cx))
    return found


def solve_polygon(cap: str = 'normal', price_q: float | None = None, ni: float | None = None):
    """linprog form: '>=' rows are negated into '<=' rows (A_ub f <= b_ub)."""
    rs = rules(cap)
    if ni is not None:
        rs = [{**rule, 'b': ni} if rule['id'] == 'ni' else rule for rule in rs]
    price = [POLY_LOTS[0]['price'], POLY_LOTS[1]['price'] if price_q is None else price_q]
    sign = [-1.0 if rule['sense'] == '>=' else 1.0 for rule in rs]
    A = [[s * v for v in rule['a']] for s, rule in zip(sign, rs)]
    b = [s * rule['b'] for s, rule in zip(sign, rs)]
    return linprog(price, A_ub=A, b_ub=b, bounds=(0, None), method='highs-ds'), sign


def ties(cs: list[dict]) -> list[float]:
    """Monel prices at which two corners cost the same and both are cheapest: the cost line lies along an edge."""
    p = POLY_LOTS[0]['price']
    out = []
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            (p1, q1), (p2, q2) = cs[i]['f'], cs[j]['f']
            if abs(q1 - q2) < 1e-12:
                continue
            q = p * (p2 - p1) / (q1 - q2)
            if PRICE_Q[0] < q < PRICE_Q[1]:
                costs = [p * c['f'][0] + q * c['f'][1] for c in cs]
                if abs(min(costs) - (p * p1 + q * q1)) < 1e-9:
                    out.append(r(q))
    return sorted(set(out))


def polygon() -> dict:
    regions = {cap: corners(rules(cap)) for cap in FE_CAP}
    res, sign = solve_polygon('normal')
    assert res.status == 0
    duals = {rule['id']: r(s * m) for rule, s, m in zip(RULES, sign, res.ineqlin.marginals)}
    strict, _ = solve_polygon('strict')
    # The best corner keeps the charge and Ni rules tight, so it is the lever mixture of P and Q at 1 kg.
    # It stays the corner while its Monel amount lies between 0 (pure P) and the amount the Fe cap allows.
    (p_lot, q_lot), cap = POLY_LOTS, FE_CAP['normal']
    q_max = (cap - p_lot['fe']) / (q_lot['fe'] - p_lot['fe'])
    lo, hi = p_lot['ni'], r(p_lot['ni'] + (q_lot['ni'] - p_lot['ni']) * q_max)
    for b in np.linspace(lo, hi, 7)[1:-1]:      # inside the range the solver's Ni price does not move
        rb, sb = solve_polygon('normal', ni=float(b))
        assert rb.status == 0 and abs(sb[1] * rb.ineqlin.marginals[1] - duals['ni']) < 1e-6
    exact_f = lever(Lot('', '', POLY_LOTS[0]['ni'], 0), Lot('', '', POLY_LOTS[1]['ni'], 0), RULES[1]['b'])
    return {
        'lots': POLY_LOTS, 'rules': RULES, 'fe_cap': FE_CAP, 'price_q': {'default': POLY_LOTS[1]['price'], 'range': list(PRICE_Q)},
        'regions': regions,
        'optimum': {'f': [r(v) for v in res.x], 'cost': r(res.fun), 'duals': duals,
                    'tight': [rule['id'] for rule in RULES if abs(res.ineqlin.residual[RULES.index(rule)]) < 1e-9],
                    'ni_range': [lo, hi]},
        'ties': ties(regions['normal']),
        'strict_status': int(strict.status),
        'exact': {'f': [r(v) for v in exact_f]},
    }


def build() -> dict:
    data = {'schema_version': 1, 'note': 'Invented teaching numbers (prices, contents, caps); not market data.',
            'blend': blend(), 'polygon': polygon()}
    json.dumps(data, allow_nan=False)
    return data


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=1, ensure_ascii=False, allow_nan=False) + '\n')
    print(f'wrote {OUTPUT.relative_to(HERE.parents[1])}')


if __name__ == '__main__':
    main()
