"""Base Radiance Surfaces class (e.g source, sphere, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..primitive import Primitive


class RadianceGeometry(Primitive):
    """Base class for Radiance geometries.

    Attributes:
        name: Geometry name as a string. Do not use white space and special character.
        type: One of Radiance standard Geometry types (e.g. polygon, cone, ...).
        modifier: Modifier. It can be material, mixture, texture or pattern. Honeybee
            currently only supports materials. For other types use Generic primitive
            class (Default: "void").
    """

    @property
    def isRadianceGeometry(self):
        """Indicate that this object is a Radiance Geometry."""
        return True
