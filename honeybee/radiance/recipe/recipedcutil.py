"""A collection of useful methods for daylight-coeff recipes."""
from ..command.rfluxmtx import Rfluxmtx
from ..command.dctimestep import Dctimestep
from ..command.rmtxop import Rmtxop, RmtxopMatrix
from ..command.gendaymtx import Gendaymtx
from ..sky.sunmatrix import SunMatrix
from ..command.oconv import Oconv
from ..command.rpict import Rpict
from ..command.rcontrib import Rcontrib
from ..command.vwrays import Vwrays
from ..parameters.imagebased import ImageBasedParameters
from .recipeutil import glzSrfTowinGroup
from .parameters import getRadianceParametersGridBased, getRadianceParametersImageBased

import os
from collections import namedtuple


def writeRadFilesDaylightCoeff(workingDir, projectName, opq, glz, wgs):
    """Write files to a target directory for daylight coefficeint method.

    The files will be written under
        workingDir/opaque
        workingDir/glazing
        workingDir/wgroup

    Args:
        workingDir: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        A named tuple for each RadFile as (fp, fpblk)
        fp returns the file path to the list of radiance files.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk'])

    folder = os.path.join(workingDir, 'opaque')
    of = opq.writeGeometries(folder, '%s..opq.rad' % projectName, 0, mkdir=True)
    om = opq.writeMaterials(folder, '%s..opq.mat' % projectName, 0, blacked=False)
    bm = opq.writeMaterials(folder, '%s..blk.mat' % projectName, 0, blacked=True)
    opqf = Files((om, of), (bm, of))

    folder = os.path.join(workingDir, 'glazing')
    ogf = glz.writeGeometries(folder, '%s..glz.rad' % projectName, 0, mkdir=True)
    ogm = glz.writeMaterials(folder, '%s..glz.mat' % projectName, 0, blacked=False)
    bgm = glz.writeMaterials(folder, '%s..blk.mat' % projectName, 0, blacked=True)
    glzf = Files((ogm, ogf), (bgm, ogf))

    wgfs = []
    folder = os.path.join(workingDir, 'wgroup')
    # write black material to folder
    for count, wgf in enumerate(wgs):
        # write it as a black geometry
        wg = wgf.hbSurfaces[0]
        name = wg.name
        if count == 0:
            wgbm = wgf.writeBlackMaterial(folder, 'black.mat', mkdir=True)

        wgbf = wgf.writeGeometriesBlacked(folder, '%s..blk.rad' % name, 0)

        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)
        wg.state = 0  # set the state back to 0
        wgfs.append(Files(wgfstate, (wgbm, wgbf)))

    return opqf, glzf, wgfs


def getCommandsSky(projectFolder, skyMatrix, reuse=True):
    """Get list of commands to generate the skies.

    1. total sky matrix
    2. direct only sky matrix
    3. sun matrix (aka analemma)

    This methdo genrates sun matrix under projectFolder/sky and return the commands
    to generate skies number 1 and 2.

    Returns a namedtuple for (outputFiles, commands)
    outputFiles in a namedtuple itself (skyMtxTotal, skyMtxDirect, analemma, sunlist,
        analemmaMtx).
    """
    OutputFiles = namedtuple('OutputFiles',
                             'skyMtxTotal skyMtxDirect analemma sunlist analemmaMtx')

    SkyCommands = namedtuple('SkyCommands', 'outputFiles commands')

    commands = []

    # # 2.1.Create sky matrix.
    skyMatrix.mode = 0
    skyMtxTotal = 'sky\\{}.smx'.format(skyMatrix.name)
    skyMatrix.mode = 1
    skyMtxDirect = 'sky\\{}.smx'.format(skyMatrix.name)
    skyMatrix.mode = 0

    # add commands for total and direct sky matrix.
    if hasattr(skyMatrix, 'isSkyMatrix'):
        for m in xrange(2):
            skyMatrix.mode = m
            gdm = skymtxToGendaymtx(skyMatrix, projectFolder)
            if gdm:
                note = ':: {} sky matrix'.format('direct' if m else 'total')
                commands.extend((note, gdm))
        skyMatrix.mode = 0
    else:
        # sky vector
        raise TypeError('You must use a SkyMatrix to generate the sky.')

    # # 2.2. Create sun matrix
    sm = SunMatrix(skyMatrix.wea, skyMatrix.north, skyMatrix.hoys, skyMatrix.skyType,
                   suffix=skyMatrix.suffix)
    analemma, sunlist, analemmaMtx = \
        sm.execute(os.path.join(projectFolder, 'sky'), reuse=reuse)

    of = OutputFiles(skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx)

    return SkyCommands(commands, of)


def getCommandsRadiationSky(projectFolder, skyMatrix, reuse=True):
    """Get list of commands to generate the skies.

    1. sky matrix diffuse
    3. sun matrix (aka analemma)

    This methdo genrates sun matrix under projectFolder/sky and return the commands
    to generate sky number 1.

    Returns a namedtuple for (outputFiles, commands)
    outputFiles in a namedtuple itself (skyMtxTotal, skyMtxDirect, analemma, sunlist,
        analemmaMtx).
    """
    OutputFiles = namedtuple('OutputFiles',
                             'skyMtxDiff analemma sunlist analemmaMtx')

    SkyCommands = namedtuple('SkyCommands', 'outputFiles commands')

    commands = []

    if not hasattr(skyMatrix, 'isSkyMatrix'):
        # sky vector
        raise TypeError('You must use a SkyMatrix to generate the sky.')

    # # 2.1.Create sky matrix.
    skyMatrix.mode = 2
    skyMtxDiff = 'sky\\{}.smx'.format(skyMatrix.name)
    gdm = skymtxToGendaymtx(skyMatrix, projectFolder)
    if gdm:
        note = ':: diffuse sky matrix'
        commands.extend((note, gdm))
    skyMatrix.mode = 0

    # # 2.2. Create sun matrix
    sm = SunMatrix(skyMatrix.wea, skyMatrix.north, skyMatrix.hoys, skyMatrix.skyType,
                   suffix=skyMatrix.suffix)
    analemma, sunlist, analemmaMtx = \
        sm.execute(os.path.join(projectFolder, 'sky'), reuse=reuse)

    of = OutputFiles(skyMtxDiff, analemma, sunlist, analemmaMtx)

    return SkyCommands(commands, of)


# TODO(mostapha): restructure inputs to make the method useful for a normal user.
# It's currently structured to satisfy what we need for the recipes.
def getCommandsSceneDaylightCoeff(
        projectName, skyDensity, projectFolder, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, reuseDaylightMtx=False,
        totalCount=1, radiationOnly=False):
    """Get commands for the static windows in the scene.

    Use getCommandsWGroupsDaylightCoeff to get the commands for the rest of the scene.

    Args:
        projectName: A string to generate uniqe file names for this project.
        skyDensity: Sky density for this study.
        projectFolder: Path to projectFolder.
        skyfiles: Collection of path to sky files. The order must be (skyMtxTotal,
            skyMtxDirect, analemma, sunlist, analemmaMtx). You can use getCommandsSky
            function to generate this list.
        inputfiles: Input files for this study. The order must be (opqfiles, glzfiles,
            wgsfiles, extrafiles). Each files object is a namedtuple which includes
            filepath to radiance files under fp and filepath to backed out files under
            fpblk.
        pointsFile: Path to pointsFile.
        totalPointCount: Number of total points inside pointsFile.
        rfluxmtxParameters: An instance of rfluxmtxParameters for daylight matrix.
        reuseDaylightMtx: A boolean not to include the commands for daylight matrix
            calculation if they already exist inside the folder.
    """
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles

    if len(wgsfiles) > 0:
        # material is the first file
        blkmaterial = [wgsfiles[0].fpblk[0]]
        # collect files for blacked geometries for all window groups
        wgsblacked = [f.fpblk[1] for c, f in enumerate(wgsfiles)]
    else:
        # there is no window group, return an empty tuple
        blkmaterial = ()
        wgsblacked = ()

    windowGroup = glzSrfTowinGroup()
    windowGroupfiles = glzfiles.fp

    commands, results = _getCommandsDaylightCoeff(
        projectName, skyDensity, projectFolder, windowGroup, skyfiles,
        inputfiles, pointsFile, totalPointCount, blkmaterial, wgsblacked,
        rfluxmtxParameters, 0, windowGroupfiles, reuseDaylightMtx, (1, totalCount),
        radiationOnly=radiationOnly)

    return commands, results


def getCommandsWGroupsDaylightCoeff(
        projectName, skyDensity, projectFolder, windowGroups, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, reuseDaylightMtx=False,
        totalCount=1, radiationOnly=False):
    """Get commands for the static windows in the scene.

    Use getCommandsWGroupsDaylightCoeff to get the commands for the rest of the scene.

    Args:
        projectName: A string to generate uniqe file names for this project.
        skyDensity: Sky density for this study.
        projectFolder: Path to projectFolder.
        windowGroups: List of windowGroups.
        skyfiles: Collection of path to sky files. The order must be (skyMtxTotal,
            skyMtxDirect, analemma, sunlist, analemmaMtx). You can use getCommandsSky
            function to generate this list.
        inputfiles: Input files for this study. The order must be (opqfiles, glzfiles,
            wgsfiles, extrafiles). Each files object is a namedtuple which includes
            filepath to radiance files under fp and filepath to backed out files under
            fpblk.
        pointsFile: Path to pointsFile.
        totalPointCount: Number of total points inside pointsFile.
        rfluxmtxParameters: An instance of rfluxmtxParameters for daylight matrix.
        reuseDaylightMtx: A boolean not to include the commands for daylight matrix
            calculation if they already exist inside the folder.
    """
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    commands = []
    results = []
    for count, windowGroup in enumerate(windowGroups):
        # get black material file
        blkmaterial = [wgsfiles[count].fpblk[0]]
        # add all the blacked window groups but the one in use
        # and finally add non-window group glazing as black
        wgsblacked = \
            [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count] + \
            list(glzfiles.fpblk)

        counter = 2 + sum(wg.stateCount for wg in windowGroups[:count])

        cmds, res = _getCommandsDaylightCoeff(
            projectName, skyDensity, projectFolder, windowGroup, skyfiles,
            inputfiles, pointsFile, totalPointCount, blkmaterial, wgsblacked,
            rfluxmtxParameters, count, windowGroupfiles=None,
            reuseDaylightMtx=reuseDaylightMtx, counter=(counter, totalCount),
            radiationOnly=radiationOnly)

        commands.extend(cmds)
        results.extend(res)
    return commands, results


# TODO(): use logging instead of print
def _getCommandsDaylightCoeff(
        projectName, skyDensity, projectFolder, windowGroup, skyfiles, inputfiles,
        pointsFile, totalPointCount, blkmaterial, wgsblacked, rfluxmtxParameters,
        windowGroupCount=0, windowGroupfiles=None, reuseDaylightMtx=False, counter=None,
        radiationOnly=False):
    """Get commands for the daylight coefficient recipe.

    This function is used by getCommandsSceneDaylightCoeff and
    getCommandsWGroupsDaylightCoeff. You usually don't want to use this function
    directly.
    """
    commands = []
    resultFiles = []
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    if radiationOnly:
        skyMtxDiff, analemma, sunlist, analemmaMtx = skyfiles
    else:
        skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx = skyfiles

    for scount, state in enumerate(windowGroup.states):
        # 2.3.Generate daylight coefficients using rfluxmtx
        # collect list of radiance files in the scene for both total and direct
        if counter:
            p = ((counter[0] + scount - 1.0) / counter[1]) * 100
            c = int(p / 10)
            commands.append(
                ':: Done with {} of {} ^|{}{}^| ({:.2f}%%)'.format(
                    counter[0] + scount - 1, counter[1], '#' * c,
                    '-' * (10 - c), float(p)
                )
            )
        commands.append('::')
        commands.append(
            ':: start of the calculation for {}, {}. State {} of {}'.format(
                windowGroup.name, state.name, scount + 1, windowGroup.stateCount
            )
        )
        commands.append('::')

        if not windowGroupfiles:
            # in case window group is not already provided
            windowGroupfiles = (wgsfiles[windowGroupCount].fp[scount],)

        rfluxScene = (
            f for fl in
            (windowGroupfiles, opqfiles.fp, extrafiles.fp,
             blkmaterial, wgsblacked)
            for f in fl)

        rfluxSceneBlacked = (
            f for fl in
            (windowGroupfiles, opqfiles.fpblk, extrafiles.fpblk,
             blkmaterial, wgsblacked)
            for f in fl)

        dMatrix = 'result\\matrix\\normal_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        dMatrixDirect = 'result\\matrix\\black_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        sunMatrix = 'result\\matrix\\sun_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
                or not reuseDaylightMtx:
            radFiles = tuple(os.path.relpath(f, projectFolder) for f in rfluxScene)
            sender = '-'
            receiver = skyReceiver(
                os.path.join(projectFolder, 'sky\\rfluxSky.rad'), skyDensity
            )

            commands.append(':: :: 1. calculating daylight matrices')
            commands.append('::')

            commands.append(':: :: [1/3] scene daylight matrix')
            commands.append(
                ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [scene]'
                ' ^> [dc.mtx]'
            )
            commands.append('::')

            # samplingRaysCount = 1 based on @sariths studies
            rflux = coeffMatrixCommands(
                dMatrix, os.path.relpath(receiver, projectFolder), radFiles, sender,
                os.path.relpath(pointsFile, projectFolder), totalPointCount,
                rfluxmtxParameters
            )
            commands.append(rflux.toRadString())

            radFilesBlacked = tuple(os.path.relpath(f, projectFolder)
                                    for f in rfluxSceneBlacked)

            commands.append(':: :: [2/3] black scene daylight matrix')
            commands.append(
                ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] '
                '[blacked scene] ^> [black dc.mtx]'
            )
            commands.append('::')

            originalValue = int(rfluxmtxParameters.ambientBounces)
            rfluxmtxParameters.ambientBounces = 1
            rfluxDirect = coeffMatrixCommands(
                dMatrixDirect, os.path.relpath(receiver, projectFolder),
                radFilesBlacked, sender, os.path.relpath(pointsFile, projectFolder),
                totalPointCount, rfluxmtxParameters
            )
            commands.append(rfluxDirect.toRadString())
            rfluxmtxParameters.ambientBounces = originalValue

            commands.append(':: :: [3/3] black scene analemma daylight matrix')
            commands.append(
                ':: :: rcontrib - [sunMatrix] [points] [wgroup] [blacked wgroups] '
                '[blacked scene] ^> [analemma dc.mtx]'
            )
            commands.append('::')
            sunCommands = sunCoeffMatrixCommands(
                sunMatrix, os.path.relpath(pointsFile, projectFolder),
                radFilesBlacked, os.path.relpath(analemma, projectFolder),
                os.path.relpath(sunlist, projectFolder),
                rfluxmtxParameters.irradianceCalc
            )

            commands.extend(cmd.toRadString() for cmd in sunCommands)
        else:
            commands.append(':: :: 1. reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: 2. matrix multiplication')
        commands.append('::')
        if radiationOnly:
            commands.append(':: :: [1/2] calculating daylight mtx * diffuse sky')
            commands.append(
                ':: :: dctimestep [dc.mtx] [diffuse sky] ^> [diffuse results.rgb]')
            dctTotal = matrixCalculation(
                'tmp\\diffuse..{}..{}.rgb'.format(windowGroup.name, state.name),
                dMatrix=dMatrix, skyMatrix=skyMtxDiff
            )
        else:
            commands.append(':: :: [1/3] calculating daylight mtx * total sky')
            commands.append(
                ':: :: dctimestep [dc.mtx] [total sky] ^> [total results.rgb]')

            dctTotal = matrixCalculation(
                'tmp\\total..{}..{}.rgb'.format(windowGroup.name, state.name),
                dMatrix=dMatrix, skyMatrix=skyMtxTotal
            )

        commands.append(dctTotal.toRadString())

        if radiationOnly:
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [diffuse results.ill]'
            )
            finalmtx = RGBMatrixFileToIll(
                (dctTotal.outputFile,),
                'result\\diffuse..{}..{}.ill'.format(windowGroup.name, state.name)
            )
        else:
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [total results.ill]'
            )
            finalmtx = RGBMatrixFileToIll(
                (dctTotal.outputFile,),
                'result\\total..{}..{}.ill'.format(windowGroup.name, state.name)
            )

        commands.append('::')
        commands.append(finalmtx.toRadString())

        if not radiationOnly:
            commands.append(
                ':: :: [2/3] calculating black daylight mtx * direct only sky')
            commands.append(
                ':: :: dctimestep [black dc.mtx] [direct only sky] ^> '
                '[direct results.rgb]')

            dctDirect = matrixCalculation(
                'tmp\\direct..{}..{}.rgb'.format(windowGroup.name, state.name),
                dMatrix=dMatrixDirect, skyMatrix=skyMtxDirect
            )
            commands.append(dctDirect.toRadString())
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [direct results.rgb] ^> '
                '[direct results.ill]'
            )
            commands.append('::')
            finalmtx = RGBMatrixFileToIll(
                (dctDirect.outputFile,),
                'result\\direct..{}..{}.ill'.format(windowGroup.name, state.name)
            )
            commands.append(finalmtx.toRadString())

        if not radiationOnly:
            commands.append(':: :: [3/3] calculating black daylight mtx * analemma')
        else:
            commands.append(':: :: [2/2] calculating black daylight mtx * analemma')

        commands.append(
            ':: :: dctimestep [black dc.mtx] [analemma only sky] ^> [sun results.rgb]')
        dctSun = sunMatrixCalculation(
            'tmp\\sun..{}..{}.rgb'.format(windowGroup.name, state.name),
            dcMatrix=sunMatrix,
            skyMatrix=os.path.relpath(analemmaMtx, projectFolder)
        )
        commands.append(dctSun.toRadString())

        commands.append(
            ':: :: rmtxop -c 47.4 119.9 11.6 [sun results.rgb] ^> '
            '[sun results.ill]'
        )
        commands.append('::')
        finalmtx = RGBMatrixFileToIll(
            (dctSun.outputFile,),
            'result\\sun..{}..{}.ill'.format(windowGroup.name, state.name)
        )
        commands.append(finalmtx.toRadString())

        commands.append(':: :: 3. calculating final results')
        if radiationOnly:
            commands.append(
                ':: :: rmtxop [diff results.ill] '
                '+ [sun results.ill] ^> [final results.ill]'
            )
            commands.append('::')
            fmtx = finalMatrixAdditionRadiation(
                'result\\diffuse..{}..{}.ill'.format(windowGroup.name, state.name),
                'result\\sun..{}..{}.ill'.format(windowGroup.name, state.name),
                'result\\{}..{}.ill'.format(windowGroup.name, state.name)
            )
            commands.append(fmtx.toRadString())
        else:
            commands.append(
                ':: :: rmtxop [total results.ill] - [direct results.ill] '
                '+ [sun results.ill] ^> [final results.ill]'
            )
            commands.append('::')
            fmtx = finalMatrixAddition(
                'result\\total..{}..{}.ill'.format(windowGroup.name, state.name),
                'result\\direct..{}..{}.ill'.format(windowGroup.name, state.name),
                'result\\sun..{}..{}.ill'.format(windowGroup.name, state.name),
                'result\\{}..{}.ill'.format(windowGroup.name, state.name)
            )
            commands.append(fmtx.toRadString())

        commands.append(
            ':: end of calculation for {}, {}'.format(windowGroup.name, state.name))
        commands.append('::')
        commands.append('::')

        resultFiles.append(
            os.path.join(projectFolder, str(fmtx.outputFile))
        )

    return commands, resultFiles


def imageBasedViewSamplingCommands(projectFolder, view, viewFile, vwraysParameters):
    """Return VWrays command for calculating view coefficient matrix."""
    # calculate view dimensions
    vwrDimFile = os.path.join(
        projectFolder, r'view\\{}.dim'.format(view.name))
    x, y = view.getViewDimension()
    with open(vwrDimFile, 'wb') as vdfile:
        vdfile.write('-x %d -y %d -ld-\n' % (x, y))

    # calculate sampling for each view
    # the value will be different for each view
    vwraysParameters.xResolution = view.xRes
    vwraysParameters.yResolution = view.yRes

    vwrSamp = Vwrays()
    vwrSamp.vwraysParameters = vwraysParameters
    vwrSamp.viewFile = os.path.relpath(viewFile, projectFolder)
    vwrSamp.outputFile = r'view\\{}.rays'.format(view.name)
    vwrSamp.outputDataFormat = 'f'

    return vwrDimFile, vwrSamp


def createReferenceMapCommand(view, viewFile, outputfolder, octreeFile):
    """Create a reference map to conver illuminance to luminance."""
    # set the parameters / options
    imgPar = ImageBasedParameters()
    imgPar.ambientAccuracy = 0
    imgPar.ambientValue = [0.31831] * 3
    imgPar.pixelSampling = 1
    imgPar.pixelJitter = 1
    x, y = view.getViewDimension()
    imgPar.xResolution = x
    imgPar.yResolution = y

    rp = Rpict()
    rp.rpictParameters = imgPar
    rp.octreeFile = octreeFile
    rp.viewFile = viewFile
    rp.outputFile = os.path.join(outputfolder, '{}_map.hdr'.format(view.name))
    return rp


def imagedBasedSunCoeffMatrixCommands(
        outputFilenameFormat, view, viewRaysFile, sceneFiles, analemma, sunlist):
    # output, pointFile, sceneFiles, analemma, sunlist, irradianceCalc

    octree = Oconv()
    octree.sceneFiles = list(sceneFiles) + [analemma]
    octree.outputFile = 'analemma.oct'

    # Creating sun coefficients
    # -ab 0 -i -ffc -dj 0 -dc 1 -dt 0
    rctbParam = getRadianceParametersImageBased(0, 1).smtx
    rctbParam.xDimension, rctbParam.yDimension = view.getViewDimension()
    rctbParam.modFile = sunlist
    rctbParam.outputDataFormat = 'fc'
    rctbParam.irradianceCalc = None  # -I
    rctbParam.iIrradianceCalc = True  # -i
    rctbParam.outputFilenameFormat = outputFilenameFormat

    rctb = Rcontrib()
    rctb.octreeFile = octree.outputFile
    rctb.pointsFile = viewRaysFile
    rctb.rcontribParameters = rctbParam
    return (octree, rctb)


def imageBasedViewCoeffMatrixCommands(
        receiver, radFiles, sender, viewInfoFile, viewFile, viewRaysFile,
        rfluxmtxParameters=None):
    """Returns radiance commands to create coefficient matrix.

    Args:
        receiver: A radiance file to indicate the receiver. In view matrix it will be the
        window group and in daylight matrix it will be the sky.
        radFiles: A collection of Radiance files that should be included in the scene.
        sender: A collection of files for senders if senders are radiance geometries
            such as window groups (Default: '-').
        pointsFile: Path to point file which will be used instead of sender.
        numberOfPoints: Number of points in pointsFile as an integer.
        samplingRaysCount: Number of sampling rays (Default: 1000).
        rfluxmtxParameters: Radiance parameters for Rfluxmtx command using a
            RfluxmtxParameters instance (Default: None).
    """
    rflux = Rfluxmtx()
    rflux.rfluxmtxParameters = rfluxmtxParameters
    rflux.radFiles = radFiles
    rflux.sender = sender or '-'
    rflux.receiverFile = receiver
    rflux.outputDataFormat = 'fc'
    rflux.verbose = True
    rflux.viewInfoFile = viewInfoFile
    rflux.viewRaysFile = viewRaysFile

    return rflux


def coeffMatrixCommands(outputName, receiver, radFiles, sender, pointsFile=None,
                        numberOfPoints=None, rfluxmtxParameters=None):
    """Returns radiance commands to create coefficient matrix.

    Args:
        outputName: Output file name.
        receiver: A radiance file to indicate the receiver. In view matrix it will be the
        window group and in daylight matrix it will be the sky.
        radFiles: A collection of Radiance files that should be included in the scene.
        sender: A collection of files for senders if senders are radiance geometries
            such as window groups (Default: '-').
        pointsFile: Path to point file which will be used instead of sender.
        numberOfPoints: Number of points in pointsFile as an integer.
        rfluxmtxParameters: Radiance parameters for Rfluxmtx command using a
            RfluxmtxParameters instance (Default: None).
    """
    sender = sender or '-'
    radFiles = radFiles or ()
    numberOfPoints = numberOfPoints or 0
    rfluxmtx = Rfluxmtx()

    if sender == '-':
        assert pointsFile, \
            ValueError('You have to set the pointsFile when sender is not defined.')

    # -------------- set the parameters ----------------- #
    rfluxmtx.rfluxmtxParameters = rfluxmtxParameters

    # -------------- set up the sender objects ---------- #
    # '-' in case of view matrix, window group in case of
    # daylight matrix. This is normally the receiver file
    # in view matrix
    rfluxmtx.sender = sender

    # points file are the senders in view matrix
    rfluxmtx.numberOfPoints = numberOfPoints
    rfluxmtx.pointsFile = pointsFile

    # --------------- set up the  receiver --------------- #
    # This will be the window for view matrix and the sky for
    # daylight matrix. It makes sense to make a method for each
    # of thme as they are pretty repetitive
    # Klems full basis sampling
    rfluxmtx.receiverFile = receiver

    # ------------- add radiance geometry files ----------------
    # For view matrix it's usually the room itself and the materials
    # in case of each view analysis rest of the windows should be
    # blacked! In case of daylight matrix it will be the context
    # outside the window.
    rfluxmtx.radFiles = radFiles

    # output file address/name
    rfluxmtx.outputMatrix = outputName

    return rfluxmtx


def windowGroupToReceiver(filepath, upnormal, materialName='vmtx_glow'):
    """Take a filepath to a window group and create a receiver."""
    recCtrlPar = Rfluxmtx.controlParameters(hemiType='kf', hemiUpDirection=upnormal)
    wg_m = Rfluxmtx.addControlParameters(filepath, {materialName: recCtrlPar})
    return wg_m


def skyReceiver(filepath, density, groundFileFormat=None, skyFileFormat=None):
    """Create a receiver sky for daylight coefficient studies."""
    if not (groundFileFormat and skyFileFormat):
        return Rfluxmtx.defaultSkyGround(filepath, skyType='r{}'.format(density))
    else:
        return Rfluxmtx.defaultSkyGround(
            filepath, skyType='r{}'.format(density),
            groundFileFormat=groundFileFormat,
            skyFileFormat=skyFileFormat)


def matrixCalculation(output, vMatrix=None, tMatrix=None, dMatrix=None, skyMatrix=None):
    """Get commands for matrix calculation.

    This method sets up a matrix calculations using Dctimestep.
    """
    dct = Dctimestep()
    dct.tmatrixFile = tMatrix
    dct.vmatrixSpec = vMatrix
    dct.dmatrixFile = dMatrix
    dct.skyVectorFile = skyMatrix
    dct.outputFile = output
    return dct


def imageBasedViewMatrixCalculation(view, wg, state, skyMatrix, extention='',
                                    digits=3):
    dct = Dctimestep()
    if os.name == 'nt':
        dct.daylightCoeffSpec = \
            'result\\dc\\{}\\%%0{}d_{}..{}..{}.hdr'.format(
                extention, digits, view.name, wg.name, state.name)
    else:
        dct.daylightCoeffSpec = \
            'result\\dc\\{}\\%0{}d_{}..{}..{}.hdr'.format(
                extention, digits, view.name, wg.name, state.name)

    dct.skyVectorFile = skyMatrix

    # sky matrix is annual
    if os.name == 'nt':
        dct.dctimestepParameters.outputDataFormat = \
            ' result\\hdr\\{}\\%%04d_{}..{}..{}.hdr'.format(
                extention, view.name, wg.name, state.name)
    else:
        dct.dctimestepParameters.outputDataFormat = \
            ' result\\hdr\\{}\\%04d_{}..{}..{}.hdr'.format(
                extention, view.name, wg.name, state.name)

    return dct


def sunMatrixCalculation(output, dcMatrix=None, skyMatrix=None):
    """Get commands for sun matrix calculation.

    This method sets up a matrix calculations using Dctimestep.
    """
    dct = Dctimestep()
    dct.daylightCoeffSpec = dcMatrix
    dct.skyVectorFile = skyMatrix
    dct.outputFile = output
    return dct


def sunCoeffMatrixCommands(output, pointFile, sceneFiles, analemma, sunlist,
                           irradianceCalc):
    """Return commands for calculating analemma coefficient.

    Args:
        output: Output daylight coefficient file (e.g. suncoeff.dc).
        pointFile: Path to point / analysis grid file. In case of multiple grid
            put them together in a single file.
        sceneFiles: A list fo scene files. Usually black scene.
        analemma: Path to analemma file. You can generate analemma file using
            SunMatrix class. Analemma has list of sun positions with their respective
            values.
        sunlist: Path to sunlist. Use SunMatrix to generate sunlist.
        simulationType:
    Returns:
        octree and rcontrib commands ready to be executed.
    """
    octree = Oconv()
    octree.sceneFiles = list(sceneFiles) + [analemma]
    octree.outputFile = 'analemma.oct'

    # Creating sun coefficients
    rctbParam = getRadianceParametersGridBased(0, 1).smtx
    rctbParam.modFile = sunlist
    rctbParam.irradianceCalc = irradianceCalc

    rctb = Rcontrib()
    rctb.octreeFile = octree.outputFile
    rctb.outputFile = output
    rctb.pointsFile = pointFile
    rctb.rcontribParameters = rctbParam
    return (octree, rctb)


def finalMatrixAddition(skymtx, skydirmtx, sunmtx, output):
    """Add final sky, direct sky and sun matrix."""
    # Instantiate matrices for subtraction and addition.
    finalMatrix = Rmtxop()

    # std. dc matrix.
    dcMatrix = RmtxopMatrix()
    dcMatrix.matrixFile = skymtx

    # direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dcDirectMatrix = RmtxopMatrix()
    dcDirectMatrix.matrixFile = skydirmtx
    dcDirectMatrix.scalarFactors = [-1]

    # Sun coefficient matrix.
    sunCoeffMatrix = RmtxopMatrix()
    sunCoeffMatrix.matrixFile = sunmtx

    # combine the matrices together. Sequence is extremely important
    finalMatrix.rmtxopMatrices = [dcMatrix, dcDirectMatrix, sunCoeffMatrix]
    finalMatrix.outputFile = output

    return finalMatrix


def finalMatrixAdditionRadiation(skydifmtx, sunmtx, output):
    """Add final diffuse sky and sun matrix."""
    # Instantiate matrices for subtraction and addition.
    finalMatrix = Rmtxop()

    # std. dc matrix.
    dcMatrix = RmtxopMatrix()
    dcMatrix.matrixFile = skydifmtx

    # Sun coefficient matrix.
    sunCoeffMatrix = RmtxopMatrix()
    sunCoeffMatrix.matrixFile = sunmtx

    # combine the matrices together. Sequence is extremely important
    finalMatrix.rmtxopMatrices = [dcMatrix, sunCoeffMatrix]
    finalMatrix.outputFile = output

    return finalMatrix


def RGBMatrixFileToIll(input, output):
    """Convert rgb values in matrix to illuminance values."""
    finalmtx = Rmtxop(matrixFiles=input, outputFile=output)
    finalmtx.rmtxopParameters.outputFormat = 'a'
    finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
    finalmtx.rmtxopParameters.transposeMatrix = False
    return finalmtx


def skymtxToGendaymtx(skyMatrix, targetFolder):
    """Return gendaymtx command based on input skyMatrix."""
    weaFilepath = 'sky\\{}.wea'.format(skyMatrix.name)
    skyMtx = 'sky\\{}.smx'.format(skyMatrix.name)
    hoursFile = os.path.join(targetFolder, 'sky\\{}.hrs'.format(skyMatrix.name))

    if not os.path.isfile(os.path.join(targetFolder, skyMtx)) \
            or not os.path.isfile(os.path.join(targetFolder, weaFilepath)) \
            or not skyMatrix.hoursMatch(hoursFile):
        # write wea file to folder
        skyMatrix.writeWea(os.path.join(targetFolder, 'sky'), writeHours=True)
        gdm = Gendaymtx(outputName=skyMtx, weaFile=weaFilepath)
        gdm.gendaymtxParameters = skyMatrix.skyMatrixParameters
        return gdm.toRadString()
