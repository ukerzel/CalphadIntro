"""Independent analytical checks for the synthetic Lesson 1 model."""

from __future__ import annotations

import math
import unittest

from course.foundations.regular_solution import (
    R_GAS,
    BinaryRegularSolution,
    lever_fraction,
)


class BinaryFoundationTests(unittest.TestCase):
    def test_pure_limits_and_invalid_domain(self) -> None:
        model = BinaryRegularSolution(600, 20000, 1000, 1200)
        self.assertEqual(model.gibbs(0), 1000)
        self.assertEqual(model.gibbs(1), 1200)
        for x in (-0.1, 1.1, math.nan, math.inf):
            with self.subTest(x=x), self.assertRaises(ValueError):
                model.gibbs(x)
        for kwargs in (
            {"temperature": 0, "omega": 1},
            {"temperature": math.inf, "omega": 1},
            {"temperature": 600, "omega": math.nan},
            {"temperature": 600, "omega": 1, "g_a0": math.inf},
            {"temperature": 600, "omega": 1, "g_b0": math.nan},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                BinaryRegularSolution(**kwargs)
        for method in (model.slope, model.curvature, model.chemical_potentials):
            for x in (0, 1, -0.1, 1.1):
                with self.subTest(method=method, x=x), self.assertRaises(ValueError):
                    method(x)

    def test_derivatives_and_potentials_from_amount_perturbations(self) -> None:
        model = BinaryRegularSolution(750, 6300, 40, -70)
        for x in (0.1, 0.35, 0.8):
            step = 1e-5
            numerical_slope = (model.gibbs(x + step) - model.gibbs(x - step)) / (2 * step)
            numerical_curvature = (
                model.gibbs(x + step) - 2 * model.gibbs(x) + model.gibbs(x - step)
            ) / step**2
            self.assertAlmostEqual(model.slope(x), numerical_slope, delta=1e-4)
            self.assertAlmostEqual(model.curvature(x), numerical_curvature, delta=0.03)
            mu_a, mu_b = model.chemical_potentials(x)
            self.assertAlmostEqual((1 - x) * mu_a + x * mu_b, model.gibbs(x), delta=1e-9)
            n_a, n_b = 1 - x, x
            def total_g(a: float, b: float) -> float:
                return (a + b) * model.gibbs(b / (a + b))
            num_a = (total_g(n_a + step, n_b) - total_g(n_a - step, n_b)) / (2 * step)
            num_b = (total_g(n_a, n_b + step) - total_g(n_a, n_b - step)) / (2 * step)
            self.assertAlmostEqual(mu_a, num_a, delta=1e-4)
            self.assertAlmostEqual(mu_b, num_b, delta=1e-4)

    def test_spinodal_is_not_binodal_and_tangent_is_supporting(self) -> None:
        model = BinaryRegularSolution(600, 20000, 1000, 1200)
        self.assertLess(model.curvature(0.5), 0)
        left, right = model.binodal()
        self.assertLess(left, 0.5)
        self.assertAlmostEqual(left + right, 1, delta=1e-14)
        self.assertGreater(model.curvature(left), 0)
        self.assertAlmostEqual(model.curvature(right), model.curvature(left), delta=1e-8)
        mu_left = model.chemical_potentials(left)
        mu_right = model.chemical_potentials(right)
        for first, second in zip(mu_left, mu_right, strict=True):
            self.assertAlmostEqual(first, second, delta=1e-7)
        tangent_slope = (model.gibbs(right) - model.gibbs(left)) / (right - left)
        self.assertAlmostEqual(tangent_slope, 200, delta=1e-7)
        self.assertAlmostEqual(model.slope(left), tangent_slope, delta=1e-7)
        self.assertAlmostEqual(model.slope(right), tangent_slope, delta=1e-7)
        for x in (left, 0.1, 0.25, 0.5, 0.75, 0.9, right):
            support = model.gibbs(left) + tangent_slope * (x - left)
            self.assertGreaterEqual(model.gibbs(x) - support, -1e-9)
        self.assertGreater(model.gibbs(0.5), model.gibbs(left) + tangent_slope * (0.5 - left))
        self.assertAlmostEqual(model.critical_temperature, model.omega / (2 * R_GAS))

    def test_no_gap_and_phase_fraction_controls(self) -> None:
        for omega in (-10, 0, 2 * R_GAS * 600, 1000):
            model = BinaryRegularSolution(600, omega)
            with self.subTest(omega=omega), self.assertRaises(ValueError):
                model.binodal()
        with self.assertRaisesRegex(ValueError, "not representably bracketed"):
            BinaryRegularSolution(600, 1e8).binodal()
        model = BinaryRegularSolution(600, 20000)
        left, right = model.binodal()
        for z in (left, 0.4, 0.5, right):
            fraction = lever_fraction(z, left, right)
            self.assertGreaterEqual(fraction, 0)
            self.assertLessEqual(fraction, 1)
            self.assertAlmostEqual((1 - fraction) * left + fraction * right, z, delta=1e-14)
        for args in ((-0.1, left, right), (0.99, left, right),
                     (0.4, right, left), (0.4, left, left),
                     (math.nan, left, right), (0.4, math.inf, right)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lever_fraction(*args)


if __name__ == "__main__":
    unittest.main()
