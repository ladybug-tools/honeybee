import unittest
from honeybee.radiance.parameters._advancedparametersbase import \
    AdvancedRadianceParameters
from honeybee.radiance.parameters._frozen import frozen
import os


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
        self.rp.add_radiance_value('o', 'o f', is_joined=True)
        self.rp.o = 'f'
        self.rp.add_radiance_tuple('c', 'color', num_type=int)
        self.rp.c = (0, 0, 254)
        self.rp.add_radiance_bool_flag('I', 'irradiance switch', is_dual_sign=True)
        self.rp.I = True
        self.rp.add_radiance_path('wea', 'wea file')
        self.rp.wea = 'tests/room/testrun/test.wea'

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        for v in ('-ab 20', '-of', '-c 0 0 254', '+I', 'tests/room/testrun/test.wea'):
            assert os.path.normpath(v) in self.rp.to_rad_string()

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
        for v in ('-ab 10', '-od', '-c 0 0 0', '-I', 'tests/room/testrun/test.wea'):
            assert os.path.normpath(v) in self.rp.to_rad_string()


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
