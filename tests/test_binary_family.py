"""Detect the synthetic binary-family contract using stored Decimal references."""
import json
from decimal import Decimal, localcontext
from pathlib import Path
import unittest
import warnings
import numpy as np
from course.foundations.binary_family import ideal_properties

REFERENCE = json.loads(Path('course/foundations/binary_family_reference.json').read_text())

class IdealPropertiesTests(unittest.TestCase):
    def test_frozen_g_and_independent_decimal_h_s(self):
        with localcontext() as ctx:
            ctx.prec = 70
            for row in REFERENCE['property_rows']:
                t, x = Decimal(row['T_K']), Decimal(row['x'])
                q = Decimal(0) if x in (0, 1) else x*x.ln()+(1-x)*(1-x).ln()
                s = 10-Decimal('8.3145')*q
                for phase in ('ALPHA', 'BETA'):
                    with self.subTest(T=t, x=x, phase=phase):
                        out = ideal_properties(float(t), float(x), phase)
                        h = 1000+12000*(x if phase == 'ALPHA' else 1-x)
                        self.assertAlmostEqual(float(out['GM']), float(row['ideal_'+phase.lower()+'_GM']), delta=1e-7)
                        self.assertAlmostEqual(float(out['HM']), float(h), delta=1e-7)
                        self.assertAlmostEqual(float(out['SM']), float(s), delta=1e-7)
                        self.assertAlmostEqual(float(out['GM']), float(out['HM']-float(t)*out['SM']), delta=1e-7)
                        self.assertEqual(float(out['HM_mix']), 0.)

    def test_limits_vector_shape_symmetry_and_no_input_change(self):
        xs = np.array([0., .05, .2, .5, .8, .95, 1.])
        original = xs.copy()
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            a = ideal_properties(1000, xs)
            b = ideal_properties(1000, 1-xs, 'BETA')
        np.testing.assert_array_equal(xs, original)
        for key in a:
            self.assertEqual(a[key].shape, xs.shape)
            self.assertTrue(np.isfinite(a[key]).all())
            np.testing.assert_allclose(a[key], b[key], atol=1e-10, rtol=0)
        np.testing.assert_array_equal(a['GM'][[0,-1]], [-9000, 3000])
        np.testing.assert_array_equal(a['SM'][[0,-1]], [10, 10])
        np.testing.assert_array_equal(a['HM'][[0,-1]], [1000,13000])
        self.assertTrue((a['GM_mix'] <= 0).all())
        self.assertTrue((a['SM_mix'] >= 0).all())
        self.assertEqual(ideal_properties(600, .5)['GM'].shape, ())

    def test_reject_invalid_conditions_without_clipping(self):
        for t in (599.9,1800.1,np.nan,np.inf,[],[1000],[[1000]]):
            with self.subTest(T=t), self.assertRaises(ValueError):
                ideal_properties(t, .5)
        for x in ([],[[]],[[.5]],-.001,1.001,np.nan,np.inf,[.2,np.nan]):
            with self.subTest(x=x), self.assertRaises(ValueError):
                ideal_properties(1000, x)
        with self.assertRaises(ValueError):
            ideal_properties(1000,.5,'LIQUID')

