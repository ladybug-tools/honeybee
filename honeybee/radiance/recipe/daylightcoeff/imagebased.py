"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""
from ..recipeutil import writeExtraFiles, glzSrfTowinGroup
from ..recipedcutil import writeRadFilesDaylightCoeff, createReferenceMapCommand
from ..recipedcutil import imageBasedViewSamplingCommands, \
    imageBasedViewCoeffMatrixCommands, imagedBasedSunCoeffMatrixCommands
from ...command.oconv import Oconv
from ...command.pcomb import Pcomb, PcombImage
from ...parameters.pcomb import PcombParameters
from ..parameters import getRadianceParametersImageBased
from ..recipedcutil import imageBasedViewMatrixCalculation
from ..recipedcutil import skyReceiver, getCommandsSky
from .._imagebasedbase import GenericImageBased
from ...parameters.vwrays import VwraysParameters
from ...imagecollection import ImageCollection
from ....futil import writeToFile

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
        """Radiance parameters for image based analysis (rfluxmtx).
            (Default: imagebased.LowQualityImage)"""

        self.vwraysParameters = vwraysParameters
        """Radiance parameters for vwrays.
            (Default: imagebased.LowQualityImage)"""

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

    @property
    def vwraysParameters(self):
        """Get and set Radiance parameters."""
        return self._vwraysParameters

    @vwraysParameters.setter
    def vwraysParameters(self, par):
        if not par:
            # set VwraysParameters as default radiance parameter for annual analysis
            par = VwraysParameters()
            par.samplingRaysCount = self.daylightMtxParameters.samplingRaysCount
        else:
            assert hasattr(par, 'isVwraysParameters'), \
                TypeError('Expected VwraysParameters not {}'.format(type(par)))
        assert par.samplingRaysCount == self.daylightMtxParameters.samplingRaysCount, \
            ValueError(
                'Number of samplingRaysCount should be equal between '
                'daylightMtxParameters [{}] and vwraysParameters [{}].'
                .format(self.daylightMtxParameters.samplingRaysCount,
                        par.samplingRaysCount))

        self._vwraysParameters = par

    def isDaylightMtxCreated(self, studyFolder, view, wg, state):
        """Check if hdr images for daylight matrix are already created."""
        for i in range(1 + 144 * (self.skyMatrix.skyDensity ** 2)):
            for t in ('total', 'direct'):
                fp = os.path.join(
                    studyFolder, 'result/dc\\%s\\%03d_%s..%s..%s.hdr' % (
                        t, i, view.name, wg.name, state.name)
                )

                if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                    # file doesn't exist or is smaller than 265 bytes
                    return False

        return True

    def isSunMtxCreated(self, studyFolder, view, wg, state):
        """Check if hdr images for daylight matrix are already created."""
        for count, h in enumerate(self.skyMatrix.hoys):
            fp = os.path.join(
                studyFolder, 'result/dc\\{}\\{}_{}..{}..{}.hdr'.format(
                    'isun', '%04d' % count, view.name, wg.name, state.name))

            if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                # file doesn't exist or is smaller than 265 bytes
                return False

        return True

    def isHdrMtxCreated(self, studyFolder, view, wg, state, stype):
        """Check if hourly hdr images for daylight matrix are already created."""
        for count, h in enumerate(self.skyMatrix.hoys):
            fp = os.path.join(
                studyFolder, 'result/hdr\\{}\\{}_{}..{}..{}.hdr'.format(
                    stype, '%04d' % (count + 1), view.name, wg.name, state.name))

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
                subfolders=['view', 'result/dc', 'result/hdr',
                            'result/dc/total', 'result/dc/direct', 'result/dc/isun',
                            'result/dc/refmap', 'result/hdr/total', 'result/hdr/direct',
                            'result/hdr/sun', 'result/hdr/combined', 'result/hdr/isun']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFilesDaylightCoeff(
            projectFolder + '\\scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )
        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '\\scene')

        # reset self.resultFiles
        self._resultFiles = [[] for v in xrange(self.viewCount)]

        # 1.write views
        viewFiles = self.writeViews(projectFolder + '\\view')

        if header:
            self.commands.append(self.header(projectFolder))

        # # 2.1.Create sky matrix.
        # # 2.2. Create sun matrix
        skycommands, skyfiles = getCommandsSky(projectFolder, self.skyMatrix,
                                               reuse=True)

        skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx = skyfiles
        self._commands.extend(skycommands)

        # for each window group - calculate total, direct and direct-analemma results
        # I can just add fenestration rad files here and that will work!

        # calculate the contribution of glazing if any with all window groups blacked
        # this is a hack. A better solution is to create a HBDynamicSurface from glazing
        # surfaces. The current limitation is that HBDynamicSurface can't have several
        # surfaces with different materials.
        allWindowGroups = [glzSrfTowinGroup()]
        allWindowGroups.extend(self.windowGroups)
        allWgsFiles = [glzfiles] + list(wgsfiles)

        # create the base octree for the scene
        # TODO(mostapha): this should be fine for most of the cases but
        # if one of the window groups has major material change in a step
        # that won't be included in this step.
        # add material file
        try:
            blkmaterial = [wgsfiles[0].fpblk[0]]
        except IndexError:
            # no window groups
            blkmaterial = []
        # add all the blacked window groups but the one in use
        # and finally add non-window group glazing as black
        wgsblacked = [f.fpblk[1] for f in wgsfiles] + list(glzfiles.fpblk)

        sceneFiles = [f for filegroups in (opqfiles.fp, glzfiles.fp, extrafiles.fp)
                      for f in filegroups]
        octSceneFiles = sceneFiles + blkmaterial + wgsblacked

        oc = Oconv(projectName)
        oc.sceneFiles = tuple(self.relpath(f, projectFolder)
                              for f in octSceneFiles)

        self._commands.append(oc.toRadString())

        # # 4.2.prepare vwray
        for viewCount, (view, viewFile) in enumerate(izip(self.views, viewFiles)):
            # create the reference map file
            self.commands.append(':: calculation for view: {}'.format(view.name))
            self.commands.append(':: 0 reference map')

            refmapfilename = '{}_map.hdr'.format(view.name)
            refmapfilepath = os.path.join('result/dc\\refmap', refmapfilename)

            if not self.reuseDaylightMtx or not os.path.isfile(
                    os.path.join(projectName, 'result/dc\\refmap', refmapfilename)):
                rfm = createReferenceMapCommand(
                    view, self.relpath(viewFile, projectFolder),
                    'result/dc\\refmap', oc.outputFile)
                self._commands.append(rfm.toRadString())

            # Step1: Create the view matrix.
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

                    sender = '-'

                    groundFileFormat = 'result/dc\\total\\%03d_%s..%s..%s.hdr' % (
                        1 + 144 * (self.skyMatrix.skyDensity ** 2),
                        view.name, wg.name, state.name
                    )

                    skyFileFormat = 'result/dc\\total\\%03d_{}..{}..{}.hdr'.format(
                        view.name, wg.name, state.name)

                    receiver = skyReceiver(
                        os.path.join(
                            projectFolder,
                            'sky\\rfluxSkyTotal..{}..{}.rad'.format(
                                wg.name, state.name)),
                        self.skyMatrix.skyDensity, groundFileFormat, skyFileFormat
                    )

                    groundFileFormat = 'result/dc\\direct\\%03d_%s..%s..%s.hdr' % (
                        1 + 144 * (self.skyMatrix.skyDensity ** 2),
                        view.name, wg.name, state.name
                    )

                    skyFileFormat = 'result/dc\\direct\\%03d_{}..{}..{}.hdr'.format(
                        view.name, wg.name, state.name)

                    receiverDir = skyReceiver(
                        os.path.join(projectFolder,
                                     'sky\\rfluxSkyDirect..{}..{}.rad'.format(
                                         wg.name, state.name)),
                        self.skyMatrix.skyDensity, groundFileFormat, skyFileFormat
                    )

                    radFilesBlacked = tuple(self.relpath(f, projectFolder)
                                            for f in rfluxSceneBlacked)
                    # Daylight matrix
                    if not self.reuseDaylightMtx or not \
                            self.isDaylightMtxCreated(projectFolder, view, wg, state):

                        self.reuseDaylightMtx = False

                        radFiles = tuple(self.relpath(f, projectFolder)
                                         for f in rfluxScene)

                        self._commands.append(
                            ':: :: 1. daylight matrix {}, {} > state {}'.format(
                                view.name, wg.name, state.name)
                        )

                        self._commands.append(':: :: 1.1 scene daylight matrix')

                        # output pattern is set in receiver
                        rflux = imageBasedViewCoeffMatrixCommands(
                            self.relpath(receiver, projectFolder),
                            radFiles, sender, viewInfoFile,
                            viewFile, str(vwrSamp.outputFile),
                            self.daylightMtxParameters)

                        self.commands.append(rflux.toRadString())
                    else:
                        print(
                            'reusing the dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if not self.reuseDaylightMtx or not \
                            self.isSunMtxCreated(projectFolder, view, wg, state):
                        self._commands.append(':: :: 1.2 blacked scene daylight matrix')

                        ab = int(self.daylightMtxParameters.ambientBounces)
                        self.daylightMtxParameters.ambientBounces = 1

                        # output pattern is set in receiver
                        rfluxDirect = imageBasedViewCoeffMatrixCommands(
                            self.relpath(receiverDir, projectFolder),
                            radFilesBlacked, sender, viewInfoFile,
                            viewFile, str(vwrSamp.outputFile),
                            self.daylightMtxParameters)

                        self._commands.append(rfluxDirect.toRadString())

                        self._commands.append(':: :: 1.3 blacked scene analemma matrix')

                        if os.name == 'nt':
                            outputFilenameFormat = \
                                ' result/dc\\isun\\%%04d_{}..{}..{}.hdr'.format(
                                    view.name, wg.name, state.name)
                        else:
                            outputFilenameFormat = \
                                ' result/dc\\isun\\%04d_{}..{}..{}.hdr'.format(
                                    view.name, wg.name, state.name)

                        sunCommands = imagedBasedSunCoeffMatrixCommands(
                            outputFilenameFormat, view, str(vwrSamp.outputFile),
                            radFilesBlacked, self.relpath(analemma, projectFolder),
                            self.relpath(sunlist, projectFolder))

                        # delete the files if they are already created
                        # rcontrib won't overwrite the files if they already exist
                        for hourcount in xrange(len(self.skyMatrix.hoys)):
                            sf = 'result/dc\\isun\\{:04d}_{}..{}..{}.hdr'.format(
                                hourcount, view.name, wg.name, state.name
                            )
                            try:
                                fp = os.path.join(projectFolder, sf)
                                os.remove(fp)
                            except Exception as e:
                                # failed to delete the file
                                if os.path.isfile(fp):
                                    print('Failed to remove {}:\n{}'.format(sf, e))

                        self._commands.extend(cmd.toRadString() for cmd in sunCommands)
                        self.daylightMtxParameters.ambientBounces = ab

                    else:
                        print(
                            'reusing the sun matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    # generate hourly images
                    if skycommands or not self.reuseDaylightMtx or not \
                        self.isHdrMtxCreated(projectFolder, view, wg,
                                             state, 'total'):
                        # Generate resultsFile
                        self._commands.append(
                            ':: :: 2.1.0 total daylight matrix calculations')
                        dct = imageBasedViewMatrixCalculation(
                            view, wg, state, skyMtxTotal, 'total')
                        self.commands.append(dct.toRadString())
                    else:
                        print(
                            'reusing the total dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if skycommands or not self.reuseDaylightMtx or not \
                        self.isHdrMtxCreated(projectFolder, view, wg,
                                             state, 'direct'):
                        self._commands.append(':: :: 2.2.0 direct matrix calculations')
                        dctDirect = imageBasedViewMatrixCalculation(
                            view, wg, state, skyMtxDirect, 'direct')
                        self._commands.append(dctDirect.toRadString())
                    else:
                        print(
                            'reusing the direct dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if skycommands or not self.reuseDaylightMtx or not \
                        self.isHdrMtxCreated(projectFolder, view, wg,
                                             state, 'sun'):
                        self._commands.append(
                            ':: :: 2.3.0 enhanced direct matrix calculations')
                        dctSun = imageBasedViewMatrixCalculation(
                            view, wg, state,
                            self.relpath(analemmaMtx, projectFolder), 'isun', 4)

                        self._commands.append(dctSun.toRadString())

                        # multiply the sun matrix with the reference map
                        # TODO: move this to a separate function
                        # TODO: write the loop as a for loop in bat/bash file
                        par = PcombParameters()
                        refmapImage = PcombImage(inputImageFile=refmapfilepath)
                        if os.name == 'nt':
                            par.expression = '"lo=li(1)*li(2)"'
                        else:
                            par.expression = "'lo=li(1)*li(2)'"

                        for hourcount in xrange(len(self.skyMatrix.hoys)):
                            inp = 'result/hdr\\isun\\{:04d}_{}..{}..{}.hdr'.format(
                                hourcount + 1, view.name, wg.name, state.name
                            )
                            out = 'result/hdr\\sun\\{:04d}_{}..{}..{}.hdr'.format(
                                hourcount + 1, view.name, wg.name, state.name
                            )
                            images = PcombImage(inputImageFile=inp), refmapImage

                            pcb = Pcomb(images, out, par)
                            self._commands.append(pcb.toRadString())
                    else:
                        print(
                            'reusing the enhanced direct dalight matrix for '
                            '{}:{} from the previous study.'
                            .format(wg.name, state.name))

                    resultFiles = tuple(os.path.join(
                        projectFolder,
                        'result/hdr\\%s\\{}_{}..{}..{}.hdr'.format(
                            '%04d' % (count + 1), view.name, wg.name, state.name))
                        for count, h in enumerate(self.skyMatrix.hoys)
                    )

                    self._resultFiles[viewCount].append(
                        (wg.name, state.name, resultFiles))

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
        hoys = self.skyMatrix.hoys

        for viewCount, viewResults in enumerate(self._resultFiles):
            imgc = ImageCollection(self.views[viewCount].name)

        for source, state, files in viewResults:
            sourceFiles = []
            for i in files:
                fpt = i % 'total'
                fpd = i % 'direct'
                fps = i % 'sun'
                sourceFiles.append((fpt, fpd, fps))

            imgc.addCoupledImageFiles(sourceFiles, hoys, source, state)

        # TODO(mostapha): Add properties to the class for output file addresses
        imgc.outputFolder = fpt.split('result/hdr')[0] + 'result/hdr\\combined'
        yield imgc

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
