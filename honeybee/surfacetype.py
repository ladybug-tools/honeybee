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
    radianceMaterial = GlassMaterial.bySingleTransValue("generic_glass", 0.65)
    """Default Radiance material."""


class Context(surfaceTypeBase):
    """Context surfaces."""

    typeId = 6
    """Surface type id."""
    radianceMaterial = PlasticMaterial.bySingleReflectValue("generic_shading", 0.35)
    """Default Radiance material."""
