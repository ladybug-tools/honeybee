from ..solaraccess.gridbased import SolarAccessGridBased
from ...material.mirror import Mirror


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
        # set -ar to 1 to capture first reflection from mirror like surfaces.
        self._radiance_parameters.direct_sec_relays = 1

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

        for surface in surfaces:
            # changing base material is for test and will be removed
            surface.radiance_properties.material = reflective_material
            surface.radiance_properties.black_material = reflective_material

        return surfaces
