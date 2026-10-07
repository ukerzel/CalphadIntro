"""Independent representation and fixed-contract pycalphad parity checks."""
import unittest
import numpy as np
from course.foundations.binary_family import ideal_properties,regular_properties,ideal_equilibrium,regular_equilibrium
from course.foundations.binary_family_tools import homogeneous_properties,binary_equilibrium

class BinaryToolsTests(unittest.TestCase):
    def test_actual_homogeneous_properties_all_contract_points(self):
        x=np.array([0,.05,.2,.5,.8,.95,1.])
        for T in (600,1000,1800):
            for phase,omega in [('ALPHA',0),('BETA',0),('ALPHA',20000)]:
                with self.subTest(T=T,phase=phase,omega=omega):
                    tool=homogeneous_properties(T,x,phase,omega)
                    np.testing.assert_allclose(tool['actual_x'],x,rtol=0,atol=1e-14)
                    plain=regular_properties(T,tool['actual_x'],omega) if phase=='ALPHA' else ideal_properties(T,tool['actual_x'],phase)
                    for key in ('GM','HM','SM'):np.testing.assert_allclose(tool[key],plain[key],atol=1e-7,rtol=0)
        scalar=homogeneous_properties(1000,.5,'ALPHA',20000)
        self.assertAlmostEqual(float(scalar['HM'])-7000,5000,delta=1e-6)

    def test_equilibrium_same_model_all_required_cases(self):
        for variant,temperatures,plain in [('I2',(600,1000,1800),ideal_equilibrium),('R1',(600,900,1100,1300,1800),regular_equilibrium)]:
            for T in temperatures:
                for z in (.05,.25,.5,.75,.95):
                    with self.subTest(variant=variant,T=T,z=z):
                        tool=binary_equilibrium(T,z,variant);expected=plain(T,z)
                        self.assertAlmostEqual(tool['GM'],expected['GM'],delta=1e-5)
                        actual=sorted(tool['regions'],key=lambda r:r['x']);ref=sorted(expected['regions'],key=lambda r:r['x'])
                        self.assertEqual(len(actual),len(ref))
                        for a,b in zip(actual,ref):
                            self.assertEqual(a['phase'],b['phase'])
                            self.assertAlmostEqual(a['x'],b['x'],delta=1e-6)
                            self.assertAlmostEqual(a['f'],b['f'],delta=1e-6)
                        self.assertAlmostEqual(sum(r['f']*r['x'] for r in actual),z,delta=1e-8)
                        self.assertAlmostEqual(sum(r['f']*(1-r['x']) for r in actual),1-z,delta=1e-8)

    def test_invalid_inputs_and_wrong_observable(self):
        for T,x,phase,omega in [(500,.5,'ALPHA',0),(1000,np.nan,'ALPHA',0),(1000,[],'ALPHA',0),(1000,.5,'BETA',20000),(1000,.5,'LIQUID',0),(1000,.5,'ALPHA',24001)]:
            with self.assertRaises(ValueError):homogeneous_properties(T,x,phase,omega)
        for T,z,variant in [(1000,.5,'unknown'),(1000,[.5],'I2'),(1000,-.1,'I2')]:
            with self.assertRaises(ValueError):binary_equilibrium(T,z,variant)
        state=binary_equilibrium(1000,.5,'R1')
        hmix=sum(r['f']*float(homogeneous_properties(1000,r['x'],'ALPHA',20000)['HM']) for r in state['regions'])-7000
        self.assertAlmostEqual(hmix,2810.68623619,delta=1e-5)
        self.assertGreater(abs(hmix-5000),2000)

    def test_reject_corrupted_tool_outputs(self):
        from unittest.mock import patch
        import xarray as xr
        from types import SimpleNamespace
        def prop(g,x):
            return xr.Dataset({'GM':(('points',),[g]),'X':(('points','component'),[[1-x,x]])},coords={'component':['A','B']})
        for dataset in (prop(np.nan,.5),prop(0,.4),prop(0,np.nan)):
            with patch('course.foundations.binary_family_tools.calculate',return_value=dataset):
                with self.assertRaises(RuntimeError):homogeneous_properties(1000,.5)
        def eq(names,fractions,x,energy=0):
            return SimpleNamespace(GM=np.array(energy),Phase=np.array(names),NP=np.array(fractions),
                X=xr.DataArray(np.column_stack((1-np.array(x),x)),dims=('vertex','component'),coords={'component':['A','B']}))
        for data in (eq(['ALPHA'],[-1],[.5]),eq(['UNKNOWN'],[1],[.5]),eq(['ALPHA'],[np.nan],[.5]),
                     eq(['ALPHA'],[1],[np.nan]),eq(['ALPHA'],[1],[1.1]),eq(['ALPHA'],[1],[.4]),
                     eq(['ALPHA'],[.5],[.5]),eq(['ALPHA'],[1],[.5],np.nan),eq([''],[np.nan],[np.nan])):
            with patch('course.foundations.binary_family_tools.equilibrium',return_value=data):
                with self.assertRaises(RuntimeError):binary_equilibrium(1000,.5)
        # A named zero-amount slot has no determined composition, just like an empty slot.
        data=eq(['ALPHA','BETA',''],[0,1,np.nan],[np.nan,.5,np.nan])
        with patch('course.foundations.binary_family_tools.equilibrium',return_value=data):
            state=binary_equilibrium(1000,.5)
            self.assertEqual(state['regions'],[{'phase':'BETA','x':.5,'f':1.}])

    def test_real_model_mismatch_controls(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from pycalphad import Database,equilibrium,variables as v
        from course.foundations.binary_family_tools import MODEL_PATH
        text=MODEL_PATH.read_text()
        with tempfile.TemporaryDirectory(prefix='d10-mutant-') as tmp:
            path=Path(tmp)/'wrong_reference.tdb'
            path.write_text(text.replace('13000-10*T','12000-10*T'))
            with patch('course.foundations.binary_family_tools.MODEL_PATH',path):
                wrong=homogeneous_properties(1000,.5)
            self.assertGreater(abs(float(wrong['GM'])-float(ideal_properties(1000,.5)['GM'])),499)
        wrong_interaction=homogeneous_properties(1000,.5,'ALPHA',0)
        self.assertGreater(abs(float(wrong_interaction['GM'])-float(regular_properties(1000,.5)['GM'])),4999)
        omitted=equilibrium(Database(str(MODEL_PATH)),['A','B'],['ALPHA'],
            {v.T:1000,v.P:100000,v.N:1,v.X('B'):.5},parameters={'LZERO':0},calc_opts={'pdens':2000})
        self.assertGreater(float(np.asarray(omitted.GM).squeeze())-ideal_equilibrium(1000,.5)['GM'],1900)
