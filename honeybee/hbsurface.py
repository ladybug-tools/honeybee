from _hbanalysissurface import HBAnalysisSurface
import os


class HBSurface(HBAnalysisSurface):
    """Base class for Honeybee surface.

    Args:
        name: A unique string for surface name
        sortedPoints: A list of 3 points or more as tuple or list with three items
            (x, y, z). Points should be sorted. This class won't sort the points.
            If surfaces has multiple subsurfaces you can pass lists of point lists
            to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
        surfaceType: Optional input for surface type. You can use any of the surface
            types available from surfacetype libraries or use a float number to
            indicate the type. If not indicated it will be assigned based on normal
            angle of the surface which will be calculated from surface points.
                0.0: Wall           0.5: UndergroundWall
                1.0: Roof           1.5: UndergroundCeiling
                2.0: Floor          2.25: UndergroundSlab
                2.5: SlabOnGrade    2.75: ExposedFloor
                3.0: Ceiling        4.0: AirWall
                6.0: Context
        isNameSetByUser: If you want the name to be changed by honeybee any case
            set isNameSetByUser to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        radProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        epProperties: EnergyPlus properties for this surface. If empty default
            epProperties will be assigned to surface by Honeybee.

    Usage:

        pts = ((0, 0, 0), (10, 0, 0), (0, 0, 10))
        hbsrf = HBSurface("001", pts, surfaceType=None, isNameSetByUser=True,
                          isTypeSetByUser=True)

        print hbsrf.toRadString(includeMaterials=True)

        > void plastic generic_wall
        > 0
        > 0
        > 5 0.500 0.500 0.500 0.000 0.000
        > generic_wall polygon 001
        > 0
        > 0
        > 9
        > 0 0 0
        > 10 0 0
        > 0 10 10
    """

    __parent = None
    __childSurfaces = []

    def __init__(self, name, sortedPoints=[], surfaceType=None,
                 isNameSetByUser=False, isTypeSetByUser=False,
                 radProperties=None, epProperties=None):
        """Init honeybee surface."""
        HBAnalysisSurface.__init__(self, name, sortedPoints=sortedPoints,
                                   surfaceType=surfaceType,
                                   isNameSetByUser=isNameSetByUser,
                                   isTypeSetByUser=isTypeSetByUser,
                                   radProperties=radProperties,
                                   epProperties=epProperties)

    @property
    def isHBSurface(self):
        """Return True for HBSurface."""
        return True

    @property
    def isChildSurface(self):
        """Return False for HBSurface."""
        return False

    @property
    def hasChildSurfaces(self):
        """Return True if Honeybee surface has Fenestration surrfaces."""
        return len(self.__childSurfaces) != 0

    @property
    def parent(self):
        """Get or set parent zone."""
        return self.__parent

    @parent.setter
    def parent(self, parent):
        """Set parent zone."""
        if hasattr(parent, 'isHBZone'):
            self.__parent = parent

    @property
    def childrenSurfaces(self):
        """Get children surfaces."""
        return self.__childSurfaces

    def addFenestrationSurface(self, fenestrationSurface):
        """Add a fenestration surface to HB surface."""
        assert hasattr(fenestrationSurface, 'isHBFenSurface'), \
            '{} is not a HBFenSurfaces'.format(type(fenestrationSurface))
        self.__childSurfaces.append(fenestrationSurface)

    def toRadString(self, includeMaterials=False,
                    includeChildrenSurfaces=True):
        """Return Radiance definition for this surface as a string."""
        surfaceString = [
            super(HBSurface, self).toRadString(includeMaterials)
        ]

        if len(self.childrenSurfaces) > 1:
            print "Honeybee currently supports one fenestration for each face."

        if includeChildrenSurfaces and self.hasChildSurfaces:
            surfaceString.append(
                self.childrenSurfaces[0].toRadString(includeMaterials)
            )

        return "\n".join(surfaceString)

    def radStringToFile(self, filePath, includeMaterials=False,
                        includeChildrenSurfaces=True):
        """Write Radiance definition for this surface to a file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/geo.rad)

        Returns:
            True in case of success. False in case of failure.
        """
        assert os.path.isdir(os.path.split(filePath)[0]), \
            "Cannot find %s." % os.path.split(filePath)[0]

        with open(filePath, "w") as outf:
            try:
                outf.write(self.toRadString(includeMaterials,
                                            includeChildrenSurfaces))
                return True
            except Exception as e:
                print "Failed to write %s to file:\n%s" % (self.name, e)
                return False
