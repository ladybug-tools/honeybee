import unittest
from honeybee.radiance.datatype import RadiancePath, RadianceNumber, \
    RadianceBoolFlag, RadianceTuple, RadianceValue


class DataTypeTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/view.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        class RadTest(object):
            # create an attribute for each type
            ab = RadianceNumber('ab', 'ambinent bounces', valid_range=None,
                                accepted_inputs=None, num_type=int,
                                check_positive=True, default_value=None)
            ad = RadianceNumber('ad', 'ambinent divisions', valid_range=[1, 128],
                                accepted_inputs=None, num_type=None,
                                check_positive=True, default_value=None)
            d = RadianceBoolFlag('d', 'sun mtx only', default_value=None,
                                 is_dual_sign=False)
            i = RadianceBoolFlag('I', 'illuminance', default_value=None,
                                 is_dual_sign=True)

            c = RadianceTuple('C', 'color', default_value=None, num_type=int,
                              valid_range=[0, 255])

            o = RadianceValue('o', 'output format', default_value=None,
                              accepted_inputs=('f', 'd'), isJoined=True)

            weaFile = RadiancePath('weaFile', 'Weather File Path', relativePath=None,
                                   checkExists=False, extension='.wea')

            def __init__(self):
                pass

            def to_rad_string(self):
                _radString = " ".join(
                    [self.ab.to_rad_string(), self.ad.to_rad_string(),
                     self.d.to_rad_string(), self.i.to_rad_string(),
                     self.c.to_rad_string(), self.o.to_rad_string()]) + " > " + \
                    self.wea_file.to_rad_string()

                return _radString.strip()

        class RadTestWithDefaults(RadTest):
            # create an attribute for each type
            ab = RadianceNumber('ab', 'ambinent bounces', valid_range=None,
                                accepted_inputs=None, num_type=int,
                                check_positive=True, default_value=2)
            ad = RadianceNumber('ad', 'ambinent divisions', valid_range=[1, 128],
                                accepted_inputs=None, num_type=None,
                                check_positive=True, default_value=5)

            d = RadianceBoolFlag('d', 'sun mtx only', default_value=False,
                                 is_dual_sign=False)
            i = RadianceBoolFlag('I', 'illuminance', default_value=False,
                                 is_dual_sign=True)

            c = RadianceTuple('C', 'color', default_value=(250, 250, 250),
                              num_type=int, valid_range=[0, 255])

            o = RadianceValue('o', 'output format', default_value='f',
                              accepted_inputs=('f', 'd'), isJoined=True)

            def __init__(self):
                self.wea_file = "c:/ladybug/test.wea"

        self.rad = RadTest()
        self.rad_with_def = RadTestWithDefaults()

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        assert self.rad_with_def.to_rad_string() == \
                         "-ab 2 -ad 5  -I -C 250 250 250 -of > " \
                         "c:/ladybug/test.wea"
        assert self.rad_with_def.ab == 2
        assert self.rad_with_def.ad == 5
        assert self.rad_with_def.c == (250, 250, 250)
        assert self.rad_with_def.wea_file == "c:/ladybug/test.wea"
        assert self.rad_with_def.i == False
        assert self.rad_with_def.d == False
        assert self.rad_with_def.o == 'f'

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        try:
            self.rad_with_def.c = 200
        except ValueError as e:
            assert type(e) == ValueError
            assert self.rad_with_def.c == (250, 250, 250)

        try:
            self.rad_with_def.ad = 200
        except ValueError as e:
            assert type(e) == ValueError
            # This is quite strange!
            # self.assertEqual(self.rad_with_def.ad, 50)

    # test for specific cases
    def test_none_values(self):
        """Make sure values with None will return empty string as radianceString."""
        assert self.rad.to_rad_string() == ">"

    def test_setting_up_values(self):
        """Make sure values will be set as expected."""
        self.rad.ab = 2
        assert self.rad.ab == 2

        self.rad.ad = 5
        assert self.rad.ad == 5

        self.rad.c = (0, 0, 0)
        assert self.rad.c == (0, 0, 0)

        self.rad.wea_file = "c:/ladybug/test.wea"
        assert self.rad.wea_file == "c:/ladybug/test.wea"

        self.rad.d = True
        assert self.rad.d == True

        self.rad.i = False
        assert self.rad.i == False

        self.rad.o = 'f'
        assert self.rad.o == 'f'

    def test_updating_values(self):
        """Make sure values will be updated as expected."""
        self.rad_with_def.ab = 12
        assert self.rad_with_def.ab == 12

        self.rad_with_def.ad = 15
        assert self.rad_with_def.ad == 15

        self.rad_with_def.c = (10, 10, 10)
        assert self.rad_with_def.c == (10, 10, 10)

        self.rad_with_def.wea_file = "c:/ladybug/test2.wea"
        assert self.rad_with_def.wea_file == "c:/ladybug/test2.wea"

        self.rad_with_def.d = False
        assert self.rad_with_def.d == False

        self.rad_with_def.i = True
        assert self.rad_with_def.i == True

        self.rad_with_def.o = 'd'
        assert self.rad_with_def.o == 'd'

    def test_to_rad_string_method(self):
        """Check to_rad_string method for all the types."""
        assert self.rad_with_def.ab.to_rad_string() == '-ab 2'
        assert self.rad_with_def.ad.to_rad_string() == '-ad 5'
        assert self.rad_with_def.c.to_rad_string() == '-C 250 250 250'
        assert self.rad_with_def.wea_file.to_rad_string() == \
                         "c:/ladybug/test.wea"
        assert self.rad_with_def.i.to_rad_string() == '-I'
        assert self.rad_with_def.d.to_rad_string() == ''
        assert self.rad_with_def.o.to_rad_string() == '-of'

    def test_value_type_for_numbers(self):
        """Check float values will be converted to intger for int value type."""
        self.rad_with_def.ab = 2.45
        assert self.rad_with_def.ab == 2

        self.rad_with_def.ab = 2.99
        assert self.rad_with_def.ab == 2

    def test_relative_path(self):
        """Check relative path."""
        assert self.rad_with_def.wea_file.to_rad_string() == \
                         "c:/ladybug/test.wea"
        self.rad_with_def.wea_file.relPath = "c:/ladybug/test/gridbased"
        assert self.rad_with_def.wea_file.to_rad_string() == \
                         r"../../test.wea"


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
