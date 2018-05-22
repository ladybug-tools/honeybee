"""Base Radiance Mixtures class.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixtures
"""
from ..primitive import Primitive


class RadianceMixture(Primitive):
    """Base class for Radiance mixtures.

    A mixture is a blend of one or more materials or textures and patterns. Blended
    materials should not be light source types or virtual source types.

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
    def isRadianceMixture(self):
        """Indicate that this object is a Radiance Material."""
        return True
