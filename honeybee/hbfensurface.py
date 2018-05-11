from _hbanalysissurface import HBAnalysisSurface
from surfaceproperties import SurfaceProperties, SurfaceState
import utilcol as util
import honeybee
try:
    import plus
except ImportError as e:
    if honeybee.isplus:
        raise ImportError(e)


class HBFenSurface(HBAnalysisSurface):
    """Honeybee fenestration surface.

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

    Usage:

        from honeybee.hbsurface import HBSurface
        from honeybee.hbfensurface import HBFenSurface

        # create a surface
        pts = [(0, 0, 0), (10, 0, 0), (0, 0, 10)]
        hbsrf = HBSurface("001", pts, surface_type=None, is_name_set_by_user=True)

        glzpts = [(1, 0, 1), (8, 0, 1), (1, 0, 8)]
        glzsrf = HBFenSurface("glz_001", glzpts)

        # add fenestration surface to hb surface
        hbsrf.add_fenestration_surface(glzsrf)

        # get full definiion of the surface including the fenestration
        print(hbsrf.to_rad_string(include_materials=True))

        # save the definiion to a .rad file
        hbsrf.rad_string_to_file(r"c:/ladybug/triangle.rad", include_materials=True)
    """

    def __init__(self, name, sorted_points=None, is_name_set_by_user=False,
                 rad_properties=None, ep_properties=None, states=None):
        """Init honeybee surface."""
        _surface_type = 5
        _is_type_set_by_user = True
        sorted_points = sorted_points or []

        states = states or ()
        HBAnalysisSurface.__init__(self, name, sorted_points, _surface_type,
                                   is_name_set_by_user, _is_type_set_by_user)

        sp = SurfaceProperties(self.surface_type, rad_properties, ep_properties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.add_surface_state(state)

        self.__isChildSurface = True
        # Parent will be set once the fen surface is added to a prent surface
        self._parent = None
        self._isCreatedFromGeo = False

    # TODO: Parse EnergyPlus properties
    @classmethod
    def from_ep_string(cls, ep_string):
        """Init Honeybee fenestration surface from an ep_string.

        Args:
            ep_string: The full ep_string for an EnergyPlus fenestration.
        """
        # clean input ep_string - split based on comma
        _segments = ep_string.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        name = _segments[1]
        _pts = range((len(_segments) - 11) / 3)

        # create points
        for count, i in enumerate(xrange(11, len(_segments), 3)):
            try:
                _pts[count] = [float(c) for c in _segments[i: i + 3]]
            except ValueError:
                raise ValueError(
                    "%s is an invalid value for points." % _segments[i: i + 3]
                )

        # create the surfaceString
        return cls(name, sorted_points=_pts, is_name_set_by_user=True)

    @classmethod
    def from_geometry(cls, name, geometry, is_name_set_by_user=False,
                      rad_properties=None, ep_properties=None, states=None, group=False):
        """Create a honeybee fenestration surface from Grasshopper geometry."""
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
        cls._isCreatedFromGeo = True

        if not group:
            hbsrfs = []
            # create a separate surface for each geometry.
            for gcount, srf in enumerate(srf_data):
                for scount, (geo, pts) in enumerate(srf):
                    try:
                        _name = '%s_%d_%d' % (names[gcount], gcount, scount)
                    except IndexError:
                        _name = '%s_%d_%d' % (names[-1], gcount, scount)

                    _srf = cls(_name, pts, is_name_set_by_user, rad_properties,
                               ep_properties, states)
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

            _srf = cls(names[0], _pts, is_name_set_by_user, rad_properties,
                       ep_properties, states)
            _srf.geometry = _geos
            return _srf

    @property
    def is_created_from_geometry(self):
        """Return True if the surface is created from a geometry not points."""
        return self._isCreatedFromGeo

    @property
    def isHBFenSurface(self):
        """Return True for HBFenSurface."""
        return True

    @property
    def is_child_surface(self):
        """Return True if Honeybee surface is Fenestration Surface."""
        return self.__isChildSurface

    @property
    def parent(self):
        """Return parent surface for this fenestration surface."""
        return self._parent

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

        assert honeybee.isplus, \
            '"profile" property can only be used in [+] libraries.'
        self._geometry = geo

    @property
    def profile(self):
        """Get profile curve of this surface."""
        assert honeybee.isplus, \
            '"profile" property can only be used in [+] libraries.'
        return plus.polygon(
            tuple(plus.xyz_to_geometrical_points(self.absolute_points))
        )
