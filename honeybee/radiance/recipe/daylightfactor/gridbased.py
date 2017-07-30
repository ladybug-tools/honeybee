"""Radiance Grid-based Analysis Recipe."""
from ..pointintime.gridbased import GridBased as PITGridBased
from ...sky.certainIlluminance import CertainIlluminanceLevel
from ladybug.dt import DateTime
from ladybug.legendparameters import LegendParameters


class GridBased(PITGridBased):
    """Daylight factor grid based analysis.

    Attributes:
        analysisGrids: List of analysis grids.
        radParameters: Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "daylightfactor")

    """
    SKYILLUM = 100000

    def __init__(self, analysisGrids, radParameters=None, hbObjects=None,
                 subFolder="daylightfactor"):
        """Create grid-based recipe."""
        # create the sky for daylight factor
        sky = CertainIlluminanceLevel(self.SKYILLUM)
        # simulation type is Illuminance
        simulationType = 0

        PITGridBased.__init__(
            self, sky, analysisGrids, simulationType, radParameters, hbObjects,
            subFolder)

    @classmethod
    def fromPointsAndVectors(
        cls, pointGroups, vectorGroups=None, radParameters=None, hbObjects=None,
            subFolder="gridbased"):
        """Create grid based recipe from points and vectors.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            radParameters: Radiance parameters for grid based analysis (rtrace).
                (Default: gridbased.LowQuality)
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
        """
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(analysisGrids, radParameters, hbObjects, subFolder)

    @property
    def legendParameters(self):
        """Legend parameters for daylight factor analysis."""
        return LegendParameters([0, 100])

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysisGrids:
            ag.unload()

        sky = self.sky
        dt = DateTime(sky.month, sky.day, int(sky.hour),
                      int(60 * (sky.hour - int(sky.hour))))

        # all the results will be divided by this value to calculated the percentage
        div = self.SKYILLUM / 100.0

        rf = self._resultFiles
        startLine = 0
        for count, analysisGrid in enumerate(self.analysisGrids):
            if count:
                startLine += len(self.analysisGrids[count - 1])

            analysisGrid.setValuesFromFile(
                rf, (int(dt.hoy),), startLine=startLine, header=False, mode=div
            )

        return self.analysisGrids

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s: Daylight Factor\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             self.AnalysisGridCount,
             self.totalPointCount)
