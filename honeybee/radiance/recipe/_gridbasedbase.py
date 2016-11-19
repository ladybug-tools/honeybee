"""Honeybee generic grid base analysis base class.

This class is base class for common gridbased analysis recipes as well as
sunlighthours recipe and annual analysis recipe.
"""

from abc import ABCMeta, abstractmethod
from ..analysisgrid import AnalysisGrid
from ._recipebase import HBDaylightAnalysisRecipe

import os
from collections import namedtuple


class HBGenericGridBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
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
        HBDaylightAnalysisRecipe.__init__(self, hbObjects=hbObjects,
                                          subFolder=subFolder)
        self.analysisGrids = analysisGrids

    @classmethod
    def fromPointsAndVectors(cls, pointGroups, vectorGroups=None, hbObjects=None,
                             subFolder="gridbased"):
        """Create the recipe from analysisGrid.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector represents direction
                of corresponding point in testPts. If the vector is not provided (0, 0, 1)
                will be assigned.
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

    @staticmethod
    def analysisGridsFromPointsAndVectors(pointGroups, vectorGroups=None):
        """Create analysisGrid classes from points and vectors.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector represents direction
                of corresponding point in testPts. If the vector is not provided (0, 0, 1)
                will be assigned.
        """
        vectorGroups = vectorGroups or ((),)

        vectorGroups = tuple(vectorGroups[i] if i < len(vectorGroups) else vectorGroups[-1]
                             for i in range(len(pointGroups)))

        print zip(pointGroups, vectorGroups)
        analysisGrids = (AnalysisGrid.fromPointsAndVectors(pts, vectors)
                         for pts, vectors in zip(pointGroups, vectorGroups))

        return analysisGrids

    def toRadString(self, hbObjects=False, points=False):
        """Return a tuple of multiline string radiance definition.

        Args:
            hbObjects: Set to True to generate string for materials and geometries (Default: False).
            points: Set to True to generate string for points (Default: False).

        Returns:
            A namedTuple of multiline data. Keys are: points materials geometries

        Usage:
            s = self.toRadString(True, True)
            ptsString , matString, geoString = s
            or
            s = self.toRadString(points=True)
            ptsString = s.points
        """
        _radDefinition = namedtuple("RadString", "points materials geometries")
        _ptsStr = ""
        _matStr = ""
        _geoStr = ""

        if points:
            _ptsStr = "\n".join((ag.toRadString() for ag in self.analysisGrids))

        if hbObjects:
            _matStr, _geoStr = self.hbObjectsToRadString()

        return _radDefinition(_ptsStr, _matStr, _geoStr)

    def writePointsToFile(self, targetDir, projectName, mkdir=False):
        """Write point groups to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            projectName: Project name as string.Points will be saved as
                projectName.pts

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(projectName) is str, "projectName should be a string."
        projectName += ".pts"

        _pts = self.write(os.path.join(targetDir, projectName),
                          self.toRadString(points=True).points + "\n", mkdir)

        if _pts:
            return _pts

    def writeHBObjectsToFile(self, targetDir, projectName, mkdir=False,
                             writeMaterial=True, writeGeometry=True):
        """Write HBobjects to *.rad and .mat files.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            projectName: Project name as string. Geometries will be saved as
                projectName.rad and materials will be saved as projectName.mat
            mkdir: Set to True to create the directory if doesn't exist (Default: False)

        Returns:
            Path to materiald and geometry files as a tuple (*.mat, *.rad).

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(projectName) is str, "projectName should be a string."

        _matStr, _geoStr = self.hbObjectsToRadString()

        _mat = self.write(os.path.join(targetDir, projectName + ".mat"),
                          _matStr + "\n", mkdir) if writeMaterial else " "

        _geo = self.write(os.path.join(targetDir, projectName + ".rad"),
                          _geoStr + "\n", mkdir) if writeMaterial else " "

        if _mat and _geo:
            return _mat, _geo

    @abstractmethod
    def writeToFile(self):
        """Write files for the analysis recipe to file."""
        pass

    @abstractmethod
    def run(self):
        """Run the analysis."""
        pass

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
