from _hbanalysissurface import HBAnalysisSurface
from surfaceproperties import SurfaceProperties, SurfaceState


class HBShadingSurface(HBAnalysisSurface):
    """Honeybee shading surface.

    Args:
        name: A unique string for surface name
        sortedPoints: A list of 3 points or more as tuple or list with three items
            (x, y, z). Points should be sorted. This class won't sort the points.
            If surfaces has multiple subsurfaces you can pass lists of point lists
            to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
        isNameSetByUser: If you want the name to be changed by honeybee any case
            set isNameSetByUser to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        radProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        epProperties: EnergyPlus properties for this surface. If empty default
            epProperties will be assigned to surface by Honeybee.
    """

    # TODO: Separate Zone:Detailed:Sahding
    def __init__(self, name, sortedPoints=[], isNameSetByUser=False,
                 radProperties=None, epProperties=None, states=None):
        """Init honeybee surface."""
        _surfaceType = 6
        _isTypeSetByUser = True

        states = states or ()
        HBAnalysisSurface.__init__(self, name, sortedPoints, _surfaceType,
                                   isNameSetByUser, _isTypeSetByUser)

        sp = SurfaceProperties(self.surfaceType, radProperties, epProperties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.addSurfaceState(state)

        self.__isChildSurface = True
        self.__parent = None

    # TODO: Parse EnergyPlus properties
    @classmethod
    def fromEPString(cls, EPString):
        """Init Honeybee shading from an EPString.

        Supported types are Shading:Site:Detailed, Shading:Building:Detailed,
        Shading:Zone:Detailed

        Args:
            EPString: The full EPString for an EnergyPlus shading object.
        """
        # clean input EPString - split based on comma
        _segments = EPString.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        _type = _segments[0].lower()
        name = _segments[1]

        if _type in ('shading:site:detailed', 'shading:building:detailed'):
            startItem = 4
        elif _type == "shading:zone:detailed":
            startItem = 5
        else:
            raise ValueError("%s is an invalid shading type." % _type)

        _pts = range((len(_segments) - startItem) / 3)

        # create points
        for count, i in enumerate(xrange(startItem, len(_segments), 3)):
            try:
                _pts[count] = [float(c) for c in _segments[i: i + 3]]
            except ValueError:
                raise ValueError(
                    "%s is an invalid value for points." % _segments[i: i + 3]
                )

        # create the surfaceString
        return cls(name, sortedPoints=_pts, isNameSetByUser=True)

    @property
    def isHBShadingSurface(self):
        """Return True for HBFenSurface."""
        return True

    @property
    def isChildSurface(self):
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
            # parent.addFenestrationSurface(self)
