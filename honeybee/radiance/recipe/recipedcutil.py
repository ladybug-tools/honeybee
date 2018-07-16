"""A collection of useful methods for daylight-coeff recipes."""
from ...futil import preparedir, copy_files_to_folder
from ..command.rfluxmtx import Rfluxmtx
from ..command.dctimestep import Dctimestep
from ..command.rmtxop import Rmtxop, RmtxopMatrix
from ..command.gendaymtx import Gendaymtx
from ..sky.sunmatrix import SunMatrix
from ..sky.analemma import AnalemmaReversed as Analemma
from ..command.oconv import Oconv
from ..command.rpict import Rpict
from ..command.rcontrib import Rcontrib
from ..command.vwrays import Vwrays
from ..parameters.rpict import RpictParameters
from .recipeutil import glz_srf_to_window_group
from .parameters import get_radiance_parameters_grid_based, \
    get_radiance_parameters_image_based

import os
from collections import namedtuple


def write_rad_files_daylight_coeff(working_dir, project_name, opq, glz, wgs):
    """Write files to a target directory for daylight coefficeint method.

    The files will be written under
        working_dir/opaque
        working_dir/glazing
        working_dir/wgroup

    Args:
        working_dir: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        A named tuple for each RadFile as (fp, fpblk)
        fp returns the file path to the list of radiance files.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk'])

    folder = os.path.join(working_dir, 'opaque')
    of = opq.write_geometries(folder, '%s..opq.rad' % project_name, 0, mkdir=True)
    om = opq.write_materials(folder, '%s..opq.mat' % project_name, 0, blacked=False)
    bm = opq.write_materials(folder, '%s..blk.mat' % project_name, 0, blacked=True)
    opqf = Files((om, of), (bm, of))

    folder = os.path.join(working_dir, 'glazing')
    ogf = glz.write_geometries(folder, '%s..glz.rad' % project_name, 0, mkdir=True)
    ogm = glz.write_materials(folder, '%s..glz.mat' % project_name, 0, blacked=False)
    bgm = glz.write_materials(folder, '%s..blk.mat' % project_name, 0, blacked=True)
    glzf = Files((ogm, ogf), (bgm, ogf))

    wgfs = []
    folder = os.path.join(working_dir, 'wgroup')
    bsdfs = []
    bsdffolder = os.path.join(working_dir, 'bsdf')
    preparedir(bsdffolder, remove_content=False)
    # write black material to folder
    for count, wgf in enumerate(wgs):
        # write it as a black geometry
        wg = wgf.hb_surfaces[0]
        name = wg.name
        if count == 0:
            wgbm = wgf.write_black_material(folder, 'black.mat', mkdir=True)

        wgbf = wgf.write_geometries_blacked(folder, '%s..blk.rad' % name, 0)

        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            if hasattr(wg.radiance_material, 'xmlfile'):
                bsdfs.append(wg.radiance_material.xmlfile)

            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)

        wg.state = 0  # set the state back to 0
        wgfs.append(Files(wgfstate, (wgbm, wgbf)))

        copy_files_to_folder(bsdfs, bsdffolder)

    return opqf, glzf, wgfs


def get_commands_sky(project_folder, sky_matrix, reuse=True):
    """Get list of commands to generate the skies.

    1. total sky matrix
    2. direct only sky matrix
    3. sun matrix (aka analemma)

    This methdo genrates sun matrix under project_folder/sky and return the commands
    to generate skies number 1 and 2.

    Returns a namedtuple for (output_files, commands)
    output_files in a namedtuple itself (sky_mtx_total, sky_mtx_direct, analemma,
        sunlist, analemmaMtx).
    """
    OutputFiles = namedtuple('OutputFiles',
                             'sky_mtx_total sky_mtx_direct analemma sunlist analemmaMtx')

    SkyCommands = namedtuple('SkyCommands', 'output_files commands')

    commands = []

    # # 2.1.Create sky matrix.
    sky_matrix.mode = 0
    sky_mtx_total = 'sky/{}.smx'.format(sky_matrix.name)
    sky_matrix.mode = 1
    sky_mtx_direct = 'sky/{}.smx'.format(sky_matrix.name)
    sky_matrix.mode = 0

    # add commands for total and direct sky matrix.
    if hasattr(sky_matrix, 'isSkyMatrix'):
        for m in xrange(2):
            sky_matrix.mode = m
            gdm = skymtx_to_gendaymtx(sky_matrix, project_folder)
            if gdm:
                note = ':: {} sky matrix'.format('direct' if m else 'total')
                commands.extend((note, gdm))
        sky_matrix.mode = 0
    else:
        # sky vector
        raise TypeError('You must use a SkyMatrix to generate the sky.')

    # # 2.2. Create sun matrix
    sm = SunMatrix(sky_matrix.wea, sky_matrix.north, sky_matrix.hoys,
                   sky_matrix.sky_type, suffix=sky_matrix.suffix)

    analemma_mtx = sm.execute(os.path.join(project_folder, 'sky'), reuse=reuse)
    ann = Analemma.from_wea(sky_matrix.wea, sky_matrix.hoys, sky_matrix.north)
    ann.execute(os.path.join(project_folder, 'sky'))
    sunlist = os.path.join('.', 'sky', ann.sunlist_file)
    analemma = os.path.join(project_folder + '/sky', ann.analemma_file)

    of = OutputFiles(sky_mtx_total, sky_mtx_direct, analemma, sunlist, analemma_mtx)

    return SkyCommands(commands, of)


def get_commands_radiation_sky(project_folder, sky_matrix, reuse=True, simplified=False):
    """Get list of commands to generate the skies.

    1. sky matrix diffuse
    3. sun matrix (aka analemma)

    This methdo genrates sun matrix under project_folder/sky and return the commands
    to generate sky number 1.

    Returns a namedtuple for (output_files, commands)
    output_files in a namedtuple itself (sky_mtx_total, sky_mtx_direct, analemma,
        sunlist, analemmaMtx).

    Simplified method will only calculate radiation under patched sky.
    """
    if not simplified:
        OutputFiles = namedtuple('OutputFiles',
                                 'sky_mtxDiff analemma sunlist analemmaMtx')
    else:
        OutputFiles = namedtuple('OutputFiles', 'sky_mtxDiff')

    SkyCommands = namedtuple('SkyCommands', 'output_files commands')

    commands = []

    if not hasattr(sky_matrix, 'isSkyMatrix'):
        # sky vector
        raise TypeError('You must use a SkyMatrix to generate the sky.')

    # # 2.1.Create sky matrix.
    sky_matrix.mode = 2 if not simplified else 0
    sky_mtx_diff = 'sky/{}.smx'.format(sky_matrix.name)
    gdm = skymtx_to_gendaymtx(sky_matrix, project_folder)
    if gdm:
        note = ':: diffuse sky matrix' if not simplified else ':: total sky matrix'
        commands.extend((note, gdm))
    sky_matrix.mode = 0

    if not simplified:
        # # 2.2. Create sun matrix
        sm = SunMatrix(sky_matrix.wea, sky_matrix.north, sky_matrix.hoys,
                       sky_matrix.sky_type, suffix=sky_matrix.suffix)
        analemma_mtx = sm.execute(os.path.join(project_folder, 'sky'), reuse=reuse)
        ann = Analemma.from_wea(sky_matrix.wea, sky_matrix.hoys, sky_matrix.north)
        ann.execute(os.path.join(project_folder, 'sky'))
        sunlist = os.path.join('.', 'sky', ann.sunlist_file)
        analemma = os.path.join(project_folder + '/sky', ann.analemma_file)

        of = OutputFiles(sky_mtx_diff, analemma, sunlist, analemma_mtx)
    else:
        of = OutputFiles(sky_mtx_diff)

    return SkyCommands(commands, of)


# TODO(mostapha): restructure inputs to make the method useful for a normal user.
# It's currently structured to satisfy what we need for the recipes.
def get_commands_scene_daylight_coeff(
        project_name, sky_density, project_folder, skyfiles, inputfiles,
        points_file, total_point_count, rfluxmtx_parameters, reuse_daylight_mtx=False,
        total_count=1, radiation_only=False, transpose=False, simplified=False):
    """Get commands for the static windows in the scene.

    Use get_commands_w_groups_daylight_coeff to get the commands for the rest of the
    scene.

    Args:
        project_name: A string to generate uniqe file names for this project.
        sky_density: Sky density for this study.
        project_folder: Path to project_folder.
        skyfiles: Collection of path to sky files. The order must be (sky_mtx_total,
            sky_mtx_direct, analemma, sunlist, analemmaMtx). You can use get_commands_sky
            function to generate this list.
        inputfiles: Input files for this study. The order must be (opqfiles, glzfiles,
            wgsfiles, extrafiles). Each files object is a namedtuple which includes
            filepath to radiance files under fp and filepath to backed out files under
            fpblk.
        points_file: Path to points_file.
        total_point_count: Number of total points inside points_file.
        rfluxmtx_parameters: An instance of rfluxmtx_parameters for daylight matrix.
        reuse_daylight_mtx: A boolean not to include the commands for daylight matrix
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

    window_group = glz_srf_to_window_group()
    window_groupfiles = glzfiles.fp

    commands, results = _get_commands_daylight_coeff(
        project_name, sky_density, project_folder, window_group, skyfiles,
        inputfiles, points_file, total_point_count, blkmaterial, wgsblacked,
        rfluxmtx_parameters, 0, window_groupfiles, reuse_daylight_mtx, (1, total_count),
        radiation_only=radiation_only, transpose=transpose, simplified=simplified)

    return commands, results


