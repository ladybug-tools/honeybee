from ..dc.gridbased import DaylightCoeffGridBasedAnalysisRecipe
from ...postprocess.annualresults import LoadAnnualsResults
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.dctimestep import Dctimestep
from ...command.rfluxmtx import Rfluxmtx
from ...command.rmtxop import Rmtxop
from ...command.gendaymtx import Gendaymtx
from ...material.glow import GlowMaterial
from ...sky.skymatrix import SkyMatrix
from ....helper import writeToFile, copyFilesToFolder

import os


# TODO: implement simulationType
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
        # create a result loader to load the results once the analysis is done.
        self.loader = LoadAnnualsResults(self.resultsFile)

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
        except:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity, simulationType,
            viewMtxParameters, daylightMtxParameters, reuseViewMtx, reuseDaylightMtx,
            hbWindowSurfaces, hbObjects, subFolder)

    @property
    def windowSurfaces(self):
        """List of window surfaces."""
        return self.__windowSurfaces

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

        self.__windowSurfaces = hbWindowSurfaces

    # TODO: Create windowGroups as classes
    @property
    def windowGroups(self):
        """Get window groups as a dictionary {'windowGroupName': [srf1, srf2,...]}.

        Window groups will be calculated from windowSurfaces. You can set-up
        windowgroup names for each surface by using radProperties.windowGroupName
        method.
        """
        _wgroups = {}
        for srf in self.windowSurfaces:
            wgn = srf.radProperties.windowGroupName or srf.name
            if wgn not in _wgroups:
                _wgroups[wgn] = {
                    'normal': srf.normal, 'upnormal': srf.upnormal, 'surfaces': [srf],
                    'states': (srf.radianceMaterial,) + tuple(srf.radProperties.alternateMaterials)}
            else:
                # the group is already created. check normal direction and it
                # to surfaces.
                assert srf.normal == _wgroups[wgn]['normal'], \
                    ValueError(
                        'Normal direction of Windows in a window groups should match.\n'
                        '{} from {} does not match {} from {}.'.format(
                            srf.normal, srf, _wgroups[wgn]['normal'], _wgroups[wgn]['surfaces'][0]
                        ))
                # TODO: Check radiance matrials and alternateMaterials to match.
                assert (srf.radianceMaterial,) + tuple(srf.radProperties.alternateMaterials) \
                    == _wgroups[wgn]['states'], \
                    '{} has a different radiance material than windowgroup material.'.format(srf)

                _wgroups[wgn]['surfaces'].append(srf)

        return _wgroups

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

    # TODO: docstring should be modified
    def write(self, targetFolder, projectName='untitled', header=True):
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
                            'objects\\windowGroups', 'results\\matrix'),
                removeSubFoldersContent=False)

        # 0.write points
        pointsFile = self.writePointsToFile(sceneFiles.path, projectName)

        # 2.write batch file
        self.commands = []
        self.resultsFile = []

        if header:
            self.commands.append(self.header(sceneFiles.path))

        # 3.0.Create sky matrix.
        if hasattr(self.skyMatrix, 'isSkyMatrix'):
            weaFilepath = 'skies\\{}.wea'.format(self.skyMatrix.name)
            skyMtx = 'skies\\{}.smx'.format(self.skyMatrix.name)
            hoursFile = os.path.join(
                sceneFiles.path, 'skies\\{}.hrs'.format(self.skyMatrix.name))
            if not os.path.isfile(os.path.join(sceneFiles.path, weaFilepath)) \
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

        # 3.1. find glazing items with .xml material, write them to a separate
        # file and invert them
        print 'Number of window groups: %d' % (len(windowGroups))

        glowM = GlowMaterial('vmtx_glow', 1, 1, 1)

        # write calculations for each window group
        for count, (windowGroup, attr) in enumerate(windowGroups.iteritems()):
            print '    [{}] {} (number of states: {})'.format(
                count, windowGroup, len(attr['states']))

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
                    outf.write(srf.toRadString(reverse=True) + '\n')

            # 3.2.Generate view matrix
            vMatrix = 'results\\matrix\\{}.vmx'.format(windowGroup)
            if not os.path.isfile(os.path.join(sceneFiles.path, vMatrix)) \
                    or not self.reuseViewMtx:
                # TODO: @sariths is checking for this to make sure we don't need
                # to include rest of the window groups in the scene
                viewMtxFiles = (sceneFiles.matFile, sceneFiles.geoFile)

                vMtxRflux = Rfluxmtx()
                vMtxRflux.sender = '-'
                vMtxRflux.rfluxmtxParameters = self.viewMtxParameters

                # Klems full basis sampling
                recCtrlPar = vMtxRflux.ControlParameters(
                    hemiType='kf', hemiUpDirection=attr['upnormal'])
                wg_m = vMtxRflux.addControlParameters(
                    windowGroupPath, {'vmtx_glow': recCtrlPar})

                vMtxRflux.receiverFile = self.relpath(wg_m, sceneFiles.path)

                vMtxRflux.radFiles = tuple(self.relpath(f, sceneFiles.path)
                                           for f in viewMtxFiles)

                vMtxRflux.pointsFile = pointsFile
                vMtxRflux.outputMatrix = vMatrix
                self.commands.append(vMtxRflux.toRadString())

            # 3.3 daylight matrix
            dMatrix = 'results\\matrix\\{}_{}_{}.dmx'.format(
                windowGroup, self.skyMatrix.skyDensity, self.numOfTotalPoints)

            if not os.path.isfile(os.path.join(sceneFiles.path, dMatrix)) \
                    or not self.reuseDaylightMtx:

                daylightMtxFiles = [sceneFiles.matFile, sceneFiles.geoFile] + \
                    sceneFiles.matFilesAdd + sceneFiles.radFilesAdd + sceneFiles.octFilesAdd

                dMtxRflux = Rfluxmtx()
                dMtxRflux.samplingRaysCount = 1000
                try:
                    # This line fails in case of not re-using daylight matrix
                    dMtxRflux.sender = str(vMtxRflux.receiverFile)
                except UnboundLocalError:
                    dMtxRflux.sender = self.relpath(
                        windowGroupPath[:-4] + '_m' + windowGroupPath[-4:],
                        sceneFiles.path)

                skyFile = dMtxRflux.defaultSkyGround(
                    os.path.join(sceneFiles.path, 'skies\\rfluxSky.rad'),
                    skyType='r{}'.format(self.skyMatrix.skyDensity))

                dMtxRflux.receiverFile = self.relpath(skyFile, sceneFiles.path)
                dMtxRflux.rfluxmtxParameters = self.daylightMtxParameters
                dMtxRflux.radFiles = tuple(self.relpath(f, sceneFiles.path)
                                           for f in daylightMtxFiles)
                dMtxRflux.outputMatrix = dMatrix
                self.commands.append(dMtxRflux.toRadString())

            for count, state in enumerate(attr['states']):
                # 4. matrix calculations
                dct = Dctimestep()
                dct.tmatrixFile = self.relpath(_xmlFiles[count], sceneFiles.path)
                dct.vmatrixSpec = vMatrix
                dct.dmatrixFile = dMatrix
                dct.skyVectorFile = skyMtx
                dct.outputFile = r'.tmp\\{}..{}.tmp'.format(windowGroup, state.name)
                self.commands.append(dct.toRadString())

                # 5. convert r, g ,b values to illuminance
                outputName = r'results\\{}..{}.ill'.format(windowGroup, state.name)
                finalmtx = Rmtxop(matrixFiles=(dct.outputFile,),
                                  outputFile=outputName)
                finalmtx.rmtxopParameters.outputFormat = 'a'
                finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
                finalmtx.rmtxopParameters.transposeMatrix = True
                self.commands.append(finalmtx.toRadString())

                self.resultsFile.append(os.path.join(sceneFiles.path, outputName))

        # 5. write batch file
        batchFile = os.path.join(sceneFiles.path, "commands.bat")
        writeToFile(batchFile, "\n".join(self.commands))
        self.__batchFile = batchFile

        print "Files are written to: %s" % sceneFiles.path
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        self.loader.resultFiles = self.resultsFile
        return self.loader.results
