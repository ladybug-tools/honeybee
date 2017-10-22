from abc import ABCMeta, abstractproperty
import utilcol as util
from hbobject import HBObject
from surfaceproperties import SurfaceProperties, SurfaceState
import surfacetype
import geometryoperation as go
from surfacetype import Floor, Wall, Window, Ceiling
from radiance.radfile import RadFile

import os
import types
import math
import copy


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
        states: A collection of SurfaceStates. SurfaceStates includes SurfaceProperties
            which includes the data for RadianceProperties and EPProperties and optional
            HBSurfaces. Each
            item in this collection stands for a different stae of the materials. Use
            the properties to model dynamic bahaviors such as dynamic blinds.
    """

    __metaclass__ = ABCMeta
    _surfaceTypes = {0.0: 'Wall', 0.5: 'UndergroundWall', 1.0: 'Roof',
                     1.5: 'UndergroundCeiling', 2.0: 'Floor',
                     2.25: 'UndergroundSlab', 2.5: 'SlabOnGrade',
                     2.75: 'ExposedFloor', 3.0: 'Ceiling', 4.0: 'AirWall',
                     6.0: 'Context'}

    def __init__(self, name, sortedPoints, surfaceType=None, isNameSetByUser=False,
                 isTypeSetByUser=False, states=None):
        """Initialize Honeybee Surface."""
        self._childSurfaces = ()
        self._states = []
        if not name:
            name = util.randomName()
            isNameSetByUser = False
        self.name = (name, isNameSetByUser)
        """Surface name."""
        self.points = sortedPoints
        """A list of points as tuples or lists of (x, y, z).
        Points should be sorted. This class won't sort the points.
        (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
        """
        self.surfaceType = (surfaceType, isTypeSetByUser)
        """Surface type."""
        self.state = 0
        """Current state of the surface."""
        states = states or \
            (SurfaceState('default', SurfaceProperties(self.surfaceType)),)
        for state in states:
            self.addSurfaceState(state)

    @classmethod
    def fromJson(cls, srfJson):
        """Create a surface from json object.

        The minimum schema is:
        {"name": "",
        "vertices": [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]],
        "surface_type": null  // 0: wall, 5: window
        }
        """
        name = srfJson["name"]
        vertices = srfJson["vertices"]
        typeId = srfJson["surface_type"]
        srfType = surfacetype.SurfaceTypes.getTypeByKey(typeId)
        return cls(name, vertices, srfType)

    @classmethod
    def fromRadEPProperties(
        cls, name, sortedPoints, surfaceType=None, isNameSetByUser=False,
            isTypeSetByUser=False, radProperties=None, epProperties=None,
            states=None):
        """Initialize Honeybee Surface.

        RadianceProperties and EPProperties will be used to create the initial state.
        """
        states = states or ()
        # create the surface first to get the surface type if not available
        _cls = cls(name, sortedPoints, surfaceType, isNameSetByUser, isTypeSetByUser)
        # replace the default properties for the initial state
        sp = SurfaceProperties(_cls.surfaceType, radProperties, epProperties)
        _cls._states[0] = SurfaceState('default', sp)

        for state in states:
            _cls.addSurfaceState(state)

        return _cls

    @property
    def isHBAnalysisSurface(self):
        """Return True for HBSurface."""
        return True

    @property
    def isHBSurface(self):
        """Return True for HBSurfaces."""
        return False

    @property
    def isHBFenSurface(self):
        """Return True for HBFenSurfaces."""
        return False

    @property
    def isHBDynamicSurface(self):
        """Return True for HBSurfaces."""
        return False

    @abstractproperty
    def isChildSurface(self):
        """Return True if Honeybee surface is Fenestration Surface."""
        pass

    @property
    def hasChildSurfaces(self):
        """Return True if surface has children surfaces."""
        return False

    @property
    def childrenSurfaces(self):
        """Get children surfaces."""
        return self._childSurfaces

    @property
    def hasBSDFRadianceMaterial(self):
        """Return True if .xml BSDF material is assigned for radiance material."""
        return self.isHBFenSurface and hasattr(self.radianceMaterial, 'xmlfile')

    @property
    def hasRadianceGlassMaterial(self):
        """Return true if surface has radiance glass material."""
        return self.radianceMaterial.isGlassMaterial

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
    def stateCount(self):
        """Number of states for this surface."""
        return len(self.states)

    @property
    def state(self):
        """The current state id."""
        return self._state

    @state.setter
    def state(self, count):
        """The current state id."""
        if count != 0:
            assert count < self.stateCount, \
                ValueError(
                    'This surface has only {} state. {} is an invalid state.'.format(
                        self.stateCount, count
                    )
                )
        self._state = count

    @property
    def states(self):
        """List of states for this surface."""
        return self._states

    def addSurfaceState(self, srfState):
        if not srfState:
            return

        assert hasattr(srfState, 'isSurfaceState'), \
            TypeError('Expected SurfaceState not {}'.format(type(srfState)))

        self._states.append(srfState)

    @property
    def name(self):
        """Retuen surface name."""
        return self._name

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
            newName, isNameSetByUser = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            newName = values[0]
            isNameSetByUser = False  # if not indicated assume it is not set by user.
        except TypeError:
            # user just passed a single value which is the name
            newName = values
            isNameSetByUser = False  # if not indicated assume it is not set by user.
        finally:
            # set new name
            self._name = str(newName)
            self._isNameSetByUser = isNameSetByUser
            util.checkName(self._name)

    @property
    def isNameSetByUser(self):
        """Return if name is set by user.

        If name is set by user the surface will never be renamed automatically.
        """
        return self._isNameSetByUser

    @property
    def surfaceTypes(self):
        """Return Honeybee valid surface types."""
        return self._surfaceTypes

    @property
    def surfaceType(self):
        """Get and set Surface Type."""
        return self._surfaceType

    @surfaceType.setter
    def surfaceType(self, values):
        # let's assume values in surfaceType and Boolean
        _surfaceType, isTypeSetByUser = values

        # Now let's check the input for surface type
        if _surfaceType is not None:
            # it is either a number or already a valid type
            if isinstance(_surfaceType, surfacetype.surfaceTypeBase):
                self._surfaceType = _surfaceType
            else:
                try:
                    # it should be a key value
                    self._surfaceType = \
                        surfacetype.SurfaceTypes.getTypeByKey(_surfaceType)()
                except KeyError:
                    raise ValueError('%s is not a valid surface type.' % _surfaceType)
        else:
            # try to figure it out based on points
            self._surfaceType = self._surfaceTypeFromPoints()
            isTypeSetByUser = False

        self._isTypeSetByUser = isTypeSetByUser

    def _surfaceTypeFromPoints(self):
        normal = go.normalFromPoints(self.points[0])
        angleToZAxis = go.vectorAngleToZAxis(normal)
        return surfacetype.SurfaceTypes.byNormalAngleAndPoints(angleToZAxis,
                                                               self.points[0])()

    @property
    def isTypeSetByUser(self):
        """Check if the type for surface is set by user."""
        return self._isTypeSetByUser

    @property
    def isFloor(self):
        """Check if surface is a Floor."""
        return isinstance(self.surfaceType, Floor)

    @property
    def isWall(self):
        """Check if surface is a Wall."""
        return isinstance(self.surfaceType, Wall)

    @property
    def isCeiling(self):
        """Check if surface is a Ceiling."""
        return isinstance(self.surfaceType, Ceiling)

    @property
    def isWindow(self):
        """Check if surface is a Window."""
        return isinstance(self.surfaceType, Window)

    @property
    def points(self):
        """Get/set points."""
        return self._points

    @property
    def absolutePoints(self):
        """Return absolute coordinates of points.

        If coordinate system is absolute, self.absolutePoints will be the same
        as self.points.
        """
        if self.isRelativeSystem:
            ptgroups = range(len(self.points))
            for count, ptGroup in enumerate(self.points):
                ptgroups[count] = [
                    (pt[0] + self.origin[0],
                     pt[1] + self.origin[1],
                     pt[2] + self.origin[2])
                    for pt in ptGroup
                ]
            return ptgroups
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
        self._points = []
        self.addPointList(pts, True)
        if hasattr(self, 'isTypeSetByUser') and not self.isTypeSetByUser:
            # re-evaluate the type if it hasn't been set by user
            self._surfaceType = self._surfaceTypeFromPoints()

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
            'Points should be a list or a tuple or a generator not {}'.format(type(pts))
        if len(pts) == 0:
            return
        if removeCurrentPoints:
            self._points = []

        if hasattr(pts[0], 'X'):
            # a single list of points from Dynamo
            self._points.append(tuple((pt.X, pt.Y, pt.Z) for pt in pts))

        elif hasattr(pts[0], '__iter__') and hasattr(pts[0][0], 'X'):
            # list of points list in Dynamo
            self._points.extend(tuple(tuple((pt.X, pt.Y, pt.Z) for pt in ptGroup)
                                      for ptGroup in pts))

        elif hasattr(pts[0], '__iter__') and not hasattr(pts[0][0], '__iter__'):
            # a list of tuples as x, y, z
            self._points.append(pts)

        elif hasattr(pts[0], '__iter__') and hasattr(pts[0][0], '__iter__'):
            # a list of list of tuples
            self._points.extend(pts)

        else:
            raise ValueError('Invalid structure for input points: {}'.format(pts))

    def addPoint(self, pt, subsurfaceNumber=-1):
        """Add a single point to current surface points.

        Args:
            pt: A point as (x, y, z) e.g. (20, 20, 10)
            subsurfaceNumber: An optional input to indicate the subsurface that
            point should be added to (Default is -1)
        """
        try:
            self._points[subsurfaceNumber].append(pt)
        except IndexError:
            # pts is a flattened list
            self._points.append([pt])
        except AttributeError:
            # input is a tuple or a generator
            self._points[subsurfaceNumber] = list(self._points[subsurfaceNumber])
            self._points[subsurfaceNumber].append(pt)

    @property
    def normal(self):
        """Return surface normal for the first face."""
        return go.normalFromPoints(self.points[0])

    @property
    def normals(self):
        """Return surface normals for all faces."""
        return tuple(go.normalFromPoints(pts) for pts in self.points)

    @property
    def normalsAngleDifference(self):
        """Maximum angle difference between normals and the first normal."""
        maxAngle = 0
        if len(self.points) == 1:
            return 0
        normals = self.normals
        base = normals[0]
        for norm in normals:
            angle = go.vectorAngle(base, norm)
            if angle > maxAngle:
                maxAngle = angle
        return maxAngle

    @property
    def upnormal(self):
        """Get upnormal for this surface.

        Use this value to set up rfluxmtx header.
        """
        return go.upVectorFromPoints(self.points[0])

    @property
    def radProperties(self):
        """Get and set Radiance properties."""
        return self.states[self.state].radProperties

    @radProperties.setter
    def radProperties(self, radProperties):
        self.states[self.state].radProperties = radProperties

    @property
    def radianceMaterial(self):
        """Get and set Radiance material.

        When you set Radiance material you can pass a Boolean to determine if the
        Radiance material is set by user or is based on surface type.

        Usage:

            radMat = PlasticMaterial.bySingleReflectValue("wall_material", 0.55)
            HBSrf.radianceMaterial = (radMat, True)
            # or
            HBSrf.radianceMaterial = radMat
        """
        if self.states[self.state].radianceMaterial:
            return self.states[self.state].radianceMaterial
        else:
            # if state doesn't have a radianceMaterial use the original radiance material
            return self.states[0].radianceMaterial

    @radianceMaterial.setter
    def radianceMaterial(self, value):
        try:
            self.states[self.state].radProperties.radianceMaterial = value
        except AttributeError:
            raise AttributeError('Failed to assign new Radiance material.'
                                 ' Current state does not have a RadianceProperties!')

    def radianceMaterials(self, toRadString=False):
        """Get the full list of materials including child surfaces if any."""
        mt_base = [self.radianceMaterial]
        mt_child = [childSrf.radianceMaterial for childSrf in self.childrenSurfaces
                    if self.hasChildSurfaces]
        mt = set(mt_base + mt_child)
        return '\n'.join(m.toRadString() for m in mt) if toRadString else tuple(mt)

    def duplicateVertices(self, flipped=False):
        """Duplicate surface vertices.

        Args:
            flipped: Set to True to get the vertices for the flipped surface. This is
                useful for cases like writing rad files for window groups in multi-phase
                modeling.
        """
        if self.isChildSurface or not self.hasChildSurfaces:
            vertices = self.absolutePoints
        else:
            # get points for first glass face
            glassPoints = [childSrf.absolutePoints[0]
                           for childSrf in self.childrenSurfaces]

            facePoints = self.absolutePoints[0]

            vertices = (AnalsysiSurfacePolyline(facePoints, glassPoints).polyline,)

        if flipped:
            return tuple(tuple(reversed(pts)) for pts in vertices)
        else:
            return vertices

    def toRadString(self, mode=1, includeMaterials=False, flipped=False, blacked=False):
        """Get full radiance file as a string.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            includeMaterials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        mode = mode or 1
        return RadFile((self,)).toRadString(mode, includeMaterials, flipped, blacked)

    def radStringToFile(self, filePath, mode=1, includeMaterials=False, flipped=False,
                        blacked=False):
        """Write Radiance definition for this surface to a file.

        Args:
            filepath: Full filepath (e.g c:/ladybug/geo.rad).
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            includeMaterials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        mode = mode or 1
        assert os.path.isdir(os.path.split(filePath)[0]), \
            "Cannot find %s." % os.path.split(filePath)[0]

        with open(filePath, "wb") as outf:
            try:
                outf.write(self.toRadString(mode, includeMaterials, flipped, blacked))
                return True
            except Exception as e:
                print "Failed to write %s to file:\n%s" % (self.name, e)
                return False

    @property
    def epProperties(self):
        """Get and set EnergyPlus properties."""
        raise NotImplementedError()

    @epProperties.setter
    def epProperties(self, epProperties):
        if epProperties is None:
            pass
        else:
            raise NotImplementedError()

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

    def duplicate(self):
        """Copy honeybee surface."""
        return copy.deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Honeybee surface."""
        return ("%s::%s::%s" % (self.__class__.__name__, self.name, self.surfaceType)) \
            .replace('Surface Type: ', '')


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
        return math.sqrt((pt2[0] - pt1[0]) ** 2 +
                         (pt2[1] - pt1[1]) ** 2 +
                         (pt2[2] - pt1[2]) ** 2)

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
        sortedTargets = sorted(
            targets, key=lambda target: self.__shortestDistance(source, target)[0])

        self.__addPoints(source, sortedTargets[0])

        if len(sortedTargets) > 1:
            self.__calculatePolyline(sortedTargets[0], sortedTargets[1:])
        else:
            self.__addPoints(sortedTargets[0], sortedTargets[0])
