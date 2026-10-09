"""Print-ready PDFs of the primer worksheets, answer sheets and reference cards.

Converts the course Markdown to LaTeX (mistune parser, a small renderer here)
and typesets it with XeLaTeX (DejaVu fonts, unicode-math). The Markdown files
stay the source; rebuild the PDFs after changing them. A person must still
check a real printout (glyphs, tables, small units), as the run sheets ask.

Run from the repository root:
    .venv/bin/python course/print/build_print.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
DOCUMENTS = [  # (source, output name, title, part: 'all' or 'reference')
    ('course/primer/worksheet.md', 'day1_worksheet', 'Day 1 primer — learner worksheet', 'all'),
    ('course/primer/answers.md', 'day1_answers', 'Day 1 primer — answers and staged hints', 'all'),
    ('course/primer/worksheet.md', 'day1_reference_card', 'Day 1 primer — reference card', 'reference'),
    ('course/primer_day2/worksheet.md', 'day2_worksheet', 'Day 2 primer — learner worksheet', 'all'),
    ('course/primer_day2/answers.md', 'day2_answers', 'Day 2 primer — answers and staged hints', 'all'),
    ('course/primer_day2/worksheet.md', 'day2_reference_card', 'Day 2 primer — reference card', 'reference'),
    ('course/primer_day2/two_phase_sheet.md', 'two_phase_sheet', 'Two phases: a recap sheet', 'all'),
    ('course/day3/lp_primer_sheet.md', 'lp_primer_sheet', 'Linear programmes — a primer sheet', 'all'),
    ('course/day3/picture_sheet.md', 'day3_picture_sheet', 'Advanced steps 07–18 — picture sheet', 'all'),
    ('course/day3/card_deck.md', 'day3_card_deck', 'Advanced steps 07–18 — card deck', 'all'),
    ('course/day3/game_kit.md', 'day3_game_kit', 'Advanced steps 07–18 — column-generation game', 'all'),
]
SPECIALS = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '$': r'\$', '&': r'\&', '#': r'\#',
            '^': r'\textasciicircum{}', '_': r'\_', '%': r'\%', '~': r'\textasciitilde{}'}


def escape(text: str) -> str:
    return ''.join(SPECIALS.get(ch, ch) for ch in text)


class Latex:
    """Render mistune's AST (renderer='ast') to LaTeX."""

    def __init__(self, base: Path = ROOT) -> None:
        self.base = base  # folder of the Markdown source, for relative image paths

    def inline(self, nodes: list[dict]) -> str:
        return ''.join(self.node(n) for n in nodes)

    def node(self, n: dict) -> str:
        kind = n['type']
        children = n.get('children') or []
        if kind == 'text':
            return escape(n['raw'])
        if kind == 'emphasis':
            return r'\emph{' + self.inline(children) + '}'
        if kind == 'strong':
            return r'\textbf{' + self.inline(children) + '}'
        if kind == 'codespan':
            return r'\texttt{' + escape(n['raw']) + '}'
        if kind in ('linebreak', 'softbreak'):
            return r'\\' + '\n' if kind == 'linebreak' else ' '
        if kind == 'inline_math':
            return '$' + n['raw'] + '$'
        if kind == 'link':
            label = self.inline(children)
            url = n['attrs']['url']
            if url.startswith('http'):
                return label + r'\footnote{\url{' + url.replace('%', r'\%').replace('#', r'\#') + '}}'
            return label  # repository-relative links: the printed text stands alone
        if kind == 'image':
            path = (self.base / n['attrs']['url']).resolve()
            if not n['attrs']['url'].startswith('http') and path.suffix == '.png' and path.is_file():
                return r'\begin{center}\includegraphics[width=0.6\linewidth]{' + path.as_posix() + r'}\end{center}'
            return '[figure: ' + self.inline(children) + ']'
        if kind in ('inline_html', 'block_html'):
            return ''
        if kind == 'strikethrough':
            return r'\sout{' + self.inline(children) + '}'
        if kind == 'paragraph':
            return self.inline(children) + '\n\n'
        if kind == 'heading':
            level = n['attrs']['level']
            command = {1: 'section*', 2: 'subsection*', 3: 'subsubsection*'}.get(level, 'paragraph*')
            return '\\' + command + '{' + self.inline(children) + '}\n\n'
        if kind == 'list':
            env = 'enumerate' if n['attrs'].get('ordered') else 'itemize'
            return f'\\begin{{{env}}}\n' + ''.join(self.node(c) for c in children) + f'\\end{{{env}}}\n\n'
        if kind == 'list_item':
            return r'\item ' + ''.join(self.node(c) for c in children).strip() + '\n'
        if kind == 'block_text':
            return self.inline(children) + '\n'
        if kind == 'block_code':
            return '\\begin{verbatim}\n' + n['raw'].rstrip('\n') + '\n\\end{verbatim}\n\n'
        if kind == 'block_quote':
            return '\\begin{quote}\n' + ''.join(self.node(c) for c in children) + '\\end{quote}\n\n'
        if kind == 'block_math':
            return '\\[\n' + n['raw'].strip() + '\n\\]\n\n'
        if kind == 'thematic_break':
            return '\\medskip\\hrule\\medskip\n\n'
        if kind == 'blank_line':
            return ''
        if kind == 'table':
            return self.table(n)
        raise ValueError(f'unsupported Markdown element: {kind}')

    def table(self, n: dict) -> str:
        head = next(c for c in n['children'] if c['type'] == 'table_head')
        body = next((c for c in n['children'] if c['type'] == 'table_body'), {'children': []})
        columns = len(head['children'])
        spec = '|' + '|'.join(['X'] * columns) + '|'
        row = lambda cells: ' & '.join(self.inline(c.get('children') or []) for c in cells) + r' \\ \hline'
        lines = [r'\begin{xltabular}{\linewidth}{' + spec + '}', r'\hline',
                 r'\rowcolor{black!8}' + row(head['children']), r'\endhead']
        lines += [row(r['children']) for r in body['children']]
        lines.append(r'\end{xltabular}')
        return '\n'.join(lines) + '\n\n'


