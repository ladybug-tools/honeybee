"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""

# from ..postprocess.gridbasedresults import LoadGridBasedDLAnalysisResults
from ladybug.dt import DateTime
from .._imagebasedbase import GenericImageBasedAnalysisRecipe
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.rfluxmtx import Rfluxmtx
from ...command.gendaymtx import Gendaymtx
from ...command.dctimestep import Dctimestep
from ...command.vwrays import Vwrays, VwraysParameters
from ....helper import writeToFile
import os


class DaylightCoeffImageBasedAnalysisRecipe(GenericImageBasedAnalysisRecipe):
    """Daylight Coefficient Image-Based.

    Attributes:
        sky: A honeybee sky for the analysis
        views: List of views.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radParameters: Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:


    """

    # TODO: implemnt isChanged at DaylightAnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, skyMtx, views, simulationType=2, daylightMtxParameters=None,
                 vwraysParameters=None, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="imagebased_dyalightcoeff"):
        """Create grid-based recipe."""
        GenericImageBasedAnalysisRecipe.__init__(
            self, views, hbObjects, subFolder)

        self.skyMatrix = skyMtx
        """A honeybee sky for the analysis."""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 0)
        """

        self.radianceParameters = daylightMtxParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)"""

        self.reuseDaylightMtx = reuseDaylightMtx

        # create a result loader to load the results once the analysis is done.
        # self.loader = LoadGridBasedDLAnalysisResults(self.simulationType,
        #                                              self.resultsFile)

    @property
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self.__simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except:
            value = 2

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky.isClimateBased, \
                "The sky for radition analysis should be climate-based."

        self.__simType = value

    @property
    def skyType(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    @property
    def radianceParameters(self):
        """Get and set Radiance parameters."""
        return self.__radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            self.__radianceParameters = RfluxmtxParameters()
            self.__radianceParameters.ambientAccuracy = 0.1
            self.__radianceParameters.ambientBounces = 5  # 10
            self.__radianceParameters.ambientDivisions = 4096  # 65536
            self.__radianceParameters.limitWeight = 0.001  # 1E-5
        else:
            assert hasattr(par, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))
            self.__daylightMtxParameters = par

    def isDaylightMtxCreated(self, studyFolder, view):
        """Check if hdr images for daylight matrix are already created."""
        for i in range(1 + 144 * (self.skyMatrix.skyDensity ** 2)):
            if not os.path.isfile(
                    os.path.join(studyFolder,
                                 'results\\matrix\\%s_%03d.hdr' % (view.name, i))):
                return False
        return True

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.

        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        sceneFiles = super(
            DaylightCoeffImageBasedAnalysisRecipe, self).populateSubFolders(
                targetFolder, projectName,
                subFolders=('.tmp', 'objects', 'skies', 'results',
                            'results\\matrix', 'views'),
                removeSubFoldersContent=False)

        # 1.write views
        viewFiles = self.writeViewsToFile(sceneFiles.path + '\\views')

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
            if not os.path.isfile(os.path.join(sceneFiles.path, weaFilepath)) \
                or not os.path.isfile(os.path.join(sceneFiles.path, skyMtx)) \
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

        # # 4.2.prepare rpict
        for view, f in zip(self.views, viewFiles):
            # Step1: Create the view matrix.

            # calculate view dimensions
            vwrDimFile = os.path.join(sceneFiles.path,
                                      r'views\\{}.dimensions'.format(view.name))
            x, y = view.getViewDimension()
            with open(vwrDimFile, 'wb') as vdfile:
                vdfile.write('-x %d -y %d -ld-\n' % (x, y))

            # calculate sampling for each view
            vwrParaSamp = VwraysParameters()
            vwrParaSamp.xResolution = view.xRes
            vwrParaSamp.yResolution = view.yRes
            vwrParaSamp.samplingRaysCount = 3  # 9
            vwrParaSamp.jitter = 0.7

            vwrSamp = Vwrays()
            vwrSamp.vwraysParameters = vwrParaSamp
            vwrSamp.viewFile = self.relpath(f, sceneFiles.path)
            vwrSamp.outputFile = r'views\\{}.rays'.format(view.name)
            vwrSamp.outputDataFormat = 'f'
            self.commands.append(vwrSamp.toRadString())

            # Daylight matrix
            if not self.reuseDaylightMtx:
                print 'Daylight matrix will be recalculated!'

            if not self.reuseDaylightMtx or not \
                    self.isDaylightMtxCreated(sceneFiles.path, view):
                rflux = Rfluxmtx()
                rflux.rfluxmtxParameters = self.radianceParameters
                rflux.radFiles = tuple(self.relpath(f, sceneFiles.path) for f in rfluxFiles)
                rflux.sender = '-'
                groundFileFormat = 'results\\matrix\\%s_%03d.hdr' % (
                    view.name, 1 + 144 * (self.skyMatrix.skyDensity ** 2))

                rflux.receiverFile = rflux.defaultSkyGround(
                    os.path.join(sceneFiles.path, 'skies\\rfluxSky.rad'),
                    skyType=self.skyType, groundFileFormat=groundFileFormat,
                    skyFileFormat='results\\matrix\\{}_%03d.hdr'.format(view.name))

                rflux.outputDataFormat = 'fc'
                rflux.verbose = True
                rflux.viewInfoFile = vwrDimFile
                rflux.viewRaysFile = str(vwrSamp.outputFile)
                rflux.samplingRaysCount = 3  # 9
                self.commands.append(rflux.toRadString())

            # Generate resultsFile
            # TODO: This should happen separately for each skyvector
            dct = Dctimestep()
            if os.name == 'nt':
                dct.daylightCoeffSpec = 'results\\matrix\\{}_%%03d.hdr'.format(view.name)
            else:
                dct.daylightCoeffSpec = 'results\\matrix\\{}_%03d.hdr'.format(view.name)

            dct.skyVectorFile = skyMtx
            if hasattr(self.skyMatrix, 'isSkyMatrix'):
                # sky matrix is annual
                if os.name == 'nt':
                    dct.dctimestepParameters.outputDataFormat = \
                        ' results\\{}_%%04d.hdr'.format(view.name)
                else:
                    dct.dctimestepParameters.outputDataFormat = \
                        ' results\\{}_%04d.hdr'.format(view.name)
                self.resultsFile = tuple(os.path.join(
                    sceneFiles.path,
                    'results\\{}_{}.hdr'.format(view.name, '%04d' % (count + 1)))
                    for count, h in enumerate(self.skyMatrix.hoys))
            else:
                dct.outputFile = 'results\\%s_%s.hdr' % (view.name,
                                                         self.skyMatrix.name)
                self.resultsFile.append(
                    os.path.join(sceneFiles.path, str(dct.outputFile)))

            self.commands.append(dct.toRadString())

        # # 4.3 write batch file
        batchFile = os.path.join(sceneFiles.path, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        print "Files are written to: %s" % sceneFiles.path
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        # self.loader.simulationType = self.simulationType
        # self.loader.resultFiles = self.resultsFile
        # return self.loader.results
        return self.resultsFile

    def renameResultFiles(self):
        """Rename result files to be named based on month_day_hour."""
        if not hasattr(self.skyMatrix, 'isSkyMatrix'):
            return self.resultsFile

        names = []
        for f, h in zip(self.results(), self.skyMatrix.hoys):
            hoy = DateTime.fromHoy(h)
            name = '%02d_%02d_%02d.hdr' % (hoy.month, hoy.day, int(hoy.hour))
            tf = f[:-8] + name
            if os.path.isfile(tf):
                try:
                    os.remove(tf)
                except:
                    print "Failed to remove %s." % tf

            try:
                os.rename(f, tf)
            except WindowsError:
                msg = 'Failed to rename (%s) to (%s)\n\t' \
                    'Access is denied. Do you have the file open?' % (f, tf)
                print msg
                names.append(f)
            else:
                names.append(tf)

        self.resultsFile = names
        return self.resultsFile

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#Views: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulationType],
             self.numOfViews)
