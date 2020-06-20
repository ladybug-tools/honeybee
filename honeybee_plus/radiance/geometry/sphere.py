"""Radiance Sphere.

http://radsite.lbl.gov/radiance/refer/ray.html#Sphere
"""
from .geometrybase import RadianceGeometry
from ..datatype import RadianceNumber, RadianceTuple


class Sphere(RadianceGeometry):
    """Radiance Sphere.

    mod sphere id
    0
    0
    4 xcent ycent zcent radius
    """
    center_pt = RadianceTuple('center_pt', tuple_size=3, num_type=float)
    radius = RadianceNumber('radius', check_positive=True)

    def __init__(self, name, center_pt=None, radius=None, modifier=None):
        """Radiance Sphere.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            center_pt: Sphere center point as (x, y, z) (Default: (0, 0 ,0)).
            radius: Sphere radius as a number (Default: 1).
            modifier: Geometry modifier (Default: "void").

        Usage:
            sphere = Sphere("test_sphere", (0, 0, 10), 10)
            print(sphere)
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.center_pt = center_pt or (0, 0, 0)
        self.radius = radius or 1

        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        cx, cy, cz, radius = base_geometry_data[3:]

        return cls(name, (cx, cy, cz), radius, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "sphere", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "radius": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        center_data = geo_json["center_pt"]
        return cls(name=geo_json["name"],
                   center_pt=(center_data["x"], center_data["y"], center_data["z"]),
                   radius=geo_json["radius"],
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt[0], self.center_pt[1], self.center_pt[2], self.radius]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "sphere", // Geometry type
            "modifier": {} or void, // Modifier
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "radius": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "radius": self.radius,
            "center_pt": {"x": self.center_pt[0],
                          "y": self.center_pt[1],
                          "z": self.center_pt[2]}
        }
