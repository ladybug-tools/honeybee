"""Radiation analysis based on Daylight Coefficient Grid-Based Analysis Recipe.

This is a slightly faster implementation for annual radiation analysis using daylight
coefficient based method. This recipe genrates -s sky and add it up with analemma.

See: https://github.com/ladybug-tools/honeybee/issues/167#issue-245745189

"""
from ..recipeutil import write_extra_files
from ..recipedcutil import write_rad_files_daylight_coeff, get_commands_radiation_sky
from ..recipedcutil import get_commands_scene_daylight_coeff
from ..recipedcutil import get_commands_w_groups_daylight_coeff
from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...sky.skymatrix import SkyMatrix
from ....futil import write_to_file

from ...analysisgrid import AnalysisGrid
from ...parameters.rfluxmtx import RfluxmtxParameters
from ....hbsurface import HBSurface

import os


class GridBased(DaylightCoeffGridBased):
    """Grid based daylight coefficient analysis recipe.

    Attributes:
        sky_mtx: A radiance SkyMatrix or SkyVector. For an SkyMatrix the analysis
            will be ran for the analysis period.
        analysis_grids: A list of Honeybee analysis grids. Daylight metrics will
            be calculated for each analysisGrid separately.
        radiance_parameters: Radiance parameters for this analysis. Parameters
            should be an instance of RfluxmtxParameters.
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "daylightcoeff").

    """

    def __init__(self, sky_mtx, analysis_grids,
                 radiance_parameters=None, reuse_daylight_mtx=True, hb_objects=None,
                 sub_folder="gridbased_radiation"):
        """Create an annual recipe."""

        simulation_type = 1

        DaylightCoeffGridBased.__init__(
            self, sky_mtx, analysis_grids, simulation_type, radiance_parameters,
            reuse_daylight_mtx, hb_objects, sub_folder)

    @classmethod
    def from_json(cls, rec_json):
        """Create radiation recipe from JSON file
            {
            "id": "radiation",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "rad_parameters": {} // radiance gridbased parameters json file
            }
        """
        sky_mtx = SkyMatrix.from_json(rec_json["sky_mtx"])
        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])

        rad_parameters = RfluxmtxParameters.from_json(rec_json["rad_parameters"])

        return cls(sky_mtx=sky_mtx, analysis_grids=analysis_grids, \
                radiance_parameters=rad_parameters, hb_objects=hb_objects)

    @classmethod
    def from_weather_file_points_and_vectors(
        cls, epw_file, point_groups, vector_groups=None, sky_density=1,
            radiance_parameters=None, reuse_daylight_mtx=True, hb_objects=None,
            sub_folder="gridbased_radiation"):
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

        return cls(sky_mtx, analysis_grids, radiance_parameters,
                   reuse_daylight_mtx, hb_objects, sub_folder)

    @classmethod
    def from_points_file(cls, epw_file, points_file, sky_density=1,
                         radiance_parameters=None, reuse_daylight_mtx=True,
                         hb_objects=None, sub_folder="gridbased_radiation"):
        """Create grid based daylight coefficient recipe from points file."""
        try:
            with open(points_file, "rb") as inf:
                point_groups = tuple(line.split()[:3] for line in inf.readline())
                vector_groups = tuple(line.split()[3:] for line in inf.readline())
        except Exception:
            raise ValueError("Couldn't import points from {}".format(points_file))

        return cls.from_weather_file_points_and_vectors(
            epw_file, point_groups, vector_groups, sky_density,
            radiance_parameters, reuse_daylight_mtx, hb_objects, sub_folder)

    def to_json(self):
        """Create radiation recipe JSON file
            {
            "id": "radiation",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "rad_parameters": {} // radiance gridbased parameters json file
            }
        """
        return {
                "id": "radiation",
                "type": "gridbased",
                "sky_mtx": self.sky_matrix.to_json(),
                "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
                "surfaces": [srf.to_json() for srf in self.hb_objects],
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
            super(DaylightCoeffGridBased, self).write_content(
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
        skycommands, skyfiles = get_commands_radiation_sky(
            project_folder, self.sky_matrix, reuse=True)

        self._commands.extend(skycommands)

        # for each window group - calculate total, direct and direct-analemma results
        # calculate the contribution of glazing if any with all window groups blacked
        inputfiles = opqfiles, glzfiles, wgsfiles, extrafiles
        commands, results = get_commands_scene_daylight_coeff(
            project_name, self.sky_matrix.sky_density, project_folder, skyfiles,
            inputfiles, points_file, self.total_point_count, self.radiance_parameters,
            self.reuse_daylight_mtx, self.total_runs_count, radiation_only=True)

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
                self.reuse_daylight_mtx, self.total_runs_count, radiation_only=True)

            self._add_commands(skycommands, commands)
            self._result_files.extend(
                os.path.join(project_folder, str(result)) for result in results
            )

        # # 2.5 write batch file
        batch_file = os.path.join(project_folder, 'commands.bat')

        # add echo to commands and write them to file
        write_to_file(batch_file, '\n'.join(self.preproc_commands()))

        return batch_file
