"""Radiance Materials (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""


class RadianceMaterial(object):
    """
    Base class for Radiance materials.

    Attributes:
        name: Material name as a string. Do not use white space and special character.
        materialType: One of Radiance standard Material types (e.g. glass, plastic, etc).
        modifier: Material modifier (Default: "void").
    """

    # list of Radiance material types
    __types = ["plastic", "glass", "trans", "metal", "mirror", "texfunc", "illum",
               "mixedfunc", "dielectric", "transdata", "light", "glow", "BSDF"]

    def __init__(self, name, materialType, modifier="void"):
        """Create material base."""
        self.name = name
        """Material name as a string. Do not use white space and special character."""
        self.type = materialType
        """One of Radiance standard Material types (e.g. glass, plastic, etc)"""
        self.modifier = modifier
        """Material modifier. Default is void"""

    @property
    def name(self):
        """Get/set material name."""
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name.rstrip().replace(" ", "_")

    @property
    def modifier(self):
        """Get/set material modifier."""
        return self.__modifier

    @modifier.setter
    def modifier(self, modifier):
        self.__modifier = modifier.rstrip().replace(" ", "_")

    @property
    def type(self):
        """Get/set material type."""
        return self.__type

    @type.setter
    def type(self, materialType):
        assert materialType in self.__types, \
            "%s is not a supported material type." % materialType + \
            "Try one of these materials:\n%s" % str(self.__types)

        self.__type = materialType

    @property
    def headLine(self):
        """Return first line of Material definition."""
        return "%s %s %s\n" % (self.modifier, self.type, self.name)

    def toRadString(self, minimal=False):
        """Return full radiance definition.

        Args:
            minimal: Set to True to get the definition in as single line.
        """
        raise NotImplementedError

    def __repr__(self):
        """Return material definition."""
        return self.toRadString()
