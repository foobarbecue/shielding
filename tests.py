from shielding import shielding
import unittest

class PbrTest(unittest.TestCase):
	def test_shielding_factors(self):
		"""Verify that the shielding factors match Greg Balco's code at http://hess.ess.washington.edu/shielding/"""
		pbrs = shielding.ShieldingScene(mesh_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv01_everything.stl",
    							samples_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv2_samples.csv")
		self.assertAlmostEqual(0.8663, pbrs.samples[0].shielding_factor, delta=0.1)
		self.assertAlmostEqual(0.5308, pbrs.samples[1].shielding_factor, delta=0.1)
		self.assertAlmostEqual(0.5321, pbrs.samples[2].shielding_factor, delta=0.1)
