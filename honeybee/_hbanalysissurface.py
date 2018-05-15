from abc import ABCMeta, abstractproperty
import utilcol as util
from hbobject import HBObject
from surfaceproperties import SurfaceProperties, SurfaceState
import surfacetype
import geometryoperation as go
from surfacetype import Floor, Wall, Window, Ceiling
from radiance.radfile import RadFile
from radiance.material.glass import Glass
from radiance.material.glow import Glow
from radiance.material.plastic import Plastic
from radiance.material.metal import Metal

import os
import types
import math
import copy


class HBAnalysisSurface(HBObject):
    """Base class for Honeybee surface.

    Args:
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
                5.0: Window         6.0: Context
        is_name_set_by_user: If you want the name to be changed by honeybee any case
            set is_name_set_by_user to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        states: A collection of SurfaceStates. SurfaceStates includes SurfaceProperties
            which includes the data for RadianceProperties and EPProperties and optional
            HBSurfaces. Each
            item in this collection stands for a different stae of the materials. Use
            the properties to model dynamic bahaviors such as dynamic blinds.
    """

    __metaclass__ = ABCMeta
    _surface_types = {0.0: 'Wall', 0.5: 'UndergroundWall', 1.0: 'Roof',
                      1.5: 'UndergroundCeiling', 2.0: 'Floor',
                      2.25: 'UndergroundSlab', 2.5: 'SlabOnGrade',
                      2.75: 'ExposedFloor', 3.0: 'Ceiling', 4.0: 'AirWall',
                      6.0: 'Context'}

    def __init__(self, name, sorted_points, surface_type=None, is_name_set_by_user=False,
                 is_type_set_by_user=False, states=None):
        """Initialize Honeybee Surface."""
        self._childSurfaces = ()
        self._states = []
        if not name:
            name = util.random_name()
            is_name_set_by_user = False
        self.name = (name, is_name_set_by_user)
        """Surface name."""
        self.points = sorted_points
        """A list of points as tuples or lists of (x, y, z).
        Points should be sorted. This class won't sort the points.
        (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
        """
        self.surface_type = (surface_type, is_type_set_by_user)
        """Surface type."""
        self.state = 0
        """Current state of the surface."""
        states = states or \
            (SurfaceState('default', SurfaceProperties(self.surface_type)),)
        for state in states:
            self.add_surface_state(state)

    @classmethod
    def from_json(cls, srf_json):
        """Create a surface from json object.

        The minimum schema is:
            {"name": "",
            "vertices": [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]],
            "surface_material": {},  // radiance material json file
             "surface_type": null  // 0: wall, 5: window
            }
        """
        name = srf_json["name"]
        vertices = srf_json["vertices"]
        type_id = srf_json["surface_type"]
        srf_type = surfacetype.SurfaceTypes.get_type_by_key(type_id)
        HBsrf = cls(name, vertices, srf_type)
        # Check material type and determine appropriate "from_json" classmethod
        if "surface_material" in srf_json.keys():
            material_json = srf_json["surface_material"]
            type = material_json["type"]
            if type == "plastic":
                radiance_material = Plastic.from_json(material_json)
            elif type == "metal":
                radiance_material = Metal.from_json(material_json)
            elif type == "glass":
                radiance_material = Glass.from_json(material_json)
            else:
                # raise ValueError "The material type {} in the surface json is either
                # not currently suported or incorrect"
                # .format(srf_json["surface_material"])
                radiance_material = None
            HBsrf.radiance_material = radiance_material
        return HBsrf

    @classmethod
    def from_rad_ep_properties(
        cls, name, sorted_points, surface_type=None, is_name_set_by_user=False,
            is_type_set_by_user=False, rad_properties=None, ep_properties=None,
            states=None):
        """Initialize Honeybee Surface.

        RadianceProperties and EPProperties will be used to create the initial state.
        """
        states = states or ()
        # create the surface first to get the surface type if not available
        _cls = cls(
            name,
            sorted_points,
            surface_type,
            is_name_set_by_user,
            is_type_set_by_user)
        # replace the default properties for the initial state
        sp = SurfaceProperties(_cls.surface_type, rad_properties, ep_properties)
        _cls._states[0] = SurfaceState('default', sp)

        for state in states:
            _cls.add_surface_state(state)

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
    def is_child_surface(self):
        """Return True if Honeybee surface is Fenestration Surface."""
        pass

    @property
    def has_child_surfaces(self):
        """Return True if surface has children surfaces."""
        return False

    @property
    def children_surfaces(self):
        """Get children surfaces."""
        return self._childSurfaces

    @property
    def has_bsdf_radiance_material(self):
        """Return True if .xml BSDF material is assigned for radiance material."""
        return self.isHBFenSurface and hasattr(self.radiance_material, 'xmlfile')

    @property
    def has_radiance_glass_material(self):
        """Return true if surface has radiance glass material."""
        return self.radiance_material.is_glass_material

    @abstractproperty
    def parent(self):
        """Return parent for HBAnalysisSurface.

        Parent will be a HBZone for a HBSurface, and a HBSurface for a
        HBFenSurface.
        """
        pass

    @property
    def is_relative_system(self):
        """Return True if coordinate system is relative."""
        if self.parent is None:
            return False
        else:
            return self.parent.is_relative_system

    @property
    def origin(self):
        """Get origin of the coordinate system for this surface.

        For Absolute system the value is always (0, 0, 0).
        """
        return self.parent.origin

    @property
    def state_count(self):
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
            assert count < self.state_count, \
                ValueError(
                    'This surface has only {} state. {} is an invalid state.'.format(
                        self.state_count, count
                    )
                )
        self._state = count

    @property
    def states(self):
        """List of states for this surface."""
        return self._states

    def add_surface_state(self, srf_state):
        if not srf_state:
            return

        assert hasattr(srf_state, 'isSurfaceState'), \
            TypeError('Expected SurfaceState not {}'.format(type(srf_state)))

        self._states.append(srf_state)

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
            if isinstance(values, str):
                raise TypeError
            new_name, is_name_set_by_user = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            new_name = values[0]
            is_name_set_by_user = False  # if not indicated assume it is not set by user.
        except TypeError:
            # user just passed a single value which is the name
            new_name = values
            is_name_set_by_user = False  # if not indicated assume it is not set by user.
        finally:
            # set new name
            self._name = str(new_name)
            self._is_name_set_by_user = is_name_set_by_user
            util.check_name(self._name)

    @property
    def is_name_set_by_user(self):
        """Return if name is set by user.

        If name is set by user the surface will never be renamed automatically.
        """
        return self._is_name_set_by_user

    @property
    def surface_types(self):
        """Return Honeybee valid surface types."""
        return self._surface_types

    @property
    def surface_type(self):
        """Get and set Surface Type."""
        return self._surface_type

    @surface_type.setter
    def surface_type(self, values):
        # let's assume values in surface_type and Boolean
        _surface_type, is_type_set_by_user = values

        # Now let's check the input for surface type
        if _surface_type is not None:
            # it is either a number or already a valid type
            if isinstance(_surface_type, surfacetype.SurfaceTypeBase):
                self._surface_type = _surface_type
            else:
                try:
                    # it should be a key value
                    self._surface_type = \
                        surfacetype.SurfaceTypes.get_type_by_key(_surface_type)()
                except KeyError:
                    raise ValueError('%s is not a valid surface type.' % _surface_type)
        else:
            # try to figure it out based on points
            self._surface_type = self._surface_type_from_points()
            is_type_set_by_user = False

        self._is_type_set_by_user = is_type_set_by_user

    def _surface_type_from_points(self):
        normal = go.normal_from_points(self.points[0])
        angle_to_z_axis = go.vector_angle_to_z_axis(normal)
        return surfacetype.SurfaceTypes.by_normal_angle_and_points(angle_to_z_axis,
                                                                   self.points[0])()

    @property
    def is_type_set_by_user(self):
        """Check if the type for surface is set by user."""
        return self._is_type_set_by_user

    @property
    def is_floor(self):
        """Check if surface is a Floor."""
        return isinstance(self.surface_type, Floor)

    @property
    def is_wall(self):
        """Check if surface is a Wall."""
        return isinstance(self.surface_type, Wall)

    @property
    def is_ceiling(self):
        """Check if surface is a Ceiling."""
        return isinstance(self.surface_type, Ceiling)

    @property
    def is_window(self):
        """Check if surface is a Window."""
        return isinstance(self.surface_type, Window)

    @property
    def points(self):
        """Get/set points."""
        return self._points

    @property
    def absolute_points(self):
        """Return absolute coordinates of points.

        If coordinate system is absolute, self.absolute_points will be the same
        as self.points.
        """
        if self.is_relative_system:
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
        self.add_point_list(pts, True)
        if hasattr(self, 'is_type_set_by_user') and not self.is_type_set_by_user:
            # re-evaluate the type if it hasn't been set by user
            self._surface_type = self._surface_type_from_points()

    def add_point_list(self, pts, remove_current_points=False):
        """Add new list of points to surface points.

        Args:
            pts: A list of points as tuples or lists of (x, y, z).
                Points should be sorted. This class won't sort the points.
                (e.g. ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
            remove_current_points: Set to True to remove current points.
                (Default: False)
        """
        assert isinstance(pts, (list, tuple, types.GeneratorType)), \
            'Points should be a list or a tuple or a generator not {}'.format(type(pts))
        if len(pts) == 0:
            return
        if remove_current_points:
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

    def add_point(self, pt, subsurface_number=-1):
        """Add a single point to current surface points.

        Args:
            pt: A point as (x, y, z) e.g. (20, 20, 10)
            subsurface_number: An optional input to indicate the subsurface that
            point should be added to (Default is -1)
        """
        try:
            self._points[subsurface_number].append(pt)
        except IndexError:
            # pts is a flattened list
            self._points.append([pt])
        except AttributeError:
            # input is a tuple or a generator
            self._points[subsurface_number] = list(self._points[subsurface_number])
            self._points[subsurface_number].append(pt)

    @property
    def normal(self):
        """Return surface normal for the first face."""
        return go.normal_from_points(self.points[0])

    @property
    def normals(self):
        """Return surface normals for all faces."""
        return tuple(go.normal_from_points(pts) for pts in self.points)

    @property
    def normals_angle_difference(self):
        """Maximum angle difference between normals and the first normal."""
        max_angle = 0
        if len(self.points) == 1:
            return 0
        normals = self.normals
        base = normals[0]
        for norm in normals:
            angle = go.vector_angle(base, norm)
            if angle > max_angle:
                max_angle = angle
        return max_angle

    @property
    def upnormal(self):
        """Get upnormal for this surface.

        Use this value to set up rfluxmtx header.
        """
        return go.up_vector_from_points(self.points[0])

    @property
    def radiance_properties(self):
        """Get and set Radiance properties."""
        return self.states[self.state].radiance_properties

    @radiance_properties.setter
    def radiance_properties(self, rad_properties):
        self.states[self.state].radiance_properties = rad_properties

    @property
    def radiance_material(self):
        """Get and set Radiance material.

        When you set Radiance material you can pass a Boolean to determine if the
        Radiance material is set by user or is based on surface type.

        Usage:

            radMat = Plastic.by_single_reflect_value("wall_material", 0.55)
            HBSrf.radiance_material = (radMat, True)
            # or
            HBSrf.radiance_material = radMat
        """
        if self.states[self.state].radiance_material:
            return self.states[self.state].radiance_material
        else:
            # if state doesn't have a radiance_material use the original radiance
            # material
            return self.states[0].radiance_material

    @radiance_material.setter
    def radiance_material(self, value):
        try:
            self.states[self.state].radiance_properties.material = value
        except AttributeError:
            raise AttributeError('Failed to assign new Radiance material.'
                                 ' Current state does not have a RadianceProperties!')

    def radiance_materials(self, to_rad_string=False):
        """Get the full list of materials including child surfaces if any."""
        mt_base = [self.radiance_material]
        mt_child = [childSrf.radiance_material for childSrf in self.children_surfaces
                    if self.has_child_surfaces]
        mt = set(mt_base + mt_child)
        return '\n'.join(m.to_rad_string() for m in mt) if to_rad_string else tuple(mt)

    def duplicate_vertices(self, flipped=False):
        """Duplicate surface vertices.

        Args:
            flipped: Set to True to get the vertices for the flipped surface. This is
                useful for cases like writing rad files for window groups in multi-phase
                modeling.
        """
        if self.is_child_surface or not self.has_child_surfaces:
            vertices = self.absolute_points
        else:
            # get points for first glass face
            glass_points = [childSrf.absolute_points[0]
                            for childSrf in self.children_surfaces]

            face_points = self.absolute_points[0]

            vertices = (AnalsysiSurfacePolyline(face_points, glass_points).polyline,)

        if flipped:
            return tuple(tuple(reversed(pts)) for pts in vertices)
        else:
            return vertices

    def to_rad_string(self, mode=1, include_materials=False,
                      flipped=False, blacked=False):
        """Get full radiance file as a string.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            include_materials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        mode = mode or 1
        return RadFile((self,)).to_rad_string(mode, include_materials, flipped, blacked)

    def rad_string_to_file(self, file_path, mode=1, include_materials=False,
                           flipped=False, blacked=False):
        """Write Radiance definition for this surface to a file.

        Args:
            filepath: Full filepath (e.g c:/ladybug/geo.rad).
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            include_materials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        mode = mode or 1
        assert os.path.isdir(os.path.split(file_path)[0]), \
            "Cannot find %s." % os.path.split(file_path)[0]

        with open(file_path, "wb") as outf:
            try:
                outf.write(self.to_rad_string(mode, include_materials, flipped, blacked))
                return True
            except Exception as e:
                print("Failed to write %s to file:\n%s" % (self.name, e))
                return False

    @property
    def ep_properties(self):
        """Get and set EnergyPlus properties."""
        raise NotImplementedError()

    @ep_properties.setter
    def ep_properties(self, ep_properties):
        if ep_properties is None:
            pass
        else:
            raise NotImplementedError()

    @property
    def energy_plus_materials(self):
        """Return list of EnergyPlus materials for this surface."""
        raise NotImplementedError()
        # self.ep_properties.energy_plus_materials

    @property
    def energy_plus_construction(self):
        """Return surface EnergyPlus construction."""
        raise NotImplementedError()
        # self.ep_properties.energy_plus_materials

    def to_ep_string(self, include_construction=False, include_materials=False):
        """Return EnergyPlus definition for this surface."""
        raise NotImplementedError()

    def duplicate(self):
        """Copy honeybee surface."""
        return copy.deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def to_json(self):
        """Get HBSurface as a dictionary.
            {"name": "",
            "vertices": [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]],
            "surface_material": {},  // radiance material json file
            "surface_type": null  // 0: wall, 5: window
            }
        """
        return {"name": self.name,
                "vertices": [[tuple(pt) for pt in ptgroup] for ptgroup in self.points],
                "surface_material": self.radiance_material.to_json(),
                "surface_type": self.surface_type.typeId
                }

    def __repr__(self):
        """Represnt Honeybee surface."""
        return ("%s::%s::%s" % (self.__class__.__name__, self.name, self.surface_type)) \
            .replace('Surface Type: ', '')


