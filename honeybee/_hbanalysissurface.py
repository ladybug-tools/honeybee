from abc import ABCMeta, abstractproperty
from hbobject import HBObject
from radiance.properties import RadianceProperties
from radiance.geometry import polygon
import surfacetype
import geometryoperation as go

import os
import types
import math


class HBAnalysisSurface(HBObject):
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

    __metaclass__ = ABCMeta

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
    def isHBAnalysisSurface(self):
        """Return True for HBSurface."""
        return True

    @abstractproperty
    def isChildSurface(self):
        """Return True if Honeybee surface is Fenestration Surface."""
        pass

    @abstractproperty
    def parent(self):
        """Return parent for HBAnalysisSurface.

        Parent will be a HBZone for a HBSurface, and a HBSurface for a
        HBFenSurface.
        """
        pass

    @property
    def isRelativeSystem(self):
        """Return True if coordinate system is relative."""
        if self.parent is None:
            return False
        else:
            return self.parent.isRelativeSystem

    @property
    def origin(self):
        """Get origin of the coordinate system for this surface.

        For Absolute system the value is always (0, 0, 0).
        """
        return self.parent.origin

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
    def surfaceTypes(self):
        """Return Honeybee valid surface types."""
        _surfaceTypes = {0.0: 'Wall', 0.5: 'UndergroundWall', 1.0: 'Roof',
                         1.5: 'UndergroundCeiling', 2.0: 'Floor',
                         2.25: 'UndergroundSlab', 2.5: 'SlabOnGrade',
                         2.75: 'ExposedFloor', 3.0: 'Ceiling', 4.0: 'AirWall',
                         6.0: 'Context'}

        return _surfaceTypes

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
        normal = go.calculateNormalFromPoints(self.points[0])
        __angleToZAxis = go.calculateVectorAngleToZAxis(normal)
        return surfacetype.SurfaceTypes.byNormalAngleAndPoints(__angleToZAxis, self.points[0])()

    @property
    def isTypeSetByUser(self):
        """Check if the type for surface is set by user."""
        return self.__isTypeSetByUser

    @property
    def points(self):
        """Get/set points."""
        return self.__pts

    @property
    def absolutePoints(self):
        """Return absolute coordinates of points.

        If coordinate system is absolute, self.absolutePoints will be the same
        as self.points.
        """
        if self.isRelativeSystem:
            _ptgroups = range(len(self.points))
            for count, ptGroup in enumerate(self.points):
                _ptgroups[count] = [
                    (pt[0] + self.origin[0],
                     pt[1] + self.origin[1],
                     pt[2] + self.origin[2])
                    for pt in ptGroup
                ]
            return _ptgroups
        else:
            return self.points

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
        self.__pts = []
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
        if hasattr(pts[0], '__iter__'):
            self.__pts.append(pts)
        else:
            self.__pts.append(tuple((pt.X, pt.Y, pt.Z) for pt in pts))

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
            assert hasattr(radProperties, 'isRadianceProperties'), \
                "%s is not a valid RadianceProperties" % str(radProperties)
            self.__radProperties = radProperties

    @property
    def radianceMaterials(self):
        """Get list of Radiance materials for a honeybee surface.

        For a surface with no fenestration it will be a list with a single item,
        However for a surface with fenestration it will be a list including
        the materials of fenestration surfaces.

        You may use self.radianceMaterial (with no s at the end) to only get
        material for the surface itself.
        """
        surfaceMaterial = [self.radianceMaterial]

        if not self.isChildSurface:
            for fen in self.childrenSurfaces:
                surfaceMaterial.append(fen.radianceMaterial)

        return set(surfaceMaterial)

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
    def radianceMaterial(self, value):
        self.radProperties.radianceMaterial = value

    def duplicateVertices(self):
        """Duplicate surface vertices."""
        if self.isChildSurface or not self.hasChildSurfaces:
            return self.absolutePoints
        else:
            # get points for first glass face
            __glassPoints = [childSrf.absolutePoints[0]
                             for childSrf in self.childrenSurfaces]

            __facePoints = self.absolutePoints[0]

            return AnalsysiSurfacePolyline(__facePoints, __glassPoints).polyline


    def toRadString(self, includeMaterials=False, joinOutput=True):
        """Return Radiance definition for this surface as a string."""
        # prepare points for surface.
        if self.isChildSurface or not self.hasChildSurfaces:
            __pts = self.absolutePoints
        else:

            # get points for first glass face
            __glassPoints = [childSrf.absolutePoints[0]
                             for childSrf in self.childrenSurfaces]

            __facePoints = self.absolutePoints[0]

            __pts = AnalsysiSurfacePolyline(__facePoints, __glassPoints).polyline

            __pts = [__pts]

        __numPtGroups = len(__pts)
        # create a place holder for each point group (face)
        # for a planar surface __numPtGroups is only one
        __pgStrings = range(__numPtGroups)

        for ptCount, pts in enumerate(__pts):
            # modify name for each sub_surface
            _name = self.name if __numPtGroups == 1 else self.name + "_{}".format(ptCount)

            # collect definition for each subsurface
            __pgStrings[ptCount] = polygon(
                name=_name, materialName=self.radianceMaterial.name, pts=pts
            )

        if joinOutput:
            return "%s\n%s" % (self.radianceMaterial, "\n".join(__pgStrings)) \
                if includeMaterials \
                else "\n".join(__pgStrings)
        else:
            return self.radianceMaterial.toRadString(), __pgStrings \
                if includeMaterials \
                else __pgStrings

    def radStringToFile(self, filePath, includeMaterials=False):
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
                outf.write(self.toRadString(includeMaterials))
                return True
            except Exception as e:
                print "Failed to write %s to file:\n%s" % (self.name, e)
                return False

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

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Honeybee surface."""
        return "HBSurface: %s" % self.name


class AnalsysiSurfacePolyline(object):
    """Calculate AnalysisSurfacePolyline for surface with fenestrations."""

    __slots__ = ('startIndex', '_ptListA', '_ptListB')

    def __init__(self, surfacePoints, fenPoints):
        """Init class."""
        self.startIndex = 0
        self._ptListA = []
        self._ptListB = []
        self.__calculatePolyline(surfacePoints, fenPoints)

    @property
    def polyline(self):
        """Return a list of points for the single polyline.

        This list of points includes based surface and fenestrations.
        """
        return self._ptListB[:-1] + list(reversed(self._ptListA))

    @staticmethod
    def distance(pt1, pt2):
        """calculate distance between two points."""
        return math.sqrt((pt2[0] - pt1[0])**2 +
                         (pt2[1] - pt1[1])**2 +
                         (pt2[2] - pt1[2])**2)

    def __shortestDistance(self, ptList1, ptList2):
        dist = float('inf')
        xi = None
        yi = None
        for xCount, xpt in enumerate(ptList1):
            for yCount, ypt in enumerate(ptList2):
                d = self.distance(xpt, ypt)
                if d < dist:
                    dist, xi, yi = d, xCount, yCount

        return dist, xi, yi

    def __addPoints(self, source, target):
        d, si, ti = self.__shortestDistance(source, target)
        if self.startIndex < si:
            start = self.startIndex
            end = si
            self._ptListA.extend(source[start: end + 1])
            self._ptListB.extend(reversed(source[end:] + source[:start + 1]))
        else:
            start = si
            end = self.startIndex
            self._ptListA.extend(reversed(source[start: end + 1]))
            self._ptListB.extend(source[end:] + source[:start + 1])

        self.startIndex = ti

    def __calculatePolyline(self, source, targets):
        """calculate single polyline for HBSurface with Fenestration."""
        # sort point groups
        sortedTargets = sorted(targets,
                               key=lambda target: self.__shortestDistance(source, target)[0])

        self.__addPoints(source, sortedTargets[0])

        if len(sortedTargets) > 1:
            self.__calculatePolyline(sortedTargets[0], sortedTargets[1:])
        else:
            self.__addPoints(sortedTargets[0], sortedTargets[0])
