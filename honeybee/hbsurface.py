import types


class HBAnalysisSurface(object):
    """Base class for Honeybee surface.

    Args:
        name: A unique string for surface name
        sortedPoints: A list of 3 points or more as tuple or list with three items
            (x, y, z). Points should be sorted. This class won't sort the points.
            If surfaces has multiple subsurfaces you can pass lists of point lists
            to this function (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0))).
        isNameSetByUser: If you want the name to be changed by honeybee any case
            set isNameSetByUser to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        EPProperties: EnergyPlus properties for this surface. If empty default
            EPProperties will be assigned to surface by Honeybee.
        RADProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
    """

    def __init__(self, name, sortedPoints=[], isNameSetByUser=False,
                 EPProperties=None, RADProperties=None):
        """Initialize Honeybee Surface."""
        self.name = (name, isNameSetByUser)
        """Surface name"""
        self.__pts = []
        self.points = sortedPoints
        """A list of points as tuples or lists of (x, y, z).
        Points should be sorted. This class won't sort the points.
        (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
        """
        self.EPProperties = EPProperties
        """EnergyPlus properties for this surface. If empty default
            EPProperties will be assigned to surface by Honeybee."""
        self.RADProperties = RADProperties
        """Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        """

    @property
    def name(self):
        """Retuen surface name."""
        return self.__name

    # TODO: name should be checked not to have illegal charecters for ep and radiance
    @name.setter
    def name(self, values):
        """Set name and isSetByUser property.

        Args:
            values: A name or a tuple as (name, isSetByUser)

        Usage:
            HBSrf.name = "surface_001"
            # or
            HBSrf.name = ("mySurfaceName", True)
        """
        try:
            # check if user passed a tuple
            __newName, __isNameSetByUser = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            __newName = values[0]
            __isNameSetByUser = False  # if not indicated assume it is not set by user.
        except TypeError:
            # user just passed a single value which is the name
            __newName = values
            __isNameSetByUser = False  # if not indicated assume it is not set by user.
        finally:
            # set new name
            self.__name = str(__newName)
            self.__isNameSetByUser = __isNameSetByUser

    def isNameSetByUser(self):
        """Return if name is set by user.

        If name is set by user the surface will never be named automatically.
        """
        return self.__isNameSetByUser

    @property
    def points(self):
        """Get/set points."""
        return self.__pts

    @points.setter
    def points(self, pts):
        """set points.

        Args:
            pts: A list of points as tuples or lists of (x, y, z).
            Points should be sorted. This class won't sort the points.
            (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
        """
        # The structure of points is list of lists so it can handle non-planar
        # surfaces which will have several subsurfaces. We don't check the structure
        # here so user can add points as needed. It will be checked once user wants
        # to write the surface to Radiance or EnergyPlus
        self.addPointList(pts, True)

    def addPointList(self, pts, removeCurrentPoints=False):
        """Add new list of points to surface points.

        Args:
            pts: A list of points as tuples or lists of (x, y, z).
                Points should be sorted. This class won't sort the points.
                (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
            removeCurrentPoints: Set to True to remove current points.
                (Default: False)
        """
        assert isinstance(pts, (list, tuple, types.GeneratorType)), \
            "Points should be a list or a tuple or a generator"
        if len(pts) == 0:
            return
        if removeCurrentPoints:
            self.__pts = []
        # append the new point list
        self.__pts.append(pts)

    def addPoint(self, pt, subsurfaceNumber=-1):
        """Add a single point to current surface points.

        Args:
            pt: A point as (x, y, z) e.g. (20, 20, 10)
            subsurfaceNumber: An optional input to indicate the subsurface that
            point should be added to (Default is -1)
        """
        try:
            self.__pts[subsurfaceNumber].append(pt)
        except IndexError:
            # pts is a flattened list
            self.__pts.append([pt])
        except AttributeError:
            # input is a tuple or a generator
            self.__pts[subsurfaceNumber] = list(self.__pts[subsurfaceNumber])
            self.__pts[subsurfaceNumber].append(pt)

    def getEnergyPlusMaterials(self, layerNumber=None):
        """Return list of EnergyPlus materials for this surface."""
        pass

    def getEnergyPlusDefinition(self, includeConstruction=False, includeMaterials=False):
        """Return EnergyPlus definition for this surface."""
        pass

    def getEnergyPlusConstruction(self):
        """Return surface EnergyPlus construction."""
        pass

if __name__ == "__main__":
    # create a surface
    pts = ((0, 0, 0), (10, 0, 0), (10, 10, 0))
    hbsrf = HBAnalysisSurface("001", pts)
    hbsrf.addPoint((0, 10, 0))

    # add new points as a subsurface
    pts2 = ((10, 0, 0), (20, 0, 0), (20, 10, 0), (10, 10, 0))
    hbsrf.addPointList(pts2)

    print hbsrf.points
