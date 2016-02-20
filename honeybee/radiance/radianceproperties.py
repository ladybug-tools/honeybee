"""Radiance Properties for HBSurfaces."""
from radiancematerial import RadianceMaterial


class radianceproperties(object):
    """Radiance properties."""

    @property
    def radianceMaterial(self):
        """Return Radiance Material."""
        return self.__radianceMaterial

    @radianceMaterial.setter
    def radianceMaterial(self, material):
        """Set Radiance Material."""
        # chek if radiance material is radiance material
        if isinstance(material, RadianceMaterial):
            self.__radianceMaterial = material
        # if type is string then try to create a material from string
        pass
