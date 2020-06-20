"""Radiance Source.

http://radsite.lbl.gov/radiance/refer/ray.html#Source
"""
from .geometrybase import RadianceGeometry
from ..datatype import RadianceNumber, RadianceTuple


class Source(RadianceGeometry):
    """Radiance Source.

    A source is not really a surface, but a solid angle. It is used for specifying light
    sources that are very distant. The direction to the center of the source and the
    number of degrees subtended by its disk are given as follows:

    mod source id
    0
    0
    4 xdir ydir zdir angle
    """
    direction = RadianceTuple('direction', tuple_size=3, num_type=float)
    angle = RadianceNumber('angle', num_type=float, check_positive=True)

    def __init__(self, name, direction=None, angle=None, modifier=None):
        """Radiance Source.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            direction: A vector to set source direction (x, y, z) (Default: (0, 0 ,-1)).
            angle: Source solid angle (Default: 0.533).
            modifier: Geometry modifier (Default: "void").

        Usage:
            source = Source("test_source", (0, 0, 10), 10)
            print(source)
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.direction = direction or (0, 0, -1)
        self.angle = angle or 0.533

        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        cx, cy, cz, angle = base_geometry_data[3:]

        return cls(name, (cx, cy, cz), angle, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "source", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "direction": {"x": float, "y": float, "z": float},
            "angle": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        direction = geo_json["direction"]
        return cls(name=geo_json["name"],
                   direction=(direction["x"], direction["y"], direction["z"]),
                   angle=geo_json["angle"],
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.direction[0], self.direction[1], self.direction[2], self.angle]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "source", // Geometry type
            "modifier": {} or void, // Modifier
            "name": "", // Geometry Name
            "direction": {"x": float, "y": float, "z": float},
            "angle": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "source",
            "name": self.name,
            "angle": self.angle,
            "direction": {"x": self.direction[0],
                          "y": self.direction[1],
                          "z": self.direction[2]}
        }
