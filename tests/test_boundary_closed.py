"""Independent high-precision checks of one finite-inventory cell."""

from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from course.foundations.boundary_closed import closed_equilibrium, closed_trial
from course.foundations.boundary_one_state import open_equilibrium


NAV = Decimal("6.02214076e23")
SIZES = (8000, 80000, 800000)
STARTS = (0.10, 0.50, 0.90)
PREFERENCES = (-5000, 0, 5000)
TRIALS = (0, 0.10, 0.25, 0.50, 1)


def dec(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal) -> Decimal:
    return ((value*value.ln() if value else Decimal(0))
            + ((1-value)*(1-value).ln() if value != 1 else Decimal(0)))


def oracle_energy(theta: float, total_b: Decimal, preference: float, nb: int):
    """Independent total-energy route with 65-digit ideal mixing arithmetic."""
    with localcontext() as ctx:
        ctx.prec = 65
        y, n, m, d = dec(theta), Decimal(nb), Decimal(200), dec(preference)
        x = (total_b-m*y)/n
        if not 0 <= x <= 1:
            raise ValueError("infeasible oracle trial")
        rt, c, tilt = Decimal("8314.5"), Decimal("-9000"), Decimal("12000")
        gb = c+tilt*x+rt*q(x)
        gs = c+(tilt+d)*y+rt*q(y)
        numerator = n*gb+m*gs
        return float(x), float(numerator/(n+m)), float(numerator/NAV)


def oracle_residual(theta: Decimal, total_b: Decimal, preference: float, nb: int):
    with localcontext() as ctx:
        ctx.prec = 65
        x = (total_b-Decimal(200)*theta)/Decimal(nb)
        return (dec(preference)+Decimal("8314.5")
                *((theta/(1-theta)).ln()-(x/(1-x)).ln()))


def oracle_root(total_b: Decimal, preference: float, nb: int) -> float:
    with localcontext() as ctx:
        ctx.prec = 65
        lo, hi = Decimal("0.000001"), Decimal("0.999999")
        for _ in range(100):
            mid = (lo+hi)/2
            if oracle_residual(mid,total_b,preference,nb) < 0:
                lo = mid
            else:
                hi = mid
        return float((lo+hi)/2)


