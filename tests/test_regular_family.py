"""Stored-reference tests for R1; the older regular_solution is never imported."""
import json,math
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from scipy.optimize import minimize_scalar
from course.foundations.binary_family import (R, regular_properties,regular_derivatives,
    regular_binodal,regular_equilibrium)
REF=json.loads(Path('course/foundations/binary_family_reference.json').read_text())
TC=20000/(2*R)

class RegularFamilyTests(unittest.TestCase):
    def test_frozen_properties_and_limits(self):
        for row in REF['property_rows']:
            T,x=float(row['T_K']),float(row['x']);p=regular_properties(T,x)
            self.assertAlmostEqual(float(p['GM']),float(row['regular_alpha_GM']),delta=1e-7)
            h=1000+12000*x+20000*x*(1-x)
            self.assertAlmostEqual(float(p['HM']),h,delta=1e-7)
            self.assertAlmostEqual(float(p['GM']),float(p['HM']-T*p['SM']),delta=1e-7)
        for omega in (0,12000,24000):
            p=regular_properties(1000,np.array([0,.5,1]),omega)
            np.testing.assert_allclose(p['HM_mix'],[0,omega/4,0],atol=1e-7,rtol=0)
            self.assertEqual(float(p['GM'][0]),-9000)
            self.assertEqual(float(p['GM'][-1]),3000)
        for omega in (-1,24001,np.nan,np.inf,[],[20000]):
            with self.assertRaises(ValueError):regular_properties(1000,.5,omega)

    def test_frozen_binodals_and_balance(self):
        for row in REF['regular_one_phase']:
            T=float(row['T_K']);out=regular_binodal(T);left,right=out['compositions']
            self.assertEqual(out['status'],'two_compositions')
            self.assertAlmostEqual(left,float(row['x_left']),delta=1e-9)
            self.assertAlmostEqual(right,float(row['x_right']),delta=1e-9)
            self.assertLess(abs((right-left)/float(row['gap'])-1),1e-5)
            dl,dr=regular_derivatives(T,left),regular_derivatives(T,right)
            for k in ('mu_A','mu_B'):self.assertAlmostEqual(float(dl[k]),float(dr[k]),delta=1e-6)
            self.assertAlmostEqual(float(dl['mu_A']),float(row['tangent_intercept_J_per_mol']),delta=1e-6)
            self.assertAlmostEqual(float(dl['slope']),12000,delta=1e-6)
            for z in (0,.05,.25,.5,.75,.95,1):
                state=regular_equilibrium(T,z);regions=state['regions']
                self.assertTrue(all(r['phase']=='ALPHA' and r['f']>0 for r in regions))
                self.assertAlmostEqual(sum(r['f'] for r in regions),1,delta=1e-10)
                self.assertAlmostEqual(sum(r['f']*r['x'] for r in regions),z,delta=1e-10)
                self.assertAlmostEqual(sum(r['f']*(1-r['x']) for r in regions),1-z,delta=1e-10)
                self.assertLessEqual(state['GM'],float(regular_properties(T,z)['GM'])+1e-7)
        for T in (TC,1300,1800):
            self.assertEqual(regular_binodal(T),{'status':'single_phase','compositions':[],'spinodal':[]})
            self.assertEqual(len(regular_equilibrium(T,.5)['regions']),1)
        near=TC*(1-0.5e-6)
        with self.assertRaisesRegex(ValueError,'near-critical'):regular_binodal(near)
        self.assertTrue(np.isfinite(regular_properties(near,.5)['GM']))
        regular_binodal(TC*(1-1e-6)) # inclusive supported boundary

    def test_global_support_metastable_and_central_root_controls(self):
        for row in REF['regular_one_phase']:
            T=float(row['T_K']);sol=regular_binodal(T);left,right=sol['compositions'];sl,sr=sol['spinodal']
            c=float(regular_derivatives(T,left)['mu_A'])
            difference=lambda x:float(regular_properties(T,x)['GM'])-c-12000*x
            # g-line derivative has turning points exactly at spinodals;
            # split intervals prevents a unimodal solver from missing another basin.
            for a,b in zip([0,sl,sr],[sl,sr,1]):
                result=minimize_scalar(difference,bounds=(a,b),method='bounded',options={'xatol':1e-14})
                self.assertTrue(result.success)
                self.assertGreaterEqual(min(result.fun,difference(a),difference(b)),-1e-6)
            self.assertLess(left,sl);self.assertLess(sl,.5);self.assertLess(.5,sr);self.assertLess(sr,right)
        p=regular_derivatives(600,.05)
        self.assertGreater(float(p['curvature']),0)
        self.assertGreater(float(regular_properties(600,.05)['GM'])-regular_equilibrium(600,.05)['GM'],50)
        self.assertLess(float(regular_derivatives(600,.5)['curvature']),0)
        self.assertEqual(float(regular_derivatives(600,.5)['slope']),12000)
        # Central root of affine-subtracted derivative has zero residual but wrong gap.
        self.assertEqual(float(regular_derivatives(600,.5)['slope'])-12000,0)
        self.assertGreater(float(REF['regular_one_phase'][0]['gap']),.95)
        with patch('course.foundations.binary_family.brentq',return_value=(.5,SimpleNamespace(converged=True))):
            with self.assertRaises(RuntimeError):regular_binodal(600)
        with patch('course.foundations.binary_family.brentq',return_value=(.1,SimpleNamespace(converged=False))):
            with self.assertRaises(RuntimeError):regular_binodal(600)

        with patch('course.foundations.binary_family.brentq',return_value=(.1,SimpleNamespace(converged=True))):
            with self.assertRaisesRegex(RuntimeError,'residual'):regular_binodal(600)

    def test_independent_total_derivatives(self):
        for x in (.2,.5,.8):
            a,b=1-x,x;out=regular_derivatives(1000,x);errors=[]
            def G(na,nb):
                n=na+nb;y=nb/n
                return n*(1000-10000+12000*y+8314.5*((1-y)*math.log(1-y)+y*math.log(y))+20000*y*(1-y))
            for h in (1e-3,1e-4,1e-5,1e-6):
                values=[(G(a+h,b)-G(a-h,b))/(2*h),(G(a,b+h)-G(a,b-h))/(2*h),(G(a-h,b+h)-G(a+h,b-h))/(2*h)]
                errors.append(max(abs(v-float(out[k])) for k,v in zip(('mu_A','mu_B','slope'),values)))
            self.assertLess(errors[2],1e-3);self.assertLess(errors[3],1e-3)
            self.assertLess(errors[1],errors[0]/50)
        for x in (0,1):
            with self.assertRaises(ValueError):regular_derivatives(1000,x)
