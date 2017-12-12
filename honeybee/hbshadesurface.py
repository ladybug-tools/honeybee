from _hbanalysissurface import HBAnalysisSurface
from surfaceproperties import SurfaceProperties, SurfaceState


class HBShadingSurface(HBAnalysisSurface):
    """Honeybee shading surface.

    Args:
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
    """

    # TODO: Separate Zone:Detailed:Sahding
    def __init__(self, name, sorted_points=[], is_name_set_by_user=False,
                 rad_properties=None, ep_properties=None, states=None):
        """Init honeybee surface."""
        _surface_type = 6
        _is_type_set_by_user = True

        states = states or ()
        HBAnalysisSurface.__init__(self, name, sorted_points, _surface_type,
                                   is_name_set_by_user, _is_type_set_by_user)

        sp = SurfaceProperties(self.surface_type, rad_properties, ep_properties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.add_surface_state(state)

        self.__isChildSurface = True
        self.__parent = None

    # TODO: Parse EnergyPlus properties
    @classmethod
    def from_ep_string(cls, ep_string):
        """Init Honeybee shading from an ep_string.

        Supported types are Shading:Site:Detailed, Shading:Building:Detailed,
        Shading:Zone:Detailed

        Args:
            ep_string: The full ep_string for an EnergyPlus shading object.
        """
        # clean input ep_string - split based on comma
        _segments = ep_string.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        _type = _segments[0].lower()
        name = _segments[1]

        if _type in ('shading:site:detailed', 'shading:building:detailed'):
            start_item = 4
        elif _type == "shading:zone:detailed":
            start_item = 5
        else:
            raise ValueError("%s is an invalid shading type." % _type)

        _pts = range((len(_segments) - start_item) / 3)

        # create points
        for count, i in enumerate(xrange(start_item, len(_segments), 3)):
            try:
                _pts[count] = [float(c) for c in _segments[i: i + 3]]
            except ValueError:
                raise ValueError(
                    "%s is an invalid value for points." % _segments[i: i + 3]
                )

        # create the surfaceString
        return cls(name, sorted_points=_pts, is_name_set_by_user=True)

    @property
    def isHBShadingSurface(self):
        """Return True for HBFenSurface."""
        return True

    @property
    def is_child_surface(self):
        """Return True if Honeybee surface is Fenestration Surface."""
        return self.__isChildSurface

    @property
    def parent(self):
        """Get or set parent zone."""
        return self.__parent

    @parent.setter
    def parent(self, parent):
        """Set parent zone."""
        if hasattr(parent, 'isHBSurface'):
            self.__parent = parent
            # parent.add_fenestration_surface(self)
