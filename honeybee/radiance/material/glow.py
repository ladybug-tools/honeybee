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
        max_radius: ---.
    """
    red = RadianceNumber('red', check_positive=True)
    blue = RadianceNumber('blue', check_positive=True)
    green = RadianceNumber('green', check_positive=True)
    max_radius = RadianceNumber('max_radius', check_positive=True)

    def __init__(self, name, red=0, green=0, blue=0, max_radius=0):
        """Init Glow material."""
        RadianceMaterial.__init__(self, name, material_type='glow', modifier='void')
        self.red = red
        """A positive value for the Red channel of the glow"""
        self.green = green
        """A positive value for the Green channel of the glow"""
        self.blue = blue
        """A positive value for the Blue channel of the glow"""
        self.max_radius = max_radius
        """Maximum radius for shadow testing"""

    def to_rad_string(self, minimal=False):
        """Return full Radiance definition"""
        base_string = self.head_line + "0\n0\n4 %.3f %.3f %.3f %.3f"

        glow_definition = base_string % (
            self.red._value, self.green._value, self.blue._value, self.max_radius._value
        )

        return glow_definition.replace("\n", " ") if minimal else glow_definition


class WhiteGlowMaterial(GlowMaterial):
    """A white glow material.

    Use this material for multi-phase daylight studies.
    """

    def __init__(self, name='white_glow'):
        """Create glow material."""
        GlowMaterial.__init__(self, name, 1, 1, 1, 0)
