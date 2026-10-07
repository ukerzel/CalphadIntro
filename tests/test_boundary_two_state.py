"""Independent Decimal challenge of two closed-state branches."""

from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from course.foundations.boundary_two_state import compare_states, crossing, state_at


NAV = Decimal("6.02214076e23")
GRID = (0.10, 0.25, 0.50, 0.90)


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(y: Decimal) -> Decimal:
    return ((y*y.ln() if y else Decimal(0))
            + ((1-y)*(1-y).ln() if y != 1 else Decimal(0)))


def oracle_state(x0: Decimal, delta: Decimal, eta: Decimal, raw: bool = False):
    """65-digit constrained-exchange bisection and independent full energy."""
    with localcontext() as ctx:
        ctx.prec = 65
        nb, m = Decimal(8000), Decimal(200)
        total = nb*x0+Decimal(50)
        rt, c, tilt = Decimal("8314.5"), Decimal("-9000"), Decimal("12000")

        def residual(theta):
            xb = (total-m*theta)/nb
            return delta+rt*((theta/(1-theta)).ln()-(xb/(1-xb)).ln())

        lo, hi = Decimal("0.000000000001"), Decimal("0.999999999999")
        for _ in range(100):
            mid = (lo+hi)/2
            if residual(mid) < 0:
                lo = mid
            else:
                hi = mid
        theta = (lo+hi)/2
        xb = (total-m*theta)/nb
        gb = c+tilt*xb+rt*q(xb)
        gs = c+(tilt+delta)*theta+rt*q(theta)+eta
        energy = (nb*gb+m*gs)/(nb+m)
        return (theta,xb,energy) if raw else (float(theta),float(xb),float(energy))


def oracle_difference(x0: Decimal, eta2: Decimal = Decimal(2000)) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 65
        left = oracle_state(x0,Decimal(-5000),Decimal(0),raw=True)[2]
        right = oracle_state(x0,Decimal(-10000),eta2,raw=True)[2]
        return right-left


def oracle_crossing() -> float:
    with localcontext() as ctx:
        ctx.prec = 65
        lo, hi = Decimal("0.10"), Decimal("0.25")
        for _ in range(34):
            mid = (lo+hi)/2
            if oracle_difference(mid) > 0:
                lo = mid
            else:
                hi = mid
        return float((lo+hi)/2)


