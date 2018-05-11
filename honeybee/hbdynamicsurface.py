"""A honeybee surface with multiple states."""
from hbsurface import HBSurface


class HBDynamicSurface(HBSurface):
    """Base class for Honeybee surface.

    Attributes:
        name: A unique string for surface name
        sorted_points: A list of 3 points or more as tuple or list with three items
            (x, y, z). Points should be sorted. This class won't sort the points.
            If surfaces has multiple subsurfaces you can pass lists of point lists
            to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
        surface_type: Optional input for surface type. You can use any of the surface
            types available from surfacetype libraries or use a float number to
            indicate the type. If not indicated it will be assigned based on normal
            angle of the surface which will be calculated from surface points.
                0.0: Wall           0.5: UndergroundWall
                1.0: Roof           1.5: UndergroundCeiling
                2.0: Floor          2.25: UndergroundSlab
                2.5: SlabOnGrade    2.75: ExposedFloor
                3.0: Ceiling        4.0: AirWall
                6.0: Context
        is_name_set_by_user: If you want the name to be changed by honeybee any case
            set is_name_set_by_user to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        rad_properties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        ep_properties: EnergyPlus properties for this surface. If empty default
            ep_properties will be assigned to surface by Honeybee.
        states: A list of SurfaceStates for this dynamic surface.
    """

    @property
    def isHBDynamicSurface(self):
        """Check if the surface is HBDynamicSurface."""
        return True
