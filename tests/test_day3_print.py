"""The printable sheets of the advanced steps are generated from the exported data and the cards, never edited by hand."""
from pathlib import Path

from course.print import build_print, day3_sheets

ROOT = Path(__file__).resolve().parents[1]


def test_sheets_match_a_fresh_generation():
    for name, make in day3_sheets.SHEETS.items():
        assert (day3_sheets.DAY3 / name).read_text(encoding='utf-8') == make(), f'{name} is stale: rerun course.print.day3_sheets'


def test_every_sheet_figure_exists_and_is_printed():
    for name in day3_sheets.FIGS:
        assert (day3_sheets.FIGURES / f'{name}.png').is_file(), name
    printed = {doc[0] for doc in build_print.DOCUMENTS}
    for name in day3_sheets.SHEETS:
        assert f'course/day3/{name}' in printed, name
        assert (ROOT / 'course' / 'print' / f"day3_{name.removesuffix('.md')}.pdf").is_file(), name


def test_card_deck_holds_every_card_once():
    import json
    cards = json.loads((ROOT / 'course' / 'self_study' / 'cards.json').read_text())['cards']
    deck = (day3_sheets.DAY3 / 'card_deck.md').read_text(encoding='utf-8')
    for card in cards:
        assert deck.count(card['title']) == 1, card['id']
    assert '[[' not in deck and ']]' not in deck
