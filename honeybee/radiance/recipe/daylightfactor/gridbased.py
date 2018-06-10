"""Radiance Grid-based Analysis Recipe."""
from ..pointintime.gridbased import GridBased as PITGridBased
from ...sky.certainIlluminance import CertainIlluminanceLevel
from ...parameters.rtrace import RtraceParameters
from ...analysisgrid import AnalysisGrid
from ladybug.dt import DateTime
from ladybug.legendparameters import LegendParameters
from ....hbsurface import HBSurface


class GridBased(PITGridBased):
    """Daylight factor grid based analysis.

    Attributes:
        analysis_grids: List of analysis grids.
        rad_parameters: Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "daylightfactor")

    """
    SKYILLUM = 100000

    def __init__(self, analysis_grids, rad_parameters=None, hb_objects=None,
                 sub_folder="daylightfactor"):
        """Create grid-based recipe."""
        # create the sky for daylight factor
        sky = CertainIlluminanceLevel(self.SKYILLUM)
        # simulation type is Illuminance
        simulation_type = 0

        PITGridBased.__init__(
            self, sky, analysis_grids, simulation_type, rad_parameters, hb_objects,
            sub_folder)

    @classmethod
    def from_json(cls, rec_json):
        """Create Daylight Factor recipe from json.
            {
            "id": "daylight_factor",
            "type": "gridbased",
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "rad_parameters": {
                gridbased_parameters: string //  A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
                },
            }
        """
        analysis_grids = tuple(AnalysisGrid.from_json(ag)
                               for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])
        rad_parameters = RtraceParameters.from_json(rec_json["rad_parameters"])

        recipe = cls(analysis_grids=analysis_grids, rad_parameters=rad_parameters,
                     hb_objects=hb_objects)

        return recipe

    @classmethod
    def from_points_and_vectors(
        cls, point_groups, vector_groups=None, rad_parameters=None, hb_objects=None,
            sub_folder="gridbased"):
        """Create grid based recipe from points and vectors.

        Args:
            point_groups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            rad_parameters: Radiance parameters for grid based analysis (rtrace).
                (Default: gridbased.LowQuality)
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")
        """
        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(analysis_grids, rad_parameters, hb_objects, sub_folder)

    def to_json(self):
        """Convert Daylight Factor recipe to json.
            {
            "id": "daylight_factor",
            "type": "gridbased",
            "analysis_grids": [], // list of analysis grids
            "surfaces": [], // list of honeybee surfaces
            "rad_parameters": {
                gridbased_parameters: tring //  A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
                },
            }
        """
        return {
            "id": "daylight_factor",
            "type": "gridbased",
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "rad_parameters": self.radiance_parameters.to_json()
        }

    @property
    def legend_parameters(self):
        """Legend parameters for daylight factor analysis."""
        return LegendParameters([0, 100])

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysis_grids:
            ag.unload()

        sky = self.sky
        dt = DateTime(sky.month, sky.day, int(sky.hour),
                      int(60 * (sky.hour - int(sky.hour))))

        # all the results will be divided by this value to calculated the percentage
        div = self.SKYILLUM / 100.0

        rf = self._result_files
        start_line = 0
        for count, analysisGrid in enumerate(self.analysis_grids):
            if count:
                start_line += len(self.analysis_grids[count - 1])

            analysisGrid.set_values_from_file(
                rf, (int(dt.hoy),), start_line=start_line, header=False, mode=div
            )

        return self.analysis_grids

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s: Daylight Factor\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             self.analysis_grid_count,
             self.total_point_count)
