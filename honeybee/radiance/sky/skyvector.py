from _skyBase import RadianceSky
from ..command.genskyvec import Genskyvec
from ..command.gensky import Gensky
from ..command.gendaylit import Gendaylit
from ..parameters.gendaylit import GendaylitParameters

from ...ladybug.epw import EPW
from ...ladybug.core import LBDateTime
import os


class SkyVector(RadianceSky):
    """Radiance sky vector.

    Attributes:
        skyFile: Full filepath to a radiance sky file. The file can be generated
            by either gensky or gendaylit. If you're not sure how to create them
            use one of the classmethods.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
    """

    def __init__(self, skyFile, skyDensity=1, isClimateBased=False):
        """Create sky."""
        RadianceSky.__init__(self)
        assert os.path.isfile(skyFile), 'Invalid path: {}'.format(skyFile)
        self.skyFile = os.path.normpath(skyFile)
        self.skyDensity = skyDensity or 1
        self.__isClimateBased = isClimateBased

    @classmethod
    def fromClimateBasedSky(cls, epwFile, month=6, day=21, hour=12, skyDensity=1):
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
        skyfile = 'CB_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour
        )
        #
        HOY = LBDateTime(month, day, hour).HOY
        dnr = epw.directNormalRadiation.values()[HOY]
        dgr = epw.diffuseHorizontalRadiation.values()[HOY]
        gdp = GendaylitParameters(dirNormDifHorzIrrad=(dnr, dgr))

        gendl = Gendaylit(monthDayHour=(month, day, hour),
                          gendaylitParameters=gdp)
        gendl.outputFile = skyfile
        gendl.execute()

        return cls(skyfile, skyDensity, isClimateBased=True)

    @classmethod
    def fromCIESky(cls, location, month=6, day=21, hour=12, skyType=0,
                   skyDensity=1):
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
        skyfile = 'CIE_{}_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour, skyType
        )
        gensk = Gensky.fromSkyType(skyfile, monthDayHour=(month, day, hour),
                                   skyType=skyType,
                                   latitude=location.latitude,
                                   longitude=location.longitude,
                                   meridian=float(location.timeZone) * -15)
        gensk.outputFile = skyfile
        gensk.execute()

        return cls(skyfile, skyDensity, isClimateBased=False)

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return self.__isClimateBased

    @property
    def name(self):
        """Sky default name."""
        return "SKYVEC_{}".format(
            '.'.join(os.path.split(self.skyFile)[-1].split('.')[:-1])
        )

    @property
    def main(self):
        """Generate Radiance's line for sky with certain illuminance value."""
        return " "

    def execute(self, workingDir, reuse=True):
        """Generate sky vector.

        Args:
            workingDir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(workingDir, '{}.vec'.format(self.name))
        if reuse and os.path.isfile(outfilepath):
            return outfilepath

        genskv = Genskyvec()
        genskv.inputSkyFile = self.skyFile
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
