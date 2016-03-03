"""Radiance Analysis Recipes."""

from sky.skyBase import RadianceSky
from sky.certainIlluminance import SkyWithCertainIlluminanceLevel
from parameters import RadianceParameters, LowQuality


class HBDaylightAnalysisRecipe(object):
    """Analysis Recipe Base class."""

    pass


class HBGridBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        testPts: A list of test points as (x, y, z)
        ptsVectors: An optional list of point vectors as (x, y, z).
        radParameters: Radiance parameters for this analysis (Default:
            RadianceParameters.LowQuality)
    """

    def __init__(self, sky, testPts, ptsVectors=[], radParameters=None):
        """Create grid-based recipe."""
        self.sky = sky
        """A honeybee sky for the analysis"""
        self.testPts = testPts
        """A list of test points as (x, y, z)"""
        self.ptsVectors = ptsVectors
        """An optional list of point vectors as Rhino.Geometry.Vector3d
            +Z Vector will be assigned if vectors are not provided."""
        self.radianceParameters = radParameters
        """Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)"""

    @property
    def sky(self):
        """Get and set sky definition."""
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert isinstance(newSky, RadianceSky), "Sky is not a valid Honeybee sky."
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
            "Invalid radiance parameters object"
        self.__radParameters = radParameters

    # TODO: @sariths do we need test point groups for 3Phase method?
    # in that case we should accept lists of lists for test points
    @property
    def testPts(self):
        """List of test points."""
        return self.__testPts

    @testPts.setter
    def testPts(self, pts):
        """Set list of test points."""
        self.__testPts = pts

    @property
    def ptsVectors(self):
        """List of vectors for each test point.

        +Z Vector will be assigned if vectors are not provided
        """
        return self.__ptsVectors

    # TODO: Add check for vectors. Remove null values. assign 0, 0, 1 in case of None
    @ptsVectors.setter
    def ptsVectors(self, vectors):
        """List of vectors for each test point.

        +Z Vector will be assigned if vectors are not provided
        """
        if vectors == []:
            self.__ptsVectors = [(0, 0, 1) for pt in self.testPts]
        else:
            assert len(self.testPts) == len(vectors), \
                "Length of test points should be equal to length of vectors."
            self.__ptsVectors = vectors

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s #testPts:%d" % (self.__class__.__name__, len(self.testPts))


class HBDaylightFactorRecipe(HBGridBasedAnalysisRecipe):
    """Daylight Factor Recipe."""

    def __init__(self):
        """Create daylight factor recipe."""
        raise NotImplementedError()


class HBAnnualAnalysisRecipe(HBGridBasedAnalysisRecipe):
    """Annual Daylight Recipe."""

    def __init__(self):
        """Create annual daylight recipe."""
        raise NotImplementedError()


class HBImageBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Image-based recipe."""

    def __init__(self):
        """Create an Image-based recipe."""
        raise NotImplementedError()


if __name__ == "__main__":
    # test code
    sky = SkyWithCertainIlluminanceLevel(2000)
    rp = HBGridBasedAnalysisRecipe(sky, [(0, 0, 0), (10, 0, 0)])

    print rp
    print "vectors:", rp.ptsVectors
