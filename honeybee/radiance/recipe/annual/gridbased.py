"""Radiance Annual Grid-Based Analysis Recipe.

This recipe is identical to daylight coefficient recipe with the exception of how
it loads the results. This class is more memory efficient in loading the results
however it can only be used for models with no window groups.

"""
from ..daylightcoeff.gridbased import DaylightCoeffGridBased
from ...sky.skymatrix import SkyMatrix
from ...analysisgrid import AnalysisGrid
from ...parameters.rfluxmtx import RfluxmtxParameters
from ....hbsurface import HBSurface

import os


class GridBased(DaylightCoeffGridBased):
    """Grid based annual recipe based on daylight coefficient analysis recipe.

    This recipe is identical to daylight coefficient recipe with the exception of how
    it loads the results. This class is more memory efficient in loading the results
    however it can only be used for models with no window groups.

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
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased_annual").

    """

    def __init__(self, sky_mtx, analysis_grids, simulation_type=0,
                 radiance_parameters=None, reuse_daylight_mtx=True, hb_objects=None,
                 sub_folder="gridbased_annual"):
        """Create an annual recipe."""

        DaylightCoeffGridBased.__init__(
            self, sky_mtx, analysis_grids, simulation_type, radiance_parameters,
            reuse_daylight_mtx, hb_objects, sub_folder)

    @classmethod
    def from_json(cls, rec_json):
        """Create annual recipe from JSON file
            {
            "id": "annual",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "rad_parameters": {
                gridbased_parameters: string //  A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
                }
            }
        """
        sky_mtx = SkyMatrix.from_json(rec_json["sky_mtx"])
        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])
        rad_parameters = RfluxmtxParameters.from_json(rec_json["rad_parameters"])
        if 'simulation_type' in rec_json:
            simulation_type = rec_json["simulation_type"]
        else:
            simulation_type = None

        return cls(sky_mtx=sky_mtx, analysis_grids=analysis_grids,
                   radiance_parameters=rad_parameters, hb_objects=hb_objects,
                   simulation_type=simulation_type)

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
        # check for window_groups
        assert len(self.window_groups) == 0, \
            'You cannot use the annual recipe for a scene with window_groups. ' \
            'Try daylightcoeff recipe instead.'
        if self.sub_folder == "gridbased_daylightcoeff":
            self.sub_folder == "gridbased_annual"

        return super(GridBased, self).write(target_folder, project_name, header)

    def to_json(self):
        """Create annual recipe JSON file
            {
            "id": "annual",
            "type": "gridbased",
            "sky_mtx": {}, // sky matrix json file
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "simulation_type": int // value between 0-2
            "rad_parameters": {
                gridbased_parameters: string //  A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
                }
            }
        """
        return {
            "id": "annual",
            "type": "gridbased",
            "sky_mtx": self.sky_matrix.to_json(),
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "simulation_type": self.simulation_type,
            "rad_parameters": self.radiance_parameters.to_json()
        }

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
            folder, name = os.path.split(rf)
            df = os.path.join(folder, 'sun..%s' % name)
            mode = 179 if self.simulation_type == 1 else 0
            start_line = 0
            for count, analysisGrid in enumerate(self.analysis_grids):
                if count:
                    start_line += len(self.analysis_grids[count - 1])

                if not os.path.exists(df):
                    print('\nAdding {} to result files for {}\n'
                          .format(rf, analysisGrid.name))
                    # total value only
                    analysisGrid.add_result_files(
                        rf, self.sky_matrix.hoys, start_line, False, header=True,
                        mode=mode
                    )
                else:
                    # total and direct values
                    print('\nAdding {} and {} to result files for {}\n'
                          .format(rf, df, analysisGrid.name))

                    analysisGrid.add_result_files(
                        rf, self.sky_matrix.hoys, start_line, False, header=True,
                        mode=mode
                    )

                    analysisGrid.add_result_files(
                        df, self.sky_matrix.hoys, start_line, True, header=True,
                        mode=mode
                    )

        return self.analysis_grids
