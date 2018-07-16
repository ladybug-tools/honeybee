"""A collection of useful methods for multi-phase recipes."""

from .recipedcutil import window_group_to_receiver, coeff_matrix_commands, sky_receiver
from .recipedcutil import matrix_calculation, rgb_matrix_file_to_ill, \
    sun_coeff_matrix_commands
from .recipedcutil import sun_matrix_calculation, final_matrix_addition
from ...futil import preparedir, copy_files_to_folder

import os
from collections import namedtuple


def write_rad_files_multi_phase(working_dir, project_name, opq, glz, wgs):
    """Write files to a target directory for multi-phase method.

    This method should only be used for daylight coefficeint and multi-phase
    daylight simulations. The files will be written under
        working_dir/opaque
        working_dir/glazing
        working_dir/wgroup

    Args:
        working_dir: Path to working directory.
        opq: A RadFile for opaque surfaces.
        glz: A RadFile for glazing surfaces.
        wgs: A collection of RadFiles for window-groups.

    Returns:
        A named tuple for each RadFile as (fp, fpblk, fpglw)
        fp returns the file path to the list of radiance files. It will be glowed
            files for window_groups.
        fpblk returns the file path to the list of blacked radiance files.
    """
    Files = namedtuple('Files', ['fp', 'fpblk', 'fpglw'])

    folder = os.path.join(working_dir, 'opaque')
    of = opq.write_geometries(folder, '%s..opq.rad' % project_name, 0, mkdir=True)
    om = opq.write_materials(folder, '%s..opq.mat' % project_name, 0, blacked=False)
    bm = opq.write_materials(folder, '%s..blk.mat' % project_name, 0, blacked=True)
    opqf = Files((om, of), (bm, of), ())

    folder = os.path.join(working_dir, 'glazing')
    ogf = glz.write_geometries(folder, '%s..glz.rad' % project_name, 0, mkdir=True)
    ogm = glz.write_materials(folder, '%s..glz.mat' % project_name, 0, blacked=False)
    bgm = glz.write_materials(folder, '%s..blk.mat' % project_name, 0, blacked=True)
    glzf = Files((ogm, ogf), (bgm, ogf), ())

    wgfs = []
    folder = os.path.join(working_dir, 'wgroup')
    bsdfs = []
    bsdffolder = os.path.join(working_dir, 'bsdf')
    preparedir(bsdffolder)
    # write black material to folder
    for count, wgf in enumerate(wgs):
        # write it as a black geometry
        wg = wgf.hb_surfaces[0]
        name = wg.name
        if count == 0:
            wgbm = wgf.write_black_material(folder, 'black.mat', mkdir=True)

        wgbf = wgf.write_geometries_blacked(folder, '%s..blk.rad' % name, 0)
        wggf = wgf.write(folder, '%s..glw.rad' % name, 0, flipped=True,
                         glowed=True, mkdir=True)
        recf = window_group_to_receiver(wggf, wg.upnormal, wg.radiance_material.name,
                                        wg.radiance_material.angle_basis)
        # remove the original window group and rename the new one to original
        os.remove(wggf)
        os.rename(recf, wggf)

        # copy xml files for each state to bsdf folder
        # raise TypeError if material is not BSDF
        # write files for each state
        wgfstate = []
        for scount, state in enumerate(wg.states):
            wg.state = scount
            assert hasattr(wg.radiance_material, 'xmlfile'), \
                ValueError(
                    'RadianceMaterial for all the states should be BSDF material.'
                    ' Radiance Material for {} state is {}.'.format(
                        state.name, type(wg.radiance_material)))
            bsdfs.append(wg.radiance_material.xmlfile)
            # write the file for each state. only useful for 5-phase
            wgfst = wgf.write(folder, '%s..%s.rad' % (name, state.name), 0)
            wgfstate.append(wgfst)

        wg.state = 0  # set the state back to 0
        wgfs.append(Files(wgfstate, (wgbm, wgbf), (wggf,)))

        copy_files_to_folder(bsdfs, bsdffolder)

    return opqf, glzf, wgfs


