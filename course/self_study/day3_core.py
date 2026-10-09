"""Advanced steps: equilibrium as a menu, a line, a gap curve and bounds.

One small library shared by the export and the notebooks of the advanced steps, so every
printed number comes from the same code. Two existing course models are used,
never a new one:

* the melting lens of step 03 part C (two_phase_export): ideal SOLID and LIQUID,
  used at 1400 K and overall B fraction z = 0.40;
* the regular solution of step 03 part B (binary_family R1): Day 2's ALPHA plus
  Omega x(1 - x), Omega = 20000 J/mol, used at 800 K and z = 0.15.

Energies are J/mol of atoms; x is the B fraction inside a state and z the
sample's overall B fraction. A *state* is one phase model at one composition (a
dot on the g-x plot). A *menu* is a finite list of states; the *master* chooses
amounts f >= 0 of menu states with sum(f) = 1 and sum(f x) = z at the lowest
energy (a linear programme). Its two multipliers give the *line*
l(x) = mu_A + d_mu x with d_mu = mu_B - mu_A. The *gap curve* is
g(x) - l(x) for every phase model; its deepest point is the *dip*.

Bounds: the best mixture found is a ceiling (G_up). The line slid down parallel
by the deepest dip, read at z, is a floor (G_low = l(z) + min(0, dip)), valid
only when the dip is the true minimum over the whole curve. For the regular
solution a chord (secant) bound on the concave term Omega x(1 - x) gives such
a floor on each interval; branch-and-bound splits [0, 1] until every interval
floor is above -epsilon. All of this is floating point: a teaching check, not
a rigorous numerical certificate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy.optimize import linprog, minimize_scalar
from scipy.special import xlogy

from course.foundations import binary_family as bf
from course.self_study import two_phase_export as tp

R = bf.R                       # 8.3145 J/(mol K), the course value
LENS_T, LENS_Z = 1400.0, 0.40
REG_T, REG_Z, OMEGA = 800.0, 0.15, bf.OMEGA_R1
SCAN_POINTS = 20001            # full-scan pricing grid on [0, 1] for nonconvex curves


def q(x):
    """x ln x + (1 - x) ln(1 - x), with the limit 0 at the pure ends."""
    x = np.asarray(x, dtype=float)
    return xlogy(x, x) + xlogy(1 - x, 1 - x)


# ---------------------------------------------------------------------------
# Phase models. Each has g(x) on [0, 1] (pure ends included) written as
#   g(x) = a + b x + RT q(x) + w x (1 - x),
# a straight end line, the ideal mixing term and an optional regular term.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PhaseModel:
    name: str
    a: float          # g at x = 0 (pure A), J/mol atoms
    b: float          # g(1) - g(0), the end line's rise, J/mol atoms
    T: float
    w: float = 0.0    # regular interaction, J/mol; 0 means ideal

    def g(self, x):
        x = np.asarray(x, dtype=float)
        return self.a + self.b * x + R * self.T * q(x) + self.w * x * (1 - x)

    def slope(self, x):
        """dg/dx at interior x (the exchange mu_B - mu_A of a homogeneous state)."""
        x = np.asarray(x, dtype=float)
        return self.b + R * self.T * np.log(x / (1 - x)) + self.w * (1 - 2 * x)

    def curvature(self, x):
        x = np.asarray(x, dtype=float)
        return R * self.T * (1 / x + 1 / (1 - x)) - 2 * self.w


def lens_models(T: float = LENS_T) -> dict[str, PhaseModel]:
    """The step 03 part C lens: ideal SOLID and LIQUID (A from step 01, an invented B)."""
    out = {}
    for phase in ('SOLID', 'LIQUID'):
        a, bb = tp.lens_g0('A', phase, T), tp.lens_g0('B', phase, T)
        out[phase] = PhaseModel(phase, a, bb - a, T)
    return out


def regular_models(T: float = REG_T) -> dict[str, PhaseModel]:
    """Step 03 part B: Day 2's ALPHA (end line 1000 + 12000 x - 10 T) plus Omega x (1 - x)."""
    return {'ALPHA': PhaseModel('ALPHA', 1000.0 - 10.0 * T, bf.DELTA, T, OMEGA)}


# ---------------------------------------------------------------------------
# The master: the cheapest mixture of a menu.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class State:
    phase: str
    x: float
    g: float


