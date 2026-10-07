"""Repeat the original unary model using pycalphad 0.11.2.

Only domain validation is shared with the plain route; pycalphad reads Gibbs
expressions from the original TDB. Conditions and limits: one_component_contract.md.
Official calculate/equilibrium examples: https://pycalphad.org/docs/latest/examples/
"""

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

import numpy as np
from pycalphad import Database, calculate, equilibrium, variables as v

from course.foundations import one_component_manual as manual

MODEL_PATH = Path(__file__).with_name('one_component_model.tdb')
PHASES = ['SOLID', 'LIQUID']


def phase_properties(temperature: float | list[float] | np.ndarray) -> dict[str, np.ndarray]:
    """Calculate both branches, including metastable states, in contract units."""
    t = np.atleast_1d(manual.checked_temperatures(temperature))
    database = Database(str(MODEL_PATH))
    properties = {}
    for output in ['GM', 'HM', 'SM']:
        columns = []
        for phase in PHASES:
            result = calculate(database, ['A'], phase, P=100000, T=t, output=output)
            columns.append(np.asarray(result[output]).reshape(-1))
        properties[output] = np.column_stack(columns)
    return properties


def equilibrium_at(temperature: float) -> dict:
    """Read minimum G and returned fractions; an invariant fraction is arbitrary."""
    t = manual.checked_temperatures(temperature)
    if t.ndim != 0:
        raise ValueError('equilibrium_at needs one scalar temperature')
    database = Database(str(MODEL_PATH))
    result = equilibrium(database, ['A'], PHASES,
                         {v.T: float(t), v.P: 100000, v.N: 1})
    fractions = {}
    for phase, fraction in zip(np.asarray(result.Phase).reshape(-1), np.asarray(result.NP).reshape(-1)):
        if phase:
            fractions[str(phase)] = fractions.get(str(phase), 0.0) + float(fraction)
    return {'GM': float(np.asarray(result.GM).squeeze()), 'fractions': fractions}


def comparison_record() -> dict:
    """Build deterministic results/provenance; numerical acceptance is in tests."""
    temperatures = [800, 900, 1000, 1100, 1200]
    properties = phase_properties(temperatures)
    rows = []
    for i, t in enumerate(temperatures):
        rows.append({'T_K': t, 'plain_GM_J_per_mol': manual.gibbs(t).tolist(),
                     'pycalphad_GM_J_per_mol': properties['GM'][i].tolist(),
                     'pycalphad_HM_J_per_mol': properties['HM'][i].tolist(),
                     'pycalphad_SM_J_per_mol_K': properties['SM'][i].tolist(),
                     'scipy_equilibrium': manual.equilibrium_at(t),
                     'pycalphad_equilibrium': equilibrium_at(t)})
    root = Path(__file__).resolve().parents[2]
    paths = ['course/foundations/one_component_model.tdb',
             'course/foundations/one_component_contract.md',
             'course/foundations/one_component_manual.py',
             'course/foundations/one_component_tools.py',
             'tests/test_one_component_course.py', 'poetry.lock']
    return {'status': 'saved comparison of the plain-Python and pycalphad routes',
            'component': 'A', 'synthetic': True, 'P_Pa': 100000, 'amount_mol': 1,
            'phase_order': PHASES, 'transition_temperature_K': manual.transition_temperature(),
            'at_crossing': 'fractions are not uniquely determined; compare energy and balance',
            'versions': {**{p: version(p) for p in ['numpy','scipy','pycalphad','matplotlib']},
                         'python': platform.python_version()},
            'sha256': {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
            'rows': rows}


def main() -> None:
    """Print the comparison record as JSON for a saved/reviewable local result."""
    print(json.dumps(comparison_record(), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
