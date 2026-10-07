"""Detect magnetic-control and lever-rule errors with original synthetic fixtures."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np
from pycalphad import Database, Model
import xarray as xr

spec = importlib.util.spec_from_file_location("cuni_lesson", Path(__file__).parents[1] / "course/materials/cuni/worked_example.py")
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)

# Invented constants; this fixture is not the published Cu-Ni input.
SYNTHETIC = """
ELEMENT CU FCC_A1 63 0 0 !
ELEMENT NI FCC_A1 59 0 0 !
ELEMENT VA VACUUM 0 0 0 !
TYPE_DEFINITION % SEQ * !
TYPE_DEFINITION & GES AMEND_PHASE_DESCRIPTION FCC_A1 MAGNETIC -3 0.28 !
PHASE FCC_A1 %& 2 1 1 !
CONSTITUENT FCC_A1 :CU,NI:VA: !
PARAMETER G(FCC_A1,CU:VA;0) 298.15 -100; 3000 N !
PARAMETER G(FCC_A1,NI:VA;0) 298.15 -500; 3000 N !
PARAMETER L(FCC_A1,CU,NI:VA;0) 298.15 2500; 3000 N !
PARAMETER TC(FCC_A1,NI:VA;0) 298.15 750; 3000 N !
PARAMETER BMAGN(FCC_A1,NI:VA;0) 298.15 0.8; 3000 N !
"""


class TeachingChecks(unittest.TestCase):
    def test_variant_removes_only_nonzero_magnetic_contribution(self):
        db = Database(SYNTHETIC)
        full = Model(db, lesson.COMPONENTS, "FCC_A1")
        off = lesson.MagneticOffModel(db, lesson.COMPONENTS, "FCC_A1")
        for name in full.models:
            if name != "mag":
                self.assertEqual(full.models[name], off.models[name])
        magnetic = lesson.evaluate(full, full.models["mag"], 400, 0.8)
        self.assertLess(magnetic, -1)
        self.assertEqual(off.models["mag"], 0)
        difference = lesson.evaluate(full, full.GM, 400, 0.8) - lesson.evaluate(off, off.GM, 400, 0.8)
        self.assertAlmostEqual(difference, magnetic, places=8)

    def fixture(self):
        return xr.Dataset({
            "NP": (("X_NI", "vertex"), [[0.25, 0.75, np.nan]]),
            "Phase": (("X_NI", "vertex"), [["FCC_A1", "LIQUID", ""]]),
            "X": (("X_NI", "vertex", "component"), [[[0.2, 0.8], [0.6, 0.4], [np.nan, np.nan]]]),
            "GM": (("X_NI",), [-100.0]),
        }, coords={"X_NI": [0.5], "component": ["NI", "CU"]})

    def test_known_balanced_sample(self):
        self.assertLess(lesson.balance_checks(self.fixture())["max_component_error"]["NI"], 1e-15)

    def test_bad_amount_or_component_or_empty_detected(self):
        for kind in ["amount", "component", "empty"]:
            with self.subTest(kind=kind):
                eq = self.fixture()
                if kind == "amount":
                    eq.NP.values[0, 0] = 0.5
                elif kind == "component":
                    eq.X.values[0, 0, 0] = 0.4
                else:
                    eq.Phase.values[:] = ""
                with self.assertRaises(ValueError):
                    lesson.balance_checks(eq)


if __name__ == "__main__":
    unittest.main()
