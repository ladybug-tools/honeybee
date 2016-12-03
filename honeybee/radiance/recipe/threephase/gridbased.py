from ..annual.gridbased import HBAnnualGridBasedAnalysisRecipe
from ...postprocess.annualresults import LoadAnnualsResults
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.dctimestep import Dctimestep
from ...command.rfluxmtx import Rfluxmtx
from ...command.rmtxop import Rmtxop
from ...material.glow import GlowMaterial
from ...sky.skymatrix import SkyMatrix

from ....helper import preparedir, getRadiancePathLines, nukedir

import os
import subprocess


class ThreePhaseGridBasedAnalysisRecipe(HBAnnualGridBasedAnalysisRecipe):
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
                 reuseDaylightMtx=True, hbWindowSurfaces=None, hbObjects=None,
                 subFolder="threephase"):
        """Create an annual recipe."""
        HBAnnualGridBasedAnalysisRecipe.__init__(
            self, skyMtx, analysisGrids, hbObjects=hbObjects, subFolder=subFolder
        )

        self.windowSurfaces = hbWindowSurfaces
        self.viewMtxParameters = viewMtxParameters
        self.daylightMtxParameters = daylightMtxParameters
        self.reuseViewMtx = reuseViewMtx
        self.reuseDaylightMtx = reuseDaylightMtx
        self.__batchFile = None
        self.__commands = []  # place-holder for batch commands
        self.resultsFile = []

        # create a result loader to load the results once the analysis is done.
        self.loader = LoadAnnualsResults(self.resultsFile)

    @classmethod
    def fromWeatherFilePointsAndVectors(
        cls, epwFile, pointGroups, vectorGroups=None, skyDensity=1,
        viewMtxParameters=None, daylightMtxParameters=None, reuseViewMtx=True,
        reuseDaylightMtx=True, hbWindowSurfaces=None, hbObjects=None,
            subFolder="threephase"):
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
            reuseViewMtx, reuseDaylightMtx, hbWindowSurfaces, hbObjects, subFolder)

    @classmethod
    def fromPointsFile(
        cls, epwFile, pointsFile, skyDensity=1, viewMtxParameters=None,
        daylightMtxParameters=None, reuseViewMtx=True, reuseDaylightMtx=True,
            hbWindowSurfaces=None, hbObjects=None, subFolder="threephase"):
        """Create an annual recipe from points file."""
        try:
            with open(pointsFile, "rb") as inf:
                pointGroups = tuple(line.split()[:3] for line in inf.readline())
                vectorGroups = tuple(line.split()[3:] for line in inf.readline())
        except:
            raise ValueError("Couldn't import points from {}".format(pointsFile))

        return cls.fromWeatherFilePointsAndVectors(
            epwFile, pointGroups, vectorGroups, skyDensity, viewMtxParameters,
            daylightMtxParameters, reuseViewMtx, reuseDaylightMtx, hbWindowSurfaces,
            hbObjects, subFolder)

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
        assert self.__windowSurfaces, \
            ValueError('At the minimum, there must be one HBWindowSurface '
                       'to set-up a three-phase analysis. 0 Found!')

        # 0.prepare target folder
        # create main folder targetFolder\projectName
        _basePath = os.path.join(targetFolder, projectName)
        _ispath = preparedir(_basePath, removeContent=False)
        assert _ispath, "Failed to create %s. Try a different path!" % _basePath

        # create main folder targetFolder\projectName\threephase
        _path = os.path.join(_basePath, self.subFolder)
        _ispath = preparedir(_path, removeContent=False)

        _subFolders = ('bsdf', 'views', 'skies', 'results', 'results/matrices')

        assert _ispath, "Failed to create %s. Try a different path!" % _path

        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 0.create a place holder for batch file
        self.__commands = []
        # add path if needed
        self.__commands.append(getRadiancePathLines())

        # TODO: This line won't work in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        self.__commands.append(dirLine)

        # 1.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 2.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 3.0.Create sky matrix.
        skyMtx = self.skyMatrix.execute(_path, reuse=True)

        # 3.1. find glazing items with .xml material, write them to a separate
        # file and invert them
        windowGroups = self.windowGroups
        assert len(windowGroups) > 0, \
            ValueError(
                ' At the minimum, there must be one HBWindowSurface in HBOjects '
                'to set-up a three-phase analysis. 0 found!')

        print 'Number of window groups: %d' % (len(windowGroups))

        glowM = GlowMaterial('vmtx_glow', 1, 1, 1)

        for count, (windowGroup, attr) in enumerate(windowGroups.iteritems()):
            print '    [{}] {} (number of states: {})'.format(
                count, windowGroup, len(attr['states']))

            # make a copy of window groups and change the material to glow
            surfaces = tuple(srf.duplicate() for srf in attr['surfaces'])
            for surface in surfaces:
                surface.radianceMaterial = glowM

            windowGroupPath = os.path.join(_path, '{}.rad'.format(windowGroup))
            with open(windowGroupPath, 'wb') as outf:
                outf.write(surfaces[0].radianceMaterial.toRadString() + '\n')
                for srf in surfaces:
                    outf.write(srf.toRadString(reverse=True) + '\n')

            # 3.2.Generate view matrix
            if not os.path.isfile(os.path.join(_path, windowGroup + ".vmx")) or \
                    not self.reuseViewMtx:
                rflux = Rfluxmtx()
                rflux.sender = '-'
                rflux.rfluxmtxParameters = self.viewMtxParameters
                # Klems full basis sampling
                recCtrlPar = rflux.ControlParameters(
                    hemiType='kf', hemiUpDirection=attr['upnormal'])
                rflux.receiverFile = rflux.addControlParameters(
                    windowGroupPath, {'vmtx_glow': recCtrlPar})

                rflux.radFiles = (matFile, geoFile, '{}.rad'.format(windowGroup))
                rflux.pointsFile = pointsFile
                rflux.outputMatrix = windowGroup + ".vmx"
                self.__commands.append(rflux.toRadString())
                vMatrix = rflux.outputMatrix
            else:
                vMatrix = windowGroup + ".vmx"

            # 3.3 daylight matrix
            if not os.path.isfile(os.path.join(_path, windowGroup + ".dmx")) or \
                    not self.reuseDaylightMtx:
                rflux2 = Rfluxmtx()
                rflux2.samplingRaysCount = 1000
                try:
                    # This will fail in case of not re-using daylight matrix
                    rflux2.sender = rflux.receiverFile
                except UnboundLocalError:
                    rflux2.sender = windowGroupPath[:-4] + '_m' + windowGroupPath[-4:]

                skyFile = rflux2.defaultSkyGround(
                    os.path.join(_path, 'rfluxSky.rad'),
                    skyType='r{}'.format(self.skyMatrix.skyDensity))

                rflux2.receiverFile = skyFile
                rflux2.rfluxmtxParameters = self.daylightMtxParameters
                rflux2.radFiles = (matFile, geoFile, '{}.rad'.format(windowGroup))
                rflux2.outputMatrix = windowGroup + ".dmx"
                self.__commands.append(rflux2.toRadString())
                dMatrix = rflux2.outputMatrix
            else:
                dMatrix = windowGroup + ".dmx"

            for state in attr['states']:
                # 4. matrix calculations
                dct = Dctimestep()
                dct.tmatrixFile = state.xmlfile
                dct.vmatrixSpec = vMatrix
                dct.dmatrixFile = str(dMatrix)
                dct.skyVectorFile = skyMtx
                dct.outputFileName = r'{}..{}.tmp'.format(windowGroup, state.name)
                self.__commands.append(dct.toRadString())

                # 5. convert r, g ,b values to illuminance
                outputName = r'{}..{}.ill'.format(windowGroup, state.name)
                self.resultsFile.append(os.path.join(_path, outputName))
                finalmtx = Rmtxop(
                    matrixFiles=[dct.outputFileName],
                    outputFile=outputName)
                finalmtx.rmtxopParameters.outputFormat = 'a'
                finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
                finalmtx.rmtxopParameters.transposeMatrix = True
                self.__commands.append(finalmtx.toRadString())

        # 6. write batch file
        batchFile = os.path.join(_path, "commands.bat")
        self.write(batchFile, "\n".join(self.__commands))
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
            # remove temp folder
            nukedir(os.path.join(os.path.dirname(self.__batchFile), '/.tmp'))
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