def get_commands_w_groups_daylight_coeff(
        project_name, sky_density, project_folder, window_groups, skyfiles, inputfiles,
        points_file, total_point_count, rfluxmtx_parameters, reuse_daylight_mtx=False,
        total_count=1, radiation_only=False, transpose=False):
    """Get commands for the static windows in the scene.

    Use get_commands_w_groups_daylight_coeff to get the commands for the rest of the
    scene.

    Args:
        project_name: A string to generate uniqe file names for this project.
        sky_density: Sky density for this study.
        project_folder: Path to project_folder.
        window_groups: List of window_groups.
        skyfiles: Collection of path to sky files. The order must be (sky_mtx_total,
            sky_mtx_direct, analemma, sunlist, analemmaMtx). You can use get_commands_sky
            function to generate this list.
        inputfiles: Input files for this study. The order must be (opqfiles, glzfiles,
            wgsfiles, extrafiles). Each files object is a namedtuple which includes
            filepath to radiance files under fp and filepath to backed out files under
            fpblk.
        points_file: Path to points_file.
        total_point_count: Number of total points inside points_file.
        rfluxmtx_parameters: An instance of rfluxmtx_parameters for daylight matrix.
        reuse_daylight_mtx: A boolean not to include the commands for daylight matrix
            calculation if they already exist inside the folder.
    """
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    commands = []
    results = []
    for count, window_group in enumerate(window_groups):
        # get black material file
        blkmaterial = [wgsfiles[count].fpblk[0]]
        # add all the blacked window groups but the one in use
        # and finally add non-window group glazing as black
        wgsblacked = \
            [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != count] + \
            list(glzfiles.fpblk)

        counter = 2 + sum(wg.state_count for wg in window_groups[:count])

        cmds, res = _get_commands_daylight_coeff(
            project_name, sky_density, project_folder, window_group, skyfiles,
            inputfiles, points_file, total_point_count, blkmaterial, wgsblacked,
            rfluxmtx_parameters, count, window_groupfiles=None,
            reuse_daylight_mtx=reuse_daylight_mtx, counter=(counter, total_count),
            radiation_only=radiation_only, transpose=transpose)

        commands.extend(cmds)
        results.extend(res)
    return commands, results


