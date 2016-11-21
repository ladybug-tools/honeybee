"""Radiance Metal Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metal
"""
from _materialbase import RadianceMaterial


class MetalMaterial(RadianceMaterial):
    """Radiance metal material."""

    def __init__(self, name, rReflectance=0, gReflectance=0, bReflectance=0,
                 specularity=0, roughness=0, modifier="void"):
        """Create metal material.

        Attributes:
            name: Material name as a string. Do not use white space and special character.
            rReflectance: Reflectance for red. The value should be between 0 and 1 (Default: 0).
            gReflectance: Reflectance for green. The value should be between 0 and 1 (Default: 0).
            bReflectance: Reflectance for blue. The value should be between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1 are
                not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value of 0
                corresponds to a perfectly smooth surface, and a value of 1 would be a very rough
                surface. Roughness values greater than 0.2 are not very realistic. (Default: 0).
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = MetalMaterial("generic wall", .55, .65, .75)
            print wallMaterial
        """
        RadianceMaterial.__init__(self, name, materialType="metal", modifier="void")
        self.rReflectance = rReflectance
        """Reflectance for red. The value should be between 0 and 1 (Default: 0)."""
        self.gReflectance = gReflectance
        """Reflectance for green. The value should be between 0 and 1 (Default: 0)."""
        self.bReflectance = bReflectance
        """Reflectance for blue. The value should be between 0 and 1 (Default: 0)."""
        self.specularity = specularity
        """Fraction of specularity. Specularity fractions greater than 0.1 are not
           realistic (Default: 0)."""
        self.roughness = roughness
        """Roughness is specified as the rms slope of surface facets. A value of 0
           corresponds to a perfectly smooth surface, and a value of 1 would be a very rough
           surface. Roughness values greater than 0.2 are not very realistic. (Default: 0)."""

    @classmethod
    def bySingleReflectValue(cls, name, rgbReflectance=0, specularity=0,
                             roughness=0, modifier="void"):
        """Create metal material with single reflectance value.

        Attributes:
            name: Material name as a string. Do not use white space and special character.
            rgbReflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1 are
                not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value of 0
                corresponds to a perfectly smooth surface, and a value of 1 would be a very rough
                surface. Roughness values greater than 0.2 are not very realistic. (Default: 0).
            modifier: Material modifier (Default: "void").

        Usage:
            wallMaterial = MetalMaterial.bySingleReflectValue("generic wall", .55)
            print wallMaterial
        """
        return cls(name, rReflectance=rgbReflectance, gReflectance=rgbReflectance,
                   bReflectance=rgbReflectance, specularity=specularity,
                   roughness=roughness, modifier="void")

    @property
    def rReflectance(self):
        """Red reflectance."""
        return self.__r

    @rReflectance.setter
    def rReflectance(self, value):
        assert 0 <= value <= 1, "Red reflectance should be between 0 and 1"
        self.__r = value

    @property
    def gReflectance(self):
        """Green reflectance."""
        return self.__g

    @gReflectance.setter
    def gReflectance(self, value):
        assert 0 <= value <= 1, "Green reflectance should be between 0 and 1"
        self.__g = value

    @property
    def bReflectance(self):
        """Blue reflectance."""
        return self.__b

    @bReflectance.setter
    def bReflectance(self, value):
        assert 0 <= value <= 1, "Blue reflectance should be between 0 and 1"
        self.__b = value

    @property
    def specularity(self):
        """Specularity fraction."""
        return self.__spec

    @specularity.setter
    def specularity(self, value):
        assert 0 <= value <= 1, "Specularity should be between 0 and 1"
        if value > 0.1:
            print "Warning: Specularity values above .1 is uncommon."
        self.__spec = value

    @property
    def roughness(self):
        """Roughness."""
        return self.__rough

    @roughness.setter
    def roughness(self, value):
        assert 0 <= value <= 1, "Roughness should be between 0 and 1"
        if value > 0.2:
            print "Warning: Roughness values above .2 is uncommon."
        self.__rough = value

    @property
    def averageReflectance(self):
        """Calculate average reflectance of metal material."""
        return (0.265 * self.rReflectance + 0.670 * self.gReflectance +
                0.065 * self.bReflectance) * (1 - self.specularity) + self.specularity

    def toRadString(self, minimal=False):
        """Return full radiance definition."""
        __baseString = self.headLine + "0\n0\n5 %.3f %.3f %.3f %.3f %.3f"

        metalDefinition = __baseString % (
            self.rReflectance, self.gReflectance, self.bReflectance,
            self.specularity, self.roughness
        )

        return metalDefinition.replace("\n", " ") if minimal else metalDefinition


if __name__ == "__main__":
    # some test code
    panelMaterial = MetalMaterial.bySingleReflectValue("generic wall", .55)
    print panelMaterial

    panelMaterial = MetalMaterial("generic wall", .55, .65, .75)
    print panelMaterial
