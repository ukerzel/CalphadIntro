"""Figures for the paper primers: the D3 tangent and the two-phase sheet.

Every curve and number comes from existing course models: Day 2's ALPHA and
the I2 ALPHA/BETA pair (course/foundations/binary_family.py), the regular
solution R1 (same file) and the melting lens of self-study step 03 part C
(course/self_study/two_phase_export.py). Nothing here is a new model.
Energies are J/mol of atoms; x and z are B atom fractions.

Run from the repository root (writes PNGs next to the Day 2 worksheet):
    .venv/bin/python -m course.print.paper_figures
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from course.foundations import binary_family as bf
from course.self_study import two_phase_export as tp

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / 'course' / 'primer_day2' / 'figures'
T_DAY2, X_D3 = 1000.0, 0.10          # D3: Day 2's ALPHA at the bulk fraction of D1-D2
T_LENS, Z_LENS = 1400.0, 0.40        # the lens case that step 10 starts from
T_REG = 800.0                        # the regular solution of step 03 part B
Z_SPLIT = 0.30                       # the sheet's lever-rule check on the ALPHA/BETA pair


def d3_numbers() -> dict:
    """The tangent of Day 2's ALPHA at x = 0.10 and the dashed reference line."""
    d = bf.ideal_derivatives(T_DAY2, X_D3, 'ALPHA')
    g = float(bf.ideal_properties(T_DAY2, X_D3, 'ALPHA')['GM'])
    mu_a, mu_b = float(d['mu_A']), float(d['mu_B'])
    # The tangent touches the curve at x: mu_A + (mu_B - mu_A) x = g.
    if abs(mu_a + (mu_b - mu_a) * X_D3 - g) > 1e-9:
        raise ValueError('D3 tangent does not touch the curve')
    ref_a = float(bf.ideal_properties(T_DAY2, 0.0, 'ALPHA')['GM'])
    ref_b = float(bf.ideal_properties(T_DAY2, 1.0, 'ALPHA')['GM'])
    return {'x': X_D3, 'g': g, 'mu_A': mu_a, 'mu_B': mu_b, 'slope': mu_b - mu_a, 'ref_A': ref_a, 'ref_B': ref_b}


def split_numbers() -> dict:
    """ALPHA/BETA common tangent at 1000 K and the lever rule at z = 0.30."""
    regions = bf.ideal_equilibrium(T_DAY2, Z_SPLIT)['regions']
    (a, b) = sorted(regions, key=lambda r: r['x'])
    d = bf.ideal_derivatives(T_DAY2, a['x'], 'ALPHA')
    f_beta = (Z_SPLIT - a['x']) / (b['x'] - a['x'])
    if abs(f_beta - b['f']) > 1e-12:
        raise ValueError('lever rule differs from the course solver')
    return {'x_ALPHA': float(a['x']), 'x_BETA': float(b['x']), 'z': Z_SPLIT, 'f_ALPHA': float(1 - f_beta), 'f_BETA': float(f_beta),
            'mu_A': float(d['mu_A']), 'mu_B': float(d['mu_B'])}


def lens_numbers() -> dict:
    x_s, x_l = tp.lens_coexistence(T_LENS)
    f_s = (Z_LENS - x_l) / (x_s - x_l)
    return {'T': T_LENS, 'z': Z_LENS, 'x_SOLID': x_s, 'x_LIQUID': x_l, 'f_SOLID': f_s, 'f_LIQUID': 1 - f_s}


def regular_numbers() -> dict:
    gap = bf.regular_binodal(T_REG)
    return {'T': T_REG, 'omega': bf.OMEGA_R1, 'binodal': gap['compositions'], 'spinodal': gap['spinodal']}


