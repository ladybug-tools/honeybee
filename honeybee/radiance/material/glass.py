"""Radiance Glass Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
import math
from _materialbase import RadianceMaterial


class GlassMaterial(RadianceMaterial):
    """Radiance glass material."""

    def __init__(self, name, rTransmittance=0, gTransmittance=0, bTransmittance=0,
                 refraction=1.52, modifier="void"):
        """Create glass material.

        Attributes:
            name: Material name as a string. Do not use white space and special character
            rTransmittance: Transmittance for red. The value should be between 0 and 1
                (Default: 0).
            gTransmittance: Transmittance for green. The value should be between 0 and 1
                (Default: 0).
            bTransmittance: Transmittance for blue. The value should be between 0 and 1
                (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").

        Usage:
            glassMaterial = GlassMaterial("generic glass", .65, .65, .65)
            print glassMaterial
        """
        RadianceMaterial.__init__(self, name, materialType="glass", modifier="void")
        self.rTransmittance = rTransmittance
        """Transmittance for red. The value should be between 0 and 1 (Default: 0)."""
        self.gTransmittance = gTransmittance
        """Transmittance for green. The value should be between 0 and 1 (Default: 0)."""
        self.bTransmittance = bTransmittance
        """Transmittance for blue. The value should be between 0 and 1 (Default: 0)."""
        self.refractionIndex = refraction
        """Index of refraction. 1.52 for glass and 1.4 for ETFE (Default: 1.52)."""

    @classmethod
    def bySingleTransValue(cls, name, rgbTransmittance=0,
                           refraction=1.52, modifier="void"):
        """Create glass material with single transmittance value.

        Attributes:
            name: Material name as a string. Do not use white space and special
                character.
            rgbTransmittance: Transmittance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").

        Usage:
            glassMaterial = GlassMaterial.bySingleTransValue("generic glass", .65)
            print glassMaterial
        """
        return cls(
            name, rTransmittance=rgbTransmittance, gTransmittance=rgbTransmittance,
            bTransmittance=rgbTransmittance, refraction=1.52, modifier="void")

    @property
    def isGlassMaterial(self):
        """Indicate if this object has glass Material.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        return True

    @property
    def rTransmittance(self):
        """Red transmittance."""
        return self.__r

    @rTransmittance.setter
    def rTransmittance(self, value):
        assert 0 <= value <= 1, "Red transmittance should be between 0 and 1"
        self.__r = value

    @property
    def gTransmittance(self):
        """Green transmittance."""
        return self.__g

    @gTransmittance.setter
    def gTransmittance(self, value):
        assert 0 <= value <= 1, "Green transmittance should be between 0 and 1"
        self.__g = value

    @property
    def bTransmittance(self):
        """Blue transmittance."""
        return self.__b

    @bTransmittance.setter
    def bTransmittance(self, value):
        assert 0 <= value <= 1, "Blue transmittance should be between 0 and 1"
        self.__b = value

    @property
    def averageTransmittance(self):
        """Calculate average transmittance."""
        return 0.265 * self.rTransmittance + \
            0.670 * self.gTransmittance + 0.065 * self.bTransmittance

    @staticmethod
    def getTransmissivity(transmittance):
        """Calculate transmissivity based on transmittance value.

        "Transmissivity is the amount of light not absorbed in one traversal of
        the material. Transmittance -- the value usually measured - is the total
        light transmitted through the pane including multiple reflections."
        """
        if transmittance == 0:
            return 0
        return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) -
                0.9166530661) / 0.0036261119 / transmittance

    def toRadString(self, minimal=False):
        """Return full radiance definition."""
        __baseString = self.headLine + "0\n0\n4 %.3f %.3f %.3f %.3f"

        glassDefinition = __baseString % (
            self.getTransmissivity(self.rTransmittance),
            self.getTransmissivity(self.gTransmittance),
            self.getTransmissivity(self.bTransmittance),
            self.refractionIndex
        )

        return glassDefinition.replace("\n", " ") if minimal else glassDefinition


if __name__ == "__main__":
    # some test code
    glassMaterial = GlassMaterial.bySingleTransValue("generic glass", .65)
    print glassMaterial
    print glassMaterial.toRadString(minimal=True)
