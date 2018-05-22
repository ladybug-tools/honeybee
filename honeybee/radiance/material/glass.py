"""Radiance Glass Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
import math
from materialbase import RadianceMaterial
from ..datatype import RadianceNumber


class Glass(RadianceMaterial):
    """Radiance glass material."""

    r_transmittance = \
        RadianceNumber('r_transmittance', num_type=float, valid_range=(0, 1))
    g_transmittance = \
        RadianceNumber('g_transmittance', num_type=float, valid_range=(0, 1))
    b_transmittance = \
        RadianceNumber('b_transmittance', num_type=float, valid_range=(0, 1))
    refraction_index = \
        RadianceNumber('refraction_index', num_type=float, check_positive=True)

    def __init__(self, name, r_transmittance=0.0, g_transmittance=0.0,
                 b_transmittance=0.0, refraction_index=1.52, modifier="void"):
        """Create glass material.

        Attributes:
            name: Material name as a string. Do not use white space and special character
            r_transmittance: Transmittance for red. The value should be between 0 and 1
                (Default: 0).
            g_transmittance: Transmittance for green. The value should be between 0 and 1
                (Default: 0).
            b_transmittance: Transmittance for blue. The value should be between 0 and 1
                (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").

        Usage:
            glassMaterial = Glass("generic glass", .65, .65, .65)
            print(glassMaterial)
        """
        RadianceMaterial.__init__(self, name, modifier=modifier)
        self.r_transmittance = float(r_transmittance)
        """Transmittance for red. The value should be between 0 and 1 (Default: 0)."""
        self.g_transmittance = float(g_transmittance)
        """Transmittance for green. The value should be between 0 and 1 (Default: 0)."""
        self.b_transmittance = float(b_transmittance)
        """Transmittance for blue. The value should be between 0 and 1 (Default: 0)."""
        self.refraction_index = float(refraction_index)
        """Index of refraction. 1.52 for glass and 1.4 for ETFE (Default: 1.52)."""
        self._update_values()

    @classmethod
    def from_json(cls, rec_json):
        """Make radiance material from json
        {
            "name": "", // Material Name
            "r_transmittance": float, // Transmittance for red
            "g_transmittance": float, // Transmittance for green
            "b_transmittance": float, // Transmittance for blue
            "refraction": float, // Index of refraction
            "modifier": "" // material modifier (Default: "void")
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), rec_json)
        return cls(name=rec_json["name"],
                   r_transmittance=rec_json["r_transmittance"],
                   g_transmittance=rec_json["g_transmittance"],
                   b_transmittance=rec_json["b_transmittance"],
                   refraction_index=rec_json["refraction_index"],
                   modifier=modifier)

    @classmethod
    def by_single_trans_value(cls, name, rgb_transmittance=0,
                              refraction_index=1.52, modifier="void"):
        """Create glass material with single transmittance value.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            rgb_transmittance: Transmittance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").

        Usage:
            glassMaterial = Glass.by_single_trans_value("generic glass", .65)
            print(glassMaterial)
        """
        return cls(
            name, r_transmittance=rgb_transmittance, g_transmittance=rgb_transmittance,
            b_transmittance=rgb_transmittance, refraction_index=refraction_index,
            modifier=modifier)

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__.lower(), material_string, modifier)

        if len(base_material_data) == 6:
            r_transmittance, g_transmittance, b_transmittance = base_material_data[3:]
            refraction = 1.52
        else:
            r_transmittance, g_transmittance, b_transmittance, refraction = \
                base_material_data[3:]

        return cls(name, r_transmittance, g_transmittance, b_transmittance, refraction,
                   modifier)

    @property
    def average_transmittance(self):
        """Calculate average transmittance."""
        return 0.265 * self.r_transmittance + \
            0.670 * self.g_transmittance + 0.065 * self.b_transmittance

    @staticmethod
    def get_transmissivity(transmittance):
        """Calculate transmissivity based on transmittance value.

        "Transmissivity is the amount of light not absorbed in one traversal of
        the material. Transmittance -- the value usually measured - is the total
        light transmitted through the pane including multiple reflections."
        """
        if transmittance == 0:
            return 0
        return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) -
                0.9166530661) / 0.0036261119 / transmittance

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = [
            self.get_transmissivity(self.r_transmittance),
            self.get_transmissivity(self.g_transmittance),
            self.get_transmissivity(self.b_transmittance),
            self.refraction_index
        ]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "glass", // Material type
            "name": "", // Material Name
            "r_transmittance": float, // Transmittance for red
            "g_transmittance": float, // Transmittance for green
            "b_transmittance": float, // Transmittance for blue
            "refraction_index": float, // Index of refraction
            "modifier": "" // material modifier (Default: "void")
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "glass",
            "name": self.name,
            "r_transmittance": self.r_transmittance,
            "g_transmittance": self.g_transmittance,
            "b_transmittance": self.b_transmittance,
            "refraction_index": self.refraction_index
        }


if __name__ == "__main__":
    # some test code
    glassMaterial = Glass.by_single_trans_value("generic glass", .65)
    print(glassMaterial)
    print(glassMaterial.to_rad_string(minimal=True))