# TODO(): use logging instead of print
def _get_commands_daylight_coeff(
        project_name, sky_density, project_folder, window_group, skyfiles, inputfiles,
        points_file, total_point_count, blkmaterial, wgsblacked, rfluxmtx_parameters,
        window_group_count=0, window_groupfiles=None, reuse_daylight_mtx=False,
        counter=None, radiation_only=False, transpose=False, simplified=False):
    """Get commands for the daylight coefficient recipe.

    This function is used by get_commands_scene_daylight_coeff and
    get_commands_w_groups_daylight_coeff. You usually don't want to use this function
    directly.
    """
    commands = []
    result_files = []
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    if radiation_only:
        if simplified:
            sky_mtxDiff = skyfiles[0]
        else:
            sky_mtxDiff, analemma, sunlist, analemmaMtx = skyfiles
    else:
        sky_mtx_total, sky_mtx_direct, analemma, sunlist, analemmaMtx = skyfiles

    for scount, state in enumerate(window_group.states):
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
                window_group.name, state.name, scount + 1, window_group.state_count
            )
        )
        commands.append('::')

        if scount != 0 or not window_groupfiles:
            # in case window group is not already provided
            window_groupfiles = (wgsfiles[window_group_count].fp[scount],)

        rflux_scene = (
            f for fl in
            (window_groupfiles, opqfiles.fp, extrafiles.fp,
             blkmaterial, wgsblacked)
            for f in fl)

        rflux_scene_blacked = (
            f for fl in
            (window_groupfiles, opqfiles.fpblk, extrafiles.fpblk,
             blkmaterial, wgsblacked)
            for f in fl)

        d_matrix = 'result/matrix/normal_{}..{}..{}.dc'.format(
            project_name, window_group.name, state.name)

        d_matrix_direct = 'result/matrix/black_{}..{}..{}.dc'.format(
            project_name, window_group.name, state.name)

        sun_matrix = 'result/matrix/sun_{}..{}..{}.dc'.format(
            project_name, window_group.name, state.name)

        if not os.path.isfile(os.path.join(project_folder, d_matrix)) \
                or not reuse_daylight_mtx:
            rad_files = tuple(os.path.relpath(f, project_folder) for f in rflux_scene)
            sender = '-'
            receiver = sky_receiver(
                os.path.join(project_folder, 'sky/rfluxSky.rad'), sky_density
            )

            commands.append(':: :: 1. calculating daylight matrices')
            commands.append('::')

            commands.append(':: :: [1/3] scene daylight matrix')
            commands.append(
                ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [scene]'
                ' ^> [dc.mtx]'
            )
            commands.append('::')

            # sampling_rays_count = 1 based on @sariths studies
            rflux = coeff_matrix_commands(
                d_matrix, os.path.relpath(receiver, project_folder), rad_files, sender,
                os.path.relpath(points_file, project_folder), total_point_count,
                rfluxmtx_parameters
            )
            commands.append(rflux.to_rad_string())

            if not simplified:
                rad_files_blacked = tuple(os.path.relpath(f, project_folder)
                                          for f in rflux_scene_blacked)

                commands.append(':: :: [2/3] black scene daylight matrix')
                commands.append(
                    ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] '
                    '[blacked scene] ^> [black dc.mtx]'
                )
                commands.append('::')

                original_value = int(rfluxmtx_parameters.ambient_bounces)
                rfluxmtx_parameters.ambient_bounces = 1
                rflux_direct = coeff_matrix_commands(
                    d_matrix_direct, os.path.relpath(receiver, project_folder),
                    rad_files_blacked, sender,
                    os.path.relpath(points_file, project_folder),
                    total_point_count, rfluxmtx_parameters
                )
                commands.append(rflux_direct.to_rad_string())
                rfluxmtx_parameters.ambient_bounces = original_value

                commands.append(':: :: [3/3] black scene analemma daylight matrix')
                commands.append(
                    ':: :: rcontrib - [sun_matrix] [points] [wgroup] [blacked wgroups] '
                    '[blacked scene] ^> [analemma dc.mtx]'
                )
                commands.append('::')
                sun_commands = sun_coeff_matrix_commands(
                    sun_matrix, os.path.relpath(points_file, project_folder),
                    rad_files_blacked, os.path.relpath(analemma, project_folder),
                    sunlist, rfluxmtx_parameters.irradiance_calc
                )

                commands.extend(cmd.to_rad_string() for cmd in sun_commands)
        else:
            commands.append(':: :: 1. reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: 2. matrix multiplication')
        commands.append('::')
        if simplified:
            rsky_type = 'total'
        else:
            rsky_type = 'diffuse'
        if radiation_only:
            commands.append(':: :: [1/2] calculating daylight mtx * %s sky' % rsky_type)
            commands.append(
                ':: :: dctimestep [dc.mtx] [%s sky] ^> [%s results.rgb]' % (rsky_type,
                                                                            rsky_type))
            dct_total = matrix_calculation(
                'tmp/{}..{}..{}.rgb'.format(rsky_type, window_group.name, state.name),
                d_matrix=d_matrix, sky_matrix=sky_mtxDiff
            )
        else:
            commands.append(':: :: [1/3] calculating daylight mtx * total sky')
            commands.append(
                ':: :: dctimestep [dc.mtx] [total sky] ^> [total results.rgb]')

            dct_total = matrix_calculation(
                'tmp/total..{}..{}.rgb'.format(window_group.name, state.name),
                d_matrix=d_matrix, sky_matrix=sky_mtx_total
            )

        commands.append(dct_total.to_rad_string())

        if radiation_only:
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [%s results.ill]' %
                rsky_type
            )
            finalmtx = rgb_matrix_file_to_ill(
                (dct_total.output_file,),
                'result/{}..{}..{}.ill'.format(rsky_type, window_group.name, state.name),
                transpose
            )
        else:
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [total results.ill]'
            )
            finalmtx = rgb_matrix_file_to_ill(
                (dct_total.output_file,),
                'result/total..{}..{}.ill'.format(window_group.name, state.name),
                transpose
            )

        commands.append('::')
        commands.append(finalmtx.to_rad_string())

        if not radiation_only:
            commands.append(
                ':: :: [2/3] calculating black daylight mtx * direct only sky')
            commands.append(
                ':: :: dctimestep [black dc.mtx] [direct only sky] ^> '
                '[direct results.rgb]')

            dct_direct = matrix_calculation(
                'tmp/direct..{}..{}.rgb'.format(window_group.name, state.name),
                d_matrix=d_matrix_direct, sky_matrix=sky_mtx_direct
            )
            commands.append(dct_direct.to_rad_string())
            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [direct results.rgb] ^> '
                '[direct results.ill]'
            )
            commands.append('::')
            finalmtx = rgb_matrix_file_to_ill(
                (dct_direct.output_file,),
                'result/direct..{}..{}.ill'.format(window_group.name, state.name),
                transpose
            )
            commands.append(finalmtx.to_rad_string())

        if not simplified:
            if not radiation_only:
                commands.append(':: :: [3/3] calculating black daylight mtx * analemma')
            else:
                commands.append(':: :: [2/2] calculating black daylight mtx * analemma')

            commands.append(
                ':: :: dctimestep [black dc.mtx] [analemma only sky] ^> '
                '[sun results.rgb]')
            dct_sun = sun_matrix_calculation(
                'tmp/sun..{}..{}.rgb'.format(window_group.name, state.name),
                dc_matrix=sun_matrix,
                sky_matrix=os.path.relpath(analemmaMtx, project_folder)
            )
            commands.append(dct_sun.to_rad_string())

            commands.append(
                ':: :: rmtxop -c 47.4 119.9 11.6 [sun results.rgb] ^> '
                '[sun results.ill]'
            )
            commands.append('::')
            finalmtx = rgb_matrix_file_to_ill(
                (dct_sun.output_file,),
                'result/sun..{}..{}.ill'.format(window_group.name, state.name),
                transpose
            )
            commands.append(finalmtx.to_rad_string())

            commands.append(':: :: 3. calculating final results')
            if radiation_only:
                commands.append(
                    ':: :: rmtxop [diff results.ill] '
                    '+ [sun results.ill] ^> [final results.ill]'
                )
                commands.append('::')
                fmtx = final_matrix_addition_radiation(
                    'result/diffuse..{}..{}.ill'.format(window_group.name, state.name),
                    'result/sun..{}..{}.ill'.format(window_group.name, state.name),
                    'result/{}..{}.ill'.format(window_group.name, state.name)
                )
                commands.append(fmtx.to_rad_string())
            else:
                commands.append(
                    ':: :: rmtxop [total results.ill] - [direct results.ill] '
                    '+ [sun results.ill] ^> [final results.ill]'
                )
                commands.append('::')
                fmtx = final_matrix_addition(
                    'result/total..{}..{}.ill'.format(window_group.name, state.name),
                    'result/direct..{}..{}.ill'.format(window_group.name, state.name),
                    'result/sun..{}..{}.ill'.format(window_group.name, state.name),
                    'result/{}..{}.ill'.format(window_group.name, state.name)
                )
                commands.append(fmtx.to_rad_string())

        commands.append(
            ':: end of calculation for {}, {}'.format(window_group.name, state.name))
        commands.append('::')
        commands.append('::')

        if not simplified:
            result_files.append(
                os.path.join(project_folder, str(fmtx.output_file))
            )
        else:
            result_files.append(
                os.path.join(project_folder, str(finalmtx.output_file))
            )

    return commands, result_files


