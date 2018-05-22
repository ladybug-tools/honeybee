"""Radiance Ring.

http://radsite.lbl.gov/radiance/refer/ray.html#Ring
"""
from .geometrybase import RadianceGeometry
from ..datatype import RadianceNumber, RadianceTuple


class Ring(RadianceGeometry):
    """Radiance Ring.

    A ring is a circular disk given by its center, surface normal, and inner and outer
    radii:

        mod ring id
        0
        0
        8
                xcent   ycent   zcent
                xdir    ydir    zdir
                r0      r1


    """
    center_pt = RadianceTuple('center_pt', tuple_size=3, num_type=float)
    surface_normal = RadianceTuple('surface_normal', tuple_size=3, num_type=float)
    radius_inner = RadianceNumber('radius_inner', check_positive=True)
    radius_outer = RadianceNumber('radius_outer', check_positive=True)

    def __init__(self, name, center_pt=None, radius_inner=None,
                 surface_normal=None, radius_outer=None, modifier=None):
        """Radiance Ring.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            center_pt: Ring start center point as (x, y, z) (Default: (0, 0 ,0)).
            surface_normal: surface normal as (x, y, z) (Default: (0, 0 ,1)).
            radius_inner: Ring inner radius as a number (Default: 5).
            radius_outer: Ring outer radius as a number (Default: 10).
            modifier: Geometry modifier (Default: "void").
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.center_pt = center_pt or (0, 0, 0)
        self.radius_inner = radius_inner or 10
        self.surface_normal = surface_normal or (0, 0, 10)
        self.radius_outer = radius_outer or 0

        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance geometry from a string.

        If the geometry has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        x0, y0, z0, x1, y1, z1, r0, r1 = base_geometry_data[3:]

        return cls(name, (x0, y0, z0), (x1, y1, z1), r0, r1, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "ring", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "surface_normal": {"x": float, "y": float, "z": float},
            "radius_inner": float,
            "radius_outer": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        st_c = geo_json["center_pt"]
        end_c = geo_json["surface_normal"]
        return cls(name=geo_json["name"],
                   center_pt=(st_c["x"], st_c["y"], st_c["z"]),
                   surface_normal=(end_c["x"], end_c["y"], end_c["z"]),
                   radius_inner=geo_json["radius_inner"],
                   radius_outer=geo_json["radius_outer"],
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt[0], self.center_pt[1], self.center_pt[2],
             self.surface_normal[0], self.surface_normal[1], self.surface_normal[2],
             self.radius_inner, self.radius_outer]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "ring", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "surface_normal": {"x": float, "y": float, "z": float},
            "radius_inner": float,
            "radius_outer": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt": {"x": self.center_pt[0],
                          "y": self.center_pt[1],
                          "z": self.center_pt[2]},
            "surface_normal": {"x": self.surface_normal[0],
                               "y": self.surface_normal[1],
                               "z": self.surface_normal[2]},
            "radius_inner": self.radius_inner,
            "radius_outer": self.radius_outer
        }
