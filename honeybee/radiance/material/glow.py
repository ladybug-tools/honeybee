"""Radiance Glow Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glow
"""

from ..datatype import RadianceNumber
from .materialbase import RadianceMaterial


class Glow(RadianceMaterial):
    """
    Create glow material.

    Attributes:

        name: Material name as a string. The name should not have whitespaces or
            special characters.
        red: A positive value for the Red channel of the glow (default: 0).
        green: A positive value for the Green channel of the glow (default: 0).
        blue: A positive value for the Blue channel of the glow (default: 0).
        max_radius: a maximum radius for shadow testing (default: 0). If maxrad is zero,
            then the surface will never be tested for shadow, although it may
            participate in an interreflection calculation. If maxrad is negative, then
            the surface will never contribute to scene illumination. Glow sources will
            never illuminate objects on the other side of an illum surface. This
            provides a convenient way to illuminate local light fixture geometry without
            overlighting nearby objects.
    """
    red = RadianceNumber('red', num_type=float, valid_range=(0, 1000000))
    green = RadianceNumber('green', num_type=float, valid_range=(0, 1000000))
    blue = RadianceNumber('blue', num_type=float, valid_range=(0, 1000000))
    max_radius = RadianceNumber('max_radius', num_type=float)

    def __init__(self, name, red=0.0, green=0.0, blue=0.0, max_radius=0.0,
                 modifier='void'):
        """Init Glow material."""
        RadianceMaterial.__init__(self, name, modifier=modifier)
        self.red = red
        """A positive value for the Red channel of the glow"""
        self.green = green
        """A positive value for the Green channel of the glow"""
        self.blue = blue
        """A positive value for the Blue channel of the glow"""
        self.max_radius = max_radius
        """Maximum radius for shadow testing"""
        self._update_values()

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be partof the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__.lower(), material_string, modifier)

        _, _, _, red, green, blue, radius = base_material_data

        return cls(name, red, green, blue, radius, modifier)

    @classmethod
    def from_json(cls, rec_json):
        """Make radiance material from json
        {
            "name": "", // Material Name
            "red": float, // A positive value for the Red channel of the glow
            "green": float, // A positive value for the Green channel of the glow
            "blue": float, // A positive value for the Blue channel of the glow
            "radius": float // Maximum radius for shadow testing
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), rec_json)

        return cls(name=rec_json["name"],
                   red=rec_json["red"],
                   green=rec_json["green"],
                   blue=rec_json["blue"],
                   max_radius=rec_json["max_radius"],
                   modifier=modifier)

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.red, self.green, self.blue, self.max_radius
        ]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "glow", // Material type
            "name": "", // Material Name
            "red": float, // A positive value for the Red channel of the glow
            "green": float, // A positive value for the Green channel of the glow
            "blue": float, // A positive value for the Blue channel of the glow
            "radius": float // Maximum radius for shadow testing
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "glow",
            "name": self.name,
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "max_radius": self.max_radius
        }


class WhiteGlow(Glow):
    """A white glow material.

    Use this material for multi-phase daylight studies.
    """

    def __init__(self, name='white_glow'):
        """Create glow material."""
        Glow.__init__(self, name, 1.0, 1.0, 1.0, 0.0)