def image_based_view_sampling_commands(
        project_folder, view, view_file, vwrays_parameters):
    """Return VWrays command for calculating view coefficient matrix."""
    # calculate view dimensions
    vwr_dim_file = os.path.join(
        project_folder, r'view/{}.dim'.format(view.name))
    x, y = view.get_view_dimension()
    with open(vwr_dim_file, 'wb') as vdfile:
        vdfile.write('-x %d -y %d -ld-\n' % (x, y))

    # calculate sampling for each view
    # the value will be different for each view
    vwrays_parameters.x_resolution = view.x_resolution
    vwrays_parameters.y_resolution = view.y_resolution

    vwr_samp = Vwrays()
    vwr_samp.vwrays_parameters = vwrays_parameters
    vwr_samp.view_file = os.path.relpath(view_file, project_folder)
    vwr_samp.output_file = r'view/{}.rays'.format(view.name)
    vwr_samp.output_data_format = 'f'

    return vwr_dim_file, vwr_samp


def create_reference_map_command(view, view_file, outputfolder, octree_file):
    """Create a reference map to conver illuminance to luminance."""
    # set the parameters / options
    img_par = RpictParameters()
    img_par.ambient_accuracy = 0
    img_par.ambient_value = [0.31831] * 3
    img_par.pixel_sampling = 1
    img_par.pixel_jitter = 1
    x, y = view.get_view_dimension()
    img_par.x_resolution = x
    img_par.y_resolution = y

    rp = Rpict()
    rp.rpict_parameters = img_par
    rp.octree_file = octree_file
    rp.view_file = view_file
    rp.output_file = os.path.join(outputfolder, '{}_map.hdr'.format(view.name))
    return rp


