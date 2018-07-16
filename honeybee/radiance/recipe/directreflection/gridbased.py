from ..solaraccess.gridbased import SolarAccessGridBased
from ...material.mirror import Mirror
from ..recipeutil import write_rad_files, write_extra_files
from ..recipedcutil import rgb_matrix_file_to_ill

from ...command.oconv import Oconv
from ...command.rcontrib import Rcontrib
from ...analysisgrid import AnalysisGrid
from ...sky.analemma import Analemma
from ....futil import write_to_file
from ....hbsurface import HBSurface

from ladybug.sunpath import Sunpath
from ladybug.location import Location

import os


class DirectReflectionGridBased(SolarAccessGridBased):
    """Direct reflection recipe.

    This recipe calculates the direct and first reflection from reflective surfaces.
    """

    def __init__(self, sun_vectors, hoys, analysis_grids, timestep=1,
                 reflective_surfaces=None, context_surfaces=None,
                 sub_folder='directreflection'):
        """
        Args:
            sun_vectors: A list of ladybug sun vectors as (x, y, z) values. Z value
                for sun vectors should be negative (coming from sun toward earth)
            hoys: A list of hours of the year for each sun vector.
            analysis_grids: List of analysis grids.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            reflective_surfaces: A list of Honeybee surfaces to be modeled as reflective
                materials (Default: None).
            context_surfaces: A list of non-reflective Honeybee surfaces (default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "directreflection")
        """
        # update materials for reflective objects and context
        reflective_surfaces = reflective_surfaces or []
        context_surfaces = context_surfaces or []

        hb_objects = self.update_reflective_surfaces(reflective_surfaces) + \
            context_surfaces

        # create honeybee objects
        SolarAccessGridBased.__init__(self, sun_vectors, hoys, analysis_grids,
                                      timestep, hb_objects, sub_folder)

        # update radiance paramters
        # set -dr to 1 to capture first reflection from mirror like surfaces.
        self._radiance_parameters.direct_sec_relays = 1

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
        raise NotImplementedError()
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
    def from_suns(cls, suns, point_groups, vector_groups=[], timestep=1,
                  reflective_surfaces=None, context_surfaces=None,
                  sub_folder='directreflection'):
        """Create direct reflection recipe from LB sun objects.

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
            reflective_surfaces: A list of Honeybee surfaces to be modeled as reflective
                materials (Default: None).
            context_surfaces: A list of non-reflective Honeybee surfaces (default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "directreflection")
        """
        # update materials for reflective objects and context
        reflective_surfaces = reflective_surfaces or []
        context_surfaces = context_surfaces or []

        hb_objects = cls.update_reflective_surfaces(reflective_surfaces) + \
            context_surfaces

        return cls.from_suns(suns, point_groups, vector_groups, timestep,
                             hb_objects, sub_folder)

    @classmethod
    def from_location_and_hoys(cls, location, hoys, point_groups, vector_groups=[],
                               timestep=1, reflective_surfaces=None,
                               context_surfaces=None, sub_folder='directreflection'):
        """Create direct reflection recipe from Location and hours of year."""
        # update materials for reflective objects and context
        reflective_surfaces = reflective_surfaces or []
        context_surfaces = context_surfaces or []

        hb_objects = cls.update_reflective_surfaces(reflective_surfaces) + \
            context_surfaces

        return cls.from_location_and_hoys(
            location, hoys, point_groups, vector_groups, timestep, hb_objects, sub_folder
        )

    @classmethod
    def from_location_and_analysis_period(
        cls, location, analysis_period, point_groups, vector_groups=None,
            reflective_surfaces=None, context_surfaces=None,
            sub_folder='directreflection'):
        """Create direct reflection recipe from Location and analysis period."""
        # update materials for reflective objects and context
        reflective_surfaces = reflective_surfaces or []
        context_surfaces = context_surfaces or []

        hb_objects = cls.update_reflective_surfaces(reflective_surfaces) + \
            context_surfaces

        return cls.from_location_and_analysis_period(
            location, analysis_period, point_groups, vector_groups,
            hb_objects, sub_folder)

    @staticmethod
    def update_reflective_surfaces(surfaces):
        """Update surface materials to reflective mirror."""
        reflective_material = Mirror('reflective_material', 1, 1, 1)
        duplicate_surfaces = [surface.duplicate() for surface in surfaces]
        for surface in duplicate_surfaces:
            # changing base material is for test and will be removed
            surface.radiance_properties.material = reflective_material
            surface.radiance_properties.black_material = reflective_material

        return duplicate_surfaces

    def write(self, target_folder, project_name='untitled', header=True,
              transpose=False):
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
            transpose: Set to True to transpose the results matrix. By defalut each
                row include the results for each point and each column is the results
                for a different timestep (default: False).

        Returns:
            True in case of success.
        """
        # 0.prepare target folder
        # create main folder target_folder/project_name
        project_folder = \
            super(SolarAccessGridBased, self).write_content(target_folder, project_name)

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
        sun_modifiers = os.path.join('.', 'sky', ann.sunlist_file)
        suns_geo = os.path.join(project_folder + '/sky', ann.analemma_file)

        # 2.1.add sun list to modifiers
        self._radiance_parameters.mod_file = sun_modifiers
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
        rct = Rcontrib('result/total..' + project_name,
                       rcontrib_parameters=self._radiance_parameters)
        rct.octree_file = str(oc.output_file)
        rct.points_file = self.relpath(points_file, project_folder)

        rmtx = rgb_matrix_file_to_ill((str(rct.output_file),),
                                      'result/total..{}.ill'.format(project_name),
                                      transpose)
        # # 4.3 write batch file
        self._commands.append(oc.to_rad_string())
        self._commands.append(rct.to_rad_string())
        self._commands.append(rmtx.to_rad_string())

        # add rcontrib for single reflection
        self._radiance_parameters.direct_sec_relays = 0
        rct2 = Rcontrib('result/sun..' + project_name,
                        rcontrib_parameters=self._radiance_parameters)
        rct2.octree_file = str(oc.output_file)
        rct2.points_file = self.relpath(points_file, project_folder)

        rmtx2 = rgb_matrix_file_to_ill((str(rct2.output_file),),
                                       'result/sun..{}.ill'.format(project_name),
                                       transpose)

        # add the last two lines to batch file.
        self._commands.append(rct2.to_rad_string())
        self._commands.append(rmtx2.to_rad_string())

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

        hours = self.hoys
        rf = self._result_files
        df = rf.replace('total..', 'sun..')
        start_line = 0
        for count, analysisGrid in enumerate(self.analysis_grids):
            if count:
                start_line += len(self.analysis_grids[count - 1])

            # TODO(): Add timestep
            analysisGrid.set_coupled_values_from_file(
                rf, df, hours, start_line=start_line,
                header=True, check_point_count=False, mode=1
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
        raise NotImplementedError()
        return {
            "id": "direct_reflection",
            "type": "gridbased",
            "location": None,
            "hoys": self.hoys,
            "surfaces": [srf.to_json() for srf in self.hb_objects],
            "analysis_grids": [ag.to_json() for ag in self.analysis_grids],
            "sun_vectors": [tuple(-1 * c for c in v) for v in self.sun_vectors]
        }
