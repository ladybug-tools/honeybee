"""Base Radiance Texture class (Texfunc, Texdata).

http://radsite.lbl.gov/radiance/refer/ray.html#Textures
"""
from ..primitive import Primitive


class RadianceTexture(Primitive):
    """Base class for Radiance texture (Texfunc, Texdata).

    A texture is a perturbation of the surface normal, and is given by either a function
    or data.

    Attributes:
        name: Primitive name as a string. Do not use white space and special character.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: "void").
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
    """

    def __init__(self, name, modifier=None, values=None, is_opaque=None):
        """Create primitive base."""
        Primitive.__init__(self, name, self.__class__.__name__.lower(), modifier,
                           values, is_opaque)

    @property
    def isRadianceTexture(self):
        """Indicate that this object is a Radiance Material."""
        return True