@dataclass
class Master:
    states: list[State]
    f: np.ndarray         # amount of each state (mol atoms per mol sample)
    G_up: float           # the best mixture's energy: a ceiling
    mu_A: float           # height of the line at x = 0
    d_mu: float           # slope of the line, mu_B - mu_A

    @property
    def mu_B(self) -> float:
        return self.mu_A + self.d_mu

    def line(self, x):
        return self.mu_A + self.d_mu * np.asarray(x, dtype=float)

    def used(self, tol: float = 1e-12) -> list[tuple[State, float]]:
        return [(s, float(f)) for s, f in zip(self.states, self.f) if f > tol]


def menu_states(models: dict[str, PhaseModel], xs) -> list[State]:
    return [State(p, float(x), float(m.g(x))) for p, m in models.items() for x in xs]


def solve_master(states: list[State], z: float) -> Master:
    """Lowest-energy amounts with sum f = 1 and sum f x = z (HiGHS dual simplex, so the answer is basic).

    linprog's equality marginals are d(G_up)/d(right-hand side): for the rows
    [1, x] they are (mu_A, d_mu), so mu_A + d_mu z = G_up.
    """
    c = np.array([s.g for s in states])
    A = np.array([[1.0] * len(states), [s.x for s in states]])
    result = linprog(c, A_eq=A, b_eq=[1.0, z], bounds=(0, None), method='highs-ds')
    if not result.success:
        raise ValueError(f'the menu cannot make z = {z}: {result.message}')
    f = np.where(result.x > 1e-14, result.x, 0.0)
    mu_a, d_mu = (float(v) for v in result.eqlin.marginals)
    return Master(list(states), f, float(result.fun), mu_a, d_mu)


def lever(z: float, x_left: float, x_right: float) -> tuple[float, float]:
    """Amounts of the left and right state that make z (the lever rule)."""
    f_right = (z - x_left) / (x_right - x_left)
    return 1 - f_right, f_right


# ---------------------------------------------------------------------------
# Pricing: the deepest point of the gap curve g(x) - line(x) for one phase model.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Dip:
    phase: str
    x: float
    depth: float      # gap at x; negative means a state below the line


def price_ideal(model: PhaseModel, mu_a: float, d_mu: float) -> Dip:
    """Closed form for an ideal phase: the gap's slope b - d_mu + RT ln(x/(1-x)) is zero at a logistic."""
    if model.w:
        raise ValueError('closed-form pricing needs an ideal phase')
    u = (d_mu - model.b) / (R * model.T)
    x = 1 / (1 + math.exp(-u)) if u > -700 else math.exp(u)
    return Dip(model.name, x, float(model.g(x) - mu_a - d_mu * x))


def price_scan(model: PhaseModel, mu_a: float, d_mu: float, points: int = SCAN_POINTS) -> Dip:
    """Full scan of [0, 1], then a bounded local refinement around the best grid point."""
    xs = np.linspace(0.0, 1.0, points)
    gap = model.g(xs) - mu_a - d_mu * xs
    k = int(np.argmin(gap))
    lo, hi = xs[max(k - 1, 0)], xs[min(k + 1, points - 1)]
    best_x, best = float(xs[k]), float(gap[k])
    res = minimize_scalar(lambda v: float(model.g(v) - mu_a - d_mu * v), bounds=(lo, hi), method='bounded',
                          options={'xatol': 1e-13})
    if res.fun < best:
        best_x, best = float(res.x), float(res.fun)
    return Dip(model.name, best_x, best)


def price(model: PhaseModel, mu_a: float, d_mu: float) -> Dip:
    return price_ideal(model, mu_a, d_mu) if model.w == 0 else price_scan(model, mu_a, d_mu)


def deepest(models: dict[str, PhaseModel], mu_a: float, d_mu: float) -> tuple[Dip, dict[str, Dip]]:
    dips = {p: price(m, mu_a, d_mu) for p, m in models.items()}
    return min(dips.values(), key=lambda d: d.depth), dips


def floor(G_line_at_z: float, dip: float) -> float:
    """The Lagrangian floor with one convexity row: the line at z, lowered by the deepest dip (never raised)."""
    return G_line_at_z + min(0.0, dip)


