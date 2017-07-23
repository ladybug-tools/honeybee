# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class GendaylitParameters(AdvancedRadianceParameters):
    """Gendaylit parameters.

    Read more:
        http://radsite.lbl.gov/radiance/man_html/gensky.1.html


    Attributes:
        altitudeAzimuth: [-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime.
        groundReflect: [-g rfl] A float number to indicate ground reflectance.
        latitude: [-a lat] A float number to indicate site altitude. Negative
            angle indicates south latitude.
        longitude: [-o lon] A float number to indicate site latitude. Negative
            angle indicates east longitude.
        meridian: [-m mer] A float number to indicate site meridian west of
        Greenwich.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:


    """

    def __init__(self, altitudeAzimuth=None, latitude=None, longitude=None,
                 meridian=None, groundReflect=None, suppressWarnings=None,
                 timeInterval=None, suppressSun=None, perezParameters=None,
                 dirNormDifHorzIrrad=None, dirHorzDifHorzIrrad=None,
                 dirHorzDifHorzIllum=None, globHorzIrrad=None, outputType=None):
        """Init sky parameters."""
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceTuple('ang', 'altitude azimuth', tupleSize=2,
                              numType=float, attributeName='altitudeAzimuth')
        self.altitudeAzimuth = altitudeAzimuth
        """[-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime."""

        self.addRadianceNumber('g', 'ground reflectance',
                               attributeName='groundReflect',
                               numType=float, validRange=(0, 1))
        self.groundReflect = groundReflect
        """[-g rfl] A float number to indicate ground reflectance """

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

        self.addRadianceBoolFlag('w', 'suppress warnings',
                                 attributeName='suppressWarnings')
        self.suppressWarnings = suppressWarnings
        """Suppress warning messages."""

        self.addRadianceNumber('i', 'time interval', attributeName='timeInterval',
                               numType=int)
        self.timeInterval = timeInterval
        """..."""

        self.addRadianceBoolFlag('s', 'suppress sun', attributeName='suppressSun')
        self.suppressSun = suppressSun
        """Prevent the solar disc from being in the output."""

        self.addRadianceTuple('P', 'perez parameters', tupleSize=2,
                              attributeName='perezParameters')
        self.perezParameters = perezParameters
        """Perez parameters corresponding to epsilon and delta values."""

        self.addRadianceTuple('W', 'direct-normal,diffuse-horizontal irradiance',
                              tupleSize=2,
                              attributeName='dirNormDifHorzIrrad')
        self.dirNormDifHorzIrrad = dirNormDifHorzIrrad
        """Direct-normal irradiance and diffuse-horizontal irradiance in W/m^2"""

        self.addRadianceTuple('G', 'direct-horizontal,diffuse-horizontal irradiance',
                              tupleSize=2,
                              attributeName='dirHorzDifHorzIrrad')
        self.dirHorzDifHorzIrrad = dirHorzDifHorzIrrad
        """Direct-horizontal irradiance and diffuse-horizontal irradiance in W/m^2"""

        self.addRadianceTuple('L', 'direct-horizontal,diffuse-horizontal illuminance',
                              tupleSize=2,
                              attributeName='dirHorzDifHorzIllum')
        self.dirHorzDifHorzIllum = dirHorzDifHorzIllum
        """Direct normal luminance and diffuse horizontal illuminance"""

        self.addRadianceNumber('E', 'global horizontal irradiance',
                               attributeName='globHorzIrrad')
        self.globHorzIrrad = globHorzIrrad
        """Global horizontal irradiance"""

        self.addRadianceNumber('O', 'output type',
                               attributeName='outputType', acceptedInputs=(0, 1, 2))
        self.outputType = outputType
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance"""

    def toRadString(self):
        """Generate Radiance string for gendaylit."""
        # Ensure only one of the inputs in the arguments below is set to True
        self.checkIncompatibleInputs(self.perezParameters.toRadString(),
                                     self.dirNormDifHorzIrrad.toRadString(),
                                     self.dirHorzDifHorzIrrad.toRadString(),
                                     self.dirHorzDifHorzIllum.toRadString(),
                                     self.globHorzIrrad.toRadString())

        return AdvancedRadianceParameters.toRadString(self)
