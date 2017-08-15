"""Radiation analysis based on Daylight Coefficient Grid-Based Analysis Recipe.

This is a slightly faster implementation for annual radiation analysis using daylight
coefficient based method. This recipe genrates -s sky and add it up with analemma.

See: https://github.com/ladybug-tools/honeybee/issues/167#issue-245745189

"""
from ..recipeutil import writeExtraFiles
from ..recipedcutil import writeRadFilesDaylightCoeff, getCommandsRadiationSky
from ..recipedcutil import getCommandsSceneDaylightCoeff
from ..recipedcutil import getCommandsWGroupsDaylightCoeff
from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...sky.skymatrix import SkyMatrix
from ....futil import writeToFile

import os


class GridBased(DaylightCoeffGridBased):
    """Grid based daylight coefficient analysis recipe.

    Attributes:
        skyMtx: A radiance SkyMatrix or SkyVector. For an SkyMatrix the analysis
            will be ran for the analysis period.
        analysisGrids: A list of Honeybee analysis grids. Daylight metrics will
            be calculated for each analysisGrid separately.
        radianceParameters: Radiance parameters for this analysis. Parameters
            should be an instance of RfluxmtxParameters.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "daylightcoeff").

    """

    def __init__(self, skyMtx, analysisGrids,
                 radianceParameters=None, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="gridbased_radiation"):
        """Create an annual recipe."""

        simulationType = 1

        DaylightCoeffGridBased.__init__(
            self, skyMtx, analysisGrids, simulationType, radianceParameters,
            reuseDaylightMtx, hbObjects, subFolder)

    @classmethod
    def fromWeatherFilePointsAndVectors(
        cls, epwFile, pointGroups, vectorGroups=None, skyDensity=1,
            radianceParameters=None, reuseDaylightMtx=True, hbObjects=None,
            subFolder="gridbased_radiation"):
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
        skyMtx = SkyMatrix.fromEpwFile(epwFile, skyDensity)
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)

        return cls(skyMtx, analysisGrids, radianceParameters,
                   reuseDaylightMtx, hbObjects, subFolder)

    @classmethod
    def fromPointsFile(cls, epwFile, pointsFile, skyDensity=1,
                       radianceParameters=None, reuseDaylightMtx=True, hbObjects=None,
                       subFolder="gridbased_radiation"):
        """Create grid based daylight coefficient recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except Exception:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity,
            radianceParameters, reuseDaylightMtx, hbObjects, subFolder)

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
        projectFolder = \
            super(DaylightCoeffGridBased, self).writeContent(
                targetFolder, projectName, False, subfolders=['tmp', 'result/matrix']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFilesDaylightCoeff(
            projectFolder + '/scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )
        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '/scene')

        # 0.write points
        pointsFile = self.writeAnalysisGrids(projectFolder, projectName)

        # 2.write batch file
        if header:
            self._commands.append(self.header(projectFolder))

        # # 2.1.Create sky matrix.
        # # 2.2. Create sun matrix
        skycommands, skyfiles = getCommandsRadiationSky(
            projectFolder, self.skyMatrix, reuse=True)

        self._commands.extend(skycommands)

        # for each window group - calculate total, direct and direct-analemma results
        # calculate the contribution of glazing if any with all window groups blacked
        inputfiles = opqfiles, glzfiles, wgsfiles, extrafiles
        commands, results = getCommandsSceneDaylightCoeff(
            projectName, self.skyMatrix.skyDensity, projectFolder, skyfiles,
            inputfiles, pointsFile, self.totalPointCount, self.radianceParameters,
            self.reuseDaylightMtx, self.totalRunsCount, radiationOnly=True)

        self._resultFiles.extend(
            os.path.join(projectFolder, str(result)) for result in results
        )

        self._addCommands(skycommands, commands)

        if self.windowGroups:
            # calculate the contribution for all window groups
            commands, results = getCommandsWGroupsDaylightCoeff(
                projectName, self.skyMatrix.skyDensity, projectFolder, self.windowGroups,
                skyfiles, inputfiles, pointsFile, self.totalPointCount,
                self.radianceParameters, self.reuseDaylightMtx, self.totalRunsCount,
                radiationOnly=True)

            self._addCommands(skycommands, commands)
            self._resultFiles.extend(
                os.path.join(projectFolder, str(result)) for result in results
            )

        # # 2.5 write batch file
        batchFile = os.path.join(projectFolder, 'commands.bat')

        # add echo to commands and write them to file
        writeToFile(batchFile, '\n'.join(self.preprocCommands()))

        return batchFile
