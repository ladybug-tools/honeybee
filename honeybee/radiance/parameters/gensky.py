# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class GenskyParameters(AdvancedRadianceParameters):
    """Gensky parameters.

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
        groundReflect: [-g rfl] A float number to indicate ground reflectance.
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

        self.addRadianceTuple('ang', 'altitude azimuth', tupleSize=2,
                              numType=float, attributeName='altitudeAzimuth')
        self.altitudeAzimuth = altitudeAzimuth
        """[-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime."""

        self.addRadianceBoolFlag('s', 'sunny sky with or without sun',
                                 attributeName='sunnySky',
                                 isDualSign=True)
        # set current value
        self.sunnySky = sunnySky
        """[-s|+s] A boolean value to generate sunny sky with or without sun.
        Set to True to generate a sunnny sky with sun, Fasle to generate a sunny
        sky without sun (Default: None)
        """

        self.addRadianceBoolFlag('c', 'cloudy sky', attributeName='cloudySky')
        self.cloudySky = cloudySky
        """[-c] A boolean value to generate cloudy sky"""

        self.addRadianceBoolFlag('i', 'intermediate sky with or without sun',
                                 attributeName='intermSky',
                                 isDualSign=True)
        self.intermSky = intermSky
        """[-i|+i] A boolean value to generate intermediate sky with or without
        sun. Set to True to generate an intermediate sky with sun, Fasle to
        generate a intermediate sky without sun (Default: None)
        """

        self.addRadianceBoolFlag('u', 'uniform cloudy sky',
                                 attributeName='uniformCloudySky')
        self.uniformCloudySky = uniformCloudySky
        """[-u] A boolean value to generate Uniform cloudy sky."""

        self.addRadianceNumber('g', 'ground reflectance',
                               attributeName='groundReflect',
                               numType=float, validRange=(0, 1))
        self.groundReflect = groundReflect
        """[-g rfl] A float number to indicate ground reflectance """

        self.addRadianceNumber('b', 'zenith brightness',
                               attributeName='zenithBright',
                               numType=float)
        self.zenithBright = zenithBright
        """ [-b brt] A float number to indicate zenith brightness in
         watts/steradian/meter-sq."""

        self.addRadianceNumber('B',
                               'zenith brightness from horizontal diffuse'
                               'irradiance',
                               attributeName='zenithBrightHorzDiff',
                               numType=float)
        self.zenithBrightHorzDiff = zenithBrightHorzDiff
        """[-B irrad] A float number to indicate zenith  brightness from
        horizontal diffuse irradiance in watts/meter-sq."""

        self.addRadianceNumber('r', 'solar radiance',
                               attributeName='solarRad',
                               numType=float)
        self.solarRad = solarRad
        """[-r rad] A float number to indicate solar radiance in
        watts/steradians/meter-sq."""

        self.addRadianceNumber('R', 'solar radiance from horizontal diffuse irradiance',
                               attributeName='solarRadHorzDiff',
                               numType=float)
        self.solarRadHorzDiff = solarRadHorzDiff
        """ [-R irrad] A float number to indicate solar radiance from horizontal
        direct irradiance in watts/meter-sq."""

        self.addRadianceNumber('t', 'turbidity', attributeName='turbidity',
                               numType=float)
        self.turbidity = turbidity
        """ [-t trb] A float number to indicate turbidity."""

        self.addRadianceNumber('a', 'latitude', attributeName='latitude',
                               numType=float)
        self.latitude = latitude
        """[-a lat] A float number to indicate site altitude. Negative angle
        indicates south latitude."""

        self.addRadianceNumber('o', 'longitude', attributeName='longitude',
                               numType=float)
        self.longitude = longitude
        """[-o lon] A float number to indicate site latitude. Negative angle
        indicates east longitude."""

        self.addRadianceNumber('m', 'meridian', attributeName='meridian',
                               numType=float)
        self.meridian = meridian
        """[-m mer] A float number to indicate site meridian west of
        Greenwich. """
