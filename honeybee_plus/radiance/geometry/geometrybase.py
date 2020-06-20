"""Base Radiance Surfaces class (e.g source, sphere, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..primitive import Primitive


class RadianceGeometry(Primitive):
    """Base class for Radiance geometries.

    Attributes:
        name: Geometry name as a string. Do not use white space and special character.
        modifier: Modifier. It can be material, mixture, texture or pattern. Honeybee
            currently only supports materials. For other types use Generic primitive
            class (Default: "void").
    """

    def __init__(self, name, modifier=None, values=None, is_opaque=None):
        """Create primitive base."""
        Primitive.__init__(self, name, self.__class__.__name__.lower(), modifier,
                           values, is_opaque)

    @property
    def isRadianceGeometry(self):
        """Indicate that this object is a Radiance Geometry."""
        return True
