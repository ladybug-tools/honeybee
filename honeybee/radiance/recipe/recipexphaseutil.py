"""A collection of useful methods for multi-phase recipes."""

from .recipedcutil import windowGroupToReceiver, coeffMatrixCommands, skyReceiver
from .recipedcutil import matrixCalculation, RGBMatrixFileToIll, sunCoeffMatrixCommands
from .recipedcutil import sunMatrixCalculation, finalMatrixAddition
from ...futil import preparedir, copyFilesToFolder

import os
from collections import namedtuple


def writeRadFilesMultiPhase(workingDir, projectName, opq, glz, wgs):
    """Write files to a target directory for multi-phase method.

    This method should only be used for daylight coefficeint and multi-phase
    daylight simulations. The files will be written under
        workingDir/opaque
        workingDir/glazing
        workingDir/wgroup

    Args:
        workingDir: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        A named tuple for each RadFile as (fp, fpblk, fpglw)
        fp returns the file path to the list of radiance files. It will be glowed
            files for windowGroups.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk', 'fpglw'])

    folder = os.path.join(workingDir, 'opaque')
    of = opq.writeGeometries(folder, '%s..opq.rad' % projectName, 0, mkdir=True)
    om = opq.writeMaterials(folder, '%s..opq.mat' % projectName, 0, blacked=False)
    bm = opq.writeMaterials(folder, '%s..blk.mat' % projectName, 0, blacked=True)
    opqf = Files((om, of), (bm, of), ())

    folder = os.path.join(workingDir, 'glazing')
    ogf = glz.writeGeometries(folder, '%s..glz.rad' % projectName, 0, mkdir=True)
    ogm = glz.writeMaterials(folder, '%s..glz.mat' % projectName, 0, blacked=False)
    bgm = glz.writeMaterials(folder, '%s..blk.mat' % projectName, 0, blacked=True)
    glzf = Files((ogm, ogf), (bgm, ogf), ())

    wgfs = []
    folder = os.path.join(workingDir, 'wgroup')
    bsdfs = []
    bsdffolder = os.path.join(workingDir, 'bsdf')
    preparedir(bsdffolder)
    # write black material to folder
    for count, wgf in enumerate(wgs):
        # write it as a black geometry
        wg = wgf.hbSurfaces[0]
        name = wg.name
        if count == 0:
            wgbm = wgf.writeBlackMaterial(folder, 'black.mat', mkdir=True)

        wgbf = wgf.writeGeometriesBlacked(folder, '%s..blk.rad' % name, 0)
        wggf = wgf.write(folder, '%s..glw.rad' % name, 0, flipped=True,
                         glowed=True, mkdir=True)
        recf = windowGroupToReceiver(wggf, wg.upnormal, wg.radianceMaterial.name)
        # remove the original window group and rename the new one to original
        os.remove(wggf)
        os.rename(recf, wggf)

        # copy xml files for each state to bsdf folder
        # raise TypeError if material is not BSDF
        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            assert hasattr(wg.radianceMaterial, 'xmlfile'), \
                ValueError(
                    'RadianceMaterial for all the states should be BSDF material.'
                    ' Radiance Material for {} state is {}.'.format(
                        state.name, type(wg.radianceMaterial)))
            bsdfs.append(wg.radianceMaterial.xmlfile)
            # write the file for each state. only useful for 5-phase
            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)

        wg.state = 0  # set the state back to 0
        wgfs.append(Files(wgfstate, (wgbm, wgbf), (wggf,)))

        copyFilesToFolder(bsdfs, bsdffolder)

    return opqf, glzf, wgfs


def getCommandsViewDaylightMatrices(
    projectFolder, windowGroup, count, inputfiles, pointsFile,
    numberOfPoints, skyDensity, viewMtxParameters, daylightMtxParameters,
        reuseViewMtx=False, reuseDaylightMtx=False, phasesCount=3):
    """Get commnds, view matrix file and daylight matrix file."""
    commands = []
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    # add material file
    blkmaterial = [wgsfiles[count].fpblk[0]]
    # add all the blacked window groups but the one in use
    # and finally add non-window group glazing as black
    wgsblacked = \
        [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count] + \
        list(glzfiles.fpblk)

    # for scount, state in enumerate(wg.states):
    # 2.3.Generate daylight coefficients using rfluxmtx
    # collect list of radiance files in the scene for both total and direct
    commands.append(
        ':: start of the 3-phase calculation for the window group {}'.format(
            windowGroup.name)
    )

    vreceiver = wgsfiles[count].fpglw[0]

    vrfluxScene = (
        f for fl in
        (opqfiles.fp, blkmaterial, wgsblacked)
        for f in fl)

    drfluxScene = (
        f for fl in
        (opqfiles.fp, extrafiles.fp, blkmaterial, wgsblacked)
        for f in fl)

    # 3.2.Generate view matrix
    vMatrix = 'result\\matrix\\{}.vmx'.format(windowGroup.name)
    if not os.path.isfile(os.path.join(projectFolder, vMatrix)) \
            or not reuseViewMtx:
        commands.append(':: :: [1/{}] calculating view matrix'.format(phasesCount))
        commands.append(
            ':: :: rfluxmtx - [wgroup] [scene] [points] [blacked wgroups]'
            ' ^> [*.vmx]'
        )
        commands.append('::')
        # prepare input files
        radFiles = tuple(os.path.relpath(f, projectFolder) for f in vrfluxScene)

        vmtx = coeffMatrixCommands(
            vMatrix, os.path.relpath(vreceiver, projectFolder), radFiles, '-',
            os.path.relpath(pointsFile, projectFolder), numberOfPoints,
            viewMtxParameters)

        commands.append(vmtx.toRadString())

    # 3.3 daylight matrix
    dMatrix = 'result\\matrix\\{}_{}.dmx'.format(windowGroup.name, skyDensity)

    if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
            or not reuseDaylightMtx:
        sender = os.path.relpath(vreceiver, projectFolder)

        receiver = skyReceiver(
            os.path.join(projectFolder, 'sky\\rfluxSky.rad'), skyDensity
        )

        radFiles = tuple(os.path.relpath(f, projectFolder) for f in drfluxScene)

        dmtx = coeffMatrixCommands(
            dMatrix, os.path.relpath(receiver, projectFolder), radFiles,
            sender, None, None, daylightMtxParameters)

        commands.append(':: :: [2/{}] calculating daylight matrix'.format(phasesCount))
        commands.append(
            ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [scene]'
            ' ^> [*.dmx]'
        )
        commands.append('::')
        commands.append(dmtx.toRadString())

    return commands, vMatrix, dMatrix


def getCommandsDirectViewDaylightMatrices(
    projectFolder, windowGroup, count, inputfiles, pointsFile,
    numberOfPoints, skyDensity, viewMtxParameters, daylightMtxParameters,
        reuseViewMtx=False, reuseDaylightMtx=False):
    """Get commnds, view matrix file and daylight matrix file for direct calculation."""
    commands = []
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    # add material file
    blkmaterial = [wgsfiles[count].fpblk[0]]
    # add all the blacked window groups but the one in use
    # and finally add non-window group glazing as black
    wgsblacked = \
        [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count] + \
        list(glzfiles.fpblk)

    # for scount, state in enumerate(wg.states):
    # 2.3.Generate daylight coefficients using rfluxmtx
    # collect list of radiance files in the scene for both total and direct
    commands.append(
        ':: start of the 3-phase direct calculation for the window group {}'.format(
            windowGroup.name)
    )

    vreceiver = wgsfiles[count].fpglw[0]

    # change here to create a black scene instead
    vrfluxScene = (
        f for fl in
        (opqfiles.fpblk, blkmaterial, wgsblacked)
        for f in fl)

    drfluxScene = (
        f for fl in
        (opqfiles.fpblk, extrafiles.fpblk, blkmaterial, wgsblacked)
        for f in fl)

    # 3.2.Generate view matrix
    vMatrix = 'result\\matrix\\{}_dir.vmx'.format(windowGroup.name)
    if not os.path.isfile(os.path.join(projectFolder, vMatrix)) \
            or not reuseViewMtx:
        commands.append(':: :: [4-1/5] calculating direct view matrix')
        commands.append(
            ':: :: rfluxmtx - [wgroup] [blacked scene] [points] [blacked wgroups]'
            ' ^> [*.vmx]'
        )
        commands.append('::')
        # prepare input files
        radFiles = tuple(os.path.relpath(f, projectFolder) for f in vrfluxScene)

        ab = int(viewMtxParameters.ambientBounces)
        viewMtxParameters.ambientBounces = 1
        vmtx = coeffMatrixCommands(
            vMatrix, os.path.relpath(vreceiver, projectFolder), radFiles, '-',
            os.path.relpath(pointsFile, projectFolder), numberOfPoints,
            viewMtxParameters)
        viewMtxParameters.ambientBounces = ab
        commands.append(vmtx.toRadString())

    # 3.3 daylight matrix
    dMatrix = 'result\\matrix\\{}_{}_dir.dmx'.format(windowGroup.name, skyDensity)

    if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
            or not reuseDaylightMtx:
        sender = os.path.relpath(vreceiver, projectFolder)

        receiver = skyReceiver(
            os.path.join(projectFolder, 'sky\\rfluxSky.rad'), skyDensity
        )

        radFiles = tuple(os.path.relpath(f, projectFolder) for f in drfluxScene)

        ab = int(daylightMtxParameters.ambientBounces)
        src = int(daylightMtxParameters.samplingRaysCount)
        daylightMtxParameters.ambientBounces = 1
        daylightMtxParameters.samplingRaysCount = 1
        dmtx = coeffMatrixCommands(
            dMatrix, os.path.relpath(receiver, projectFolder), radFiles,
            sender, None, None, daylightMtxParameters)
        daylightMtxParameters.ambientBounces = ab
        daylightMtxParameters.samplingRaysCount = src

        commands.append(':: :: [4-2/5] calculating direct daylight matrix')
        commands.append(
            ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [blacked scene]'
            ' ^> [*.dmx]'
        )
        commands.append('::')
        commands.append(dmtx.toRadString())

    return commands, vMatrix, dMatrix


def matrixCalculationThreePhase(
        projectFolder, windowGroup, vMatrix, dMatrix, skyMtxTotal):
    """Three phase matrix calculation.

    Args:
        projectFolder: Full path to project folder.
        windowGroup: A windowGroup.
        vMatrix: Path to view matrix.
        dMatrix: Path to daylight matrix.
        skyMtxTotal: Path to sky matrix.
    Returns:
        commands, resultFiles
    """
    commands = []
    results = []

    for stcount, state in enumerate(windowGroup.states):
        # 4. matrix calculations
        windowGroup.state = stcount
        tMatrix = 'scene\\bsdf\\{}'.format(
            os.path.split(windowGroup.radianceMaterial.xmlfile)[-1])
        output = r'tmp\\{}..{}.tmp'.format(windowGroup.name, state.name)
        dct = matrixCalculation(output, vMatrix, tMatrix, dMatrix, skyMtxTotal)
        commands.append(':: :: State {} [{} out of {}]'
                        .format(state.name, stcount + 1, len(windowGroup.states)))
        commands.append(':: :: [3/3] vMatrix * dMatrix * tMatrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalOutput = r'result\\{}..{}.ill'.format(windowGroup.name, state.name)
        finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
        commands.append(
            ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [results.ill]')
        commands.append('::')
        commands.append('::')
        commands.append(finalmtx.toRadString())

        results.append(os.path.join(projectFolder, finalOutput))

    return commands, results


def matrixCalculationFivePhase(
        projectName, skyDensity, projectFolder, windowGroup, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, vMatrix, dMatrix, dvMatrix,
        ddMatrix, windowGroupCount=0, reuseViewMtx=False, reuseDaylightMtx=False,
        counter=None):
    """Get commands for the five phase recipe.

    This function takes the resultFiles from 3phase calculation and adds direct
    calculation phases to it.
    """
    commands = []
    results = []
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx = skyfiles

    # get black material file
    blkmaterial = [wgsfiles[windowGroupCount].fpblk[0]]
    # add all the blacked window groups but the one in use
    # and finally add non-window group glazing as black
    wgsblacked = \
        [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != windowGroupCount] + \
        list(glzfiles.fpblk)

    for scount, state in enumerate(windowGroup.states):
        # 2.3.Generate daylight coefficients using rfluxmtx
        # collect list of radiance files in the scene for both total and direct
        if counter:
            p = ((counter[0] + scount - 1.0) / counter[1]) * 100
            c = int(p / 10)
            commands.append(
                ':: {} of {} ^|{}{}^| ({:.2f}%%)'.format(
                    counter[0] + scount - 1, counter[1], '#' * c,
                    '-' * (10 - c), float(p)
                )
            )
        commands.append('::')

        # TODO(mostapha): only calculate it if either view materix of daylight matrix
        # is recalculated or t-matrix is new.
        windowGroup.state = scount
        tMatrix = 'scene\\bsdf\\{}'.format(
            os.path.split(windowGroup.radianceMaterial.xmlfile)[-1])
        output = r'tmp\\3phase..{}..{}.tmp'.format(windowGroup.name, state.name)
        dct = matrixCalculation(output, vMatrix, tMatrix, dMatrix, skyMtxTotal)
        commands.append(':: :: [3/5] vMatrix * dMatrix * tMatrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalOutput = r'result\\3phase..{}..{}.ill'.format(windowGroup.name, state.name)
        finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
        commands.append(finalmtx.toRadString())

        results.append(os.path.join(projectFolder, finalOutput))

        commands.append('::')

        # calculate direct matrix with black scene
        output = r'tmp\\direct..{}..{}.tmp'.format(windowGroup.name, state.name)
        dct = matrixCalculation(output, dvMatrix, tMatrix, ddMatrix, skyMtxDirect)
        commands.append(':: :: [4/5] vMatrix * dMatrix * tMatrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalOutput = r'result\\direct..{}..{}.ill'.format(windowGroup.name, state.name)
        finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
        commands.append(finalmtx.toRadString())

        results.append(os.path.join(projectFolder, finalOutput))

        commands.append('::')

        # in case window group is not already provided
        windowGroupfiles = (wgsfiles[windowGroupCount].fp[scount],)

        rfluxSceneBlacked = (
            f for fl in
            (windowGroupfiles, opqfiles.fpblk, extrafiles.fpblk,
             blkmaterial, wgsblacked)
            for f in fl)

        sunMatrix = 'result\\matrix\\sun_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        if not os.path.isfile(os.path.join(projectFolder, sunMatrix)) \
                or not reuseDaylightMtx:

            radFilesBlacked = tuple(os.path.relpath(f, projectFolder)
                                    for f in rfluxSceneBlacked)

            # replace the 4th phase with the new function
            commands.append(':: :: [5/5] black scene analemma daylight matrix')
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
            commands.append(':: :: reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: calculating black daylight mtx * analemma')
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

        commands.append(':: :: calculating final results')
        commands.append(
            ':: :: rmtxop [3phase results.ill] - [direct results.ill] + '
            '[sun results.ill] ^> [final results.ill]'
        )
        commands.append('::')

        fmtx = finalMatrixAddition(
            'result\\3phase..{}..{}.ill'.format(windowGroup.name, state.name),
            'result\\direct..{}..{}.ill'.format(windowGroup.name, state.name),
            'result\\sun..{}..{}.ill'.format(windowGroup.name, state.name),
            'result\\{}..{}.ill'.format(windowGroup.name, state.name)
        )

        commands.append(fmtx.toRadString())
        commands.append(
            ':: end of calculation for {}, {}'.format(windowGroup.name, state.name))
        commands.append('::')
        commands.append('::')

        results.append(
            os.path.join(projectFolder, str(fmtx.outputFile))
        )

    return commands, results
