from ..parameters import getRadianceParametersGridBased

from ..recipeutil import writeExtraFiles
from ..recipedcutil import getCommandsSceneDaylightCoeff, getCommandsSky

from ..recipexphaseutil import matrixCalculationThreePhase, writeRadFilesMultiPhase
from ..recipexphaseutil import getCommandsViewDaylightMatrices

from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...sky.skymatrix import SkyMatrix
from ....futil import writeToFile

import os


class ThreePhaseGridBased(DaylightCoeffGridBased):
    """Grid based three phase analysis recipe.

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
        analysisRecipe = ThreePhaseGridBased(
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
                 viewMtxParameters=None, daylightMtxParameters=None,
                 reuseViewMtx=True, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="gridbased_threephase"):
        """Create an annual recipe."""
        DaylightCoeffGridBased.__init__(
            self, skyMtx, analysisGrids, simulationType,
            reuseDaylightMtx=reuseDaylightMtx, hbObjects=hbObjects,
            subFolder=subFolder
        )

        self.viewMtxParameters = viewMtxParameters
        self.daylightMtxParameters = daylightMtxParameters
        self.reuseViewMtx = reuseViewMtx

    @classmethod
    def fromWeatherFilePointsAndVectors(
        cls, epwFile, pointGroups, vectorGroups=None, skyDensity=1,
        simulationType=0, viewMtxParameters=None, daylightMtxParameters=None,
        reuseViewMtx=True, reuseDaylightMtx=True, hbWindowSurfaces=None,
            hbObjects=None, subFolder="gridbased_threephase"):
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
            skyMtx, analysisGrids, simulationType, viewMtxParameters,
            daylightMtxParameters, reuseViewMtx, reuseDaylightMtx, hbWindowSurfaces,
            hbObjects, subFolder)

    @classmethod
    def fromPointsFile(
        cls, epwFile, pointsFile, skyDensity=1, simulationType=0,
        viewMtxParameters=None, daylightMtxParameters=None, reuseViewMtx=True,
        reuseDaylightMtx=True, hbWindowSurfaces=None, hbObjects=None,
            subFolder="gridbased_threephase"):
        """Create an annual recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except Exception as e:
            raise ValueError("Couldn't import points from {}:\n\t{}".format(
                pointsFile, e))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity, simulationType,
            viewMtxParameters, daylightMtxParameters, reuseViewMtx, reuseDaylightMtx,
            hbWindowSurfaces, hbObjects, subFolder)

    @property
    def viewMtxParameters(self):
        """View matrix parameters."""
        return self._viewMtxParameters

    @viewMtxParameters.setter
    def viewMtxParameters(self, vm):
        if not vm:
            self._viewMtxParameters = getRadianceParametersGridBased(0, 2).vmtx
        else:
            assert hasattr(vm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(vm)))
            self._viewMtxParameters = vm

        # reset -I option for when parameters are updated.
        if self._simType < 2:
            self._viewMtxParameters.irradianceCalc = True
        else:
            self._viewMtxParameters.irradianceCalc = None

    @property
    def daylightMtxParameters(self):
        """View matrix parameters."""
        return self._daylightMtxParameters

    @daylightMtxParameters.setter
    def daylightMtxParameters(self, dm):
        if not dm:
            self._daylightMtxParameters = getRadianceParametersGridBased(0, 2).dmtx
        else:
            assert hasattr(dm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(dm)))
            self._daylightMtxParameters = dm

        # reset -I option for when parameters are updated.
        if self._simType < 2:
            self._daylightMtxParameters.irradianceCalc = True
        else:
            self._daylightMtxParameters.irradianceCalc = None

    @property
    def skyDensity(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.
            header: A boolean to include path to radiance folder in commands file.

        Returns:
            Path yo commands file.
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        projectFolder = \
            super(DaylightCoeffGridBased, self).writeContent(
                targetFolder, projectName, False, subfolders=['tmp', 'result/matrix']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFilesMultiPhase(
            projectFolder + '/scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )

        assert len(self.windowGroups) > 0, \
            ValueError(
                'Found no window groups! If you do not have a window group'
                ' in the scene use daylight coefficient ')

        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '/scene')

        # 0.write points
        pointsFile = self.writeAnalysisGrids(projectFolder, projectName)
        numberOfPoints = sum(len(ag) for ag in self.analysisGrids)

        # 2.write batch file
        if header:
            self.commands.append(self.header(projectFolder))

        # # 2.1.Create sky matrix.
        # # 2.2. Create sun matrix
        skycommands, skyfiles = getCommandsSky(projectFolder, self.skyMatrix,
                                               reuse=True)

        self._commands.extend(skycommands)

        # for statcic glazing - calculate total, direct and direct-analemma results
        # calculate the contribution of glazing if any with all window groups blacked
        inputfiles = opqfiles, glzfiles, wgsfiles, extrafiles
        commands, results = getCommandsSceneDaylightCoeff(
            projectName, self.skyMatrix.skyDensity, projectFolder, skyfiles,
            inputfiles, pointsFile, self.totalPointCount, self.radianceParameters,
            self.reuseDaylightMtx, self.totalRunsCount)

        self._commands.extend(commands)
        self._resultFiles.extend(
            os.path.join(projectFolder, str(result)) for result in results
        )

        # calculate three-phase for window groups
        for count, wg in enumerate(self.windowGroups):

            commands, vMatrix, dMatrix = getCommandsViewDaylightMatrices(
                projectFolder, wg, count, inputfiles, pointsFile, numberOfPoints,
                self.skyMatrix.skyDensity, self.viewMtxParameters,
                self.daylightMtxParameters, self.reuseViewMtx, self.reuseDaylightMtx)

            self._commands.extend(commands)

            # tMatrix
            cmd, results = matrixCalculationThreePhase(
                projectFolder, wg, vMatrix, dMatrix, skyfiles.skyMtxTotal)

            self._commands.extend(cmd)
            self._resultFiles.extend(results)

        # # 5. write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")
        writeToFile(batchFile, '\n'.join(self.preprocCommands()))

        return batchFile
