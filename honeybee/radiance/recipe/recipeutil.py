"""A collection of useful methods for recipes."""
from ..command.rfluxmtx import Rfluxmtx
from ..command.dctimestep import Dctimestep
from ..command.rmtxop import Rmtxop, RmtxopMatrix
from ..command.gendaymtx import Gendaymtx
from ..sky.sunmatrix import SunMatrix
from ..command.oconv import Oconv
from ..command.rcontrib import Rcontrib, RcontribParameters
from ..command.xform import Xform, XformParameters
from ..command.vwrays import Vwrays, VwraysParameters
from ..material.plastic import BlackMaterial
from ..radfile import RadFile
from ...futil import writeToFileByName, copyFilesToFolder, preparedir

import os
from collections import Counter, namedtuple


def glzSrfTowinGroup():
    """Create a named tuple that looks like window groups for glazing surfaces.

    This is neccessary to work with normal glazing just like window groups.
    """
    State = namedtuple('State', 'name')
    WindowGroup = namedtuple('WindowGroup', 'name states stateCount')

    state = State('default')
    wg = WindowGroup('scene', (state,), 1)

    return wg


def viewSamplingCommands(projectFolder, view, viewFile, vwraysParameters=None):
    """Return VWrays command for calculating view coefficient matrix."""
    # calculate view dimensions
    vwrDimFile = os.path.join(
        projectFolder, r'view\\{}.dimensions'.format(view.name))
    x, y = view.getViewDimension()
    with open(vwrDimFile, 'wb') as vdfile:
        vdfile.write('-x %d -y %d -ld-\n' % (x, y))

    # calculate sampling for each view
    if not vwraysParameters:
        vwrParaSamp = VwraysParameters()
        vwrParaSamp.xResolution = view.xRes
        vwrParaSamp.yResolution = view.yRes
        vwrParaSamp.samplingRaysCount = 6  # 9
        vwrParaSamp.jitter = 0.7
    else:
        vwrParaSamp = vwraysParameters

    vwrSamp = Vwrays()
    vwrSamp.vwraysParameters = vwrParaSamp
    vwrSamp.viewFile = os.path.relpath(viewFile, projectFolder)
    vwrSamp.outputFile = r'view\\{}.rays'.format(view.name)
    vwrSamp.outputDataFormat = 'f'

    return vwrDimFile, vwrSamp


def viewCoeffMatrixCommands(
        outputName, receiver, radFiles, sender, viewInfoFile, viewFile, viewRaysFile,
        samplingRaysCount=None, rfluxmtxParameters=None):
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
    if samplingRaysCount:
        rflux.samplingRaysCount = samplingRaysCount  # 9

    return rflux


def coeffMatrixCommands(outputName, receiver, radFiles, sender, pointsFile=None,
                        numberOfPoints=None, samplingRaysCount=None,
                        rfluxmtxParameters=None):
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
        samplingRaysCount: Number of sampling rays (Default: 1000).
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
    # ray counts
    if samplingRaysCount:
        rfluxmtx.samplingRaysCount = samplingRaysCount

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


def viewMatrixCalculation(output, view, wg, state, skyMatrix, extention=''):
    ext = extention
    dct = Dctimestep()
    if os.name == 'nt':
        dct.daylightCoeffSpec = \
            'result\\matrix\\{}_{}_{}_%%03d.hdr'.format(
                view.name, wg.name, state.name + '_' + ext if ext else state.name)
    else:
        dct.daylightCoeffSpec = \
            'result\\matrix\\{}_{}_{}_%03d.hdr'.format(
                view.name, wg.name, state.name + '_' + ext if ext else state.name)

    dct.skyVectorFile = skyMatrix

    # sky matrix is annual
    if os.name == 'nt':
        dct.dctimestepParameters.outputDataFormat = \
            ' result\\{}_{}_{}_%%04d.hdr'.format(
                view.name, wg.name, state.name + '_' + ext if ext else state.name)
    else:
        dct.dctimestepParameters.outputDataFormat = \
            ' result\\{}_{}_{}_%04d.hdr'.format(
                view.name, wg.name, state.name + '_' + ext if ext else state.name)

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


