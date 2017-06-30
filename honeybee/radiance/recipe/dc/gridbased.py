from .._gridbasedbase import GenericGridBasedAnalysisRecipe
from ...postprocess.annualresults import LoadAnnualsResults
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.rfluxmtx import Rfluxmtx
from ...command.gendaymtx import Gendaymtx
from ...command.dctimestep import Dctimestep
from ...command.rmtxop import Rmtxop
from ...sky.skymatrix import SkyMatrix
from ....futil import writeToFile

import os


# TODO: implement simulationType
class DaylightCoeffGridBasedAnalysisRecipe(GenericGridBasedAnalysisRecipe):
    """Grid based daylight coefficient analysis recipe.

    Attributes:
        skyMtx: A radiance SkyMatrix or SkyVector. For an SkyMatrix the analysis
            will be ran for the analysis period.
        analysisGrids: A list of Honeybee analysis grids. Daylight metrics will
            be calculated for each analysisGrid separately.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radianceParameters: Radiance parameters for this analysis. Parameters
            should be an instance of RfluxmtxParameters.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "daylightcoeff").


    Usage:

        # initiate analysisRecipe
        analysisRecipe = DaylightCoeffGridBasedAnalysisRecipe(
            skyMtx, analysisGrids, radParameters
            )

        # add honeybee object
        analysisRecipe.hbObjects = HBObjs

        # write analysis files to local drive
        commandsFile = analysisRecipe.write(_folder_, _name_)

        # run the analysis
        analysisRecipe.run(commandsFile)

        # get the results
        print analysisRecipe.results()
    """

    def __init__(self, skyMtx, analysisGrids, simulationType=0,
                 radianceParameters=None, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="gridbased_daylightcoeff"):
        """Create an annual recipe."""
        GenericGridBasedAnalysisRecipe.__init__(
            self, analysisGrids, hbObjects, subFolder
        )

        assert hasattr(skyMtx, 'skyDensity'), \
            TypeError('{} is not a SkyMatrix'.format(skyMtx))

        self.skyMatrix = skyMtx

        self.radianceParameters = radianceParameters
        self.reuseDaylightMtx = reuseDaylightMtx
        # create a result loader to load the results once the analysis is done.
        self.loader = LoadAnnualsResults(self.resultsFile)

    @classmethod
    def fromWeatherFilePointsAndVectors(
        cls, epwFile, pointGroups, vectorGroups=None, skyDensity=1,
            simulationType=0, radianceParameters=None, reuseDaylightMtx=True,
            hbObjects=None,
            subFolder="gridbased_daylightcoeff"):
        """Create grid based daylight coefficient from weather file, points and vectors.

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

        return cls(skyMtx, analysisGrids, simulationType, radianceParameters,
                   reuseDaylightMtx, hbObjects, subFolder)

    @classmethod
    def fromPointsFile(cls, epwFile, pointsFile, skyDensity=1,
                       simulationType=0, radianceParameters=None,
                       reuseDaylightMtx=True, hbObjects=None,
                       subFolder="gridbased_daylightcoeff"):
        """Create grid based daylight coefficient recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except Exception:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity, simulationType,
            radianceParameters, reuseDaylightMtx, hbObjects, subFolder)

    @property
    def radianceParameters(self):
        """Radiance parameters for annual analysis."""
        return self.__radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            self.__radianceParameters = RfluxmtxParameters()
            self.__radianceParameters.irradianceCalc = True
            self.__radianceParameters.ambientAccuracy = 0.1
            self.__radianceParameters.ambientDivisions = 4096
            self.__radianceParameters.ambientBounces = 6
            self.__radianceParameters.limitWeight = 0.001
        else:
            assert hasattr(par, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))
            self.__daylightMtxParameters = par

    @property
    def skyType(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    # TODO: docstring should be modified
    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.
            header: A boolean to include the header lines in commands.bat. header
                includes PATH and cd toFolder
        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        sceneFiles = super(
            GenericGridBasedAnalysisRecipe, self).populateSubFolders(
                targetFolder, projectName,
                subFolders=('.tmp', 'objects', 'skies', 'results', 'results\\matrix'),
                removeSubFoldersContent=False)

        # 0.write points
        pointsFile = self.writePointsToFile(sceneFiles.path, projectName)

        # 2.write batch file
        self.commands = []
        self.resultsFile = []

        if header:
            self.commands.append(self.header(sceneFiles.path))

        # 2.1.Create sky matrix.
        if hasattr(self.skyMatrix, 'isSkyMatrix'):
            weaFilepath = 'skies\\{}.wea'.format(self.skyMatrix.name)
            skyMtx = 'skies\\{}.smx'.format(self.skyMatrix.name)
            hoursFile = os.path.join(
                sceneFiles.path, 'skies\\{}.hrs'.format(self.skyMatrix.name))
            if not os.path.isfile(os.path.join(sceneFiles.path, skyMtx)) \
                or not os.path.isfile(os.path.join(sceneFiles.path, weaFilepath)) \
                    or not self.skyMatrix.hoursMatch(hoursFile):
                self.skyMatrix.writeWea(
                    os.path.join(sceneFiles.path, 'skies'), writeHours=True)
                gdm = Gendaymtx(outputName=skyMtx, weaFile=weaFilepath)
                gdm.gendaymtxParameters.skyDensity = self.skyMatrix.skyDensity
                self.commands.append(gdm.toRadString())
        else:
            # sky vector
            skyMtx = 'skies\\{}.vec'.format(self.skyMatrix.name)
            wdir = os.path.join(sceneFiles.path, 'skies')
            if not os.path.isfile(os.path.join(sceneFiles.path, skyMtx)):
                self.skyMatrix.execute(wdir)
                # TODO: adding this line to command line didn't work on windows
                # self.commands.append(self.skyMatrix.toRadString(wdir, sceneFiles.path))

        # # 2.2.Generate daylight coefficients using rfluxmtx
        rfluxFiles = [sceneFiles.matFile, sceneFiles.geoFile] + \
            sceneFiles.matFilesAdd + sceneFiles.radFilesAdd + sceneFiles.octFilesAdd

        dMatrix = 'results\\matrix\\{}_{}_{}.dc'.format(
            projectName, self.skyMatrix.skyDensity, self.numOfTotalPoints)
        if not os.path.isfile(os.path.join(sceneFiles.path, dMatrix)) \
                or not self.reuseDaylightMtx:
            rflux = Rfluxmtx()
            rflux.rfluxmtxParameters = self.radianceParameters
            rflux.radFiles = tuple(self.relpath(f, sceneFiles.path) for f in rfluxFiles)
            rflux.sender = '-'
            skyFile = rflux.defaultSkyGround(
                os.path.join(sceneFiles.path, 'skies\\rfluxSky.rad'),
                skyType=self.skyType)
            rflux.receiverFile = self.relpath(skyFile, sceneFiles.path)
            rflux.pointsFile = pointsFile
            rflux.outputMatrix = dMatrix
            self.commands.append(rflux.toRadString())

        # # 2.3. matrix calculations
        dct = Dctimestep()
        dct.skyVectorFile = skyMtx
        dct.dmatrixFile = dMatrix
        dct.outputFile = '.tmp\\illuminance.tmp'
        self.commands.append(dct.toRadString())

        finalmtx = Rmtxop(matrixFiles=(dct.outputFile,),
                          outputFile='results\\illuminance.ill')
        finalmtx.rmtxopParameters.outputFormat = 'a'
        finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
        finalmtx.rmtxopParameters.transposeMatrix = False
        self.commands.append(finalmtx.toRadString())

        # # 2.3 write batch file
        batchFile = os.path.join(sceneFiles.path, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        self.resultsFile = (os.path.join(sceneFiles.path, str(finalmtx.outputFile)),)

        print "Files are written to: %s" % sceneFiles.path
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        for r in self.resultsFile:
            # source, state = os.path.split(r)[-1][:-4].split("..")
            self.analysisGrids[0].setValuesFromFile(r, self.skyMatrix.hoys)
        return self.analysisGrids
