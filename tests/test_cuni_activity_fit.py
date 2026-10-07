"""Detect component/reference/sign and identifiability errors with invented data."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np
from pycalphad import Database

spec = importlib.util.spec_from_file_location(
    "cuni_activity_fit", Path(__file__).parents[1] / "course/materials/cuni/fit_activity.py")
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)

# Invented unary and interaction energies, not a published database.
SYNTHETIC = """
ELEMENT CU FCC_A1 63 0 0 !
ELEMENT NI FCC_A1 59 0 0 !
ELEMENT VA VACUUM 0 0 0 !
TYPE_DEFINITION % SEQ * !
PHASE FCC_A1 % 2 1 1 !
CONSTITUENT FCC_A1 :CU,NI:VA: !
PARAMETER G(FCC_A1,CU:VA;0) 298.15 1200; 3000 N !
PARAMETER G(FCC_A1,NI:VA;0) 298.15 4000; 3000 N !
PARAMETER L(FCC_A1,CU,NI:VA;0) 298.15 2500; 3000 N !
PARAMETER L(FCC_A1,CU,NI:VA;1) 298.15 0; 3000 N !
"""


class ActivityFitChecks(unittest.TestCase):
    def setUp(self):
        self.forward = lesson.make_forward_model(Database(SYNTHETIC))

    def test_ni_component_and_pure_reference_by_hand(self):
        x = 0.3
        expected = lesson.R * lesson.TEMPERATURE * np.log(x) + 2500 * (1-x)**2
        actual = self.forward["mu_relative"]([x])[0]
        self.assertAlmostEqual(actual, expected, delta=1e-7)
        self.assertAlmostEqual(self.forward["pure_ni_G"], 4000, delta=1e-7)
        self.assertAlmostEqual(lesson.predict_activity(self.forward, [1.0], [5000, -1000])[0],
                               1.0, delta=1e-10)

    def test_recovers_two_known_isothermal_interactions(self):
        x = np.array([0.1, 0.25, 0.4, 0.6, 0.8, 0.9])
        # Independent partial-molar formula for total L0=7000, L1=-900.
        measured = np.exp((lesson.R * lesson.TEMPERATURE * np.log(x)
                           + (1-x)**2 * (7000 - 900*(1-4*x)))
                          / (lesson.R * lesson.TEMPERATURE))
        fitted = lesson.fit_isothermal(self.forward, x, measured)
        np.testing.assert_allclose(fitted["delta_L_J_per_mol"], [4500, -900], atol=1e-5, rtol=0)
        self.assertLess(fitted["sse_after_J2_per_mol2"], 1e-12)

    def test_chemical_potential_matches_independent_finite_difference(self):
        x, h = 0.37, 1e-6
        g = self.forward["g"]
        expected = g([x])[0] + (1-x) * (g([x+h])[0]-g([x-h])[0])/(2*h)
        expected -= self.forward["pure_ni_G"]
        self.assertAlmostEqual(self.forward["mu_relative"]([x])[0], expected, delta=1e-3)

    def test_invalid_or_unidentifiable_observations_rejected(self):
        for x, activity in [([0.2, 0.2], [0.4, 0.5]), ([0, 0.8], [0.3, 0.9]),
                            ([0.2, 0.8], [0, 0.9]), ([0.2, 0.8], [np.nan, 0.9]),
                            ([0.2], [0.4, 0.9])]:
            with self.subTest(x=x, activity=activity), self.assertRaises(ValueError):
                lesson.fit_isothermal(self.forward, x, activity)

    def test_one_temperature_cannot_identify_four_A_B_coefficients(self):
        x = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        basis = lesson.interaction_basis(x)
        full = np.column_stack((basis[:, 0], lesson.TEMPERATURE*basis[:, 0],
                                basis[:, 1], lesson.TEMPERATURE*basis[:, 1]))
        self.assertEqual(np.linalg.matrix_rank(full), 2)


if __name__ == "__main__":
    unittest.main()
