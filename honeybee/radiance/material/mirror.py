"""Radiance Mirror Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Mirror
"""
from .materialbase import RadianceMaterial
from ..datatype import RadianceNumber


class Mirror(RadianceMaterial):
    """Radiance mirror material."""

    r_reflectance = RadianceNumber('r_reflectance', num_type=float, valid_range=(0, 1))
    g_reflectance = RadianceNumber('g_reflectance', num_type=float, valid_range=(0, 1))
    b_reflectance = RadianceNumber('b_reflectance', num_type=float, valid_range=(0, 1))

    def __init__(self, name, r_reflectance=0.95, g_reflectance=0.95, b_reflectance=0.95,
                 modifier="void"):
        """Create mirror material.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            r_reflectance: Reflectance for red. The value should be between 0 and 1
                (Default: 0.95).
            g_reflectance: Reflectance for green. The value should be between 0 and 1
                (Default: 0.95).
            b_reflectance: Reflectance for blue. The value should be between 0 and 1
                (Default: 0.95).
            modifier: Material modifier (Default: "void").

        Usage:
            mirror_material = Mirror("mirror_mat", .95, .95, .95)
            print(mirror_material)
        """
        RadianceMaterial.__init__(self, name, modifier=modifier)
        self.r_reflectance = r_reflectance
        """Reflectance for red. The value should be between 0 and 1 (Default: 0)."""
        self.g_reflectance = g_reflectance
        """Reflectance for green. The value should be between 0 and 1 (Default: 0)."""
        self.b_reflectance = b_reflectance
        """Reflectance for blue. The value should be between 0 and 1 (Default: 0)."""
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
            "type": "mirror", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "modifier": modifier
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), rec_json)

        return cls(name=rec_json["name"],
                   r_reflectance=rec_json["r_reflectance"],
                   g_reflectance=rec_json["g_reflectance"],
                   b_reflectance=rec_json["b_reflectance"],
                   modifier=modifier)

    @classmethod
    def by_single_reflect_value(cls, name, rgb_reflectance=0, modifier="void"):
        """Create mirror material with single reflectance value.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = Mirror.by_single_reflect_value("generic wall", .55)
            print(wallMaterial)
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, modifier=modifier)

    @property
    def average_reflectance(self):
        """Calculate average reflectance of mirror material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance)

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [self.r_reflectance, self.g_reflectance, self.b_reflectance]

    def to_json(self):
        """Translate radiance material to json
        {
            "modifier": modifier,
            "type": "mirror", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float  // Reflectance for blue
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "mirror",
            "name": self.name,
            "r_reflectance": self.r_reflectance,
            "g_reflectance": self.g_reflectance,
            "b_reflectance": self.b_reflectance
        }


if __name__ == "__main__":
    # some test code
    panelMaterial = Mirror.by_single_reflect_value("mirror_mat", .9)
    print(panelMaterial)

    panelMaterial = Mirror("mirror_wall", .95, .95, .75)
    print(panelMaterial)
