from ..recipeutil import write_extra_files
from ..recipexphaseutil import write_rad_filesMultiPhase, matrix_calculation_five_phase
from ..recipedcutil import get_commands_scene_daylight_coeff, get_commands_sky
from ..recipexphaseutil import get_commands_view_daylight_matrices
from ..recipexphaseutil import get_commands_direct_view_daylight_matrices

from ..threephase.gridbased import ThreePhaseGridBased
from ....futil import write_to_file

import os


class FivePhaseGridBased(ThreePhaseGridBased):
    """Grid based five phase analysis recipe.

    Attributes:
        sky_mtx: A radiance SkyMatrix or SkyVector. For an SkyMatrix the analysis
            will be ran for the analysis period.
        analysis_grids: A list of Honeybee analysis grids. Daylight metrics will
            be calculated for each analysisGrid separately.
        simulation_type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radiance_parameters: Radiance parameters for this analysis. Parameters
            should be an instance of RfluxmtxParameters.
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "daylightcoeff").

    Usage:

        # initiate analysis_recipe
        analysis_recipe = ThreePhaseGridBased(
            sky_mtx, analysis_grids, rad_parameters
            )

        # add honeybee object
        analysis_recipe.hb_objects = HBObjs

        # write analysis files to local drive
        commandsFile = analysis_recipe.write(_folder_, _name_)

        # run the analysis
        analysis_recipe.run(commandsFile)

        # get the results
        print analysis_recipe.results()
    """

    def __init__(self, sky_mtx, analysis_grids, simulation_type=0,
                 view_mtx_parameters=None, daylight_mtx_parameters=None,
                 reuse_view_mtx=True, reuse_daylight_mtx=True, hb_objects=None,
                 sub_folder="gridbased_fivephase"):
        """Create an annual recipe."""
        ThreePhaseGridBased.__init__(
            self, sky_mtx, analysis_grids, simulation_type,
            view_mtx_parameters, daylight_mtx_parameters,
            reuse_view_mtx, reuse_daylight_mtx, hb_objects,
            sub_folder)

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.
            header: A boolean to include path to radiance folder in commands file.

        Returns:
            Path yo commands file.
        """
        # 0.prepare target folder
        # create main folder target_folder\project_name
        project_folder = \
            super(ThreePhaseGridBased, self).write_content(
                target_folder, project_name, False, subfolders=['tmp', 'result/matrix']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_filesMultiPhase(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )

        assert len(self.window_groups) > 0, \
            ValueError(
                'Found no window groups! If you do not have a window group'
                ' in the scene use daylight coefficient ')

        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene')

        # 0.write points
        points_file = self.write_analysis_grids(project_folder, project_name)
        number_of_points = sum(len(ag) for ag in self.analysis_grids)

        # 2.write batch file
        if header:
            self.commands.append(self.header(project_folder))

        # # 2.1.Create sky matrix.
        # # 2.2. Create sun matrix
        skycommands, skyfiles = get_commands_sky(project_folder, self.sky_matrix,
                                                 reuse=True)

        self._commands.extend(skycommands)

        # for each window group - calculate total, direct and direct-analemma results
        # calculate the contribution of glazing if any with all window groups blacked
        inputfiles = opqfiles, glzfiles, wgsfiles, extrafiles
        commands, results = get_commands_scene_daylight_coeff(
            project_name, self.sky_matrix.sky_density, project_folder, skyfiles,
            inputfiles, points_file, self.total_point_count, self.radiance_parameters,
            self.reuse_daylight_mtx, self.total_runs_count)

        self._commands.extend(commands)
        self._resultFiles.extend(
            os.path.join(project_folder, str(result)) for result in results
        )

        for count, wg in enumerate(self.window_groups):

            # v_matrix and d_matrix
            commands, v_matrix, d_matrix = get_commands_view_daylight_matrices(
                project_folder, wg, count, inputfiles, points_file, number_of_points,
                self.sky_matrix.sky_density, self.view_mtx_parameters,
                self.daylight_mtx_parameters, self.reuse_view_mtx, self.reuse_daylight_mtx,
                phases_count=5)

            self._commands.extend(commands)

            # direct v_matrix and d_matrix
            commands, dv_matrix, dd_matrix = get_commands_direct_view_daylight_matrices(
                project_folder, wg, count, inputfiles, points_file, number_of_points,
                self.sky_matrix.sky_density, self.view_mtx_parameters,
                self.daylight_mtx_parameters, self.reuse_view_mtx, self.reuse_daylight_mtx)

            self._commands.extend(commands)

            counter = 2 + sum(wg.state_count for wg in self.window_groups[:count])

            # t_matrix - direct + analemma
            # TODO(mostapha): send the enalysis grid and not the points file
            # otherwise we won't be able to support multiple grids.
            cmd, results = matrix_calculation_five_phase(
                project_name, self.sky_matrix.sky_density, project_folder, wg, skyfiles,
                inputfiles, points_file, self.total_point_count, self.daylight_mtx_parameters,
                v_matrix, d_matrix, dv_matrix, dd_matrix, count, self.reuse_view_mtx,
                self.reuse_daylight_mtx, (counter, self.total_runs_count))

            self._commands.extend(cmd)
            self._resultFiles.extend(results)

        # # 5. write batch file
        batch_file = os.path.join(project_folder, "commands.bat")
        write_to_file(batchFile, '\n'.join(self.preproc_commands()))

        return batchFile
