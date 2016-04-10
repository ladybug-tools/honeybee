# coding=utf-8
from _advancedparametersbase import AdvancedRadianceParameters


class GenskyParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    Read more:
    http://radsite.lbl.gov/radiance/man_html/gensky.1.html


    Attributes:
        altitudeAzimuth: [-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime.
        sunnySky: [-s|+s] A boolean value to generate sunny sky with or without
            sun. Set to True to generate a sunnny sky with sun, Fasle to generate
            a sunny sky without sun (Default: None)
        cloudySky: [-c] A boolean value to generate cloudy sky
        intermSky: [-i|+i] A boolean value to generate intermediate sky with or
            without sun. Set to True to generate an intermediate sky with sun,
            Fasle to generate a intermediate sky without sun (Default: None)
        uniformCloudySky: [-u] A boolean value to generate Uniform cloudy sky.
        groundReflect: [-g rfl] A float number to indicate ground reflectance
        zenithBright: [-b brt] A float number to indicate zenith brightness in
            watts/steradian/meter-sq.
        zenithBrightHorzDiff: [-B irrad] A float number to indicate zenith
            brightness from horizontal diffuse irradiance in watts/meter-sq.
        solarRad: [-r rad] A float number to indicate solar radiance in
        watts/steradians/meter-sq.
        solarRadHorzDiff: [-R irrad] A float number to indicate solar radiance
            from horizontal direct irradiance in watts/meter-sq.
        turbidity: [-t trb] A float number to indicate turbidity.
        latitude: [-a lat] A float number to indicate site altitude. Negative
            angle indicates south latitude.
        longitude: [-o lon] A float number to indicate site latitude. Negative
            angle indicates east longitude.
        meridian: [-m mer] A float number to indicate site meridian west of
        Greenwich.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        gnskyparam = GenskyParameters()

        # check the current values
        print gnskyparam.toRadString()
        > -g 0.5


        # set altitude and azimuth angle values
        gnsky.altitudeAzimuth = (12,31)

        #check the new values added.
        print gnskyparam.toRadString()
        > -g 0.5 -ang 12.0 31.0

    """

    def __init__(self, altitudeAzimuth=None, sunnySky=None,
                 cloudySky=None, intermSky=None, uniformCloudySky=None,
                 groundReflect=None, zenithBright=None, zenithBrightHorzDiff=None,
                 solarRad=None, solarRadHorzDiff=None, turbidity=None,
                 latitude=None, longitude=None, meridian=None):
        """Init sky parameters."""
        AdvancedRadianceParameters.__init__(self)

        self.altitudeAzimuth = None
        """[-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime."""

        self.sunnySky = None
        """[-s|+s] A boolean value to generate sunny sky with or without sun.
        Set to True to generate a sunnny sky with sun, Fasle to generate a sunny
        sky without sun (Default: None)
        """

        self.cloudySky = None
        """[-c] A boolean value to generate cloudy sky"""

        self.intermSky = None
        """[-i|+i] A boolean value to generate intermediate sky with or without
        sun. Set to True to generate an intermediate sky with sun, Fasle to
        generate a intermediate sky without sun (Default: None)
        """

        self.uniformCloudySky = None
        """[-u] A boolean value to generate Uniform cloudy sky."""

        self.groundReflect = None
        """[-g rfl] A float number to indicate ground reflectance """

        self.zenithBright = None
        """ [-b brt] A float number to indicate zenith brightness in
         watts/steradian/meter-sq."""

        self.zenithBrightHorzDiff = None
        """[-B irrad] A float number to indicate zenith  brightness from
        horizontal diffuse irradiance in watts/meter-sq."""

        self.solarRad = None
        """[-r rad] A float number to indicate solar radiance in
        watts/steradians/meter-sq."""

        self.solarRadHorzDiff = None
        """ [-R irrad] A float number to indicate solar radiance from horizontal
        direct irradiance in watts/meter-sq."""

        self.turbidity = None
        """ [-t trb] A float number to indicate turbidity."""

        self.latitude = None
        """[-a lat] A float number to indicate site altitude. Negative angle
        indicates south latitude."""

        self.longitude = None
        """[-o lon] A float number to indicate site latitude. Negative angle
        indicates east longitude."""

        self.meridian = None
        """[-m mer] A float number to indicate site meridian west of
        Greenwich. """

        self.addRadianceTuple('ang', 'altitude azimuth', tupleSize=2,
                              numType=float, attributeName='altitudeAzimuth',
                              defaultValue=altitudeAzimuth)

        self.addRadianceBoolFlag('s', 'sunny sky with or without sun',
                                 defaultValue=sunnySky,
                                 attributeName='sunnySky',
                                 isDualSign=True)

        self.addRadianceBoolFlag('c', 'cloudy sky', defaultValue=cloudySky,
                                 attributeName='cloudySky')

        self.addRadianceBoolFlag('i', 'intermediate sky with or without sun',
                                 defaultValue=intermSky,
                                 attributeName='intermSky',
                                 isDualSign=True)

        self.addRadianceBoolFlag('u', 'uniform cloudy sky',
                                 defaultValue=uniformCloudySky,
                                 attributeName='uniformCloudySky')

        self.addRadianceNumber('g', 'ground reflectance',
                               defaultValue=groundReflect,
                               attributeName='groundReflect',
                               numType=float, validRange=(0, 1))

        self.addRadianceNumber('b', 'zenith brightness',
                               defaultValue=zenithBright,
                               attributeName='zenithBright',
                               numType=float)

        self.addRadianceNumber('B',
                               'zenith brightness from horizontal diffuse'
                               'irradiance',
                               defaultValue=zenithBrightHorzDiff,
                               attributeName='zenithBrightHorzDiff',
                               numType=float)

        self.addRadianceNumber('r', 'solar radiance',
                               defaultValue=solarRad,
                               attributeName='solarRad',
                               numType=float)

        self.addRadianceNumber('R', 'solar radiance from horizontal diffuse irradiance',
                               defaultValue=solarRadHorzDiff,
                               attributeName='solarRadHorzDiff',
                               numType=float)

        self.addRadianceNumber('t', 'turbidity', defaultValue=turbidity,
                               attributeName='turbidity', numType=float)

        self.addRadianceNumber('a', 'latitude', defaultValue=latitude,
                               attributeName='latitude', numType=float)

        self.addRadianceNumber('o', 'longitude', defaultValue=longitude,
                               attributeName='longitude', numType=float)

        self.addRadianceNumber('m', 'meredian', defaultValue=meridian,
                               attributeName='meredian', numType=float)
