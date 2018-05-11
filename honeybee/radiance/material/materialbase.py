"""Base Radiance Material class (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..primitive import Primitive


class RadianceMaterial(Primitive):
    """Base class for Radiance materials."""

    @property
    def isRadianceMaterial(self):
        """Indicate that this object is a Radiance Material."""
        return True
