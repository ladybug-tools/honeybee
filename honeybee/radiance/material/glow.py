"""Radiance Glow Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glow
"""

from ..datatype import RadianceNumber
from ._materialbase import RadianceMaterial


class GlowMaterial(RadianceMaterial):
    """
    Create glow material.

    Attributes:

        name: Material name as a string. The name should not have whitespaces or
            special characters.
        red: A positive value for the Red channel of the glow
        green: A positive value for the Green channel of the glow
        blue: A positive value for the Blue channel of the glow
        maxRadius: ---.
    """
    red = RadianceNumber('red', checkPositive=True)
    blue = RadianceNumber('blue', checkPositive=True)
    green = RadianceNumber('green', checkPositive=True)
    maxRadius = RadianceNumber('maxRadius', checkPositive=True)

    def __init__(self, name, red=0, green=0, blue=0, maxRadius=0):
        """Init Glow material."""
        RadianceMaterial.__init__(self, name, materialType='glow', modifier='void')
        self.red = red
        """A positive value for the Red channel of the glow"""
        self.green = green
        """A positive value for the Green channel of the glow"""
        self.blue = blue
        """A positive value for the Blue channel of the glow"""
        self.maxRadius = maxRadius
        """Maximum radius for shadow testing"""

    def toRadString(self, minimal=False):
        """Return full Radiance definition"""
        baseString = self.headLine + "0\n0\n4 %.3f %.3f %.3f %.3f"

        glowDefinition = baseString % (
            self.red._value, self.green._value, self.blue._value, self.maxRadius._value
        )

        return glowDefinition.replace("\n", " ") if minimal else glowDefinition


class WhiteGlowMaterial(GlowMaterial):
    """A white glow material.

    Use this material for multi-phase daylight studies.
    """

    def __init__(self, name='white_glow'):
        """Create glow material."""
        GlowMaterial.__init__(self, name, 1, 1, 1, 0)
