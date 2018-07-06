"""Radiance Grid-based Analysis Recipe."""
from .._gridbasedbase import GenericGridBased
from ..recipeutil import write_rad_files, write_extra_files
from ...parameters.rtrace import LowQuality
from ...command.oconv import Oconv
from ...command.rtrace import Rtrace
from ...command.rcalc import Rcalc
from ....futil import write_to_file
from ...analysisgrid import AnalysisGrid
from ....hbsurface import HBSurface
from ...sky.cie import CIE
from ...parameters.rtrace import RtraceParameters

from ladybug.dt import DateTime

import os


class GridBased(GenericGridBased):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        analysis_grids: List of analysis grids.
        simulation_type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        rad_parameters: Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:
        # create the sky
        sky = SkyWithCertainIlluminanceLevel(2000)

        # initiate analysis_recipe
        analysis_recipe = GridBased(
            sky, testPoints, ptsVectors, simType
            )

        # add honeybee object
        analysis_recipe.hb_objects = HBObjs

        # write analysis files to local drive
        analysis_recipe.write(_folder_, _name_)

        # run the analysis
        analysis_recipe.run(debaug=False)

        # get the results
        print(analysis_recipe.results())
    """

    # TODO: implemnt isChanged at AnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, analysis_grids, simulation_type=0, rad_parameters=None,
                 hb_objects=None, sub_folder="gridbased"):
        """Create grid-based recipe."""
        GenericGridBased.__init__(
            self, analysis_grids, hb_objects, sub_folder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radiance_parameters = rad_parameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)"""

        self.simulation_type = simulation_type
        """Simulation type: 0: Illuminance(lux), 1: Radiation (wh),
           2: Luminance (Candela) (Default: 0)
        """

    @classmethod
    def from_json(cls, rec_json):
        """Create the solar access recipe from json.
        {
          "id": "point_in_time",
          "type": "gridbased",
          "sky": null, // a honeybee sky
          "surfaces": [], // list of honeybee surfaces
          "analysis_grids": [] // list of analysis grids
          // [0] illuminance(lux), [1] radiation (kwh), [2] luminance (Candela).
          "analysis_type": 0
        }
        """
        sky = CIE.from_json(rec_json['sky'])
        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json['analysis_grids'])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json['surfaces'])
        rad_parameters = RtraceParameters.from_json(rec_json["rad_parameters"])
        return cls(sky, analysis_grids, rec_json['analysis_type'], rad_parameters,
                   hb_objects)

    @classmethod
    def from_points_and_vectors(cls, sky, point_groups, vector_groups=None,
                                simulation_type=0, rad_parameters=None,
                                hb_objects=None, sub_folder="gridbased"):
        """Create grid based recipe from points and vectors.

        Args:
            sky: A honeybee sky for the analysis
            point_groups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            simulation_type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance
                (Candela) (Default: 0).
            rad_parameters: Radiance parameters for grid based analysis (rtrace).
                (Default: gridbased.LowQuality)
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")
        """
        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(sky, analysis_grids, simulation_type, rad_parameters, hb_objects,
                   sub_folder)

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
            assert self.sky.is_climate_based, \
                "The sky for radition analysis should be climate-based."

        self._simType = value
        if self.sky.is_climate_based:
            self.sky.sky_type = value

    @property
    def sky(self):
        """Get and set sky definition."""
        return self._sky

    @sky.setter
    def sky(self, new_sky):
        assert hasattr(new_sky, 'isRadianceSky'), \
            '%s is not a valid Honeybee sky.' % type(new_sky)
        assert new_sky.is_point_in_time, \
            TypeError('Sky must be one of the point-in-time skies.')
        self._sky = new_sky.duplicate()

    @property
    def radiance_parameters(self):
        """Get and set Radiance parameters."""
        return self._radiance_parameters

    @radiance_parameters.setter
    def radiance_parameters(self, rad_parameters):
        if not rad_parameters:
            rad_parameters = LowQuality()
        assert hasattr(rad_parameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(rad_parameters)
        self._radiance_parameters = rad_parameters

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <project_name.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if hb_objects
                is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if hb_objects
                is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <project_name.mat> <project_name.rad>
                <additional rad_files> > <project_name.oct>
                rtrace <radiance_parameters> <project_name.oct> > <project_name.res>
            results file <*.res>: Results file once the analysis is over.

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
            super(GenericGridBased, self).write_content(target_folder, project_name)

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )
        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene')

        # 1.write points
        points_file = self.write_analysis_grids(project_folder, project_name)

        # 2.write batch file
        if header:
            self.commands.append(self.header(project_folder))

        # 3.write sky file
        self._commands.append(self.sky.to_rad_string(folder='sky'))

        # 3.1. write ground and sky materials
        skyground = self.sky.write_sky_ground(os.path.join(project_folder, 'sky'))

        # TODO(Mostapha): add window_groups here if any!
        # # 4.1.prepare oconv
        oct_scene_files = \
            [os.path.join(project_folder, str(self.sky.command('sky').output_file)),
             skyground] + opqfiles + glzfiles + wgsfiles + extrafiles.fp

        oct_scene_files_items = []
        for f in oct_scene_files:
            if isinstance(f, (list, tuple)):
                print('Point-in-time recipes cannot currently handle dynamic window'
                      ' groups. The first state will be used for simulation.')
                oct_scene_files_items.append(f[0])
            else:
                oct_scene_files_items.append(f)
        oc = Oconv(project_name)
        oc.scene_files = tuple(self.relpath(f, project_folder)
                               for f in oct_scene_files_items)

        # # 4.2.prepare rtrace
        rt = Rtrace('result/' + project_name,
                    simulation_type=self.simulation_type,
                    radiance_parameters=self.radiance_parameters)
        rt.radiance_parameters.h = True
        rt.octree_file = str(oc.output_file)
        rt.points_file = self.relpath(points_file, project_folder)

        # # 4.3. add rcalc to convert rgb values to irradiance
        rc = Rcalc('result/{}.ill'.format(project_name), str(rt.output_file))

        if os.name == 'nt':
            rc.rcalc_parameters.expression = '"$1=(0.265*$1+0.67*$2+0.065*$3)*179"'
        else:
            rc.rcalc_parameters.expression = "'$1=(0.265*$1+0.67*$2+0.065*$3)*179'"

        # # 4.4 write batch file
        self._commands.append(oc.to_rad_string())
        self._commands.append(rt.to_rad_string())
        self._commands.append(rc.to_rad_string())

        batch_file = os.path.join(project_folder, "commands.bat")

        write_to_file(batch_file, "\n".join(self.commands))

        self._result_files = os.path.join(project_folder, str(rc.output_file))

        return batch_file

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

        rf = self._result_files
        start_line = 0
        mode = 179 if self.simulation_type == 1 else 0

        for count, analysisGrid in enumerate(self.analysis_grids):
            if count:
                start_line += len(self.analysis_grids[count - 1])

            analysisGrid.set_values_from_file(
                rf, (int(dt.hoy),), start_line=start_line, header=False, mode=mode
            )

        return self.analysis_grids

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def to_json(self):
        """Create point-in-time recipe from json.
            {
              "id": "point_in_time",
              "type": "gridbased",
              "sky": null, // a honeybee sky
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [] // list of analysis grids
              // [0] illuminance(lux), [1] radiation (kwh), [2] luminance (Candela).
              "analysis_type": 0
            }
        """
        return {
            "id": "point_in_time",
            "type": "gridbased",
            "sky": self.sky.to_json(),
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "analysis_type": self.simulation_type,
            "rad_parameters": self.radiance_parameters.to_json()
        }

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulation_type],
             self.analysis_grid_count,
             self.total_point_count)
