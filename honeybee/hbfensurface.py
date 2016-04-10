from _hbanalysissurface import HBAnalysisSurface


class HBFenSurface(HBAnalysisSurface):
    """Honeybee fenestration surface.

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

    Usage:

        from honeybee.hbsurface import HBSurface
        from honeybee.hbfensurface import HBFenSurface

        # create a surface
        pts = [(0, 0, 0), (10, 0, 0), (0, 0, 10)]
        hbsrf = HBSurface("001", pts, surfaceType=None, isNameSetByUser=True)

        glzpts = [(1, 0, 1), (8, 0, 1), (1, 0, 8)]
        glzsrf = HBFenSurface("glz_001", glzpts)

        # add fenestration surface to hb surface
        hbsrf.addFenestrationSurface(glzsrf)

        # get full definiion of the surface including the fenestration
        print hbsrf.toRadString(includeMaterials=True,
                                includeChildrenSurfaces=True)

        # save the definiion to a .rad file
        hbsrf.radStringToFile(r"c:/ladybug/triangle.rad", True, True)
    """

    __isChildSurface = True
    __parent = None

    def __init__(self, name, sortedPoints=[], isNameSetByUser=False,
                 isTypeSetByUser=False, radProperties=None, epProperties=None):
        """Init honeybee surface."""
        _surfaceType = 5

        HBAnalysisSurface.__init__(self, name, sortedPoints=sortedPoints,
                                   surfaceType=_surfaceType,
                                   isNameSetByUser=isNameSetByUser,
                                   isTypeSetByUser=isTypeSetByUser,
                                   radProperties=radProperties,
                                   epProperties=epProperties)

    @property
    def isHBFenSurface(self):
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
