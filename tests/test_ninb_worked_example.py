"""Detect amount/balance mistakes without redistributing the source database."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np
import xarray as xr

spec = importlib.util.spec_from_file_location("ninb_lesson", Path(__file__).parents[1] / "course/materials/ninb/worked_example.py")
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class BalanceChecks(unittest.TestCase):
    def fixture(self):
        # One mole atoms, two phases: 0.25*0.2 + 0.75*0.6 = 0.5 Nb.
        return xr.Dataset({
            "NP": (("X_NB", "vertex"), [[0.25, 0.75, np.nan]]),
            "Phase": (("X_NB", "vertex"), [["DELTA", "MU_PHASE", ""]]),
            "X": (("X_NB", "vertex", "component"), [[[0.2, 0.8], [0.6, 0.4], [np.nan, np.nan]]]),
            "GM": (("X_NB",), [-100.0]),
        }, coords={"X_NB": [0.5], "component": ["NB", "NI"]})

    def test_known_balanced_two_phase_lever_rule(self):
        result = lesson.balance_checks(self.fixture())
        self.assertLess(result["max_component_error"]["NB"], 1e-15)

    def test_wrong_amount_and_wrong_component_detected(self):
        for change in ["amount", "component"]:
            with self.subTest(change=change):
                eq = self.fixture()
                if change == "amount":
                    eq.NP.values[0, 0] = 0.5
                else:
                    eq.X.values[0, 0, 0] = 0.4
                with self.assertRaises(ValueError):
                    lesson.balance_checks(eq)

    def test_empty_or_nonfinite_solution_detected(self):
        for field in ["empty", "energy", "composition"]:
            with self.subTest(field=field):
                eq = self.fixture()
                if field == "empty":
                    eq.Phase.values[:] = ""
                elif field == "energy":
                    eq.GM.values[:] = np.nan
                else:
                    eq.X.values[0, 0, 0] = np.nan
                with self.assertRaises(ValueError):
                    lesson.balance_checks(eq)


if __name__ == "__main__":
    unittest.main()
