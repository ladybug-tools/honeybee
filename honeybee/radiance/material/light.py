"""Radiance Light Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Light
"""

from ..datatype import RadianceNumber
from _materialbase import RadianceMaterial

class LightMaterial(RadianceMaterial):


    red = RadianceNumber('red',checkPositive=True)
    blue = RadianceNumber('blue', checkPositive=True)
    green= RadianceNumber('green',checkPositive=True)
    def __init__(self,name,red=0,green=0,blue=0):
        """
        Create light material
        Attributes:

            name: Material name as a string. The name should not have whitespaces or special
                characters.
            red: A positive value for the Red channel of the light
            green: A positive value for the Green channel of the light
            blue: A positive value for the Blue channel of the light
            modifer: Material modifier. The default value is void.
        """
        RadianceMaterial.__init__(self,name,materialType='light',modifier='void')
        self.red=red
        """A positive value for the Red channel of the light"""
        self.green=green
        """A positive value for the Green channel of the light"""
        self.blue=blue
        """A positive value for the Blue channel of the light"""

    def toRadString(self, minimal=False):
        """Return full Radiance definition"""
        __baseString=self.headLine + "0\n0\n3 %.3f %.3f %.3f"

        lightDefinition=__baseString%(self.red._value,self.green._value,self.blue._value)

        return lightDefinition.replace("\n", " ") if minimal else lightDefinition