def get_commands_view_daylight_matrices(
    project_folder, window_group, count, inputfiles, points_file,
    number_of_points, sky_density, view_mtx_parameters, daylight_mtx_parameters,
        reuse_view_mtx=False, reuse_daylight_mtx=False, phases_count=3):
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
            window_group.name)
    )

    vreceiver = wgsfiles[count].fpglw[0]

    vrflux_scene = (
        f for fl in
        (opqfiles.fp, blkmaterial, wgsblacked)
        for f in fl)

    drflux_scene = (
        f for fl in
        (opqfiles.fp, extrafiles.fp, blkmaterial, wgsblacked)
        for f in fl)

    # 3.2.Generate view matrix
    v_matrix = 'result/matrix/{}.vmx'.format(window_group.name)
    if not os.path.isfile(os.path.join(project_folder, v_matrix)) \
            or not reuse_view_mtx:
        commands.append(':: :: [1/{}] calculating view matrix'.format(phases_count))
        commands.append(
            ':: :: rfluxmtx - [wgroup] [scene] [points] [blacked wgroups]'
            ' ^> [*.vmx]'
        )
        commands.append('::')
        # prepare input files
        rad_files = tuple(os.path.relpath(f, project_folder) for f in vrflux_scene)

        vmtx = coeff_matrix_commands(
            v_matrix, os.path.relpath(vreceiver, project_folder), rad_files, '-',
            os.path.relpath(points_file, project_folder), number_of_points,
            view_mtx_parameters)

        commands.append(vmtx.to_rad_string())

    # 3.3 daylight matrix
    d_matrix = 'result/matrix/{}_{}.dmx'.format(window_group.name, sky_density)

    if not os.path.isfile(os.path.join(project_folder, d_matrix)) \
            or not reuse_daylight_mtx:
        sender = os.path.relpath(vreceiver, project_folder)

        receiver = sky_receiver(
            os.path.join(project_folder, 'sky/rfluxSky.rad'), sky_density
        )

        rad_files = tuple(os.path.relpath(f, project_folder) for f in drflux_scene)

        dmtx = coeff_matrix_commands(
            d_matrix, os.path.relpath(receiver, project_folder), rad_files,
            sender, None, None, daylight_mtx_parameters)

        commands.append(':: :: [2/{}] calculating daylight matrix'.format(phases_count))
        commands.append(
            ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [scene]'
            ' ^> [*.dmx]'
        )
        commands.append('::')
        commands.append(dmtx.to_rad_string())

    return commands, v_matrix, d_matrix


