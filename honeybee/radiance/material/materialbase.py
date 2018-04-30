"""Base Radiance Material class (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..primitive import Primitive


class RadianceMaterial(Primitive):
    """Base class for Radiance materials.

    Attributes:
        name: Material name as a string. Do not use white space and special character.
        type: One of Radiance standard Material types (e.g. glass, plastic).
        modifier: Material modifier (Default: "void").
    """
    @property
    def isRadianceMaterial(self):
        """Indicate that this object is a Radiance Material."""
        return True

    @property
    def can_be_modifier(self):
        """Indicate if this object can be a modifier.

        Materials, mixtures, textures or patterns can be modifiers.
        """
        return True

    @property
    def isGlassMaterial(self):
        """Indicate if this object has glass Material.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        return not self.is_opaque

    @property
    def is_opaque(self):
        """Indicate if the material is opaque."""
        return self.type not in ('glass', 'trans')
