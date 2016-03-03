import types
from radiance.properties import RadianceProperties
from radiance.geometry import polygon
import surfacetype
import geometryoperation as go


class HBAnalysisSurface(object):
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
                5.0: Window         6.0: Context
        isNameSetByUser: If you want the name to be changed by honeybee any case
            set isNameSetByUser to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        radProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        epProperties: EnergyPlus properties for this surface. If empty default
            epProperties will be assigned to surface by Honeybee.
    """

    def __init__(self, name, sortedPoints=[], surfaceType=None,
                 isNameSetByUser=False, isTypeSetByUser=False,
                 radProperties=None, epProperties=None):
        """Initialize Honeybee Surface."""
        self.name = (name, isNameSetByUser)
        """Surface name."""
        self.points = sortedPoints
        """A list of points as tuples or lists of (x, y, z).
        Points should be sorted. This class won't sort the points.
        (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
        """
        self.surfaceType = (surfaceType, isTypeSetByUser)
        """Surface type."""
        self.epProperties = epProperties
        """EnergyPlus properties for this surface. If empty default
            EPProperties will be assigned to surface by Honeybee."""
        self.radProperties = radProperties
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
            if type(values) is str:
                raise TypeError
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

        If name is set by user the surface will never be renamed automatically.
        """
        return self.__isNameSetByUser

    @property
    def surfaceType(self):
        """Get and set Surface Type."""
        return self.__surfaceType

    @surfaceType.setter
    def surfaceType(self, values):
        # let's assume values in surfaceType and Boolean
        __surfaceType, __isTypeSetByUser = values

        # Now let's check the input for surface type
        if __surfaceType is not None:
            # it is either a number or already a valid type
            if isinstance(__surfaceType, surfacetype.surfaceTypeBase):
                self.__surfaceType = __surfaceType
            else:
                # it should be a key value
                self.__surfaceType = \
                    surfacetype.SurfaceTypes.getTypeByKey(__surfaceType)
        else:
            # try to figure it out based on points
            if self.points == []:
                # unless user add the points we can't find the type
                self.__surfaceType = None
            else:
                self.__surfaceType = self.__surfaceTypeFromPoints()
                __isTypeSetByUser = False

        self.__isTypeSetByUser = __isTypeSetByUser

    def __surfaceTypeFromPoints(self):
        # calculate normal of the surface by surface points
        __surfaceNormal = go.calculateNormalFromPoints(self.points[0])
        __angleToZAxis = go.calculateVectorAngleToZAxis(__surfaceNormal)
        return surfacetype.SurfaceTypes.byNormalAngleAndPoints(__angleToZAxis, self.points[0])

    @property
    def isTypeSetByUser(self):
        """Check if the type for surface is set by user."""
        return self.__isTypeSetByUser

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

        try:
            if not self.isTypeSetByUser:
                # re-evalute type based on points if it's not set by user
                self.__surfaceType = self.__surfaceTypeFromPoints()
        except AttributeError:
            # Initiating the object.
            pass

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

    @property
    def radProperties(self):
        """Get and set Radiance properties."""
        return self.__radProperties

    @radProperties.setter
    def radProperties(self, radProperties):
        if radProperties is None:
            self.__radProperties = RadianceProperties()
        else:
            assert isinstance(radProperties, RadianceProperties), \
                "%s is not a valid RadianceProperties" % str(radProperties)
            self.__radProperties = radProperties

    @property
    def radianceMaterial(self):
        """Get and set Radiance material.

        When you set Radiance material you can pass a Boolean to determine if the
        Radiance material is set by user or is based on surface type.

        Usage:
            radianceMaterial = PlasticMaterial.bySingleReflectValue("wall_material", 0.55)
            HBSrf.radianceMaterial = (radianceMaterial, True)
            # or
            HBSrf.radianceMaterial = radianceMaterial
        """
        if self.radProperties.radianceMaterial is None:
            if self.surfaceType is not None:
                # set the material based on type
                self.radProperties.radianceMaterial = \
                    self.surfaceType.radianceMaterial

        return self.radProperties.radianceMaterial

    @radianceMaterial.setter
    def radianceMaterial(self, values):
        self.radProperties.radianceMaterial = values

    # TODO: Add support for multiple point list in one surface
    # I just need to iterate through the point list
    def toRadString(self, includeMaterials=False):
        """Return Radiance definition for this surface as a string."""
        __pgString = polygon(name=self.name,
                             materialName=self.radianceMaterial.name,
                             pts=self.points[0])

        return "%s\n%s" % (self.radianceMaterial, __pgString) if includeMaterials \
            else __pgString

    @property
    def epProperties(self):
        """Get and set EnergyPlus properties."""
        return self.__epProperties

    @epProperties.setter
    def epProperties(self, epProperties):
        if epProperties is None:
            pass
        else:
            raise NotImplementedError

    @property
    def energyPlusMaterials(self):
        """Return list of EnergyPlus materials for this surface."""
        raise NotImplementedError
        # self.epProperties.energyPlusMaterials

    @property
    def energyPlusConstruction(self):
        """Return surface EnergyPlus construction."""
        raise NotImplementedError
        # self.epProperties.energyPlusMaterials

    def toEPString(self, includeConstruction=False, includeMaterials=False):
        """Return EnergyPlus definition for this surface."""
        raise NotImplementedError

if __name__ == "__main__":
    # create a surface
    pts = ((0, 0, 0), (10, 0, 0), (0, 0, 10))
    hbsrf = HBAnalysisSurface("001", pts, surfaceType=None, isNameSetByUser=True, isTypeSetByUser=True)
    hbsrf.addPoint((0, 10, 0))
    print hbsrf.name
    print hbsrf.isNameSetByUser()
    # add new points as a subsurface
    # pts2 = ((10, 0, 0), (20, 0, 0), (20, 10, 0), (10, 10, 0))
    # hbsrf.addPointList(pts2)
    print hbsrf.radianceMaterial.toRadString(minimal=True)
    print
    print hbsrf.toRadString(includeMaterials=False)
    print
    print hbsrf.toRadString(includeMaterials=True)
