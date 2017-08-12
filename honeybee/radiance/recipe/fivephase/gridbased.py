from ..recipeutil import writeExtraFiles
from ..recipexphaseutil import writeRadFilesMultiPhase, matrixCalculationFivePhase
from ..recipedcutil import getCommandsSceneDaylightCoeff, getCommandsSky
from ..recipexphaseutil import getCommandsViewDaylightMatrices
from ..recipexphaseutil import getCommandsDirectViewDaylightMatrices

from ..threephase.gridbased import ThreePhaseGridBased
from ....futil import writeToFile

import os


class FivePhaseGridBased(ThreePhaseGridBased):
    """Grid based five phase analysis recipe.

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
                 subFolder="gridbased_fivephase"):
        """Create an annual recipe."""
        ThreePhaseGridBased.__init__(
            self, skyMtx, analysisGrids, simulationType,
            viewMtxParameters, daylightMtxParameters,
            reuseViewMtx, reuseDaylightMtx, hbObjects,
            subFolder)

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
            super(ThreePhaseGridBased, self).writeContent(
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

        # for each window group - calculate total, direct and direct-analemma results
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

        for count, wg in enumerate(self.windowGroups):

            # vMatrix and dMatrix
            commands, vMatrix, dMatrix = getCommandsViewDaylightMatrices(
                projectFolder, wg, count, inputfiles, pointsFile, numberOfPoints,
                self.skyMatrix.skyDensity, self.viewMtxParameters,
                self.daylightMtxParameters, self.reuseViewMtx, self.reuseDaylightMtx,
                phasesCount=5)

            self._commands.extend(commands)

            # direct vMatrix and dMatrix
            commands, dvMatrix, ddMatrix = getCommandsDirectViewDaylightMatrices(
                projectFolder, wg, count, inputfiles, pointsFile, numberOfPoints,
                self.skyMatrix.skyDensity, self.viewMtxParameters,
                self.daylightMtxParameters, self.reuseViewMtx, self.reuseDaylightMtx)

            self._commands.extend(commands)

            counter = 2 + sum(wg.stateCount for wg in self.windowGroups[:count])

            # tMatrix - direct + analemma
            # TODO(mostapha): send the enalysis grid and not the points file
            # otherwise we won't be able to support multiple grids.
            cmd, results = matrixCalculationFivePhase(
                projectName, self.skyMatrix.skyDensity, projectFolder, wg, skyfiles,
                inputfiles, pointsFile, self.totalPointCount, self.daylightMtxParameters,
                vMatrix, dMatrix, dvMatrix, ddMatrix, count, self.reuseViewMtx,
                self.reuseDaylightMtx, (counter, self.totalRunsCount))

            self._commands.extend(cmd)
            self._resultFiles.extend(results)

        # # 5. write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")
        writeToFile(batchFile, '\n'.join(self.preprocCommands()))

        return batchFile
