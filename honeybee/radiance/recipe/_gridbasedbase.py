"""Honeybee generic grid base analysis baseclass.

This class is base class for common gridbased analysis recipes as well as
sunlighthours recipe and annual analysis recipe.
"""

from abc import ABCMeta, abstractmethod
from ..analysisgrid import AnalysisGrid
from ...futil import writeToFile
from ._recipebase import DaylightAnalysisRecipe

from ladybug.legendparameters import LegendParameters

import os


class GenericGridBasedAnalysisRecipe(DaylightAnalysisRecipe):
    """Honeybee generic grid base analysis base class.

    This class is base class for common gridbased analysis recipes as well as
    sunlighthours recipe and annual analysis recipe.

    Attributes:
        analysisGrids: A collection of honeybee AnalysisGrid. Use fromPointsAndVectors
            classmethod to create the recipe by points and vectors.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, analysisGrids, hbObjects=None, subFolder="gridbased"):
        """Create grid-based recipe."""
        # keep track of original points for re-structuring them later on
        DaylightAnalysisRecipe.__init__(self, hbObjects=hbObjects,
                                        subFolder=subFolder)
        self.analysisGrids = analysisGrids

    @classmethod
    def fromPointsAndVectors(cls, pointGroups, vectorGroups=None, hbObjects=None,
                             subFolder="gridbased"):
        """Create the recipe from analysisGrid.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a
                    TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be
                    created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector represents
                direction of corresponding point in testPts. If the vector is not
                provided (0, 0, 1) will be assigned.
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "gridbased").
        """
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups, vectorGroups)
        return cls(analysisGrids, hbObjects, subFolder)

    @property
    def analysisGrids(self):
        """Return analysis grids."""
        return self.__analysisGrids

    @analysisGrids.setter
    def analysisGrids(self, ags):
        """Set analysis grids."""
        self.__analysisGrids = tuple(ags)

        for ag in self.__analysisGrids:
            assert hasattr(ag, 'isAnalysisGrid'), \
                '{} is not an AnalysisGrid.'.format(ag)

    @property
    def points(self):
        """Return nested list of points."""
        return tuple(ap.points for ap in self.analysisGrids)

    @property
    def vectors(self):
        """Nested list of vectors."""
        return tuple(ap.vectors for ap in self.analysisGrids)

    @property
    def numOfAnalysisGrids(self):
        """Number of point groups."""
        return len(self.analysisGrids)

    @property
    def numOfTotalPoints(self):
        """Number of total points."""
        return sum(len(tuple(pts)) for pts in self.points)

    @property
    def legendParameters(self):
        """Legend parameters for grid based analysis."""
        return LegendParameters([0, 3000])

    @staticmethod
    def analysisGridsFromPointsAndVectors(pointGroups, vectorGroups=None):
        """Create analysisGrid classes from points and vectors.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a
                    TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be
                    created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector represents
                direction of corresponding point in testPts. If the vector is not
                provided (0, 0, 1) will be assigned.
        """
        vectorGroups = vectorGroups or ((),)

        vectorGroups = tuple(vectorGroups[i] if i < len(vectorGroups)
                             else vectorGroups[-1] for i in range(len(pointGroups)))

        print zip(pointGroups, vectorGroups)
        analysisGrids = (AnalysisGrid.fromPointsAndVectors(pts, vectors)
                         for pts, vectors in zip(pointGroups, vectorGroups))

        return analysisGrids

    def toRadStringPoints(self):
        """Return points radiance definition as a single multiline string."""
        return '\n'.join((ag.toRadString() for ag in self.analysisGrids))

    def writePointsToFile(self, targetDir, fileName, mkdir=False):
        """Write point groups to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            fileName: File name as string. Points will be saved as
                fileName.pts

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(fileName) is str, 'fileName should be a string.'
        fileName = fileName if fileName.lower().endswith('.pts') \
            else fileName + '.pts'

        return writeToFile(os.path.join(targetDir, fileName),
                           self.toRadStringPoints() + "\n", mkdir)

    @abstractmethod
    def results(self):
        """Return results for this analysis."""
        pass

    def ToString(self):
        """Overwriet .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s\n#AnalysisGrids: %d #Points: %d" % \
            (self.__class__.__name__,
             self.numOfAnalysisGrids,
             self.numOfTotalPoints)