def get_commands_direct_view_daylight_matrices(
    project_folder, window_group, count, inputfiles, points_file,
    number_of_points, sky_density, view_mtx_parameters, daylight_mtx_parameters,
        reuse_view_mtx=False, reuse_daylight_mtx=False):
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
            window_group.name)
    )

    vreceiver = wgsfiles[count].fpglw[0]

    # change here to create a black scene instead
    vrflux_scene = (
        f for fl in
        (opqfiles.fpblk, blkmaterial, wgsblacked)
        for f in fl)

    drflux_scene = (
        f for fl in
        (opqfiles.fpblk, extrafiles.fpblk, blkmaterial, wgsblacked)
        for f in fl)

    # 3.2.Generate view matrix
    v_matrix = 'result/matrix/{}_dir.vmx'.format(window_group.name)
    if not os.path.isfile(os.path.join(project_folder, v_matrix)) \
            or not reuse_view_mtx:
        commands.append(':: :: [4-1/5] calculating direct view matrix')
        commands.append(
            ':: :: rfluxmtx - [wgroup] [blacked scene] [points] [blacked wgroups]'
            ' ^> [*.vmx]'
        )
        commands.append('::')
        # prepare input files
        rad_files = tuple(os.path.relpath(f, project_folder) for f in vrflux_scene)

        ab = int(view_mtx_parameters.ambient_bounces)
        view_mtx_parameters.ambient_bounces = 1
        vmtx = coeff_matrix_commands(
            v_matrix, os.path.relpath(vreceiver, project_folder), rad_files, '-',
            os.path.relpath(points_file, project_folder), number_of_points,
            view_mtx_parameters)
        view_mtx_parameters.ambient_bounces = ab
        commands.append(vmtx.to_rad_string())

    # 3.3 daylight matrix
    d_matrix = 'result/matrix/{}_{}_dir.dmx'.format(window_group.name, sky_density)

    if not os.path.isfile(os.path.join(project_folder, d_matrix)) \
            or not reuse_daylight_mtx:
        sender = os.path.relpath(vreceiver, project_folder)

        receiver = sky_receiver(
            os.path.join(project_folder, 'sky/rfluxSky.rad'), sky_density
        )

        rad_files = tuple(os.path.relpath(f, project_folder) for f in drflux_scene)

        ab = int(daylight_mtx_parameters.ambient_bounces)
        src = int(daylight_mtx_parameters.sampling_rays_count)
        daylight_mtx_parameters.ambient_bounces = 1
        daylight_mtx_parameters.sampling_rays_count = 1
        dmtx = coeff_matrix_commands(
            d_matrix, os.path.relpath(receiver, project_folder), rad_files,
            sender, None, None, daylight_mtx_parameters)
        daylight_mtx_parameters.ambient_bounces = ab
        daylight_mtx_parameters.sampling_rays_count = src

        commands.append(':: :: [4-2/5] calculating direct daylight matrix')
        commands.append(
            ':: :: rfluxmtx - [sky] [points] [wgroup] [blacked wgroups] [blacked scene]'
            ' ^> [*.dmx]'
        )
        commands.append('::')
        commands.append(dmtx.to_rad_string())

    return commands, v_matrix, d_matrix


