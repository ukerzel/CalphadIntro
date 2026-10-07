"""Checks for the step 06 mu-phase structure sketch export."""
import json
import math
from pathlib import Path

import pytest

from course.self_study import mu_structure as mu

GENERATED = Path(__file__).resolve().parents[1] / 'course/self_study/generated/mu_structure.json'


@pytest.fixture(scope='module')
def data():
    return mu.build()


def test_committed_file_matches_a_fresh_build(data):
    assert json.loads(GENERATED.read_text()) == json.loads(json.dumps(data))


def test_cell_holds_three_formula_units_of_thirteen_atoms(data):
    counts = {s['site']: s['atoms_per_cell'] for s in data['sites']}
    assert counts == {'3a': 3, '6c_1': 6, '6c_2': 6, '6c_3': 6, '18h': 18}
    assert data['atoms_per_hexagonal_cell'] == 39 and data['formula_units_per_cell'] == 3
    assert len(data['atoms']) == 4 * 39
    # database MU_PHASE sites per formula unit 2:2:2:6:1, times three formula units
    assert sorted(c // 3 for c in counts.values()) == sorted([2, 2, 2, 6, 1])


def test_ideal_nb7ni6_and_coordination(data):
    nb = sum(s['atoms_per_cell'] for s in data['sites'] if s['element_Nb7Ni6'] == 'Nb')
    assert (nb, 39 - nb) == (21, 18)  # Nb7Ni6 x 3
    assert {s['site']: s['CN'] for s in data['sites']} == {'3a': 12, '6c_1': 15, '6c_2': 16, '6c_3': 14, '18h': 12}


def test_no_two_atoms_closer_than_a_bond(data):
    xyz = [a['xyz_A'] for a in data['atoms']]
    assert min(math.dist(p, q) for i, p in enumerate(xyz) for q in xyz[:i]) > 2.3