class IdealEquilibriumTests(unittest.TestCase):
    def test_frozen_equilibrium_and_balances(self):
        from course.foundations.binary_family import ideal_equilibrium
        for row in REFERENCE['ideal_two_phase']:
            T=float(row['T_K'])
            for state in row['states']:
                z=float(state['z']); out=ideal_equilibrium(T,z)
                self.assertAlmostEqual(out['GM'],float(state['g_eq_J_per_mol']),delta=1e-6)
                self.assertAlmostEqual(sum(r['f'] for r in out['regions']),1,delta=1e-10)
                self.assertAlmostEqual(sum(r['f']*r['x'] for r in out['regions']),z,delta=1e-10)
                self.assertAlmostEqual(sum(r['f']*(1-r['x']) for r in out['regions']),1-z,delta=1e-10)
                fb=sum(r['f'] for r in out['regions'] if r['phase']=='BETA')
                self.assertAlmostEqual(fb,float(state['f_beta']),delta=1e-8)
                if len(out['regions'])==2:
                    for region,key in zip(out['regions'],['x_alpha','x_beta']):
                        self.assertAlmostEqual(region['x'],float(row[key]),delta=1e-8)
        for z in (0.,1.):
            out=ideal_equilibrium(1000,z)
            self.assertEqual(len(out['regions']),1)
            self.assertEqual(out['regions'][0]['x'],z)
        row=REFERENCE['ideal_two_phase'][1]
        for key in ('x_alpha','x_beta'):
            out=ideal_equilibrium(1000,float(row[key]))
            # Roundoff at a tie boundary may yield a vanishing second amount.
            self.assertAlmostEqual(max(r['f'] for r in out['regions']),1,delta=1e-14)

    def test_nested_grid_feasibility_upper_bound_and_refinement(self):
        from course.foundations.binary_family import ideal_equilibrium, ideal_grid
        for T in (600.,1000.,1800.):
            for z in (.05,.25,.5,.75,.95):
                exact=ideal_equilibrium(T,z)['GM']; previous=float('inf')
                for points in (21,101,501):
                    out=ideal_grid(T,z,points)
                    f=np.array([r['f'] for r in out['regions']]); x=np.array([r['x'] for r in out['regions']])
                    self.assertTrue((f>=0).all())
                    self.assertAlmostEqual(f.sum(),1,delta=1e-10)
                    self.assertAlmostEqual(f@x,z,delta=1e-10)
                    self.assertAlmostEqual(f@(1-x),1-z,delta=1e-10)
                    self.assertGreaterEqual(out['GM'],exact-1e-7)
                    self.assertLessEqual(out['GM'],previous+1e-7)
                    previous=out['GM']
        for z in (0.,1.):
            self.assertAlmostEqual(ideal_grid(1000,z,21)['GM'],-9000,delta=1e-7)
        # Omitting BETA incorrectly makes the equimolar ideal sample homogeneous.
        self.assertGreater(float(ideal_properties(1000,.5)['GM'])-ideal_equilibrium(1000,.5)['GM'],1900)

    def test_fail_closed_and_no_clipped_balance(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from course.foundations.binary_family import ideal_equilibrium, ideal_grid, lever_fraction
        for function in (ideal_equilibrium,ideal_grid):
            for z in ([],[.5],-.1,1.1,np.nan):
                with self.subTest(function=function.__name__,z=z),self.assertRaises(ValueError):function(1000,z)
        for count in (1,21.5,True):
            with self.assertRaises(ValueError):ideal_grid(1000,.5,count)
        self.assertAlmostEqual(lever_fraction(.3,.1,.6),.4)
        for args in ((.8,.1,.6),(.3,.3,.3),(.3,.6,.1),([.3],.1,.6)):
            with self.assertRaises(ValueError):lever_fraction(*args)
        with patch('course.foundations.binary_family.linprog',return_value=SimpleNamespace(success=False,message='injected failure')):
            with self.assertRaises(RuntimeError):ideal_grid(1000,.5,21)
        for weights in (np.full(42,np.nan),np.zeros(42),np.r_[-1.,2.,np.zeros(40)]):
            with patch('course.foundations.binary_family.linprog',return_value=SimpleNamespace(success=True,x=weights)):
                with self.assertRaises(RuntimeError):ideal_grid(1000,.5,21)

class IdealChemicalPotentialTests(unittest.TestCase):
    @staticmethod
    def independent_total(T,nA,nB,phase):
        import math
        n=nA+nB; x=nB/n
        tilt=12000*x if phase=='ALPHA' else 12000*(1-x)
        return n*(1000-10*T+tilt+8.3145*T*((1-x)*math.log(1-x)+x*math.log(x)))

    def test_independent_addition_and_exchange_refinement(self):
        from course.foundations.binary_family import ideal_derivatives
        for phase in ('ALPHA','BETA'):
            for x in (.2,.5,.8):
                a,b=1-x,x; out=ideal_derivatives(1000,x,phase)
                errors=[]
                for step in (1e-3,1e-4,1e-5,1e-6):
                    G=lambda na,nb:self.independent_total(1000,na,nb,phase)
                    mua=(G(a+step,b)-G(a-step,b))/(2*step)
                    mub=(G(a,b+step)-G(a,b-step))/(2*step)
                    exchange=(G(a-step,b+step)-G(a+step,b-step))/(2*step)
                    errors.append(max(abs(mua-out['mu_A']),abs(mub-out['mu_B']),abs(exchange-out['slope'])))
                self.assertLess(errors[2],1e-3);self.assertLess(errors[3],1e-3)
                self.assertLess(errors[1],errors[0]/50)
                self.assertAlmostEqual(out['mu_B']-out['mu_A'],out['slope'],delta=1e-7)
                g=float(ideal_properties(1000,x,phase)['GM'])
                self.assertAlmostEqual(g,(1-x)*out['mu_A']+x*out['mu_B'],delta=1e-7)
                self.assertGreater(abs(out['slope']-out['mu_B']),1000)

    def test_global_support_all_branches_and_counterexample(self):
        from scipy.optimize import minimize_scalar
        from course.foundations.binary_family import ideal_derivatives,ideal_equilibrium
        for T in (600,1000,1800):
            for z in (.05,.25,.5,.75,.95):
                state=ideal_equilibrium(T,z); r=state['regions'][0]
                d=ideal_derivatives(T,r['x'],r['phase']); intercept=float(d['mu_A']); slope=float(d['slope'])
                for region in state['regions']:
                    other=ideal_derivatives(T,region['x'],region['phase'])
                    self.assertAlmostEqual(float(d['mu_A']),float(other['mu_A']),delta=1e-6)
                    self.assertAlmostEqual(float(d['mu_B']),float(other['mu_B']),delta=1e-6)
                for phase in ('ALPHA','BETA'):
                    difference=lambda x:float(ideal_properties(T,x,phase)['GM'])-(intercept+slope*x)
                    result=minimize_scalar(difference,bounds=(0,1),method='bounded',options={'xatol':1e-14})
                    self.assertTrue(result.success)
                    self.assertGreaterEqual(min(result.fun,difference(0),difference(1)),-1e-6)
                    self.assertTrue((ideal_derivatives(T,np.array([.001,.2,.5,.8,.999]),phase)['curvature']>0).all())
        # ALPHA's tangent at .5 supports ALPHA but lies above BETA at .8.
        d=ideal_derivatives(1000,.5)
        gap=float(ideal_properties(1000,.8,'BETA')['GM'])-(d['mu_A']+d['slope']*.8)
        self.assertLess(gap,-5000)

    def test_common_affine_reference_shift(self):
        from scipy.optimize import linprog
        from course.foundations.binary_family import ideal_grid,ideal_derivatives
        x=np.tile(np.linspace(0,1,101),2)
        energies=np.r_[ideal_properties(1000,x[:101])['GM'],ideal_properties(1000,x[:101],'BETA')['GM']]
        a,b=432.,-765.
        for z in (.05,.25,.5,.75,.95):
            shifted=linprog(energies+a+b*x,A_eq=[np.ones_like(x),x],b_eq=[1,z],bounds=(0,None),method='highs')
            self.assertTrue(shifted.success)
            original=ideal_grid(1000,z,101)
            weights=np.zeros(202)
            for r in original['regions']:weights[round(100*r['x'])+(0 if r['phase']=='ALPHA' else 101)]=r['f']
            np.testing.assert_allclose(shifted.x,weights,atol=1e-8,rtol=0)
            self.assertAlmostEqual(shifted.fun,original['GM']+a+b*z,delta=1e-6)
        d=ideal_derivatives(1000,.2); g=float(ideal_properties(1000,.2)['GM'])
        self.assertAlmostEqual(g+a+b*.2-.2*(d['slope']+b),d['mu_A']+a,delta=1e-7)
        self.assertAlmostEqual(g+a+b*.2+.8*(d['slope']+b),d['mu_B']+a+b,delta=1e-7)

    def test_endpoints_and_unrepresentable_output_rejected(self):
        from course.foundations.binary_family import ideal_derivatives
        for x in (0,1,[.5,0],np.nextafter(0.,1.)):
            with self.subTest(x=x),self.assertRaises(ValueError):ideal_derivatives(1000,x)
        for phase in ('ALPHA','BETA'):
            d=ideal_derivatives(600,np.array([1e-12,1-1e-12]),phase)
            for value in d.values():self.assertTrue(np.isfinite(value).all())
        with self.assertRaises(ValueError):ideal_derivatives(1000,.5,'SOLID')