def matrix_calculation_three_phase(
        project_folder, window_group, v_matrix, d_matrix, sky_mtx_total,
        transpose=False):
    """Three phase matrix calculation.

    Args:
        project_folder: Full path to project folder.
        window_group: A window_group.
        v_matrix: Path to view matrix.
        d_matrix: Path to daylight matrix.
        sky_mtx_total: Path to sky matrix.
    Returns:
        commands, result_files
    """
    commands = []
    results = []

    for stcount, state in enumerate(window_group.states):
        # 4. matrix calculations
        window_group.state = stcount
        t_matrix = 'scene/bsdf/{}'.format(
            os.path.split(window_group.radiance_material.xmlfile)[-1])
        output = r'tmp/{}..{}.tmp'.format(window_group.name, state.name)
        dct = matrix_calculation(output, v_matrix, t_matrix, d_matrix, sky_mtx_total)
        commands.append(':: :: State {} [{} out of {}]'
                        .format(state.name, stcount + 1, len(window_group.states)))
        commands.append(':: :: [3/3] v_matrix * d_matrix * t_matrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.to_rad_string())

        # 5. convert r, g ,b values to illuminance
        final_output = r'result/{}..{}.ill'.format(window_group.name, state.name)
        finalmtx = rgb_matrix_file_to_ill((dct.output_file,), final_output, transpose)
        commands.append(
            ':: :: rmtxop -c 47.4 119.9 11.6 [results.rgb] ^> [results.ill]')
        commands.append('::')
        commands.append('::')
        commands.append(finalmtx.to_rad_string())

        results.append(os.path.join(project_folder, final_output))

    return commands, results


def matrix_calculation_five_phase(
        project_name, sky_density, project_folder, window_group, skyfiles,
        inputfiles, points_file, total_point_count, rfluxmtx_parameters, v_matrix,
        d_matrix, dv_matrix, dd_matrix, window_group_count=0, reuse_view_mtx=False,
        reuse_daylight_mtx=False, counter=None, transpose=False):
    """Get commands for the five phase recipe.

    This function takes the result_files from 3phase calculation and adds direct
    calculation phases to it.
    """
    commands = []
    results = []
    # unpack inputs
    opqfiles, glzfiles, wgsfiles, extrafiles = inputfiles
    sky_mtx_total, sky_mtx_direct, analemma, sunlist, analemmaMtx = skyfiles

    # get black material file
    blkmaterial = [wgsfiles[window_group_count].fpblk[0]]
    # add all the blacked window groups but the one in use
    # and finally add non-window group glazing as black
    wgsblacked = \
        [f.fpblk[1] for c, f in enumerate(wgsfiles) if c != window_group_count] + \
        list(glzfiles.fpblk)

    for scount, state in enumerate(window_group.states):
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
        window_group.state = scount
        t_matrix = 'scene/bsdf/{}'.format(
            os.path.split(window_group.radiance_material.xmlfile)[-1])
        output = r'tmp/3phase..{}..{}.tmp'.format(window_group.name, state.name)
        dct = matrix_calculation(output, v_matrix, t_matrix, d_matrix, sky_mtx_total)
        commands.append(':: :: [3/5] v_matrix * d_matrix * t_matrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.to_rad_string())

        # 5. convert r, g ,b values to illuminance
        final_output = r'result/3phase..{}..{}.ill'.format(
            window_group.name, state.name)
        finalmtx = rgb_matrix_file_to_ill((dct.output_file,), final_output, transpose)
        commands.append(finalmtx.to_rad_string())

        results.append(os.path.join(project_folder, final_output))

        commands.append('::')

        # calculate direct matrix with black scene
        output = r'tmp/direct..{}..{}.tmp'.format(window_group.name, state.name)
        dct = matrix_calculation(output, dv_matrix, t_matrix, dd_matrix, sky_mtx_direct)
        commands.append(':: :: [4/5] v_matrix * d_matrix * t_matrix')
        commands.append(':: :: dctimestep [vmx] [tmtx] [dmtx] ^ > [results.rgb]')
        commands.append(dct.to_rad_string())

        # 5. convert r, g ,b values to illuminance
        final_output = r'result/direct..{}..{}.ill'.format(
            window_group.name, state.name)
        finalmtx = rgb_matrix_file_to_ill((dct.output_file,), final_output, transpose)
        commands.append(finalmtx.to_rad_string())

        results.append(os.path.join(project_folder, final_output))

        commands.append('::')

        # in case window group is not already provided
        window_groupfiles = (wgsfiles[window_group_count].fp[scount],)

        rflux_scene_blacked = (
            f for fl in
            (window_groupfiles, opqfiles.fpblk, extrafiles.fpblk,
             blkmaterial, wgsblacked)
            for f in fl)

        sun_matrix = 'result/matrix/sun_{}..{}..{}.dc'.format(
            project_name, window_group.name, state.name)

        if not os.path.isfile(os.path.join(project_folder, sun_matrix)) \
                or not reuse_daylight_mtx:

            rad_files_blacked = tuple(os.path.relpath(f, project_folder)
                                      for f in rflux_scene_blacked)

            # replace the 4th phase with the new function
            commands.append(':: :: [5/5] black scene analemma daylight matrix')
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
            commands.append(':: :: reusing daylight matrices')
            commands.append('::')

        commands.append(':: :: calculating black daylight mtx * analemma')
        commands.append(
            ':: :: dctimestep [black dc.mtx] [analemma only sky] ^> [sun results.rgb]')
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
            'result/sun..{}..{}.ill'.format(window_group.name, state.name), transpose
        )
        commands.append(finalmtx.to_rad_string())

        commands.append(':: :: calculating final results')
        commands.append(
            ':: :: rmtxop [3phase results.ill] - [direct results.ill] + '
            '[sun results.ill] ^> [final results.ill]'
        )
        commands.append('::')

        fmtx = final_matrix_addition(
            'result/3phase..{}..{}.ill'.format(window_group.name, state.name),
            'result/direct..{}..{}.ill'.format(window_group.name, state.name),
            'result/sun..{}..{}.ill'.format(window_group.name, state.name),
            'result/{}..{}.ill'.format(window_group.name, state.name)
        )

        commands.append(fmtx.to_rad_string())
        commands.append(
            ':: end of calculation for {}, {}'.format(window_group.name, state.name))
        commands.append('::')
        commands.append('::')

        results.append(
            os.path.join(project_folder, str(fmtx.output_file))
        )

    return commands, results
