"""Radiance Trans Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Trans
https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf
"""
from .materialbase import RadianceMaterial
from ..datatype import RadianceNumber


class Trans(RadianceMaterial):
    """Radiance translucent material."""

    r_reflectance = RadianceNumber('r_reflectance', num_type=float, valid_range=(0, 1))
    g_reflectance = RadianceNumber('g_reflectance', num_type=float, valid_range=(0, 1))
    b_reflectance = RadianceNumber('b_reflectance', num_type=float, valid_range=(0, 1))
    specularity = RadianceNumber('specularity', num_type=float, valid_range=(0, 1))
    roughness = RadianceNumber('roughness', num_type=float, valid_range=(0, 1))
    transmitted_diff = \
        RadianceNumber('transmitted_diff', num_type=float, valid_range=(0, 1))
    transmitted_spec = \
        RadianceNumber('transmitted_spec', num_type=float, valid_range=(0, 1))

    def __init__(self, name, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
                 specularity=0.0, roughness=0.0, transmitted_diff=0.0,
                 transmitted_spec=0.0, modifier="void"):
        """Create trans material.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            r_reflectance: Reflectance for red. The value should be between 0 and 1
                (Default: 0).
            g_reflectance: Reflectance for green. The value should be between 0 and 1
                (Default: 0).
            b_reflectance: Reflectance for blue. The value should be between 0 and 1
                (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1
                are not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A
                value of 0 corresponds to a perfectly smooth surface, and a value of 1
                would be a very rough surface. Roughness values greater than 0.2 are not
                very realistic. (Default: 0).
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
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
           realistic (Default: 0)."""
        self.roughness = roughness
        """Roughness is specified as the rms slope of surface facets. A value of 0
           corresponds to a perfectly smooth surface, and a value of 1 would be a
           very rough surface. Roughness values greater than 0.2 are not very realistic.
           (Default: 0)."""
        self.transmitted_diff = transmitted_diff
        self.transmitted_spec = transmitted_spec
        self._update_values()

    @classmethod
    def from_reflected_spacularity(
            cls, name, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
            reflected_spacularity=0.0, roughness=0.0, transmitted_diff=0.0,
            transmitted_spec=0.0, modifier="void"):
        """Create trans material from reflected spacularityself.

        See:
        https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            r_reflectance: Reflectance for red. The value should be between 0 and 1
                (Default: 0).
            g_reflectance: Reflectance for green. The value should be between 0 and 1
                (Default: 0).
            b_reflectance: Reflectance for blue. The value should be between 0 and 1
                (Default: 0).
            reflected_spacularity: Fraction of reflected spacular. The reflected
                specularity of common uncoated glass is around .06, Matte = min 0,
                Satin = suggested max 0.07 (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A
                value of 0 corresponds to a perfectly smooth surface, and a value of 1
                would be a very rough surface. Roughness values greater than 0.2 are not
                very realistic. (Default: 0).
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: "void").
        """
        cr, cg, cb, rs, roughness, td, ts = \
            r_reflectance, g_reflectance, b_reflectance, reflected_spacularity, \
            roughness, transmitted_diff, transmitted_spec

        rd = (0.265 * cr + 0.670 * cg + 0.065 * cb)

        absorb = 1 - td - ts - rd - rs

        if absorb < 0:
            summ = td + ts + rd + rs
            msg = 'Sum of Diffuse Transmission (%.3f), Specular Transmission (%.3f),' \
                'Specular Reflection (%.3f) and Diffuse Reflection (%.3f) cannot be ' \
                'more than 1 (%.3f).' % (td, ts, rs, rd, summ)
            raise ValueError(msg)

        # calculate the material
        a7 = ts / (td + ts)
        a6 = (td + ts) / (rd + td + ts)
        a5 = roughness
        a4 = rs
        a3 = cb / ((1 - rs) * (1 - a6))
        a2 = cg / ((1 - rs) * (1 - a6))
        a1 = cr / ((1 - rs) * (1 - a6))

        if a3 > 1 or a2 > 1 or a1 > 1:
            raise ValueError(
                'This material is physically impossible to create!\n'
                'You need to adjust the inputs for diffuse reflectance values.')

        return(cls, name, a1, a2, a3, a4, a5, a6, a7, modifier)

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be partof the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__.lower(), material_string, modifier)

        _, _, _, r_reflectance, g_reflectance, b_reflectance, specularity, \
            roughness, transmitted_diff, transmitted_spec = base_material_data

        return cls(name, r_reflectance, g_reflectance, b_reflectance, specularity,
                   roughness, transmitted_diff, transmitted_spec, modifier)

    @classmethod
    def from_json(cls, rec_json):
        """Make radiance material from json
        {
            "modifier": {} or void, // Material modifier
            "type": "trans", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "transmitted_diff": float,
            "transmitted_spec": float
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), rec_json)
        return cls(name=rec_json["name"],
                   r_reflectance=rec_json["r_reflectance"],
                   g_reflectance=rec_json["g_reflectance"],
                   b_reflectance=rec_json["b_reflectance"],
                   specularity=rec_json["specularity"],
                   roughness=rec_json["roughness"],
                   transmitted_diff=rec_json["transmitted_diff"],
                   transmitted_spec=rec_json["transmitted_spec"],
                   modifier=modifier)

    @classmethod
    def by_single_reflect_value(cls, name, rgb_reflectance=0.0, specularity=0.0,
                                roughness=0.0, transmitted_diff=0.0,
                                transmitted_spec=0.0, modifier="void"):
        """Create trans material with single reflectance value.

        Attributes:
            name: Material name as a string. Do not use white space and special character
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1
                are not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value
                of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
                a very rough surface. Roughness values greater than 0.2 are not very
                realistic. (Default: 0).
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = trans.by_single_reflect_value("generic wall", .55)
            print(wallMaterial)
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, specularity=specularity,
                   roughness=roughness, transmitted_diff=transmitted_diff,
                   transmitted_spec=transmitted_spec, modifier=modifier)

    @property
    def average_reflectance(self):
        """Calculate average reflectance of trans material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance) * (1 - self.specularity) + self.specularity

    @property
    def specular_sampling_threshold(self):
        """Specular sampling threshold (-st)."""
        return self.transmitted_diff * self.transmitted_spec * \
            (1 - (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                  0.065 * self.b_reflectance)) * self.specularity

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness, self.transmitted_diff,
            self.transmitted_spec
        ]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "trans", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "transmitted_diff": float,
            "transmitted_spec": float
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "trans",
            "name": self.name,
            "r_reflectance": self.r_reflectance,
            "g_reflectance": self.g_reflectance,
            "b_reflectance": self.b_reflectance,
            "specularity": self.specularity,
            "roughness": self.roughness,
            "transmitted_diff": self.transmitted_diff,
            "transmitted_spec": self.transmitted_spec
        }