def sunCoeffMatrixCommands(output, pointFile, sceneFiles, analemma, sunlist):
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

    Returns:
        octree and rcontrib commands ready to be executed.
    """
    octree = Oconv()
    octree.sceneFiles = list(sceneFiles) + [analemma]
    octree.outputFile = 'analemma.oct'

    # Creating sun coefficients
    rctbParam = RcontribParameters()
    rctbParam.ambientBounces = 0
    rctbParam.directJitter = 0
    rctbParam.directCertainty = 1
    rctbParam.directThreshold = 0
    rctbParam.modFile = sunlist
    rctbParam.irradianceCalc = True

    rctb = Rcontrib()
    rctb.octreeFile = octree.outputFile
    rctb.outputFile = output
    rctb.pointsFile = pointFile
    rctb.rcontribParameters = rctbParam

    return (octree, rctb)


def viewSunCoeffMatrixCommands(output, view):
    # raise NotImplementedError()
    return ''


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


def inputSrfsToRadFiles(inSrfs):
    """separate input honeybee surfaces to RadFiles based on type.

    This function analyzes a collection of input honeybee surfaces and returns
    3 radFile like objecs for opaque, glazing and tuple(window groups).
    """
    opaque = []
    fen = []
    wgs = []

    for srf in inSrfs:
        if srf.isHBDynamicSurface:
            # window groups, multiple of single state
            wgs.append(srf)
        elif srf.isHBFenSurface or srf.radianceMaterial.isGlassMaterial:
            # generic window surfaces
            fen.append(srf)
        elif srf.isHBSurface:
            opaque.append(srf)
            fen.extend(srf.childrenSurfaces)
        else:
            raise TypeError('{} is not an analysis surface.'.format(srf))

    # make sure there is no duplicat name in window groups
    dup = tuple(k for k, v in Counter((wg.name for wg in wgs)).items() if v > 1)
    assert len(dup) == 0, \
        ValueError('Found duplicate window-group names: {}\n'
                   'Each window-group must have a uniqe name.'.format(dup))

    print 'Found %d opaque surfaces.' % len(opaque)
    print 'Found %d fenestration surfaces.' % len(fen)
    print 'Found %d window-groups.' % len(wgs)

    for count, wg in enumerate(wgs):
        if len(wg.states) == 1:
            print '  [%d] %s, 1 state.' % (count, wg.name)
        else:
            print '  [%d] %s, %d states.' % (count, wg.name, len(wg.states))

    return RadFile(opaque), RadFile(fen), tuple(RadFile((wg,)) for wg in wgs)


def writeExtraFiles(radScene, targetDir, addBlacked=False):
    """Copy additionl files from radScenes to workingDir.

    Args:
        radScene: A RadScene object.
        targetDir: Target study folder. The files will be copied under extra.
        addBlacked: Set to True to add the blacked radiance file to the same folder.
            The file will be named *_blacked.rad.

        A named tuple for each RadFile as (fp, fpblk)
        fp returns the file path to the list of original radiance files.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk'])
    if not radScene:
        return Files([], [])

    if radScene.fileCount == 1:
        print 'One file from the radiance scene is added to the analysis.'
    else:
        print '%d files from the radiance scene are added to the analysis.' % \
            radScene.fileCount

    targetDir = os.path.join(targetDir, 'extra')
    if radScene.copyLocal:
        preparedir(targetDir, radScene.overwrite)
        sceneMatFiles = copyFilesToFolder(
            radScene.files.mat, targetDir, radScene.overwrite)
        sceneRadFiles = copyFilesToFolder(
            radScene.files.rad, targetDir, radScene.overwrite)
        sceneOctFiles = copyFilesToFolder(
            radScene.files.oct, targetDir, radScene.overwrite)
    else:
        sceneMatFiles = radScene.files.mat
        sceneRadFiles = radScene.files.rad
        sceneOctFiles = radScene.files.oct

    radFiles = sceneMatFiles, sceneRadFiles, sceneOctFiles

    # use xform to generate the blacked version
    blacked = []
    if addBlacked:
        blackMat = RadFile.header() + '\n\n' + BlackMaterial().toRadString()
        xfrPara = XformParameters()
        xfrPara.modReplace = BlackMaterial().name

        # Note: Xform has this thing it only works well if the paths are absolute.
        for f in sceneRadFiles:
            # copy black material file if doesn't exist and add it to blacked
            folder, name = os.path.split(f)
            materialfile = os.path.join(folder, 'black.mat')
            if not os.path.exists(materialfile):
                writeToFileByName(folder, 'black.mat', blackMat)
                blacked.append(materialfile)
            # create blacked rad scene
            xfr = Xform()
            xfr.xformParameters = xfrPara
            xfr.radFile = f
            xfr.outputFile = f[:-4] + '_blacked' + f[-4:]
            xfr.execute()
            blacked.append(xfr.outputFile)

    return Files([f for fl in radFiles for f in fl], blacked)


