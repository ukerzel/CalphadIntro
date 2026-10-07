"""Detect line-fit, shared-area and boundary-site normalization mistakes."""
import unittest

import numpy as np

from course.materials.boundaries import ni_twin as lesson


class NiTwinChecks(unittest.TestCase):
    def test_recovers_known_invented_line_and_entropy_sign(self):
        t = np.array([100., 300., 500., 800.])
        fitted = lesson.fit_curve(t, 0.08-2e-5*t)
        self.assertAlmostEqual(fitted["A_J_per_m2"], 0.08, delta=1e-8)
        self.assertAlmostEqual(fitted["B_J_per_m2_K"], -2e-5, delta=1e-12)
        self.assertLess(np.max(np.abs(fitted["residual_J_per_m2"])), 1e-8)
        self.assertGreater(-fitted["B_J_per_m2_K"], 0)

    def test_residual_accounting_with_nonzero_data_deviations(self):
        t = np.array([100., 200., 300.])
        fitted = lesson.fit_curve(t, np.array([0.08, 0.071, 0.06]))
        expected = np.array([1/3000, -1/1500, 1/3000])  # Fit minus reading.
        np.testing.assert_allclose(fitted["residual_J_per_m2"], expected,
                                   atol=1e-8, rtol=0)
        self.assertAlmostEqual(fitted["sse_J2_per_m4"], expected @ expected, delta=1e-12)

    def test_shared_faces_volume_and_two_plane_site_count_by_hand(self):
        g = lesson.geometry(0.352e-9, 100e-9)
        expected_volume = lesson.AVOGADRO*(0.352e-9)**3/4
        self.assertAlmostEqual(g["molar_volume_m3_per_mol"], expected_volume, delta=1e-15)
        # Six cube faces, each shared by two grains: three faces per volume.
        expected_area = 3*expected_volume/100e-9
        self.assertAlmostEqual(g["area_m2_for_one_mol_NI"], expected_area, delta=1e-8)
        expected_density = 2*4/(np.sqrt(3)*(0.352e-9)**2)/lesson.AVOGADRO
        self.assertAlmostEqual(g["site_density_mol_per_m2"], expected_density, delta=1e-12)
        self.assertAlmostEqual(g["boundary_NI_mol"], expected_density*expected_area, delta=1e-10)
        self.assertAlmostEqual(g["bulk_NI_mol"]+g["boundary_NI_mol"], 1, delta=1e-10)

    def test_offset_conserves_NI_and_total_area_energy(self):
        g = lesson.geometry(0.352e-9, 100e-9)
        out = lesson.cell_energy(-17000, 0.06, g)
        self.assertAlmostEqual(out["epsilon_J_per_mol_sites"]*g["site_density_mol_per_m2"],
                               0.06, delta=1e-8)
        expected = g["area_m2_for_one_mol_NI"]*0.06
        self.assertAlmostEqual(out["excess_total_J"], expected, delta=1e-7)
        self.assertAlmostEqual(out["cell_G_J"], -17000+expected, delta=1e-7)
        self.assertAlmostEqual(lesson.cell_energy(-17000, 0, g)["cell_G_J"],
                               -17000, delta=1e-7)

    def test_invalid_fit_and_impossible_site_allocation_rejected(self):
        for t, gamma in [([200, 200], [0.08, 0.06]), ([100, 200], [0.06]),
                         ([100, np.nan], [0.08, 0.06]), ([100, 200], [0.08, -0.06])]:
            with self.assertRaises(ValueError):
                lesson.fit_curve(t, gamma)
        for a, d in [(0, 100e-9), (0.352e-9, np.nan), (0.352e-9, 0.1e-9)]:
            with self.assertRaises(ValueError):
                lesson.geometry(a, d)


if __name__ == "__main__":
    unittest.main()
