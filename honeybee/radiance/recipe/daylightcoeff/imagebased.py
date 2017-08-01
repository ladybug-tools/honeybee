"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""
from ..recipeutil import writeExtraFiles, glzSrfTowinGroup
from ..recipedcutil import writeRadFilesDaylightCoeff
from ..recipedcutil import imageBasedViewSamplingCommands, \
    imageBasedViewCoeffMatrixCommands, imagedBasedSunCoeffMatrixCommands
from ..parameters import getRadianceParametersImageBased
from ..recipedcutil import imageBasedViewMatrixCalculation
from ..recipedcutil import skyReceiver, skymtxToGendaymtx
from .._imagebasedbase import GenericImageBased
from ...sky.sunmatrix import SunMatrix
from ....futil import writeToFile

from ladybug.dt import DateTime
import os

from itertools import izip


class DaylightCoeffImageBased(GenericImageBased):
    """Daylight Coefficient Image-Based.

    Attributes:
        skyMtx: A honeybee sky for the analysis
        views: List of views.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 2)
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
                 subFolder="imagebased_daylightcoeff"):
        """Create grid-based recipe."""
        GenericImageBased.__init__(
            self, views, hbObjects, subFolder)

        self.skyMatrix = skyMtx
        """A honeybee sky for the analysis."""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 2)
        """

        self.daylightMtxParameters = daylightMtxParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)"""

        self.vwraysParameters = vwraysParameters

        self.reuseDaylightMtx = reuseDaylightMtx

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
        self._skyMatrix = newSky.duplicate()

    @property
    def skyDensity(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.skyMatrix.skyDensity)

    # TODO(mostapha): Change this to daylightMtxParameters and use default values from
    # the parameters! Do not set them up manually.
    @property
    def daylightMtxParameters(self):
        """Get and set Radiance parameters."""
        return self._daylightMtxParameters

    @daylightMtxParameters.setter
    def daylightMtxParameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            par = getRadianceParametersImageBased(0, 1).dmtx
        else:
            assert hasattr(par, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))
        self._daylightMtxParameters = par

    def isDaylightMtxCreated(self, studyFolder, view, wg, state):
        """Check if hdr images for daylight matrix are already created."""
        for i in range(1 + 144 * (self.skyMatrix.skyDensity ** 2)):
            fp = os.path.join(
                studyFolder, 'results\\matrix\\%s_%s_%s_%03d.hdr' % (
                    view.name, wg.name, state.name, i)
            )

            if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                # file doesn't exist or is smaller than 265 bytes
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

        # # 4.2.prepare vwray
        for view, viewFile in izip(self.views, viewFiles):
            # Step1: Create the view matrix.
            self.commands.append(':: calculation for view: {}'.format(view.name))
            self.commands.append(':: 1 view sampling')
            viewInfoFile, vwrSamp = imageBasedViewSamplingCommands(
                projectFolder, view, viewFile, self.vwraysParameters)
            self.commands.append(vwrSamp.toRadString())

            # set up the geometries
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
                        [f.fpblk[1] for c, f in enumerate(wgsfiles)
                         if c != count - 1] + list(glzfiles.fpblk)

                for scount, state in enumerate(wg.states):
                    # 2.3.Generate daylight coefficients using rfluxmtx
                    # collect list of radiance files in the scene for both total
                    # and direct
                    self._commands.append(
                        '\n:: calculation for {} window group {}'.format(wg.name,
                                                                         state.name))
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

                    dMatrix = 'result\\matrix\\normal_{}_{}_{}..{}..{}.dc'.format(
                        view.name, projectName, self.skyMatrix.skyDensity, wg.name,
                        state.name)

                    dMatrixDirect = 'result\\matrix\\black_{}_{}_{}..{}..{}.dc'.format(
                        view.name, projectName, self.skyMatrix.skyDensity, wg.name,
                        state.name)

                    sunMatrix = 'result\\matrix\\sun_{}_{}_{}..{}..{}.dc'.format(
                        view.name, projectName, self.skyMatrix.skyDensity, wg.name,
                        state.name)

                    # Daylight matrix
                    if not self.reuseDaylightMtx or not \
                            self.isDaylightMtxCreated(projectFolder, view, wg, state):

                        radFiles = tuple(self.relpath(f, projectFolder)
                                         for f in rfluxScene)
                        sender = '-'

                        groundFileFormat = 'result\\matrix\\%s_%s_%s_%03d.hdr' % (
                            view.name, wg.name, state.name,
                            1 + 144 * (self.skyMatrix.skyDensity ** 2)
                        )

                        skyFileFormat = 'result\\matrix\\{}_{}_{}_%03d.hdr'.format(
                            view.name, wg.name, state.name)

                        receiver = skyReceiver(
                            os.path.join(projectFolder, 'sky\\rfluxSky.rad'),
                            self.skyMatrix.skyDensity, groundFileFormat, skyFileFormat
                        )

                        self._commands.append(
                            ':: :: 1. daylight matrix {}, {} > state {}'.format(
                                view.name, wg.name, state.name)
                        )

                        self._commands.append(':: :: 1.1 scene daylight matrix')

                        rflux = imageBasedViewCoeffMatrixCommands(
                            dMatrix, self.relpath(receiver, projectFolder),
                            radFiles, sender, viewInfoFile,
                            viewFile, str(vwrSamp.outputFile),
                            self.daylightMtxParameters)

                        self.commands.append(rflux.toRadString())

                        radFilesBlacked = tuple(self.relpath(f, projectFolder)
                                                for f in rfluxSceneBlacked)

                        self._commands.append(':: :: 1.2 blacked scene daylight matrix')
                        self.daylightMtxParameters.samplingRaysCount = 1
                        self.daylightMtxParameters.ambientBounces = 1
                        rfluxDirect = imageBasedViewCoeffMatrixCommands(
                            dMatrixDirect, self.relpath(receiver, projectFolder),
                            radFilesBlacked, sender, viewInfoFile,
                            viewFile, str(vwrSamp.outputFile),
                            self.daylightMtxParameters)

                        self._commands.append(rfluxDirect.toRadString())

                        self._commands.append(':: :: 1.3 blacked scene analemma matrix')

                        if os.name == 'nt':
                            outputFilenameFormat = \
                                ' result\\{}_{}_{}_sun_%%04d.hdr'.format(
                                    view.name, wg.name, state.name)
                        else:
                            outputFilenameFormat = \
                                ' result\\{}_{}_{}_sun_%04d.hdr'.format(
                                    view.name, wg.name, state.name)

                        sunCommands = imagedBasedSunCoeffMatrixCommands(
                            outputFilenameFormat, view, str(vwrSamp.outputFile),
                            radFilesBlacked, self.relpath(analemma, projectFolder),
                            self.relpath(sunlist, projectFolder))

                        self._commands.extend(cmd.toRadString() for cmd in sunCommands)

                    # Generate resultsFile
                    self._commands.append(
                        ':: :: 2.1.0 total daylight matrix calculations')
                    dct = imageBasedViewMatrixCalculation(
                        dMatrix, view, wg, state, skyMtxTotal, 'total')
                    self.commands.append(dct.toRadString())

                    self._commands.append(':: :: 2.2.0 direct matrix calculations')
                    dctDirect = imageBasedViewMatrixCalculation(
                        dMatrixDirect, view, wg, state, skyMtxDirect, 'direct')
                    self.commands.append(dctDirect.toRadString())

                    self._commands.append(
                        ':: :: 2.3.0 enhanced direct matrix calculations')
                    # dctSun = viewSunCoeffMatrixCommands(sunMatrix)
                    dctSun = imageBasedViewMatrixCalculation(
                        sunMatrix, view, wg, state, analemmaMtx, 'sun')
                    self.commands.append(dctSun.toRadString())

                    self._commands.append(':: :: 2.4 final matrix calculation')

                    # TODO(sarith) final addition of the images
                    resultFiles = tuple(os.path.join(
                        projectFolder,
                        'results\\{}_{}_{}_{}.hdr'.format(
                            view.name, wg.name, state.name, '%04d' % (count + 1)))
                        for count, h in enumerate(self.skyMatrix.hoys)
                    )
                    self._resultFiles.extend(resultFiles)

        # # 4.3 write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        print "Files are written to: %s" % projectFolder
        return batchFile

    def results(self):
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