def writeRadFiles(sceneFolder, projectName, opq, glz, wgs):
    """Write files to a target directory.

    This method should only be used for daylight coefficeint and multi-phase
    daylight simulations. The files will be written under
        sceneFolder/opaque
        sceneFolder/glazing
        sceneFolder/wgroup
    If any of the surfaces has BSDF material the xml file will be copied under
    sceneFolder/*/bsdf and the path to the material will be modified to the new
    path.

    Args:
        sceneFolder: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        Return 3 list for radiance files for opaque, glz and window groups.
        The list for windowgroups will be a list of lists for each window group
        and its states.
    """
    folder = os.path.join(sceneFolder, 'opaque')
    of = opq.writeGeometries(folder, '%s..opq.rad' % projectName, 0, mkdir=True)
    om = opq.writeMaterials(folder, '%s..opq.mat' % projectName, 0, blacked=False)
    opqf = [om, of]

    folder = os.path.join(sceneFolder, 'glazing')
    ogf = glz.writeGeometries(folder, '%s..glz.rad' % projectName, 0, mkdir=True)
    ogm = glz.writeMaterials(folder, '%s..glz.mat' % projectName, 0, blacked=False)
    glzf = [ogm, ogf]

    wgfs = []
    folder = os.path.join(sceneFolder, 'wgroup')

    for count, wgf in enumerate(wgs):
        wg = wgf.hbSurfaces[0]
        name = wg.name
        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)

        wgfs.append(wgfstate)

    return opqf, glzf, wgfs


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
    sm = SunMatrix(skyMatrix.wea, skyMatrix.north, skyMatrix.hoys, skyMatrix.skyType)
    analemma, sunlist, analemmaMtx = \
        sm.execute(os.path.join(projectFolder, 'sky'), reuse=reuse)

    of = OutputFiles(skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx)

    return SkyCommands(commands, of)


# TODO(mostapha): restructure inputs to make the method useful for a normal user.
# It's currently structured to satisfy what we need for the recipes.
def getCommandsSceneDaylightCoeff(
        projectName, skyDensity, projectFolder, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, reuseDaylightMtx=False,
        totalCount=1):
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
        rfluxmtxParameters, 0, windowGroupfiles, reuseDaylightMtx, (1, totalCount))

    return commands, results


def getCommandsWGroupsDaylightCoeff(
        projectName, skyDensity, projectFolder, windowGroups, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, reuseDaylightMtx=False,
        totalCount=1):
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
            reuseDaylightMtx=reuseDaylightMtx, counter=(counter, totalCount))

        commands.extend(cmds)
        results.extend(res)
    return commands, results


