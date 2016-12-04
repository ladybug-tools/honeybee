"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""

# from ..postprocess.gridbasedresults import LoadGridBasedDLAnalysisResults
from .._imagebasedbase import GenericImageBasedAnalysisRecipe
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.rfluxmtx import Rfluxmtx
from ...command.epw2wea import Epw2wea
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
        for i in range(1 + 144 * (self.skyMatrix.density ** 2)):
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

        # # 2.1.Create annual daylight vectors through epw2wea and gendaymtx.
        # TODO: Update skyMtx and use skyMatrix.write to write wea file
        # and then add execute line to batch file if needed.
        # skyMtx = self.skyMatrix.execute(sceneFiles.path, reuse=True)
        weaFilepath = 'skies\\{}.wea'.format(projectName)
        if not os.path.isfile(os.path.join(sceneFiles.path, weaFilepath)):
            weaFile = Epw2wea(self.skyMatrix.epwFile)
            weaFile.outputWeaFile = weaFilepath
            self.commands.append(weaFile.toRadString())

        skyMtx = 'skies\\{}.smx'.format(projectName)
        if not os.path.isfile(os.path.join(sceneFiles.path, skyMtx)):
            gdm = Gendaymtx(outputName=skyMtx, weaFile=weaFilepath)
            gdm.gendaymtxParameters.skyDensity = self.skyMatrix.skyDensity
            self.commands.append(gdm.toRadString())

        # # 2.2.Generate daylight coefficients using rfluxmtx
        rfluxFiles = [sceneFiles.matFile, sceneFiles.geoFile] + \
            sceneFiles.matFilesAdd + sceneFiles.radFilesAdd + sceneFiles.octFilesAdd

        # # 4.2.prepare rpict
        for view, f in zip(self.views, viewFiles):
            # Step1: Create the view matrix.

            # calculate view dimensions
            vwrParaDim = VwraysParameters()
            vwrParaDim.calcImageDim = True
            vwrParaDim.xResolution = view.xRes
            vwrParaDim.yResolution = view.yRes

            vwrDim = Vwrays()
            vwrDim.vwraysParameters = vwrParaDim
            vwrDim.viewFile = self.relpath(f, sceneFiles.path)
            vwrDim.outputFile = r'views\\{}.dimensions'.format(view.name)
            self.commands.append(vwrDim.toRadString())

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
            if not self.reuseDaylightMtx or not \
                    self.isDaylightMtxCreated(sceneFiles.path, view):
                rflux = Rfluxmtx()
                rflux.rfluxmtxParameters = self.radianceParameters
                rflux.radFiles = tuple(self.relpath(f, sceneFiles.path) for f in rfluxFiles)
                rflux.sender = '-'
                groundFileFormat = 'results\\matrix\\%s_%03d.hdr' % (
                    view.name, 1 + 144 * (self.skyMatrix.density ** 2))

                rflux.receiverFile = rflux.defaultSkyGround(
                    os.path.join(sceneFiles.path, 'skies\\rfluxSky.rad'),
                    skyType=self.skyType, groundFileFormat=groundFileFormat,
                    skyFileFormat='results\\matrix\\%s_%03d.hdr' % view.name)

                rflux.outputDataFormat = 'fc'
                rflux.verbose = True
                rflux.viewInfoFile = str(vwrDim.outputFile)
                rflux.viewRaysFile = str(vwrSamp.outputFile)
                rflux.samplingRaysCount = 3  # 9
                self.commands.append(rflux.toRadString())

            # Generate resultsFile
            # TODO: This should happen separately for each skyvector
            dct = Dctimestep()
            dct.daylightCoeffSpec = 'results\\matrix\\%s_%03d.hdr' % view.name
            dct.skyVectorFile = skyMtx
            dct.outputFile = 'results\\%s.hdr' % view.name
            self.commands.append(dct.toRadString())

            self.resultsFile.append(
                os.path.join(sceneFiles.path, str(dct.outputFile)))

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
