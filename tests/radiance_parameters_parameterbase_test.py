import unittest
from honeybee.radiance.parameters._parametersBase import RadianceParameters
from honeybee.radiance.datatype import RadianceNumber, RadianceValue


class ParametersTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/parameters/_parametersBase.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        class CustomRP(RadianceParameters):
            ab = RadianceNumber('ab', 'ambient bounces', defaultValue=15)
            ad = RadianceValue('ad', 'ambient divisions')

            def __init__(self, ab=None, ad=None):
                """Init radiance paramters."""
                RadianceParameters.__init__(self)

                self.ab = ab
                self.ad = ad

                # add paramter names to dynamic keys
                self.dynamicKeys = ['ab', 'ad']

        self.rp = CustomRP(ad=12)

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        self.assertEqual(self.rp.toRadString(), '-ab 15 -ad 12')

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        pass
        # more tests here

    # test for specific cases
    def test_import_from_string(self):
        """Test import parameters form a string."""
        self.rp.importParameterValuesFromString('-dj   20  -fo -dc 1 -ab 16')
        self.assertTrue(self.rp.toRadString() == '-ab 16 -ad 12 -dj 20 -fo -dc 1')

    def test_update_value(self):
        """Make sure values updates correctly."""
        self.rp.ad = 40
        self.assertEqual(self.rp.toRadString(), '-ab 15 -ad 40')

    def test_add_value_by_name_value(self):
        """Add a new parameter by name and value."""
        self.rp.addParamterByNameAndValue('aa', '0.0')
        self.assertEqual(self.rp.toRadString(), '-ab 15 -ad 12 -aa 0.0')
        self.assertEqual(self.rp.aa, '0.0')

    def test_remove_static_parameter(self):
        """Remove a static a key after adding the parameter."""
        self.rp.addParamterByNameAndValue('aa', '0.5')
        # make sure value is added.
        self.assertEqual(self.rp.toRadString(), '-ab 15 -ad 12 -aa 0.5')
        # now remove the value
        self.rp.removeParameter('aa')
        self.assertEqual(self.rp.toRadString(), '-ab 15 -ad 12')

    def test_remove_dynamic_parameter(self):
        """Remove a dynamic key."""
        self.rp.removeParameter('ab')
        self.assertEqual(self.rp.toRadString(), '-ad 12')

    def test_remove_all_parameters(self):
        """Remove all parameters."""
        self.rp.removeParameters()
        self.assertEqual(self.rp.toRadString(), "")


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
