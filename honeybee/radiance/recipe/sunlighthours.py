from ._gridbasedbase import HBGenericGridBasedAnalysisRecipe
from ..postprocess.sunlighthourresults import LoadSunlighthoursResults
from ..parameters.rcontrib import RcontribParameters
from ..command._commandbase import RadianceCommand
from ..command.oconv import Oconv
from ..command.rcontrib import Rcontrib
from ...helper import preparedir
from ...vectormath.euclid import Vector3

from ...ladybug.sunpath import LBSunpath

import os
import subprocess


class HBSunlightHoursAnalysisRecipe(HBGenericGridBasedAnalysisRecipe):
    """Sunlight hour analysis.

    This class calculates number of sunlight hours for a group of test points.

    Attributes:
        sunVectors: A list of ladybug sun vectors as (x, y, z) values. Z value
            for sun vectors should be negative (coming from sun toward earth)
        pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test
            points. Each list of test points will be converted to a
            TestPointGroup. If testPts is a single flattened list only one
            TestPointGroup will be created.
        vectorGroups: An optional list of (x, y, z) vectors. Each vector
            represents direction of corresponding point in testPts. If the
            vector is not provided (0, 0, 1) will be assigned.
        timestep: The number of timesteps per hour for sun vectors. This number
            should be smaller than 60 and divisible by 60. The default is set to
            1 such that one sun vector is generated for each hour (Default: 1).
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")

    Usage:
        # initiate analysisRecipe
        analysisRecipe = HBSunlightHoursAnalysisRecipe(
            sunVectors, testPoints, ptsVectors
            )

        # add honeybee object
        analysisRecipe.hbObjects = HBObjs

        # write analysis files to local drive
        analysisRecipe.writeToFile(_folder_, _name_)

        # run the analysis
        analysisRecipe.run(debaug=False)

        # get the results
        print analysisRecipe.results()
    """

    # ad =

    def __init__(self, sunVectors, pointGroups, vectorGroups=[],
                 timestep=1, hbObjects=None, subFolder="sunlighthour"):
        """Create sunlighthours recipe."""
        HBGenericGridBasedAnalysisRecipe.__init__(
            self, pointGroups, vectorGroups, hbObjects, subFolder
        )

        self.sunVectors = sunVectors
        self.timestep = timestep

        self.__radianceParameters = RcontribParameters()
        self.__radianceParameters.I = True
        self.__radianceParameters.ab = 0
        self.__radianceParameters.dc = 1
        self.__radianceParameters.dt = 0
        self.__radianceParameters.dj = 0

        self.__batchFile = None
        self.resultsFile = []
        # create a result loader to load the results once the analysis is done.
        self.loader = LoadSunlighthoursResults(self.timestep, self.resultsFile)

    @classmethod
    def fromLBSuns(cls, suns, pointGroups, vectorGroups=[], timestep=1,
                   hbObjects=None, subFolder="sunlighthour"):
        """Create sunlighthours recipe from LB sun objects.

        Attributes:
            suns: A list of ladybug suns.
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test
                points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        try:
            sunVectors = [s.sunVector for s in suns if s.isDuringDay]
        except AttributeError:
            raise ValueError("%s is not a valid LBSun" % s)

        return cls(sunVectors, pointGroups, vectorGroups, timestep,
                   hbObjects, subFolder)

    @classmethod
    def fromLocationAndHoys(cls, location, HOYs, pointGroups, vectorGroups=[],
                            timestep=1, hbObjects=None, subFolder="sunlighthour"):
        """Create sunlighthours recipe from Location and hours of year."""
        sp = LBSunpath.fromLocation(location)

        suns = [sp.calculateSunFromHOY(HOY) for HOY in HOYs]

        sunVectors = [s.sunVector for s in suns if s.isDuringDay]

        return cls(sunVectors, pointGroups, vectorGroups, timestep,
                   hbObjects, subFolder)

    @classmethod
    def fromLocationAndAnalysisPeriod(
        cls, location, analysisPeriod, pointGroups, vectorGroups=[],
        hbObjects=None, subFolder="sunlighthour"
    ):
        """Create sunlighthours recipe from Location and analysis period."""
        sp = LBSunpath.fromLocation(location)

        suns = [sp.calculateSunFromHOY(HOY) for HOY in analysisPeriod.floatHOYs]

        sunVectors = [s.sunVector for s in suns if s.isDuringDay]

        return cls(sunVectors, pointGroups, vectorGroups,
                   analysisPeriod.timestep, hbObjects,
                   subFolder)

    @property
    def sunVectors(self):
        """A list of ladybug sun vectors as (x, y, z) values."""
        return self.__sunVectors

    @sunVectors.setter
    def sunVectors(self, vectors):
        try:
            self.__sunVectors = [Vector3(*v).flipped() for v in vectors
                                 if v[2] < 0]
        except TypeError:
            self.__sunVectors = [Vector3(v.X, v.Y, v.Z).flipped()
                                 for v in vectors if v.Z < 0]
        except IndexError:
            raise ValueError("Failed to create a sun vector from %s" % str(v))

        if len(self.sunVectors) != len(vectors):
            print "%d vectors with positive z value are found and removed " \
                "from sun vectors" % (len(vectors) - len(self.sunVectors))

    @property
    def timestep(self):
        """An intger for the number of timesteps per hour for sun vectors.

        This number should be smaller than 60 and divisible by 60.
        """
        return self.__timestep

    @timestep.setter
    def timestep(self, ts):
        try:
            self.__timestep = int(ts)
        except:
            self.__timestep = 1

        assert self.__timestep != 0, "ValueError: TimeStep cannot be 0."

    def writeSunsToFile(self, targetDir, projectName, mkdir=False):
        """Write sunlist, sun geometry and sun material files.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            projectName: Project name as string. Suns will be saved as
                projectName.sun

        Returns:
            A tuple of paths to sunlist file, sun materials and sun geometries

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(projectName) is str, "projectName should be a string."

        _suns = range(len(self.sunVectors))
        _mat = range(len(self.sunVectors))
        _geo = range(len(self.sunVectors))

        # create data
        for count, v in enumerate(self.sunVectors):
            _suns[count] = "solar%d" % count
            _mat[count] = "void light solar%d 0 0 3 1.0 1.0 1.0" % count
            _geo[count] = \
                "solar{0} source sun{0} 0 0 4 {1} {2} {3} 0.533".format(
                    count, v.X, v.Y, v.Z)

        _sunsf = self.write(os.path.join(targetDir, projectName + ".sun"),
                            "\n".join(_suns) + "\n", mkdir)
        _matf = self.write(os.path.join(targetDir, projectName + "_suns.mat"),
                           "\n".join(_mat) + "\n", mkdir)
        _geof = self.write(os.path.join(targetDir, projectName + "_suns.rad"),
                           "\n".join(_geo) + "\n", mkdir)

        if _sunsf and _matf and _geof:
            return _sunsf, _matf, _geof

    # TODO: Add path to PATH and use relative path in batch files
    def writeToFile(self, targetFolder, projectName, radFiles=None,
                    useRelativePath=False):
        """Write analysis files to target folder.

        Files for sunlight hours analysis are:
            test points <projectName.pts>: List of analysis points.
            suns file <*.sun>: list of sun sources .
            suns material file <*_suns.mat>: Radiance materials for sun sources.
            suns geometry file <*_suns.rad>: Radiance geometries for sun sources.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is None.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconv [material file] [geometry file] [sun materials file] [sun geometries file] > [octree file]
                rcontrib -ab 0 -ad 10000 -I -M [sunlist.txt] -dc 1 [octree file]< [pts file] > [rcontrib results file]

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

        # 1.write sun files
        sunsList, sunsMat, sunsGeo = self.writeSunsToFile(_path, projectName)

        # 1.1.add sun list to modifiers
        self.__radianceParameters.modFile = RadianceCommand.normspace(sunsList)

        # 2.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 3.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 4.write batch file
        batchFileLines = []

        # TODO: This line won't work in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        batchFileLines.append(dirLine)

        # # 4.1.prepare oconv
        oc = Oconv(projectName)
        oc.sceneFiles = [matFile, geoFile, sunsMat, sunsGeo]

        # # 4.2.prepare rtrace
        rct = Rcontrib(projectName,
                       rcontribParameters=self.__radianceParameters)
        rct.octreeFile = os.path.join(_path, projectName + ".oct")
        rct.pointsFile = pointsFile

        # # 4.3 write batch file
        batchFileLines.append(oc.toRadString())
        batchFileLines.append(rct.toRadString())
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

            if len(self.sunVectors) > 2047:
                print "Update Radiance in case you get this error: " \
                    "rcontrib: internal - too many modifiers."

            subprocess.call(self.__batchFile)

            self.isCalculated = True
            # self.isChanged = False

            self.resultsFile = [self.__batchFile.replace(".bat", ".dc")]
            return True
        else:
            raise Exception("You need to write the files before running the recipe.")

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        self.loader.timestep = self.timestep
        self.loader.resultFiles = self.resultsFile
        return self.loader.results
