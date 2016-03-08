"""Radiance Analysis Recipes."""
from ..sky.skyBase import RadianceSky
from ..parameters import RadianceParameters, LowQuality
import os


class HBDaylightAnalysisRecipe(object):
    """Analysis Recipe Base class.

    Attributes:
        sky: A honeybee sky for the analysis.
        radParameters: Radiance parameters for this analysis.
            (Default: RadianceParameters.LowQuality)
    """

    def __init__(self, sky, radParameters=None):
        """Create Analysis recipe."""
        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radianceParameters = radParameters
        """Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)."""

    @property
    def sky(self):
        """Get and set sky definition."""
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert isinstance(newSky, RadianceSky), "%s is not a valid Honeybee sky." % type(newSky)
        self.__sky = newSky

    @property
    def radianceParameters(self, radianceParameters):
        """Get and set Radiance parameters."""
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = LowQuality()
        assert isinstance(radParameters, RadianceParameters), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radParameters = radParameters

    def toRadString(self):
        """Radiance representation of the recipe."""
        raise NotImplementedError

    def toFile(self, targetFolder):
        """Write files for the analysis recipe to file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/testPts.pts)

        Returns:
            True in case of success. False in case of failure.
        """
        assert os.path.isdir(targetFolder), \
            "Cannot find %s." % targetFolder
