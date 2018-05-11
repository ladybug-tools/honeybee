"""A collection of useful methods for recipes."""
from ..command.xform import Xform, XformParameters
from ..material.plastic import BlackMaterial
from ..radfile import RadFile
from ...futil import write_to_file_by_name, copy_files_to_folder, preparedir

import os
from collections import Counter, namedtuple


def input_srfs_to_rad_files(in_srfs):
    """separate input honeybee surfaces to RadFiles based on type.

    This function analyzes a collection of input honeybee surfaces and returns
    3 rad_file like objecs for opaque, glazing and tuple(window groups).
    """
    opaque = []
    fen = []
    wgs = []

    for srf in in_srfs:
        if srf.isHBDynamicSurface:
            # window groups, multiple of single state
            wgs.append(srf)
        elif srf.isHBFenSurface or not srf.radiance_material.is_opaque:
            # generic window surfaces
            fen.append(srf)
        elif srf.isHBSurface:
            opaque.append(srf)
            fen.extend(srf.children_surfaces)
        else:
            raise TypeError('{} is not an analysis surface.'.format(srf))

    # make sure there is no duplicat name in window groups
    dup = tuple(k for k, v in Counter((wg.name for wg in wgs)).items() if v > 1)
    assert len(dup) == 0, \
        ValueError('Found duplicate window-group names: {}\n'
                   'Each window-group must have a uniqe name.'.format(dup))

    print('Found %d opaque surfaces.' % len(opaque))
    print('Found %d fenestration surfaces.' % len(fen))
    print('Found %d window-groups.' % len(wgs))

    for count, wg in enumerate(wgs):
        if len(wg.states) == 1:
            print('  [%d] %s, 1 state.' % (count, wg.name))
        else:
            print('  [%d] %s, %d states.' % (count, wg.name, len(wg.states)))

    return RadFile(opaque), RadFile(fen), tuple(RadFile((wg,)) for wg in wgs)


def glz_srf_to_window_group():
    """Create a named tuple that looks like window groups for glazing surfaces.

    This is neccessary to work with normal glazing just like window groups.
    """
    State = namedtuple('State', 'name')
    WindowGroup = namedtuple('WindowGroup', 'name states state_count')

    state = State('default')
    wg = WindowGroup('scene', (state,), 1)

    return wg


def write_extra_files(rad_scene, target_dir, add_blacked=False):
    """Copy additionl files from rad_scenes to working_dir.

    Args:
        rad_scene: A RadScene object.
        target_dir: Target study folder. The files will be copied under extra.
        add_blacked: Set to True to add the blacked radiance file to the same folder.
            The file will be named *_blacked.rad.

        A named tuple for each RadFile as (fp, fpblk)
        fp returns the file path to the list of original radiance files.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk'])
    if not rad_scene:
        return Files([], [])

    if rad_scene.file_count == 1:
        print('One file from the radiance scene is added to the analysis.')
    else:
        print('%d files from the radiance scene are added to the analysis.' %
              rad_scene.file_count)

    target_dir = os.path.join(target_dir, 'extra')
    if rad_scene.copy_local:
        preparedir(target_dir, rad_scene.overwrite)
        scene_mat_files = copy_files_to_folder(
            rad_scene.files.mat, target_dir, rad_scene.overwrite)
        scene_rad_files = copy_files_to_folder(
            rad_scene.files.rad, target_dir, rad_scene.overwrite)
        scene_oct_files = copy_files_to_folder(
            rad_scene.files.oct, target_dir, rad_scene.overwrite)
    else:
        scene_mat_files = rad_scene.files.mat
        scene_rad_files = rad_scene.files.rad
        scene_oct_files = rad_scene.files.oct

    rad_files = scene_mat_files, scene_rad_files, scene_oct_files

    # use xform to generate the blacked version
    blacked = []
    if add_blacked:
        black_mat = RadFile.header() + '\n\n' + BlackMaterial().to_rad_string()
        xfr_para = XformParameters()
        xfr_para.mod_replace = BlackMaterial().name

        # Note: Xform has this thing it only works well if the paths are absolute.
        for f in scene_rad_files:
            # copy black material file if doesn't exist and add it to blacked
            folder, name = os.path.split(f)
            materialfile = os.path.join(folder, 'black.mat')
            if not os.path.exists(materialfile):
                write_to_file_by_name(folder, 'black.mat', black_mat)
                blacked.append(materialfile)
            # create blacked rad scene
            xfr = Xform()
            xfr.xform_parameters = xfr_para
            xfr.rad_file = f
            xfr.output_file = f[:-4] + '_blacked' + f[-4:]
            xfr.execute()
            blacked.append(xfr.output_file)

    return Files([f for fl in rad_files for f in fl], blacked)


def write_rad_files(scene_folder, project_name, opq, glz, wgs):
    """Write files to a target directory.

    This method should only be used for daylight coefficeint and multi-phase
    daylight simulations. The files will be written under
        scene_folder/opaque
        scene_folder/glazing
        scene_folder/wgroup
    If any of the surfaces has BSDF material the xml file will be copied under
    scene_folder/*/bsdf and the path to the material will be modified to the new
    path.

    Args:
        scene_folder: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        Return 3 list for radiance files for opaque, glz and window groups.
        The list for windowgroups will be a list of lists for each window group
        and its states.
    """
    folder = os.path.join(scene_folder, 'opaque')
    of = opq.write_geometries(folder, '%s..opq.rad' % project_name, 0, mkdir=True)
    om = opq.write_materials(folder, '%s..opq.mat' % project_name, 0, blacked=False)
    opqf = [om, of]

    folder = os.path.join(scene_folder, 'glazing')
    ogf = glz.write_geometries(folder, '%s..glz.rad' % project_name, 0, mkdir=True)
    ogm = glz.write_materials(folder, '%s..glz.mat' % project_name, 0, blacked=False)
    glzf = [ogm, ogf]

    wgfs = []
    folder = os.path.join(scene_folder, 'wgroup')

    for count, wgf in enumerate(wgs):
        wg = wgf.hb_surfaces[0]
        name = wg.name
        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)

        wgfs.append(wgfstate)

    return opqf, glzf, wgfs
