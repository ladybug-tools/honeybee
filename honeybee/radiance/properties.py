"""Radiance Properties for HBSurfaces."""
import copy
from .material.plastic import BlackMaterial
from .material.glow import WhiteGlow


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

    __slots__ = ('_material', '_black_material', '_glow_material')

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
        """Radiance black material."""
        return self._black_material

    @black_material.setter
    def black_material(self, material, rename_black_material=False):
        """Set Radiance black_materialblack material.

        Args:
            material: A radiance material. Default material is BlackMaterial.
            rename_black_material: Rename default black material to the same name as
            radiance material (Default: False).
        """
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._black_material = material
        else:
            self._black_material = BlackMaterial()
            if self.material and rename_black_material:
                self._black_material.name = self.radiance.name

    @property
    def glow_material(self):
        """Radiance glow material."""
        return self._glow_material

    @glow_material.setter
    def glow_material(self, material, rename_glow_material=False):
        """Set Radiance glow_materialblack material.

        Args:
            material: A radiance material. Default material is GlowMaterial.
            rename_glow_material: Rename default glow material to the same name as
            radiance material (Default: False).
        """
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._glow_material = material
        else:
            self._glow_material = WhiteGlow()
            if self.material and rename_glow_material:
                self._glow_material.name = self.radiance.name

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
