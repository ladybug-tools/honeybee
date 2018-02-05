"""Radiance Light Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Light
"""

from ..datatype import RadianceNumber
from ._materialbase import RadianceMaterial


class LightMaterial(RadianceMaterial):

    red = RadianceNumber('red', check_positive=True)
    blue = RadianceNumber('blue', check_positive=True)
    green = RadianceNumber('green', check_positive=True)

    def __init__(self, name, red=0, green=0, blue=0):
        """
        Create light material
        Attributes:

            name: Material name as a string. The name should not have whitespaces or
                special characters.
            red: A positive value for the Red channel of the light
            green: A positive value for the Green channel of the light
            blue: A positive value for the Blue channel of the light
            modifer: Material modifier. The default value is void.
        """
        RadianceMaterial.__init__(self, name, material_type='light', modifier='void')
        self.red = red
        """A positive value for the Red channel of the light"""
        self.green = green
        """A positive value for the Green channel of the light"""
        self.blue = blue
        """A positive value for the Blue channel of the light"""

    def to_rad_string(self, minimal=False):
        """Return full Radiance definition"""
        __base_string = self.head_line + "0\n0\n3 %.3f %.3f %.3f"

        light_definition = __base_string % (
            self.red._value, self.green._value, self.blue._value)

        return light_definition.replace("\n", " ") if minimal else light_definition
