import unittest
from honeybee.radiance.sky.certainIlluminance \
    import CertainIlluminanceLevel as radSky
from honeybee.radiance.analysisgrid import AnalysisGrid
from honeybee.radiance.recipe.pointintime.gridbased import GridBased

import pytest


class GridbasedTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/recipe/gridbased.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        # create a sky to be able to initiate gridbased module
        sky = radSky(1000)
        points = [(0,0,0),(1,1,0),(3,2,0)]
        analysis_grid = AnalysisGrid.from_points_and_vectors(points)
        self.rp = GridBased(sky, analysis_grids = [analysis_grid])

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        assert self.rp.simulation_type == 0, \
                         "Default simulation type is changed from 0!"
        # more tests here

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        # results should not be available before the analysis is ran
        with pytest.raises(
            TypeError):
            self.rp.results("Results should not be available unless the analysis is executed!")
        # more tests here

    # test for specific cases
    def test_single_point_input(self):
        """A single point should be converted to a single test group."""
        pass
        # The methods below don't exist anymore.
        # self.rp.updatepoint_groups([0, 0, 0])
        # assert self.rp.num_of_point_groups == 1, \
        #                  "Failed to convert single test point to a group!"


if __name__ == '__main__':
    # You can run the test module from the root folder by using
    # python -m unittest -v tests.radiance_recipe_gridbased_test
    unittest.main()
