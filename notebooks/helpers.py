"""Small helpers shared by the course notebooks (notebooks/*.ipynb).

Every notebook starts with SETUP_CELL (copied verbatim; a test checks this),
then imports from here:

- show_versions(release): print Python and package versions next to the
  locked ones and say plainly if Colab needs a restart.
- check(answer, key): for "your turn" cells. Says whether an answer matches
  without printing the expected value; skips answers left as None.
- confirm(value, expected, what, tol): for "after your attempt" cells that
  reproduce a lesson value with the course code; stops with a clear message
  if the value does not reproduce.
- database(name): find, download or upload a published database into a folder
  outside the course checkout, checking its size and SHA-256. Returns None
  (no-database mode) if no checked copy is available.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import urllib.request
import zipfile
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / 'notebooks' / 'requirements-colab.txt'
KEYS = ROOT / 'notebooks' / 'checks'  # one JSON file of stored values per notebook
IN_COLAB = 'google.colab' in sys.modules

SETUP_CELL = '''\
# Setup: run this cell first. Locally it finds the course folder; in Colab it
# downloads the tested course release and the locked package versions.
# In Colab, the first run then restarts the session on purpose and Colab reports
# a crash: that is expected. Run this cell again, then the rest of the notebook.
RELEASE = "v0.1.1"
import os, pathlib, subprocess, sys, time
ROOT = next((p for p in (pathlib.Path.cwd(), *pathlib.Path.cwd().parents)
             if (p / "pyproject.toml").is_file() and (p / "course").is_dir()), None)
if ROOT is None and "google.colab" in sys.modules:
    ROOT = pathlib.Path("/content/CalphadIntro")
    if not ROOT.is_dir():
        clone = ["git", "clone", "-q", "--depth", "1", "--branch", RELEASE,
                 "https://github.com/ukerzel/CalphadIntro.git", str(ROOT)]
        git = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        if subprocess.run(clone, env=git, capture_output=True).returncode:
            raise SystemExit(f"Could not download course release {RELEASE}: check the internet "
                             "connection and run this cell again.")
    if not (ROOT / ".colab-ready").exists():
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r",
                           str(ROOT / "notebooks" / "requirements-colab.txt")]).returncode:
            raise SystemExit("Installing the course packages failed; run this cell again.")
        (ROOT / ".colab-ready").touch()
        # Colab has already loaded its own numpy; a fresh session is needed to use the installed versions.
        print("Installed the course's package versions. Colab now restarts this session and"
              " reports a crash; that is expected. When it has reconnected, run this cell again"
              " (it will not install twice), then the rest of the notebook.", flush=True)
        time.sleep(3)
        os.kill(os.getpid(), 9)
if ROOT is None:
    raise SystemExit("Open this notebook from the course folder (poetry run jupyter lab) or in Colab.")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from notebooks.helpers import check, confirm, database, show_versions
show_versions(RELEASE)'''


def locked_versions() -> dict[str, str]:
    lines = [line.split('==') for line in REQUIREMENTS.read_text().splitlines() if '==' in line]
    return {name: version for name, version in lines}


def show_versions(release: str, packages: tuple[str, ...] = ('numpy', 'scipy', 'matplotlib', 'xarray', 'pycalphad')) -> bool:
    """Print versions; True when everything matches the locked run."""
    locked, same = locked_versions(), True
    print(f'Course release {release} · Python {platform.python_version()}'
          f'{"" if platform.python_version().startswith("3.12.") else " (the locked run used 3.12)"}')
    for name in packages:
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = 'not installed'
        loaded = sys.modules.get(name)
        running = getattr(loaded, '__version__', installed) if loaded else installed
        note = '' if running == locked.get(name) else f'  ← locked run used {locked.get(name)}'
        same &= not note
        print(f'  {name:<11} {running}{note}')
    if not same and IN_COLAB:
        print('Colab still has its own versions loaded: choose Runtime → Restart session, then run this cell again.')
    elif not same:
        print('Some versions differ from the locked run; results may differ in the last digits.')
    return same


def _key() -> dict:
    merged: dict = {}
    for path in sorted(KEYS.glob('*.json')):
        merged.update(json.loads(path.read_text()))
    return merged


RELATIVE = 5e-4  # numbers: an answer to about four significant figures is accepted


def _matches(answer, expected, tol: float, strict: bool = False) -> tuple[bool, bool]:
    """(matches, close) for one stored value."""
    is_bool = type(answer).__name__ in ('bool', 'bool_')  # also numpy booleans
    if isinstance(expected, bool):
        return is_bool and bool(answer) == expected, False
    if isinstance(expected, (int, float)):
        if is_bool:
            return False, False
        difference = abs(float(answer) - float(expected))
        allowed = tol if strict else max(tol, RELATIVE * abs(expected))  # strict: the stored tolerance only
        return difference <= allowed, difference <= 0.02 * abs(expected)
    return str(answer).strip().casefold() == str(expected).strip().casefold(), False


def check(answer, key: str) -> bool | None:
    """Compare a learner's answer with the stored value without showing it.

    Numbers match within the stored tolerance or about four significant figures
    (only the stored tolerance for entries marked strict, where a small difference
    is the mistake being tested);
    words ignore case (a stored list accepts any of its words); yes/no answers
    need True or False.
    """
    entry = _key().get(key)
    if entry is None:
        raise KeyError(f'no stored value named {key!r}')
    if answer is None:
        print(f'{key}: not attempted yet. Replace None with your value and run the cell again.')
        return None
    stored = entry['value'] if isinstance(entry['value'], list) else [entry['value']]
    try:
        results = [_matches(answer, value, entry.get('tol', 0), entry.get('strict', False)) for value in stored]
    except (TypeError, ValueError):
        results = [(False, False)]
    if any(ok for ok, _ in results):
        print(f'{key}: ✓ matches.')
        return True
    if entry.get('near_miss', True) and any(close for _, close in results):  # off where two answers lie close together
        print(f'{key}: close (within 2 %) but not a match. Check the method first, then the rounding. {entry.get("hint", "")}'.rstrip())
    else:
        print(f'{key}: not yet. {entry.get("hint", "Check the units and the amount basis.")}')
    return False


def confirm(value: float, expected: float, what: str, tol: float) -> None:
    """A reference calculation must reproduce the lesson value; stop if it does not."""
    if abs(value - expected) > tol:
        raise AssertionError(f'{what}: got {value!r}, the lesson has {expected!r} (tolerance {tol}). '
                             'Check the package versions printed by the setup cell before anything else.')
    print(f'✓ {what} reproduces the lesson value.')


SOURCES = {
    'cuni': {
        'file': 'CuNi-92Mey-LB.tdb', 'bytes': 6789,
        'sha256': '7e52adda858e302168ae26b5abfe17f4726ccbfaaff0880abcad5b38e3f559e1',
        'url': 'https://phasediagrams.org/uploads/CuNi-92Mey-LB.tdb', 'member': None,
        'cite': 'S. an Mey, Calphad 16 (1992) 255–260, doi:10.1016/0364-5916(92)90022-P; '
                'B. Hallstedt, Calphad 89 (2025) 102833, doi:10.1016/j.calphad.2025.102833',
        'env': 'CALPHAD_CUNI_TDB',
    },
    'ninb': {
        'file': 'calpha_102563_Nb-Ni_new_mmc1.tdb', 'bytes': 13087,
        'sha256': 'ceb0c4667a031900aab8c15867b0186ed88ba822f37a0f9390328c55457b8c0a',
        'url': 'https://ars.els-cdn.com/content/image/1-s2.0-S0364591623000354-mmc1.zip',
        'member': 'calpha_102563_Nb-Ni_new_mmc1.tdb',
        'cite': 'H. Sun et al., Calphad 82 (2023) 102563, doi:10.1016/j.calphad.2023.102563',
        'env': 'CALPHAD_NINB_TDB',
    },
}


def database_folder() -> Path:
    """Where downloaded databases are kept: outside the course checkout."""
    folder = Path('/content/databases') if IN_COLAB else Path.home() / '.cache' / 'calphad-course'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _verified(path: Path, source: dict) -> bool:
    data = path.read_bytes()
    return len(data) == source['bytes'] and hashlib.sha256(data).hexdigest() == source['sha256']


def database(name: str, download: bool = False) -> Path | None:
    """Return a checked copy of a published database, or None for no-database mode.

    Looks at the file named by CALPHAD_CUNI_TDB / CALPHAD_NINB_TDB, then in
    $CALPHAD_INPUT_DIR and ~/calphad-inputs (the setup guide's folder), then in
    the download folder;
    with download=True it fetches the file (and, in Colab, offers an upload if
    the download fails). The file is never placed inside the course checkout.
    """
    source = SOURCES[name]
    candidates = [Path(os.environ[source['env']])] if os.environ.get(source['env']) else []
    if os.environ.get('CALPHAD_INPUT_DIR'):  # the folder the setup guide uses
        candidates.append(Path(os.environ['CALPHAD_INPUT_DIR']) / source['file'])
    candidates.append(Path.home() / 'calphad-inputs' / source['file'])  # the setup guide's default
    if not os.environ.get('CALPHAD_IGNORE_REPO_INPUTS'):  # tests set this to check the no-database mode
        candidates.append(ROOT / 'inputs' / 'databases' / source['file'])  # a local inputs/ folder, if present
    candidates.append(database_folder() / source['file'])
    for path in candidates:
        if path.is_file():
            if _verified(path, source):
                print(f'Using {path} (size and SHA-256 match). Cite: {source["cite"]}.')
                return path
            print(f'{path} is not the expected file (size or SHA-256 differ); it was not used.')
    if not download:
        print(f'No checked copy of {source["file"]} found. Set DOWNLOAD = True in this cell and run it again to fetch it, '
              f'or continue in no-database mode with the saved results.')
        return None
    target = database_folder() / source['file']
    problem = ''
    try:
        with urllib.request.urlopen(urllib.request.Request(source['url'], headers={'User-Agent': 'calphad-course-notebook (python-urllib)'}), timeout=60) as response:
            data = response.read()
        if source['member']:
            from io import BytesIO
            with zipfile.ZipFile(BytesIO(data)) as archive:
                data = archive.read(source['member'])
        target.write_bytes(data)
        if not _verified(target, source):
            target.unlink()
            problem = 'the downloaded file is not the published one (size or SHA-256 differ)'
    except Exception as error:  # network refused, blocked, or a web page instead of the file
        problem = f'the download did not work ({error.__class__.__name__})'
    if problem:
        print(f'{problem.capitalize()}. Download it in your browser from\n  {source["url"]}\n'
              + (f'and take {source["member"]} out of the ZIP, ' if source['member'] else '')
              + ('then upload it below.' if IN_COLAB else f'then save it as {target} and run this cell again.'))
        if not IN_COLAB:
            return None
        from google.colab import files  # type: ignore[import-not-found]
        uploaded = files.upload()
        if not uploaded:
            return None
        name, data = next(iter(uploaded.items()))
        Path(name).unlink(missing_ok=True)  # the upload also lands in the working folder: keep it out of the checkout
        target.write_bytes(data)
        if not _verified(target, source):
            target.unlink()
            print(f'The uploaded file is not {source["file"]} as published (size or SHA-256 differ), so it was removed. '
                  'Check that you took the right file; continue in no-database mode meanwhile.')
            return None
    print(f'Saved and checked {target}. Cite: {source["cite"]}.')
    return target
