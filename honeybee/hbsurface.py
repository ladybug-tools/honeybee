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

    def __init__(self, name, sortedPoints=[], surfaceType=None,
                 isNameSetByUser=False, isTypeSetByUser=False,
                 radProperties=None, epProperties=None, states=None):
        """Init honeybee surface."""
        states = states or ()

        HBAnalysisSurface.__init__(self, name, sortedPoints, surfaceType,
                                   isNameSetByUser, isTypeSetByUser)

        sp = SurfaceProperties(self.surfaceType, radProperties, epProperties)
        self._states[0] = SurfaceState('default', sp)
        for state in states:
            self.addSurfaceState(state)

        self._parent = None
        self._childSurfaces = []
        self._isCreatedFromGeo = False

    # TODO: Parse EnergyPlus properties
    @classmethod
    def fromEPString(cls, EPString):
        """Init Honeybee surface from an EPString.

        Args:
            EPString: The full EPString for an EnergyPlus surface.
        """
        types = {'Wall': 0, 'Roof': 1, 'Floor': 2, 'Ceiling': 3}

        # clean input EPString - split based on comma
        segments = EPString.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        name = segments[1]
        srfType = types[segments[2].capitalize()]
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
        return cls(name, pts, srfType, isNameSetByUser=True, isTypeSetByUser=True)

    @classmethod
    def fromGeometry(cls, name, geometry, surfaceType=None,
                     isNameSetByUser=False, isTypeSetByUser=False,
                     radProperties=None, epProperties=None, states=None, group=False):
        """Create honeybee surface[s] from a Grasshopper geometry.

        If group is False it will return a list of HBSurfaces.
        """
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
            if epProperties:
                print('epProperties.duplicate must be implemented to honeybee surface.')
            hbsrfs = []
            # create a separate surface for each geometry.
            for gcount, srf in enumerate(srfData):
                for scount, (geo, pts) in enumerate(srf):
                    try:
                        _name = '%s_%d_%d' % (names[gcount], gcount, scount)
                    except IndexError:
                        _name = '%s_%d_%d' % (names[-1], gcount, scount)

                    if radProperties:
                        _srf = cls(_name, pts, surfaceType, isNameSetByUser,
                                   isTypeSetByUser, radProperties.duplicate(),
                                   epProperties, states)
                    else:
                        _srf = cls(_name, pts, surfaceType, isNameSetByUser,
                                   isTypeSetByUser, radProperties, epProperties, states)

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

            _srf = cls(names[0], _pts, surfaceType, isNameSetByUser, isTypeSetByUser,
                       radProperties, epProperties, states)
            _srf.geometry = _geos
            return _srf

    @property
    def isCreatedFromGeometry(self):
        """Return True if the surface is created from a geometry not points."""
        return self._isCreatedFromGeo

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
        return len(self._childSurfaces) != 0

    @property
    def parent(self):
        """Get or set parent zone."""
        return self._parent

    @property
    def childrenSurfaces(self):
        """Get children surfaces."""
        return self._childSurfaces

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

    def addFenestrationSurfaceBySize(self, name, width, height, sillHeight=1,
                                     radianceMaterial=None):
        """Add rectangular fenestration surface to surface.

        Args:
            width: Opening width. Opening will be centered in HBSurface.
            height: Opening height.
            sillHeight: Sill height (default: 1).
            radianceMaterial: Optional radiance material for this fenestration.
        """
        for pts in self.points:
            assert len(pts) == 4, 'Length of points should be 4.'
            pt0 = Point3(*pts[0])
            pt1 = Point3(*pts[1])
            pt3 = Point3(*pts[-1])
            xAxis = Vector3(*(pt1 - pt0)).normalized()
            yAxis = Vector3(*(pt3 - pt0)).normalized()
            srfWidth = pt0.distance(pt1)
            srfHeight = pt0.distance(pt3)

            assert srfWidth > width, \
                'Opening width [{}] should be smaller than ' \
                'HBSurface width [{}].'.format(srfWidth, width)

            assert srfHeight > height + sillHeight, \
                'Opening height plus sill height [{}] should be smaller than ' \
                'HBSurface height [{}].'.format(srfHeight + sillHeight, height)

            # create fenestration surface
            xGap = (srfWidth - width) / 2.0
            glzPt0 = pt0 + (xGap * xAxis) + (sillHeight * yAxis)
            glzPt1 = pt0 + ((xGap + width) * xAxis) + (sillHeight * yAxis)
            glzPt2 = pt0 + ((xGap + width) * xAxis) + ((sillHeight + height) * yAxis)
            glzPt3 = pt0 + (xGap * xAxis) + ((sillHeight + height) * yAxis)

            glzsrf = HBFenSurface(name, [glzPt0, glzPt1, glzPt2, glzPt3])

            if radianceMaterial:
                glzsrf.radianceMaterial = radianceMaterial

            self.addFenestrationSurface(glzsrf)

    def addFenestrationSurface(self, fenestrationSurface):
        """Add a fenestration surface to HB surface."""
        assert hasattr(fenestrationSurface, 'isHBFenSurface'), \
            '{} is not a HBFenSurfaces'.format(type(fenestrationSurface))

        self._childSurfaces.append(fenestrationSurface)

        # set up parent object if it's not set
        fenestrationSurface._parent = self
