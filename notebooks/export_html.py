"""Executed HTML copies of the invented-model notebooks, for instructors.

They are the offline / projector fallback for the primer demonstrations and
show every result, including the "after your attempt" cells: instructor
material, not for learners before their attempt. Only notebooks without a
published database are exported (f0–f8), so no database text can appear.

Run from the repository root:
    .venv/bin/python notebooks/export_html.py
"""
from __future__ import annotations

from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / 'notebooks'
OUTPUT = NOTEBOOKS / 'instructor_exports'
NAMES = ['f0_jupyter_and_potentials', 'f1_unary_by_hand_and_code', 'f2_unary_pycalphad',
         'f3_binary_mixing_potentials', 'f4_two_phases_and_diagrams', 'f5_binary_pycalphad',
         'f6_fitting_synthetic', 'f7_boundary_open_closed', 'f8_boundary_states']
NOTE = ('<div style="border:2px solid #b45309;padding:.6em 1em;margin:1em 0;font-family:sans-serif">'
        '<strong>Instructor copy.</strong> Executed notebook with all results shown, including the '
        '"after your attempt" cells. Projector/offline fallback; learners should use the notebook itself.</div>')


def export(name: str) -> Path:
    notebook = nbformat.read(NOTEBOOKS / f'{name}.ipynb', as_version=4)
    ExecutePreprocessor(timeout=600, kernel_name='python3').preprocess(notebook, {'metadata': {'path': str(NOTEBOOKS)}})
    for cell in notebook.cells:  # Colab-only form hiding does not apply in HTML; show everything
        cell.metadata.pop('cellView', None)
    body, _ = HTMLExporter(template_name='classic').from_notebook_node(notebook)
    body = body.replace('<body>', '<body>' + NOTE, 1)
    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / f'{name}.html'
    path.write_text(body, encoding='utf-8')
    return path


if __name__ == '__main__':
    for name in NAMES:
        path = export(name)
        print(f'wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} kB)')