# ---------------------------------------------------------------------------
# Column generation: add the deepest dip, re-solve, repeat.
# ---------------------------------------------------------------------------
@dataclass
class Iteration:
    k: int
    master: Master
    dips: dict[str, Dip]
    best: Dip
    G_low_raw: float
    G_low_best: float

    @property
    def gap(self) -> float:
        return self.master.G_up - self.G_low_best


def column_generation(models: dict[str, PhaseModel], seed: list[State], z: float, tol: float = 1e-6,
                      max_iter: int = 30, line: Callable[[Master, int], tuple[float, float]] | None = None) -> list[Iteration]:
    """One column (the deepest dip over all phase models) per iteration.

    line(master, k) may replace the solver's line by a chosen one (used only to
    illustrate a degenerate master); by default the solver's multipliers are used.
    """
    states = list(seed)
    history: list[Iteration] = []
    best_low = -math.inf
    for k in range(max_iter + 1):
        master = solve_master(states, z)
        if line is not None:
            mu_a, d_mu = line(master, k)
            master = Master(master.states, master.f, master.G_up, mu_a, d_mu)
        best, dips = deepest(models, master.mu_A, master.d_mu)
        raw = floor(float(master.line(z)), best.depth)
        best_low = max(best_low, raw)
        history.append(Iteration(k, master, dips, best, raw, best_low))
        if master.G_up - best_low <= tol or best.depth >= 0:
            break
        states.append(State(best.phase, best.x, float(models[best.phase].g(best.x))))
    return history


# ---------------------------------------------------------------------------
# Chord (secant) floors and branch-and-bound for the regular solution.
# ---------------------------------------------------------------------------
def chord_floor(model: PhaseModel, mu_a: float, d_mu: float, lo: float, hi: float) -> tuple[float, float]:
    """Lowest value on [lo, hi] of the gap with w x(1-x) replaced by its chord.

    w x(1-x) is concave, so it lies above its chord on [lo, hi]: the replaced
    function is below the gap everywhere on the interval (a guaranteed floor).
    It is convex (ideal mixing plus straight lines), so its minimum is where its
    slope b - d_mu + w (1 - lo - hi) + RT ln(x/(1-x)) is zero, clipped to [lo, hi].
    Returns (floor, x where it is reached).
    """
    s = model.b - d_mu + model.w * (1 - lo - hi)
    u = -s / (R * model.T)
    x = 1 / (1 + math.exp(-u)) if u > -700 else math.exp(u)
    x = min(max(x, lo), hi)
    chord = model.w * (lo * (1 - lo) + (1 - lo - hi) * (x - lo))
    value = model.a + model.b * x + R * model.T * float(q(x)) + chord - mu_a - d_mu * x
    return float(value), float(x)


def looseness(model: PhaseModel, lo: float, hi: float) -> float:
    """Largest distance between w x(1-x) and its chord on [lo, hi] (at the midpoint): w (hi - lo)^2 / 4."""
    return model.w * (hi - lo) ** 2 / 4


@dataclass
class Node:
    n: int
    lo: float
    hi: float
    floor: float | None       # None: never examined (the search stopped first)
    x_floor: float | None
    gap_at_x: float | None    # the gap curve itself at x_floor: an evaluated state
    action: str               # 'prune', 'split', 'dip found' or 'open'


@dataclass
class Search:
    nodes: list[Node]
    leaves: list[Node]        # the intervals that cover [0, 1] at the end
    status: str               # 'proved', 'dip found' or 'unresolved'
    found: Node | None = None
    m: float = 0.0            # lowest leaf floor

    def G_low(self, line_at_z: float) -> float:
        return floor(line_at_z, self.m)


