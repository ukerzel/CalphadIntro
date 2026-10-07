"""Open-reservoir one-state detecting checks against independent high-precision site thermodynamics."""

from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from course.foundations.boundary_one_state import grand_potential, open_equilibrium


XB = (0.01, 0.10, 0.50, 0.90, 0.99)
PREFERENCE = (-10000.0, 0.0, 10000.0)
THETA = (0.0, 0.10, 0.50, 0.90, 1.0)
NAV = Decimal("6.02214076e23")


def oracle(x_bulk: float, preference: float, theta: float) -> tuple[float, float, float]:
    """Independent Decimal KL/ratio route, not the binary-family energy implementation."""
    with localcontext() as ctx:
        ctx.prec = 65
        x, d, y = map(lambda value: Decimal(str(value)), (x_bulk, preference, theta))
        rt = Decimal("8.3145") * Decimal(1000)
        first = Decimal(0) if y == 1 else (1-y) * ((1-y)/(1-x)).ln()
        second = Decimal(0) if y == 0 else y * (y/x).ln()
        phi = rt * (first + second) + d*y
        ratio = x/(1-x) * (-d/rt).exp()
        optimum = ratio/(1+ratio)
        min_phi = -rt * ((1-x)+x*(-d/rt).exp()).ln()
        return float(phi), float(optimum), float(min_phi)


class OpenBoundaryTests(TestCase):
    def test_potential_independent_decimal_grid_and_endpoint_policy(self):
        for x in XB:
            for preference in PREFERENCE:
                for theta in THETA:
                    with self.subTest(x=x, preference=preference, theta=theta):
                        expected, _, _ = oracle(x, preference, theta)
                        self.assertAlmostEqual(
                            grand_potential(theta, x, preference), expected, delta=1e-7
                        )
        for x in XB:
            self.assertAlmostEqual(grand_potential(x, x, 0), 0.0, delta=1e-9)

    def test_direct_minimum_analytic_oracle_excess_and_signs(self):
        for x in XB:
            for preference in PREFERENCE:
                with self.subTest(x=x, preference=preference):
                    out = open_equilibrium(x, preference)
                    _, theta_ref, phi_ref = oracle(x, preference, x)
                    self.assertAlmostEqual(out["theta_analytic"], theta_ref, delta=1e-12)
                    self.assertAlmostEqual(out["theta"], theta_ref, delta=2e-6)
                    odds_ratio = (out["theta_analytic"]/(1-out["theta_analytic"]))/(x/(1-x))
                    self.assertAlmostEqual(
                        odds_ratio, np.exp(-preference/(8.3145*1000)), delta=1e-12
                    )
                    self.assertAlmostEqual(out["phi_J_per_mol_sites"], phi_ref, delta=1e-6)
                    self.assertGreater(out["nfev"], 0)
                    self.assertTrue(out["solver_success"])
                    whole_b = 8000*x + 200*out["theta"]
                    whole_gamma = (whole_b - 8200*x) / (float(NAV) * 40e-18)
                    self.assertAlmostEqual(
                        out["gamma_B_mol_per_m2"], whole_gamma, delta=1e-10
                    )
                    if preference == 0:
                        self.assertAlmostEqual(out["theta"], x, delta=2e-6)
                        self.assertAlmostEqual(out["gamma_B_mol_per_m2"], 0, delta=1e-10)
                    elif preference < 0:
                        self.assertGreater(out["theta"], x)
                        self.assertGreater(out["gamma_B_mol_per_m2"], 0)
                    else:
                        self.assertLess(out["theta"], x)
                        self.assertLess(out["gamma_B_mol_per_m2"], 0)

    def test_wrong_exchange_sign_reference_and_area_are_detected(self):
        x, preference = 0.1, -5000.0
        out = open_equilibrium(x, preference)
        _, correct, _ = oracle(x, preference, x)
        _, reversed_sign, _ = oracle(x, -preference, x)
        self.assertGreater(abs(correct-reversed_sign), 0.10)
        from course.foundations.binary_family import DELTA, R, ideal_derivatives

        mu_b = float(ideal_derivatives(1000, x, "ALPHA")["mu_B"])
        wrong_mu_b_only = 1/(1+np.exp(-(mu_b-DELTA-preference)/(R*1000)))
        self.assertGreater(abs(correct-wrong_mu_b_only), 0.10)
        wrong_one_area = (200*(out["theta"]-x))/(float(NAV)*20e-18)
        self.assertAlmostEqual(wrong_one_area, 2*out["gamma_B_mol_per_m2"], delta=1e-12)
        self.assertGreater(abs(wrong_one_area-out["gamma_B_mol_per_m2"]), 1e-7)
        self.assertEqual(800+50+20, 870)  # invalid closed B total if bulk x is held fixed
        self.assertEqual(780+70, 850)  # correctly closed counterpart

    def test_invalid_inputs_and_solver_failures(self):
        for theta, x, preference in (
            (-0.01, 0.1, 0), (1.01, 0.1, 0), (np.nan, 0.1, 0),
            ([0.1], 0.1, 0), (0.5, 0.009, 0), (0.5, 0.991, 0),
            (0.5, np.inf, 0), (0.5, [0.1], 0),
            (0.5, 0.1, -10001), (0.5, 0.1, 10001),
            (0.5, 0.1, np.nan), (0.5, 0.1, [0]),
            (0.5, 0.1, "not-a-number"),
        ):
            with self.subTest(theta=theta, x=x, preference=preference):
                with self.assertRaises(ValueError):
                    grand_potential(theta, x, preference)
        for x, preference in ((0, 0), (1, 0), ([0.1], 0), (0.1, np.inf), (0.1, 10001)):
            with self.assertRaises(ValueError):
                open_equilibrium(x, preference)
        for fake in (
            SimpleNamespace(success=False, message="injected", x=0.2, fun=0, nfev=2),
            SimpleNamespace(success=True, x=np.nan, fun=0, nfev=2),
            SimpleNamespace(success=True, x=1.2, fun=0, nfev=2),
            SimpleNamespace(success=True, x=0.2, fun=np.nan, nfev=2),
            SimpleNamespace(success=True, x=0.5, fun=0, nfev=2),
            SimpleNamespace(success=True, x=0.1, fun=100, nfev=2),
            SimpleNamespace(success=True, x=oracle(0.1, -5000, 0.1)[1],
                            fun=100, nfev=2),
            SimpleNamespace(success=True, x=[0.2], fun=0, nfev=2),
            SimpleNamespace(success=True, x=0.2, fun=[0], nfev=2),
            SimpleNamespace(success=True, x=0.2, fun=0, nfev=0),
            SimpleNamespace(success=True, x="bad", fun=0, nfev=2),
        ):
            with self.subTest(fake=fake), patch(
                "course.foundations.boundary_one_state.minimize_scalar", return_value=fake
            ):
                with self.assertRaises(RuntimeError):
                    open_equilibrium(0.1, -5000)
        with patch(
            "course.foundations.boundary_one_state.minimize_scalar",
            return_value=SimpleNamespace(success=True, x=0.2, fun=0, nfev=2),
        ):
            with self.assertRaises(RuntimeError):
                open_equilibrium(0.1, 0)
