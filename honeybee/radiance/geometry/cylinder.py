"""Radiance Cylinder.

http://radsite.lbl.gov/radiance/refer/ray.html#Cylinder
"""
from .geometrybase import RadianceGeometry
from ..datatype import RadianceNumber, RadianceTuple


class Cylinder(RadianceGeometry):
    """Radiance Cylinder.

    A cylinder is like a cone, but its starting and ending radii are equal.

        mod cylinder id
        0
        0
        7
                x0      y0      z0
                x1      y1      z1
                rad
    """
    center_pt_start = RadianceTuple('center_pt_start', tuple_size=3, num_type=float)
    center_pt_end = RadianceTuple('center_pt_end', tuple_size=3, num_type=float)
    radius = RadianceNumber('radius', check_positive=True)

    def __init__(self, name, center_pt_start=None, center_pt_end=None, radius=None,
                 modifier=None):
        """Radiance Cylinder.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            center_pt_start: Cylinder start center point as (x, y, z)
                (Default: (0, 0 ,0)).
            center_pt_end: Cylinder end center point as (x, y, z) (Default: (0, 0 ,10)).
            radius: Cylinder start radius as a number (Default: 10).
            modifier: Geometry modifier (Default: "void").
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.center_pt_start = center_pt_start or (0, 0, 0)
        self.center_pt_end = center_pt_end or (0, 0, 10)
        self.radius = radius or 10

        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance geometry from a string.

        If the geometry has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        x0, y0, z0, x1, y1, z1, r0 = base_geometry_data[3:]

        return cls(name, (x0, y0, z0), (x1, y1, z1), r0, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "cylinder", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        st_c = geo_json["center_pt_start"]
        end_c = geo_json["center_pt_end"]
        return cls(name=geo_json["name"],
                   center_pt_start=(st_c["x"], st_c["y"], st_c["z"]),
                   center_pt_end=(end_c["x"], end_c["y"], end_c["z"]),
                   radius=geo_json["radius"],
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt_start[0], self.center_pt_start[1], self.center_pt_start[2],
             self.center_pt_end[0], self.center_pt_end[1], self.center_pt_end[2],
             self.radius]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "cylinder", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt_start": {"x": self.center_pt_start[0],
                                "y": self.center_pt_start[1],
                                "z": self.center_pt_start[2]},
            "center_pt_end": {"x": self.center_pt_end[0],
                              "y": self.center_pt_end[1],
                              "z": self.center_pt_end[2]},
            "radius": self.radius
        }