class ClosedBoundaryTests(TestCase):
    def test_trial_energy_balance_and_endpoint_grid(self):
        for nb in SIZES:
            for x0 in STARTS:
                total = Decimal(nb)*dec(x0)+Decimal(50)
                for preference in PREFERENCES:
                    for theta in TRIALS:
                        with self.subTest(nb=nb,x0=x0,d=preference,theta=theta):
                            result = closed_trial(theta,float(total),preference,nb)
                            xb, gm, gj = oracle_energy(theta,total,preference,nb)
                            self.assertAlmostEqual(result["x_bulk"],xb,delta=1e-12)
                            self.assertAlmostEqual(result["G_molar_J_per_mol_sites"],gm,delta=1e-7)
                            self.assertAlmostEqual(result["G_cell_J"],gj,delta=1e-24)
                            b = nb*result["x_bulk"]+200*theta
                            a = nb*(1-result["x_bulk"])+200*(1-theta)
                            self.assertAlmostEqual(b,float(total),delta=1e-9)
                            self.assertAlmostEqual(a,nb+200-float(total),delta=1e-9)
        initial = closed_trial(0.25,850,-5000,8000)
        changed = closed_trial(0.35,850,-5000,8000)
        self.assertAlmostEqual(initial["x_bulk"],0.10,delta=1e-15)
        self.assertAlmostEqual(changed["x_bulk"],0.0975,delta=1e-15)
        self.assertNotAlmostEqual(changed["x_bulk"],0.10,delta=1e-6)

    def test_independent_exchange_root_direct_minimum_and_excess(self):
        for nb in SIZES:
            for x0 in STARTS:
                total = Decimal(nb)*dec(x0)+Decimal(50)
                for preference in PREFERENCES:
                    with self.subTest(nb=nb,x0=x0,d=preference):
                        out = closed_equilibrium(x0,preference,nb)
                        root = oracle_root(total,preference,nb)
                        xb, gm, gj = oracle_energy(root,total,preference,nb)
                        self.assertAlmostEqual(out["theta_root"],root,delta=1e-10)
                        self.assertAlmostEqual(out["theta"],root,delta=2e-6)
                        self.assertAlmostEqual(
                            out["x_bulk"],(float(total)-200*out["theta"])/nb,delta=1e-12
                        )
                        self.assertAlmostEqual(out["x_bulk"],xb,delta=(200/nb)*2e-6)
                        self.assertAlmostEqual(out["G_molar_J_per_mol_sites"],gm,delta=1e-6)
                        self.assertAlmostEqual(out["G_cell_J"],gj,delta=1e-22)
                        self.assertAlmostEqual(float(total),out["total_B_atoms"],delta=1e-9)
                        self.assertLessEqual(abs(float(oracle_residual(dec(out["theta_root"]),total,preference,nb))),1e-6)
                        self.assertTrue(out["solver_success"] and out["root_converged"])
                        self.assertGreater(out["nfev"],0)
                        self.assertGreater(out["root_iterations"],0)
                        whole_excess = (nb*out["x_bulk"]+200*out["theta"]
                                        -(nb+200)*out["x_bulk"])
                        gamma = whole_excess/(float(NAV)*40e-18)
                        self.assertAlmostEqual(out["gamma_B_mol_per_m2"],gamma,delta=1e-10)
                        if preference == 0:
                            z = float(total)/float(nb+200)
                            self.assertAlmostEqual(out["theta"],z,delta=2e-6)
                            self.assertAlmostEqual(out["x_bulk"],z,delta=2e-6)
                        elif preference < 0:
                            self.assertGreater(out["theta"],out["x_bulk"])
                        else:
                            self.assertLess(out["theta"],out["x_bulk"])

    def test_large_reservoir_limit_and_negative_controls(self):
        open_theta = open_equilibrium(0.10,-5000)["theta_analytic"]
        errors = [abs(closed_equilibrium(.10,-5000,nb)["theta"]-open_theta)
                  for nb in SIZES]
        self.assertGreater(errors[0],errors[1])
        self.assertGreater(errors[1],errors[2])
        self.assertLessEqual(errors[2],5e-5)
        with self.assertRaises(ValueError):
            closed_trial(0.625,30,-5000,8000)  # 125 B on boundaries exceeds 30 total
        self.assertEqual(closed_trial(0.15,30,-5000,8000)["x_bulk"],0.0)
        out = closed_equilibrium(.10,-5000,8000)
        wrong_one_area = 200*(out["theta"]-out["x_bulk"])/(float(NAV)*20e-18)
        self.assertAlmostEqual(wrong_one_area,2*out["gamma_B_mol_per_m2"],delta=1e-12)
        self.assertGreater(abs(wrong_one_area-out["gamma_B_mol_per_m2"]),1e-7)
        wrong_total = 8000*.10+200*out["theta"]
        self.assertGreater(abs(wrong_total-850),1)
        negative = closed_equilibrium(.10,-5000,8000)
        positive = closed_equilibrium(.10,+5000,8000)
        self.assertGreater(negative["theta"],negative["x_bulk"])
        self.assertLess(positive["theta"],positive["x_bulk"])

    def test_reject_inputs_and_solver_corruption(self):
        for theta,total,pref,nb in (
            (-.1,850,0,8000),(1.1,850,0,8000),(np.nan,850,0,8000),
            ([.2],850,0,8000),(.2,-1,0,8000),(.2,8201,0,8000),
            (.2,30,0,8000),(.2,np.inf,0,8000),(.2,850,10001,8000),
            (.2,850,"bad",8000),(.2,850,0,9000),
        ):
            with self.subTest(theta=theta,total=total,pref=pref,nb=nb):
                with self.assertRaises(ValueError):
                    closed_trial(theta,total,pref,nb)
        for x0,pref,nb in ((.099,0,8000),(.901,0,8000),([.1],0,8000),
                           (.1,np.nan,8000),(.1,0,9000)):
            with self.assertRaises(ValueError):
                closed_equilibrium(x0,pref,nb)
        fakes = (
            SimpleNamespace(success=False,message="injected",x=.2,fun=0,nfev=2),
            SimpleNamespace(success=True,x=np.nan,fun=0,nfev=2),
            SimpleNamespace(success=True,x=1.2,fun=0,nfev=2),
            SimpleNamespace(success=True,x=.2,fun=np.nan,nfev=2),
            SimpleNamespace(success=True,x=[.2],fun=0,nfev=2),
            SimpleNamespace(success=True,x="bad",fun=0,nfev=2),
            SimpleNamespace(success=True,x=.2,fun=0,nfev=0),
            SimpleNamespace(success=True,x=.5,fun=0,nfev=2),
            SimpleNamespace(success=True,x=.2,fun=100,nfev=2),
        )
        for fake in fakes:
            with self.subTest(fake=fake), patch(
                "course.foundations.boundary_closed.minimize_scalar",return_value=fake
            ):
                with self.assertRaises(RuntimeError):
                    closed_equilibrium(.1,-5000,8000)
        normal = closed_equilibrium(.1,-5000,8000)
        with patch(
            "course.foundations.boundary_closed.minimize_scalar",
            return_value=SimpleNamespace(success=True,x=normal["theta_root"],fun=100,nfev=2),
        ):
            with self.assertRaises(RuntimeError):
                closed_equilibrium(.1,-5000,8000)
        with patch("course.foundations.boundary_closed.brentq",
                   return_value=(np.nan,SimpleNamespace(converged=True,iterations=2))):
            with self.assertRaises(RuntimeError):
                closed_equilibrium(.1,-5000,8000)
        with patch("course.foundations.boundary_closed.brentq",
                   return_value=(.2,SimpleNamespace(converged=False,iterations=2))):
            with self.assertRaises(RuntimeError):
                closed_equilibrium(.1,-5000,8000)
        with patch("course.foundations.boundary_closed.brentq",
                   return_value=(.2,SimpleNamespace(converged=True,iterations=2))):
            with self.assertRaises(RuntimeError):
                closed_equilibrium(.1,-5000,8000)
