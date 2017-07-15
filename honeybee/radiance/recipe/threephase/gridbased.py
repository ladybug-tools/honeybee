from ..recipeutil import writeRadFilesMultiPhase, writeExtraFiles, getCommandsSky
from ..recipeutil import coeffMatrixCommands, matrixCalculation, RGBMatrixFileToIll
from ..recipeutil import skyReceiver, getCommandsSceneDaylightCoeff
from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...parameters.rfluxmtx import RfluxmtxParameters
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
            self, skyMtx, analysisGrids, simulationType, hbObjects=hbObjects,
            subFolder=subFolder
        )

        self.viewMtxParameters = viewMtxParameters
        self.daylightMtxParameters = daylightMtxParameters
        self.reuseViewMtx = reuseViewMtx
        self.reuseDaylightMtx = reuseDaylightMtx

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
            self._viewMtxParameters = RfluxmtxParameters()
            self._viewMtxParameters.irradianceCalc = True
            self._viewMtxParameters.ambientAccuracy = 0.1
            self._viewMtxParameters.ambientBounces = 10
            self._viewMtxParameters.ambientDivisions = 65536
            self._viewMtxParameters.limitWeight = 1E-5
        else:
            assert hasattr(vm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(vm)))
            self._viewMtxParameters = vm

    @property
    def daylightMtxParameters(self):
        """View matrix parameters."""
        return self._daylightMtxParameters

    @daylightMtxParameters.setter
    def daylightMtxParameters(self, dm):
        if not dm:
            self._daylightMtxParameters = RfluxmtxParameters()
            self._daylightMtxParameters.ambientAccuracy = 0.1
            self._daylightMtxParameters.ambientDivisions = 1024
            self._daylightMtxParameters.ambientBounces = 2
            self._daylightMtxParameters.limitWeight = 0.0000001

        else:
            assert hasattr(dm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(dm)))
            self._daylightMtxParameters = dm

    @property
    def skyDensity(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    # TODO(): docstring should be modified
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
            # add material file
            blkmaterial = [wgsfiles[count].fpblk[0]]
            # add all the blacked window groups but the one in use
            # and finally add non-window group glazing as black
            wgsblacked = \
                [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count] + \
                list(glzfiles.fpblk)

            # for scount, state in enumerate(wg.states):
            # 2.3.Generate daylight coefficients using rfluxmtx
            # collect list of radiance files in the scene for both total and direct
            self._commands.append(
                '\n:: calculation for window group {}'.format(wg.name)
            )

            vreceiver = wgsfiles[count].fp[0]

            vrfluxScene = (
                f for fl in
                (opqfiles.fp, blkmaterial, wgsblacked)
                for f in fl)

            drfluxScene = (
                f for fl in
                (opqfiles.fp, extrafiles.fp, blkmaterial, wgsblacked)
                for f in fl)

            # 3.2.Generate view matrix
            vMatrix = 'result\\matrix\\{}.vmx'.format(wg.name)
            if not os.path.isfile(os.path.join(projectFolder, vMatrix)) \
                    or not self.reuseViewMtx:
                self.commands.append(':: :: 1. view matrix calculation')
                # prepare input files
                radFiles = tuple(self.relpath(f, projectFolder) for f in vrfluxScene)

                vmtx = coeffMatrixCommands(
                    vMatrix, self.relpath(vreceiver, projectFolder), radFiles, '-',
                    self.relpath(pointsFile, projectFolder), numberOfPoints,
                    None, self.viewMtxParameters)

                self.commands.append(vmtx.toRadString())

            # 3.3 daylight matrix
            dMatrix = 'result\\matrix\\{}_{}.dmx'.format(
                wg.name, self.skyMatrix.skyDensity)

            if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
                    or not self.reuseDaylightMtx:
                sender = self.relpath(vreceiver, projectFolder)

                receiver = skyReceiver(
                    os.path.join(projectFolder, 'sky\\rfluxSky.rad'),
                    self.skyMatrix.skyDensity
                )

                samplingRaysCount = 1000
                radFiles = tuple(self.relpath(f, projectFolder) for f in drfluxScene)

                dmtx = coeffMatrixCommands(
                    dMatrix, self.relpath(receiver, projectFolder), radFiles,
                    sender, None, None, samplingRaysCount, self.daylightMtxParameters)

                self.commands.append(':: :: 2. daylight matrix calculation')
                self.commands.append(dmtx.toRadString())

            for count, state in enumerate(wg.states):
                # 4. matrix calculations
                wg.state = count
                tMatrix = 'scene\\bsdf\\{}'.format(
                    os.path.split(wg.radianceMaterial.xmlfile)[-1])
                output = r'tmp\\{}..{}.tmp'.format(wg.name, state.name)
                dct = matrixCalculation(output, vMatrix, tMatrix, dMatrix,
                                        skyfiles.skyMtxTotal)

                self.commands.append(
                    ':: :: 3.1.{} final matrix calculation for {}'.format(count,
                                                                          state.name))
                self.commands.append(dct.toRadString())

                # 5. convert r, g ,b values to illuminance
                finalOutput = r'result\\{}..{}.ill'.format(wg.name, state.name)
                finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
                self.commands.append(
                    ':: :: 3.2.{} convert RGB values to illuminance for {}'.format(
                        count, state.name)
                )
                self.commands.append(finalmtx.toRadString())

                self._resultFiles.append(os.path.join(projectFolder, finalOutput))

        # # 5. write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")
        writeToFile(batchFile, "\n".join(self.commands))

        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        # self.loader.resultFiles = self._resultFiles
        for r in self._resultFiles:
            source, state = os.path.split(r)[-1][:-4].split("..")
            self.analysisGrids[0].setValuesFromFile(r, self.skyMatrix.hoys,
                                                    source, state)
        return self.analysisGrids
