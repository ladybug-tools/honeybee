import unittest
from honeybee.radiance.parameters._advancedparametersbase import AdvancedRadianceParameters


class AdvancedParametersTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/parameters/_advancedparametersbase.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        class CustomParameters(AdvancedRadianceParameters):
            pass

        self.rp = CustomParameters()

        # add parameters
        self.rp.addRadianceNumber('ab', 'ambient bounces', defaultValue=20)
        self.rp.addRadianceValue('o', 'o f', defaultValue='f', isJoined=True)
        self.rp.addRadianceNumericTuple('c', 'color', defaultValue=(0, 0, 254), numType=int)
        self.rp.addRadianceBoolFlag('I', 'irradiance switch', defaultValue=True, isDualSign=True)
        self.rp.addRadiancePath('wea', 'wea file')
        self.rp.wea = 'c:\\ladybug\\test.wea'

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        self.assertEqual(self.rp.toRadString(), '-ab 20 -of -c 0 0 254 +I c:\\ladybug\\test.wea')

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        pass
        # more tests here

    def test_update_values(self):
        """Make sure values updates correctly."""
        self.rp.ab = 10
        self.rp.o = 'd'
        self.rp.c = (0, 0, 0)
        self.rp.I = False
        self.assertEqual(self.rp.toRadString(), '-ab 10 -od -c 0 0 0 -I c:\\ladybug\\test.wea')


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
