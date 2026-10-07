"""Checks for the course notebooks (notebooks/*.py paired with notebooks/*.ipynb).

- every notebook's .py and .ipynb hold the same cells, and the .ipynb has no outputs
- every notebook starts with the canonical setup cell from notebooks/helpers.py
- every notebook runs top to bottom as plain Python from inside notebooks/
- requirements-colab.txt matches a fresh export from poetry.lock
- check() never prints the stored value; database() rejects a wrong file
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import jupytext
import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / 'notebooks'
sys.path.insert(0, str(ROOT))
from notebooks import export_requirements, helpers  # noqa: E402

TOOLS = {'helpers.py', 'export_requirements.py', 'run_companion.py', 'export_html.py'}
SOURCES = sorted(p for p in NOTEBOOKS.glob('*.py') if p.name not in TOOLS)


def cells(notebook):
    return [(c.cell_type, c.source.strip()) for c in notebook.cells]


def test_there_are_notebooks():
    assert any(p.stem == 'setup_check' for p in SOURCES)


@pytest.mark.parametrize('source', SOURCES, ids=lambda p: p.stem)
def test_pair_in_sync_without_outputs(source):
    paired = source.with_suffix('.ipynb')
    assert paired.is_file(), f'{paired.name} missing: run jupytext --sync {source.relative_to(ROOT)}'
    assert cells(jupytext.read(source)) == cells(jupytext.read(paired)), f'{source.name} and {paired.name} differ'
    raw = json.loads(paired.read_text())
    for cell in raw['cells']:
        if cell['cell_type'] == 'code':
            assert cell['outputs'] == [] and cell['execution_count'] is None, f'{paired.name} stores outputs'
    assert raw['metadata'].get('kernelspec', {}).get('name') == 'python3'


@pytest.mark.parametrize('source', SOURCES, ids=lambda p: p.stem)
def test_starts_with_the_setup_cell(source):
    code = [c.source for c in jupytext.read(source).cells if c.cell_type == 'code']
    assert code and code[0].strip() == helpers.SETUP_CELL.strip()


@pytest.mark.parametrize('source', SOURCES, ids=lambda p: p.stem)
def test_runs_top_to_bottom(source, tmp_path):
    env = dict(os.environ, MPLBACKEND='Agg', MPLCONFIGDIR=str(tmp_path), HOME=str(tmp_path),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CALPHAD_IGNORE_REPO_INPUTS='1')
    for name in ('CALPHAD_CUNI_TDB', 'CALPHAD_NINB_TDB', 'CALPHAD_INPUT_DIR'):
        env.pop(name, None)
    run = subprocess.run([sys.executable, source.name], cwd=NOTEBOOKS, env=env,
                         capture_output=True, text=True, timeout=600)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]


TASKS = [p for p in SOURCES if p.stem.startswith('task')]


@pytest.mark.parametrize('source', TASKS, ids=lambda p: p.stem)
def test_task_notebooks_run_with_the_stored_databases(source, tmp_path):
    if not (ROOT / 'inputs' / 'databases').is_dir():
        pytest.skip('no stored databases (public release)')
    env = dict(os.environ, MPLBACKEND='Agg', MPLCONFIGDIR=str(tmp_path), HOME=str(tmp_path),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    env.pop('CALPHAD_IGNORE_REPO_INPUTS', None)
    run = subprocess.run([sys.executable, source.name], cwd=NOTEBOOKS, env=env,
                         capture_output=True, text=True, timeout=900)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    assert 'size and SHA-256 match' in run.stdout or source.stem in ('task03_ni_twin',), run.stdout[-1500:]


def test_stored_check_values_are_unique_and_complete():
    seen = {}
    for path in sorted((NOTEBOOKS / 'checks').glob('*.json')):
        for key, entry in json.loads(path.read_text()).items():
            assert key not in seen, f'{key} in both {seen.get(key)} and {path.name}'
            assert 'value' in entry and 'hint' in entry, f'{path.name}:{key} needs value and hint'
            seen[key] = path.name
    used = {m for p in SOURCES for m in __import__('re').findall(r"check\([^,]+, \"([A-Za-z0-9_]+)\"\)", p.read_text())}
    assert used <= set(seen), f'check() keys without stored values: {sorted(used - set(seen))}'


def test_colab_requirements_match_the_lock():
    assert (NOTEBOOKS / 'requirements-colab.txt').read_text() == export_requirements.render()
    locked = helpers.locked_versions()
    assert locked['pycalphad'] == '0.11.2' and locked['numpy'] == '2.5.3' and locked['scipy'] == '1.18.1'


def test_check_does_not_reveal_the_value(tmp_path, monkeypatch, capsys):
    (tmp_path / 'demo.json').write_text(json.dumps({'g_solid_900': {'value': -8000.0, 'tol': 0.5, 'hint': 'Use kelvin.'}}))
    monkeypatch.setattr(helpers, 'KEYS', tmp_path)
    assert helpers.check(None, 'g_solid_900') is None
    assert helpers.check(-7999.8, 'g_solid_900') is True
    assert helpers.check(-8.0, 'g_solid_900') is False
    out = capsys.readouterr().out
    assert 'not attempted' in out and '✓ matches' in out and 'Use kelvin.' in out and '8000' not in out
    assert helpers.check(-7998.0, 'g_solid_900') is True    # about four significant figures
    assert helpers.check(-7900.0, 'g_solid_900') is False   # close, but not enough digits
    assert 'close' in capsys.readouterr().out
    (tmp_path / 'near.json').write_text(json.dumps({'paired': {'value': 0.8206, 'hint': 'Which cell?', 'near_miss': False}}))
    assert helpers.check(0.8224, 'paired') is False and 'Which cell?' in capsys.readouterr().out
    (tmp_path / 'more.json').write_text(json.dumps({'word': {'value': 'together', 'hint': 'h'}, 'yesno': {'value': False, 'hint': 'h'}}))
    assert helpers.check(' Together ', 'word') is True and helpers.check('apart', 'word') is False
    assert helpers.check(False, 'yesno') is True and helpers.check(0, 'yesno') is False
    import numpy as np
    assert helpers.check(np.bool_(False), 'yesno') is True
    (tmp_path / 'words.json').write_text(json.dumps({'either': {'value': ['together', 'closer'], 'hint': 'h'}}))
    assert helpers.check('Closer', 'either') is True
    with pytest.raises(AssertionError):
        helpers.confirm(1.0, 2.0, 'value', tol=0.1)


def test_strict_keys_reject_the_mistake_they_target(capsys):
    key = {k: v for path in (NOTEBOOKS / 'checks').glob('*.json') for k, v in json.loads(path.read_text()).items()}
    assert helpers.check(key['f4_mu_a_best']['value'], 'f4_mu_a_best') is True
    assert helpers.check(key['f4_g_split_half']['value'], 'f4_mu_a_best') is False    # split energy is not μ_A
    assert helpers.check(key['f4_mu_a_best']['value'], 'f4_g_split_half') is False
    cu = key['task01_liquid_cu_1500']['value']
    assert helpers.check(cu - 3.7, 'task01_liquid_cu_1500') is False                # neighbouring range of the expression
    assert helpers.check(round(cu, 2), 'task01_liquid_cu_1500') is True


def test_setup_cell_clones_the_public_release_without_credentials():
    cell = helpers.SETUP_CELL
    assert all(word not in cell for word in ('getpass', 'token', 'Authorization', '@github.com', 'check=True'))
    assert '--branch", RELEASE' in cell and 'GIT_TERMINAL_PROMPT="0"' in cell


def test_database_rejects_a_wrong_file(tmp_path, monkeypatch, capsys):
    wrong = tmp_path / 'CuNi-92Mey-LB.tdb'
    wrong.write_text('not the database')
    monkeypatch.setenv('CALPHAD_CUNI_TDB', str(wrong))
    monkeypatch.setattr(helpers, 'database_folder', lambda: tmp_path / 'empty')
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.delenv('CALPHAD_INPUT_DIR', raising=False)
    monkeypatch.setattr(helpers, 'ROOT', tmp_path)  # no inputs/ folder here
    (tmp_path / 'empty').mkdir()
    assert helpers.database('cuni') is None
    assert 'not the expected file' in capsys.readouterr().out


def test_instructor_exports_exist_for_the_invented_model_notebooks():
    from notebooks import export_html
    for name in export_html.NAMES:
        html = (NOTEBOOKS / 'instructor_exports' / f'{name}.html').read_text()
        assert 'Instructor copy.' in html and '/home/' not in html, name


def test_database_found_in_the_setup_guide_folder(tmp_path, monkeypatch):
    import hashlib
    data = b'stand-in database text'
    fake = dict(helpers.SOURCES['cuni'], bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    monkeypatch.setitem(helpers.SOURCES, 'cuni', fake)
    folder = tmp_path / 'inputs'
    folder.mkdir()
    (folder / fake['file']).write_bytes(data)
    monkeypatch.delenv('CALPHAD_CUNI_TDB', raising=False)
    monkeypatch.setenv('CALPHAD_INPUT_DIR', str(folder))
    monkeypatch.setattr(helpers, 'database_folder', lambda: tmp_path / 'empty')
    assert helpers.database('cuni') == folder / fake['file']