def imaged_based_sun_coeff_matrix_commands(
        output_filename_format, view, view_rays_file, scene_files, analemma, sunlist):
    # output, point_file, scene_files, analemma, sunlist, irradiance_calc

    octree = Oconv()
    octree.scene_files = list(scene_files) + [analemma]
    octree.output_file = 'analemma.oct'

    # Creating sun coefficients
    # -ab 0 -i -ffc -dj 0 -dc 1 -dt 0
    rctb_param = get_radiance_parameters_image_based(0, 1).smtx
    rctb_param.x_dimension, rctb_param.y_dimension = view.get_view_dimension()
    rctb_param.mod_file = sunlist
    rctb_param.output_data_format = 'fc'
    rctb_param.irradiance_calc = None  # -I
    rctb_param.i_irradiance_calc = True  # -i
    rctb_param.output_filename_format = output_filename_format

    rctb = Rcontrib()
    rctb.octree_file = octree.output_file
    rctb.points_file = view_rays_file
    rctb.rcontrib_parameters = rctb_param
    return (octree, rctb)


def image_based_view_coeff_matrix_commands(
        receiver, rad_files, sender, view_info_file, view_file, view_rays_file,
        rfluxmtx_parameters=None):
    """Returns radiance commands to create coefficient matrix.

    Args:
        receiver: A radiance file to indicate the receiver. In view matrix it will be the
        window group and in daylight matrix it will be the sky.
        rad_files: A collection of Radiance files that should be included in the scene.
        sender: A collection of files for senders if senders are radiance geometries
            such as window groups (Default: '-').
        points_file: Path to point file which will be used instead of sender.
        number_of_points: Number of points in points_file as an integer.
        sampling_rays_count: Number of sampling rays (Default: 1000).
        rfluxmtx_parameters: Radiance parameters for Rfluxmtx command using a
            RfluxmtxParameters instance (Default: None).
    """
    rflux = Rfluxmtx()
    rflux.rfluxmtx_parameters = rfluxmtx_parameters
    rflux.rad_files = rad_files
    rflux.sender = sender or '-'
    rflux.receiver_file = receiver
    rflux.output_data_format = 'fc'
    rflux.verbose = True
    rflux.view_info_file = view_info_file
    rflux.view_rays_file = view_rays_file

    return rflux