class AnalsysiSurfacePolyline(object):
    """Calculate AnalysisSurfacePolyline for surface with fenestrations."""

    __slots__ = ('startIndex', '_ptListA', '_ptListB')

    def __init__(self, surface_points, fen_points):
        """Init class."""
        self.startIndex = 0
        self._ptListA = []
        self._ptListB = []
        self.__calculate_polyline(surface_points, fen_points)

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

    def __shortest_distance(self, pt_list1, pt_list2):
        dist = float('inf')
        xi = None
        yi = None
        for xCount, xpt in enumerate(pt_list1):
            for yCount, ypt in enumerate(pt_list2):
                d = self.distance(xpt, ypt)
                if d < dist:
                    dist, xi, yi = d, xCount, yCount

        return dist, xi, yi

    def __add_points(self, source, target):
        d, si, ti = self.__shortest_distance(source, target)
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

    def __calculate_polyline(self, source, targets):
        """calculate single polyline for HBSurface with Fenestration."""
        # sort point groups
        sorted_targets = sorted(
            targets, key=lambda target: self.__shortest_distance(source, target)[0])

        self.__add_points(source, sorted_targets[0])

        if len(sorted_targets) > 1:
            self.__calculate_polyline(sorted_targets[0], sorted_targets[1:])
        else:
            self.__add_points(sorted_targets[0], sorted_targets[0])
