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
            ab = RadianceNumber('ab', 'ambinent bounces', validRange=None,
                                acceptedInputs=None, numType=int,
                                checkPositive=True, defaultValue=None)
            ad = RadianceNumber('ad', 'ambinent divisions', validRange=[1, 128],
                                acceptedInputs=None, numType=None,
                                checkPositive=True, defaultValue=None)
            d = RadianceBoolFlag('d', 'sun mtx only', defaultValue=None, isDualSign=False)
            i = RadianceBoolFlag('I', 'illuminance', defaultValue=None, isDualSign=True)

            c = RadianceTuple('C', 'color', defaultValue=None, numType=int,
                                     validRange=[0, 255])

            o = RadianceValue('o', 'output format', defaultValue=None,
                              acceptedInputs=('f', 'd'), isJoined=True)

            weaFile = RadiancePath('weaFile', 'Weather File Path', relativePath=None,
                                   checkExists=False, extension='.wea')

            def __init__(self):
                pass

            def toRadString(self):
                _radString = " ".join(
                    [self.ab.toRadString(), self.ad.toRadString(),
                     self.d.toRadString(), self.i.toRadString(),
                     self.c.toRadString(), self.o.toRadString()]) + " > " + \
                     self.weaFile.toRadString()

                return _radString.strip()

        class RadTestWithDefaults(RadTest):
            # create an attribute for each type
            ab = RadianceNumber('ab', 'ambinent bounces', validRange=None,
                                acceptedInputs=None, numType=int,
                                checkPositive=True, defaultValue=2)
            ad = RadianceNumber('ad', 'ambinent divisions', validRange=[1, 128],
                                acceptedInputs=None, numType=None,
                                checkPositive=True, defaultValue=5)

            d = RadianceBoolFlag('d', 'sun mtx only', defaultValue=False, isDualSign=False)
            i = RadianceBoolFlag('I', 'illuminance', defaultValue=False, isDualSign=True)

            c = RadianceTuple('C', 'color', defaultValue=(250, 250, 250),
                                     numType=int, validRange=[0, 255])

            o = RadianceValue('o', 'output format', defaultValue='f',
                              acceptedInputs=('f', 'd'), isJoined=True)

            def __init__(self):
                self.weaFile = "c:\ladybug\\test.wea"

        self.rad = RadTest()
        self.radWDef = RadTestWithDefaults()

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Make sure default values are set correctly."""
        self.assertEqual(self.radWDef.toRadString(),
                         "-ab 2 -ad 5  -I -C 250 250 250 -of > c:\\ladybug\\test.wea")
        self.assertEqual(self.radWDef.ab, 2)
        self.assertEqual(self.radWDef.ad, 5)
        self.assertEqual(self.radWDef.c, (250, 250, 250))
        self.assertEqual(self.radWDef.weaFile, "c:\ladybug\\test.wea")
        self.assertEqual(self.radWDef.i, False)
        self.assertEqual(self.radWDef.d, False)
        self.assertEqual(self.radWDef.o, 'f')

    # test for assertion and exceptions
    def test_assertions_exceptions(self):
        """Make sure the class catches wrong inputs, etc."""
        try:
            self.radWDef.c = 200
        except ValueError as e:
            self.assertEqual(type(e), ValueError)
            self.assertEqual(self.radWDef.c, (250, 250, 250))

        try:
            self.radWDef.ad = 200
        except ValueError as e:
            self.assertEqual(type(e), ValueError)
            # This is quite strange!
            # self.assertEqual(self.radWDef.ad, 50)

    # test for specific cases
    def test_None_values(self):
        """Make sure values with None will return empty string as radianceString."""
        self.assertEqual(self.rad.toRadString(), ">")

    def test_setting_up_values(self):
        """Make sure values will be set as expected."""
        self.rad.ab = 2
        self.assertEqual(self.rad.ab, 2)

        self.rad.ad = 5
        self.assertEqual(self.rad.ad, 5)

        self.rad.c = (0, 0, 0)
        self.assertEqual(self.rad.c, (0, 0, 0))

        self.rad.weaFile = "c:\ladybug\\test.wea"
        self.assertEqual(self.rad.weaFile, "c:\ladybug\\test.wea")

        self.rad.d = True
        self.assertEqual(self.rad.d, True)

        self.rad.i = False
        self.assertEqual(self.rad.i, False)

        self.rad.o = 'f'
        self.assertEqual(self.rad.o, 'f')

    def test_updating_values(self):
        """Make sure values will be updated as expected."""
        self.radWDef.ab = 12
        self.assertEqual(self.radWDef.ab, 12)

        self.radWDef.ad = 15
        self.assertEqual(self.radWDef.ad, 15)

        self.radWDef.c = (10, 10, 10)
        self.assertEqual(self.radWDef.c, (10, 10, 10))

        self.radWDef.weaFile = "c:\ladybug\\test2.wea"
        self.assertEqual(self.radWDef.weaFile, "c:\ladybug\\test2.wea")

        self.radWDef.d = False
        self.assertEqual(self.radWDef.d, False)

        self.radWDef.i = True
        self.assertEqual(self.radWDef.i, True)

        self.radWDef.o = 'd'
        self.assertEqual(self.radWDef.o, 'd')

    def test_toRadString_method(self):
        """Check toRadString method for all the types."""
        self.assertEqual(self.radWDef.ab.toRadString(), '-ab 2')
        self.assertEqual(self.radWDef.ad.toRadString(), '-ad 5')
        self.assertEqual(self.radWDef.c.toRadString(), '-C 250 250 250')
        self.assertEqual(self.radWDef.weaFile.toRadString(), "c:\ladybug\\test.wea")
        self.assertEqual(self.radWDef.i.toRadString(), '-I')
        self.assertEqual(self.radWDef.d.toRadString(), '')
        self.assertEqual(self.radWDef.o.toRadString(), '-of')

    def test_value_type_for_numbers(self):
        """Check float values will be converted to intger for int value type."""
        self.radWDef.ab = 2.45
        self.assertEqual(self.radWDef.ab, 2)

        self.radWDef.ab = 2.99
        self.assertEqual(self.radWDef.ab, 2)

    def test_relative_path(self):
        """Check relative path."""
        self.assertEqual(self.radWDef.weaFile.toRadString(), "c:\ladybug\\test.wea")
        self.radWDef.weaFile.relPath = "c:\\ladybug\\test\\gridbased"
        self.assertEqual(self.radWDef.weaFile.toRadString(), r"..\..\test.wea")


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
