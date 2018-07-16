import unittest
from honeybee.radiance.parameters._advancedparametersbase import \
    AdvancedRadianceParameters
from honeybee.radiance.parameters._frozen import frozen

# TODO: Change all 'c:/ladybug/*' to local file in tests directory
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
        self.rp.add_radiance_number('ab', 'ambient bounces')
        self.rp.ab = 20
        self.rp.add_radiance_value('o', 'o f', isJoined=True)
        self.rp.o = 'f'
        self.rp.add_radiance_tuple('c', 'color', numType=int)
        self.rp.c = (0, 0, 254)
        self.rp.add_radiance_bool_flag('I', 'irradiance switch', isDualSign=True)
        self.rp.I = True
        self.rp.add_radiance_path('wea', 'wea file')
        self.rp.wea = 'c:/ladybug/test.wea'

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        for v in ('-ab 20', '-of', '-c 0 0 254', '+I', 'c:/ladybug/test.wea'):
            assert v in self.rp.to_rad_string()

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
        for v in ('-ab 10', '-od', '-c 0 0 0', '-I', 'c:/ladybug/test.wea'):
            assert v in self.rp.to_rad_string()


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
