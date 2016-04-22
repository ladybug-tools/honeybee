import unittest
from honeybee.radiance.parameters._advancedparametersbase import AdvancedRadianceParameters
from honeybee.radiance.parameters._frozen import frozen


class AdvancedParametersTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/parameters/_advancedparametersbase.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        @frozen
        class CustomParameters(AdvancedRadianceParameters):
            pass

        self.rp = CustomParameters()

        # add parameters
        self.rp.addRadianceNumber('ab', 'ambient bounces')
        self.rp.ab = 20
        self.rp.addRadianceValue('o', 'o f', isJoined=True)
        self.rp.o = 'f'
        self.rp.addRadianceTuple('c', 'color', numType=int)
        self.rp.c = (0, 0, 254)
        self.rp.addRadianceBoolFlag('I', 'irradiance switch', isDualSign=True)
        self.rp.I = True
        self.rp.addRadiancePath('wea', 'wea file')
        self.rp.wea = 'c:\\ladybug\\test.wea'

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        for v in ('-ab 20', '-of', '-c 0 0 254', '+I', 'c:\\ladybug\\test.wea'):
            self.assertIn(v, self.rp.toRadString())

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
        for v in ('-ab 10', '-od', '-c 0 0 0', '-I', 'c:\\ladybug\\test.wea'):
            self.assertIn(v, self.rp.toRadString())


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
