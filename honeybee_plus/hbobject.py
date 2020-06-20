
class HBObject(object):
    """Base class for Honeybee Zone and Surface."""

    @property
    def isHBObject(self):
        """Return True."""
        return True

    def ToString(self):
        """Overwrite .NET's ToString's method."""
        return self.__repr__()
