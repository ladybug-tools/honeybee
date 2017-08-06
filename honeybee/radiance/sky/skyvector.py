from ._skyBase import RadianceSky
from ..command.genskyvec import Genskyvec
from ..command.gensky import Gensky
from ..command.gendaylit import Gendaylit
from ..parameters.gendaylit import GendaylitParameters

from ladybug.epw import EPW
from ladybug.dt import DateTime
import os


class SkyVector(RadianceSky):
    """Radiance sky vector.

    Attributes:
        sky: A sky object generated either by gensky or gendaylit. If you're not
            sure how to create them use one of the classmethods.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
    """

    def __init__(self, sky, skyDensity=1, isClimateBased=False):
        """Create sky."""
        RadianceSky.__init__(self)
        self.sky = sky
        self.__month = self.sky.monthDayHour[0]
        self.__day = self.sky.monthDayHour[1]
        self.__hour = self.sky.monthDayHour[2]
        self.skyDensity = skyDensity or 1
        self.__isClimateBased = isClimateBased

    # from radiation values
    @classmethod
    def fromRadiationValues(
        cls, location, directNormalRadiation, diffuseHorizontalRadiation,
            month=6, day=21, hour=12, skyDensity=1, north=0):
        """From radiation values."""
        skyfile = 'CB_{}_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour, north
        )

        gdp = GendaylitParameters(dirNormDifHorzIrrad=(directNormalRadiation,
                                                       diffuseHorizontalRadiation))

        gendl = Gendaylit(monthDayHour=(month, day, hour), rotation=north,
                          gendaylitParameters=gdp)

        gendl.outputFile = skyfile

        return cls(gendl, skyDensity, isClimateBased=True)

    @classmethod
    def fromEpwFile(cls, epwFile, month=6, day=21, hour=12, skyDensity=1,
                    north=0):
        """Generate a climate-based sky vector.

        This methos uses Radiance's gendaylit.

        Args:
            epwFile: Full path to epw weather file.
            month: Month [1..12] (default: 6).
            day: Day [1..31] (default: 21).
            hour: Hour [0..23] (default: 12).
            skyType: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
            skyDensity: A positive intger for sky density. [1] Tregenza Sky,
                [2] Reinhart Sky, etc. (Default: 1)
        """
        epw = EPW(epwFile)
        location = epw.location
        HOY = DateTime(month, day, hour).HOY
        dnr = epw.directNormalRadiation.values()[HOY]
        dhr = epw.diffuseHorizontalRadiation.values()[HOY]

        return cls.fromRadiationValues(location, dnr, dhr, month, day, hour,
                                       skyDensity, north)

    @classmethod
    def fromCIESky(cls, location, month=6, day=21, hour=12, skyType=0,
                   skyDensity=1, north=0):
        """Generate a sky vector from an standard CIE sky.

        Args:
            month: Month [1..12] (default: 6).
            day: Day [1..31] (default: 21).
            hour: Hour [0..23] (default: 12).
            skyType: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        """
        skyfile = 'CIE_{}_{}_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour, skyType, north
        )
        gensk = Gensky.fromSkyType(skyfile, monthDayHour=(month, day, hour),
                                   skyType=skyType,
                                   latitude=location.latitude,
                                   longitude=location.longitude,
                                   meridian=float(location.timeZone) * -15,
                                   rotation=north)
        gensk.outputFile = skyfile

        return cls(gensk, skyDensity, isClimateBased=False)

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return self.__isClimateBased

    @property
    def isSkyVector(self):
        """Return True."""
        return True

    @property
    def hour(self):
        """Return hour."""
        return self.__hour

    @property
    def day(self):
        """Return hour."""
        return self.__day

    @property
    def month(self):
        """Return hour."""
        return self.__month

    @property
    def name(self):
        """Sky default name."""
        try:
            return "SKYVEC_{}".format(
                '.'.join(os.path.split(self.sky.outputFile)[-1].split('.')[:-1])
            )
        except TypeError:
            return "SKYVEC_{}".format(
                '.'.join(str(self.sky.outputFile).split('.')[:-1])
            )

    # TODO: re-write the method! It's Currently very shaky
    def toRadString(self, workingDir=None, relativePath=None):
        """Return Radiance command line."""
        if workingDir:
            # make sure the original sky (*.sky) will be writtern to working dir
            skyoutputFile = os.path.join(workingDir, str(self.sky.outputFile))
            # set the sky vector to be written to the working dir (*.vec)
            outfilepath = os.path.join(workingDir, '{}.vec'.format(self.name))
            if relativePath:
                outfilepath = os.path.relpath(outfilepath, relativePath)
                skyoutputFile = os.path.relpath(skyoutputFile, relativePath)
        else:
            outfilepath = '{}.vec'.format(self.name)
            skyoutputFile = str(self.sky.outputFile)

        self.sky.outputFile = skyoutputFile
        self.sky.execute()

        genskv = Genskyvec()
        genskv.inputSkyFile = skyoutputFile
        genskv.outputFile = outfilepath
        genskv.skySubdivision = self.skyDensity
        return genskv.toRadString()

    def execute(self, workingDir, reuse=True):
        """Generate sky vector.

        Args:
            workingDir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(workingDir, '{}.vec'.format(self.name))
        if reuse and os.path.isfile(outfilepath):
            return outfilepath

        #  update path for the sky file
        self.sky.outputFile = os.path.join(workingDir, str(self.sky.outputFile))
        genskv = Genskyvec()
        genskv.inputSkyFile = str(self.sky.execute())
        genskv.outputFile = outfilepath
        genskv.skySubdivision = self.skyDensity
        genskv.execute()
        return outfilepath

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
