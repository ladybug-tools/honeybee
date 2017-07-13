# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple
from ..parameters.gensky import GenskyParameters

import os


class Gensky(RadianceCommand):
    u"""
    gensky - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        outputName: An optional name for output file name (Default: 'untitled').
        monthDayHour: A tuple containing inputs for month, day and hour.
        genskyParameters: Radiance parameters for gensky. If None Default
            parameters will be set. You can use self.genskyParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gensky import GenSkyParameters
        from honeybee.radiance.command.gensky import GenSky

        # create and modify genskyParameters. In this case a sunny with no sun
        # will be generated.
        gnskyParam = GenSkyParameters()
        gnskyParam.sunnySkyNoSun = True

        # create the gensky Command.
        gnsky = GenSky(monthDayHour=(1,1,11), genskyParameters=gnskyParam,
        outputName = r'd:/sunnyWSun_010111.sky' )

        # run gensky
        gnsky.execute()

        >
    """

    monthDayHour = RadianceTuple('monthDayHour', 'month day hour', tupleSize=3,
                                 testType=False)

    outputFile = RadiancePath('outputFile', descriptiveName='output sky file',
                              relativePath=None, checkExists=False)

    def __init__(self, outputName='untitled', monthDayHour=None, rotation=0,
                 genskyParameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.outputFile = outputName if outputName.lower().endswith(".sky") \
            else outputName + ".sky"
        """results file for sky (Default: untitled)"""

        self.monthDayHour = monthDayHour
        self.rotation = rotation
        self.genskyParameters = genskyParameters

    @classmethod
    def fromSkyType(cls, outputName='untitled', monthDayHour=(9, 21, 12),
                    skyType=0, latitude=None, longitude=None, meridian=None,
                    rotation=0):
        """Create a sky by sky type.

        Args:
            outputName: An optional name for output file name (Default: 'untitled').
            monthDayHour: A tuple containing inputs for month, day and hour.
            skyType: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
            latitude: [-a] A float number to indicate site altitude. Negative
                angle indicates south latitude.
            longitude: [-o] A float number to indicate site latitude. Negative
                angle indicates east longitude.
            meridian: [-m] A float number to indicate site meridian west of
                Greenwich.
        """
        _skyParameters = GenskyParameters(latitude=latitude, longitude=longitude,
                                          meridian=meridian)

        # modify parameters based on sky type
        try:
            skyType = int(skyType)
        except TypeError:
            "skyType should be an integer between 0-5."

        assert 0 <= skyType <= 5, "Sky type should be an integer between 0-5."

        if skyType == 0:
            _skyParameters.sunnySky = True
        elif skyType == 1:
            _skyParameters.sunnySky = False
        elif skyType == 2:
            _skyParameters.intermSky = True
        elif skyType == 3:
            _skyParameters.intermSky = False
        elif skyType == 4:
            _skyParameters.cloudySky = True
        elif skyType == 5:
            _skyParameters.uniformCloudySky = True

        return cls(outputName=outputName, monthDayHour=monthDayHour,
                   genskyParameters=_skyParameters, rotation=rotation)

    @classmethod
    def uniformSkyfromIlluminanceValue(cls, outputName="untitled",
                                       illuminanceValue=10000, skyType=4):
        """Uniform CIE sky based on illuminance value.

        Attributes:
            outputName: An optional name for output file name (Default: 'untitled').
            illuminanceValue: Desired illuminance value in lux
        """
        assert float(illuminanceValue) >= 0, "Illuminace value can't be negative."

        _skyParameters = GenskyParameters(zenithBrightHorzDiff=illuminanceValue / 179.0)

        if skyType == 4:
            _skyParameters.cloudySky = True
        elif skyType == 5:
            _skyParameters.uniformCloudySky = True
        else:
            raise ValueError(
                'Invalid skyType input: {}. '
                'Sky type can only be 4 [cloudySky] or 5 [uniformSky].'.format(skyType)
            )

        return cls(outputName=outputName, monthDayHour=(9, 21, 12),
                   genskyParameters=_skyParameters)

    @property
    def genskyParameters(self):
        """Get and set genskyParameters."""
        return self.__genskyParameters

    @genskyParameters.setter
    def genskyParameters(self, genskyParam):
        self.__genskyParameters = genskyParam if genskyParam is not None \
            else GenskyParameters()

        assert hasattr(self.genskyParameters, "isRadianceParameters"), \
            "input genskyParameters is not a valid parameters type."

    def toRadString(self):
        """Return full command as a string."""
        # generate the name from self.weaFile
        if self.rotation != 0:
            radString = "%s %s %s | xform -rz %.3f > %s" % (
                self.normspace(os.path.join(self.radbinPath, 'gensky')),
                self.monthDayHour.toRadString().replace("-monthDayHour ", ""),
                self.genskyParameters.toRadString(),
                self.rotation,
                self.normspace(self.outputFile.toRadString())
            )
        else:
            radString = "%s %s %s > %s" % (
                self.normspace(os.path.join(self.radbinPath, 'gensky')),
                self.monthDayHour.toRadString().replace("-monthDayHour ", ""),
                self.genskyParameters.toRadString(),
                self.normspace(self.outputFile.toRadString())
            )
        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return None
