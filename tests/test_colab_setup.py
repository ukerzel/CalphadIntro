"""Rehearse the Colab route of every notebook without a network.

In Colab the setup cell clones the course at RELEASE from GitHub, installs the
locked packages, restarts the session, and on the second run imports the course
code. Here a local git repository built from this copy of the course stands in
for GitHub (git's url.<base>.insteadOf), a stand-in google.colab module makes the
cell take its Colab branch, and a stand-in pip records the install instead of
downloading. Colab's own Python and package downloads are not covered: the lock
file check in test_notebooks.py covers the package list.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from notebooks import helpers  # noqa: E402

TOOLS = {'helpers.py', 'export_requirements.py', 'run_companion.py', 'export_html.py'}
NOTEBOOKS = sorted(p.stem for p in (ROOT / 'notebooks').glob('*.py') if p.name not in TOOLS)
RELEASE = next(line.split('"')[1] for line in helpers.SETUP_CELL.splitlines() if line.startswith('RELEASE = '))
PUBLIC = 'https://github.com/ukerzel/CalphadIntro.git'
SKIP = shutil.ignore_patterns('__pycache__', '*.pyc', 'instructor_exports')
CLONED = ['notebooks', 'course', 'pyproject.toml']                     # what the notebooks use from a clone


def run(command, **kw):
    return subprocess.run(command, capture_output=True, text=True, **kw)


@pytest.fixture(scope='module')
def colab(tmp_path_factory):
    """A fake GitHub repository at RELEASE, a fake /content, google.colab and pip stand-ins, and the first (installing) run."""
    base = tmp_path_factory.mktemp('colab')
    origin = base / 'origin'
    for item in CLONED:
        source = ROOT / item
        if source.is_dir():
            shutil.copytree(source, origin / item, ignore=SKIP)
        else:
            origin.mkdir(exist_ok=True)
            shutil.copy2(source, origin / item)
    who = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
    for command in (['git', 'init', '-q', '-b', 'trunk'], ['git', 'add', '-A'], ['git', 'commit', '-q', '-m', 'release']):
        assert run(command, cwd=origin, env=who).returncode == 0
    ref = ['git', 'branch', RELEASE] if RELEASE == 'main' else ['git', 'tag', RELEASE]
    assert run(ref, cwd=origin, env=who).returncode == 0

    stubs = base / 'stubs'
    (stubs / 'google' / 'colab').mkdir(parents=True)
    (stubs / 'google' / '__init__.py').write_text('')
    (stubs / 'google' / 'colab' / '__init__.py').write_text('class files:\n    @staticmethod\n    def upload():\n        return {}\n')
    (stubs / 'pip').mkdir()
    (stubs / 'pip' / '__init__.py').write_text('')
    (stubs / 'pip' / '__main__.py').write_text(
        'import os, sys\n'
        'args = sys.argv[1:]\n'
        'assert args[:3] == ["install", "-q", "-r"], args\n'
        'lines = open(args[3]).read().splitlines()\n'
        'assert any(line.startswith("pycalphad==") for line in lines), "no pycalphad pin"\n'
        'open(os.environ["PIP_LOG"], "a").write(" ".join(args) + "\\n")\n')
    content = base / 'content'
    content.mkdir()
    env = dict(os.environ, PYTHONPATH=str(stubs), MPLBACKEND='Agg', MPLCONFIGDIR=str(base / 'mpl'), HOME=str(base / 'home'),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PIP_LOG=str(base / 'pip.log'),
               GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0=f'url.{origin.as_uri()}.insteadOf', GIT_CONFIG_VALUE_0=PUBLIC)
    for name in ('CALPHAD_CUNI_TDB', 'CALPHAD_NINB_TDB', 'CALPHAD_INPUT_DIR'):
        env.pop(name, None)

    def notebook(name: str):
        # Colab's /content is not writable here: point the cell's and helpers' /content at the stand-in folder.
        source = (ROOT / 'notebooks' / f'{name}.py').read_text().replace('/content/', f'{content}/')
        script = base / f'{name}.py'
        script.write_text('import google.colab\n' + source)
        return run([sys.executable, str(script)], cwd=content, env=env, timeout=600)

    first = notebook('setup_check')
    yield {'notebook': notebook, 'first': first, 'content': content, 'pip_log': base / 'pip.log'}


def test_first_run_clones_installs_and_restarts(colab):
    first, clone = colab['first'], colab['content'] / 'CalphadIntro'
    assert first.returncode == -9, first.stdout + first.stderr       # the cell ends the session on purpose
    assert 'Colab now restarts this session' in first.stdout
    assert (clone / '.colab-ready').is_file() and (clone / 'notebooks' / 'helpers.py').is_file()
    assert colab['pip_log'].read_text().count('requirements-colab.txt') == 1


@pytest.mark.parametrize('name', NOTEBOOKS)
def test_second_run_works_in_colab(colab, name):
    clone = colab['content'] / 'CalphadIntro'
    helpers_path = clone / 'notebooks' / 'helpers.py'
    text = helpers_path.read_text()
    if '/content/' in text:                                             # databases folder, as in the notebook above
        helpers_path.write_text(text.replace('/content/', f"{colab['content']}/"))
    result = colab['notebook'](name)
    assert result.returncode == 0, f'{name} failed in the Colab rehearsal:\n{result.stdout[-2000:]}\n{result.stderr[-3000:]}'
    assert f'Course release {RELEASE}' in result.stdout
    assert colab['pip_log'].read_text().count('requirements-colab.txt') == 1   # no second install
