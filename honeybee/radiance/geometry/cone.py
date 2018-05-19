"""Radiance Cone.

http://radsite.lbl.gov/radiance/refer/ray.html#Cone
"""
from .geometrybase import RadianceGeometry
from ..datatype import RadianceNumber, RadianceTuple


class Cone(RadianceGeometry):
    """Radiance Cone.

    A cone is a megaphone-shaped object. It is truncated by two planes perpendicular to
    its axis, and one of its ends may come to a point. It is given as two axis endpoints,
    and the starting and ending radii:

        mod cone id
        0
        0
        8
                x0      y0      z0
                x1      y1      z1
                r0      r1

    """
    center_pt_start = RadianceTuple('center_pt_start', tuple_size=3, num_type=float)
    radius_start = RadianceNumber('radius_start', check_positive=True)
    center_pt_end = RadianceTuple('center_pt_end', tuple_size=3, num_type=float)
    radius_end = RadianceNumber('radius_end', check_positive=True)

    def __init__(self, name, center_pt_start=None, radius_start=None,
                 center_pt_end=None, radius_end=None, modifier=None):
        """Radiance Cone.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            center_pt_start: Cone start center point as (x, y, z) (Default: (0, 0 ,0)).
            radius_start: Cone start radius as a number (Default: 10).
            center_pt_end: Cone end center point as (x, y, z) (Default: (0, 0 ,10)).
            radius_end: Cone end radius as a number (Default: 0).
            modifier: Geometry modifier (Default: "void").
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.center_pt_start = center_pt_start or (0, 0, 0)
        self.radius_start = radius_start or 10
        self.center_pt_end = center_pt_end or (0, 0, 10)
        self.radius_end = radius_end or 0

        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        x0, y0, z0, x1, y1, z1, r0, r1 = base_geometry_data[3:]

        return cls(name, (x0, y0, z0), r0, (x1, y1, z1), r1, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "radius_start": float,
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius_end": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        st_c = geo_json["center_pt_start"]
        end_c = geo_json["center_pt_end"]
        return cls(name=geo_json["name"],
                   center_pt_start=(st_c["x"], st_c["y"], st_c["z"]),
                   radius_start=geo_json["radius_start"],
                   center_pt_end=(end_c["x"], end_c["y"], end_c["z"]),
                   radius_end=geo_json["radius_end"],
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt_start[0], self.center_pt_start[1], self.center_pt_start[2],
             self.center_pt_end[0], self.center_pt_end[1], self.center_pt_end[2],
             self.radius_start, self.radius_end]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "radius_start": float,
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius_end": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "radius_start": self.radius_start,
            "center_pt_start": {"x": self.center_pt_start[0],
                                "y": self.center_pt_start[1],
                                "z": self.center_pt_start[2]},
            "radius_end": self.radius_end,
            "center_pt_end": {"x": self.center_pt_end[0],
                              "y": self.center_pt_end[1],
                              "z": self.center_pt_end[2]}
        }
