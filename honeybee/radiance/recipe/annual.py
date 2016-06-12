from ._gridbasedbase import HBGenericGridBasedAnalysisRecipe
from ..postprocess.annualresults import LoadAnnualsResults
from ..parameters.rfluxmtx import RfluxmtxParameters
from ..command.rfluxmtx import Rfluxmtx
from ..command.epw2wea import Epw2wea
from ..command.gendaymtx import Gendaymtx
from ..command.rmtxop import Rmtxop

from ...helper import preparedir, getRadiancePathLines

import os
import subprocess


class HBAnnualAnalysisRecipe(HBGenericGridBasedAnalysisRecipe):
    """Annual analysis.

    This class calculates number of sunlight hours for a group of test points.

    Attributes:
        epwFile: An EnergyPlus weather file.
        pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test
            points. Each list of test points will be converted to a
            TestPointGroup. If testPts is a single flattened list only one
            TestPointGroup will be created.
        vectorGroups: An optional list of (x, y, z) vectors. Each vector
            represents direction of corresponding point in testPts. If the
            vector is not provided (0, 0, 1) will be assigned.
        skyDensity: A positive intger for sky density. 1: Tregenza Sky,
            2: Reinhart Sky, etc. (Default: 1)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")

    Usage:
        # initiate analysisRecipe
        analysisRecipe = HBAnnualAnalysisRecipe(
            epwFile, testPoints, ptsVectors
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

    def __init__(self, epwFile, pointGroups, vectorGroups=[],
                 skyDensity=1, hbObjects=None, subFolder="annualdaylight"):
        """Create an annual recipe."""
        HBGenericGridBasedAnalysisRecipe.__init__(
            self, pointGroups, vectorGroups, hbObjects, subFolder
        )

        self.epwFile = epwFile

        # TODO: @sarith sky density needs to have check for input values
        self.skyDensity = skyDensity

        # set RfluxmtxParameters as default radiance parameter for annual analysis
        self.__radianceParameters = RfluxmtxParameters()
        self.__radianceParameters.I = True

        # @sarith do we want to set these values as default?
        self.__radianceParameters.aa = 0.1
        self.__radianceParameters.ad = 4096
        self.__radianceParameters.ab = 6
        self.__radianceParameters.lw = 0.001

        self.__batchFile = None
        self.resultsFile = []

        # create a result loader to load the results once the analysis is done.
        self.loader = LoadAnnualsResults(self.resultsFile)

    @classmethod
    def fromPointsFile(cls, epwFile, pointsFile, skyDensity=0, hbObjects=None,
                       subFolder="annualdaylight"):
        """Create an annual recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls(epwFile, pointGroups, vectorGroups, skyDensity, hbObjects,
                   subFolder)

    @property
    def radianceParameters(self):
        """Radiance parameters for annual analysis."""
        return self.__radianceParameters

    @property
    def skyType(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyDensity)

    # TODO: Add path to PATH and use relative path in batch files
    # TODO: @sariths docstring should be modified
    def writeToFile(self, targetFolder, projectName, radFiles=None,
                    useRelativePath=False):
        """Write analysis files to target folder.

        Files for sunlight hours analysis are:
            test points <projectName.pts>: List of analysis points.
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

        # create main folder targetFolder\projectName\annualdaylight
        _path = os.path.join(_basePath, self.subFolder)
        _ispath = preparedir(_path)

        assert _ispath, "Failed to create %s. Try a different path!" % _path

        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 0.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 1.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 2.write batch file
        batchFileLines = []

        # add path if needed
        batchFileLines.append(getRadiancePathLines())

        # TODO: This line won't work in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        batchFileLines.append(dirLine)

        # # 2.1.Create annual daylight vectors through epw2wea and gendaymtx.
        weaFile = Epw2wea(self.epwFile)
        weaFile.outputWeaFile = os.path.join(_path, projectName + ".wea")
        batchFileLines.append(weaFile.toRadString())

        gdm = Gendaymtx(outputName=os.path.join(_path, projectName + ".smx"),
                        weaFile=weaFile.outputWeaFile)

        gdm.gendaymtxParameters.skyDensity = self.skyDensity
        batchFileLines.append(gdm.toRadString())

        # # 2.2.Generate daylight coefficients using rfluxmtx
        rflux = Rfluxmtx(projectName)
        rflux.rfluxmtxParameters = self.radianceParameters

        rflux.sender = '-'

        # I think it should be more explicit that this line is writing the sky
        # to a file - rflux.writeDefaultSkyGroundToFile ?
        skyFile = rflux.defaultSkyGround(os.path.join(_path, "rfluxSky.rad"),
                                         skyType=self.skyType)
        rflux.receiverFile = skyFile
        rflux.radFiles = [matFile, geoFile]
        rflux.pointsFile = pointsFile
        rflux.outputMatrix = os.path.join(_path, projectName + ".dc")

        batchFileLines.append(rflux.toRadString())

        # # 2.3. matrix calculations
        tempmtx = Rmtxop(matrixFiles=(rflux.outputMatrix, gdm.outputFile),
                         outputFile=os.path.join(_path, "illuminance.tmp"))

        batchFileLines.append(tempmtx.toRadString())

        finalmtx = Rmtxop(matrixFiles=[tempmtx.outputFile],
                          outputFile=os.path.join(_path, "illuminance.ill"))
        finalmtx.rmtxopParameters.outputFormat = 'a'
        finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
        finalmtx.rmtxopParameters.transposeMatrix = True
        batchFileLines.append(finalmtx.toRadString())

        # # 2.3 write batch file
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

            self.resultsFile = [os.path.join(os.path.split(self.__batchFile)[0],
                                             "illuminance.ill")]
            return True
        else:
            raise Exception("You need to write the files before running the recipe.")

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        self.loader.resultFiles = self.resultsFile
        return self.loader.results