def coeff_matrix_commands(output_name, receiver, rad_files, sender, points_file=None,
                          number_of_points=None, rfluxmtx_parameters=None):
    """Returns radiance commands to create coefficient matrix.

    Args:
        output_name: Output file name.
        receiver: A radiance file to indicate the receiver. In view matrix it will be the
        window group and in daylight matrix it will be the sky.
        rad_files: A collection of Radiance files that should be included in the scene.
        sender: A collection of files for senders if senders are radiance geometries
            such as window groups (Default: '-').
        points_file: Path to point file which will be used instead of sender.
        number_of_points: Number of points in points_file as an integer.
        rfluxmtx_parameters: Radiance parameters for Rfluxmtx command using a
            RfluxmtxParameters instance (Default: None).
    """
    sender = sender or '-'
    rad_files = rad_files or ()
    number_of_points = number_of_points or 0
    rfluxmtx = Rfluxmtx()

    if sender == '-':
        assert points_file, \
            ValueError('You have to set the points_file when sender is not defined.')

    # -------------- set the parameters ----------------- #
    rfluxmtx.rfluxmtx_parameters = rfluxmtx_parameters

    # -------------- set up the sender objects ---------- #
    # '-' in case of view matrix, window group in case of
    # daylight matrix. This is normally the receiver file
    # in view matrix
    rfluxmtx.sender = sender

    # points file are the senders in view matrix
    rfluxmtx.number_of_points = number_of_points
    rfluxmtx.points_file = points_file

    # --------------- set up the  receiver --------------- #
    # This will be the window for view matrix and the sky for
    # daylight matrix. It makes sense to make a method for each
    # of thme as they are pretty repetitive
    # Klems full basis sampling
    rfluxmtx.receiver_file = receiver

    # ------------- add radiance geometry files ----------------
    # For view matrix it's usually the room itself and the materials
    # in case of each view analysis rest of the windows should be
    # blacked! In case of daylight matrix it will be the context
    # outside the window.
    rfluxmtx.rad_files = rad_files

    # output file address\name
    rfluxmtx.output_matrix = output_name

    return rfluxmtx


