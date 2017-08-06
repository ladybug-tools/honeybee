"""Radiance Daylight Coefficient Grid-Based Analysis Recipe."""
from ..recipeutil import writeExtraFiles
from ..recipedcutil import writeRadFilesDaylightCoeff, getCommandsSky
from ..recipedcutil import getCommandsSceneDaylightCoeff
from ..recipedcutil import getCommandsWGroupsDaylightCoeff
from .._gridbasedbase import GenericGridBased
from ..parameters import getRadianceParametersGridBased
from ...sky.skymatrix import SkyMatrix
from ....futil import writeToFile

import os


class DaylightCoeffGridBased(GenericGridBased):
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
        analysisRecipe = DaylightCoeffGridBased(
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
        GenericGridBased.__init__(
            self, analysisGrids, hbObjects, subFolder
        )

        self.skyMatrix = skyMtx

        self.radianceParameters = radianceParameters

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 2)
        """

        self.reuseDaylightMtx = reuseDaylightMtx

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
        skyMtx = SkyMatrix.fromEpwFile(epwFile, skyDensity)
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
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except TypeError:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.skyMatrix.isClimateBased, \
                "The sky for radition analysis should be climate-based."

        self._simType = value
        self.skyMatrix.skyType = value

        if self._simType < 2:
            self.radianceParameters.irradianceCalc = True
        else:
            self.radianceParameters.irradianceCalc = None

        if hasattr(self, 'viewMtxParameters'):
            if self._simType < 2:
                self.viewMtxParameters.irradianceCalc = True
            else:
                self.viewMtxParameters.irradianceCalc = None

        if hasattr(self, 'daylightMtxParameters'):
            if self._simType < 2:
                self.daylightMtxParameters.irradianceCalc = True
            else:
                self.daylightMtxParameters.irradianceCalc = None

    @property
    def skyMatrix(self):
        """Get and set sky definition."""
        return self._skyMatrix

    @skyMatrix.setter
    def skyMatrix(self, newSky):
        assert hasattr(newSky, 'isRadianceSky'), \
            '%s is not a valid Honeybee sky.' % type(newSky)
        assert not newSky.isPointInTime, \
            TypeError('Sky for daylight coefficient recipe must be a sky matrix.')
        self._skyMatrix = newSky.duplicate()

    @property
    def radianceParameters(self):
        """Radiance parameters for annual analysis."""
        return self._radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            par = getRadianceParametersGridBased(0, 1).dmtx

        assert hasattr(par, 'isRfluxmtxParameters'), \
            TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))

        self._radianceParameters = par

    @property
    def skyDensity(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    @property
    def totalRunsCount(self):
        """Number of total runs for all window groups and states."""
        return sum(wg.stateCount for wg in self.windowGroups) + 1  # 1 for base case

    def preprocCommands(self):
        """Add echo in front of comments in batch file comments."""
        cmd = [c for c in self._commands if c]
        cmd = ['echo ' + c if c[:2] == '::' else c for c in cmd]
        return ['@echo off'] + cmd

    def _addCommands(self, skycommands, commands):
        """Check if the commands should be added to self._commands."""
        if self.reuseDaylightMtx:
            if not skycommands:
                for f in self._resultFiles:
                    if not os.path.isfile(f):
                        self._commands.extend(commands)
                        break
            else:
                # there are changes in the sky.
                # matrices multiplication needs to be recalculated.
                self._commands.extend(commands)
        else:
            # there are changes in the sky.
            # matrices multiplication needs to be recalculated.
            self._commands.extend(commands)

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
            super(GenericGridBased, self).writeContent(
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

        self._resultFiles.extend(
            os.path.join(projectFolder, str(result)) for result in results
        )

        self._addCommands(skycommands, commands)

        if self.windowGroups:
            # calculate the contribution for all window groups
            commands, results = getCommandsWGroupsDaylightCoeff(
                projectName, self.skyMatrix.skyDensity, projectFolder, self.windowGroups,
                skyfiles, inputfiles, pointsFile, self.totalPointCount,
                self.radianceParameters, self.reuseDaylightMtx, self.totalRunsCount)

            self._addCommands(skycommands, commands)
            self._resultFiles.extend(
                os.path.join(projectFolder, str(result)) for result in results
            )

        # # 2.5 write batch file
        batchFile = os.path.join(projectFolder, 'commands.bat')

        # add echo to commands and write them to file
        writeToFile(batchFile, '\n'.join(self.preprocCommands()))

        return batchFile

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysisGrids:
            ag.unload()

        # results are merged as a single file
        for rf in self._resultFiles:
            fn = os.path.split(rf)[-1][:-4].split("..")
            source = fn[-2]
            state = fn[-1]

            folder, name = os.path.split(rf)
            df = os.path.join(folder, 'sun..%s' % name)
            mode = 179 if self.simulationType == 1 else 0
            startLine = 0
            for count, analysisGrid in enumerate(self.analysisGrids):
                if count:
                    startLine += len(self.analysisGrids[count - 1])

                if not os.path.exists(df):
                    print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                          .format(analysisGrid.name, source, state, rf))
                    # total value only
                    analysisGrid.setValuesFromFile(
                        rf, self.skyMatrix.hoys, source, state, startLine=startLine,
                        header=True, checkPointCount=False, mode=mode
                    )
                else:
                    # total and direct values
                    print(
                        '\nloading total and direct results for {} AnalysisGrid'
                        ' from {}::{}\n{}\n{}\n'.format(
                            analysisGrid.name, source, state, rf, df))

                    analysisGrid.setCoupledValuesFromFile(
                        rf, df, self.skyMatrix.hoys, source, state,
                        startLine=startLine, header=True, checkPointCount=False,
                        mode=mode
                    )

        return self.analysisGrids
