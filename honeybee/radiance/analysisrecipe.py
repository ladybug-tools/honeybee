from abc import ABCMeta, abstractmethod, abstractproperty
from sky import *
from radianceParameters import *

class HBDaylightAnalysisRecipe(object):
    pass

class HBGridBasedAnalysisRecipe(DaylightAnalysisRecipe):
    """Grid base analysis base class

        Attributes:
            sky: A honeybee sky for the analysis
            radianceParameters: Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)
    """
    def __init__(self, sky, radParameters = None):
        self.sky(sky)
        self.radianceParameters(radParameters)

    @property
    def sky(self):
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert isinstance(newSky, HBSky), "Sky is not a valid Honeybee sky."
        self.__sky = sky

    @property
    def radianceParameters(radianceParameters):
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(radParameters):
        if not radParameters: radParameters = LowQuality
        assert isinstance(radParameters, RadianceParameters), \
            "Invalid radiance parameters object"
        self.__radParameters = radParameters

    @abstractproperty
    def testPts(self):
        """List of test points
            Should be implemented in geometry libraries
        """
        pass

    @abstractproperty
    def ptsVectors(self):
        """List of vectors for each test point.
            Should be implemented in geometry libraries
            +Z Vector will be assigned if vectors are not provided
        """
        pass

class HBDaylightFactorRecipe(GridBasedAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()

class HBAnnualAnalysisRecipe(GridBasedAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()


class HBImageBasedAnalysisRecipe(DaylightAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()
