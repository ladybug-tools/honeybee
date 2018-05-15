"""Radiance Daylight Coefficient Grid-Based Analysis Recipe."""
from ..recipeutil import write_extra_files
from ..recipedcutil import write_rad_files_daylight_coeff, get_commands_sky
from ..recipedcutil import get_commands_scene_daylight_coeff
from ..recipedcutil import get_commands_w_groups_daylight_coeff
from .._gridbasedbase import GenericGridBased
from ..parameters import get_radiance_parameters_grid_based
from ...sky.skymatrix import SkyMatrix
from ....futil import write_to_file
from ...analysisgrid import AnalysisGrid
from ...parameters.rfluxmtx import RfluxmtxParameters
from ....hbsurface import HBSurface

import os


class DaylightCoeffGridBased(GenericGridBased):
    """Grid based daylight coefficient analysis recipe.

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
        analysis_recipe = DaylightCoeffGridBased(
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
                 radiance_parameters=None, reuse_daylight_mtx=True, hb_objects=None,
                 sub_folder="gridbased_daylightcoeff"):
        """Create an annual recipe."""
        GenericGridBased.__init__(
            self, analysis_grids, hb_objects, sub_folder
        )

        self.sky_matrix = sky_mtx

        self.radiance_parameters = radiance_parameters

        self.simulation_type = simulation_type
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 2)
        """

        self.reuse_daylight_mtx = reuse_daylight_mtx

    @classmethod
    def from_json(cls, rec_json):
        """Create daylight coefficient recipe from JSON file
            {
            "id": "daylight_coeff",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "rad_parameters": {} // radiance gridbased parameters json file
            }
        """
        sky_mtx = SkyMatrix.from_json(rec_json["sky_mtx"])
        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])
        rad_parameters = RfluxmtxParameters.from_json(rec_json["rad_parameters"])
        simulation_type = rec_json["simulation_type"]

        return cls(sky_mtx=sky_mtx, analysis_grids=analysis_grids,
                   radiance_parameters=rad_parameters, hb_objects=hb_objects,
                   simulation_type=simulation_type)

    @classmethod
    def from_weather_file_points_and_vectors(
        cls, epw_file, point_groups, vector_groups=None, sky_density=1,
            simulation_type=0, radiance_parameters=None, reuse_daylight_mtx=True,
            hb_objects=None,
            sub_folder="gridbased_daylightcoeff"):
        """Create grid based daylight coefficient from weather file, points and vectors.

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
        sky_mtx = SkyMatrix.from_epw_file(epw_file, sky_density)
        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)

        return cls(sky_mtx, analysis_grids, simulation_type, radiance_parameters,
                   reuse_daylight_mtx, hb_objects, sub_folder)

    @classmethod
    def from_points_file(cls, epw_file, points_file, sky_density=1,
                         simulation_type=0, radiance_parameters=None,
                         reuse_daylight_mtx=True, hb_objects=None,
                         sub_folder="gridbased_daylightcoeff"):
        """Create grid based daylight coefficient recipe from points file."""
        try:
            with open(points_file, "rb") as inf:
                point_groups = tuple(line.split()[:3] for line in inf.readline())
                vector_groups = tuple(line.split()[3:] for line in inf.readline())
        except Exception:
            raise ValueError("Couldn't import points from {}".format(points_file))

        return cls.from_weather_file_points_and_vectors(
            epw_file, point_groups, vector_groups, sky_density, simulation_type,
            radiance_parameters, reuse_daylight_mtx, hb_objects, sub_folder)

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

        if self._simType < 2:
            self.radiance_parameters.irradiance_calc = True
        else:
            self.radiance_parameters.irradiance_calc = None

        if hasattr(self, 'view_mtx_parameters'):
            if self._simType < 2:
                self.view_mtx_parameters.irradiance_calc = True
            else:
                self.view_mtx_parameters.irradiance_calc = None

        if hasattr(self, 'daylight_mtx_parameters'):
            if self._simType < 2:
                self.daylight_mtx_parameters.irradiance_calc = True
            else:
                self.daylight_mtx_parameters.irradiance_calc = None

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
    def radiance_parameters(self):
        """Radiance parameters for annual analysis."""
        return self._radiance_parameters

    @radiance_parameters.setter
    def radiance_parameters(self, par):
        if not par:
            # set RfluxmtxParameters as default radiance parameter for annual analysis
            par = get_radiance_parameters_grid_based(0, 1).dmtx

        assert hasattr(par, 'isRfluxmtxParameters'), \
            TypeError('Expected RfluxmtxParameters not {}'.format(type(par)))

        self._radiance_parameters = par

    @property
    def sky_density(self):
        """Radiance sky type e.g. r1, r2, r4."""
        return "r{}".format(self.sky_matrix.sky_density)

    @property
    def total_runs_count(self):
        """Number of total runs for all window groups and states."""
        return sum(wg.state_count for wg in self.window_groups) + 1  # 1 for base case

    def preproc_commands(self):
        """Add echo in front of comments in batch file comments."""
        cmd = [c for c in self._commands if c]
        cmd = ['echo ' + c if c[:2] == '::' else c for c in cmd]
        return ['@echo off'] + cmd

    def _add_commands(self, skycommands, commands):
        """Check if the commands should be added to self._commands."""
        if self.reuse_daylight_mtx:
            if not skycommands:
                for f in self._result_files:
                    if not os.path.isfile(f):
                        self._commands.extend(commands)
                        break
            else:
                # there are changes in the sky.
                # matrices multiplication needs to be recalculated.
                self._commands.extend(commands)
        else:
            # there are changes in the sky.
            # matrices multiplication needs to be recalculated.
            self._commands.extend(commands)

    def to_json(self):
        """Create daylight coefficient JSON file
            {
            "id": "daylight_coeff",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "rad_parameters": {} // radiance gridbased parameters json file
            }
        """
        return {
            "id": "daylight_coeff",
            "type": "gridbased",
            "sky_mtx": self.sky_matrix.to_json(),
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "simulation_type": self.simulation_type,
            "rad_parameters": self.radiance_parameters.to_json()
        }

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.
            header: A boolean to include the header lines in commands.bat. header
                includes PATH and cd toFolder
        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder target_folder/project_name
        project_folder = \
            super(GenericGridBased, self).write_content(
                target_folder, project_name, False, subfolders=['tmp', 'result/matrix']
            )

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files_daylight_coeff(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )
        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene', True)

        # 0.write points
        points_file = self.write_analysis_grids(project_folder, project_name)

        # 2.write batch file
        if header:
            self._commands.append(self.header(project_folder))

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

        self._result_files.extend(
            os.path.join(project_folder, str(result)) for result in results
        )

        self._add_commands(skycommands, commands)

        if self.window_groups:
            # calculate the contribution for all window groups
            commands, results = get_commands_w_groups_daylight_coeff(
                project_name, self.sky_matrix.sky_density, project_folder,
                self.window_groups, skyfiles, inputfiles, points_file,
                self.total_point_count, self.radiance_parameters,
                self.reuse_daylight_mtx, self.total_runs_count)

            self._add_commands(skycommands, commands)
            self._result_files.extend(
                os.path.join(project_folder, str(result)) for result in results
            )

        # # 2.5 write batch file
        batch_file = os.path.join(project_folder, 'commands.bat')

        # add echo to commands and write them to file
        write_to_file(batch_file, '\n'.join(self.preproc_commands()))

        return batch_file

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysis_grids:
            ag.unload()

        # results are merged as a single file
        for rf in self._result_files:
            fn = os.path.split(rf)[-1][:-4].split("..")
            source = fn[-2]
            state = fn[-1]

            folder, name = os.path.split(rf)
            df = os.path.join(folder, 'sun..%s' % name)
            mode = 179 if self.simulation_type == 1 else 0
            start_line = 0
            for count, analysisGrid in enumerate(self.analysis_grids):
                if count:
                    start_line += len(self.analysis_grids[count - 1])

                if not os.path.exists(df):
                    print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                          .format(analysisGrid.name, source, state, rf))
                    # total value only
                    analysisGrid.set_values_from_file(
                        rf, self.sky_matrix.hoys, source, state, start_line=start_line,
                        header=True, check_point_count=False, mode=mode
                    )
                else:
                    # total and direct values
                    print(
                        '\nloading total and direct results for {} AnalysisGrid'
                        ' from {}::{}\n{}\n{}\n'.format(
                            analysisGrid.name, source, state, rf, df))

                    analysisGrid.set_coupled_values_from_file(
                        rf, df, self.sky_matrix.hoys, source, state,
                        start_line=start_line, header=True, check_point_count=False,
                        mode=mode
                    )

        return self.analysis_grids