def window_group_to_receiver(filepath, upnormal, material_name='vmtx_glow',
                             angle_basis='Kelms Full'):
    """Take a filepath to a window group and create a receiver."""
    hemi_type_mapper = {
        'klemsfull': 'kf', 'klemshalf': 'kh', 'klemsquarter': 'kq'
    }

    assert ''.join(angle_basis.split()).lower() != 'tensortree', \
        'Tensor Tree BSDF ({}) can only be used for in-scene caluclation.' \
        .format(material_name)
    try:
        hemi_type = hemi_type_mapper[''.join(angle_basis.split()).lower()]
    except KeyError:
        raise ValueError('{} is not a valid angle basis.'.format(angle_basis))

    rec_ctrl_par = Rfluxmtx.control_parameters(
        hemi_type=hemi_type, hemi_up_direction=upnormal)

    wg_m = Rfluxmtx.add_control_parameters(filepath, {material_name: rec_ctrl_par})
    return wg_m


def sky_receiver(filepath, density, ground_file_format=None, sky_file_format=None):
    """Create a receiver sky for daylight coefficient studies."""
    if not (ground_file_format and sky_file_format):
        return Rfluxmtx.default_sky_ground(filepath, sky_type='r{}'.format(density))
    else:
        return Rfluxmtx.default_sky_ground(
            filepath, sky_type='r{}'.format(density),
            ground_file_format=ground_file_format,
            sky_file_format=sky_file_format)


def matrix_calculation(output, v_matrix=None, t_matrix=None,
                       d_matrix=None, sky_matrix=None):
    """Get commands for matrix calculation.

    This method sets up a matrix calculations using Dctimestep.
    """
    dct = Dctimestep()
    dct.tmatrix_file = t_matrix
    dct.vmatrix_spec = v_matrix
    dct.dmatrix_file = d_matrix
    dct.sky_vector_file = sky_matrix
    dct.output_file = output
    return dct


def image_based_view_matrix_calculation(view, wg, state, sky_matrix, extention='',
                                        digits=3):
    dct = Dctimestep()
    if os.name == 'nt':
        dct.daylight_coeff_spec = \
            'result/dc/{}/%%0{}d_{}..{}..{}.hdr'.format(
                extention, digits, view.name, wg.name, state.name)
    else:
        dct.daylight_coeff_spec = \
            'result/dc/{}/%0{}d_{}..{}..{}.hdr'.format(
                extention, digits, view.name, wg.name, state.name)

    dct.sky_vector_file = sky_matrix

    # sky matrix is annual
    if os.name == 'nt':
        dct.dctimestep_parameters.output_data_format = \
            ' result/hdr/{}/%%04d_{}..{}..{}.hdr'.format(
                extention, view.name, wg.name, state.name)
    else:
        dct.dctimestep_parameters.output_data_format = \
            ' result/hdr/{}/%04d_{}..{}..{}.hdr'.format(
                extention, view.name, wg.name, state.name)

    return dct


def sun_matrix_calculation(output, dc_matrix=None, sky_matrix=None):
    """Get commands for sun matrix calculation.

    This method sets up a matrix calculations using Dctimestep.
    """
    dct = Dctimestep()
    dct.daylight_coeff_spec = dc_matrix
    dct.sky_vector_file = sky_matrix
    dct.output_file = output
    return dct


