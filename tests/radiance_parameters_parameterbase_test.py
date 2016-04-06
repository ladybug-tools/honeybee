import unittest
from honeybee.radiance.parameters._parametersbase import RadianceParameters
from honeybee.radiance.datatype import RadianceNumber, RadianceValue


class ParametersTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/parameters/_parametersbase.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        class CustomRP(RadianceParameters):
            ambientBounces = RadianceNumber('ab', 'ambient bounces', defaultValue=15)
            ambientDivisions = RadianceValue('ad', 'ambient divisions')

            def __init__(self, ab=None, ad=None):
                """Init radiance paramters."""
                RadianceParameters.__init__(self)

                self.ambientBounces = ab
                self.ambientDivisions = ad

                # add paramter names to dynamic keys
                self.addDefaultParameterName('ambientBounces', 'ab')
                self.addDefaultParameterName('ambientDivisions', 'ad')

        self.rp = CustomRP(ad=12)

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        for v in ('-ab 15', '-ad 12'):
            self.assertIn(v, self.rp.toRadString())

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        pass
        # more tests here

    # test for specific cases
    def test_import_from_string(self):
        """Test import parameters form a string."""
        self.rp.importParameterValuesFromString('-dj   20  -fo -dc 1 -ab 16')

        for v in ('-ab 16', '-ad 12', '-dj 20', '-fo', '-dc 1'):
            self.assertIn(v, self.rp.toRadString())

    def test_update_value(self):
        """Make sure values updates correctly."""
        self.rp.ambientDivisions = 40
        for v in ('-ab 15', '-ad 40'):
            self.assertIn(v, self.rp.toRadString())

    def test_add_value_by_name_value(self):
        """Add a new parameter by name and value."""
        self.rp.addAdditionalParameterByNameAndValue('aa', '0.0')
        for v in ('-ab 15', '-ad 12', '-aa 0.0'):
            self.assertIn(v, self.rp.toRadString())
        self.assertEqual(self.rp.aa, '0.0')

    def test_remove_static_parameter(self):
        """Remove a static a key after adding the parameter."""
        self.rp.addAdditionalParameterByNameAndValue('aa', '0.5')
        # make sure value is added.
        for v in ('-ab 15', '-ad 12', '-aa 0.5'):
            self.assertIn(v, self.rp.toRadString())
        # now remove the value
        self.rp.removeParameter('aa')
        for v in ('-ab 15', '-ad 12'):
            self.assertIn(v, self.rp.toRadString())

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
