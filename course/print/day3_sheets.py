"""Printable material for the advanced steps: the picture sheet, the card deck and the game kit.

Every number comes from course/self_study/generated/day3.json (made by
course/self_study/day3_export.py), the LP primer sheet's two figures from
generated/lp_primer.json (course/self_study/lp_primer.py), and every card from
course/self_study/cards.json,
so the paper and the web pages agree. Writes PNG figures to course/day3/figures/
and three Markdown sheets to course/day3/; build_print.py turns them into PDFs.

Run from the repository root:
    .venv/bin/python -m course.print.day3_sheets
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DAY3 = ROOT / 'course' / 'day3'
FIGURES = DAY3 / 'figures'
DATA = ROOT / 'course' / 'self_study' / 'generated' / 'day3.json'
CARDS = ROOT / 'course' / 'self_study' / 'cards.json'
LP_DATA = ROOT / 'course' / 'self_study' / 'generated' / 'lp_primer.json'
SOLID, LIQUID, LINE, MIN = '#2445c4', '#cf4418', '#8f6400', '#b58900'
ACTION = {'prune': '#2a9d8f', 'split': '#e9c46a', 'dip found': '#ad3810', 'open': '#bbbbbb'}


def data() -> dict:
    return json.loads(DATA.read_text())


def _axes(fig, ax) -> None:
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    fig.tight_layout()


def menu_line(plt, lens: dict, path: Path) -> None:
    line, z = lens['s2'], lens['z']
    fig, ax = plt.subplots(figsize=(6.6, 2.7))
    for phase, colour in (('SOLID', SOLID), ('LIQUID', LIQUID)):
        ax.plot(lens['curve']['x'], lens['curve'][phase], color=colour, lw=1, alpha=.25)
        dots = [p for p in lens['menu']['dots'] if p['phase'] == phase]
        ax.plot([p['x'] for p in dots], [p['g'] for p in dots], 'o', color=colour, label=phase)
    ax.plot([0, 1], [line['mu_A'], line['mu_B']], color=LINE, lw=1.6, label='the line of the menu')
    ax.axvline(z, color='0.5', ls=':', lw=1)
    ax.annotate(f"μA = {line['mu_A']:.1f}", (0, line['mu_A']), (0.02, line['mu_A'] + 350), fontsize=9, color=LINE)
    ax.annotate(f"μB = {line['mu_B']:.1f}", (1, line['mu_B']), (0.70, line['mu_B'] + 350), fontsize=9, color=LINE)
    ax.set(xlim=(0, 1), ylim=(-21500, -11500), xlabel='B atom fraction x', ylabel='g, J/mol atoms', title='The menu and its line (steps 10–11)')
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def gap_curve(plt, lens: dict, path: Path) -> None:
    line, xs = lens['s2'], np.array(lens['curve']['x'])
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    for phase, colour in (('SOLID', SOLID), ('LIQUID', LIQUID)):
        ax.plot(xs, np.array(lens['curve'][phase]) - (line['mu_A'] + line['d_mu'] * xs), color=colour, label=phase)
        dots = [g for g in lens['s4']['gaps'] if g['phase'] == phase]
        ax.plot([g['x'] for g in dots], [g['gap'] for g in dots], 'o', color=colour)
    for dip in lens['s7']['dips'].values():
        ax.annotate(f"{dip['depth']:.1f}", (dip['x'], dip['depth']), (dip['x'] + 0.03, dip['depth'] - 40), fontsize=9,
                    arrowprops={'arrowstyle': '->', 'color': MIN})
    ax.axhline(0, color='black', lw=0.8)
    ax.set(xlim=(0.2, 0.6), ylim=(-100, 600), xlabel='B atom fraction x', ylabel='gap, J/mol atoms', title='The gap curve against the menu\'s line (step 12)')
    ax.legend(fontsize=8, frameon=False)
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def bounds(plt, lens: dict, path: Path) -> None:
    its = lens['s6']['iterations'][:4]
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    for k, it in enumerate(its):
        ax.plot([it['G_low_best'], it['G_up']], [k, k], color='0.4', lw=2)
        ax.plot(it['G_up'], k, 'o', color=MIN); ax.plot(it['G_low_best'], k, 'o', color=SOLID)
        ax.text(it['G_up'] + 1.5, k, f"{it['remaining']:.4g}", va='center', fontsize=8)
    ax.axvline(lens['truth']['G'], color=LIQUID, ls='--', lw=1, label='truth')
    ax.set(yticks=range(len(its)), yticklabels=[f'round {k}' for k in range(len(its))], xlabel='energy at z, J/mol atoms',
           title='Floor (blue), ceiling (gold) and the remaining uncertainty (step 14)')
    ax.invert_yaxis(); ax.legend(fontsize=8, frameon=False, loc='lower left')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def intervals(plt, reg: dict, path: Path) -> None:
    s9, xs = reg['s9'], np.array(reg['curve']['x'])
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(xs, np.array(reg['curve']['ALPHA']) - (s9['line']['mu_A'] + s9['line']['d_mu'] * xs), color=SOLID, lw=1.4)
    ax.axhline(0, color='black', lw=0.8); ax.axhline(-s9['eps'], color=MIN, ls=':', lw=1)
    for leaf in s9['leaves']:
        ax.add_patch(__import__('matplotlib.patches', fromlist=['Rectangle']).Rectangle(
            (leaf['lo'], -38), leaf['hi'] - leaf['lo'], 12, color=ACTION[leaf['action']], ec='white'))
    ax.set(xlim=(0, 1), ylim=(-45, 120), xlabel='B atom fraction x', ylabel='gap, J/mol atoms',
           title=f"Branch-and-bound: {len(s9['leaves'])} pruned intervals cover [0, 1] (step 16)")
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def dot_sheet(plt, lens: dict, path: Path, curves: bool) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for phase, colour in (('SOLID', SOLID), ('LIQUID', LIQUID)):
        if curves:
            ax.plot(lens['curve']['x'], lens['curve'][phase], color=colour, label=phase)
        else:
            dots = [p for p in lens['menu']['dots'] if p['phase'] == phase]
            ax.plot([p['x'] for p in dots], [p['g'] for p in dots], 'o', color=colour, label=phase)
    ax.axvline(lens['z'], color='0.5', ls=':', lw=1)
    if curves:   # zoomed, so a dip of a few tens of J/mol is visible on paper
        ax.set_xticks(np.arange(0.28, 0.4801, 0.02), minor=True); ax.set_yticks(np.arange(-20620, -20219, 20), minor=True)
        ax.grid(True, which='both', color='0.85', lw=0.5)
        ax.set(xlim=PRICER_X, ylim=PRICER_Y, xlabel='B atom fraction x', ylabel='g, J/mol atoms',
               title='The full curves, zoomed (the pricer\'s sheet)')
    else:
        ax.grid(True, color='0.85', lw=0.6)
        ax.set(xlim=(0, 1), ylim=(-21500, -11500), xlabel='B atom fraction x', ylabel='g, J/mol atoms',
               title='The menu\'s dots (the master\'s sheet)')
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def lp_dots(plt, blend: dict, path: Path) -> None:
    """The LP primer sheet, part 2: six lots, price against Ni content, on a grid fine enough for a ruler."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for lot in blend['lots']:
        ax.plot(lot['w'], lot['price'], 'o', color=SOLID)
        ax.annotate(lot['short'], (lot['w'], lot['price']), textcoords='offset points', xytext=(-6 if lot['w'] > 0.9 else 6, 6),
                    ha='right' if lot['w'] > 0.9 else 'left', fontsize=9)
    ax.axvline(blend['target'], color='0.5', ls=':', lw=1)
    ax.set_xticks(np.arange(0, 1.001, 0.05), minor=True); ax.set_yticks(np.arange(6, 16.01, 0.25), minor=True)
    ax.grid(True, which='both', color='0.88', lw=0.5)
    ax.set(xlim=(-0.03, 1.03), ylim=(6, 16.5), xlabel='Ni content w (kg Ni per kg)', ylabel='price, € per kg', title='Six lots of scrap (invented prices)')
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