def branch_and_bound(model: PhaseModel, mu_a: float, d_mu: float, eps: float = 1.0, max_nodes: int = 500,
                     stop_on_dip: bool = False) -> Search:
    """Prune an interval when its chord floor is at least -eps; split it at the midpoint otherwise.

    Intervals are handled first in, first out. A state whose evaluated gap is
    below -eps is a *dip found* (a column to add); with stop_on_dip the search
    stops there. At most max_nodes intervals are examined; intervals still
    waiting are 'open', with no floor (they were never examined), and the
    result is then 'unresolved', never 'stable'.
    """
    queue = [(0.0, 1.0)]
    nodes, leaves = [], []
    found = None
    while queue:
        if len(nodes) >= max_nodes:
            leaves += [Node(-1, lo2, hi2, None, None, None, 'open') for lo2, hi2 in queue]
            queue = []
            break
        lo, hi = queue.pop(0)
        fl, xf = chord_floor(model, mu_a, d_mu, lo, hi)
        gx = float(model.g(xf) - mu_a - d_mu * xf)
        node = Node(len(nodes), lo, hi, fl, xf, gx, '')
        nodes.append(node)
        if fl >= -eps:
            node.action = 'prune'
            leaves.append(node)
            continue
        if gx < -eps and found is None:
            found = node
            if stop_on_dip:
                node.action = 'dip found'
                leaves.append(node)
                leaves += [Node(-1, lo2, hi2, None, None, None, 'open') for lo2, hi2 in queue]
                queue = []
                break
        node.action = 'dip found' if node is found else 'split'
        mid = 0.5 * (lo + hi)
        queue += [(lo, mid), (mid, hi)]
    leaves.sort(key=lambda nd: nd.lo)
    status = 'dip found' if found else ('proved' if all(nd.action == 'prune' for nd in leaves) else 'unresolved')
    floors = [nd.floor for nd in leaves if nd.floor is not None]
    m = min(floors) if floors else 0.0
    return Search(nodes, leaves, status, found, m)


# ---------------------------------------------------------------------------
# A checkable answer and its verifier (independent of the solver above).
# ---------------------------------------------------------------------------
@dataclass
class Answer:
    states: list[tuple[str, float, float]]      # (phase, x, f)
    mu_A: float
    d_mu: float
    intervals: list[tuple[float, float]]
    eps: float
    z: float
    tolerance: float
    claimed_G_up: float
    claimed_G_low: float
    notes: list[str] = field(default_factory=list)


def verify(answer: Answer, model: PhaseModel, slack: float = 1e-9) -> tuple[bool, list[str]]:
    """Recompute everything from the formula: a floating-point teaching check, not a rigorous certificate.

    Checks: the mixture is feasible (f >= 0, sum f = 1, sum f x = z) and its
    energy is the claimed ceiling; the intervals cover [0, 1] without holes;
    every interval's chord floor (recomputed here) is at least -eps; the floor
    l(z) + min(0, lowest interval floor) is the claimed floor; and
    ceiling - floor is within the tolerance.
    """
    problems = []
    f = np.array([s[2] for s in answer.states])
    x = np.array([s[1] for s in answer.states])
    if np.any(f < 0) or abs(f.sum() - 1) > slack or abs(f @ x - answer.z) > slack:
        problems.append('the mixture does not make the sample (amounts or B balance)')
    g_up = float(sum(fi * model.g(xi) for (_, xi, fi) in answer.states))
    if abs(g_up - answer.claimed_G_up) > 1e-6:
        problems.append('the ceiling is not the mixture energy')
    iv = sorted(answer.intervals)
    if not iv or iv[0][0] != 0.0 or iv[-1][1] != 1.0 or any(a[1] != b[0] for a, b in zip(iv, iv[1:])):
        problems.append('the intervals do not cover [0, 1] without holes')
    lows = []
    for lo, hi in iv:
        fl, _ = chord_floor(model, answer.mu_A, answer.d_mu, lo, hi)
        lows.append(fl)
        if fl < -answer.eps:
            problems.append(f'interval [{lo}, {hi}] has floor {fl:.4g} below -eps')
    g_low = floor(answer.mu_A + answer.d_mu * answer.z, min(lows) if lows else -math.inf)
    if abs(g_low - answer.claimed_G_low) > 1e-6:
        problems.append('the floor is not the line lowered by the lowest interval floor')
    if g_up - g_low > answer.tolerance + slack:
        problems.append('ceiling minus floor exceeds the tolerance')
    return not problems, problems


