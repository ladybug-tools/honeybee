"""Radiance Light Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Light
"""

from ..datatype import RadianceNumber
from .materialbase import RadianceMaterial


class Light(RadianceMaterial):

    red = RadianceNumber('red', num_type=float, check_positive=True)
    blue = RadianceNumber('blue', num_type=float, check_positive=True)
    green = RadianceNumber('green', num_type=float, check_positive=True)

    def __init__(self, name, red=0.0, green=0.0, blue=0.0, modifier='void'):
        """
        Create light material
        Attributes:

            name: Material name as a string. The name should not have whitespaces or
                special characters.
            red: A positive value for the Red channel of the light (default: 0).
            green: A positive value for the Green channel of the light (default: 0).
            blue: A positive value for the Blue channel of the light (default: 0).
            modifier: Material modifier. The default value is void.
        """
        RadianceMaterial.__init__(self, name, modifier=modifier)
        self.red = red
        """A positive value for the Red channel of the light"""
        self.green = green
        """A positive value for the Green channel of the light"""
        self.blue = blue
        """A positive value for the Blue channel of the light"""
        self._update_values()

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be partof the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__.lower(), material_string, modifier)

        _, _, _, red, green, blue = base_material_data

        return cls(name, red, green, blue, modifier)

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
                   modifier=modifier)

    @classmethod
    def by_single_reflect_value(cls, name, rgb=0, modifier="void"):
        """Create light material with single value.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            rgb: Input for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: "void").

        Usage:
            sample_light = Light.by_single_reflect_value("sample_light", 1)
            print(sample_light)
        """
        return cls(name, red=rgb, green=rgb, blue=rgb, modifier=modifier)

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [self.red, self.green, self.blue]

    def to_json(self):
        """Translate radiance material to json
        {
            "modifier": modifier,
            "type": "light", // Material type
            "name": "", // Material Name
            "red": float, // A positive value for the Red channel of the glow
            "green": float, // A positive value for the Green channel of the glow
            "blue": float // A positive value for the Blue channel of the glow
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "light",
            "name": self.name,
            "red": self.red,
            "green": self.green,
            "blue": self.blue
        }