# TODO(): use logging instead of print
def _getCommandsDaylightCoeff(
        projectName, skyDensity, projectFolder, windowGroup, skyfiles, inputfiles,
        pointsFile, totalPointCount, blkmaterial, wgsblacked, rfluxmtxParameters,
        windowGroupCount=0, windowGroupfiles=None, reuseDaylightMtx=False, counter=None):
    """Get commands for the daylight coefficient recipe.

    This function is used by getCommandsSceneDaylightCoeff and
    getCommandsWGroupsDaylightCoeff. You usually don't want to use this function
    directly.
    """
    commands = []
    resultFiles = []
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    skyMtxTotal, skyMtxDirect, analemma, sunlist, analemmaMtx = skyfiles

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
        commands.append(
            ':: start of calculation for {}, {}. Number of states: #{}'.format(
                windowGroup.name, state.name, windowGroup.stateCount
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
            rfluxmtxParameters.ambientBounces = 5
            rflux = coeffMatrixCommands(
                dMatrix, os.path.relpath(receiver, projectFolder), radFiles, sender,
                os.path.relpath(pointsFile, projectFolder), totalPointCount,
                1, rfluxmtxParameters
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

            rfluxmtxParameters.ambientBounces = 1
            rfluxDirect = coeffMatrixCommands(
                dMatrixDirect, os.path.relpath(receiver, projectFolder),
                radFilesBlacked, sender, os.path.relpath(pointsFile, projectFolder),
                totalPointCount, None, rfluxmtxParameters
            )
            commands.append(rfluxDirect.toRadString())

            commands.append(':: :: [3/3] black scene analemma daylight matrix')
            commands.append(
                ':: :: rcontrib - [sunMatrix] [points] [wgroup] [blacked wgroups] '
                '[blacked scene] ^> [analemma dc.mtx]'
            )
            commands.append('::')
            sunCommands = sunCoeffMatrixCommands(
                sunMatrix, os.path.relpath(pointsFile, projectFolder),
                radFilesBlacked, os.path.relpath(analemma, projectFolder),
                os.path.relpath(sunlist, projectFolder)
            )

            commands.extend(cmd.toRadString() for cmd in sunCommands)
        else:
            commands.append(':: :: 1. reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: 2. matrix multiplication')
        commands.append('::')
        commands.append(':: :: [1/3] calculating daylight mtx * total sky')
        commands.append(':: :: dctimestep [dc.mtx] [total sky] ^> [total results.rgb]')
        dctTotal = matrixCalculation(
            'tmp\\total..{}..{}.rgb'.format(windowGroup.name, state.name),
            dMatrix=dMatrix, skyMatrix=skyMtxTotal
        )
        commands.append(dctTotal.toRadString())

        commands.append(
            ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [total results.ill]'
        )
        finalmtx = RGBMatrixFileToIll(
            (dctTotal.outputFile,),
            'result\\total..{}..{}.ill'.format(windowGroup.name, state.name)
        )
        commands.append('::')
        commands.append(finalmtx.toRadString())

        commands.append(':: :: [2/3] calculating black daylight mtx * direct only sky')
        commands.append(
            ':: :: dctimestep [black dc.mtx] [direct only sky] ^> [direct results.rgb]')

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

        commands.append(':: :: [3/3] calculating black daylight mtx * analemma')
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
        commands.append(
            ':: :: rmtxop [total results.ill] - [direct results.ill] + [sun results.ill]'
            ' ^> [final results.ill]'
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
        commands.append('::')

        resultFiles.append(
            os.path.join(projectFolder, str(fmtx.outputFile))
        )

    return commands, resultFiles


def getCommandsViewDaylightMatrices(
    projectFolder, windowGroup, count, inputfiles, pointsFile,
    numberOfPoints, skyDensity, viewMtxParameters, daylightMtxParameters,
        reuseViewMtx=False, reuseDaylightMtx=False):
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
        ':: calculation for the window group {}'.format(windowGroup.name)
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
        commands.append(':: :: 1. view matrix calculation')
        # prepare input files
        radFiles = tuple(os.path.relpath(f, projectFolder) for f in vrfluxScene)

        vmtx = coeffMatrixCommands(
            vMatrix, os.path.relpath(vreceiver, projectFolder), radFiles, '-',
            os.path.relpath(pointsFile, projectFolder), numberOfPoints,
            None, viewMtxParameters)

        commands.append(vmtx.toRadString())

    # 3.3 daylight matrix
    dMatrix = 'result\\matrix\\{}_{}.dmx'.format(windowGroup.name, skyDensity)

    if not os.path.isfile(os.path.join(projectFolder, dMatrix)) \
            or not reuseDaylightMtx:
        sender = os.path.relpath(vreceiver, projectFolder)

        receiver = skyReceiver(
            os.path.join(projectFolder, 'sky\\rfluxSky.rad'), skyDensity
        )

        samplingRaysCount = 1000
        radFiles = tuple(os.path.relpath(f, projectFolder) for f in drfluxScene)

        dmtx = coeffMatrixCommands(
            dMatrix, os.path.relpath(receiver, projectFolder), radFiles,
            sender, None, None, samplingRaysCount, daylightMtxParameters)

        commands.append(':: :: 2. daylight matrix calculation')
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

        commands.append(
            ':: :: 3.1.{} final matrix calculation for {}'.format(stcount,
                                                                  state.name))
        commands.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalOutput = r'result\\{}..{}.ill'.format(windowGroup.name, state.name)
        finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
        commands.append(
            ':: :: 3.2.{} convert RGB values to illuminance for {}'.format(
                stcount, state.name)
        )
        commands.append(finalmtx.toRadString())

        results.append(os.path.join(projectFolder, finalOutput))

    return commands, results


def matrixCalculationFivePhase(
        projectName, skyDensity, projectFolder, windowGroup, skyfiles, inputfiles,
        pointsFile, totalPointCount, rfluxmtxParameters, vMatrix, dMatrix,
        windowGroupCount=0, reuseViewMtx=False, reuseDaylightMtx=False,
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

        commands.append(
            ':: :: 3.1.{} final matrix calculation for {}'.format(scount,
                                                                  state.name))
        commands.append(dct.toRadString())

        # 5. convert r, g ,b values to illuminance
        finalOutput = r'result\\3phase..{}..{}.ill'.format(windowGroup.name, state.name)
        finalmtx = RGBMatrixFileToIll((dct.outputFile,), finalOutput)
        commands.append(
            ':: :: 3.2.{} convert RGB values to illuminance for {}'.format(
                scount, state.name)
        )
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

        dMatrixDirect = 'result\\matrix\\black_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        sunMatrix = 'result\\matrix\\sun_{}..{}..{}.dc'.format(
            projectName, windowGroup.name, state.name)

        if not os.path.isfile(os.path.join(projectFolder, dMatrixDirect)) \
                or not reuseDaylightMtx:
            sender = '-'
            receiver = skyReceiver(
                os.path.join(projectFolder, 'sky\\rfluxSky.rad'), skyDensity
            )

            radFilesBlacked = tuple(os.path.relpath(f, projectFolder)
                                    for f in rfluxSceneBlacked)

            commands.append(':: :: [4/5] black scene daylight matrix')
            commands.append(
                ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] '
                '[blacked scene] ^> [black dc.mtx]'
            )
            commands.append('::')

            rfluxmtxParameters.ambientBounces = 1
            rfluxDirect = coeffMatrixCommands(
                dMatrixDirect, os.path.relpath(receiver, projectFolder),
                radFilesBlacked, sender, os.path.relpath(pointsFile, projectFolder),
                totalPointCount, None, rfluxmtxParameters
            )
            commands.append(rfluxDirect.toRadString())

            commands.append(':: :: [5/5] black scene analemma daylight matrix')
            commands.append(
                ':: :: rcontrib - [sunMatrix] [points] [wgroup] [blacked wgroups] '
                '[blacked scene] ^> [analemma dc.mtx]'
            )
            commands.append('::')
            sunCommands = sunCoeffMatrixCommands(
                sunMatrix, os.path.relpath(pointsFile, projectFolder),
                radFilesBlacked, os.path.relpath(analemma, projectFolder),
                os.path.relpath(sunlist, projectFolder)
            )

            commands.extend(cmd.toRadString() for cmd in sunCommands)
        else:
            commands.append(':: :: 1. reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: 2. matrix multiplication')
        commands.append('::')

        commands.append(':: :: [2/3] calculating black daylight mtx * direct only sky')
        commands.append(
            ':: :: dctimestep [black dc.mtx] [direct only sky] ^> [direct results.rgb]')

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

        commands.append(':: :: [3/3] calculating black daylight mtx * analemma')
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
        commands.append(
            ':: :: rmtxop [total results.ill] - [direct results.ill] + [sun results.ill]'
            ' ^> [final results.ill]'
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
        commands.append('::')

        results.append(
            os.path.join(projectFolder, str(fmtx.outputFile))
        )

    return commands, results
