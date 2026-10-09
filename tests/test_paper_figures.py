"""The D3 tangent figure and the two-phase recap sheet print the course models' numbers."""
import re
from pathlib import Path

import pytest

from course.foundations import binary_family as bf
from course.print import paper_figures as pf

ROOT = Path(__file__).resolve().parents[1]
DAY2 = ROOT / 'course' / 'primer_day2'


def text(name: str) -> str:
    return (DAY2 / name).read_text(encoding='utf-8')


def test_d3_figure_matches_the_supplied_values():
    n = pf.d3_numbers()
    worksheet = text('worksheet.md')
    assert n['mu_A'] == pytest.approx(-9876.020, abs=1e-3)
    assert n['mu_B'] == pytest.approx(-16144.844, abs=1e-3)
    assert n['slope'] == pytest.approx(-6268.824, abs=1e-3)
    assert (n['ref_A'], n['ref_B']) == (-9000.0, 3000.0)  # the dashed line -9000 + 12000x
    for value in ('-9876.020', '-16144.844', '-6268.824'):
        assert value in worksheet
    assert '![' in worksheet and '](figures/d3_tangent.png)' in worksheet


def test_every_sheet_and_worksheet_image_exists():
    for name in ('worksheet.md', 'two_phase_sheet.md'):
        for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text(name)):
            assert (DAY2 / target).is_file(), target
    assert set(pf.FIGURE_FILES) == {p.name for p in (DAY2 / 'figures').glob('*.png')}


def test_sheet_numbers_come_from_the_models():
    sheet = text('two_phase_sheet.md')
    split, lens, regular = pf.split_numbers(), pf.lens_numbers(), pf.regular_numbers()
    assert f"{split['x_ALPHA']:.3f}" == '0.191' and f"{split['x_BETA']:.3f}" == '0.809'
    assert f"{split['mu_A']:.1f}" == f"{split['mu_B']:.1f}" == '-10762.7'
    assert f"{split['f_BETA']:.3f}" == '0.176'
    alpha, beta = (float(bf.ideal_properties(1000, 0.30, p)['GM']) for p in ('ALPHA', 'BETA'))
    assert (f'{alpha:.1f}', f'{beta:.1f}') == ('-10479.0', '-5679.0')
    assert round(alpha - split['mu_A']) == 284
    assert (f"{lens['x_LIQUID']:.3f}", f"{lens['x_SOLID']:.3f}") == ('0.312', '0.441')
    assert f"{lens['f_SOLID']:.2f}" == '0.68'
    left, right = regular['binodal']
    assert (f'{left:.3f}', f'{right:.3f}') == ('0.070', '0.930')
    assert f'{(0.20 - left) / (right - left):.2f}' == '0.15'
    for value in ('0.191', '0.809', '−10762.7'.replace('−', '-'), '-10479.0', '-5679.0', '284',
                  '0.312', '0.441', '0.68', '0.070', '0.930', '0.15', '0.176'):
        assert value in sheet, value


def test_task01_routes_name_the_sheet():
    assert 'two_phase_sheet.md' in text('README.md')
    assert 'two_phase_sheet.md' in (ROOT / 'course' / 'materials' / 'cuni' / 'README.md').read_text(encoding='utf-8')


def test_day2_figures_print_the_worksheet_numbers():
    worksheet = text('worksheet.md')
    d1 = pf.d1_numbers()
    assert d1['z'] == pytest.approx(0.30) and d1['A'] == pytest.approx(0.70)          # the worked count
    d4 = pf.d4_numbers()
    assert (d4['bulk_sites'], d4['sites_per_boundary'], d4['boundaries'], d4['cell_sites']) == (8000, 100, 2, 8200)
    assert d4['area_per_boundary_nm2'] == pytest.approx(20)
    d5 = pf.d5_numbers()
    assert f"{d5['theta']:.8f}" == '0.16856026' and '0.16856026' in worksheet
    assert (round(d5['mu_A'], 3), round(d5['mu_B'], 3)) == (-9876.020, -16144.844)    # the D3 tangent
    assert d5['phi'] < 0                                                               # the slid line lies below the tangent
    d6 = pf.d6_numbers()
    assert (d6['start_bulk_B'], d6['start_boundary_B'], d6['total_B']) == (800, 50, 850) == (800, 50, d6['model_total_B'])
    assert f"{d6['theta']:.7f}" == '0.1716075' and f"{d6['x_bulk']:.8f}" == '0.10195981'
    assert '0.1716075' in worksheet and '0.10195981' in worksheet
    d7 = pf.d7_curve(points=7)
    rows = d7['rows']
    assert (f"{rows[0.10]['I']:.5f}", f"{rows[0.10]['II']:.5f}") == ('-10541.72679', '-10519.50695')
    assert (f"{rows[0.25]['I']:.5f}", f"{rows[0.25]['II']:.5f}") == ('-10713.32958', '-10718.80845')
    assert f"{d7['crossing']:.5f}" == '0.21619' and '0.21619' in worksheet
    assert rows[0.10]['D'] > 0 > rows[0.25]['D']


def test_day2_figures_follow_their_worked_examples():
    """No figure sits above the question whose answer it would show."""
    worksheet = text('worksheet.md')
    order = [worksheet.index(s) for s in ('figures/d6_ledger.png', 'figures/d7_crossing.png')]
    assert worksheet.index('2. With the supplied selected pair') < order[0]
    assert worksheet.index('3. A report omits') < order[1]
    for name in ('d1_counts', 'd4_cell', 'd5_parallel', 'd6_ledger', 'd7_crossing'):
        assert f'](figures/{name}.png)' in worksheet, name
