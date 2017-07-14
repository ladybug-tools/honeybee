"""Radiance Daylight Coefficient Grid-Based Analysis Recipe."""
from ..recipeutil import writeRadFilesDaylightCoeff, writeExtraFiles
from ..recipeutil import coeffMatrixCommands, matrixCalculation, RGBMatrixFileToIll
from ..recipeutil import skyReceiver, skymtxToGendaymtx, finalMatrixAddition
from ..recipeutil import sunCoeffMatrixCommands, sunMatrixCalculation, glzSrfTowinGroup
from .._gridbasedbase import GenericGridBased
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...sky.skymatrix import SkyMatrix
from ...sky.sunmatrix import SunMatrix
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

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 2)
        """

        self.radianceParameters = radianceParameters
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
        self._skyMatrix = newSky

    @property
    def radianceParameters(self):
        """Radiance parameters for annual analysis."""
        return self._radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            self._radianceParameters = RfluxmtxParameters()
            self._radianceParameters.irradianceCalc = True
            self._radianceParameters.ambientAccuracy = 0.1
            self._radianceParameters.ambientDivisions = 4096
            self._radianceParameters.ambientBounces = 5
            self._radianceParameters.limitWeight = 0.0002
        else:
            assert hasattr(par, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))
            self._radianceParameters = par

    @property
    def skyDensity(self):
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
        self.skyMatrix.mode = 0
        skyMtxTotal = 'sky\\{}.smx'.format(self.skyMatrix.name)
        self.skyMatrix.mode = 1
        skyMtxDirect = 'sky\\{}.smx'.format(self.skyMatrix.name)
        self.skyMatrix.mode = 0

        # add commands for total and direct sky matrix.
        if hasattr(self.skyMatrix, 'isSkyMatrix'):
            for m in xrange(2):
                self.skyMatrix.mode = m
                gdm = skymtxToGendaymtx(self.skyMatrix, projectFolder)
                if gdm:
                    note = ':: {} sky matrix'.format('direct' if m else 'total')
                    self._commands.extend((note, gdm))
            self.skyMatrix.mode = 0
        else:
            # sky vector
            raise TypeError('You must use a SkyMatrix to generate the sky.')

        # # 2.2. Create sun matrix
        sm = SunMatrix(self.skyMatrix.wea, self.skyMatrix.north,
                       self.skyMatrix.hoys, self.simulationType)
        analemma, sunlist, analemmaMtx = \
            sm.execute(os.path.join(projectFolder, 'sky'))

        # for each window group - calculate total, direct and direct-analemma results
        # I can just add fenestration rad files here and that will work!

        # calculate the contribution of glazing if any with all window groups blacked
        # this is a hack. A better solution is to create a HBDynamicSurface from glazing
        # surfaces. The current limitation is that HBDynamicSurface can't have several
        # surfaces with different materials.
        allWindowGroups = [glzSrfTowinGroup()]
        allWindowGroups.extend(self.windowGroups)
        allWgsFiles = [glzfiles] + list(wgsfiles)

        for count, wg in enumerate(allWindowGroups):
            if count == 0:
                if len(wgsfiles) > 0:
                    blkmaterial = [wgsfiles[0].fpblk[0]]
                    wgsblacked = [f.fpblk[1] for c, f in enumerate(wgsfiles)]
                else:
                    blkmaterial = []
                    wgsblacked = []
            else:
                # add material file
                blkmaterial = [allWgsFiles[count].fpblk[0]]
                # add all the blacked window groups but the one in use
                # and finally add non-window group glazing as black
                wgsblacked = \
                    [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count - 1] + \
                    list(glzfiles.fpblk)

            for scount, state in enumerate(wg.states):
                # 2.3.Generate daylight coefficients using rfluxmtx
                # collect list of radiance files in the scene for both total and direct
                self._commands.append(
                    '\n:: calculation for {} window group {}'.format(wg.name, state.name)
                )

                if count == 0:
                    # normal glazing
                    nonBlackedWgfiles = allWgsFiles[count].fp
                else:
                    nonBlackedWgfiles = (allWgsFiles[count].fp[scount],)

                rfluxScene = (
                    f for fl in
                    (nonBlackedWgfiles, opqfiles.fp, extrafiles.fp,
                     blkmaterial, wgsblacked)
                    for f in fl)

                rfluxSceneBlacked = (
                    f for fl in
                    (nonBlackedWgfiles, opqfiles.fpblk, extrafiles.fpblk,
                     blkmaterial, wgsblacked)
                    for f in fl)

                dMatrix = 'result\\matrix\\normal_{}_{}..{}..{}.dc'.format(
                    projectName, self.skyMatrix.skyDensity, wg.name, state.name)

                dMatrixDirect = 'result\\matrix\\black_{}_{}..{}..{}.dc'.format(
                    projectName, self.skyMatrix.skyDensity, wg.name, state.name)

                sunMatrix = 'result\\matrix\\sun_{}_{}..{}..{}.dc'.format(
                    projectName, self.skyMatrix.skyDensity, wg.name, state.name)

                if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
                        or not self.reuseDaylightMtx:
                    radFiles = tuple(self.relpath(f, projectFolder) for f in rfluxScene)
                    sender = '-'
                    receiver = skyReceiver(
                        os.path.join(projectFolder, 'sky\\rfluxSky.rad'),
                        self.skyMatrix.skyDensity
                    )

                    self._commands.append(
                        ':: :: 1. daylight matrix {} > state {}'.format(wg.name,
                                                                        state.name)
                    )

                    self._commands.append(':: :: 1.1 scene daylight matrix')
                    # samplingRaysCount = 1 based on @sariths studies
                    self.radianceParameters.ambientBounces = 5
                    rflux = coeffMatrixCommands(
                        dMatrix, self.relpath(receiver, projectFolder), radFiles, sender,
                        self.relpath(pointsFile, projectFolder), self.totalPointCount,
                        1, self.radianceParameters
                    )
                    self._commands.append(rflux.toRadString())

                    radFilesBlacked = tuple(self.relpath(f, projectFolder)
                                            for f in rfluxSceneBlacked)

                    self._commands.append(':: :: 1.2 blacked scene daylight matrix')
                    self.radianceParameters.ambientBounces = 1
                    rfluxDirect = coeffMatrixCommands(
                        dMatrixDirect, self.relpath(receiver, projectFolder),
                        radFilesBlacked, sender, self.relpath(pointsFile, projectFolder),
                        self.totalPointCount, None, self.radianceParameters
                    )
                    self._commands.append(rfluxDirect.toRadString())

                    self._commands.append(':: :: 1.3 blacked scene analemma matrix')
                    sunCommands = sunCoeffMatrixCommands(
                        sunMatrix, self.relpath(pointsFile, projectFolder),
                        radFilesBlacked, self.relpath(analemma, projectFolder),
                        self.relpath(sunlist, projectFolder)
                    )

                    self._commands.extend(cmd.toRadString() for cmd in sunCommands)

                self._commands.append(':: :: 2.1.0 total daylight matrix calculations')
                dctTotal = matrixCalculation(
                    'tmp\\total..{}..{}.rgb'.format(wg.name, state.name),
                    dMatrix=dMatrix, skyMatrix=skyMtxTotal
                )
                self._commands.append(dctTotal.toRadString())

                self._commands.append(':: :: 2.1.1 convert RGB values to illuminance')
                finalmtx = RGBMatrixFileToIll(
                    (dctTotal.outputFile,),
                    'result\\total..{}..{}.ill'.format(wg.name, state.name)
                )
                self._commands.append(finalmtx.toRadString())

                self._commands.append(':: :: 2.2.0 direct matrix calculations')
                dctDirect = matrixCalculation(
                    'tmp\\direct..{}..{}.rgb'.format(wg.name, state.name),
                    dMatrix=dMatrixDirect, skyMatrix=skyMtxDirect
                )
                self._commands.append(dctDirect.toRadString())

                self._commands.append(':: :: 2.2.1 convert RGB values to illuminance')
                finalmtx = RGBMatrixFileToIll(
                    (dctTotal.outputFile,),
                    'result\\direct..{}..{}.ill'.format(wg.name, state.name)
                )
                self._commands.append(finalmtx.toRadString())

                self._commands.append(':: :: 2.3.1 enhanced direct matrix calculations')
                dctSun = sunMatrixCalculation(
                    'tmp\\sun..{}..{}.rgb'.format(wg.name, state.name),
                    dcMatrix=sunMatrix,
                    skyMatrix=self.relpath(analemmaMtx, projectFolder)
                )
                self._commands.append(dctSun.toRadString())

                self._commands.append(':: :: 2.3.2 convert RGB values to illuminance')
                finalmtx = RGBMatrixFileToIll(
                    (dctSun.outputFile,),
                    'result\\sun..{}..{}.ill'.format(wg.name, state.name)
                )
                self._commands.append(finalmtx.toRadString())

                self._commands.append(':: :: 2.4 final matrix calculation')
                fmtx = finalMatrixAddition(
                    'result\\total..{}..{}.ill'.format(wg.name, state.name),
                    'result\\direct..{}..{}.ill'.format(wg.name, state.name),
                    'result\\sun..{}..{}.ill'.format(wg.name, state.name),
                    'result\\{}..{}.ill'.format(wg.name, state.name)
                )
                self._commands.append(fmtx.toRadString())

                self._resultFiles.append(
                    os.path.join(projectFolder, str(fmtx.outputFile))
                )

        # # 2.5 write batch file
        batchFile = os.path.join(projectFolder, 'commands.bat')

        writeToFile(batchFile, '\n'.join(self._commands))

        return batchFile

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        # results are merged as a single file
        for rf in self._resultFiles:
            fn = os.path.split(rf)[-1][:-4].split("..")
            source = fn[-2]
            state = fn[-1]
            print('loading restults for {}::{} from {}'.format(source, state, rf))
            startLine = 0
            for count, analysisGrid in enumerate(self.analysisGrids):
                if count:
                    startLine += len(self.analysisGrids[count - 1])

                analysisGrid.setValuesFromFile(
                    rf, self.skyMatrix.hoys, source, state, startLine=startLine,
                    header=True, checkPointCount=False
                )

        return self.analysisGrids
