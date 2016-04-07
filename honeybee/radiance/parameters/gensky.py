# coding=utf-8
from _advancedparametersbase import AdvancedRadianceParameters


class GenskyParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    Read more:
    http://radsite.lbl.gov/radiance/man_html/gensky.1.html


    Attributes:
        altitudeAzimuth: [-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime.
        sunnySkyNoSun: [-s] A boolean value to generate sunny sky without sun.
        sunnySkyWithSun: [+s] A boolean value to generate sunny sky with sun.
        cloudySky: [-c] A boolean value to generate cloudy sky
        intermSkyNoSun: [-i] A boolean value to generate intermediate sky without
            sun.
        intermSkyWithSun: [+i] A boolean value to generate Intermediate sky with
            sun.
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
        gnsky = GenskyParameters()

        # check the current values
        print gensky.toRadString()


        # ask only for direct sun
        gnsky.intermSkyWithSun=True

    """
    pass

    def __init__(self,altitudeAzimuth=None,sunnySkyNoSun=None,
                 sunnySkyWithSun=None,cloudySky=None,intermSkyNoSun=None,
                 intermSkyWithSun=None,uniformCloudySky=None,groundReflect=None,
                 zenithBright=None,zenithBrightHorzDiff=None,solarRad=None,
                 solarRadHorzDiff=None,turbidity=None,latitude=None,
                 longitude=None,meridian=None):
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceTuple('ang','altitude azimuth',tupleSize=2,
                                     numType=float,attributeName=altitudeAzimuth)
        self.addRadianceBoolFlag('s','sunny sky with no sun',
                                 defaultValue=sunnySkyNoSun,
                                 attributeName='sunnySkyNoSun')
        self.addRadianceBoolFlag('s','sunny sky with sun',
                                 defaultValue=sunnySkyWithSun,
                                 attributeName='sunnySkyWithSun',
                                 isDualSign=True)
        self.addRadianceBoolFlag('c','cloudy sky',defaultValue=cloudySky,
                                 attributeName='cloudySky')
        self.addRadianceBoolFlag('i','intermediate sky with sun',
                                 defaultValue=intermSkyWithSun,
                                 attributeName='intermSkyWithSun',
                                 isDualSign=True)
        self.addRadianceBoolFlag('i','intermediate sky without sun',
                                 defaultValue=intermSkyNoSun,
                                 attributeName='intermSkyNoSun')
        self.addRadianceBoolFlag('u','uniform cloudy sky',
                                 defaultValue=uniformCloudySky,
                                 attributeName='uniformCloudySky')
        self.addRadianceNumber('g','ground reflectance',
                               defaultValue=groundReflect,
                               attributeName='groundReflect',
                               numType=float,validRange=(0, 1))
        self.addRadianceNumber('b','zenith brightness',
                               defaultValue=zenithBright,
                               attributeName='zenithBright',
                               numType=float)
        self.addRadianceNumber('B',
                               'zenith brightness from horizontal diffuse'
                               'irradiance',
                               defaultValue=zenithBrightHorzDiff,
                               attributeName='zenithBrightHorzDiff',
                               numType=float)
        self.addRadianceNumber('r','solar radiance',
                               defaultValue=solarRad,
                               attributeName='solarRad',
                               numType=float)
        self.addRadianceNumber('R','solar radiance from horizontal diffuse '
                                   'irradiance',
                               defaultValue=solarRadHorzDiff,
                               attributeName='solarRadHorzDiff',
                               numType=float)
        self.addRadianceNumber('t','turbidity',defaultValue=turbidity,
                               attributeName='turbidity',numType=float)

        self.addRadianceNumber('a','latitude',defaultValue=latitude,
                               attributeName='latitude',numType=float)
        self.addRadianceNumber('o','longitude',defaultValue=longitude,
                               attributeName='longitude',numType=float)
        self.addRadianceNumber('m','meredian',defaultValue=meridian,
                               attributeName='meredian',numType=float)