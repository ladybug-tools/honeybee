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
        type: One of Radiance standard Primitive types (e.g. mixfunc, mixdata, etc)
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: "void").
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
    """

    @property
    def isRadianceMixture(self):
        """Indicate that this object is a Radiance Material."""
        return True
