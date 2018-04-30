"""Honeybee surface types (e.g. wall, roof, etc.)."""
from radiance.material.plastic import Plastic
from radiance.material.glass import Glass


class SurfaceTypeBase(object):
    """Base class for surface types."""

    # define materials as static property
    # so they can be accessed without initiating the class
    typeId = -1
    """Surface type id."""
    radiance_material = None
    """Default Radiance material."""
    energyPlusConstruction = None
    """Default EnergyPlus Construction."""

    def isSurfaceType(self):
        """Return True for surface types."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Return class name."""
        return "Surface Type: %s" % (self.__class__.__name__)


class Wall(SurfaceTypeBase):
    """Wall."""

    typeId = 0.0
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_wall", 0.50)
    """Default Radiance material."""


class UndergroundWall(SurfaceTypeBase):
    """Underground wall."""

    typeId = 0.5
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_wall", 0.50)
    """Default Radiance material."""


class Roof(SurfaceTypeBase):
    """Roof."""

    typeId = 1.0
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_roof", 0.80)
    """Default Radiance material."""


class UndergroundCeiling(SurfaceTypeBase):
    """Underground Ceiling."""

    typeId = 1.5
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_wall", 0.5)
    """Default Radiance material."""


class Floor(SurfaceTypeBase):
    """Floor."""

    typeId = 2.0
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_floor", 0.20)
    """Default Radiance material."""


class UndergroundSlab(SurfaceTypeBase):
    """Underground slab.

    Any floor that is located under ground (z < 0)
    """

    typeId = 2.25
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_floor", 0.20)
    """Default Radiance material."""


class SlabOnGrade(SurfaceTypeBase):
    """Slab on Grade.

    Any floor that is touching the ground. z=0
    """

    typeId = 2.5
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_floor", 0.20)
    """Default Radiance material."""


class ExposedFloor(SurfaceTypeBase):
    """Exposed Floor.

    Part of the floor/slab the is cantilevered.
    """

    typeId = 2.75
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_floor", 0.20)
    """Default Radiance material."""


class Ceiling(SurfaceTypeBase):
    """Ceiling."""

    typeId = 3
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_ceiling", 0.80)
    """Default Radiance material."""


class AirWall(SurfaceTypeBase):
    """Air wall.

    Virtual wall to define zones inside a space. AirWalls don't exist in reality.
    """

    typeId = 4
    """Surface type id."""
    radiance_material = Glass.by_single_trans_value("generic_glass", 1.00)
    """Default Radiance material."""


class Window(SurfaceTypeBase):
    """Window surfaces."""

    typeId = 5
    """Surface type id."""
    radiance_material = Glass.by_single_trans_value("generic_glass", 0.60)
    """Default Radiance material."""


class Context(SurfaceTypeBase):
    """Context surfaces."""

    typeId = 6
    """Surface type id."""
    radiance_material = Plastic.by_single_reflect_value("generic_shading", 0.35)
    """Default Radiance material."""


class SurfaceTypes(object):
    """Collection of surface types.

    0.0: Wall,
    0.5: UndergroundWall,
    1.0: Roof,
    1.5: UndergroundCeiling,
    2.0: Floor,
    2.25: UndergroundSlab,
    2.5: SlabOnGrade,
    2.75: ExposedFloor,
    3.0: Ceiling,
    4.0: AirWall,
    5.0: Window,
    6.0: Context
    """

    _types = {
        0.0: Wall,
        0.5: UndergroundWall,
        1.0: Roof,
        1.5: UndergroundCeiling,
        2.0: Floor,
        2.25: UndergroundSlab,
        2.5: SlabOnGrade,
        2.75: ExposedFloor,
        3.0: Ceiling,
        4.0: AirWall,
        5.0: Window,
        6.0: Context
    }

    @classmethod
    def get_type_by_key(cls, key):
        """Return type based on key value.

        Args:
            key: 0.0: Wall, 0.5: UndergroundWall,
                1.0: Roof, 1.5: UndergroundCeiling,
                2.0: Floor, 2.25: UndergroundSlab,
                2.5: SlabOnGrade, 2.75: ExposedFloor,
                3.0: Ceiling,
                4.0: AirWall,
                5.0: Window,
                6.0: Context

        Usage:
            srf_type = SurfaceTypes.get_type_by_key(6)
        """
        if hasattr(key, 'isSurfaceType'):
            return key
        try:
            return cls._types[key]
        except KeyError as e:
            _msg = "%s is  invalid." % str(e) + \
                " Use one of the valid values: %s" % str(cls._types.keys())

            raise KeyError(_msg)

    # TODO: Add changed on boundary condition of the surface
    @classmethod
    def by_normal_angle_and_points(cls, normal_angle, points=[]):
        """Get surface type based on surface normal angle to Z axis.

        Args:
            normal_angle: Angle between surface normal and z axis in degrees.
            points: List of surface points. If not provided the base type will
                be returned.
        Returns:
            Surface type as SurfaceTypeBase object.
        """
        _srf_type = cls.get_base_type_by_normal_angle(normal_angle)

        # if len(points) > 3:
        #     _srf_type = cls.re_evaluate_surface_type(_srf_type, points)

        return cls._types[_srf_type]

    @staticmethod
    def get_base_type_by_normal_angle(angle_to_z_axis, maximum_roof_angle=30):
        """Get based type of the surface.

        This method does calculte base methods as wall,roof and floor

        Args:
            angle_to_z_axis: Angle between surface normal and z_axis in degrees.

        Returns:
            An integer between 0-2 0: Wall, 1: Roof, 2: Floor
        """
        if angle_to_z_axis < maximum_roof_angle \
                or angle_to_z_axis > 360 - maximum_roof_angle:
            return 1  # roof
        elif 160 < angle_to_z_axis < 200:
            return 2  # floor
        else:
            return 0  # wall

    def re_evaluate_surface_type(self, base_surface_type, pts):
        """Re-evaluate base type for special types."""
        if pts == []:
            return base_surface_type

        if base_surface_type == 0:
            if self.is_surface_underground():
                base_surface_type += 0.5  # UndergroundWall

        elif base_surface_type == 1:
            # A roof underground will be assigned as UndergroundCeiling
            if self.is_surface_underground():
                base_surface_type += 0.5  # UndergroundCeiling

        elif base_surface_type == 2:
            # floor
            if self.is_surface_on_ground():
                base_surface_type += 0.5  # SlabOnGrade
            elif self.is_surface_underground():
                base_surface_type += 0.25  # UndergroundSlab

        return base_surface_type

    @staticmethod
    def is_surface_underground(pts):
        """Check if this surface is underground."""
        for pt in pts:
            if pt[2] > 0:
                return False
        return True

    @staticmethod
    def is_surface_on_ground(pts):
        """Check if this surface is on the ground."""
        for pt in pts:
            if pt[2] != 0:
                return False
        return True

    def __repr__(self):
        """Return types dictionary."""
        return self._types
