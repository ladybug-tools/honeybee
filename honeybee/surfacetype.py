"""Honeybee surface types (e.g. wall, roof, etc.)."""
from radiance.material.plastic import PlasticMaterial
from radiance.material.glass import GlassMaterial


class surfaceTypeBase(object):
    """Base class for surface types."""

    # define materials as static property
    # so they can be accessed without initiating the class
    typeId = -1
    """Surface type id."""
    radianceMaterial = None
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


class Wall(surfaceTypeBase):
    """Wall."""

    typeId = 0.0
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_wall", 0.50)
    """Default Radiance material."""


class UndergroundWall(surfaceTypeBase):
    """Underground wall."""

    typeId = 0.5
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_wall", 0.50)
    """Default Radiance material."""


class Roof(surfaceTypeBase):
    """Roof."""

    typeId = 1.0
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_roof", 0.80)
    """Default Radiance material."""


class UndergroundCeiling(surfaceTypeBase):
    """Underground Ceiling."""

    typeId = 1.5
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_wall", 0.5)
    """Default Radiance material."""


class Floor(surfaceTypeBase):
    """Floor."""

    typeId = 2.0
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_floor", 0.20)
    """Default Radiance material."""


class UndergroundSlab(surfaceTypeBase):
    """Underground slab.

    Any floor that is located under ground (z < 0)
    """

    typeId = 2.25
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_floor", 0.20)
    """Default Radiance material."""


class SlabOnGrade(surfaceTypeBase):
    """Slab on Grade.

    Any floor that is touching the ground. z=0
    """

    typeId = 2.5
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_floor", 0.20)
    """Default Radiance material."""


class ExposedFloor(surfaceTypeBase):
    """Exposed Floor.

    Part of the floor/slab the is cantilevered.
    """

    typeId = 2.75
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_floor", 0.20)
    """Default Radiance material."""


class Ceiling(surfaceTypeBase):
    """Ceiling."""

    typeId = 3
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_ceiling", 0.80)
    """Default Radiance material."""


class AirWall(surfaceTypeBase):
    """Air wall.

    Virtual wall to define zones inside a space. AirWalls don't exist in reality.
    """

    typeId = 4
    """Surface type id."""
    radianceMaterial = GlassMaterial.bySingleTransValue("generic_glass", 1.00)
    """Default Radiance material."""


class Window(surfaceTypeBase):
    """Window surfaces."""

    typeId = 5
    """Surface type id."""
    radianceMaterial = GlassMaterial.bySingleTransValue("generic_glass", 0.60)
    """Default Radiance material."""


class Context(surfaceTypeBase):
    """Context surfaces."""

    typeId = 6
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_shading", 0.35)
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
    def getTypeByKey(cls, key):
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
            srfType = SurfaceTypes.getTypeByKey(6)
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
    def byNormalAngleAndPoints(cls, normalAngle, points=[]):
        """Get surface type based on surface normal angle to Z axis.

        Args:
            normalAngle: Angle between surface normal and z axis in degrees.
            points: List of surface points. If not provided the base type will
                be returned.
        Returns:
            Surface type as surfaceTypeBase object.
        """
        _srfType = cls.getBaseTypeByNormalAngle(normalAngle)

        # if len(points) > 3:
        #     _srfType = cls.reEvaluateSurfaceType(_srfType, points)

        return cls._types[_srfType]

    @staticmethod
    def getBaseTypeByNormalAngle(angleToZAxis, maximumRoofAngle=30):
        """Get based type of the surface.

        This method does calculte base methods as wall,roof and floor

        Args:
            angleToZAxis: Angle between surface normal and zAxis in degrees.

        Returns:
            An integer between 0-2 0: Wall, 1: Roof, 2: Floor
        """
        if angleToZAxis < maximumRoofAngle or angleToZAxis > 360 - maximumRoofAngle:
            return 1  # roof
        elif 160 < angleToZAxis < 200:
            return 2  # floor
        else:
            return 0  # wall

    def reEvaluateSurfaceType(self, baseSurfaceType, pts):
        """Re-evaluate base type for special types."""
        if pts == []:
            return baseSurfaceType

        if baseSurfaceType == 0:
            if self.isSurfaceUnderground():
                baseSurfaceType += 0.5  # UndergroundWall

        elif baseSurfaceType == 1:
            # A roof underground will be assigned as UndergroundCeiling
            if self.isSurfaceUnderground():
                baseSurfaceType += 0.5  # UndergroundCeiling

        elif baseSurfaceType == 2:
            # floor
            if self.isSurfaceOnGround():
                baseSurfaceType += 0.5  # SlabOnGrade
            elif self.isSurfaceUnderground():
                baseSurfaceType += 0.25  # UndergroundSlab

        return baseSurfaceType

    @staticmethod
    def isSurfaceUnderground(pts):
        """Check if this surface is underground."""
        for pt in pts:
            if pt[2] > 0:
                return False
        return True

    @staticmethod
    def isSurfaceOnGround(pts):
        """Check if this surface is on the ground."""
        for pt in pts:
            if pt[2] != 0:
                return False
        return True

    def __repr__(self):
        """Return types dictionary."""
        return self._types
