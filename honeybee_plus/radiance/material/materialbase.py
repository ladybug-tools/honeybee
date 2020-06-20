"""Base Radiance Material class (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..primitive import Primitive


class RadianceMaterial(Primitive):
    """Base class for Radiance materials."""

    def __init__(self, name, modifier=None, values=None, is_opaque=None):
        """Create primitive base."""
        material_type = self.__class__.__name__.lower()
        Primitive.__init__(self, name, material_type, modifier, values, is_opaque)

    @property
    def isRadianceMaterial(self):
        """Indicate that this object is a Radiance Material."""
        return True