def lp_polygon(plt, poly: dict, path: Path) -> None:
    """The LP primer sheet, part 5: the four rule lines and the allowed polygon, without the answer."""
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    corners = poly['regions']['normal']
    ax.fill([c['f'][0] for c in corners], [c['f'][1] for c in corners], color='#2a9d8f', alpha=0.22, label='allowed charges')
    fp = np.array([0.0, 1.7])
    names = {'charge': 'weight ≥ 1', 'ni': 'nickel ≥ 0.40', 'fe': 'iron ≤ 0.012', 'furnace': 'furnace ≤ 1.5'}
    for rule in poly['rules']:
        b = poly['fe_cap']['normal'] if rule['id'] == 'fe' else rule['b']
        ax.plot(fp, (b - rule['a'][0] * fp) / rule['a'][1], lw=1.3, label=names[rule['id']])
    for c in corners:
        ax.plot(*c['f'], 'o', color='0.2', ms=4)
    ax.set_xticks(np.arange(0, 1.701, 0.05), minor=True); ax.set_yticks(np.arange(0, 0.801, 0.025), minor=True)
    ax.grid(True, which='both', color='0.88', lw=0.5)
    ax.set(xlim=(0, 1.7), ylim=(0, 0.8), xlabel='f_P: kg of CuNi30', ylabel='f_Q: kg of Monel', title='Two lots, four rules')
    ax.legend(fontsize=8, frameon=False, loc='upper right', ncol=2)
    _axes(fig, ax); fig.savefig(path, dpi=200); plt.close(fig)


