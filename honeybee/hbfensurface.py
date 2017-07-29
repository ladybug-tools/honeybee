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
        print hbsrf.toRadString(includeMaterials=True)

        # save the definiion to a .rad file
        hbsrf.radStringToFile(r"c:/ladybug/triangle.rad", includeMaterials=True)
    """

    def __init__(self, name, sortedPoints=None, isNameSetByUser=False,
                 radProperties=None, epProperties=None, states=None):
        """Init honeybee surface."""
        _surfaceType = 5
        _isTypeSetByUser = True
        sortedPoints = sortedPoints or []

        states = states or ()
        HBAnalysisSurface.__init__(self, name, sortedPoints, _surfaceType,
                                   isNameSetByUser, _isTypeSetByUser)

        sp = SurfaceProperties(self.surfaceType, radProperties, epProperties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.addSurfaceState(state)

        self.__isChildSurface = True
        # Parent will be set once the fen surface is added to a prent surface
        self._parent = None
        self._isCreatedFromGeo = False

    # TODO: Parse EnergyPlus properties
    @classmethod
    def fromEPString(cls, EPString):
        """Init Honeybee fenestration surface from an EPString.

        Args:
            EPString: The full EPString for an EnergyPlus fenestration.
        """
        # clean input EPString - split based on comma
        _segments = EPString.replace("\t", "") \
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
        return cls(name, sortedPoints=_pts, isNameSetByUser=True)

    @classmethod
    def fromGeometry(cls, name, geometry, isNameSetByUser=False, radProperties=None,
                     epProperties=None, states=None, group=False):
        """Create a honeybee fenestration surface from Grasshopper geometry."""
        assert honeybee.isplus, \
            '"fromGeometries" method can only be used in [+] libraries.'

        name = name or util.randomName()

        if isinstance(name, basestring):
            names = (name,)
        elif not hasattr(name, '__iter__'):
            names = (name,)
        else:
            names = name

        namescount = len(names) - 1

        srfData = plus.extractGeometryPoints(geometry)
        cls._isCreatedFromGeo = True

        if not group:
            hbsrfs = []
            # create a separate surface for each geometry.
            for gcount, srf in enumerate(srfData):
                for scount, (geo, pts) in enumerate(srf):
                    try:
                        _name = '%s_%d_%d' % (names[gcount], gcount, scount)
                    except IndexError:
                        _name = '%s_%d_%d' % (names[-1], gcount, scount)

                    _srf = cls(_name, pts, isNameSetByUser, radProperties, epProperties,
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
            for srf in srfData:
                for geo, pts in srf:
                    _pts.extend(pts)
                    _geos.append(geo)

            _srf = cls(names[0], _pts, isNameSetByUser, radProperties, epProperties,
                       states)
            _srf.geometry = _geos
            return _srf

    @property
    def isCreatedFromGeometry(self):
        """Return True if the surface is created from a geometry not points."""
        return self._isCreatedFromGeo

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
        """Return parent surface for this fenestration surface."""
        return self._parent

    @property
    def geometry(self):
        """Return geometry."""
        assert honeybee.isplus, \
            '"geometry" property can only be used in [+] libraries.'
        if self.isCreatedFromGeometry:
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
            tuple(plus.xyzToGeometricalPoints(self.absolutePoints))
        )
