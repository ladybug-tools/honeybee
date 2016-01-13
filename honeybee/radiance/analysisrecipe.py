from abc import ABCMeta, abstractmethod, abstractproperty
from sky import *
from radianceparameters import *

class HBDaylightAnalysisRecipe(object):
    pass

class HBGridBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Grid base analysis base class

        Attributes:
            sky: A honeybee sky for the analysis
            radianceParameters: Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)
    """
    def __init__(self, sky, radParameters = None):
        self.sky = sky
        self.radianceParameters = radParameters

    @property
    def sky(self):
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert isinstance(newSky, HBSky), "Sky is not a valid Honeybee sky."
        self.__sky = newSky

    @property
    def radianceParameters(self, radianceParameters):
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters: radParameters = LowQuality()
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

class HBDaylightFactorRecipe(HBGridBasedAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()

class HBAnnualAnalysisRecipe(HBGridBasedAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()


class HBImageBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    def __init__(self):
        raise NotImplementedError()


"""
sky = HBCertainIlluminanceLevelSky(2000)
rp = HBGridBasedAnalysisRecipe(sky)
"""
