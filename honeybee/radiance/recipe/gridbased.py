"""Radiance Analysis Recipes."""

from ..postprocess.gridbasedresults import LoadGridBasedDLAnalysisResults
from ...hbpointgroup import AnalysisPointGroup
from .recipeBase import HBDaylightAnalysisRecipe
from ..command.oconv import Oconv
from ..command.rtrace import Rtrace
from ...helper import preparedir

import os
from collections import namedtuple, Iterable
import subprocess


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
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radParameters: Radiance parameters for this analysis.
            (Default: RadianceParameters.LowQuality)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    # TODO: implemnt isChanged at HBDaylightAnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, pointGroups, vectorGroups=[], simulationType=0,
                 radParameters=None, hbObjects=None, subFolder="gridbased"):
        """Create grid-based recipe."""
        HBDaylightAnalysisRecipe.__init__(self, sky=sky,
                                          simulationType=simulationType,
                                          radParameters=radParameters,
                                          hbObjects=hbObjects,
                                          subFolder=subFolder)

        self.__batchFile = None
        self.resultsFile = []

        # create a result loader to load the results once the analysis is done.
        self.loader = LoadGridBasedDLAnalysisResults(self.simulationType,
                                                     self.resultsFile)

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

    # TODO: Add path to PATH and use relative path in batch files
    def writeToFile(self, targetFolder, projectName, radFiles=None,
                    useRelativePath=False):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <projectName.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles> > <projectName.oct>
                rtrace <radianceParameters> <projectName.oct> > <projectName.res>
            results file <*.res>: Results file once the analysis is over.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.
            radFiles: A list of additional .rad files to be added to the scene
            useRelativePath: Set to True to use relative path in bat file <NotImplemented!>.

        Returns:
            True in case of success.
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        _basePath = os.path.join(targetFolder, projectName)
        _ispath = preparedir(_basePath)
        assert _ispath, "Failed to create %s. Try a different path!" % _basePath

        # create main folder targetFolder\projectName\gridbased
        _path = os.path.join(_basePath, self.subFolder)
        _ispath = preparedir(_path)

        assert _ispath, "Failed to create %s. Try a different path!" % _path

        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 1.write sky file
        skyFile = self.sky.writeToFile(_path)

        # 2.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 3.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 4.write batch file
        batchFileLines = []

        # TODO: This line won't work for in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        batchFileLines.append(dirLine)

        # # 4.1.prepare oconv
        oc = Oconv(projectName)
        oc.inputFiles = [skyFile, matFile, geoFile]

        # # 4.2.prepare rtrace
        rt = Rtrace(projectName,
                    simulationType=self.simulationType,
                    radianceParameters=self.radianceParameters)
        rt.octFile = os.path.join(_path, projectName + ".oct")
        rt.pointFile = pointsFile

        # # 4.3 write batch file
        batchFileLines.append(oc.toRadString())
        batchFileLines.append(rt.toRadString())
        batchFile = os.path.join(_path, projectName + ".bat")

        self.write(batchFile, "\n".join(batchFileLines))

        self.__batchFile = batchFile

        print "Files are written to: %s" % _path
        return _path

    # TODO: Update the method to batch run and move it to baseclass
    def run(self, debug=False):
        """Run the analysis."""
        if self.__batchFile:
            if debug:
                with open(self.__batchFile, "a") as bf:
                    bf.write("\npause")

            subprocess.call(self.__batchFile)

            self.isCalculated = True
            # self.isChanged = False

            self.resultsFile = [self.__batchFile.replace(".bat", ".res")]
            return True
        else:
            raise Exception("You need to write the files before running the recipe.")

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        self.loader.simulationType = self.simulationType
        self.loader.resultFiles = self.resultsFile
        return self.loader.results

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulationType],
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
