"""Radiance Properties for HBSurfaces."""
import copy
from .material.plastic import BlackMaterial


class RadianceProperties(object):
    """Radiance properties for HBSurface.

    Args:
        material: Radiance material. Use honeybee.radiace.material to create a
            radiance material (Default: None).
        black_material: A material that will be used for blacking out this surface. By
            default black material is set to black color with no reflectance. In cases
            such as interior glass black material should be set to the original glass
            material.
    """

    __slots__ = ('_material', '_black_material')

    def __init__(self, material=None, black_material=None):
        """Create radiance properties for surface."""
        self.material = material
        self.black_material = black_material

    @property
    def isRadianceProperties(self):
        """Indicate this object is RadianceProperties."""
        return True

    @property
    def material(self):
        """Return Radiance Material."""
        return self._material

    @material.setter
    def material(self, material):
        """Set Radiance material."""
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._material = material
        else:
            self._material = None

    @property
    def black_material(self):
        """Return Radiance Material."""
        return self._black_material

    @black_material.setter
    def black_material(self, material):
        """Set Radiance black_materialblack material."""
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._black_material = material
        else:
            self._black_material = BlackMaterial()

    def duplicate(self):
        """Duplicate RadianceProperties."""
        return copy.copy(self)

    def to_rad_string(self):
        """Get Radiance definition for honeybee surfaces if any."""
        raise NotImplementedError()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Radiance properties."""
        if not self.material:
            return 'RadianceProp::Material.Unset'
        else:
            return 'RadianceProp::%s' % self.material.name


if __name__ == "__main__":
    rp = RadianceProperties()
    print(rp)
    print(rp.is_material_set_by_user)