PRICER_X, PRICER_Y = (0.28, 0.48), (-20620, -20220)   # the pricer's zoomed window
FIGS = ['menu_line', 'gap_curve', 'bounds', 'intervals', 'dot_sheet', 'curve_sheet', 'lp_dots', 'lp_polygon']


def figures() -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d = data()
    FIGURES.mkdir(parents=True, exist_ok=True)
    menu_line(plt, d['lens'], FIGURES / 'menu_line.png')
    gap_curve(plt, d['lens'], FIGURES / 'gap_curve.png')
    bounds(plt, d['lens'], FIGURES / 'bounds.png')
    intervals(plt, d['regular'], FIGURES / 'intervals.png')
    dot_sheet(plt, d['lens'], FIGURES / 'dot_sheet.png', curves=False)
    dot_sheet(plt, d['lens'], FIGURES / 'curve_sheet.png', curves=True)
    lp = json.loads(LP_DATA.read_text())
    lp_dots(plt, lp['blend'], FIGURES / 'lp_dots.png')
    lp_polygon(plt, lp['polygon'], FIGURES / 'lp_polygon.png')


def plain(text: str) -> str:
    """Narration markup to Markdown: cross-references and card links keep only their words."""
    return re.sub(r'\[\[[a-z][a-z0-9#/-]*\|([^\]|]+)\]\]', r'\1', text)


def picture_sheet() -> str:
    d = data()
    lens, reg = d['lens'], d['regular']
    return f"""# Advanced steps 07–18: the picture sheet

One page to keep beside the advanced steps 07–18. All energies are J/mol of atoms.

![The ten menu dots on the melting lens at 1400 K and the line through the two used dots](figures/menu_line.png)

**The menu and its line.** At $z={lens['z']:.2f}$ the cheapest mixture of the
menu uses LIQUID at 0.3 and SOLID at 0.5, at ${lens['s1']['G_up']:.2f}$. The line
through them lies under every dot: a floor for the menu. Its end heights are
$\\mu_A={lens['s2']['mu_A']:.1f}$ and $\\mu_B={lens['s2']['mu_B']:.1f}$.

![The gap curve against the menu's line: the curves dip below zero between the dots](figures/gap_curve.png)

**The gap curve.** Energy minus the line. Used dots sit at zero; the curves
dip below it between the dots, deepest at SOLID near {lens['s7']['dips']['SOLID']['x']:.4f}
(${lens['s7']['dips']['SOLID']['depth']:.1f}$).

![Floor and ceiling for the first rounds of column generation, with the true answer between them](figures/bounds.png)

**Ceiling and floor.** The ceiling is the best mixture found; the floor is the
line slid down by the deepest dip. The truth, ${lens['truth']['G']:.2f}$, lies
between them; their distance is the remaining uncertainty.

![Interval bars covering 0 to 1 under the regular solution's gap curve](figures/intervals.png)

**Branch-and-bound.** On the regular solution at 800 K every interval of
$[0,1]$ has a floor of at least $-{reg['s9']['eps']:.0f}$ against the final line:
no valley deeper than the tolerance is left. Floor ${reg['s9']['G_low']:.2f}$,
ceiling ${reg['s9']['G_up']:.2f}$.
"""