def _axes(fig, ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    fig.tight_layout()


def draw_d3(plt, path: Path) -> None:
    n = d3_numbers()
    x = np.linspace(0.0, 1.0, 401)
    g = bf.ideal_properties(T_DAY2, x, 'ALPHA')['GM']
    fig, ax = plt.subplots(figsize=(6.0, 3.9))
    ax.plot(x, g, color='black', lw=2, label='$g_b(x)$, Day 2 ALPHA at 1000 K')
    ax.plot([0, 1], [n['ref_A'], n['ref_B']], color='0.45', lw=1.2, ls='--', label='reference line $-9000+12000x$')
    ax.plot([0, 1], [n['mu_A'], n['mu_B']], color='#1f5fa8', lw=1.6, label='tangent at $x_b=0.10$')
    ax.plot([n['x']], [n['g']], 'o', color='#1f5fa8')
    ax.plot([0, 1], [n['mu_A'], n['mu_B']], 's', color='#1f5fa8', ms=6, clip_on=False)
    ax.annotate(f"$\\mu_A\\approx{n['mu_A']:.1f}$", (0, n['mu_A']), (0.03, n['mu_A'] - 2600), fontsize=10, color='#1f5fa8')
    ax.annotate(f"$\\mu_B\\approx{n['mu_B']:.1f}$", (1, n['mu_B']), (0.76, n['mu_B'] + 2700), fontsize=10, color='#1f5fa8')
    ax.annotate('slope $=\\mu_B-\\mu_A$', (0.55, n['mu_A'] + 0.55 * n['slope']), (0.38, n['mu_A'] + 0.55 * n['slope'] - 3400),
                fontsize=10, color='#1f5fa8', arrowprops={'arrowstyle': '->', 'color': '#1f5fa8'})
    ax.set_xlim(0, 1)
    ax.set_xlabel('B atom fraction $x$')
    ax.set_ylabel('J/mol atoms')
    ax.legend(fontsize=8.5, loc='upper left', frameon=False)
    _axes(fig, ax)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def draw_split(plt, path: Path) -> None:
    n = split_numbers()
    x = np.linspace(0.0, 1.0, 401)
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    for phase, colour in (('ALPHA', '#1f5fa8'), ('BETA', '#b5512b')):
        ax.plot(x, bf.ideal_properties(T_DAY2, x, phase)['GM'], color=colour, lw=2, label=f'{phase} at 1000 K')
    ax.plot([0, 1], [n['mu_A'], n['mu_B']], color='black', lw=1.2, label='common tangent')
    ax.plot([n['x_ALPHA'], n['x_BETA']], [n['mu_A'] + (n['mu_B'] - n['mu_A']) * v for v in (n['x_ALPHA'], n['x_BETA'])], 'ko')
    ax.axvline(n['z'], color='0.5', lw=1, ls=':')
    ax.text(n['z'] + 0.01, -4500, f"$z={n['z']:.2f}$", fontsize=9)
    ax.text(0.01, n['mu_A'] + 350, '$\\mu_A$', fontsize=10)
    ax.text(0.94, n['mu_B'] + 350, '$\\mu_B$', fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_xlabel('B atom fraction $x$')
    ax.set_ylabel('J/mol atoms')
    ax.legend(fontsize=8.5, loc='upper center', frameon=False)
    _axes(fig, ax)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def draw_lens(plt, path: Path) -> None:
    n = lens_numbers()
    temps = np.linspace(1000.5, 1799.5, 400)
    pairs = [tp.lens_coexistence(t) for t in temps]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot([p[1] for p in pairs], temps, color='#b5512b', lw=2, label='liquidus (liquid composition)')
    ax.plot([p[0] for p in pairs], temps, color='#1f5fa8', lw=2, label='solidus (solid composition)')
    ax.plot([n['x_LIQUID'], n['x_SOLID']], [T_LENS, T_LENS], 'k-o', lw=1.4, ms=4, label='tie line at 1400 K')
    ax.plot([n['z']], [T_LENS], 'kD', ms=5)
    ax.text(n['z'] - 0.02, T_LENS + 30, f"$z={n['z']:.2f}$", fontsize=9)
    ax.text(0.78, 1450, 'SOLID', fontsize=10)
    ax.text(0.12, 1650, 'LIQUID', fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(950, 1850)
    ax.set_xlabel('B atom fraction')
    ax.set_ylabel('T / K')
    ax.legend(fontsize=8.5, loc='lower right', frameon=False)
    _axes(fig, ax)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def draw_regular(plt, path: Path) -> None:
    n = regular_numbers()
    x = np.linspace(0.0, 1.0, 801)
    mix = bf.regular_properties(T_REG, x)['GM_mix']
    left, right = n['binodal']
    level = float(bf.regular_properties(T_REG, left)['GM_mix'])
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(x, mix, color='#1f5fa8', lw=2, label='one phase model (ALPHA with $\\Omega$) at 800 K')
    ax.plot([0, 1], [level, level], color='black', lw=1.2, label='one tangent, touching twice')
    ax.plot([left, right], [level, level], 'ko')
    ax.text(left + 0.025, level + 25, f'{left:.3f}', fontsize=9)
    ax.text(right - 0.025, level + 25, f'{right:.3f}', ha='right', fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xlabel('B atom fraction $x$')
    ax.set_ylabel('$g$ minus its end line, J/mol atoms')
    ax.legend(fontsize=8.5, loc='lower center', bbox_to_anchor=(0.5, 0.08), frameon=False)
    _axes(fig, ax)
    fig.savefig(path, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Day 2: counts, the teaching cell, the open boundary, the closed ledger, two states.
# ---------------------------------------------------------------------------
X_D1, F_D1 = (0.10, 0.50), (0.5, 0.5)       # D1's worked count
X_D5, DELTA_D5 = 0.10, -5000.0              # D5: reservoir bulk fraction and boundary preference
X0_D6 = 0.10                                # D6: start of the closed cell
D7_ROWS = (0.10, 0.25)                      # D7: the two tabulated starting bulk fractions


def d1_numbers() -> dict:
    z = sum(f * x for f, x in zip(F_D1, X_D1))
    a = sum(f * (1 - x) for f, x in zip(F_D1, X_D1))
    return {'x': X_D1, 'f': F_D1, 'z': z, 'A': a}


def d4_numbers() -> dict:
    from course.foundations import boundary_one_state as b1, boundary_two_state as b2
    return {'bulk_sites': b2.BULK_SITES, 'sites_per_boundary': b1.SITES_PER_BOUNDARY,
            'boundaries': b2.BOUNDARY_SITES / b1.SITES_PER_BOUNDARY, 'cell_sites': b2.CELL_SITES,
            'area_per_boundary_nm2': b1.AREA_PER_BOUNDARY_M2 * 1e18}


def d5_numbers() -> dict:
    """The bulk tangent at x_b and the parallel line touching the boundary function at θ*."""
    from course.foundations import boundary_one_state as b1
    out = b1.open_equilibrium(X_D5, DELTA_D5)
    d = bf.ideal_derivatives(b1.TEMPERATURE, X_D5, 'ALPHA')
    mu_a, mu_b = float(d['mu_A']), float(d['mu_B'])
    theta = out['theta_analytic']
    g_s = float(bf.ideal_properties(b1.TEMPERATURE, theta, 'ALPHA')['GM']) + DELTA_D5 * theta
    phi = g_s - (mu_a + (mu_b - mu_a) * theta)        # how far the parallel line lies below the tangent
    if abs(phi - out['phi_J_per_mol_sites']) > 1e-6:
        raise ValueError('the parallel line does not match the grand potential')
    return {'x_b': X_D5, 'delta': DELTA_D5, 'theta': theta, 'mu_A': mu_a, 'mu_B': mu_b, 'phi': phi, 'g_s': g_s}


def d6_numbers() -> dict:
    from course.foundations import boundary_closed as bc, boundary_two_state as b2
    start_bulk, start_boundary = b2.BULK_SITES * X0_D6, b2.BOUNDARY_SITES * 0.25
    out = bc.closed_equilibrium(X0_D6, DELTA_D5)
    return {'start_bulk_B': start_bulk, 'start_boundary_B': start_boundary, 'total_B': start_bulk + start_boundary,
            'theta': out['theta'], 'x_bulk': out['x_bulk'], 'model_total_B': out['total_B_atoms']}


def d7_curve(points: int = 31) -> dict:
    """D = ḡ_II* − ḡ_I* against the starting bulk fraction, the two tabulated rows and the crossing."""
    from course.foundations import boundary_two_state as b2
    xs = np.linspace(0.10, 0.40, points)
    ds = [float(b2.compare_states(x)['difference_J_per_mol_sites']) for x in xs]
    rows = {x: b2.compare_states(x) for x in D7_ROWS}
    return {'x0': xs.tolist(), 'D': ds, 'crossing': float(b2.crossing()['x_initial']),
            'rows': {x: {'I': r['I']['G_molar_J_per_mol_sites'], 'II': r['II']['G_molar_J_per_mol_sites'],
                         'D': r['difference_J_per_mol_sites']} for x, r in rows.items()}}


def draw_d1(plt, path: Path) -> None:
    n = d1_numbers()
    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    left = 0.0
    for i, (f, x) in enumerate(zip(n['f'], n['x'])):
        ax.add_patch(plt.Rectangle((left, 0), f, 1, fc='#e8eef9', ec='black', lw=1.2))
        ax.add_patch(plt.Rectangle((left, 0), f, x, fc='#b5512b', ec='none', alpha=.75))
        ax.text(left + f / 2, 1.08, f'region {i + 1}: $f={f}$', ha='center', fontsize=9.5)
        ax.text(left + f / 2, x + 0.04, f'B share $x={x:.2f}$', ha='center', fontsize=9, color='#7a2e10')
        left += f
    ax.add_patch(plt.Rectangle((1.15, 0), 0.25, 1, fc='#e8eef9', ec='black', lw=1.2))
    ax.add_patch(plt.Rectangle((1.15, 0), 0.25, n['z'], fc='#b5512b', ec='none', alpha=.75))
    ax.text(1.275, 1.08, 'whole sample', ha='center', fontsize=9.5)
    ax.text(1.275, n['z'] + 0.04, f"$z={n['z']:.2f}$", ha='center', fontsize=9, color='#7a2e10')
    ax.annotate('', (0, -0.12), (1, -0.12), arrowprops={'arrowstyle': '<->'})
    ax.text(0.5, -0.24, 'width: how much of the sample ($f$), adding to 1', ha='center', fontsize=9)
    ax.set_xlim(-0.05, 1.45); ax.set_ylim(-0.32, 1.22); ax.axis('off')
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def draw_d4(plt, path: Path) -> None:
    n = d4_numbers()
    fig, ax = plt.subplots(figsize=(6.4, 2.2))
    blocks = [(0, 0.45, 'bulk'), (0.45, 0.05, 'gb'), (0.5, 0.45, 'bulk'), (0.95, 0.05, 'gb')]
    for x0, w, kind in blocks:
        ax.add_patch(plt.Rectangle((x0, 0), w, 1, fc='#e8eef9' if kind == 'bulk' else '#d9a441', ec='black', lw=1.1))
    ax.text(0.475, 1.12, f"boundary: {n['sites_per_boundary']:.0f} sites, {n['area_per_boundary_nm2']:.0f} nm²", ha='center', fontsize=9)
    ax.text(0.975, 1.12, 'boundary (same)', ha='center', fontsize=9)
    for cx in (0.225, 0.725):
        ax.text(cx, 0.5, 'bulk', ha='center', va='center', fontsize=10)
    ax.text(0.475, -0.05, f"bulk: {n['bulk_sites']} sites in all", ha='center', va='top', fontsize=9)
    ax.text(0.5, -0.27, f"one periodic cell: {n['bulk_sites']} + {int(n['boundaries'])} × {n['sites_per_boundary']:.0f} = {n['cell_sites']} sites;"
            f" {int(n['boundaries'])} × {n['area_per_boundary_nm2']:.0f} = {int(n['boundaries'] * n['area_per_boundary_nm2'])} nm² of boundary",
            ha='center', fontsize=9)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.42, 1.25); ax.axis('off')
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def draw_d5(plt, path: Path) -> None:
    n = d5_numbers()
    x = np.linspace(0.0, 0.4, 401)
    g_b = bf.ideal_properties(T_DAY2, x, 'ALPHA')['GM']
    slope = n['mu_B'] - n['mu_A']
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot(x, g_b, color='black', lw=2, label='bulk $g_b$')
    ax.plot(x, g_b + n['delta'] * x, color='#7a3fc0', lw=2, label=r'boundary $g_s=g_b+\delta\theta$')
    ax.plot(x, n['mu_A'] + slope * x, color='#1f5fa8', lw=1.4, label='bulk tangent at $x_b=0.10$')
    ax.plot(x, n['mu_A'] + n['phi'] + slope * x, color='#1f5fa8', lw=1.4, ls='--', label='the same line, slid down')
    ax.plot([n['x_b']], [n['mu_A'] + slope * n['x_b']], 'o', color='#1f5fa8')
    ax.plot([n['theta']], [n['g_s']], 'o', color='#7a3fc0')
    ax.annotate(rf"$\theta_*\approx{n['theta']:.5f}$", (n['theta'], n['g_s']), (n['theta'] + 0.04, n['g_s'] - 900), fontsize=9,
                arrowprops={'arrowstyle': '->'})
    ax.set(xlim=(0, 0.4), ylim=(-12500, -7000), xlabel='B fraction ($x$ for bulk, $\\theta$ for boundary sites)', ylabel='J/mol sites')
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def draw_d6(plt, path: Path) -> None:
    n = d6_numbers()
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    labels = ['bulk B', 'boundary B', 'total B']
    start = [n['start_bulk_B'], n['start_boundary_B'], n['total_B']]
    ax.bar([0, 1, 2], start, width=0.35, color=['#1f5fa8', '#d9a441', '#555555'], label='start: $x_0=0.10$, $\\theta_0=0.25$')
    ax.bar([0.4, 1.4, 2.4], [0, 0, n['total_B']], width=0.35, fill=False, ec='black', ls='--', label='after minimising: fill in')
    for i, v in enumerate(start):
        ax.text(i, v + 15, f'{v:.0f}', ha='center', fontsize=9)
    ax.text(2.4, n['total_B'] + 15, f"{n['total_B']:.0f}", ha='center', fontsize=9)
    ax.axhline(n['total_B'], color='0.5', lw=0.8, ls=':')
    ax.set_xticks([0.2, 1.2, 2.2], labels); ax.set_ylabel('B atoms in the 8200-site cell'); ax.set_ylim(0, 1000)
    ax.legend(fontsize=8, frameon=False, loc='center', bbox_to_anchor=(0.5, 0.62))
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def draw_d7(plt, path: Path) -> None:
    n = d7_curve()
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.plot(n['x0'], n['D'], color='black', lw=1.8)
    ax.axhline(0, color='0.4', lw=0.8)
    ax.axvline(n['crossing'], color='#b5512b', ls=':', lw=1)
    ax.text(n['crossing'] + 0.005, 10, f"crossing near {n['crossing']:.5f}", fontsize=9, color='#b5512b')
    for x0, row in n['rows'].items():
        ax.plot([x0], [row['D']], 'o', color='#1f5fa8')
    ax.text(0.30, 15, '$D>0$: state I lower', fontsize=9); ax.text(0.12, -18, '$D<0$: state II lower', fontsize=9)
    ax.set(xlim=(0.10, 0.40), xlabel='starting bulk B fraction $x_0$', ylabel='$D$, J/mol all sites')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


FIGURE_FILES = {'d3_tangent.png': draw_d3, 'twophase_tangent.png': draw_split,
                'twophase_lens.png': draw_lens, 'twophase_regular.png': draw_regular,
                'd1_counts.png': draw_d1, 'd4_cell.png': draw_d4, 'd5_parallel.png': draw_d5,
                'd6_ledger.png': draw_d6, 'd7_crossing.png': draw_d7}


def main() -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt': 'calphad', 'font.size': 10})
    FIGURES.mkdir(exist_ok=True)
    for name, draw in FIGURE_FILES.items():
        draw(plt, FIGURES / name)
        print('wrote', (FIGURES / name).relative_to(ROOT))
    for label, numbers in (('D3', d3_numbers()), ('split', split_numbers()), ('lens', lens_numbers()), ('regular', regular_numbers())):
        print(label, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in numbers.items()})


if __name__ == '__main__':
    main()
