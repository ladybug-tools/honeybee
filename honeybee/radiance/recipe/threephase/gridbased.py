from ..parameters import get_radiance_parameters_grid_based

from ..recipeutil import write_extra_files
from ..recipedcutil import get_commands_scene_daylight_coeff, get_commands_sky

from ..recipexphaseutil import matrix_calculation_three_phase, \
    write_rad_files_multi_phase
from ..recipexphaseutil import get_commands_view_daylight_matrices

from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...sky.skymatrix import SkyMatrix
from ....futil import write_to_file

from ...analysisgrid import AnalysisGrid
from ...parameters.rfluxmtx import RfluxmtxParameters
from ....hbsurface import HBSurface

import os


class ThreePhaseGridBased(DaylightCoeffGridBased):
    """Grid based three phase analysis recipe.

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
                 sub_folder="gridbased_threephase"):
        """Create an annual recipe."""
        DaylightCoeffGridBased.__init__(
            self, sky_mtx, analysis_grids, simulation_type,
            reuse_daylight_mtx=reuse_daylight_mtx, hb_objects=hb_objects,
            sub_folder=sub_folder
        )

        self.view_mtx_parameters = view_mtx_parameters
        self.daylight_mtx_parameters = daylight_mtx_parameters
        self.reuse_view_mtx = reuse_view_mtx

    @classmethod
    def from_json(cls, rec_json):
        """Create three phase recipe from JSON file
            {
            "id": "three_phase",
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

        view_mtx_parameters = RfluxmtxParameters.from_json(rec_json["view_mtx_parameters"])
        daylight_mtx_parameters = RfluxmtxParameters.from_json(rec_json["view_mtx_parameters"])

        return cls(sky_mtx=sky_mtx, analysis_grids=analysis_grids, \
                view_mtx_parameters=view_mtx_parameters, \
                daylight_mtx_parameters=daylight_mtx_parameters, \
                hb_objects=hb_objects, \
                simulation_type=simulation_type)

    @classmethod
    def from_weather_file_points_and_vectors(
        cls, epw_file, point_groups, vector_groups=None, sky_density=1,
        simulation_type=0, view_mtx_parameters=None, daylight_mtx_parameters=None,
        reuse_view_mtx=True, reuse_daylight_mtx=True, hb_window_surfaces=None,
            hb_objects=None, sub_folder="gridbased_threephase"):
        """Create three-phase recipe from weather file, points and vectors.

        Args:
            epw_file: An EnergyPlus weather file.
            point_groups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            sky_density: A positive intger for sky density. 1: Tregenza Sky,
                2: Reinhart Sky, etc. (Default: 1)
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        assert epw_file.lower().endswith('.epw'), \
            ValueError('{} is not a an EnergyPlus weather file.'.format(epw_file))
        sky_mtx = SkyMatrix(epw_file, sky_density)
        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)

        return cls(
            sky_mtx, analysis_grids, simulation_type, view_mtx_parameters,
            daylight_mtx_parameters, reuse_view_mtx, reuse_daylight_mtx,
            hb_window_surfaces, hb_objects, sub_folder)

    @classmethod
    def from_points_file(
        cls, epw_file, points_file, sky_density=1, simulation_type=0,
        view_mtx_parameters=None, daylight_mtx_parameters=None, reuse_view_mtx=True,
        reuse_daylight_mtx=True, hb_window_surfaces=None, hb_objects=None,
            sub_folder="gridbased_threephase"):
        """Create an annual recipe from points file."""
        try:
            with open(points_file, "rb") as inf:
                point_groups = tuple(line.split()[:3] for line in inf.readline())
                vector_groups = tuple(line.split()[3:] for line in inf.readline())
        except Exception as e:
            raise ValueError("Couldn't import points from {}:\n\t{}".format(
                points_file, e))

        return cls.from_weather_file_points_and_vectors(
            epw_file, point_groups, vector_groups, sky_density, simulation_type,
            view_mtx_parameters, daylight_mtx_parameters, reuse_view_mtx,
            reuse_daylight_mtx, hb_window_surfaces, hb_objects, sub_folder)

    @property
    def view_mtx_parameters(self):
        """View matrix parameters."""
        return self._view_mtx_parameters

    @view_mtx_parameters.setter
    def view_mtx_parameters(self, vm):
        if not vm:
            self._view_mtx_parameters = get_radiance_parameters_grid_based(0, 2).vmtx
        else:
            assert hasattr(vm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(vm)))
            self._view_mtx_parameters = vm

        # reset -I option for when parameters are updated.
        if self._simType < 2:
            self._view_mtx_parameters.irradiance_calc = True
        else:
            self._view_mtx_parameters.irradiance_calc = None

    @property
    def daylight_mtx_parameters(self):
        """View matrix parameters."""
        return self._daylight_mtx_parameters

    @daylight_mtx_parameters.setter
    def daylight_mtx_parameters(self, dm):
        if not dm:
            self._daylight_mtx_parameters = get_radiance_parameters_grid_based(0, 2).dmtx
        else:
            assert hasattr(dm, 'isRfluxmtxParameters'), \
                TypeError('Expected RfluxmtxParameters not {}'.format(type(dm)))
            self._daylight_mtx_parameters = dm

        # reset -I option for when parameters are updated.
        if self._simType < 2:
            self._daylight_mtx_parameters.irradiance_calc = True
        else:
            self._daylight_mtx_parameters.irradiance_calc = None

    @property
    def sky_density(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.sky_matrix.sky_density)

    def to_json(self):
        """Create three phase recipe JSON file
            {
            "id": "three_phase",
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
                "id": "three_phase",
                "type": "gridbased",
                "sky_mtx": self.sky_matrix.to_json(),
                "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
                "surfaces": [srf.to_json() for srf in self.hb_objects],
                "simulation_type": self.simulation_type,
                "view_mtx_parameters": self.view_mtx_parameters.to_json(),
                "daylight_mtx_parameters": self.daylight_mtx_parameters.to_json()
                }

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
        # create main folder target_folder/project_name
        project_folder = \
            super(DaylightCoeffGridBased, self).write_content(
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

        # for statcic glazing - calculate total, direct and direct-analemma results
        # calculate the contribution of glazing if any with all window groups blacked
        inputfiles = opqfiles, glzfiles, wgsfiles, extrafiles
        commands, results = get_commands_scene_daylight_coeff(
            project_name, self.sky_matrix.sky_density, project_folder, skyfiles,
            inputfiles, points_file, self.total_point_count, self.radiance_parameters,
            self.reuse_daylight_mtx, self.total_runs_count)

        self._commands.extend(commands)
        self._result_files.extend(
            os.path.join(project_folder, str(result)) for result in results
        )

        # calculate three-phase for window groups
        for count, wg in enumerate(self.window_groups):

            commands, v_matrix, d_matrix = get_commands_view_daylight_matrices(
                project_folder, wg, count, inputfiles, points_file, number_of_points,
                self.sky_matrix.sky_density, self.view_mtx_parameters,
                self.daylight_mtx_parameters, self.reuse_view_mtx,
                self.reuse_daylight_mtx)

            self._commands.extend(commands)

            # t_matrix
            cmd, results = matrix_calculation_three_phase(
                project_folder, wg, v_matrix, d_matrix, skyfiles.sky_mtx_total)

            self._commands.extend(cmd)
            self._result_files.extend(results)

        # # 5. write batch file
        batch_file = os.path.join(project_folder, "commands.bat")
        write_to_file(batch_file, '\n'.join(self.preproc_commands()))

        return batch_file
