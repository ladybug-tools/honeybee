"""Radiance Daylight Coefficient Image-Based Analysis Recipe."""
from ..recipeutil import write_extra_files, glz_srf_to_window_group
from ..recipedcutil import write_rad_files_daylight_coeff, create_reference_map_command
from ..recipedcutil import image_based_view_sampling_commands, \
    image_based_view_coeff_matrix_commands, imaged_based_sun_coeff_matrix_commands
from ...command.oconv import Oconv
from ...command.pcomb import Pcomb, PcombImage
from ...parameters.pcomb import PcombParameters
from ..parameters import get_radiance_parameters_image_based
from ..recipedcutil import image_based_view_matrix_calculation
from ..recipedcutil import sky_receiver, get_commands_sky
from .._imagebasedbase import GenericImageBased
from ...parameters.vwrays import VwraysParameters
from ...imagecollection import ImageCollection
from ....futil import write_to_file

import os

from itertools import izip


class DaylightCoeffImageBased(GenericImageBased):
    """Daylight Coefficient Image-Based.

    Attributes:
        sky_mtx: A honeybee sky for the analysis
        views: List of views.
        simulation_type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 2)
        rad_parameters: Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:


    """

    # TODO: implemnt isChanged at AnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky_mtx, views, simulation_type=2, daylight_mtx_parameters=None,
                 vwrays_parameters=None, reuse_daylight_mtx=True, hb_objects=None,
                 sub_folder="imagebased_daylightcoeff"):
        """Create grid-based recipe."""
        GenericImageBased.__init__(
            self, views, hb_objects, sub_folder)

        self.sky_matrix = sky_mtx
        """A honeybee sky for the analysis."""

        self.simulation_type = simulation_type
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 2)
        """

        self.daylight_mtx_parameters = daylight_mtx_parameters
        """Radiance parameters for image based analysis (rfluxmtx).
            (Default: imagebased.LowQualityImage)"""

        self.vwrays_parameters = vwrays_parameters
        """Radiance parameters for vwrays.
            (Default: imagebased.LowQualityImage)"""

        self.reuse_daylight_mtx = reuse_daylight_mtx

    @property
    def simulation_type(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulation_type.setter
    def simulation_type(self, value):
        try:
            value = int(value)
        except TypeError:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky_matrix.is_climate_based, \
                "The sky for radition analysis should be climate-based."

        self._simType = value
        self.sky_matrix.sky_type = value

    @property
    def sky_matrix(self):
        """Get and set sky definition."""
        return self._sky_matrix

    @sky_matrix.setter
    def sky_matrix(self, new_sky):
        assert hasattr(new_sky, 'isRadianceSky'), \
            '%s is not a valid Honeybee sky.' % type(new_sky)
        assert not new_sky.is_point_in_time, \
            TypeError('Sky for daylight coefficient recipe must be a sky matrix.')
        self._sky_matrix = new_sky.duplicate()

    @property
    def sky_density(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.sky_matrix.sky_density)

    @property
    def daylight_mtx_parameters(self):
        """Get and set Radiance parameters."""
        return self._daylight_mtx_parameters

    @daylight_mtx_parameters.setter
    def daylight_mtx_parameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            par = get_radiance_parameters_image_based(0, 1).dmtx
        else:
            assert hasattr(par, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))
        self._daylight_mtx_parameters = par

    @property
    def vwrays_parameters(self):
        """Get and set Radiance parameters."""
        return self._vwrays_parameters

    @vwrays_parameters.setter
    def vwrays_parameters(self, par):
        if not par:
            # set VwraysParameters as default radiance parameter for annual analysis
            par = VwraysParameters()
            par.sampling_rays_count = self.daylight_mtx_parameters.sampling_rays_count
        else:
            assert hasattr(par, 'isVwraysParameters'), \
                TypeError('Expected VwraysParameters not {}'.format(type(par)))
        assert par.sampling_rays_count == \
            self.daylight_mtx_parameters.sampling_rays_count, \
            ValueError(
                'Number of sampling_rays_count should be equal between '
                'daylight_mtx_parameters [{}] and vwrays_parameters [{}].'
                .format(self.daylight_mtx_parameters.sampling_rays_count,
                        par.sampling_rays_count))

        self._vwrays_parameters = par

    def is_daylight_mtx_created(self, study_folder, view, wg, state):
        """Check if hdr images for daylight matrix are already created."""
        for i in range(1 + 144 * (self.sky_matrix.sky_density ** 2)):
            for t in ('total', 'direct'):
                fp = os.path.join(
                    study_folder, 'result/dc/%s/%03d_%s..%s..%s.hdr' % (
                        t, i, view.name, wg.name, state.name)
                )

                if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                    # file doesn't exist or is smaller than 265 bytes
                    return False

        return True

    def is_sun_mtx_created(self, study_folder, view, wg, state):
        """Check if hdr images for daylight matrix are already created."""
        for count, h in enumerate(self.sky_matrix.hoys):
            fp = os.path.join(
                study_folder, 'result/dc/{}/{}_{}..{}..{}.hdr'.format(
                    'isun', '%04d' % count, view.name, wg.name, state.name))

            if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                # file doesn't exist or is smaller than 265 bytes
                return False

        return True

    def is_hdr_mtx_created(self, study_folder, view, wg, state, stype):
        """Check if hourly hdr images for daylight matrix are already created."""
        for count, h in enumerate(self.sky_matrix.hoys):
            fp = os.path.join(
                study_folder, 'result/hdr/{}/{}_{}..{}..{}.hdr'.format(
                    stype, '%04d' % (count + 1), view.name, wg.name, state.name))

            if not os.path.isfile(fp) or os.path.getsize(fp) < 265:
                # file doesn't exist or is smaller than 265 bytes
                return False

        return True

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.

        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder target_folder/project_name
        project_folder = \
            super(GenericImageBased, self).write_content(
                target_folder, project_name, False,
                subfolders=['view', 'result/dc', 'result/hdr',
                            'result/dc/total', 'result/dc/direct', 'result/dc/isun',
                            'result/dc/refmap', 'result/hdr/total', 'result/hdr/direct',
                            'result/hdr/sun', 'result/hdr/combined', 'result/hdr/isun']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files_daylight_coeff(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )
        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene', True)

        # reset self.result_files
        self._result_files = [[] for v in xrange(self.view_count)]

        # 1.write views
        view_files = self.write_views(project_folder + '/view')

        if header:
            self.commands.append(self.header(project_folder))

        # # 2.1.Create sky matrix.
        # # 2.2. Create sun matrix
        skycommands, skyfiles = get_commands_sky(project_folder, self.sky_matrix,
                                                 reuse=True)

        sky_mtx_total, sky_mtx_direct, analemma, sunlist, analemmaMtx = skyfiles
        self._commands.extend(skycommands)

        # for each window group - calculate total, direct and direct-analemma results
        # I can just add fenestration rad files here and that will work!

        # calculate the contribution of glazing if any with all window groups blacked
        # this is a hack. A better solution is to create a HBDynamicSurface from glazing
        # surfaces. The current limitation is that HBDynamicSurface can't have several
        # surfaces with different materials.
        all_window_groups = [glz_srf_to_window_group()]
        all_window_groups.extend(self.window_groups)
        all_wgs_files = [glzfiles] + list(wgsfiles)

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

        scene_files = [f for filegroups in (opqfiles.fp, glzfiles.fp, extrafiles.fp)
                       for f in filegroups]
        oct_scene_files = scene_files + blkmaterial + wgsblacked

        oc = Oconv(project_name)
        oc.scene_files = tuple(self.relpath(f, project_folder)
                               for f in oct_scene_files)

        self._commands.append(oc.to_rad_string())

        # # 4.2.prepare vwray
        for viewCount, (view, view_file) in enumerate(izip(self.views, view_files)):
            # create the reference map file
            self.commands.append(':: calculation for view: {}'.format(view.name))
            self.commands.append(':: 0 reference map')

            refmapfilename = '{}_map.hdr'.format(view.name)
            refmapfilepath = os.path.join('result/dc/refmap', refmapfilename)

            if not self.reuse_daylight_mtx or not os.path.isfile(
                    os.path.join(project_name, 'result/dc/refmap', refmapfilename)):
                rfm = create_reference_map_command(
                    view, self.relpath(view_file, project_folder),
                    'result/dc/refmap', oc.output_file)
                self._commands.append(rfm.to_rad_string())
            # Step1: Create the view matrix.
            self.commands.append(':: 1 view sampling')
            view_info_file, vwr_samp = image_based_view_sampling_commands(
                project_folder, view, view_file, self.vwrays_parameters)
            self.commands.append(vwr_samp.to_rad_string())

            # set up the geometries
            for count, wg in enumerate(all_window_groups):
                if count == 0:
                    if len(wgsfiles) > 0:
                        blkmaterial = [wgsfiles[0].fpblk[0]]
                        wgsblacked = [f.fpblk[1] for c, f in enumerate(wgsfiles)]
                    else:
                        blkmaterial = []
                        wgsblacked = []
                else:
                    # add material file
                    blkmaterial = [all_wgs_files[count].fpblk[0]]
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
                        non_blacked_wgfiles = all_wgs_files[count].fp
                    else:
                        non_blacked_wgfiles = (all_wgs_files[count].fp[scount],)

                    rflux_scene = (
                        f for fl in
                        (non_blacked_wgfiles, opqfiles.fp, extrafiles.fp,
                         blkmaterial, wgsblacked)
                        for f in fl)

                    rflux_scene_blacked = (
                        f for fl in
                        (non_blacked_wgfiles, opqfiles.fpblk, extrafiles.fpblk,
                         blkmaterial, wgsblacked)
                        for f in fl)

                    sender = '-'

                    ground_file_format = 'result/dc/total/%03d_%s..%s..%s.hdr' % (
                        1 + 144 * (self.sky_matrix.sky_density ** 2),
                        view.name, wg.name, state.name
                    )

                    sky_file_format = 'result/dc/total/%03d_{}..{}..{}.hdr'.format(
                        view.name, wg.name, state.name)

                    receiver = sky_receiver(
                        os.path.join(
                            project_folder,
                            'sky/rfluxSkyTotal..{}..{}.rad'.format(
                                wg.name, state.name)),
                        self.sky_matrix.sky_density, ground_file_format, sky_file_format
                    )

                    ground_file_format = 'result/dc/direct/%03d_%s..%s..%s.hdr' % (
                        1 + 144 * (self.sky_matrix.sky_density ** 2),
                        view.name, wg.name, state.name
                    )

                    sky_file_format = 'result/dc/direct/%03d_{}..{}..{}.hdr'.format(
                        view.name, wg.name, state.name)

                    receiver_dir = sky_receiver(
                        os.path.join(project_folder,
                                     'sky/rfluxSkyDirect..{}..{}.rad'.format(
                                         wg.name, state.name)),
                        self.sky_matrix.sky_density, ground_file_format, sky_file_format
                    )

                    rad_files_blacked = tuple(self.relpath(f, project_folder)
                                              for f in rflux_scene_blacked)
                    # Daylight matrix
                    if not self.reuse_daylight_mtx or not \
                            self.is_daylight_mtx_created(project_folder, view, wg,
                                                         state):

                        self.reuse_daylight_mtx = False

                        rad_files = tuple(self.relpath(f, project_folder)
                                          for f in rflux_scene)

                        self._commands.append(
                            ':: :: 1. daylight matrix {}, {} > state {}'.format(
                                view.name, wg.name, state.name)
                        )

                        self._commands.append(':: :: 1.1 scene daylight matrix')

                        # output pattern is set in receiver
                        rflux = image_based_view_coeff_matrix_commands(
                            self.relpath(receiver, project_folder),
                            rad_files, sender, view_info_file,
                            view_file, str(vwr_samp.output_file),
                            self.daylight_mtx_parameters)

                        self.commands.append(rflux.to_rad_string())
                    else:
                        print(
                            'reusing the dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if not self.reuse_daylight_mtx or not \
                            self.is_sun_mtx_created(project_folder, view, wg, state):
                        self._commands.append(':: :: 1.2 blacked scene daylight matrix')

                        ab = int(self.daylight_mtx_parameters.ambient_bounces)
                        self.daylight_mtx_parameters.ambient_bounces = 1

                        # output pattern is set in receiver
                        rflux_direct = image_based_view_coeff_matrix_commands(
                            self.relpath(receiver_dir, project_folder),
                            rad_files_blacked, sender, view_info_file,
                            view_file, str(vwr_samp.output_file),
                            self.daylight_mtx_parameters)

                        self._commands.append(rflux_direct.to_rad_string())

                        self._commands.append(':: :: 1.3 blacked scene analemma matrix')

                        if os.name == 'nt':
                            output_filename_format = \
                                ' result/dc/isun/%%04d_{}..{}..{}.hdr'.format(
                                    view.name, wg.name, state.name)
                        else:
                            output_filename_format = \
                                ' result/dc/isun/%04d_{}..{}..{}.hdr'.format(
                                    view.name, wg.name, state.name)

                        sun_commands = imaged_based_sun_coeff_matrix_commands(
                            output_filename_format, view, str(vwr_samp.output_file),
                            rad_files_blacked, self.relpath(analemma, project_folder),
                            self.relpath(sunlist, project_folder))

                        # delete the files if they are already created
                        # rcontrib won't overwrite the files if they already exist
                        for hourcount in xrange(len(self.sky_matrix.hoys)):
                            sf = 'result/dc/isun/{:04d}_{}..{}..{}.hdr'.format(
                                hourcount, view.name, wg.name, state.name
                            )
                            try:
                                fp = os.path.join(project_folder, sf)
                                os.remove(fp)
                            except Exception as e:
                                # failed to delete the file
                                if os.path.isfile(fp):
                                    print('Failed to remove {}:\n{}'.format(sf, e))

                        self._commands.extend(cmd.to_rad_string()
                                              for cmd in sun_commands)
                        self.daylight_mtx_parameters.ambient_bounces = ab

                    else:
                        print(
                            'reusing the sun matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    # generate hourly images
                    if skycommands or not self.reuse_daylight_mtx or not \
                        self.is_hdr_mtx_created(project_folder, view, wg,
                                                state, 'total'):
                        # Generate resultsFile
                        self._commands.append(
                            ':: :: 2.1.0 total daylight matrix calculations')
                        dct = image_based_view_matrix_calculation(
                            view, wg, state, sky_mtx_total, 'total')
                        self.commands.append(dct.to_rad_string())
                    else:
                        print(
                            'reusing the total dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if skycommands or not self.reuse_daylight_mtx or not \
                        self.is_hdr_mtx_created(project_folder, view, wg,
                                                state, 'direct'):
                        self._commands.append(':: :: 2.2.0 direct matrix calculations')
                        dct_direct = image_based_view_matrix_calculation(
                            view, wg, state, sky_mtx_direct, 'direct')
                        self._commands.append(dct_direct.to_rad_string())
                    else:
                        print(
                            'reusing the direct dalight matrix for {}:{} from '
                            'the previous study.'.format(wg.name, state.name))

                    if skycommands or not self.reuse_daylight_mtx or not \
                        self.is_hdr_mtx_created(project_folder, view, wg,
                                                state, 'sun'):
                        self._commands.append(
                            ':: :: 2.3.0 enhanced direct matrix calculations')
                        dct_sun = image_based_view_matrix_calculation(
                            view, wg, state,
                            self.relpath(analemmaMtx, project_folder), 'isun', 4)

                        self._commands.append(dct_sun.to_rad_string())

                        # multiply the sun matrix with the reference map
                        # TODO: move this to a separate function
                        # TODO: write the loop as a for loop in bat/bash file
                        par = PcombParameters()
                        refmap_image = PcombImage(input_image_file=refmapfilepath)
                        if os.name == 'nt':
                            par.expression = '"lo=li(1)*li(2)"'
                        else:
                            par.expression = "'lo=li(1)*li(2)'"

                        for hourcount in xrange(len(self.sky_matrix.hoys)):
                            inp = 'result/hdr/isun/{:04d}_{}..{}..{}.hdr'.format(
                                hourcount + 1, view.name, wg.name, state.name
                            )
                            out = 'result/hdr/sun/{:04d}_{}..{}..{}.hdr'.format(
                                hourcount + 1, view.name, wg.name, state.name
                            )
                            images = PcombImage(input_image_file=inp), refmap_image

                            pcb = Pcomb(images, out, par)
                            self._commands.append(pcb.to_rad_string())
                    else:
                        print(
                            'reusing the enhanced direct dalight matrix for '
                            '{}:{} from the previous study.'
                            .format(wg.name, state.name))

                    result_files = tuple(os.path.join(
                        project_folder,
                        'result/hdr/%s/{}_{}..{}..{}.hdr'.format(
                            '%04d' % (count + 1), view.name, wg.name, state.name))
                        for count, h in enumerate(self.sky_matrix.hoys)
                    )

                    self._result_files[viewCount].append(
                        (wg.name, state.name, result_files))

        # # 4.3 write batch file
        batch_file = os.path.join(project_folder, "commands.bat")

        write_to_file(batch_file, "\n".join(self.commands))

        print("Files are written to: %s" % project_folder)
        return batch_file

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."
        hoys = self.sky_matrix.hoys

        for viewCount, viewResults in enumerate(self._result_files):
            imgc = ImageCollection(self.views[viewCount].name)

        for source, state, files in viewResults:
            source_files = []
            for i in files:
                fpt = i % 'total'
                fpd = i % 'direct'
                fps = i % 'sun'
                source_files.append((fpt, fpd, fps))

            imgc.add_coupled_image_files(source_files, hoys, source, state)

        # TODO(mostapha): Add properties to the class for output file addresses
        imgc.output_folder = fpt.split('result/hdr')[0] + 'result/hdr/combined'
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
             _analysisType[self.simulation_type],
             self.view_count)