PREAMBLE = r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=18mm]{geometry}
\usepackage{fontspec}
\usepackage{unicode-math}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}[Scale=0.85]
\setmathfont{DejaVu Math TeX Gyre}
\usepackage{xltabular,colortbl,xcolor,amsmath,graphicx}
\usepackage[normalem]{ulem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\renewcommand{\tabularxcolumn}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\footnotesize TITLE}\fancyfoot[R]{\footnotesize \thepage}
\sloppy\emergencystretch=3em
\begin{document}
'''


def reference_part(markdown: str) -> str:
    """The worksheet's reference-sheet section (from its heading to the end)."""
    match = re.search(r'^##\s+[^\n]*[Rr]eference[^\n]*$', markdown, re.M)
    if not match:
        raise ValueError('no reference section found')
    return markdown[match.start():]


def build(source: str, name: str, title: str, part: str, workdir: Path) -> Path:
    markdown = (ROOT / source).read_text(encoding='utf-8')
    if part == 'reference':
        markdown = reference_part(markdown)
    tokens = mistune.create_markdown(renderer='ast', plugins=['table', 'math', 'strikethrough'])(markdown)
    body = ''.join(Latex((ROOT / source).parent).node(t) for t in tokens)
    tex = PREAMBLE.replace('TITLE', escape(title) + r' \textperiodcentered{} CALPHAD School 2026') + body + '\\end{document}\n'
    (workdir / f'{name}.tex').write_text(tex, encoding='utf-8')
    for _ in range(2):  # xltabular needs two passes for column widths
        run = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', f'{name}.tex'],
                             cwd=workdir, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(f'xelatex failed for {name}:\n' + run.stdout[-2500:])
    target = OUTPUT / f'{name}.pdf'
    shutil.copyfile(workdir / f'{name}.pdf', target)
    return target


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp:
        for document in DOCUMENTS:
            path = build(*document, Path(tmp))
            print(f'wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} kB)')