def card_deck() -> str:
    cards = json.loads(CARDS.read_text())
    deck = {'M': 'maths and optimisation', 'O': 'thermodynamics', 'both': 'both decks'}
    out = ['# Advanced steps 07–18: the card deck', '',
           'Short answers to “hang on, what was this?”. Cards marked “Core” are the ones most steps need. Cut along the rules.', '']
    for card in cards['cards']:
        out += ['---', '', f"### {'Core · ' if card['core'] else ''}{card['title']}", '',
                f"*{deck[card['deck']]} · needed for step{'s' if len(card['pages']) > 1 else ''} {', '.join(card['pages'])}*", '']
        for block in card['blocks']:
            if block['type'] == 'list':
                out += [f'- {plain(item)}' for item in block['items']] + ['']
            else:
                out += [plain(block['text']), '']
        out += [f"*{cards['closing']}*", '']
    return '\n'.join(out)


def game_kit() -> str:
    d = data()
    lens = d['lens']
    return f"""# Advanced steps 07–18: the column-generation game

For two players or two teams. The **master** holds the dots and draws a line;
the **pricer** holds the full curves and offers a state below the line, or
says “none”. Then swap roles. You need this sheet, a transparent ruler (the
“line”) and a pencil.

**Rules.**

1. The master marks the sample at $z={lens['z']:.2f}$, chooses the cheapest
   mixture of the dots on the master's sheet (lever rule), and lays the ruler
   through the two used dots. The master announces the line's heights at
   $x=0$ and $x=1$.
2. The pricer's sheet is zoomed to $x$ from 0.28 to 0.48. The pricer works
   out the line's height at both edges, $\\mu_A+\\Delta\\mu\\,x$ (with
   $\\Delta\\mu=\\mu_B-\\mu_A$), draws the line there with the ruler, and
   looks for any point of the curves below it. If there is one, the pricer
   names its composition and phase model; the master adds it as a new dot.
3. Repeat until the pricer says “none”. Write down the ceiling (the master's
   best mixture) after every round.
4. Debrief: how did you know when to stop? How far below the ruler was the
   deepest point the pricer found in the first round?

![The master's sheet: the ten menu dots on a grid](figures/dot_sheet.png)

![The pricer's sheet: the full SOLID and LIQUID curves on the same grid](figures/curve_sheet.png)

**For the debrief.** First round: the master's line has $\\mu_A={lens['s2']['mu_A']:.1f}$
and $\\mu_B={lens['s2']['mu_B']:.1f}$; the deepest point below it is SOLID near
{lens['s7']['dips']['SOLID']['x']:.2f}, ${lens['s7']['dips']['SOLID']['depth']:.1f}$
J/mol atoms. The true answer is ${lens['truth']['G']:.2f}$.
"""


SHEETS = {'picture_sheet.md': picture_sheet, 'card_deck.md': card_deck, 'game_kit.md': game_kit}


def main() -> None:
    figures()
    for name, make in SHEETS.items():
        (DAY3 / name).write_text(make(), encoding='utf-8')
        print('wrote', (DAY3 / name).relative_to(ROOT))


if __name__ == '__main__':
    main()
