"""Base Radiance Material class (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ...utilcol import check_name


class RadianceMaterial(object):
    """Base class for Radiance materials.

    Attributes:
        name: Material name as a string. Do not use white space and special character.
        material_type: One of Radiance standard Material types (e.g. glass, plastic).
        modifier: Material modifier (Default: "void").
    """

    # list of Radiance material types
    TYPES = set(("plastic", "glass", "trans", "metal", "mirror", "texfunc", "illum",
                 "mixedfunc", "dielectric", "transdata", "light", "glow", "BSDF",
                 "BRTDfunc"))

    def __init__(self, name, material_type, modifier="void"):
        """Create material base."""
        self.name = name
        """Material name as a string. Do not use white space and special character."""
        self.type = material_type
        """One of Radiance standard Material types (e.g. glass, plastic, etc)"""
        self.modifier = modifier
        """Material modifier. Default is void"""

    @property
    def isRadianceMaterial(self):
        """Indicate that this object is a Radiance Material."""
        return True

    @property
    def isGlassMaterial(self):
        """Indicate if this object has glass Material.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        return False

    @property
    def name(self):
        """Get/set material name."""
        return self._name

    @name.setter
    def name(self, name):
        assert name not in self.TYPES, \
            '%s is a radiance material type and' \
            ' should not be used as a material name.' % name
        self._name = name.rstrip().replace(" ", "_")
        check_name(self._name)

    @property
    def modifier(self):
        """Get/set material modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        self._modifier = modifier.rstrip().replace(" ", "_")

    @property
    def type(self):
        """Get/set material type."""
        return self._type

    @type.setter
    def type(self, material_type):
        assert material_type in self.TYPES, \
            "%s is not a supported material type." % material_type + \
            "Try one of these materials:\n%s" % str(self.TYPES)

        self._type = material_type

    @property
    def head_line(self):
        """Return first line of Material definition."""
        return "%s %s %s\n" % (self.modifier, self.type, self.name)

    def to_rad_string(self, minimal=False):
        """Return full radiance definition.

        Args:
            minimal: Set to True to get the definition in as single line.
        """
        raise NotImplementedError

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Return material definition."""
        return self.to_rad_string()
