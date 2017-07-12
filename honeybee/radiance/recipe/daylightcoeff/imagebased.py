"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""

from ..recipeutil import writeRadFilesDaylightCoeff, writeExtraFiles
from .._imagebasedbase import GenericImageBased
from ...parameters.rfluxmtx import RfluxmtxParameters
from ...command.rfluxmtx import Rfluxmtx
from ...command.gendaymtx import Gendaymtx
from ...command.dctimestep import Dctimestep
from ...command.vwrays import Vwrays, VwraysParameters
from ....futil import writeToFile

from ladybug.dt import DateTime
import os


class DaylightCoeffImageBased(GenericImageBased):
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

    # TODO: implemnt isChanged at AnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, skyMtx, views, simulationType=2, daylightMtxParameters=None,
                 vwraysParameters=None, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="imagebased_dyalightcoeff"):
        """Create grid-based recipe."""
        GenericImageBased.__init__(
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
        #                                              self._resultFiles)

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
        except TypeError:
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
        projectFolder = \
            super(GenericImageBased, self).writeContent(
                targetFolder, projectName, False,
                subfolders=['.tmp', 'result/matrix', 'view']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFilesDaylightCoeff(
            projectFolder + '\\scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )
        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '\\scene')

        # 1.write views
        viewFiles = self.writeViews(projectFolder + '\\view')

        if header:
            self.commands.append(self.header(projectFolder))

        # # 2.1.Create sky matrix.
        skyMtxTotal = 'sky\\{}.smx'.format(self.skyMatrix.name)
        self.skyMatrix.mode = 1
        skyMtxDirect = 'sky\\{}.smx'.format(self.skyMatrix.name)

        # add commands for total and direct sky matrix.
        if hasattr(self.skyMatrix, 'isSkyMatrix'):
            for m in xrange(2):
                self.skyMatrix.mode = m
                gdm = skymtxToGendaymtx(self.skyMatrix, projectFolder)
                if gdm:
                    note = ':: {} sky matrix'.format('direct' if m else 'total')
                    self._commands.extend((note, gdm))
        else:
            # sky vector
            raise TypeError('You must use a SkyMatrix to generate the sky.')

        # # 2.2. Create sun matrix
        sm = SunMatrix(self.skyMatrix.wea, self.skyMatrix.north)
        analemma, sunlist, sunMtxFile = \
            sm.execute(os.path.join(projectFolder, 'sky'), shell=True)

        # # 4.2.prepare vwray
        for view, f in zip(self.views, viewFiles):
            # Step1: Create the view matrix.

            # calculate view dimensions
            vwrDimFile = os.path.join(projectFolder,
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
            vwrSamp.viewFile = self.relpath(f, projectFolder)
            vwrSamp.outputFile = r'views\\{}.rays'.format(view.name)
            vwrSamp.outputDataFormat = 'f'
            self.commands.append(vwrSamp.toRadString())

            # Daylight matrix
            if not self.reuseDaylightMtx or not \
                    self.isDaylightMtxCreated(projectFolder, view):
                rflux = Rfluxmtx()
                rflux.rfluxmtxParameters = self.radianceParameters
                rflux.radFiles = tuple(self.relpath(f, projectFolder)
                                       for f in rfluxFiles)
                rflux.sender = '-'
                groundFileFormat = 'results\\matrix\\%s_%03d.hdr' % (
                    view.name, 1 + 144 * (self.skyMatrix.skyDensity ** 2))

                rflux.receiverFile = rflux.defaultSkyGround(
                    os.path.join(projectFolder, 'skies\\rfluxSky.rad'),
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
                self._resultFiles = tuple(os.path.join(
                    projectFolder,
                    'results\\{}_{}.hdr'.format(view.name, '%04d' % (count + 1)))
                    for count, h in enumerate(self.skyMatrix.hoys))
            else:
                dct.outputFile = 'results\\%s_%s.hdr' % (view.name,
                                                         self.skyMatrix.name)
                self._resultFiles.append(
                    os.path.join(projectFolder, str(dct.outputFile)))

            self.commands.append(dct.toRadString())

        # # 4.3 write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        print "Files are written to: %s" % projectFolder
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."
        return self._resultFiles

    def renameResultFiles(self):
        """Rename result files to be named based on month_day_hour."""
        if not hasattr(self.skyMatrix, 'isSkyMatrix'):
            return self._resultFiles

        names = []
        for f, h in zip(self.results(), self.skyMatrix.hoys):
            hoy = DateTime.fromHoy(h)
            name = '%02d_%02d_%02d.hdr' % (hoy.month, hoy.day, int(hoy.hour))
            tf = f[:-8] + name
            if os.path.isfile(tf):
                try:
                    os.remove(tf)
                except Exception as e:
                    print "Failed to remove %s: %s" % (tf, str(e))

            try:
                os.rename(f, tf)
            except WindowsError:
                msg = 'Failed to rename (%s) to (%s)\n\t' \
                    'Access is denied. Do you have the file open?' % (f, tf)
                print msg
                names.append(f)
            else:
                names.append(tf)

        self._resultFiles = names
        return self._resultFiles

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
             self.viewCount)
