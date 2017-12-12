"""Radiance Plastic Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plastic
"""
from _materialbase import RadianceMaterial


class PlasticMaterial(RadianceMaterial):
    """Radiance plastic material."""

    def __init__(self, name, r_reflectance=0, g_reflectance=0, b_reflectance=0,
                 specularity=0, roughness=0, modifier="void"):
        """Create plastic material.

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
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = PlasticMaterial("generic wall", .55, .65, .75)
            print(wallMaterial)
        """
        RadianceMaterial.__init__(self, name, material_type="plastic", modifier="void")
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

    @classmethod
    def by_single_reflect_value(cls, name, rgb_reflectance=0, specularity=0,
                                roughness=0, modifier="void"):
        """Create plastic material with single reflectance value.

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
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = PlasticMaterial.by_single_reflect_value("generic wall", .55)
            print(wallMaterial)
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, specularity=specularity,
                   roughness=roughness, modifier="void")

    @property
    def r_reflectance(self):
        """Red reflectance."""
        return self._r

    @r_reflectance.setter
    def r_reflectance(self, value):
        assert 0 <= value <= 1, "Red reflectance should be between 0 and 1"
        self._r = value

    @property
    def g_reflectance(self):
        """Green reflectance."""
        return self._g

    @g_reflectance.setter
    def g_reflectance(self, value):
        assert 0 <= value <= 1, "Green reflectance should be between 0 and 1"
        self._g = value

    @property
    def b_reflectance(self):
        """Blue reflectance."""
        return self._b

    @b_reflectance.setter
    def b_reflectance(self, value):
        assert 0 <= value <= 1, "Blue reflectance should be between 0 and 1"
        self._b = value

    @property
    def specularity(self):
        """Specularity fraction."""
        return self._spec

    @specularity.setter
    def specularity(self, value):
        assert 0 <= value <= 1, "Specularity should be between 0 and 1"
        if value > 0.1:
            print("Warning: Specularity values above .1 is uncommon.")
        self._spec = value

    @property
    def roughness(self):
        """Roughness."""
        return self._rough

    @roughness.setter
    def roughness(self, value):
        assert 0 <= value <= 1, "Roughness should be between 0 and 1"
        if value > 0.2:
            print("Warning: Roughness values above .2 is uncommon.")
        self._rough = value

    @property
    def average_reflectance(self):
        """Calculate average reflectance of plastic material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance) * (1 - self.specularity) + self.specularity

    def to_rad_string(self, minimal=False):
        """Return full radiance definition."""
        base_string = self.head_line + "0\n0\n5 %.3f %.3f %.3f %.3f %.3f"

        plastic_definition = base_string % (
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness
        )

        return plastic_definition.replace("\n", " ") if minimal else plastic_definition


class BlackMaterial(PlasticMaterial):
    """Radiance black plastic material."""

    def __init__(self, name='black'):
        PlasticMaterial.__init__(self, name)


if __name__ == "__main__":
    # some test code
    wallMaterial = PlasticMaterial.by_single_reflect_value("generic wall", .55)
    print(wallMaterial)

    wallMaterial = PlasticMaterial("generic wall", .55, .65, .75)
    print(wallMaterial)

    print(BlackMaterial())
