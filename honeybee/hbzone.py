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
        geometry_rules: EnergyPlus geometry_rules. (default: "LowerLeftCorner";
            "CounterClockWise"; "Absolute")
        building_program: HBZone building program.
        zone_program: Specific program for this zone from the available building
            programs.
        is_conditioned: A boolean that indicates if the zone is conditioned.
            (default: True)
    """

    def __init__(self, name=None, origin=(0, 0, 0), geometry_rules=None,
                 building_program=None, zone_program=None, is_conditioned=True):
        """Init Honeybee Zone."""
        self.name = name
        """Zone name"""

        self.origin = origin
        """origin of the zone."""

        self.geometry_rules = geometry_rules

        self.building_program = building_program

        self.zone_program = zone_program

        self._surfaces = []

    @classmethod
    def from_ep_string(cls, ep_string, geometry_rules=None, building_program=None,
                      zone_program=None, is_conditioned=True):
        """Init Honeybee zone from an ep_string.

        Args:
            ep_string: The full ep_string for an EnergyPlus Zone.
        """
        # clean input ep_string - split based on comma
        segments = ep_string.replace("\t", "") \
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

        return cls(name, origin, geometry_rules, building_program, zone_program,
                   is_conditioned)

    @property
    def isHBZone(self):
        """Return True if a HBZone."""
        return True

    @property
    def name(self):
        """Retuen surface name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set name and isSetByUser property.

        Args:
            new_name: A name.
        """
        new_name = new_name or util.random_name()
        self._name = str(new_name)
        util.check_name(self._name)

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
    def geometry_rules(self):
        """Get and set global geometry rules for this zone."""
        return self._geometry_rules

    @geometry_rules.setter
    def geometry_rules(self, geometry_rules):
        if not geometry_rules:
            geometry_rules = GlobalGeometryRules()

        self._geometry_rules = geometry_rules

    @property
    def is_relative_system(self):
        """Return True if coordinate system is relative.

        To find the absolute coordinate values in a relative system you should
        add surface coordinates to zone origin.
        """
        return self.geometry_rules.system.lower() == "relative"

    @property
    def floors(self):
        """Get floor surfaces."""
        return tuple(srf for srf in self.surfaces if srf.is_floor)

    @property
    def walls(self):
        """Get wall surfaces."""
        return tuple(srf for srf in self.surfaces if srf.is_wall)

    @property
    def ceilings(self):
        """Get ceilings surfaces."""
        return tuple(srf for srf in self.surfaces if srf.is_ceiling)

    @property
    def surfaces(self):
        """Get list of HBSurfaces for this zone."""
        return self._surfaces

    @property
    def children_surfaces(self):
        """Get list of children Surfaces for this zone."""
        return tuple(childrenSurfaces
                     for srf in self.surfaces
                     for childrenSurfaces in srf.children_surfaces
                     )

    def add_surface(self, surface):
        """Add a surface to Honeybee zone."""
        assert hasattr(surface, "isHBSurface"), \
            "%s input is not a Honeybee surface." % str(surface)

        self._surfaces.append(surface)

        # update surface parent
        surface._parent = self

    @property
    def radiance_materials(self):
        """Get list of Radiance materials for zone including fenestration."""
        return set(tuple(material for srf in self.surfaces
                         for material in srf.radiance_materials))

    def to_rad_file(self):
        """Return a RadFile like object.

        Use this method to get easy access to radiance geometries and materials for this
        zone. For a full definition as a string use to_rad_string method.
        """
        return RadFile((srf for srf in self.surfaces))

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
        return self.to_rad_file().to_rad_string(mode, include_materials, flipped,
                                                blacked)

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
    def geometry(self):
        """Return zone geometry for visualization."""
        _geo = []
        for surface in self.surfaces:
            _geo.append(surface.geometry)
            if surface.has_child_surfaces:
                for childSurface in surface.children_surfaces:
                    _geo.append(childSurface.geometry)

        return _geo

    @property
    def profile(self):
        """Return zone profile for visualization."""
        _profile = []
        for surface in self.surfaces:
            _profile.append(surface.profile)
            if surface.has_child_surfaces:
                for childSurface in surface.children_surfaces:
                    _profile.append(childSurface.profile)

        return _profile

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Zone representation."""
        if self.zone_program and self.building_program:
            return "HBZone %s %s:%s" % (self.name, self.zone_program,
                                        self.building_program)
        else:
            return "HBZone: %s" % self.name