# ---------------------------------------------------------------------------
# The draggable line's reveal: lift, then pivot from dot to dot.
# ---------------------------------------------------------------------------
def lift_and_pivot(states: list[State], z: float, slope: float) -> list[dict]:
    """Frames of the reveal animation, starting from a line of the given slope.

    Lift the line until it touches a dot. Then, while the touching dots do not
    bracket z (one on each side) and none sits at z, pivot about the touching
    dot in the direction that raises the height at z until the next dot
    touches; that dot becomes the new pivot. Every frame keeps all dots on or
    above the line (a floor).
    """
    xs = np.array([s.x for s in states])
    gs = np.array([s.g for s in states])
    k = int(np.argmin(gs - slope * xs))
    mu_a = float(gs[k] - slope * xs[k])
    frames = [{'mu_A': mu_a, 'd_mu': slope, 'touch': [k]}]
    for _ in range(len(states)):
        xc, gc = xs[k], gs[k]
        if abs(xc - z) < 1e-12:
            break
        if xc > z:                 # rotate to lower the slope: the first dot hit has the largest chord slope from the left
            cand = [((gc - gs[j]) / (xc - xs[j]), j) for j in range(len(xs)) if xs[j] < xc - 1e-12]
            slope, j = max(cand)
        else:
            cand = [((gs[j] - gc) / (xs[j] - xc), j) for j in range(len(xs)) if xs[j] > xc + 1e-12]
            slope, j = min(cand)
        mu_a = float(gc - slope * xc)
        frames.append({'mu_A': mu_a, 'd_mu': float(slope), 'touch': [k, j]})
        if (xs[j] - z) * (xc - z) <= 0:
            break
        k = j
    return frames


def bb_deepest(model: PhaseModel, mu_a: float, d_mu: float, tol: float = 1.0, max_nodes: int = 500) -> Search:
    """Branch-and-bound as a search for the deepest dip (a pricer that cannot miss a valley).

    The best evaluated gap so far is the incumbent. An interval is pruned when
    its chord floor is at least incumbent - tol (it cannot hold a dip deeper by
    more than tol); otherwise it is split. Lowest floor first. The result's
    `found` is the node whose evaluated state is the incumbent.
    """
    import heapq
    nodes: list[Node] = []
    leaves: list[Node] = []
    heap: list[tuple[float, int, float, float]] = []
    best: Node | None = None

    def visit(lo: float, hi: float) -> Node:
        nonlocal best
        fl, xf = chord_floor(model, mu_a, d_mu, lo, hi)
        mid = 0.5 * (lo + hi)
        candidates = [(float(model.g(v) - mu_a - d_mu * v), v) for v in (xf, mid)]
        gx, xv = min(candidates)
        node = Node(len(nodes), lo, hi, fl, xv, gx, '')
        nodes.append(node)
        if best is None or gx < best.gap_at_x:
            best = node
        heapq.heappush(heap, (fl, node.n, lo, hi))
        return node

    visit(0.0, 1.0)
    while heap:
        fl, n, lo, hi = heapq.heappop(heap)
        node = nodes[n]
        if fl >= best.gap_at_x - tol:
            node.action = 'prune'
            leaves.append(node)
            continue
        if len(nodes) + 2 > max_nodes:
            node.action = 'open'
            leaves.append(node)
            continue
        node.action = 'split'
        mid = 0.5 * (lo + hi)
        visit(lo, mid)
        visit(mid, hi)
    for node in nodes:
        if node.action == '':
            node.action = 'open'
            leaves.append(node)
    leaves.sort(key=lambda nd: nd.lo)
    status = 'proved' if all(nd.action == 'prune' for nd in leaves) else 'unresolved'
    return Search(nodes, leaves, status, best, min(nd.floor for nd in leaves))


def local_descent(model: PhaseModel, mu_a: float, d_mu: float, start: float, step: float = 2e-5,
                  max_steps: int = 400) -> list[float]:
    """The computer's local search on the gap curve (not what atoms do): steepest descent with halving steps.

    Each move goes downhill along the gap curve's slope; a move that would not
    lower the gap is halved. Returns the visited compositions.
    """
    x = start
    path = [x]

    def gap(v: float) -> float:
        return float(model.g(v) - mu_a - d_mu * v)

    for _ in range(max_steps):
        s = float(model.slope(x)) - d_mu
        if abs(s) < 1e-6:
            break
        h = step
        moved = False
        while h * abs(s) > 1e-12:
            v = min(max(x - h * s, 1e-12), 1 - 1e-12)
            if gap(v) < gap(x):
                x, moved = v, True
                break
            h /= 2
        if not moved:
            break
        path.append(x)
    return path
