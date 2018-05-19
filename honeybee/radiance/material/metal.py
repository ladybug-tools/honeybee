"""Radiance Metal Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metal
"""
from materialbase import RadianceMaterial
from ..datatype import RadianceNumber


class Metal(RadianceMaterial):
    """Radiance metal material."""

    r_reflectance = RadianceNumber('r_reflectance', num_type=float, valid_range=(0, 1))
    g_reflectance = RadianceNumber('g_reflectance', num_type=float, valid_range=(0, 1))
    b_reflectance = RadianceNumber('b_reflectance', num_type=float, valid_range=(0, 1))
    specularity = RadianceNumber('specularity', num_type=float, valid_range=(0, 1))
    roughness = RadianceNumber('roughness', num_type=float, valid_range=(0, 1))

    def __init__(self, name, r_reflectance=0, g_reflectance=0, b_reflectance=0,
                 specularity=0.9, roughness=0, modifier="void"):
        """Create metal material.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            r_reflectance: Reflectance for red. The value should be between 0 and 1
                (Default: 0).
            g_reflectance: Reflectance for green. The value should be between 0 and 1
                (Default: 0).
            b_reflectance: Reflectance for blue. The value should be between 0 and 1
                (Default: 0).
            specularity: Fraction of specularity. Specularity of metals is usually .9
                or greater (Default: 0.9).
            roughness: Roughness is specified as the rms slope of surface facets.
                A value of 0 corresponds to a perfectly smooth surface, and a value of
                1 would be a very rough surface. Roughness values greater than 0.2 are
                not very realistic. (Default: 0).
            modifier: Material modifier (Default: "void").
        """
        RadianceMaterial.__init__(self, name, modifier=modifier)
        self.r_reflectance = r_reflectance
        """Reflectance for red. The value should be between 0 and 1 (Default: 0)."""
        self.g_reflectance = g_reflectance
        """Reflectance for green. The value should be between 0 and 1 (Default: 0)."""
        self.b_reflectance = b_reflectance
        """Reflectance for blue. The value should be between 0 and 1 (Default: 0)."""
        self.specularity = specularity
        """Fraction of specularity. Specularity fractions greater than 0.1 are not
           realistic (Default: 0.9)."""
        self.roughness = roughness
        """Roughness is specified as the rms slope of surface facets. A value of 0
           corresponds to a perfectly smooth surface, and a value of 1 would be a very
           rough surface. Roughness values greater than 0.2 are not very realistic.
           (Default: 0)."""
        self._update_values()

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be partof the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__.lower(), material_string, modifier)

        _, _, _, r_reflectance, g_reflectance, b_reflectance, \
            specularity, roughness = base_material_data

        return cls(name, r_reflectance, g_reflectance, b_reflectance, specularity,
                   roughness, modifier)

    @classmethod
    def from_json(cls, rec_json):
        """Make radiance material from json
        {
            "modifier": modifier,
            "type": "metal", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float // Material roughness
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), rec_json)

        return cls(name=rec_json["name"],
                   r_reflectance=rec_json["r_reflectance"],
                   g_reflectance=rec_json["g_reflectance"],
                   b_reflectance=rec_json["b_reflectance"],
                   specularity=rec_json["specularity"],
                   roughness=rec_json["roughness"],
                   modifier=modifier)

    @classmethod
    def by_single_reflect_value(cls, name, rgb_reflectance=0, specularity=0,
                                roughness=0, modifier="void"):
        """Create metal material with single reflectance value.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1
                are not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value
                of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
                a very rough surface. Roughness values greater than 0.2 are not very
                realistic. (Default: 0).
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = Metal.by_single_reflect_value("generic wall", .55)
            print(wallMaterial)
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, specularity=specularity,
                   roughness=roughness, modifier=modifier)

    @property
    def average_reflectance(self):
        """Calculate average reflectance of metal material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance) * (1 - self.specularity) + self.specularity

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness
        ]
        if self.specularity < 0.9:
            print("Warning: Specularity of metals is usually .9 or greater.")
        if self.roughness > 0.2:
            print("Warning: Roughness values above .2 is uncommon.")

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "metal", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float // Material roughness
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "metal",
            "name": self.name,
            "r_reflectance": self.r_reflectance,
            "g_reflectance": self.g_reflectance,
            "b_reflectance": self.b_reflectance,
            "specularity": self.specularity,
            "roughness": self.roughness
        }
