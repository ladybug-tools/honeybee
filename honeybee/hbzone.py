from hbobject import HBObject
from vectormath.euclid import Point3
from energyplus.geometryrules import GlobalGeometryRules

from collections import namedtuple
import os


class HBZone(HBObject):
    """Honeybee base class."""

    def __init__(self, name, origin=(0, 0, 0), geometryrules=None,
                 buildingProgram=None, zoneProgram=None, isConditioned=True):
        """Init Honeybee Zone."""
        self.name = name
        """Zone name"""

        self.origin = origin
        """origin of the zone."""

        self.__surfaces = []

    @property
    def isHBZone(self):
        """Return True if a HBZone."""
        return True

    @property
    def origin(self):
        """Get set origin of the zone."""
        return self.__origin

    @origin.setter
    def origin(self, value):
        try:
            self.__origin = Point3(*value)
        except:
            raise Exception("Failed to set zone origin.")

    @property
    def surfaces(self):
        """Get list of HBSurfaces for this zone."""
        return self.__surfaces

    def addSurface(self, HBSurface):
        """Add a surface to Honeybee zone."""
        assert hasattr(HBSurface, "isHBSurface"), \
            "%s input is not a Honeybee surface." % str(HBSurface)
        self.__surfaces.append(HBSurface)
        HBSurface.parent = self

    @property
    def radianceMaterials(self):
        """Get list of Radiance materials for zone including fenestration."""
        return set([srf.radianceMaterials for srf in self.surfaces])

    def toRadString(self, includeMaterials=False, includeChildrenSurfaces=True):
        """Return geometries and materials as a tuple of multiline string.

        Returns:
            if includeMaterials = False:
                A namedTuple of multiline data. Keys are: materials geometries
            else:
                A multiline string for geometries

        Usage:

            s = self.toRadString()
            geoString = s.geometries
            matString = s.materials
            or
            s = self.toRadString()
            matString, geoString = s
        """
        _radDefinition = namedtuple("RadString", "materials geometries")
        _matStr = ""
        _geoStr = ""

        if len(self.surfaces) > 0:
            _materials = []
            _geos = []
            for hbsurface in self.surfaces:
                # Both surface and fenestration material
                _materials.extend(hbsurface.radianceMaterials)
                _geos.append(hbsurface.toRadString(
                    includeMaterials=False,
                    includeChildrenSurfaces=includeChildrenSurfaces
                )
                )

            # remove duplicated materials
            _materials = set([mat.toRadString() for mat in _materials])
            _matStr = "\n".join(_materials)

            # joing geometries
            _geoStr = "\n".join(_geos)
        else:
            print "Warning: Found no Honeybee objects."

        if includeMaterials:
            return _radDefinition(_matStr, _geoStr)
        else:
            return _radDefinition("", _geoStr)

    def radStringToFile(self, filePath, includeMaterials=False,
                        includeChildrenSurfaces=True):
        """Write HBZone Radiance definition to a file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/geo.rad)

        Returns:
            True in case of success. False in case of failure.
        """
        assert os.path.isdir(os.path.split(filePath)[0]), \
            "Cannot find %s." % os.path.split(filePath)[0]

        with open(filePath, "w") as outf:
            try:
                # The output of toRadString for a zone is a tuple
                outf.write("\n".join(self.toRadString(includeMaterials,
                                                      includeChildrenSurfaces)))
                return True
            except Exception as e:
                print "Failed to write %s to file:\n%s" % (self.name, e)
                return False
