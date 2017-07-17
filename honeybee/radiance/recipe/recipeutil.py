"""A collection of useful methods for recipes."""
from ..command.xform import Xform, XformParameters
from ..material.plastic import BlackMaterial
from ..radfile import RadFile
from ...futil import writeToFileByName, copyFilesToFolder, preparedir

import os
from collections import Counter, namedtuple


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


def glzSrfTowinGroup():
    """Create a named tuple that looks like window groups for glazing surfaces.

    This is neccessary to work with normal glazing just like window groups.
    """
    State = namedtuple('State', 'name')
    WindowGroup = namedtuple('WindowGroup', 'name states stateCount')

    state = State('default')
    wg = WindowGroup('scene', (state,), 1)

    return wg


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
