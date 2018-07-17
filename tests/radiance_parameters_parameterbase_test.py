import unittest
from honeybee.radiance.parameters._parametersbase import RadianceParameters
from honeybee.radiance.parameters._frozen import frozen
from honeybee.radiance.datatype import RadianceNumber, RadianceValue


class ParametersTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/parameters/_parametersbase.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        @frozen
        class CustomRP(RadianceParameters):
            ambient_bounces = RadianceNumber('ab', 'ambient bounces', default_value=15)
            ambient_divisions = RadianceValue('ad', 'ambient divisions')

            def __init__(self, ab=None, ad=None):
                """Init radiance paramters."""
                RadianceParameters.__init__(self)

                self.ambient_bounces = ab
                self.ambient_divisions = ad

                # add paramter names to dynamic keys
                self.add_default_parameter_name('ambient_bounces', 'ab')
                self.add_default_parameter_name('ambient_divisions', 'ad')

        self.rp = CustomRP(ad=12)

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        for v in ('-ab 15', '-ad 12'):
            assert v in self.rp.to_rad_string()

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        pass
        # more tests here

    # test for specific cases
    def test_import_from_string(self):
        """Test import parameters form a string."""
        self.rp.import_parameter_values_from_string('-dj   20  -fo -dc 1 -ab 16')

        for v in ('-ab 16', '-ad 12', '-dj 20', '-fo', '-dc 1'):
            assert v in self.rp.to_rad_string()

    def test_update_value(self):
        """Make sure values updates correctly."""
        self.rp.ambient_divisions = 40
        for v in ('-ab 15', '-ad 40'):
            assert v in self.rp.to_rad_string()

    def test_add_value_by_name_value(self):
        """Add a new parameter by name and value."""
        self.rp.add_additional_parameter_by_name_and_value('aa', '0.0')
        for v in ('-ab 15', '-ad 12', '-aa 0.0'):
            assert v in self.rp.to_rad_string()
        assert self.rp.aa == '0.0'

    def test_remove_static_parameter(self):
        """Remove a static a key after adding the parameter."""
        self.rp.add_additional_parameter_by_name_and_value('aa', '0.5')
        # make sure value is added.
        for v in ('-ab 15', '-ad 12', '-aa 0.5'):
            assert v in self.rp.to_rad_string()
        # now remove the value
        self.rp.remove_parameter('aa')
        for v in ('-ab 15', '-ad 12'):
            assert v in self.rp.to_rad_string()

    def test_remove_dynamic_parameter(self):
        """Remove a dynamic key."""
        self.rp.remove_parameter('ab')
        assert self.rp.to_rad_string() == '-ad 12'

    def test_remove_all_parameters(self):
        """Remove all parameters."""
        self.rp.remove_parameters()
        assert self.rp.to_rad_string() == ""


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
