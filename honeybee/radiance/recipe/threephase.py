from .annual import HBAnnualAnalysisRecipe
from ..postprocess.annualresults import LoadAnnualsResults
from ..parameters.rfluxmtx import RfluxmtxParameters
from ..command.dctimestep import Dctimestep
from ..command.rfluxmtx import Rfluxmtx
from ..command.rmtxop import Rmtxop
from ..material.glow import GlowMaterial
from ..sky.skymatrix import SkyMatrix

from ...helper import preparedir, getRadiancePathLines

import os
import subprocess


class HBThreePhaseAnalysisRecipe(HBAnnualAnalysisRecipe):
    """Annual analysis recipe.

    Attributes:

        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "threephase")

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

    def __init__(self, skyMtx, analysisGrids, viewMtxParameters=None,
                 daylightMtxParameters=None, reuseViewMtx=True,
                 reuseDaylightMtx=True, hbObjects=None, subFolder="threephase"):
        """Create an annual recipe."""
        HBAnnualAnalysisRecipe.__init__(
            self, skyMtx, analysisGrids, hbObjects=hbObjects, subFolder=subFolder
        )

        self.viewMtxParameters = viewMtxParameters
        self.daylightMtxParameters = daylightMtxParameters
        self.reuseViewMtx = reuseViewMtx
        self.reuseDaylightMtx = reuseDaylightMtx
        self.__batchFile = None
        self.resultsFile = []

        # create a result loader to load the results once the analysis is done.
        self.loader = LoadAnnualsResults(self.resultsFile)

    @classmethod
    def fromWeatherFilePointsAndVectors(
        cls, epwFile, pointGroups, vectorGroups=None, skyDensity=1,
        viewMtxParameters=None, daylightMtxParameters=None, reuseViewMtx=True,
            reuseDaylightMtx=True, hbObjects=None, subFolder="threephase"):
        """Create three-phase recipe from weather file, points and vectors.

        Args:
            epwFile: An EnergyPlus weather file.
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            skyDensity: A positive intger for sky density. 1: Tregenza Sky,
                2: Reinhart Sky, etc. (Default: 1)
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        assert epwFile.lower().endswith('.epw'), \
            ValueError('{} is not a an EnergyPlus weather file.'.format(epwFile))
        skyMtx = SkyMatrix(epwFile, skyDensity)
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)

        return cls(
            skyMtx, analysisGrids, viewMtxParameters, daylightMtxParameters,
            reuseViewMtx, reuseDaylightMtx, hbObjects, subFolder)

    @classmethod
    def fromPointsFile(
        cls, epwFile, pointsFile, skyDensity=1, viewMtxParameters=None,
        daylightMtxParameters=None, reuseViewMtx=True, reuseDaylightMtx=True,
            hbObjects=None, subFolder="threephase"):
        """Create an annual recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity, viewMtxParameters,
            daylightMtxParameters, reuseViewMtx, reuseDaylightMtx, hbObjects,
            subFolder)

    @property
    def viewMtxParameters(self):
        """View matrix parameters."""
        return self.__viewMtxParameters

    @viewMtxParameters.setter
    def viewMtxParameters(self, vm):
        if not vm:
            self.__viewMtxParameters = RfluxmtxParameters()
            self.__viewMtxParameters.irradianceCalc = True
            self.__viewMtxParameters.ambientAccuracy = 0.1
            self.__viewMtxParameters.ambientBounces = 10
            self.__viewMtxParameters.ambientDivisions = 65536
            self.__viewMtxParameters.limitWeight = 1E-5
        else:
            assert hasattr(vm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(vm)))
            self.__viewMtxParameters = vm

    @property
    def daylightMtxParameters(self):
        """View matrix parameters."""
        return self.__daylightMtxParameters

    @daylightMtxParameters.setter
    def daylightMtxParameters(self, dm):
        if not dm:
            self.__daylightMtxParameters = RfluxmtxParameters()
            self.__daylightMtxParameters.ambientAccuracy = 0.1
            self.__daylightMtxParameters.ambientDivisions = 1024
            self.__daylightMtxParameters.ambientBounces = 2
            self.__daylightMtxParameters.limitWeight = 0.0000001

        else:
            assert hasattr(dm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(dm)))
            self.__daylightMtxParameters = dm

    @property
    def skyType(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

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
        _ispath = preparedir(_basePath, removeContent=False)
        assert _ispath, "Failed to create %s. Try a different path!" % _basePath

        # create main folder targetFolder\projectName\threephase
        _path = os.path.join(_basePath, self.subFolder)
        _ispath = preparedir(_path, removeContent=False)

        assert _ispath, "Failed to create %s. Try a different path!" % _path

        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 0.create a place holder for batch file
        batchFileLines = []
        # add path if needed
        batchFileLines.append(getRadiancePathLines())

        # TODO: This line won't work in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        batchFileLines.append(dirLine)

        # 1.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 2.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 3.0. find glazing items with .xml material, write them to a separate
        # file and invert them
        bsdfGlazing = tuple(f for f in self.hbObjects
                            if hasattr(f.radianceMaterial, 'xmlfile'))[0].duplicate()

        tMatrix = bsdfGlazing.radianceMaterial.xmlfile

        # maek a copy of the glass and change the material to glow
        bsdfGlazing.radianceMaterial = GlowMaterial(
            bsdfGlazing.radianceMaterial.name + '_glow', 1, 1, 1)
        glassPath = os.path.join(_path, 'glazing.rad')

        bsdfGlazing.radStringToFile(glassPath, includeMaterials=True, reverse=True)

        # # 3.1.Create annual daylight vectors through epw2wea and gendaymtx.
        skyMtx = self.skyMatrix.execute(_path, reuse=True)

        # # 3.2.Generate view matrix
        if not os.path.isfile(os.path.join(_path, projectName + ".vmx")) or \
                not self.reuseViewMtx:
            rflux = Rfluxmtx(projectName)
            rflux.sender = '-'
            rflux.rfluxmtxParameters = self.viewMtxParameters
            # This needs to be automated based on the normal of each window.
            # Klems full basis sampling and the window faces +Y
            recCtrlPar = rflux.ControlParameters(
                hemiType='kf', hemiUpDirection=bsdfGlazing.upnormal)
            rflux.receiverFile = rflux.addControlParameters(
                glassPath, {bsdfGlazing.radianceMaterial.name: recCtrlPar})

            rflux.radFiles = (matFile, geoFile, 'glazing.rad')
            rflux.pointsFile = pointsFile
            rflux.outputMatrix = projectName + ".vmx"
            batchFileLines.append(rflux.toRadString())
            vMatrix = rflux.outputMatrix
        else:
            vMatrix = projectName + ".vmx"

        # 3.3 daylight matrix
        if not os.path.isfile(os.path.join(_path, projectName + ".dmx")) or \
                not self.reuseDaylightMtx:
            rflux2 = Rfluxmtx()
            rflux2.samplingRaysCount = 1000
            try:
                # This will fail in case of not re-using daylight matrix
                rflux2.sender = rflux.receiverFile
            except UnboundLocalError:
                rflux2.sender = glassPath[:-4] + '_m' + glassPath[-4:]

            skyFile = rflux2.defaultSkyGround(
                os.path.join(_path, 'rfluxSky.rad'),
                skyType='r{}'.format(self.skyMatrix.skyDensity))

            rflux2.receiverFile = skyFile
            rflux2.rfluxmtxParameters = self.daylightMtxParameters
            rflux2.radFiles = (matFile, geoFile, 'glazing.rad')
            rflux2.outputMatrix = projectName + ".dmx"
            batchFileLines.append(rflux2.toRadString())
            dMatrix = rflux2.outputMatrix
        else:
            dMatrix = projectName + ".dmx"

        # 4. matrix calculations
        dct = Dctimestep()
        dct.tmatrixFile = tMatrix
        dct.vmatrixSpec = vMatrix
        dct.dmatrixFile = str(dMatrix)
        dct.skyVectorFile = skyMtx
        dct.outputFileName = r"illuminance.tmp"
        batchFileLines.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalmtx = Rmtxop(matrixFiles=[dct.outputFileName],
                          outputFile="illuminance.ill")
        finalmtx.rmtxopParameters.outputFormat = 'a'
        finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
        finalmtx.rmtxopParameters.transposeMatrix = True
        batchFileLines.append(finalmtx.toRadString())

        # 6. write batch file
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
