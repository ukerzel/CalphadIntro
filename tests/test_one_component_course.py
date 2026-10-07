"""Analytical and cross-implementation checks of the declared unary teaching model."""

import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from course.foundations import one_component_manual as manual
from course.foundations import one_component_tools as calphad


class UnaryCourseTests(unittest.TestCase):
    def test_branch_energies_and_thermodynamic_properties(self):
        temperatures = np.array([800., 900., 1000., 1100., 1200.])
        expected = np.array([[-7000,-5800],[-8000,-7400],[-9000,-9000],
                             [-10000,-10600],[-11000,-12200]])
        np.testing.assert_allclose(manual.gibbs(temperatures), expected, rtol=0, atol=1e-7)
        props = calphad.phase_properties(temperatures)
        np.testing.assert_allclose(props['GM'], expected, rtol=0, atol=1e-7)
        np.testing.assert_allclose(props['HM'], np.tile([1000,7000],(5,1)), rtol=0, atol=1e-7)
        np.testing.assert_allclose(props['SM'], np.tile([10,16],(5,1)), rtol=0, atol=1e-7)

    def test_equilibrium_balance_and_invariant_degeneracy(self):
        for t in [800., 900., 1000., 1100., 1200.]:
            expected = min(1000-10*t, 7000-16*t)
            for run in [manual.equilibrium_at, calphad.equilibrium_at]:
                with self.subTest(t=t, run=run):
                    result = run(t)
                    self.assertAlmostEqual(result['GM'], expected, delta=1e-6)
                    fractions = result['fractions']
                    self.assertAlmostEqual(sum(fractions.values()), 1, delta=1e-8)
                    self.assertTrue(all(-1e-8 <= f <= 1+1e-8 for f in fractions.values()))
                    reconstructed = fractions.get('SOLID',0)*(1000-10*t)+fractions.get('LIQUID',0)*(7000-16*t)
                    self.assertAlmostEqual(reconstructed, result['GM'], delta=1e-6)
                    if t != 1000:
                        stable = 'SOLID' if t<1000 else 'LIQUID'
                        self.assertAlmostEqual(fractions.get(stable,0),1,delta=1e-8)
        for f in [0, .2, .5, 1]:
            self.assertAlmostEqual((1-f)*(-9000)+f*(-9000), -9000, delta=1e-7)
        self.assertAlmostEqual(manual.transition_temperature(),1000,delta=1e-8)
        # A common reference shift leaves the crossing and preferred phase unchanged.
        values=manual.gibbs([900,1000,1100])
        np.testing.assert_array_equal(np.diff(values+500,axis=1),np.diff(values,axis=1))

    def test_invalid_domains_and_failed_optimizer(self):
        for bad in [[], [900,np.nan], np.inf, 799., 1201., [[900.]]]:
            for run in [manual.gibbs, calphad.phase_properties]:
                with self.subTest(bad=bad,run=run), self.assertRaises(ValueError): run(bad)
        for run in [manual.equilibrium_at,calphad.equilibrium_at]:
            with self.assertRaises(ValueError): run([900.,1000.])
        with patch.object(manual,'linprog',return_value=SimpleNamespace(success=False,message='forced failure')):
            with self.assertRaisesRegex(RuntimeError,'forced failure'): manual.equilibrium_at(900.)

    def test_record_and_figure_are_reproducible(self):
        record=calphad.comparison_record()
        self.assertEqual(record['component'],'A')
        self.assertEqual(len(record['rows']),5)
        self.assertEqual(record['transition_temperature_K'],1000.)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'figure.svg'
            manual.save_figure(path)
            self.assertIn('<svg',path.read_text())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            runpy.run_path(manual.__file__, run_name='__main__')
        self.assertIn('1000.000000',output.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            runpy.run_path(calphad.__file__, run_name='__main__')
        self.assertEqual(json.loads(output.getvalue()),record)


if __name__ == '__main__':
    unittest.main()