def sun_coeff_matrix_commands(output, point_file, scene_files, analemma, sunlist,
                              irradiance_calc):
    """Return commands for calculating analemma coefficient.

    Args:
        output: Output daylight coefficient file (e.g. suncoeff.dc).
        point_file: Path to point / analysis grid file. In case of multiple grid
            put them together in a single file.
        scene_files: A list fo scene files. Usually black scene.
        analemma: Path to analemma file. You can generate analemma file using
            sun_matrix class. Analemma has list of sun positions with their respective
            values.
        sunlist: Path to sunlist. Use sun_matrix to generate sunlist.
        simulation_type:
    Returns:
        octree and rcontrib commands ready to be executed.
    """
    octree = Oconv()
    octree.scene_files = list(scene_files) + [analemma]
    octree.output_file = 'analemma.oct'

    # Creating sun coefficients
    rctb_param = get_radiance_parameters_grid_based(0, 1).smtx
    rctb_param.mod_file = sunlist
    rctb_param.irradiance_calc = irradiance_calc

    rctb = Rcontrib()
    rctb.octree_file = octree.output_file
    rctb.output_file = output
    rctb.points_file = point_file
    rctb.rcontrib_parameters = rctb_param
    return (octree, rctb)


def final_matrix_addition(skymtx, skydirmtx, sunmtx, output):
    """Add final sky, direct sky and sun matrix."""
    # Instantiate matrices for subtraction and addition.
    final_matrix = Rmtxop()

    # std. dc matrix.
    dc_matrix = RmtxopMatrix()
    dc_matrix.matrix_file = skymtx

    # direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dc_direct_matrix = RmtxopMatrix()
    dc_direct_matrix.matrix_file = skydirmtx
    dc_direct_matrix.scalar_factors = [-1]

    # Sun coefficient matrix.
    sun_coeff_matrix = RmtxopMatrix()
    sun_coeff_matrix.matrix_file = sunmtx

    # combine the matrices together. Sequence is extremely important
    final_matrix.rmtxop_matrices = [dc_matrix, dc_direct_matrix, sun_coeff_matrix]
    final_matrix.output_file = output

    return final_matrix


def final_matrix_addition_radiation(skydifmtx, sunmtx, output):
    """Add final diffuse sky and sun matrix."""
    # Instantiate matrices for subtraction and addition.
    final_matrix = Rmtxop()

    # std. dc matrix.
    dc_matrix = RmtxopMatrix()
    dc_matrix.matrix_file = skydifmtx

    # Sun coefficient matrix.
    sun_coeff_matrix = RmtxopMatrix()
    sun_coeff_matrix.matrix_file = sunmtx

    # combine the matrices together. Sequence is extremely important
    final_matrix.rmtxop_matrices = [dc_matrix, sun_coeff_matrix]
    final_matrix.output_file = output

    return final_matrix


def rgb_matrix_file_to_ill(input, output, transpose=False):
    """Convert rgb values in matrix to illuminance values."""
    finalmtx = Rmtxop(matrix_files=input, output_file=output)
    finalmtx.rmtxop_parameters.output_format = 'a'
    finalmtx.rmtxop_parameters.combine_values = (47.4, 119.9, 11.6)
    finalmtx.rmtxop_parameters.transpose_matrix = transpose
    return finalmtx


def skymtx_to_gendaymtx(sky_matrix, target_folder):
    """Return gendaymtx command based on input sky_matrix."""
    wea_filepath = 'sky/{}.wea'.format(sky_matrix.name)
    sky_mtx = 'sky/{}.smx'.format(sky_matrix.name)
    hours_file = os.path.join(target_folder, 'sky/{}.hrs'.format(sky_matrix.name))

    if not os.path.isfile(os.path.join(target_folder, sky_mtx)) \
            or not os.path.isfile(os.path.join(target_folder, wea_filepath)) \
            or not sky_matrix.hours_match(hours_file):
        # write wea file to folder
        sky_matrix.write_wea(os.path.join(target_folder, 'sky'), write_hours=True)
        gdm = Gendaymtx(output_name=sky_mtx, wea_file=wea_filepath)
        gdm.gendaymtx_parameters = sky_matrix.sky_matrix_parameters
        return gdm.to_rad_string()
