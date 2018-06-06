"""Radiance Solar Access Grid-based Analysis Recipe."""
from .._gridbasedbase import GenericGridBased
from ..recipeutil import write_rad_files, write_extra_files
from ..recipedcutil import rgb_matrix_file_to_ill
from ...parameters.rcontrib import RcontribParameters
from ...command.oconv import Oconv
from ...command.rcontrib import Rcontrib
from ...analysisgrid import AnalysisGrid
from ...sky.analemma import Analemma
from ....futil import write_to_file
from ....vectormath.euclid import Vector3
from ....hbsurface import HBSurface

from ladybug.sunpath import Sunpath
from ladybug.location import Location
from ladybug.legendparameters import LegendParameters
from ladybug.color import Colorset

import os


class SolarAccessGridBased(GenericGridBased):
    """Solar access recipe.

    This class calculates number of sunlight hours for a group of test points.

    Attributes:
        sun_vectors: A list of ladybug sun vectors as (x, y, z) values. Z value
            for sun vectors should be negative (coming from sun toward earth)
        hoys: A list of hours of the year for each sun vector.
        analysis_grids: List of analysis grids.
        timestep: The number of timesteps per hour for sun vectors. This number
            should be smaller than 60 and divisible by 60. The default is set to
            1 such that one sun vector is generated for each hour (Default: 1).
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "solaraccess")

    Usage:
        # initiate analysis_recipe
        analysis_recipe = SolarAccess(sun_vectors, analysis_grids)

        # add honeybee object
        analysis_recipe.hb_objects = HBObjs

        # write analysis files to local drive
        analysis_recipe.write_to_file(_folder_, _name_)

        # run the analysis
        analysis_recipe.run(debaug=False)

        # get the results
        print(analysis_recipe.results())
    """

    def __init__(self, sun_vectors, hoys, analysis_grids, timestep=1, hb_objects=None,
                 sub_folder='solaraccess'):
        """Create sunlighthours recipe."""
        GenericGridBased.__init__(
            self, analysis_grids, hb_objects, sub_folder
        )

        assert len(hoys) == len(sun_vectors), \
            ValueError(
                'Length of sun_vectors [] must be equall to '
                'the length of hoys []'.format(len(sun_vectors), len(hoys))
        )
        self.sun_vectors = sun_vectors
        self._hoys = hoys
        self.timestep = timestep

        # this is a bug! should be set under a setter method
        self._radiance_parameters = RcontribParameters()
        self._radiance_parameters.irradiance_calc = True
        self._radiance_parameters.ambient_bounces = 0
        self._radiance_parameters.direct_certainty = 1
        self._radiance_parameters.direct_threshold = 0
        self._radiance_parameters.direct_jitter = 0

    @classmethod
    def from_json(cls, rec_json):
        """Create the solar access recipe from json.
            {
              "id": "solar_access",
              "type": "gridbased",
              "location": null, // a honeybee location - see below
              "hoys": [], // list of hours of the year
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [] // list of analysis grids
              "sun_vectors": [] // list of sun vectors if location is not provided
            }
        """
        hoys = rec_json["hoys"]
        if 'sun_vectors' not in rec_json or not rec_json['sun_vectors']:
            # create sun vectors from location inputs
            loc = Location.from_json(rec_json['location'])
            sp = Sunpath.from_location(loc)
            suns = (sp.calculate_sun_from_hoy(hoy) for hoy in hoys)
            sun_vectors = tuple(s.sun_vector for s in suns if s.is_during_day)
        else:
            sun_vectors = rec_json['sun_vectors']

        analysis_grids = \
            tuple(AnalysisGrid.from_json(ag) for ag in rec_json["analysis_grids"])
        hb_objects = tuple(HBSurface.from_json(srf) for srf in rec_json["surfaces"])
        return cls(sun_vectors, hoys, analysis_grids, 1, hb_objects)

    @classmethod
    def from_points_and_vectors(cls, sun_vectors, hoys, point_groups, vector_groups=[],
                                timestep=1, hb_objects=None, sub_folder='sunlighthour'):
        """Create sunlighthours recipe from points and vectors.

        Args:
            sun_vectors: A list of ladybug sun vectors as (x, y, z) values. Z value
                for sun vectors should be negative (coming from sun toward earth)
            hoys: A list of hours of the year for each sun vector.
            point_groups: A list of (x, y, z) test points or lists of (x, y, z) test
                points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(sun_vectors, hoys, analysis_grids, timestep, hb_objects, sub_folder)

    @classmethod
    def from_suns(cls, suns, point_groups, vector_groups=[], timestep=1,
                  hb_objects=None, sub_folder='sunlighthour'):
        """Create sunlighthours recipe from LB sun objects.

        Attributes:
            suns: A list of ladybug suns.
            point_groups: A list of (x, y, z) test points or lists of (x, y, z) test
                points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        try:
            sun_vectors = tuple(s.sun_vector for s in suns if s.is_during_day)
            hoys = tuple(s.hoy for s in suns if s.is_during_day)
        except AttributeError:
            raise TypeError('The input is not a valid LBSun.')

        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(sun_vectors, hoys, analysis_grids, timestep, hb_objects, sub_folder)

    @classmethod
    def from_location_and_hoys(cls, location, hoys, point_groups, vector_groups=[],
                               timestep=1, hb_objects=None, sub_folder='sunlighthour'):
        """Create sunlighthours recipe from Location and hours of year."""
        sp = Sunpath.from_location(location)

        suns = (sp.calculate_sun_from_hoy(hoy) for hoy in hoys)

        sun_vectors = tuple(s.sun_vector for s in suns if s.is_during_day)

        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(sun_vectors, hoys, analysis_grids, timestep, hb_objects, sub_folder)

    @classmethod
    def from_location_and_analysis_period(
        cls, location, analysis_period, point_groups, vector_groups=None,
            hb_objects=None, sub_folder='sunlighthour'):
        """Create sunlighthours recipe from Location and analysis period."""
        vector_groups = vector_groups or ()

        sp = Sunpath.from_location(location)

        suns = (sp.calculate_sun_from_hoy(hoy) for hoy in analysis_period.float_hoys)

        sun_vectors = tuple(s.sun_vector for s in suns if s.is_during_day)
        hoys = tuple(s.hoy for s in suns if s.is_during_day)

        analysis_grids = cls.analysis_grids_from_points_and_vectors(point_groups,
                                                                    vector_groups)
        return cls(sun_vectors, hoys, analysis_grids, analysis_period.timestep,
                   hb_objects, sub_folder)

    @property
    def hoys(self):
        """Return list of hours of the year."""
        return self._hoys

    @property
    def sun_vectors(self):
        """A list of ladybug sun vectors as (x, y, z) values."""
        return self._sun_vectors

    @sun_vectors.setter
    def sun_vectors(self, vectors):
        try:
            self._sun_vectors = tuple(Vector3(*v).flipped() for v in vectors
                                      if v[2] < 0)
        except TypeError:
            self._sun_vectors = tuple(Vector3(v.X, v.Y, v.Z).flipped()
                                      for v in vectors if v.Z < 0)
        except IndexError:
            raise ValueError("Failed to create the sun vectors!")

        if len(self.sun_vectors) != len(vectors):
            print('%d vectors with positive z value are found and removed '
                  'from sun vectors' % (len(vectors) - len(self.sun_vectors)))

    @property
    def timestep(self):
        """An intger for the number of timesteps per hour for sun vectors.

        This number should be smaller than 60 and divisible by 60.
        """
        return self._timestep

    @timestep.setter
    def timestep(self, ts):
        try:
            self._timestep = int(ts)
        except TypeError:
            self._timestep = 1

        assert self._timestep != 0, 'ValueError: TimeStep cannot be 0.'

    @property
    def legend_parameters(self):
        """Legend parameters for solar access analysis."""
        col = Colorset.ecotect()
        return LegendParameters([0, 'max'], colors=col)

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Files for sunlight hours analysis are:
            test points <project_name.pts>: List of analysis points.
            suns file <*.sun>: list of sun sources .
            suns material file <*_suns.mat>: Radiance materials for sun sources.
            suns geometry file <*_suns.rad>: Radiance geometries for sun sources.
            material file <*.mat>: Radiance materials. Will be empty if hb_objects is
                None.
            geometry file <*.rad>: Radiance geometries. Will be empty if hb_objects is
                None.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconv [material file] [geometry file] [sun materials file] [sun
                    geometries file] > [octree file]
                rcontrib -ab 0 -ad 10000 -I -M [sunlist.txt] -dc 1 [octree file]< [pts
                    file] > [rcontrib results file]

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.

        Returns:
            True in case of success.
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
        extrafiles = write_extra_files(self.scene, project_folder + '/scene', True)

        # 1.write points
        points_file = self.write_analysis_grids(project_folder, project_name)

        # 2.write sun files
        ann = Analemma(self.sun_vectors, self.hoys)
        ann.execute(project_folder + '/sky')
        sun_modifiers = os.path.join(project_folder + '/sky', ann.sunlist_file)
        suns_geo = os.path.join(project_folder + '/sky', ann.analemma_file)

        # 2.1.add sun list to modifiers
        self._radiance_parameters.mod_file = self.relpath(sun_modifiers, project_folder)
        self._radiance_parameters.y_dimension = self.total_point_count

        # 3.write batch file
        if header:
            self._commands.append(self.header(project_folder))

        # TODO(Mostapha): add window_groups here if any!
        # # 4.1.prepare oconv
        oct_scene_files = opqfiles + glzfiles + wgsfiles + [suns_geo] + \
            extrafiles.fp

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

        # # 4.2.prepare Rcontrib
        rct = Rcontrib('result/' + project_name,
                       rcontrib_parameters=self._radiance_parameters)
        rct.octree_file = str(oc.output_file)
        rct.points_file = self.relpath(points_file, project_folder)

        batch_file = os.path.join(project_folder, "commands.bat")
        rmtx = rgb_matrix_file_to_ill((str(rct.output_file),),
                                      'result/{}.ill'.format(project_name))
        # # 4.3 write batch file
        self._commands.append(oc.to_rad_string())
        self._commands.append(rct.to_rad_string())
        self._commands.append(rmtx.to_rad_string())

        self._result_files = os.path.join(project_folder, str(rmtx.output_file))

        batch_file = os.path.join(project_folder, "commands.bat")
        return write_to_file(batch_file, '\n'.join(self.commands))

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysis_grids:
            ag.unload()

        hours = tuple(int(self.timestep * h) for h in self.hoys)
        rf = self._result_files
        start_line = 0
        for count, analysisGrid in enumerate(self.analysis_grids):
            if count:
                start_line += len(self.analysis_grids[count - 1])

            # TODO(): Add timestep
            analysisGrid.set_values_from_file(
                rf, hours, start_line=start_line, header=True, check_point_count=False,
                mode=1
            )

        return self.analysis_grids

    def to_json(self):
        """Create the solar access recipe from json.
            {
              "id": "solar_access",
              "type": "gridbased",
              "location": null, // a honeybee location - see below
              "hoys": [], // list of hours of the year
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [], // list of analysis grids
              "sun_vectors": []
            }
        """
        return {
            "id": "solar_access",
            "type": "gridbased",
            "location": None,
            "hoys": self.hoys,
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "sun_vectors": [tuple(-1 * c for c in v) for v in self.sun_vectors]
        }
