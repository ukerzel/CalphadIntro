"""Binary-family homogeneous-observable recovery, isolation and identifiability controls."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from course.foundations.binary_fit import predict_hmix,fit_interaction

TRAIN=np.array([.1,.3,.5,.7,.9]);H=np.array([1800.,4200.,5000.,4200.,1800.])
HELD=np.array([.2,.4,.6,.8]);HELD_H=np.array([3200.,4800.,4800.,3200.])

class BinaryFitTests(unittest.TestCase):
    def test_recovery_and_heldout_plain_and_tool(self):
        a=TRAIN*(1-TRAIN);oracle=float(a@H/(a@a))
        self.assertAlmostEqual(oracle,20000,delta=1e-10)
        for route in ('plain','tool'):
            calls=[]
            def recording(omega,x,selected_route='plain'):
                calls.append(np.asarray(x).copy())
                return predict_hmix(omega,x,selected_route)
            with patch('course.foundations.binary_fit.predict_hmix',side_effect=recording):
                fit=fit_interaction(TRAIN,H,route)
            self.assertTrue(all(np.array_equal(x,TRAIN) for x in calls))
            self.assertAlmostEqual(fit['omega'],oracle,delta=1e-5)
            np.testing.assert_allclose(predict_hmix(fit['omega'],HELD,route),HELD_H,atol=1e-6,rtol=0)
            self.assertLess(fit['sse'],1e-10)
        np.testing.assert_allclose(predict_hmix(18000,TRAIN)-H,[-180,-420,-500,-420,-180],atol=1e-10,rtol=0)
        self.assertAlmostEqual(float(np.sum((predict_hmix(18000,TRAIN)-H)**2)),667600,delta=1e-6)

    def test_parameter_bounds_invalid_data_and_identifiability(self):
        for route in ('plain','tool'):
            np.testing.assert_allclose(predict_hmix(0,[0,.5,1],route),[0,0,0],atol=1e-7,rtol=0)
            self.assertAlmostEqual(float(predict_hmix(24000,.5,route)),6000,delta=1e-7)
        for args in [([],[]),(.5,5000),([.5],[np.nan]),([.2,.5],[5000]),([[.5]],[[5000]]),([0,1],[0,0])]:
            with self.assertRaises(ValueError):fit_interaction(*args)
        for omega,x,route in [(-1,.5,'plain'),(24001,.5,'plain'),(20000,1.1,'plain'),(20000,.5,'bad')]:
            with self.assertRaises(ValueError):predict_hmix(omega,x,route)
        with self.assertRaises(ValueError):fit_interaction(TRAIN,H,'bad')
        # Entropy-like B*T*x(1-x) cancels from H=G-T*dG/dT: only A identifiable.
        x=.3;T=1000.;A=20000.
        for B in (-10.,0.,25.):
            gm=(A+B*T)*x*(1-x);dgdt=B*x*(1-x)
            self.assertAlmostEqual(gm-T*dgdt,A*x*(1-x),delta=1e-10)

    def test_failed_solver_and_wrong_observable(self):
        from course.foundations.binary_family_tools import binary_equilibrium,homogeneous_properties
        with patch('course.foundations.binary_fit.least_squares',return_value=SimpleNamespace(success=False,message='forced failure')):
            with self.assertRaises(RuntimeError):fit_interaction(TRAIN,H)
        with patch('course.foundations.binary_fit.least_squares',return_value=SimpleNamespace(success=True,x=np.array([np.nan]))):
            with self.assertRaises(ValueError):fit_interaction(TRAIN,H)
        with patch('course.foundations.binary_fit.least_squares',return_value=SimpleNamespace(success=True,x=np.array([20000.]))):
            with self.assertRaisesRegex(RuntimeError,'nonfinite'):fit_interaction([.5],[1e308])
        state=binary_equilibrium(1000,.5,'R1')
        wrong=sum(r['f']*float(homogeneous_properties(1000,r['x'],'ALPHA',20000)['HM']) for r in state['regions'])-7000
        self.assertGreater(abs(wrong-float(predict_hmix(20000,.5,'tool'))),2000)
