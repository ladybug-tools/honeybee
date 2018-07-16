import unittest
from honeybee.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.epw import EPW

import os


class SunlighthoursTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/recipe/sunlighthours.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.test_pts = [(0, 0, 0)]
        self.test_vec = [(-1, 0, 0)]
        self.sun_vectors = (
            (-0.810513, 0.579652, -0.084093), (-0.67166, 0.702357, -0.235729),
            (-0.487065, 0.798284, -0.354275), (-0.269301, 0.8609, -0.431657),
            (-0.033196, 0.885943, -0.462605), (0.20517, 0.871705, -0.445013),
            (0.429563, 0.819156, -0.380077), (0.624703, 0.731875, -0.272221),
            (0.777301, 0.615806, -0.128788))
        self.sun_vectors = []
        self.base_folder = os.path.abspath("tests/room/testrun")
        self.run_folder = os.path.abspath("tests/room/testrun/test/sunlighthour")
        self.epwfile = os.path.abspath("tests/room/test.epw")

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        files = [self.run_folder + "/" + f for f in os.listdir(self.run_folder)]

        for f in files:
            try:
                # remove the file which is just created
                os.remove(f)
            except Exception:
                pass
    # test default values

    def test_init_func(self):
        """Test normal init function."""
        slh = SolarAccessGridBased(self.sun_vectors, self.test_pts, self.test_vec)

        slh.write_to_file(self.base_folder, project_name="test")

        if slh.run():
            assert slh.results() == [4]

    def test_cls_method_analysis_period(self):
        """Make sure default values are set correctly."""
        location = EPW(self.epwfile).location

        ap = AnalysisPeriod(st_month=1, end_month=3)

        slh = SolarAccessGridBased.fromLocationAndAnalysisPeriod(
            location, ap, self.test_pts, self.test_vec)

        slh.write_to_file(self.base_folder, project_name="test")

        if slh.run():
            assert slh.results() == [475]

    def test_cls_method_hoy(self):
        """Make sure default values are set correctly."""
        location = EPW(self.epwfile).location

        hoys = range(1, 24)

        slh = SolarAccessGridBased.fromLocationAndHoys(
            location, hoys, self.test_pts, self.test_vec)

        slh.write_to_file(self.base_folder, project_name="test")

        if slh.run():
            assert slh.results() == [4]


if __name__ == '__main__':
    # You can run the test module from the root folder by using
    # python -m unittest -v tests.radiance_recipe_gridbased_test
    os.chdir(os.pardir)
    unittest.main()
