import unittest
from honeybee.radiance.view import View


class ViewTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/view.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.v = View()

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        self.assertEqual(self.v.viewPoint, (0, 0, 0))
        self.assertEqual(self.v.viewDirection, (0, 0, 1))
        self.assertEqual(self.v.viewUpVector, (0, 1, 0))
        # more tests here

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        pass
        # more tests here

    # test for specific cases
    def test_fish_eye_view(self):
        """vh and vv should set to 180 for fisheye view."""
        self.v.viewType = 1
        self.assertEqual(self.v.viewHSize, 180)
        self.assertEqual(self.v.viewVSize, 180)

    def test_updating_view(self):
        """Change location and direction."""
        self.v.viewPoint = (0, 0, 10)
        self.v.viewDirection = (0, 0, -1)
        self.assertEqual(self.v.viewPoint, [0, 0, 10])
        self.assertEqual(self.v.viewDirection, [0, 0, -1])


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
