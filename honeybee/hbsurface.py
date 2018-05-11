from _hbanalysissurface import HBAnalysisSurface
from hbfensurface import HBFenSurface
from surfaceproperties import SurfaceProperties, SurfaceState
from vectormath.euclid import Vector3, Point3
import utilcol as util
import honeybee
try:
    import plus
except ImportError as e:
    if honeybee.isplus:
        raise ImportError(e)


class HBSurface(HBAnalysisSurface):
    """Base class for Honeybee surface.

    Attributes:
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
                6.0: Context
        is_name_set_by_user: If you want the name to be changed by honeybee any case
            set is_name_set_by_user to True. Default is set to False which let Honeybee
            to rename the surface in cases like creating a newHBZone.
        rad_properties: Radiance properties for this surface. If empty default
            RADProperties will be assigned to surface by Honeybee.
        ep_properties: EnergyPlus properties for this surface. If empty default
            ep_properties will be assigned to surface by Honeybee.

    Usage:

        pts = ((0, 0, 0), (10, 0, 0), (0, 0, 10))
        hbsrf = HBSurface("001", pts, surface_type=None, is_name_set_by_user=True,
                          is_type_set_by_user=True)

        print(hbsrf.to_rad_string(include_materials=True))

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

    def __init__(self, name, sorted_points=[], surface_type=None,
                 is_name_set_by_user=False, is_type_set_by_user=False,
                 rad_properties=None, ep_properties=None, states=None):
        """Init honeybee surface."""
        states = states or ()

        HBAnalysisSurface.__init__(self, name, sorted_points, surface_type,
                                   is_name_set_by_user, is_type_set_by_user)

        sp = SurfaceProperties(self.surface_type, rad_properties, ep_properties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.add_surface_state(state)

        self._parent = None
        self._child_surfaces = []
        self._is_created_from_geo = False

    # TODO: Parse EnergyPlus properties
    @classmethod
    def from_ep_string(cls, ep_string):
        """Init Honeybee surface from an ep_string.

        Args:
            ep_string: The full ep_string for an EnergyPlus surface.
        """
        types = {'Wall': 0, 'Roof': 1, 'Floor': 2, 'Ceiling': 3}

        # clean input ep_string - split based on comma
        segments = ep_string.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        name = segments[1]
        srf_type = types[segments[2].capitalize()]
        pts = range((len(segments) - 11) / 3)

        # create points
        for count, i in enumerate(xrange(11, len(segments), 3)):
            try:
                pts[count] = [float(c) for c in segments[i: i + 3]]
            except ValueError:
                raise ValueError(
                    "%s is an invalid value for points." % segments[i: i + 3]
                )

        # create the surfaceString
        return cls(name, pts, srf_type, is_name_set_by_user=True,
                   is_type_set_by_user=True)

    @classmethod
    def from_geometry(cls, name, geometry, surface_type=None,
                      is_name_set_by_user=False, is_type_set_by_user=False,
                      rad_properties=None, ep_properties=None, states=None, group=False):
        """Create honeybee surface[s] from a Grasshopper geometry.

        If group is False it will return a list of HBSurfaces.
        """
        assert honeybee.isplus, \
            '"fromGeometries" method can only be used in [+] libraries.'

        name = name or util.random_name()

        if isinstance(name, basestring):
            names = (name,)
        elif not hasattr(name, '__iter__'):
            names = (name,)
        else:
            names = name

        namescount = len(names) - 1

        srf_data = plus.extract_geometry_points(geometry)
        cls._is_created_from_geo = True
        if not group:
            if ep_properties:
                print('ep_properties.duplicate must be implemented to honeybee surface.')
            hbsrfs = []
            # create a separate surface for each geometry.
            for gcount, srf in enumerate(srf_data):
                for scount, (geo, pts) in enumerate(srf):
                    try:
                        _name = '%s_%d_%d' % (names[gcount], gcount, scount)
                    except IndexError:
                        _name = '%s_%d_%d' % (names[-1], gcount, scount)

                    if rad_properties:
                        _srf = cls(_name, pts, surface_type, is_name_set_by_user,
                                   is_type_set_by_user, rad_properties.duplicate(),
                                   ep_properties, states)
                    else:
                        _srf = cls(_name, pts, surface_type, is_name_set_by_user,
                                   is_type_set_by_user, rad_properties, ep_properties,
                                   states)

                    _srf.geometry = geo
                    hbsrfs.append(_srf)

            # check naming and fix it if it's only single geometry
            if (gcount == 0 or gcount <= namescount) and scount == 0:
                # this is just a single geometry. remove counter
                for hbsrf in hbsrfs:
                    hbsrf.name = '_'.join(hbsrf.name.split('_')[:-2])
            elif gcount == 0 or gcount == namescount:
                # this is a single geometry with multiple sub surfaces like a polysurface
                for hbs in hbsrfs:
                    bname = hbs.name.split('_')
                    hbs.name = '%s_%s' % ('_'.join(bname[:-2]), bname[-1])
            return hbsrfs
        else:
            _geos = []
            _pts = []
            # collect all the points in a single list
            for srf in srf_data:
                for geo, pts in srf:
                    _pts.extend(pts)
                    _geos.append(geo)

            _srf = cls(names[0], _pts, surface_type, is_name_set_by_user,
                       is_type_set_by_user, rad_properties, ep_properties, states)
            _srf.geometry = _geos
            return _srf

    @property
    def is_created_from_geometry(self):
        """Return True if the surface is created from a geometry not points."""
        return self._isCeatedFromGeo

    @property
    def isHBSurface(self):
        """Return True for HBSurface."""
        return True

    @property
    def is_child_surface(self):
        """Return False for HBSurface."""
        return False

    @property
    def has_child_surfaces(self):
        """Return True if Honeybee surface has Fenestration surrfaces."""
        return len(self._child_surfaces) != 0

    @property
    def parent(self):
        """Get or set parent zone."""
        return self._parent

    @property
    def children_surfaces(self):
        """Get children surfaces."""
        return self._child_surfaces

    @property
    def geometry(self):
        """Return geometry."""
        assert honeybee.isplus, \
            '"geometry" property can only be used in [+] libraries.'
        if self.is_created_from_geometry:
            return self._geometry
        else:
            return self.profile

    @geometry.setter
    def geometry(self, geo):
        """Set geometry."""
        assert honeybee.isplus, \
            '"geometry" property can only be used in [+] libraries.'
        self._geometry = geo

    @property
    def profile(self):
        """Get profile curve of this surface."""
        assert honeybee.isplus, \
            '"profile" property can only be used in [+] libraries.'
        return plus.polygon(
            tuple(plus.xyz_to_geometrical_points(self.absolute_points))
        )

    def add_fenestration_surface_by_size(self, name, width, height, sill_height=1,
                                         radiance_material=None):
        """Add rectangular fenestration surface to surface.

        Args:
            width: Opening width. Opening will be centered in HBSurface.
            height: Opening height.
            sill_height: Sill height (default: 1).
            radiance_material: Optional radiance material for this fenestration.
        """
        for pts in self.points:
            assert len(pts) == 4, 'Length of points should be 4.'
            pt0 = Point3(*pts[0])
            pt1 = Point3(*pts[1])
            pt3 = Point3(*pts[-1])
            x_axis = Vector3(*(pt1 - pt0)).normalized()
            y_axis = Vector3(*(pt3 - pt0)).normalized()
            srf_width = pt0.distance(pt1)
            srf_height = pt0.distance(pt3)

            assert srf_width > width, \
                'Opening width [{}] should be smaller than ' \
                'HBSurface width [{}].'.format(srf_width, width)

            assert srf_height > height + sill_height, \
                'Opening height plus sill height [{}] should be smaller than ' \
                'HBSurface height [{}].'.format(srf_height + sill_height, height)

            # create fenestration surface
            x_gap = (srf_width - width) / 2.0
            glz_pt0 = pt0 + (x_gap * x_axis) + (sill_height * y_axis)
            glz_pt1 = pt0 + ((x_gap + width) * x_axis) + (sill_height * y_axis)
            glz_pt2 = pt0 + ((x_gap + width) * x_axis) + \
                ((sill_height + height) * y_axis)
            glz_pt3 = pt0 + (x_gap * x_axis) + ((sill_height + height) * y_axis)

            glzsrf = HBFenSurface(name, [glz_pt0, glz_pt1, glz_pt2, glz_pt3])

            if radiance_material:
                glzsrf.radiance_material = radiance_material

            self.add_fenestration_surface(glzsrf)

    def add_fenestration_surface(self, fenestration_surface):
        """Add a fenestration surface to HB surface."""
        assert hasattr(fenestration_surface, 'isHBFenSurface'), \
            '{} is not a HBFenSurfaces'.format(type(fenestration_surface))

        self._child_surfaces.append(fenestration_surface)

        # set up parent object if it's not set
        fenestration_surface._parent = self
