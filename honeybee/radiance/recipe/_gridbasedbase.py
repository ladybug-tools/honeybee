"""Honeybee generic grid base analysis base class.

This class is base class for common gridbased analysis recipes as well as
sunlighthours recipe and annual analysis recipe.
"""

from abc import ABCMeta, abstractmethod
from ...hbpointgroup import AnalysisPointGroup
from ._recipebase import HBDaylightAnalysisRecipe

import os
from collections import namedtuple, Iterable


class HBGenericGridBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Honeybee generic grid base analysis base class.

    This class is base class for common gridbased analysis recipes as well as
    sunlighthours recipe and annual analysis recipe.

    Attributes:
        pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test points.
            Each list of test points will be converted to a TestPointGroup. If testPts
            is a single flattened list only one TestPointGroup will be created.
        vectorGroups: An optional list of (x, y, z) vectors. Each vector represents direction
            of corresponding point in testPts. If the vector is not provided (0, 0, 1)
            will be assigned.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, pointGroups, vectorGroups=[], hbObjects=None,
                 subFolder="gridbased"):
        """Create grid-based recipe."""
        HBDaylightAnalysisRecipe.__init__(self, hbObjects=hbObjects,
                                          subFolder=subFolder)

        # create analysisi point groups
        self.createAnalysisPointGroups(pointGroups, vectorGroups)

    @property
    def pointGroups(self):
        """Return analysis point groups."""
        return self.analysisPointsGroups

    @pointGroups.setter
    def pointGroups(self):
        """Return analysis point groups."""
        raise ValueError("You can't set pointGroups directly. " +
                         "Use updatePointGroups method instead.")

    def updatePointGroups(self, pointGroups, vectorGroups=[]):
        """Update point groups.

        Args:
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
        """
        self.createAnalysisPointGroups(pointGroups, vectorGroups)

    @property
    def points(self):
        """Return nested list of points."""
        return [ap.points for ap in self.analysisPointsGroups]

    @property
    def numOfPointGroups(self):
        """Number of point groups."""
        return len(self.analysisPointsGroups)

    @property
    def numOfTotalPoints(self):
        """Number of total points."""
        return sum(len(ap) for ap in self.analysisPointsGroups)

    @property
    def vectors(self):
        """Nested list of vectors."""
        return [ap.vectors for ap in self.analysisPointsGroups]

    @property
    def analysisPointsGroups(self):
        """Return list of AnalysisPointGroups."""
        return self.__analysisPointGroups

    def createAnalysisPointGroups(self, pointGroups, vectorGroups):
        """Create AnalysisPointGroups from input points and vectors.

        You can acces AnalysisPointGroups using self.analysisPointsGroups property.
        """
        self.__analysisPointGroups = []

        if len(pointGroups) == 0:
            return
        # input is single point! Create a single group but seriously!?
        elif not isinstance(pointGroups[0], Iterable):
            pointGroups = [[pointGroups]]
            vectorGroups = [[vectorGroups]]
        # if point group is flatten - create a single group
        elif not isinstance(pointGroups[0][0], Iterable) \
                and not hasattr(pointGroups[0][0], "X"):
            pointGroups = [pointGroups]
            vectorGroups = [vectorGroups]

        for groupCount, pts in enumerate(pointGroups):
            try:
                # create a list for vectors if it's not provided by user
                vectors = vectorGroups[groupCount]
                if vectors == [[]]:
                    vectors = [(0, 0, 1)]
            except IndexError:
                vectors = [(0, 0, 1)]
            finally:
                # last check for vectors in case user input is a flatten lists
                # for nested group of points.
                if not isinstance(vectors[0], Iterable) and not hasattr(vectors[0], 'X'):
                    vectors = [vectors]

                self.__analysisPointGroups.append(AnalysisPointGroup(pts, vectors))

    def flatten(self, inputList):
        """Return a flattened genertor from an input list.

        Usage:

            inputList = [['a'], ['b', 'c', 'd'], [['e']], ['f']]
            list(flatten(inputList))
            >> ['a', 'b', 'c', 'd', 'e', 'f']
        """
        for el in inputList:
            if isinstance(el, Iterable) and not isinstance(el, basestring):
                for sub in self.flatten(el):
                    yield sub
            else:
                yield el

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
            _ptsStr = "\n".join([ap.toRadString() for ap in self.analysisPointsGroups])

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
                          self.toRadString(points=True).points, mkdir)

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
                          _matStr, mkdir) if writeMaterial else " "

        _geo = self.write(os.path.join(targetDir, projectName + ".rad"),
                          _geoStr, mkdir) if writeMaterial else " "

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

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             self.numOfPointGroups,
             self.numOfTotalPoints)
