"""Radiance window group."""

from .hbdynamicsurface import HBDynamicSurface


class WindowGroup(HBDynamicSurface):
    """Honeybee window group.

    A window group is a single or list of Honeybee surfaces with the same normal
    direction. Window groups are normally dynamic and have serveral states. It's
    a subclass of HBDynamicSurface which can only be of type of glass.

    Window groups are mainly useful for radiance daylight simulation.

    Attributes:
        name: A unique string for surface name
        sorted_points: A list of 3 points or more as tuple or list with three items
            (x, y, z). Points should be sorted. This class won't sort the points.
            If surfaces has multiple subsurfaces you can pass lists of point lists
            to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
        is_name_set_by_user: If you want the name to be changed by honeybee any case
            set is_name_set_by_user to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        rad_properties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        ep_properties: EnergyPlus properties for this surface. If empty default
            ep_properties will be assigned to surface by Honeybee.
        states: A list of SurfaceStates for this dynamic surface.
    """

    def __init__(self, name, sorted_points, is_name_set_by_user=False,
                 is_type_set_by_user=False, states=None):
        """Honeybee window group.

        A window group is a single or list of Honeybee surfaces with the same normal
        direction. Window groups are normally dynamic and have serveral states.

        Args:
            name: A unique string for surface name
            sorted_points: A list of 3 points or more as tuple or list with three items
                (x, y, z). Points should be sorted. This class won't sort the points.
                If surfaces has multiple subsurfaces you can pass lists of point lists
                to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
            is_name_set_by_user: If you want the name to be changed by honeybee any case
                set is_name_set_by_user to True. Default is set to False which let
                Honeybee to rename the surface in cases like creating a newHBZone.
            rad_properties: Radiance properties for this surface. If empty default
                RADProperties will be assigned to surface by Honeybee.
            ep_properties: EnergyPlus properties for this surface. If empty default
                ep_properties will be assigned to surface by Honeybee.
            states: A list of SurfaceStates for this dynamic surface.
        """
        # surface type is always 5
        surface_type = 5  # window
        super(WindowGroup, self).__init__(name, sorted_points, surface_type,
                                          is_name_set_by_user,
                                          is_type_set_by_user, states)
        self.check_normals()

    @classmethod
    def from_json(cls, srf_json):
        """Create a surface from json object.

        The minimum schema is:
        {"name": "",
        "vertices": [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]]
        }
        """
        srf_json["surface_type"] = 5
        _cls = super(WindowGroup, cls).from_json(srf_json)
        _cls.check_normals()
        return _cls

    @classmethod
    def from_geometry(cls, name, geometry, is_name_set_by_user=False,
                      is_type_set_by_user=False, rad_properties=None,
                      ep_properties=None, states=None):
        """Honeybee window group.

        A window group is a single or list of Honeybee surfaces with the same normal
        direction. Window groups are normally dynamic and have serveral states.

        Args:
            name: A unique string for surface name.
            geometry: Input geometry.
            is_name_set_by_user: If you want the name to be changed by honeybee any case
                set is_name_set_by_user to True. Default is set to False which let
                Honeybee to rename the surface in cases like creating a newHBZone.
            rad_properties: Radiance properties for this surface. If empty default
                RADProperties will be assigned to surface by Honeybee.
            ep_properties: EnergyPlus properties for this surface. If empty default
                ep_properties will be assigned to surface by Honeybee.
            states: A list of SurfaceStates for this dynamic surface.
        """
        surface_type = 5  # window
        group = True
        _cls = super(WindowGroup, cls).from_geometry(
            name, geometry, surface_type, is_name_set_by_user, is_type_set_by_user,
            rad_properties, ep_properties, states, group)
        _cls.check_normals()
        return _cls

    def check_normals(self):
        """Check the normal direction of the surfaces to match."""
        # check the normals and ensure they are all facing the same direction in case
        # bsdf matrial is used.
        max_angle = self.normals_angle_difference
        if max_angle < 1:
            return

        for count, state in enumerate(self.states):
            self.state = count
            if self.has_bsdf_radiance_material:
                raise ValueError(
                    'Normal direction of all surfaces in WindowGroup should face'
                    'the same direction. Current angle difference: {}'.format(
                        self.normals_angle_difference))
        self.state = 0

    def isWindowGroup(self):
        """Return True for WindowGroup."""
        return True