class TwoStateBoundaryTests(TestCase):
    def test_independent_state_minima_energy_and_same_inventory(self):
        for x0 in GRID:
            with self.subTest(x0=x0):
                total = 8000*x0+50
                pair = compare_states(x0)
                for state,delta,eta in (("I",-5000,0),("II",-10000,2000)):
                    out = pair[state]
                    theta,xb,energy = oracle_state(d(x0),d(delta),d(eta))
                    self.assertAlmostEqual(out["theta"],theta,delta=2e-6)
                    self.assertAlmostEqual(out["x_bulk"],(total-200*out["theta"])/8000,delta=1e-12)
                    self.assertAlmostEqual(out["x_bulk"],xb,delta=(200/8000)*2e-6)
                    self.assertAlmostEqual(out["G_molar_J_per_mol_sites"],energy,delta=1e-6)
                    self.assertAlmostEqual(8000*out["x_bulk"]+200*out["theta"],total,delta=1e-9)
                    self.assertAlmostEqual(out["G_cell_J"],energy*8200/float(NAV),delta=1e-22)
                self.assertGreater(pair["II"]["theta"],pair["I"]["theta"])
                self.assertLess(pair["II"]["x_bulk"],pair["I"]["x_bulk"])
                self.assertAlmostEqual(pair["difference_J_per_mol_sites"],
                                       pair["II"]["G_molar_J_per_mol_sites"]
                                       -pair["I"]["G_molar_J_per_mol_sites"],delta=1e-12)
        self.assertGreater(compare_states(.10)["difference_J_per_mol_sites"],5)
        self.assertLess(compare_states(.25)["difference_J_per_mol_sites"],-5)

    def test_unique_crossing_decimal_oracle_and_scan(self):
        out = crossing()
        expected = oracle_crossing()
        self.assertAlmostEqual(out["x_initial"],expected,delta=1e-7)
        self.assertLess(abs(out["difference_J_per_mol_sites"]),1e-6)
        self.assertTrue(out["root_converged"])
        self.assertGreater(out["root_iterations"],0)
        self.assertNotAlmostEqual(out["I"]["theta"],out["II"]["theta"],delta=.01)
        xs = np.linspace(.10,.90,17)
        values = [compare_states(float(x))["difference_J_per_mol_sites"] for x in xs]
        self.assertTrue(all(a>b for a,b in zip(values,values[1:])))
        self.assertEqual(sum(a*b<0 for a,b in zip(values,values[1:])),1)

    def test_baseline_sensitivity_and_negative_controls(self):
        crossings = {eta:crossing(eta)["x_initial"] for eta in (1900,2000,2100)}
        self.assertLess(crossings[1900],crossings[2000])
        self.assertLess(crossings[2000],crossings[2100])
        self.assertGreater(crossings[2000]-crossings[1900],1e-3)
        self.assertGreater(crossings[2100]-crossings[2000],1e-3)
        for x0 in (.10,.25,.50):
            base = compare_states(x0,2000)
            for eta in (1900,2100):
                shifted = compare_states(x0,eta)
                self.assertAlmostEqual(
                    shifted["difference_J_per_mol_sites"]-base["difference_J_per_mol_sites"],
                    200*(eta-2000)/8200,delta=1e-9,
                )
                self.assertAlmostEqual(shifted["II"]["theta"],base["II"]["theta"],delta=1e-9)
        base_low = compare_states(.10)["difference_J_per_mol_sites"]
        omitted_baseline = base_low-200*2000/8200
        self.assertLess(omitted_baseline,0)  # wrong state ordering at low B
        total_at_025 = 8000*.25+50
        before_min = 200*(2000+(-10000+5000)*.25)/8200
        self.assertGreater(before_min,0)  # wrong ordering if both trials held at .25
        self.assertLess(compare_states(.25)["difference_J_per_mol_sites"],0)
        fixed_bulk_wrong = 8000*.25+200*.50
        self.assertNotEqual(fixed_bulk_wrong,total_at_025)
        self.assertAlmostEqual(state_at(.25,"I")["G_molar_J_per_mol_sites"],
                               compare_states(.25)["I"]["G_molar_J_per_mol_sites"],delta=1e-12)

    def test_invalid_inputs_and_corrupted_crossing(self):
        for x,state,eta in ((.099,"I",2000),(.901,"I",2000),([.2],"I",2000),
                            ("bad","I",2000),(.2,"I","bad"),
                            (np.nan,"I",2000),(.2,"III",2000),(.2,"I",1800),
                            (.2,"II",np.nan),(.2,"II",[2000])):
            with self.subTest(x=x,state=state,eta=eta):
                with self.assertRaises(ValueError):
                    state_at(x,state,eta)
        for eta in (1800,np.nan,[2000]):
            with self.assertRaises(ValueError):
                crossing(eta)
        valid = state_at(.2,"I")
        bad = dict(valid,x_bulk=.9)
        with patch("course.foundations.boundary_two_state.closed_equilibrium",return_value=bad):
            with self.assertRaises(RuntimeError):
                state_at(.2,"I")
        bad_energy = dict(valid,G_molar_J_per_mol_sites=np.inf,G_cell_J=np.inf)
        with patch("course.foundations.boundary_two_state.closed_equilibrium",return_value=bad_energy):
            with self.assertRaises(RuntimeError):
                state_at(.2,"I")
        with patch("course.foundations.boundary_two_state.compare_states",
                   return_value={"difference_J_per_mol_sites":1}):
            with self.assertRaises(RuntimeError):
                crossing()
        for fake in ((np.nan,SimpleNamespace(converged=True,iterations=2)),
                     (.2,SimpleNamespace(converged=False,iterations=2)),
                     (.3,SimpleNamespace(converged=True,iterations=2)),
                     (.2,SimpleNamespace(converged=True,iterations=2))):
            with self.subTest(fake=fake), patch(
                "course.foundations.boundary_two_state.brentq",return_value=fake
            ):
                with self.assertRaises(RuntimeError):
                    crossing()
