from ..radrecutil import windowGroupToReceiver, coeffMatrixCommands, skyReceiver, \
    matrixCalculation, convertMatrixResults, skymtxToGendaymtx
from ..dc.gridbased import DaylightCoeffGridBasedAnalysisRecipe
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...material.glow import GlowMaterial
from ...sky.skymatrix import SkyMatrix
from ....futil import writeToFile, copyFilesToFolder

import os


# TODO(): implement simulationType
class ThreePhaseGridBasedAnalysisRecipe(DaylightCoeffGridBasedAnalysisRecipe):
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
        analysisRecipe = ThreePhaseGridBasedAnalysisRecipe(
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
                 reuseViewMtx=True, reuseDaylightMtx=True, hbWindowSurfaces=None,
                 hbObjects=None, subFolder="gridbased_threephase"):
        """Create an annual recipe."""
        DaylightCoeffGridBasedAnalysisRecipe.__init__(
            self, skyMtx, analysisGrids, hbObjects=hbObjects, subFolder=subFolder
        )

        self.windowSurfaces = hbWindowSurfaces
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
    def windowSurfaces(self):
        """List of window surfaces."""
        return self._windowSurfaces

    @windowSurfaces.setter
    def windowSurfaces(self, hbWindowSurfaces):
        """List of window surfaces.

        Args:
            ws: A list of window surfaces.
        """
        hbWindowSurfaces = hbWindowSurfaces or ()
        # check inputs
        for f in hbWindowSurfaces:
            assert f.hasBSDFRadianceMaterial, \
                TypeError(
                    '{} is not a HBWindowSurface. A HBWindowSurface must be a '
                    'HBFenSurface and has a BSDF radiance material.'.format(f))

        self._windowSurfaces = hbWindowSurfaces

    # TODO(): Create windowGroups as classes
    @property
    def windowGroups(self):
        """Get window groups as a dictionary {'windowGroupName': [srf1, srf2,...]}.

        Window groups will be calculated from windowSurfaces. You can set-up
        windowgroup names for each surface by using radProperties.windowGroupName
        method.
        """
        _wgroups = {}
        for srf in self.windowSurfaces:
            wgn = srf.name
            if wgn not in _wgroups:
                states = tuple(st.radianceMaterial for st in srf.states)
                _wgroups[wgn] = {
                    'normal': srf.normal, 'upnormal': srf.upnormal, 'surfaces': [srf],
                    'states': states}
                _wgroups[wgn]['surfaces'].append(srf)

        return _wgroups

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
    def skyType(self):
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
            True in case of success.
        """
        windowGroups = self.windowGroups
        assert len(windowGroups) > 0, \
            ValueError(
                ' At the minimum, there must be one HBWindowSurface in HBOjects '
                'to set-up a three-phase analysis. 0 found!')

        # 0.prepare target folder
        # create main folder targetFolder\projectName
        sceneFiles = super(
            ThreePhaseGridBasedAnalysisRecipe, self).populateSubFolders(
                targetFolder, projectName,
                subFolders=('.tmp', 'bsdfs', 'objects', 'skies', 'results',
                            'objects\\windowgroups', 'results\\matrix'),
                removeSubFoldersContent=False)

        # 0.write points
        pointsFile = self.writePointsToFile(sceneFiles.path, projectName)
        numberOfPoints = sum(len(ag) for ag in self.analysisGrids)

        # 2.write batch file
        self.commands = []
        self.resultsFile = []

        if header:
            self.commands.append(self.header(sceneFiles.path))

        # 3.0.Create sky matrix.
        skyMtx = 'skies\\{}.smx'.format(self.skyMatrix.name)
        if hasattr(self.skyMatrix, 'isSkyMatrix'):
            gdm = skymtxToGendaymtx(self.skyMatrix, sceneFiles.path)
            if gdm:
                self.commands.append(':: sky matrix')
                self.commands.append(gdm.toRadString())
        else:
            # sky vector
            raise TypeError('You must use a SkyMatrix to generate the sky.')

        # 3.1. find glazing items with .xml material, write them to a separate
        # file and invert them
        print('Number of window groups: %d' % (len(windowGroups)))

        glowM = GlowMaterial('vmtx_glow', 1, 1, 1)

        # write calculations for each window group
        for count, (windowGroup, attr) in enumerate(windowGroups.iteritems()):
            print('    [{}] {} (number of states: {})'.format(
                count, windowGroup, len(attr['states'])))
            self.commands.append('\n:: calculation for windowGroup [{}]: {}'.format(
                count, windowGroup))

            # copy all the state materials to bsdfs folder
            _xmlFiles = copyFilesToFolder(
                tuple(s.xmlfile for s in attr['states']),
                os.path.join(sceneFiles.path, 'bsdfs'))

            # make a copy of window groups and change the material to glow
            surfaces = tuple(srf.duplicate() for srf in attr['surfaces'])
            for surface in surfaces:
                surface.radianceMaterial = glowM

            # write each window group
            windowGroupPath = os.path.join(
                sceneFiles.path, 'objects\\windowgroups\\{}.rad'.format(windowGroup))

            with open(windowGroupPath, 'wb') as outf:
                outf.write(surfaces[0].radianceMaterial.toRadString() + '\n')
                for srf in surfaces:
                    outf.write(srf.toRadString(flipped=True) + '\n')

            # 3.2.Generate view matrix
            vMatrix = 'results\\matrix\\{}.vmx'.format(windowGroup)
            if not os.path.isfile(os.path.join(sceneFiles.path, vMatrix)) \
                    or not self.reuseViewMtx:
                # prepare input files
                receiver = windowGroupToReceiver(windowGroupPath, attr['upnormal'])
                viewMtxFiles = (sceneFiles.matFile, sceneFiles.geoFile)
                radFiles = tuple(self.relpath(f, sceneFiles.path) for f in viewMtxFiles)

                vmtx = coeffMatrixCommands(
                    vMatrix, self.relpath(receiver, sceneFiles.path), radFiles, '-',
                    self.relpath(pointsFile, sceneFiles.path), numberOfPoints,
                    None, self.viewMtxParameters)

                self.commands.append(':: :: 1. view matrix calculation')
                self.commands.append(vmtx.toRadString())

            # 3.3 daylight matrix
            dMatrix = 'results\\matrix\\{}_{}_{}.dmx'.format(
                windowGroup, self.skyMatrix.skyDensity, self.numOfTotalPoints)

            if not os.path.isfile(os.path.join(sceneFiles.path, dMatrix)) \
                    or not self.reuseDaylightMtx:

                daylightMtxFiles = [sceneFiles.matFile, sceneFiles.geoFile] + \
                    sceneFiles.matFilesAdd + sceneFiles.radFilesAdd + \
                    sceneFiles.octFilesAdd

                try:
                    # This line fails in case of not re-using daylight matrix
                    sender = str(vmtx.receiverFile)
                except UnboundLocalError:
                    sender = self.relpath(
                        windowGroupPath[:-4] + '_m' + windowGroupPath[-4:],
                        sceneFiles.path)

                receiver = skyReceiver(
                    os.path.join(sceneFiles.path, 'skies\\rfluxSky.rad'),
                    self.skyMatrix.skyDensity
                )

                samplingRaysCount = 1000
                radFiles = tuple(self.relpath(f, sceneFiles.path)
                                 for f in daylightMtxFiles)

                dmtx = coeffMatrixCommands(
                    dMatrix, self.relpath(receiver, sceneFiles.path), radFiles,
                    sender, None, None, samplingRaysCount, self.daylightMtxParameters)

                self.commands.append(':: :: 2. daylight matrix calculation')
                self.commands.append(dmtx.toRadString())

            for count, state in enumerate(attr['states']):
                # 4. matrix calculations
                tMatrix = self.relpath(_xmlFiles[count], sceneFiles.path)
                output = r'.tmp\\{}..{}.tmp'.format(windowGroup, state.name)
                dct = matrixCalculation(output, vMatrix, tMatrix, dMatrix, skyMtx)

                self.commands.append(
                    ':: :: 3.1.{} final matrix calculation for {}'.format(count,
                                                                          state.name))
                self.commands.append(dct.toRadString())

                # 5. convert r, g ,b values to illuminance
                finalOutput = r'results\\{}..{}.ill'.format(windowGroup, state.name)
                finalmtx = convertMatrixResults(finalOutput, (dct.outputFile,))
                self.commands.append(
                    ':: :: 3.2.{} convert RGB values to illuminance for {}'.format(
                        count, state.name)
                )
                self.commands.append(finalmtx.toRadString())

                self.resultsFile.append(os.path.join(sceneFiles.path, finalOutput))

        # 5. write batch file
        batchFile = os.path.join(sceneFiles.path, "commands.bat")
        writeToFile(batchFile, "\n".join(self.commands))
        self.__batchFile = batchFile  # TODO() > What is this for?

        print("Files are written to: %s" % sceneFiles.path)
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        # self.loader.resultFiles = self.resultsFile
        for r in self.resultsFile:
            source, state = os.path.split(r)[-1][:-4].split("..")
            self.analysisGrids[0].setValuesFromFile(r, self.skyMatrix.hoys,
                                                    source, state)
        return self.analysisGrids
