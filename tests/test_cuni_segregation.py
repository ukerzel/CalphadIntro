"""Detect exchange-sign, finite-inventory and excess-basis errors."""
import unittest

import numpy as np

from course.materials.boundaries import segregation as lesson


class SegregationChecks(unittest.TestCase):
    def setUp(self):
        rt = lesson.R * lesson.TEMPERATURE
        self.bulk = {
            "g": lambda x: 1200 + 3800*x + rt*((1-x)*np.log(1-x)+x*np.log(x)),
            "dg": lambda x: 3800 + rt*np.log(x/(1-x)),
            "d2g": lambda x: rt/(x*(1-x)),
        }

    def test_open_occupancy_matches_independent_ideal_odds(self):
        x, delta = 0.4, 6000
        k = np.exp(-delta/(lesson.R*lesson.TEMPERATURE))
        expected = k*x/(1-x+k*x)
        actual = lesson.open_occupancy(self.bulk, x, delta)
        self.assertAlmostEqual(actual, expected, delta=1e-10)
        self.assertLess(actual, x)  # Positive Ni preference enriches Cu.
        self.assertAlmostEqual(self.bulk["dg"](x)-self.bulk["dg"](actual),
                               delta, delta=1e-6)

    def test_closed_inventory_matches_independent_quadratic(self):
        z, f, delta = 0.25, 0.2, 6000
        k = np.exp(-delta/(lesson.R*lesson.TEMPERATURE))
        a = f*(1-k)
        b = 1-f-z+k*(z+f)
        expected = 2*k*z/(b+np.sqrt(b*b+4*a*k*z))
        x, y = lesson.closed_occupancy(self.bulk, z, f, delta)
        self.assertAlmostEqual(y, expected, delta=1e-10)
        self.assertAlmostEqual((1-f)*x+f*y, z, delta=1e-10)
        self.assertAlmostEqual((1-f)*(1-x)+f*(1-y), 1-z, delta=1e-10)
        self.assertGreater(x, z)
        self.assertGreater(y, lesson.open_occupancy(self.bulk, z, delta))

    def test_closed_energy_derivative_uses_exchange_and_site_amount(self):
        z, f, delta, y, h = 0.5, 0.1, 6000, 0.3, 1e-6
        def energy(occupancy):
            x = (z-f*occupancy)/(1-f)
            return (1-f)*self.bulk["g"](x)+f*(self.bulk["g"](occupancy)+delta*occupancy)
        x = (z-f*y)/(1-f)
        independent = (energy(y+h)-energy(y-h))/(2*h)
        expected = f*(self.bulk["dg"](y)+delta-self.bulk["dg"](x))
        self.assertAlmostEqual(independent, expected, delta=1e-3)

    def test_zero_preference_gives_uniform_composition(self):
        for z in [0.2, 0.5, 0.8]:
            self.assertAlmostEqual(lesson.open_occupancy(self.bulk, z, 0), z, delta=1e-10)
            x, y = lesson.closed_occupancy(self.bulk, z, 0.02, 0)
            self.assertAlmostEqual(x, z, delta=1e-10)
            self.assertAlmostEqual(y, z, delta=1e-10)

    def test_excess_matches_independent_counts_and_area_conversion(self):
        # 200 occupied sites/20 nm², 140 Cu versus 100 in the bulk reference.
        excess = lesson.cu_excess(0.5, 0.3, 10)
        self.assertAlmostEqual(excess["atoms_per_nm2"], (140-100)/20, delta=1e-10)
        self.assertAlmostEqual(excess["mol_per_m2"],
                               (140-100)/(20e-18*lesson.AVOGADRO), delta=1e-10)

    def test_invalid_inputs_and_solute_limited_feasible_interval(self):
        for x in [0, 1, np.nan]:
            with self.assertRaises(ValueError):
                lesson.open_occupancy(self.bulk, x, 6000)
        for f in [0, 1, np.nan]:
            with self.assertRaises(ValueError):
                lesson.closed_occupancy(self.bulk, 0.5, f, 6000)
        with self.assertRaises(ValueError):
            lesson.open_occupancy(self.bulk, 0.5, np.nan)
        x, y = lesson.closed_occupancy(self.bulk, 0.005, 0.2, 6000)
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertLess(y, 0.005/0.2)
        self.assertAlmostEqual(0.8*x+0.2*y, 0.005, delta=1e-10)


if __name__ == "__main__":
    unittest.main()
