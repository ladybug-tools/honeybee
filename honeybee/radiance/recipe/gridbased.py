"""Radiance Analysis Recipes."""

from ...hbpointgroup import AnalysisPointGroup
from .recipeBase import HBDaylightAnalysisRecipe
from collections import Iterable
import os


class HBGridBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test points.
            Each list of test points will be converted to a TestPointGroup. If testPts
            is a single flattened list only one TestPointGroup will be created.
        vectorGroups: An optional list of (x, y, z) vectors. Each vector represents direction
            of corresponding point in testPts. If the vector is not provided (0, 0, 1)
            will be assigned.
        radParameters: Radiance parameters for this analysis.
            (Default: RadianceParameters.LowQuality)
    """

    def __init__(self, sky, pointGroups, vectorGroups=[], radParameters=None):
        """Create grid-based recipe."""
        HBDaylightAnalysisRecipe.__init__(self, sky=sky, radParameters=radParameters)

        self.createAnalysisPointGroups(pointGroups, vectorGroups)

    @property
    def points(self):
        """Return nested list of points."""
        return [ap.poins for ap in self.analysisPointsGroups]

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
        # input is single point! Create a single group but seriously!
        elif not isinstance(pointGroups[0], Iterable):
            pointGroups = [[pointGroups]]
            vectorGroups = [[vectorGroups]]
        # if point group is flatten - create a single group
        elif not isinstance(pointGroups[0][0], Iterable) and not hasattr(pointGroups[0][0], "X"):
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
                if not isinstance(vectors[0], Iterable):
                    vectors = [vectors]
                self.__analysisPointGroups.append(AnalysisPointGroup(pts, vectors))

    def toRadString(self):
        """Return a multiline string of analysis points for Radiance."""
        return "\n".join([ap.toRadString() for ap in self.analysisPointsGroups])

    def ptsToFile(self, filePath):
        """Write point groups to file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/testPts.pts)

        Returns:
            True in case of success. False in case of failure.
        """
        targetFolder = os.path.split(filePath)[0]

        # check targer folder
        self.toFile(targetFolder)

        with open(filePath, "w") as outf:
            try:
                outf.write(self.toRadString())
                return True
            except Exception as e:
                print "Failed to write points to file:\n%s" % e
                return False

    # TODO: Add path to PATH and use relative path in batch files
    def toFile(self, tragetFolder, projectName, HBObjects=None, radFiles=None,
               useRelativePath=False):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <projectName.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance material file.
            geometry file <*.rad>: Radiance geometry file.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles> > <projectName.oct>
                rtrace <radianceParameters> <projectName.oct> > <projectName.res>
            results file <*.res>: Results file once the analysis is over.

        Args:
            tragetFolder:
            projectName:
            HBObjects:
            radFiles:
            useRelativePath:

        Returns:
            True in case of success. False in case of failure.
        """
        pass

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s #PointGroup: %d #Points: %d" % \
            (self.__class__.__name__,
             self.numOfPointGroups,
             self.numOfTotalPoints)


if __name__ == "__main__":
    # test code
    from sky.certainIlluminance import SkyWithCertainIlluminanceLevel

    sky = SkyWithCertainIlluminanceLevel(2000)
    rp = HBGridBasedAnalysisRecipe(sky, [[(0, 0, 0), (10, 0, 0)]])

    print rp
    print "vectors:", rp.ptsVectors

    rp.writePointsToFile("c:/ladybug/points.pts")
