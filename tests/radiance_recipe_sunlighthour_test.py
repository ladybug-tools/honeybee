import unittest
from honeybee.radiance.recipe.sunlighthours import HBSunlightHoursAnalysisRecipe
from honeybee.ladybug.core import AnalysisPeriod
from honeybee.ladybug.epw import EPW

import os


class SunlighthoursTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/recipe/sunlighthours.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.testPts = [(0, 0, 0)]
        self.testVec = [(-1, 0, 0)]
        self.sunVectors = ((-0.810513, 0.579652, -0.084093), (-0.67166, 0.702357, -0.235729),
                           (-0.487065, 0.798284, -0.354275), (-0.269301, 0.8609, -0.431657),
                           (-0.033196, 0.885943, -0.462605), (0.20517, 0.871705, -0.445013),
                           (0.429563, 0.819156, -0.380077), (0.624703, 0.731875, -0.272221),
                           (0.777301, 0.615806, -0.128788))
        self.sunVectors = []
        self.baseFolder = os.path.abspath("./tests/room/testrun")
        self.runFolder = os.path.abspath("./tests/room/testrun/test/sunlighthour")
        self.epwfile = os.path.abspath("./tests/room/test.epw")

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        files = [self.runFolder + "/" + f for f in os.listdir(self.runFolder)]

        # for f in files:
        #     # remove the file which is just created
        #     os.remove(f)

    # test default values
    def test_init_func(self):
        """Test normal init function."""
        slh = HBSunlightHoursAnalysisRecipe(self.sunVectors, self.testPts,
                                            self.testVec)

        slh.writeToFile(self.baseFolder, projectName="test")

        if slh.run():
            self.assertEqual(slh.results(), [4])

    def test_cls_method_analysis_period(self):
        """Make sure default values are set correctly."""
        location = EPW(self.epwfile).location

        ap = AnalysisPeriod(stMonth=1, endMonth=3)

        slh = HBSunlightHoursAnalysisRecipe.fromLocationAndAnalysisPeriod(
            location, ap, self.testPts, self.testVec)

        slh.writeToFile(self.baseFolder, projectName="test")

        if slh.run():
            self.assertEqual(slh.results(), [475])

    def test_cls_method_hoy(self):
        """Make sure default values are set correctly."""
        location = EPW(self.epwfile).location

        hoys = range(1, 24)

        slh = HBSunlightHoursAnalysisRecipe.fromLocationAndHoys(
            location, hoys, self.testPts, self.testVec)

        slh.writeToFile(self.baseFolder, projectName="test")

        if slh.run():
            self.assertEqual(slh.results(), [4])

if __name__ == '__main__':
    # You can run the test module from the root folder by using
    # python -m unittest -v tests.radiance_recipe_gridbased_test
    os.chdir(os.pardir)
    unittest.main()
