import utilcol as util
from hbobject import HBObject
from vectormath.euclid import Point3
from radiance.radfile import RadFile
from energyplus.geometryrules import GlobalGeometryRules

import os


class HBZone(HBObject):
    """Honeybee base class.

    Args:
        name: Unique name for this zone.
        origin: Zone origin point (default: 0, 0, 0)
        geometryRules: EnergyPlus geometryRules. (default: "LowerLeftCorner";
            "CounterClockWise"; "Absolute")
        buildingProgram: HBZone building program.
        zoneProgram: Specific program for this zone from the available building
            programs.
        isConditioned: A boolean that indicates if the zone is conditioned.
            (default: True)
    """

    def __init__(self, name=None, origin=(0, 0, 0), geometryRules=None,
                 buildingProgram=None, zoneProgram=None, isConditioned=True):
        """Init Honeybee Zone."""
        self.name = name
        """Zone name"""

        self.origin = origin
        """origin of the zone."""

        self.geometryRules = geometryRules

        self.buildingProgram = buildingProgram

        self.zoneProgram = zoneProgram

        self._surfaces = []

    @classmethod
    def fromEPString(cls, EPString, geometryRules=None, buildingProgram=None,
                     zoneProgram=None, isConditioned=True):
        """Init Honeybee zone from an EPString.

        Args:
            EPString: The full EPString for an EnergyPlus Zone.
        """
        # clean input EPString - split based on comma
        segments = EPString.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        name = segments[1]
        try:
            north, x, y, z = segments[2:6]
        except Exception:
            x, y, z = 0, 0, 0

        try:
            origin = map(float, (x, y, z))
        except ValueError:
            origin = 0, 0, 0

        return cls(name, origin, geometryRules, buildingProgram, zoneProgram,
                   isConditioned)

    @property
    def isHBZone(self):
        """Return True if a HBZone."""
        return True

    @property
    def name(self):
        """Retuen surface name."""
        return self._name

    @name.setter
    def name(self, newName):
        """Set name and isSetByUser property.

        Args:
            newName: A name.
        """
        newName = newName or util.randomName()
        self._name = str(newName)
        util.checkName(self._name)

    @property
    def origin(self):
        """Get set origin of the zone."""
        return self._origin

    @origin.setter
    def origin(self, value):
        try:
            self._origin = Point3(*value)
        except Exception as e:
            raise ValueError("Failed to set zone origin: {}".format(e))

    @property
    def geometryRules(self):
        """Get and set global geometry rules for this zone."""
        return self._geometryRules

    @geometryRules.setter
    def geometryRules(self, geometryRules):
        if not geometryRules:
            geometryRules = GlobalGeometryRules()

        self._geometryRules = geometryRules

    @property
    def isRelativeSystem(self):
        """Return True if coordinate system is relative.

        To find the absolute coordinate values in a relative system you should
        add surface coordinates to zone origin.
        """
        return self.geometryRules.system.lower() == "relative"

    @property
    def floors(self):
        """Get floor surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isFloor)

    @property
    def walls(self):
        """Get wall surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isWall)

    @property
    def ceilings(self):
        """Get ceilings surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isCeiling)

    @property
    def surfaces(self):
        """Get list of HBSurfaces for this zone."""
        return self._surfaces

    @property
    def childrenSurfaces(self):
        """Get list of children Surfaces for this zone."""
        return tuple(childrenSurfaces
                     for srf in self.surfaces
                     for childrenSurfaces in srf.childrenSurfaces
                     )

    def addSurface(self, HBSurface):
        """Add a surface to Honeybee zone."""
        assert hasattr(HBSurface, "isHBSurface"), \
            "%s input is not a Honeybee surface." % str(HBSurface)

        self._surfaces.append(HBSurface)

        # update surface parent
        HBSurface._parent = self

    @property
    def radianceMaterials(self):
        """Get list of Radiance materials for zone including fenestration."""
        return set(tuple(material for srf in self.surfaces
                         for material in srf.radianceMaterials))

    def toRadFile(self):
        """Return a RadFile like object.

        Use this method to get easy access to radiance geometries and materials for this
        zone. For a full definition as a string use toRadString method.
        """
        return RadFile((srf for srf in self.surfaces))

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
        return self.toRadFile().toRadString(mode, includeMaterials, flipped, blacked)

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
    def geometry(self):
        """Return zone geometry for visualization."""
        _geo = []
        for surface in self.surfaces:
            _geo.append(surface.geometry)
            if surface.hasChildSurfaces:
                for childSurface in surface.childrenSurfaces:
                    _geo.append(childSurface.geometry)

        return _geo

    @property
    def profile(self):
        """Return zone profile for visualization."""
        _profile = []
        for surface in self.surfaces:
            _profile.append(surface.profile)
            if surface.hasChildSurfaces:
                for childSurface in surface.childrenSurfaces:
                    _profile.append(childSurface.profile)

        return _profile

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Zone representation."""
        if self.zoneProgram and self.buildingProgram:
            return "HBZone %s %s:%s" % (self.name, self.zoneProgram,
                                        self.buildingProgram)
        else:
            return "HBZone: %s" % self.name
