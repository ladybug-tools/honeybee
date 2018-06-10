from ..recipeutil import write_extra_files
from ..recipexphaseutil import write_rad_files_multi_phase, matrix_calculation_five_phase
from ..recipedcutil import get_commands_scene_daylight_coeff, get_commands_sky
from ..recipexphaseutil import get_commands_view_daylight_matrices
from ..recipexphaseutil import get_commands_direct_view_daylight_matrices

from ..threephase.gridbased import ThreePhaseGridBased
from ....futil import write_to_file

from ...sky.skymatrix import SkyMatrix
from ...analysisgrid import AnalysisGrid
from ...parameters.rfluxmtx import RfluxmtxParameters
from ....hbsurface import HBSurface

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
        print(analysis_recipe.results())
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

    @classmethod
    def from_json(cls, rec_json):
        """Create five phase recipe from JSON file
            {
            "id": "five_phase",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "view_mtx_parameters": {} // radiance gridbased parameters json file
            "daylight_mtx_parameters": {} //radiance gridbased parameters json file
            }
        """
        sky_mtx = SkyMatrix.from_json(rec_json["sky_mtx"])
        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])
        simulation_type = rec_json["simulation_type"]

        view_mtx_parameters = \
            RfluxmtxParameters.from_json(rec_json["view_mtx_parameters"])
        daylight_mtx_parameters = \
            RfluxmtxParameters.from_json(rec_json["daylight_mtx_parameters"])

        return cls(sky_mtx=sky_mtx, analysis_grids=analysis_grids,
                   view_mtx_parameters=view_mtx_parameters,
                   daylight_mtx_parameters=daylight_mtx_parameters,
                   hb_objects=hb_objects,
                   simulation_type=simulation_type)

    def to_json(self):
        """Create five phase recipe JSON file
            {
            "id": "five_phase",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "view_mtx_parameters": {} // radiance gridbased parameters json file
            "daylight_mtx_parameters": {} //radiance gridbased parameters json file
            }
        """
        return {
            "id": "five_phase",
            "type": "gridbased",
            "sky_mtx": self.sky_matrix.to_json(),
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "simulation_type": self.simulation_type,
            "view_mtx_parameters": self.view_mtx_parameters.to_json(),
            "daylight_mtx_parameters": self.daylight_mtx_parameters.to_json()
        }

    def write(self, target_folder, project_name='untitled', header=True,
              transpose=False):
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
        # create main folder target_folder/project_name
        project_folder = \
            super(ThreePhaseGridBased, self).write_content(
                target_folder, project_name, False, subfolders=['tmp', 'result/matrix']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files_multi_phase(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )

        assert len(self.window_groups) > 0, \
            ValueError(
                'Found no window groups! If you do not have a window group'
                ' in the scene use daylight coefficient ')

        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene', True)

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
            self.reuse_daylight_mtx, self.total_runs_count, transpose=transpose)

        self._commands.extend(commands)
        self._result_files.extend(
            os.path.join(project_folder, str(result)) for result in results
        )

        for count, wg in enumerate(self.window_groups):

            # v_matrix and d_matrix
            commands, v_matrix, d_matrix = get_commands_view_daylight_matrices(
                project_folder, wg, count, inputfiles, points_file, number_of_points,
                self.sky_matrix.sky_density, self.view_mtx_parameters,
                self.daylight_mtx_parameters, self.reuse_view_mtx,
                self.reuse_daylight_mtx, phases_count=5)

            self._commands.extend(commands)

            # direct v_matrix and d_matrix
            commands, dv_matrix, dd_matrix = get_commands_direct_view_daylight_matrices(
                project_folder, wg, count, inputfiles, points_file, number_of_points,
                self.sky_matrix.sky_density, self.view_mtx_parameters,
                self.daylight_mtx_parameters, self.reuse_view_mtx,
                self.reuse_daylight_mtx)

            self._commands.extend(commands)

            counter = 2 + sum(wg.state_count for wg in self.window_groups[:count])

            # t_matrix - direct + analemma
            # TODO(mostapha): send the enalysis grid and not the points file
            # otherwise we won't be able to support multiple grids.
            cmd, results = matrix_calculation_five_phase(
                project_name, self.sky_matrix.sky_density, project_folder, wg, skyfiles,
                inputfiles, points_file, self.total_point_count,
                self.daylight_mtx_parameters, v_matrix, d_matrix, dv_matrix, dd_matrix,
                count, self.reuse_view_mtx, self.reuse_daylight_mtx,
                (counter, self.total_runs_count), transpose=transpose)

            self._commands.extend(cmd)
            self._result_files.extend(results)

        # # 5. write batch file
        batch_file = os.path.join(project_folder, "commands.bat")
        write_to_file(batch_file, '\n'.join(self.preproc_commands()))

        return batch_file
